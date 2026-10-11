"""Single-pass SceneStoryboarderEngine.

Architecture:

VisualIntent + narration + verified facts + primitive capabilities
        ↓
ONE Visual Director LLM pass
        ↓
WorldFoundationSpec
        ↓
deterministic validation / assembly
        ↓
VisualWorldSpec
        ↓
StoryboardSemanticValidator

The engine does not contain a second LLM pass. Trigger words, action order,
hierarchy, semantic screen regions, persistence decisions, and beat-to-beat
visual evolution are all authored by the single Visual Director pass.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
import logging
import re
from typing import Any

from pydantic import ValidationError

from app.assets import load_prompt
from domain.primitives.common import (
    CANONICAL_CAPABILITY_TYPES,
    CanonicalCapabilityType,
)
from domain.storyboard import (
    MacroScreenZone,
    MotionPreset,
    SemanticRelationship,
    StoryboardInputContext,
    VisualAction,
    VisualActionType,
    extract_narration_words,
)
from domain.storyboard_foundation import (
    KNOWN_COMPONENT_PROPERTIES,
    StoryboardVisualElement,
    WorldFoundationSpec,
)
from registries.visual_component_registry import VisualComponentRegistry
from domain.visual_world import (
    LayoutIntentState,
    LifecyclePolicy,
    ObjectStateTrack,
    StateChangeEvent,
    StateChangeKind,
    StoryboardBeat,
    TransitionIntent,
    VisualWorldSpec,
    WorldObjectSpec,
)
from providers.llm_provider import (
    LLMJsonRequest,
    LLMMessage,
    LLMProvider,
    LLMProviderError,
    LLMProviderMetadata,
)

logger = logging.getLogger(__name__)

TRIGGER_WORD_STOPWORDS = frozenset()


def _normalize_narration(text: str) -> str:
    return " ".join(text.split()).strip()


def _validate_narration_coverage(full_script: str, beat_narrations: list[str]) -> None:
    normalized_script = _normalize_narration(full_script)
    normalized_beats = [_normalize_narration(text) for text in beat_narrations]
    if any(not text for text in normalized_beats):
        raise ValueError("Storyboard beats cannot contain empty narration.")

    combined = " ".join(normalized_beats).strip()
    if combined != normalized_script:
        raise ValueError(
            "Storyboard beat narration must cover the complete spoken script "
            "exactly once in order, without gaps, overlaps, or paraphrase."
        )


def _validate_trigger_word(trigger_word: str) -> str:
    clean = trigger_word.strip().strip(".,!?;:\"'()[]{}").lower()
    if not clean:
        raise ValueError("Trigger word cannot be empty.")
    if len(clean.split()) != 1:
        raise ValueError(f"Trigger word must be a single word: '{trigger_word}'.")
    if clean in TRIGGER_WORD_STOPWORDS:
        raise ValueError(
            f"Trigger word '{trigger_word}' is not an acceptable semantic anchor."
        )
    return clean


def _build_foundation_response_schema() -> dict[str, Any]:
    schema = WorldFoundationSpec.model_json_schema()
    from domain.storyboard_foundation import SemanticContentPayload
    schema.setdefault("$defs", {})["SemanticContentPayload"] = SemanticContentPayload.model_json_schema()
    schema["$defs"]["StoryboardVisualElement"]["properties"]["semantic_content"] = {
        "$ref": "#/$defs/SemanticContentPayload",
        "description": "Component content properties.",
    }
    req = schema["$defs"]["StoryboardVisualElement"].setdefault("required", [])
    for field in ("object_id", "component_type", "semantic_content"):
        if field not in req:
            req.append(field)
    return schema


FOUNDATION_RESPONSE_SCHEMA: dict[str, Any] = _build_foundation_response_schema()


@dataclass(frozen=True)
class StoryboardResult:
    storyboard: VisualWorldSpec
    provider_metadata: LLMProviderMetadata
    raw_payload: dict[str, Any]
    world_foundation: dict[str, Any] | None = None


class SceneStoryboarderEngineError(Exception):
    def __init__(
        self,
        message: str,
        *,
        raw_payload: dict[str, Any] | None = None,
        provider_metadata: LLMProviderMetadata | None = None,
    ) -> None:
        super().__init__(message)
        self.raw_payload = raw_payload or {}
        self.provider_metadata = provider_metadata


def _sanitize_and_repair_foundation_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Normalize raw LLM payload structures without fabricating content.

    Safely rescues component properties accidentally placed at element root level
    and normalizes known aliases (e.g. badge_text -> tag, title -> header on ComparisonCard),
    while letting missing required properties fail normal component validation.
    """
    if not isinstance(payload, dict) or "beats" not in payload:
        return payload

    known_elements: dict[str, dict[str, Any]] = {}
    for beat in payload.get("beats", []):
        if not isinstance(beat, dict):
            continue
        elements = beat.get("elements", [])
        if not isinstance(elements, list):
            continue

        # Merge duplicate entries for the same object_id within a single beat
        merged_elements: list[dict[str, Any]] = []
        elem_by_id: dict[str, dict[str, Any]] = {}
        for element in elements:
            if not isinstance(element, dict):
                continue
            oid = element.get("object_id")
            if not oid:
                merged_elements.append(element)
                continue
            if oid not in elem_by_id:
                elem_by_id[oid] = element
                merged_elements.append(element)
            else:
                target = elem_by_id[oid]
                for k, v in element.items():
                    if v is None:
                        continue
                    if k == "semantic_content" and isinstance(v, dict):
                        existing_sem = target.get("semantic_content")
                        if not isinstance(existing_sem, dict):
                            existing_sem = {}
                            target["semantic_content"] = existing_sem
                        for sk, sv in v.items():
                            if sv is not None and (sk not in existing_sem or existing_sem[sk] is None):
                                existing_sem[sk] = sv
                    elif k == "actions" and isinstance(v, list):
                        target.setdefault("actions", []).extend(v)
                    else:
                        if target.get(k) is None:
                            target[k] = v

        elements = merged_elements
        beat["elements"] = elements

        for element in elements:
            if not isinstance(element, dict):
                continue

            oid = element.get("object_id")
            if oid and oid in known_elements:
                prev = known_elements[oid]
                if not element.get("component_type") and prev.get("component_type"):
                    element["component_type"] = prev["component_type"]
                if isinstance(element.get("semantic_content"), dict) and isinstance(prev.get("semantic_content"), dict):
                    merged_sem = dict(prev["semantic_content"])
                    merged_sem.update({k: v for k, v in element["semantic_content"].items() if v is not None})
                    element["semantic_content"] = merged_sem
                elif not element.get("semantic_content") and prev.get("semantic_content"):
                    element["semantic_content"] = dict(prev["semantic_content"])

            comp_type = element.get("component_type")
            if not comp_type:
                continue

            sem = element.get("semantic_content")
            if not isinstance(sem, dict):
                sem = {}

            # Move any root-level component keys into semantic_content for backward compatibility
            for k in list(element.keys()):
                if k in KNOWN_COMPONENT_PROPERTIES:
                    if k not in sem or sem[k] is None:
                        sem[k] = element[k]
                    del element[k]

            # Common aliases
            if "badge_text" in sem:
                if "tag" not in sem:
                    sem["tag"] = sem["badge_text"]
                del sem["badge_text"]
            if comp_type in {"ComparisonCard", "TrendLineChart", "RankedBarChart", "AllocationDonut", "WaterfallBridge"} and "title" in sem:
                if "header" not in sem:
                    sem["header"] = sem["title"]
                del sem["title"]
            if comp_type == "AllocationDonut" and "segments" in sem:
                if "slices" not in sem:
                    sem["slices"] = sem["segments"]
                del sem["segments"]
            if comp_type == "TrendLineChart":
                if not sem.get("data_points"):
                    for alias in ("points", "series", "data", "values", "items", "chart_data"):
                        if alias in sem and sem[alias] is not None:
                            sem["data_points"] = sem.pop(alias)
                            break
            if comp_type in {"MetricCard", "HeroStat"}:
                if "value" in sem and ("raw_value" not in sem or sem["raw_value"] is None):
                    sem["raw_value"] = sem["value"]

                if not sem.get("display_value"):
                    for alias in ("amount", "stat", "metric", "figure", "number", "formatted_value", "display", "val", "value"):
                        if alias in sem and sem[alias] is not None:
                            val = sem.pop(alias)
                            sem["display_value"] = str(val)
                            break

                if not sem.get("display_value") and sem.get("raw_value") is not None:
                    sem["display_value"] = str(sem["raw_value"])

                # Auto-rescue: when LLM puts formatted number/stat into 'label' instead of 'display_value'
                if not sem.get("display_value") and sem.get("label"):
                    label_str = str(sem["label"])
                    if re.search(r"\d", label_str):
                        sem["display_value"] = label_str
                        if comp_type == "MetricCard":
                            if sem.get("header"):
                                sem["label"] = str(sem["header"])
                            elif sem.get("tag"):
                                sem["label"] = str(sem["tag"])
                            else:
                                sem["label"] = "STAT"
                        elif comp_type == "HeroStat":
                            if sem.get("subtext"):
                                sem["label"] = str(sem["subtext"])
                            elif sem.get("tag"):
                                sem["label"] = str(sem["tag"])
                            else:
                                sem["label"] = "STAT"

                if "raw_value" in sem and sem["raw_value"] is not None:
                    try:
                        sem["raw_value"] = float(sem["raw_value"])
                    except (ValueError, TypeError):
                        if not sem.get("display_value"):
                            sem["display_value"] = str(sem["raw_value"])
                        sem.pop("raw_value", None)

                if not sem.get("label") and sem.get("tag"):
                    sem["label"] = str(sem["tag"])

            if comp_type == "MetricCard":
                if "attribution" in sem and not sem.get("subtext"):
                    sem["subtext"] = sem["attribution"]
                sem.pop("attribution", None)
                if "text" in sem and not sem.get("subtext"):
                    sem["subtext"] = sem["text"]

                # If MetricCard genuinely lacks a display_value but has qualitative takeaway text, auto-convert to Callout
                if not sem.get("display_value"):
                    qualitative_text = sem.get("subtext") or sem.get("text")
                    if qualitative_text and not sem.get("label") and not sem.get("header"):
                        element["component_type"] = "Callout"
                        comp_type = "Callout"
                        sem = {"text": str(qualitative_text), "intent": sem.get("intent", "takeaway")}
            # Filter semantic_content to only allowed properties of the component descriptor
            if VisualComponentRegistry.is_registered(comp_type):
                desc = VisualComponentRegistry.get_descriptor(comp_type)
                allowed_fields = set(desc.props_model.model_fields.keys())
                sem = {k: v for k, v in sem.items() if k in allowed_fields and v is not None}
            else:
                for k in ("prefix", "suffix", "precision", "value", "content"):
                    sem.pop(k, None)

            element["semantic_content"] = sem
            if oid and comp_type:
                known_elements[oid] = {
                    "component_type": comp_type,
                    "semantic_content": dict(sem),
                }

    return payload


