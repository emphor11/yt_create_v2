"""Semantic completeness validator for VisualWorldSpec.

This validator runs AFTER VisualWorldSpec.model_validate() succeeds.
It catches worlds that are structurally valid but semantically incomplete —
worlds that would pass Pydantic but produce visually meaningless output.

The goal is NOT to make creative decisions.
The goal is to BLOCK obviously incomplete worlds before they reach WorldCompiler.

BLOCKERS (hard failures — world is rejected):
1. An ordinary beat has zero visual coverage (no world object includes it in beat_ids),
   unless the beat is explicitly marked as a hold or transition.
2. A number primitive has empty semantic_content (no numeric value key present).
3. An object references a beat_id not present in world.beats (integrity; belt-and-suspenders).

WARNINGS (soft — world proceeds but log warns):
1. A multi-beat world with persistent objects has zero actions and zero state tracks
   across all beats, suggesting the world was underspecified.
"""
from __future__ import annotations

from domain.primitives.common import CanonicalCapabilityType
from domain.validation import ValidationResult
from domain.visual_world import StateChangeKind, VisualWorldSpec

# Keys that satisfy the number content requirement.
# At least one must appear in semantic_content for a number primitive.
_NUMBER_CONTENT_KEYS: frozenset[str] = frozenset({
    "number_value",
    "value",
    "numeric_value",
})

# transition_intent.kind values that explicitly mark a beat as a visual pause.
# These beats are exempt from the zero-coverage check.
_HOLD_TRANSITION_KINDS: frozenset[str] = frozenset({
    "hold",
    "transition",
})


