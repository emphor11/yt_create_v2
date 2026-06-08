from domain.semantic_scene import SemanticEntity, SemanticRelationship, SemanticScene
from domain.visual_event_sequence import VisualEvent, VisualEventSequence


class VisualEventSequenceEngine:
    def run(self, semantic_scene: SemanticScene) -> VisualEventSequence:
        product_price = self._find_entity(semantic_scene.entities, "product_price")
        monthly_payment = self._find_entity(semantic_scene.entities, "monthly_payment")
        reframes_relationship = self._find_relationship(
            semantic_scene.relationships,
            "reframes",
        )

        events: list[VisualEvent] = []
        if product_price is not None:
            events.append(
                VisualEvent(
                    event_id="event_full_price",
                    semantic_entity_id=product_price.id,
                    primitive="reveal_full_price",
                    intent="establish_real_cost",
                    world_object="full_price",
                )
            )
        if monthly_payment is not None:
            events.append(
                VisualEvent(
                    event_id="event_monthly_payment",
                    semantic_entity_id=monthly_payment.id,
                    primitive="reveal_monthly_payment",
                    intent="create_comfort",
                    world_object="monthly_payment",
                )
            )
        if reframes_relationship is not None:
            events.append(
                VisualEvent(
                    event_id="event_attention_shift",
                    semantic_relationship_type=reframes_relationship.type,
                    primitive="attention_shift",
                    intent="create_realization",
                    world_object="comparison_focus",
                )
            )

        return VisualEventSequence(
            scene_id=semantic_scene.scene_id,
            primary_concept=semantic_scene.primary_concept,
            events=events,
        )

    @staticmethod
    def _find_entity(entities: list[SemanticEntity], role: str) -> SemanticEntity | None:
        return next((entity for entity in entities if entity.role == role), None)

    @staticmethod
    def _find_relationship(
        relationships: list[SemanticRelationship],
        relationship_type: str,
    ) -> SemanticRelationship | None:
        return next(
            (
                relationship
                for relationship in relationships
                if relationship.type == relationship_type
            ),
            None,
        )
