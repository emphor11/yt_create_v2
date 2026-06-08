from domain.semantic_scene import SemanticEntity, SemanticScene
from domain.visual_event_sequence import VisualEvent, VisualEventSequence
from domain.visual_plan import SplitComparisonProps, VisualPlan, VisualPlanSide
from registries.component_registry import ComponentRegistry


class VisualPlanEngine:
    def __init__(self, component_registry: ComponentRegistry):
        self.component_registry = component_registry

    def run(
        self,
        *,
        semantic_scene: SemanticScene,
        visual_event_sequence: VisualEventSequence,
    ) -> VisualPlan:
        component_definition = self.component_registry.get_component("SplitComparison")
        left_role = component_definition.constraints["left_role"]
        right_role = component_definition.constraints["right_role"]
        left_entity = self._find_entity(semantic_scene.entities, left_role)
        right_entity = self._find_entity(semantic_scene.entities, right_role)
        attention_shift_event = self._find_event(
            visual_event_sequence.events,
            "attention_shift",
        )

        return VisualPlan(
            scene_id=semantic_scene.scene_id,
            primary_concept=semantic_scene.primary_concept,
            component=component_definition.component,
            selection_reason=(
                "Selected SplitComparison because payment_pain_reduction contains "
                "product_price and monthly_payment with an attention_shift event."
            ),
            props=SplitComparisonProps(
                left=self._side_from_entity(left_entity, "Full price"),
                right=self._side_from_entity(right_entity, "Monthly payment"),
                attention_shift_event_id=attention_shift_event.event_id,
            ),
        )

    @staticmethod
    def _find_entity(entities: list[SemanticEntity], role: str) -> SemanticEntity:
        return next(entity for entity in entities if entity.role == role)

    @staticmethod
    def _find_event(events: list[VisualEvent], primitive: str) -> VisualEvent:
        return next(event for event in events if event.primitive == primitive)

    @staticmethod
    def _side_from_entity(entity: SemanticEntity, label: str) -> VisualPlanSide:
        return VisualPlanSide(
            role=entity.role,
            semantic_entity_id=entity.id,
            label=label,
            raw=entity.raw,
            value=entity.value,
            unit=entity.unit,
        )
