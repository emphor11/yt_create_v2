"""Validator for SceneStoryboardSpec and ProjectStoryboardSpec.

Enforces strict semantic boundaries:
- Canonical 13 primitives only (no high-level templates: card, hero, kpi, etc.)
- Trigger-words must match verbatim words in scene narration
- Micro-layout container rules (only groups can have children)
- Absolute rejection of pixel coordinates, frame numbers, and timestamps
- VisualIntent.relationship_type is semantic context only (never deterministic mapping)
"""
from __future__ import annotations

from domain.storyboard import (
    SceneStoryboardSpec,
    ProjectStoryboardSpec,
    StoryboardNode,
    extract_narration_words,
    PROHIBITED_DOWNSTREAM_KEYS,
)
from domain.validation import ValidationResult
from domain.primitives.common import CanonicalCapabilityType, FORBIDDEN_COMPOSITION_TYPES


BANNED_TEMPLATE_IDENTIFIERS: set[str] = {
    "group_comparison", "group_card", "group_hero", "group_kpi",
    "group_timeline", "group_waterfall", "card_group", "hero_group",
    "kpi_group", "comparison_group",
}


class StoryboardValidator:
    """Validates SceneStoryboardSpec and ProjectStoryboardSpec against the contract."""

    def validate_scene(self, scene: SceneStoryboardSpec) -> ValidationResult:
        errors: list[str] = []
        warnings: list[str] = []

        # 1. Scene ID & Narration
        if not scene.scene_id.strip():
            errors.append("Scene requires a non-empty scene_id.")
        if not scene.narration.strip():
            errors.append(f"Scene '{scene.scene_id}' narration is required and cannot be empty.")

        # 2. Node hierarchy and uniqueness
        all_node_ids: set[str] = set()
        persistent_keys: set[str] = set()

        def validate_node(node: StoryboardNode, parent_id: str | None = None) -> None:
            if not node.id.strip():
                errors.append(f"Scene '{scene.scene_id}' contains a node with an empty id.")
                return

            if node.id in all_node_ids:
                errors.append(f"Duplicate node ID '{node.id}' in scene '{scene.scene_id}'.")
            all_node_ids.add(node.id)

            if node.persistence_key:
                persistent_keys.add(node.persistence_key)

            # Check for banned high-level composition template names in IDs/names
            node_id_lower = node.id.lower()
            node_name_lower = (node.name or "").lower()
            for banned in BANNED_TEMPLATE_IDENTIFIERS:
                if banned in node_id_lower or banned in node_name_lower:
                    errors.append(
                        f"Node '{node.id}' in scene '{scene.scene_id}' uses template composition name '{banned}'. "
                        "Groups are layout containers, not hidden composition templates. "
                        "Use semantic identities like 'income_world', 'salary_metric', 'rent_metric' instead."
                    )

            # Check capability type
            if str(node.type) in FORBIDDEN_COMPOSITION_TYPES or node.type.value in FORBIDDEN_COMPOSITION_TYPES:
                errors.append(
                    f"Node '{node.id}' in scene '{scene.scene_id}' uses forbidden capability '{node.type}'. "
                    f"Cards, heroes, KPIs, and comparisons must be built using primitive groups."
                )

            # Check group vs children
            if node.type != CanonicalCapabilityType.GROUP and len(node.children) > 0:
                errors.append(
                    f"Node '{node.id}' is of type '{node.type.value}' but has {len(node.children)} children. "
                    "Only 'group' primitives may contain child nodes."
                )

            # Recursively check props for downstream coordinates or frames
            for prop_key in node.props.keys():
                if prop_key.lower() in PROHIBITED_DOWNSTREAM_KEYS:
                    errors.append(
                        f"Node '{node.id}' contains prohibited downstream property '{prop_key}'. "
                        "The Storyboarder must not output pixel coordinates, frame numbers, or timestamps."
                    )

            # Recurse children
            for child in node.children:
                validate_node(child, parent_id=node.id)

        for root in scene.root_nodes:
            validate_node(root)

        # 3. Explicit Semantic Relationships Validation
        for rel in scene.relationships:
            if not rel.source_id.strip():
                errors.append(f"Scene '{scene.scene_id}' contains a relationship with empty source_id.")
            if not rel.relation.strip():
                errors.append(f"Scene '{scene.scene_id}' contains a relationship with empty relation.")
            if not rel.target_id.strip():
                errors.append(f"Scene '{scene.scene_id}' contains a relationship with empty target_id.")

        # 4. Actions & Trigger Word Validation
        clean_words = extract_narration_words(scene.narration)
        word_counts: dict[str, int] = {}
        for w in clean_words:
            word_counts[w.lower()] = word_counts.get(w.lower(), 0) + 1

        for action in scene.actions:
            if not action.action_id.strip():
                errors.append(f"Scene '{scene.scene_id}' contains an action with an empty action_id.")

            # Target node check
            if action.target_node_id not in all_node_ids and action.target_node_id not in persistent_keys:
                errors.append(
                    f"Action '{action.action_id}' in scene '{scene.scene_id}' targets unknown node "
                    f"'{action.target_node_id}'. Available nodes: {sorted(all_node_ids)}"
                )

            # Trigger word check
            trigger_clean = action.trigger_word.strip().strip(".,!?;:\"'()[]{}").lower()
            if not trigger_clean:
                errors.append(f"Action '{action.action_id}' trigger word is empty.")
            else:
                count = word_counts.get(trigger_clean, 0)
                if count == 0:
                    errors.append(
                        f"Action '{action.action_id}' trigger word '{action.trigger_word}' was not found "
                        f"in scene '{scene.scene_id}' narration: '{scene.narration}'"
                    )
                elif action.trigger_occurrence > count:
                    errors.append(
                        f"Action '{action.action_id}' trigger word '{action.trigger_word}' requests "
                        f"occurrence {action.trigger_occurrence}, but only appears {count} time(s) "
                        f"in scene '{scene.scene_id}' narration."
                    )

        if errors:
            return ValidationResult(status="blocked", errors=errors, warnings=warnings)
        return ValidationResult(status="valid", warnings=warnings)

    def validate(self, spec: SceneStoryboardSpec | ProjectStoryboardSpec) -> ValidationResult:
        """Validates either a single scene spec or a full project storyboard spec."""
        if isinstance(spec, SceneStoryboardSpec):
            return self.validate_scene(spec)

        # Project storyboard validation
        all_errors: list[str] = []
        all_warnings: list[str] = []
        seen_scene_ids: set[str] = set()
        introduced_persistent_keys: set[str] = set()

        if not spec.scenes:
            all_errors.append("Project storyboard must contain at least one scene.")

        for scene in spec.scenes:
            if scene.scene_id in seen_scene_ids:
                all_errors.append(f"Duplicate scene_id '{scene.scene_id}' in project storyboard.")
            seen_scene_ids.add(scene.scene_id)

            res = self.validate_scene(scene)
            if res.errors:
                all_errors.extend(res.errors)
            if res.warnings:
                all_warnings.extend(res.warnings)

            # Check cross-scene persistence continuity:
            # Persistent objects already introduced in earlier scenes must NOT re-trigger appear/enter actions.
            node_key_map: dict[str, str] = {}
            def map_node_keys(n: StoryboardNode) -> None:
                if n.persistence_key:
                    node_key_map[n.id] = n.persistence_key
                    node_key_map[n.persistence_key] = n.persistence_key
                for c in n.children:
                    map_node_keys(c)

            for r in scene.root_nodes:
                map_node_keys(r)

            for act in scene.actions:
                act_type = act.action_type.value if hasattr(act.action_type, "value") else str(act.action_type)
                target_key = node_key_map.get(act.target_node_id, act.target_node_id)
                if target_key in introduced_persistent_keys and act_type in ("appear", "enter"):
                    all_errors.append(
                        f"Action '{act.action_id}' in scene '{scene.scene_id}' re-triggers '{act_type}' "
                        f"on persistent object '{act.target_node_id}' (persistence_key: '{target_key}') which was already "
                        "introduced in an earlier scene. Persistent objects must not re-appear; "
                        "use reposition, transform, highlight, pulse, or update_value instead."
                    )

            # Record cross-scene persistent keys present in this scene for subsequent scenes
            def record_keys(n: StoryboardNode) -> None:
                if n.persistence_key and n.persistence_scope == "cross_scene":
                    introduced_persistent_keys.add(n.persistence_key)
                    introduced_persistent_keys.add(n.id)
                for c in n.children:
                    record_keys(c)

            for r in scene.root_nodes:
                record_keys(r)

        if all_errors:
            return ValidationResult(status="blocked", errors=all_errors, warnings=all_warnings)
        return ValidationResult(status="valid", warnings=all_warnings)