class StoryboardSemanticValidator:
    """Validates semantic completeness of a VisualWorldSpec.

    Instantiate once and call ``validate(world)`` for each world.
    """

    def validate(self, world: VisualWorldSpec) -> ValidationResult:
        blockers: list[str] = []
        warnings: list[str] = []

        # Pre-compute: which objects cover each beat?
        beat_to_objects: dict[str, list[str]] = {beat.beat_id: [] for beat in world.beats}
        for obj in world.objects:
            for beat_id in obj.beat_ids:
                if beat_id in beat_to_objects:
                    beat_to_objects[beat_id].append(obj.object_id)
                # Note: invalid beat references are already caught by VisualWorldSpec.validate_world()

        # ----------------------------------------------------------------
        # BLOCKER 1: Ordinary beat with zero visual coverage
        # ----------------------------------------------------------------
        for beat in world.beats:
            # Check if this beat is explicitly a hold/transition
            is_exempt = (
                beat.transition_intent is not None
                and beat.transition_intent.kind in _HOLD_TRANSITION_KINDS
            )
            if is_exempt:
                continue

            covered = beat_to_objects.get(beat.beat_id, [])
            if not covered:
                blockers.append(
                    f"BLOCKER [beat_coverage] Beat '{beat.beat_id}' has zero visual coverage "
                    f"(no world object includes it in beat_ids). "
                    f"Narration: \"{beat.narration[:80]}{'...' if len(beat.narration) > 80 else ''}\". "
                    f"Every ordinary beat must have at least one visible world object. "
                    f"If this is a deliberate visual pause, set transition_intent.kind = 'hold'."
                )
                continue

            # Must have at least one visual action in the beat (cannot be empty of visible actions/elements)
            if not beat.actions:
                blockers.append(
                    f"BLOCKER [beat_coverage] Beat '{beat.beat_id}' has zero visual actions or participating elements. "
                    f"Narration: \"{beat.narration[:80]}{'...' if len(beat.narration) > 80 else ''}\". "
                    f"Every ordinary beat must include at least one visual element with an active action (e.g. 'hold', 'enter')."
                )

            # Check if all covered objects are explicitly set to hidden/invisible in this beat
            hidden_objects = {
                evt.object_id for evt in beat.state_change_events
                if evt.kind == StateChangeKind.VISIBILITY and evt.visible is False
            }
            if set(covered).issubset(hidden_objects):
                blockers.append(
                    f"BLOCKER [beat_coverage] Beat '{beat.beat_id}' has all objects set to hidden/invisible. "
                    f"Narration: \"{beat.narration[:80]}{'...' if len(beat.narration) > 80 else ''}\". "
                    f"Every ordinary beat must have at least one visible visual element."
                )

        # ----------------------------------------------------------------
        # BLOCKER 2: Component props and number primitive validation
        # ----------------------------------------------------------------
        for obj in world.objects:
            if obj.component_type is not None:
                from registries.visual_component_registry import VisualComponentRegistry
                if not VisualComponentRegistry.is_registered(obj.component_type):
                    blockers.append(
                        f"BLOCKER [unknown_component] Object '{obj.object_id}' uses unknown component '{obj.component_type}'."
                    )
                else:
                    try:
                        VisualComponentRegistry.validate_props(obj.component_type, obj.semantic_content)
                    except Exception as err:
                        blockers.append(
                            f"BLOCKER [component_props] Object '{obj.object_id}' of type '{obj.component_type}' "
                            f"has invalid props: {err}"
                        )
                continue

            if obj.primitive_type == CanonicalCapabilityType.NUMBER:
                has_value_key = bool(obj.semantic_content) and any(
                    k in obj.semantic_content for k in _NUMBER_CONTENT_KEYS
                )
                if not has_value_key:
                    blockers.append(
                        f"BLOCKER [number_content] Object '{obj.object_id}' is a number primitive "
                        f"but semantic_content is missing a numeric value key. "
                        f"Required: at least one of {sorted(_NUMBER_CONTENT_KEYS)}. "
                        f"Current semantic_content: {obj.semantic_content!r}. "
                        f"Populate it with the real number from the narration "
                        f"(e.g., {{\"number_value\": 10, \"unit\": \"%\", \"label\": \"Salary Raise\"}})."
                    )

        # A continue/transform transition without any preserved object is not
        # continuity; it is a sequence of unrelated slides. A deliberate cut
        # is allowed to start a new visual world.
        for index, beat in enumerate(world.beats[1:], start=1):
            transition = beat.transition_intent
            if transition is None or transition.kind not in {"continue", "transform"}:
                continue
            previous_ids = {
                obj.object_id for obj in world.objects
                if world.beats[index - 1].beat_id in obj.beat_ids
            }
            current_ids = {
                obj.object_id for obj in world.objects
                if beat.beat_id in obj.beat_ids
            }
            if previous_ids & current_ids:
                continue
            message = (
                f"Transition '{world.beats[index - 1].beat_id}' -> '{beat.beat_id}' "
                f"is marked '{transition.kind}' but preserves no object IDs. "
                "Reuse at least one stable object_id or mark the transition as 'cut' or 'introduce_world'."
            )
            blockers.append(f"BLOCKER [continuity] {message}")

        # ----------------------------------------------------------------
        # WARNING: multi-beat world with no state evolution
        # ----------------------------------------------------------------
        if len(world.beats) > 2:
            all_actions: list[object] = []
            for beat in world.beats:
                all_actions.extend(beat.actions)
                all_actions.extend(beat.state_change_events)
            all_state_tracks = world.object_state_tracks
            has_persistent = any(
                obj.lifecycle.mode == "persistent" for obj in world.objects
            )

            if has_persistent and not all_actions and not all_state_tracks:
                warnings.append(
                    f"WARNING [no_state_evolution] World '{world.world_id}' has {len(world.beats)} beats "
                    f"and persistent objects, but zero actions, zero state_change_events, and zero "
                    f"object_state_tracks. A multi-beat world that describes evolving information "
                    f"should have at least some state evolution. Consider adding visibility, value, "
                    f"or layout state changes to show how concepts develop beat-by-beat."
                )

        if blockers:
            return ValidationResult(status="blocked", errors=blockers, warnings=warnings)
        if warnings:
            return ValidationResult(status="warning", errors=[], warnings=warnings)
        return ValidationResult(status="valid", errors=[], warnings=warnings)