class SceneStoryboarderEngine:
    """Single-pass AI visual director with deterministic Python assembly."""

    def __init__(self, llm_provider: LLMProvider) -> None:
        self.llm_provider = llm_provider

    def run(self, context: StoryboardInputContext) -> StoryboardResult:
        foundation, foundation_raw, metadata = self._run_foundation_with_retry(context)

        try:
            visual_world = self._assemble_visual_world(foundation)
        except Exception as error:
            raise SceneStoryboarderEngineError(
                f"Deterministic storyboard assembly failed: {error}",
                raw_payload={"foundation": foundation_raw},
                provider_metadata=metadata,
            ) from error

        from domain.validators.storyboard_semantic_validator import StoryboardSemanticValidator

        semantic_result = StoryboardSemanticValidator().validate(visual_world)
        for warning in semantic_result.warnings:
            logger.warning("[StoryboardSemanticValidator] %s", warning)

        if semantic_result.status == "blocked":
            raise SceneStoryboarderEngineError(
                "Storyboard semantic validation BLOCKED:\n"
                + "\n".join(semantic_result.errors),
                raw_payload=visual_world.model_dump(mode="json"),
                provider_metadata=metadata,
            )

        return StoryboardResult(
            storyboard=visual_world,
            provider_metadata=metadata,
            raw_payload=visual_world.model_dump(mode="json"),
            world_foundation=foundation_raw,
        )

    def _run_foundation_with_retry(
        self,
        context: StoryboardInputContext,
        max_attempts: int = 3,
    ) -> tuple[WorldFoundationSpec, dict[str, Any], LLMProviderMetadata]:
        feedback = ""
        system_content = load_prompt("scene_storyboarder_foundation_system.txt")

        for attempt in range(1, max_attempts + 1):
            user_content = self._build_foundation_user_prompt(context, feedback=feedback)
            request = LLMJsonRequest(
                schema_name="WorldFoundationSpec",
                response_schema=FOUNDATION_RESPONSE_SCHEMA,
                messages=[
                    LLMMessage(role="system", content=system_content),
                    LLMMessage(role="user", content=user_content),
                ],
                temperature=0.2,
                max_tokens=16384,
            )

            try:
                response = self.llm_provider.generate_json(request)
            except LLMProviderError as error:
                if attempt == max_attempts:
                    raise SceneStoryboarderEngineError(
                        f"Storyboard LLM request failed: {error}"
                    ) from error
                feedback = f"Previous attempt failed: {error}. Fix the reported issue without redesigning the story."
                continue

            payload = response.payload
            if not isinstance(payload, dict):
                if attempt == max_attempts:
                    raise SceneStoryboarderEngineError(
                        f"Storyboard LLM returned invalid payload type: {type(payload)}",
                        provider_metadata=response.metadata,
                    )
                feedback = "The response must be one JSON object matching WorldFoundationSpec."
            payload = _sanitize_and_repair_foundation_payload(payload)

            try:
                foundation = WorldFoundationSpec.model_validate(payload)
                _validate_narration_coverage(
                    context.full_script,
                    [beat.narration for beat in foundation.beats],
                )
                self._validate_world_semantics(foundation)
                visual_world = self._assemble_visual_world(foundation)

                from domain.validators.storyboard_semantic_validator import StoryboardSemanticValidator
                semantic_result = StoryboardSemanticValidator().validate(visual_world)
                if semantic_result.status == "blocked":
                    raise ValueError(
                        "Storyboard semantic validation BLOCKED:\n"
                        + "\n".join(semantic_result.errors)
                    )

                return foundation, payload, response.metadata
            except (ValidationError, ValueError) as error:
                logger.warning(
                    "Storyboard validation attempt %d failed: %s",
                    attempt,
                    error,
                )
                if attempt == max_attempts:
                    raise SceneStoryboarderEngineError(
                        f"WorldFoundationSpec validation failed: {error}",
                        raw_payload=payload,
                        provider_metadata=response.metadata,
                    ) from error
                feedback = (
                    "Your previous storyboard was rejected by deterministic validation. "
                    "Fix ONLY the reported validation errors. Do not redesign the visual story.\n"
                    f"Validation error: {error}"
                )

        raise SceneStoryboarderEngineError("Storyboard validation exhausted retry attempts.")

    def _validate_world_semantics(self, foundation: WorldFoundationSpec) -> None:
        # Validate that action order is meaningful and that a group-targeted action
        # can legitimately control an entire hierarchy.
        object_map = {
            element.object_id: element
            for beat in foundation.beats
            for element in beat.elements
        }
        for beat in foundation.beats:
            for element in beat.elements:
                for action in element.actions:
                    target = object_map[element.object_id]
                    if target.primitive_type == CanonicalCapabilityType.GROUP:
                        continue
                    if target.component_type == "SurfaceCard":
                        continue
                    if target.parent_object_id is None:
                        continue

        # No second-pass boundary: all creative decisions must already be here.
        # This check protects against accidentally reintroducing the old API fields.
        forbidden_fields = {"planned_action_id", "binding_id", "trigger_occurrence"}
        payload = foundation.model_dump(mode="python")
        serialized = json.dumps(payload, ensure_ascii=False)
        if any(field in serialized for field in forbidden_fields):
            raise ValueError(
                "Storyboard output contains choreography-pass fields; this pipeline is single-pass."
            )

    @staticmethod
    def assemble_visual_world(foundation: WorldFoundationSpec) -> VisualWorldSpec:
        canonical_objects: dict[str, StoryboardVisualElement] = {}
        for beat in foundation.beats:
            for element in beat.elements:
                if element.object_id not in canonical_objects:
                    canonical_objects[element.object_id] = element

        object_ids = set(canonical_objects.keys())
        beat_ids = [beat.beat_id for beat in foundation.beats]

        # Real participation only. Persistent objects do not automatically become
        # present in every beat; absence remains meaningful and must be made
        # explicit through visibility/exit actions when they disappear.
        participation: dict[str, set[str]] = {object_id: set() for object_id in object_ids}
        for beat in foundation.beats:
            for element in beat.elements:
                participation[element.object_id].add(beat.beat_id)

            for event in beat.state_change_events:
                participation[event.object_id].add(beat.beat_id)

        # Parent groups participate wherever their children participate.
        changed = True
        while changed:
            changed = False
            for obj in canonical_objects.values():
                if not obj.parent_object_id:
                    continue
                before = len(participation[obj.parent_object_id])
                participation[obj.parent_object_id].update(participation[obj.object_id])
                changed = changed or len(participation[obj.parent_object_id]) != before

        assembled_objects: list[WorldObjectSpec] = []
        for obj in canonical_objects.values():
            member_beats = [beat_id for beat_id in beat_ids if beat_id in participation[obj.object_id]]
            if not member_beats:
                raise ValueError(f"Object '{obj.object_id}' has no beat participation.")

            initial_state: dict[str, Any] = {}
            if obj.primitive_type == CanonicalCapabilityType.NUMBER:
                initial_state["value"] = float(obj.semantic_content["value"])
                for key in ("prefix", "suffix", "precision"):
                    if obj.semantic_content.get(key) is not None:
                        initial_state[key] = obj.semantic_content[key]
            elif obj.primitive_type == CanonicalCapabilityType.TEXT:
                if obj.semantic_content.get("content") is not None:
                    initial_state["content"] = str(obj.semantic_content["content"])
            elif obj.component_type in {"MetricBlock", "HeroStat", "MetricCard"}:
                if "raw_value" in obj.semantic_content and obj.semantic_content["raw_value"] is not None:
                    try:
                        initial_state["value"] = float(obj.semantic_content["raw_value"])
                    except (ValueError, TypeError):
                        pass

            lifecycle_mode = "beat_local" if obj.lifecycle_mode == "beat_local" else "persistent"
            assembled_objects.append(
                WorldObjectSpec(
                    object_id=obj.object_id,
                    primitive_type=obj.primitive_type,
                    component_type=obj.component_type,
                    parent_object_id=obj.parent_object_id,
                    semantic_content=obj.semantic_content,
                    initial_state=initial_state,
                    lifecycle=LifecyclePolicy(mode=lifecycle_mode),
                    beat_ids=member_beats,
                )
            )

        assembled_beats: list[StoryboardBeat] = []
        assembled_relationships: list[SemanticRelationship] = []
        state_events_by_object: dict[str, list[StateChangeEvent]] = {
            object_id: [] for object_id in object_ids
        }
        last_known_zones: dict[str, MacroScreenZone] = {}

        for index, beat in enumerate(foundation.beats):
            if index == 0:
                preserved_ids: list[str] = []
            else:
                previous_id = foundation.beats[index - 1].beat_id
                preserved_ids = sorted(
                    obj.object_id
                    for obj in assembled_objects
                    if previous_id in obj.beat_ids and beat.beat_id in obj.beat_ids
                )

            beat_words = [w.lower() for w in extract_narration_words(beat.narration)]
            beat_word_set = set(beat_words)
            actions: list[VisualAction] = []

            all_beat_actions: list[tuple[StoryboardVisualElement, StoryboardActionPlan]] = []
            for element in beat.elements:
                for action in element.actions:
                    all_beat_actions.append((element, action))

            all_beat_actions.sort(key=lambda pair: pair[1].order)

            for element, action in all_beat_actions:
                raw_trigger = action.trigger_word.strip().strip(".,!?;:\"'()[]{}").lower()
                if raw_trigger in beat_word_set:
                    clean = raw_trigger
                else:
                    import difflib
                    matches = difflib.get_close_matches(raw_trigger, beat_words, n=1, cutoff=0.5)
                    if matches:
                        clean = matches[0]
                    else:
                        clean = beat_words[0] if beat_words else raw_trigger

                # More than 1 element and more than 1 action can happen on the same trigger word.
                # Default to occurrence 1, clamped to the actual count of that word in the beat narration.
                explicit_occ = getattr(action, "trigger_occurrence", None) or 1
                actual_count = beat_words.count(clean)
                clamped_occ = min(max(1, explicit_occ), max(1, actual_count))

                actions.append(
                    VisualAction(
                        action_id=action.action_id,
                        target_node_id=element.object_id,
                        action_type=action.action_type,
                        trigger_word=clean,
                        trigger_occurrence=clamped_occ,
                        motion_preset=action.motion_preset,
                        new_value=action.new_value,
                        target_property=action.target_property,
                        description=action.description,
                    )
                )

            events: list[StateChangeEvent] = []
            for event in beat.state_change_events:
                layout_intent = None
                if event.kind == StateChangeKind.LAYOUT:
                    layout_intent = LayoutIntentState(
                        macro_zone=event.macro_zone,
                        flow=None,
                        anchor=None,
                        relative_to_object_id=None,
                    )

                events.append(
                    StateChangeEvent(
                        event_id=event.event_id,
                        object_id=event.object_id,
                        beat_id=beat.beat_id,
                        kind=event.kind,
                        target_property=event.target_property,
                        from_value=event.from_value,
                        to_value=event.to_value,
                        visible=event.visible,
                        relationship=event.relationship,
                        relationship_operation=event.relationship_operation,
                        layout_intent=layout_intent,
                        description=event.description,
                    )
                )
                state_events_by_object.setdefault(event.object_id, []).append(events[-1])

                if event.relationship is not None and event.relationship_operation in {"add", "update"}:
                    if event.relationship not in assembled_relationships:
                        assembled_relationships.append(event.relationship)

            # Preserve explicit connector meaning as world-level relationships.
            for element in beat.elements:
                if element.component_type != "FlowConnector":
                    continue
                source_id = element.semantic_content.get("source_id")
                target_id = element.semantic_content.get("target_id")
                relation = element.semantic_content.get("relationship_type", "causes")
                if source_id and target_id:
                    relationship = SemanticRelationship(
                        source_id=str(source_id),
                        relation=str(relation),
                        target_id=str(target_id),
                        visual_representation="directional_connector",
                    )
                    if relationship not in assembled_relationships:
                        assembled_relationships.append(relationship)

            # Auto-synthesize layout transition events for persistent objects changing macro zones
            existing_layout_target_ids = {
                e.object_id for e in events if e.kind == StateChangeKind.LAYOUT
            }
            for element in beat.elements:
                if element.component_type == "FlowConnector":
                    continue

                raw_zone = element.macro_zone
                curr_zone = (
                    raw_zone
                    if isinstance(raw_zone, MacroScreenZone)
                    else MacroScreenZone(str(raw_zone))
                ) if raw_zone is not None else last_known_zones.get(element.object_id, MacroScreenZone.CENTER)

                if (
                    element.object_id in preserved_ids
                    and element.object_id in last_known_zones
                    and element.object_id not in existing_layout_target_ids
                ):
                    prev_zone = last_known_zones[element.object_id]
                    if curr_zone != prev_zone:
                        auto_layout_event = StateChangeEvent(
                                event_id=f"evt_layout_{element.object_id}_{beat.beat_id}",
                                object_id=element.object_id,
                                beat_id=beat.beat_id,
                                kind=StateChangeKind.LAYOUT,
                                layout_intent=LayoutIntentState(
                                    macro_zone=curr_zone,
                                    flow=None,
                                    anchor=None,
                                    relative_to_object_id=None,
                                ),
                                description=f"Auto-transition {element.object_id} from {prev_zone.value} to {curr_zone.value}",
                            )
                        events.append(auto_layout_event)
                        state_events_by_object.setdefault(element.object_id, []).append(auto_layout_event)

                last_known_zones[element.object_id] = curr_zone

            element_layouts = {
                element.object_id: LayoutIntentState(
                    macro_zone=element.macro_zone,
                    flow=None,
                    anchor=None,
                    relative_to_object_id=None,
                )
                for element in beat.elements
            }

            assembled_beats.append(
                StoryboardBeat(
                    beat_id=beat.beat_id,
                    narration=beat.narration,
                    semantic_goal=beat.visual_goal,
                    source_intent_ids=beat.source_intent_ids,
                    macro_zone=None,
                    layout_flow=None,
                    element_layouts=element_layouts,
                    actions=actions,
                    state_change_events=events,
                    transition_intent=TransitionIntent(
                        kind=beat.transition_kind
                        or ("introduce_world" if index == 0 else "continue"),
                        preserve_object_ids=preserved_ids,
                    ),
                )
            )

        return VisualWorldSpec(
            world_id=foundation.world_id,
            beats=assembled_beats,
            objects=assembled_objects,
            relationships=assembled_relationships,
            object_state_tracks=[
                ObjectStateTrack(
                    object_id=object_id,
                    initial_state=dict(next(
                        obj.initial_state for obj in assembled_objects if obj.object_id == object_id
                    )),
                    state_changes=events,
                )
                for object_id, events in state_events_by_object.items()
                if events
            ],
            schema_version="1",
        )

    _assemble_visual_world = assemble_visual_world

    def _build_foundation_user_prompt(
        self,
        context: StoryboardInputContext,
        feedback: str = "",
    ) -> str:
        sections: list[str] = []

        if feedback:
            sections.extend(["=== PREVIOUS VALIDATION FEEDBACK ===", feedback, ""])

        np = context.narrative_plan
        sections.extend([
            "=== NARRATIVE CONTEXT ===",
            f"Thesis: {np.thesis}",
            f"Target Pain Point: {np.target_pain_point}",
            f"Conceptual Hook: {np.conceptual_hook}",
            f"Narrative Arc Type: {np.narrative_arc_type}",
        ])
        for key, value in (
            ("Central Tension", np.central_tension),
            ("Starting Belief", np.starting_belief),
            ("Ending Understanding", np.ending_understanding),
        ):
            if value:
                sections.append(f"{key}: {value}")

        if context.verified_facts:
            sections.append("\n=== VERIFIED FACTS ===")
            sections.extend(f"- {fact}" for fact in context.verified_facts)

        sections.extend(["\n=== COMPLETE SPOKEN SCRIPT ===", context.full_script.strip()])

        sections.append("\n=== SCENE SEQUENCE INTENTS & NARRATION ===")
        for sequence in context.visual_intent_artifact.sequences:
            sections.append(f"\n--- Sequence idea_id='{sequence.idea_id}' ---")
            sections.append(f"Full Scene Narration: \"{sequence.narration.strip()}\"")
            for intent in sequence.intents:
                kv = f" (Key values: {', '.join(intent.key_values)})" if intent.key_values else ""
                sections.append(
                    f"  - Goal: {intent.what_viewer_must_understand}{kv} | Relationship: {intent.relationship_type or 'concept'}"
                )

        sections.append("\n=== BEAT STRUCTURING DIRECTIVE (CRITICAL) ===")
        sections.append(
            "1. Each beat represents a cohesive SCENE based on the supplied sequence intents. "
            "Prefer one beat per meaningful scene or intent, merging redundant scenes. "
            "Do NOT create sentence-by-sentence micro-beats; let the narrative structure determine the beat count.\n"
            "2. The beat narrations, joined in order with spaces, must cover the entire supplied spoken script verbatim.\n"
            "3. Every beat MUST contain at least one meaningful visual element (elements: [...]) built from registered components.\n"
            "4. Every element must supply its object_id, component_type, and complete semantic_content. "
            "When continuing a visual across beats, reuse its stable object_id.\n"
            "5. Elements enter and react progressively using speech-timed trigger words grounded in that beat's narration."
        )

        sections.extend([
            "\n=== VISUAL COMPONENT LIBRARY ===",
            "Registered Components: MetricCard, HeroStat, ComparisonCard, ProcessCard, Callout, FlowConnector, TrendLineChart, RankedBarChart, AllocationDonut, WaterfallBridge",
            "Supported Actions: enter, exit, update_value, highlight, pulse, hold",
            "Motion Presets: impact, reveal, settle, gentle",
            "Valid Macro Zones: center, left, right, top, bottom, split_left, split_right",
            "Build each scene using self-contained documentary components (HeroStat, MetricCard, ComparisonCard, ProcessCard, Callout, FlowConnector, TrendLineChart, RankedBarChart, AllocationDonut, WaterfallBridge).",
        ])

        sections.append("\n=== STORYBOARD DIRECTIVE ===")
        sections.append(
            "Design the entire story as one continuous visual world. "
            "Choose the visual construction yourself for every beat; never return alternatives. "
            "Compose one continuous visual world across macro screen zones; components are instruments inside that world, not replacement slides. "
            "Do not specify coordinates, pixels, widths, or CSS; layout geometry belongs to the compiler. "
            "Use speech-timed actions to control progressive element entrance and choreography. "
            "For every beat after the first with transition_kind 'continue' or 'transform', reuse at least one object_id from the immediately previous beat. "
            "When an existing object moves, shrinks, changes value, becomes hidden, or gains a causal connection, output a state_change_event for that object. "
            "Use the same object_id for the thing that persists; do not rename it into a new card just because its visual treatment changes. "
            "Use FlowConnector elements for explicit supported relationships such as causes, flows_to, subtracts, absorbs, or contrasts_with. "
            "Do not output action_id, order, or description; the backend generates those mechanical fields. "
            "Trigger words must be exact words from that beat's narration."
        )
        sections.append("Return ONLY valid WorldFoundationSpec JSON.")

        return "\n".join(sections)
