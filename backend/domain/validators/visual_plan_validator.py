from domain.semantic_scene import SemanticEntity, SemanticScene
from domain.validation import ValidationResult
from domain.visual_event_sequence import VisualEventSequence
from domain.visual_plan import VisualPlan, VisualPlanSide
from registries.component_registry import ComponentRegistry


FORBIDDEN_DOWNSTREAM_KEYS = {
    "timed_spans",
    "duration_seconds",
    "fps",
    "render_spec",
    "frames",
}


class VisualPlanValidator:
    def __init__(self, component_registry: ComponentRegistry):
        self.component_registry = component_registry

    def validate(
        self,
        visual_plan: VisualPlan,
        *,
        semantic_scene: SemanticScene,
        visual_event_sequence: VisualEventSequence,
    ) -> ValidationResult:
        errors: list[str] = []

        if visual_plan.scene_id != semantic_scene.scene_id:
            errors.append("VisualPlan scene_id must match SemanticScene scene_id.")
        if visual_plan.scene_id != visual_event_sequence.scene_id:
            errors.append("VisualPlan scene_id must match VisualEventSequence scene_id.")
        if visual_plan.primary_concept != semantic_scene.primary_concept:
            errors.append("VisualPlan primary_concept must match SemanticScene primary_concept.")
        if visual_plan.primary_concept != visual_event_sequence.primary_concept:
            errors.append(
                "VisualPlan primary_concept must match VisualEventSequence primary_concept."
            )

        if not self.component_registry.has_component(visual_plan.component):
            errors.append(f"VisualPlan component is not registered: {visual_plan.component}.")
            return ValidationResult(status="blocked", errors=errors)

        component_definition = self.component_registry.get_component(visual_plan.component)
        if not visual_plan.selection_reason.strip():
            errors.append("VisualPlan selection_reason is required.")

        role_to_entity = {entity.role: entity for entity in semantic_scene.entities}
        event_primitives = {event.primitive for event in visual_event_sequence.events}
        for role in component_definition.required_roles:
            if role not in role_to_entity:
                errors.append(f"VisualPlan missing required semantic role: {role}.")
        for primitive in component_definition.supported_events:
            if primitive not in event_primitives:
                errors.append(f"VisualPlan missing required visual event primitive: {primitive}.")

        left_role = component_definition.constraints["left_role"]
        right_role = component_definition.constraints["right_role"]
        if visual_plan.props.left.role != left_role:
            errors.append(f"VisualPlan left role must be {left_role}.")
        if visual_plan.props.right.role != right_role:
            errors.append(f"VisualPlan right role must be {right_role}.")

        self._validate_side(
            side=visual_plan.props.left,
            expected_entity=role_to_entity.get(left_role),
            side_name="left",
            errors=errors,
        )
        self._validate_side(
            side=visual_plan.props.right,
            expected_entity=role_to_entity.get(right_role),
            side_name="right",
            errors=errors,
        )
        self._validate_attention_shift_event(
            visual_plan=visual_plan,
            visual_event_sequence=visual_event_sequence,
            errors=errors,
        )
        self._validate_all_entities_are_linked(
            visual_plan=visual_plan,
            semantic_scene=semantic_scene,
            errors=errors,
        )

        leaked_keys = FORBIDDEN_DOWNSTREAM_KEYS.intersection(visual_plan.model_dump().keys())
        if leaked_keys:
            errors.append(
                "VisualPlan must not contain downstream fields: "
                + ", ".join(sorted(leaked_keys))
                + "."
            )

        if errors:
            return ValidationResult(status="blocked", errors=errors)

        return ValidationResult(status="valid")

    @staticmethod
    def _validate_side(
        *,
        side: VisualPlanSide,
        expected_entity: SemanticEntity | None,
        side_name: str,
        errors: list[str],
    ) -> None:
        if expected_entity is None:
            return
        if not side.label.strip():
            errors.append(f"VisualPlan {side_name} label is required.")
        if side.semantic_entity_id != expected_entity.id:
            errors.append(f"VisualPlan {side_name} semantic_entity_id must match SemanticScene.")
        if side.raw != expected_entity.raw:
            errors.append(f"VisualPlan {side_name} raw value must match SemanticScene.")
        if side.value != expected_entity.value:
            errors.append(f"VisualPlan {side_name} value must match SemanticScene.")
        if side.unit != expected_entity.unit:
            errors.append(f"VisualPlan {side_name} unit must match SemanticScene.")

    @staticmethod
    def _validate_attention_shift_event(
        *,
        visual_plan: VisualPlan,
        visual_event_sequence: VisualEventSequence,
        errors: list[str],
    ) -> None:
        event = next(
            (
                candidate
                for candidate in visual_event_sequence.events
                if candidate.event_id == visual_plan.props.attention_shift_event_id
            ),
            None,
        )
        if event is None:
            errors.append("VisualPlan attention_shift_event_id must reference a visual event.")
            return
        if event.primitive != "attention_shift":
            errors.append("VisualPlan attention_shift_event_id must reference attention_shift.")
        if event.semantic_relationship_type != "reframes":
            errors.append("VisualPlan attention_shift_event_id must reference reframes.")

    @staticmethod
    def _validate_all_entities_are_linked(
        *,
        visual_plan: VisualPlan,
        semantic_scene: SemanticScene,
        errors: list[str],
    ) -> None:
        linked_entity_ids = {
            visual_plan.props.left.semantic_entity_id,
            visual_plan.props.right.semantic_entity_id,
        }
        unlinked_entities = [
            entity
            for entity in semantic_scene.entities
            if entity.id not in linked_entity_ids
        ]
        if unlinked_entities:
            errors.append("VisualPlan cannot proceed with unlinked semantic money entities.")
