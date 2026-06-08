from domain.semantic_scene import SemanticEntity, SemanticScene
from domain.validation import ValidationResult
from domain.visual_event_sequence import VisualEvent, VisualEventSequence


ENTITY_EVENT_RULES = {
    "product_price": {
        "event_id": "event_full_price",
        "primitive": "reveal_full_price",
        "intent": "establish_real_cost",
        "world_object": "full_price",
    },
    "monthly_payment": {
        "event_id": "event_monthly_payment",
        "primitive": "reveal_monthly_payment",
        "intent": "create_comfort",
        "world_object": "monthly_payment",
    },
}

RELATIONSHIP_EVENT_RULES = {
    "reframes": {
        "event_id": "event_attention_shift",
        "primitive": "attention_shift",
        "intent": "create_realization",
        "world_object": "comparison_focus",
    }
}

FORBIDDEN_DOWNSTREAM_KEYS = {
    "component",
    "props",
    "timed_spans",
    "render_spec",
    "frames",
}


class VisualEventSequenceValidator:
    def validate(
        self,
        visual_event_sequence: VisualEventSequence,
        *,
        semantic_scene: SemanticScene,
    ) -> ValidationResult:
        errors: list[str] = []

        if visual_event_sequence.scene_id != semantic_scene.scene_id:
            errors.append("VisualEventSequence scene_id must match SemanticScene scene_id.")
        if visual_event_sequence.primary_concept != semantic_scene.primary_concept:
            errors.append(
                "VisualEventSequence primary_concept must match SemanticScene primary_concept."
            )
        if not visual_event_sequence.events:
            errors.append("At least one visual event is required.")

        entity_by_id = {entity.id: entity for entity in semantic_scene.entities}
        relationship_types = {relationship.type for relationship in semantic_scene.relationships}
        event_ids: set[str] = set()

        for event in visual_event_sequence.events:
            if not event.event_id.strip():
                errors.append("Visual event event_id is required.")
            if event.event_id in event_ids:
                errors.append(f"Duplicate visual event id: {event.event_id}.")
            event_ids.add(event.event_id)

            if not event.primitive.strip():
                errors.append(f"Visual event {event.event_id} primitive is required.")
            if not event.intent.strip():
                errors.append(f"Visual event {event.event_id} intent is required.")
            if not event.world_object.strip():
                errors.append(f"Visual event {event.event_id} world_object is required.")

            if event.semantic_entity_id and event.semantic_relationship_type:
                errors.append(
                    f"Visual event {event.event_id} must reference either an entity or a relationship, not both."
                )
            if not event.semantic_entity_id and not event.semantic_relationship_type:
                errors.append(
                    f"Visual event {event.event_id} must reference a semantic entity or relationship."
                )
            if event.semantic_entity_id:
                self._validate_entity_event(event, entity_by_id, errors)
            if event.semantic_relationship_type:
                self._validate_relationship_event(event, relationship_types, errors)

        self._validate_required_entity_event("product_price", semantic_scene.entities, visual_event_sequence.events, errors)
        self._validate_required_entity_event(
            "monthly_payment",
            semantic_scene.entities,
            visual_event_sequence.events,
            errors,
        )
        self._validate_required_relationship_event(
            "reframes",
            relationship_types,
            visual_event_sequence.events,
            errors,
        )

        leaked_keys = FORBIDDEN_DOWNSTREAM_KEYS.intersection(visual_event_sequence.model_dump().keys())
        if leaked_keys:
            errors.append(
                "VisualEventSequence must not contain downstream fields: "
                + ", ".join(sorted(leaked_keys))
                + "."
            )

        if errors:
            return ValidationResult(status="blocked", errors=errors)

        return ValidationResult(status="valid")

    def _validate_entity_event(
        self,
        event: VisualEvent,
        entity_by_id: dict[str, SemanticEntity],
        errors: list[str],
    ) -> None:
        entity = entity_by_id.get(event.semantic_entity_id or "")
        if entity is None:
            errors.append(f"Visual event {event.event_id} references unknown semantic entity.")
            return

        expected = ENTITY_EVENT_RULES.get(entity.role)
        if expected is None:
            errors.append(
                f"Visual event {event.event_id} references unsupported semantic role: {entity.role}."
            )
            return

        self._validate_event_shape(event, expected, errors)

    def _validate_relationship_event(
        self,
        event: VisualEvent,
        relationship_types: set[str],
        errors: list[str],
    ) -> None:
        relationship_type = event.semantic_relationship_type or ""
        if relationship_type not in relationship_types:
            errors.append(f"Visual event {event.event_id} references unknown semantic relationship.")
            return

        expected = RELATIONSHIP_EVENT_RULES.get(relationship_type)
        if expected is None:
            errors.append(
                f"Visual event {event.event_id} references unsupported relationship type: {relationship_type}."
            )
            return

        self._validate_event_shape(event, expected, errors)

    @staticmethod
    def _validate_event_shape(
        event: VisualEvent,
        expected: dict[str, str],
        errors: list[str],
    ) -> None:
        for field_name, expected_value in expected.items():
            actual_value = getattr(event, field_name)
            if actual_value != expected_value:
                errors.append(
                    f"Visual event {event.event_id} {field_name} must be {expected_value}."
                )

    @staticmethod
    def _validate_required_entity_event(
        role: str,
        entities: list[SemanticEntity],
        events: list[VisualEvent],
        errors: list[str],
    ) -> None:
        entity = next((candidate for candidate in entities if candidate.role == role), None)
        if entity is None:
            return
        expected = ENTITY_EVENT_RULES[role]
        if not any(
            event.semantic_entity_id == entity.id
            and event.primitive == expected["primitive"]
            for event in events
        ):
            errors.append(f"VisualEventSequence missing required event for role: {role}.")

    @staticmethod
    def _validate_required_relationship_event(
        relationship_type: str,
        relationship_types: set[str],
        events: list[VisualEvent],
        errors: list[str],
    ) -> None:
        if relationship_type not in relationship_types:
            return
        expected = RELATIONSHIP_EVENT_RULES[relationship_type]
        if not any(
            event.semantic_relationship_type == relationship_type
            and event.primitive == expected["primitive"]
            for event in events
        ):
            errors.append(
                f"VisualEventSequence missing required event for relationship: {relationship_type}."
            )
