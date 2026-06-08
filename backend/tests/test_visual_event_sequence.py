import pytest
from pydantic import ValidationError

from domain.semantic_scene import SemanticEntity, SemanticRelationship, SemanticScene
from domain.validators.visual_event_sequence_validator import VisualEventSequenceValidator
from domain.visual_event_sequence import VisualEvent, VisualEventSequence
from engines.visual_event_sequence_engine import VisualEventSequenceEngine


def make_semantic_scene() -> SemanticScene:
    return SemanticScene(
        scene_id="scene_01",
        primary_concept="payment_pain_reduction",
        confidence=1.0,
        warnings=[],
        entities=[
            SemanticEntity(
                id="entity_price",
                role="product_price",
                raw="₹80,000",
                value=80000,
                unit="INR",
                source_text="The phone costs ₹80,000.",
            ),
            SemanticEntity(
                id="entity_emi",
                role="monthly_payment",
                raw="₹6,667",
                value=6667,
                unit="INR",
                source_text="But the EMI is shown as ₹6,667 per month.",
            ),
        ],
        relationships=[
            SemanticRelationship(
                type="reframes",
                from_entity_id="entity_emi",
                to_entity_id="entity_price",
            )
        ],
    )


def test_visual_event_sequence_engine_maps_semantic_scene_to_events() -> None:
    semantic_scene = make_semantic_scene()

    sequence = VisualEventSequenceEngine().run(semantic_scene)

    assert sequence.scene_id == "scene_01"
    assert sequence.primary_concept == "payment_pain_reduction"
    assert [event.primitive for event in sequence.events] == [
        "reveal_full_price",
        "reveal_monthly_payment",
        "attention_shift",
    ]
    assert sequence.events[0].semantic_entity_id == "entity_price"
    assert sequence.events[1].semantic_entity_id == "entity_emi"
    assert sequence.events[2].semantic_relationship_type == "reframes"


def test_visual_event_sequence_validator_accepts_mvp_events() -> None:
    semantic_scene = make_semantic_scene()
    sequence = VisualEventSequenceEngine().run(semantic_scene)

    result = VisualEventSequenceValidator().validate(
        sequence,
        semantic_scene=semantic_scene,
    )

    assert result.status == "valid"
    assert result.errors == []


def test_visual_event_sequence_validator_blocks_missing_event() -> None:
    semantic_scene = make_semantic_scene()
    sequence = VisualEventSequenceEngine().run(semantic_scene)
    sequence.events = sequence.events[:2]

    result = VisualEventSequenceValidator().validate(
        sequence,
        semantic_scene=semantic_scene,
    )

    assert result.status == "blocked"
    assert (
        "VisualEventSequence missing required event for relationship: reframes."
        in result.errors
    )


def test_visual_event_sequence_validator_blocks_unknown_entity_reference() -> None:
    semantic_scene = make_semantic_scene()
    sequence = VisualEventSequenceEngine().run(semantic_scene)
    sequence.events[0].semantic_entity_id = "missing_entity"

    result = VisualEventSequenceValidator().validate(
        sequence,
        semantic_scene=semantic_scene,
    )

    assert result.status == "blocked"
    assert "Visual event event_full_price references unknown semantic entity." in result.errors


def test_visual_event_sequence_validator_blocks_role_primitive_mismatch() -> None:
    semantic_scene = make_semantic_scene()
    sequence = VisualEventSequenceEngine().run(semantic_scene)
    sequence.events[0].semantic_entity_id = "entity_emi"

    result = VisualEventSequenceValidator().validate(
        sequence,
        semantic_scene=semantic_scene,
    )

    assert result.status == "blocked"
    assert "Visual event event_full_price primitive must be reveal_monthly_payment." in result.errors


def test_visual_event_sequence_validator_blocks_unknown_relationship_reference() -> None:
    semantic_scene = make_semantic_scene()
    sequence = VisualEventSequenceEngine().run(semantic_scene)
    sequence.events[2].semantic_relationship_type = "compounds"

    result = VisualEventSequenceValidator().validate(
        sequence,
        semantic_scene=semantic_scene,
    )

    assert result.status == "blocked"
    assert "Visual event event_attention_shift references unknown semantic relationship." in result.errors


def test_visual_event_sequence_rejects_downstream_fields() -> None:
    payload = {
        "scene_id": "scene_01",
        "primary_concept": "payment_pain_reduction",
        "events": [],
        "component": "SplitComparison",
    }

    with pytest.raises(ValidationError):
        VisualEventSequence.model_validate(payload)


def test_visual_event_rejects_both_entity_and_relationship_reference() -> None:
    semantic_scene = make_semantic_scene()
    sequence = VisualEventSequence(
        scene_id="scene_01",
        primary_concept="payment_pain_reduction",
        events=[
            VisualEvent(
                event_id="event_invalid",
                primitive="reveal_full_price",
                intent="establish_real_cost",
                world_object="full_price",
                semantic_entity_id="entity_price",
                semantic_relationship_type="reframes",
            )
        ],
    )

    result = VisualEventSequenceValidator().validate(
        sequence,
        semantic_scene=semantic_scene,
    )

    assert result.status == "blocked"
    assert (
        "Visual event event_invalid must reference either an entity or a relationship, not both."
        in result.errors
    )
