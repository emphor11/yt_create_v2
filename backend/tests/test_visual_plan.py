import pytest
from pydantic import ValidationError

from domain.semantic_scene import SemanticEntity, SemanticRelationship, SemanticScene
from domain.validators.visual_plan_validator import VisualPlanValidator
from domain.visual_event_sequence import VisualEvent, VisualEventSequence
from domain.visual_plan import VisualPlan
from engines.visual_plan_engine import VisualPlanEngine
from registries.component_registry import ComponentRegistry


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


def make_visual_event_sequence() -> VisualEventSequence:
    return VisualEventSequence(
        scene_id="scene_01",
        primary_concept="payment_pain_reduction",
        events=[
            VisualEvent(
                event_id="event_full_price",
                semantic_entity_id="entity_price",
                primitive="reveal_full_price",
                intent="establish_real_cost",
                world_object="full_price",
            ),
            VisualEvent(
                event_id="event_monthly_payment",
                semantic_entity_id="entity_emi",
                primitive="reveal_monthly_payment",
                intent="create_comfort",
                world_object="monthly_payment",
            ),
            VisualEvent(
                event_id="event_attention_shift",
                semantic_relationship_type="reframes",
                primitive="attention_shift",
                intent="create_realization",
                world_object="comparison_focus",
            ),
        ],
    )


def make_visual_plan() -> tuple[SemanticScene, VisualEventSequence, VisualPlan]:
    semantic_scene = make_semantic_scene()
    visual_event_sequence = make_visual_event_sequence()
    registry = ComponentRegistry()
    visual_plan = VisualPlanEngine(registry).run(
        semantic_scene=semantic_scene,
        visual_event_sequence=visual_event_sequence,
    )
    return semantic_scene, visual_event_sequence, visual_plan


def test_component_registry_registers_only_split_comparison_for_mvp() -> None:
    registry = ComponentRegistry()

    component = registry.get_component("SplitComparison")

    assert registry.available_components() == {
        "SplitComparison",
        "Timeline",
        "NumberCounter",
        "Charts",
        "Stock Image",
        "Stock Video",
        "Typography",
        "Icon Animation",
    }
    assert component.required_roles == ["product_price", "monthly_payment"]
    assert component.supported_events == [
        "reveal_full_price",
        "reveal_monthly_payment",
        "attention_shift",
    ]
    assert component.constraints == {
        "left_role": "product_price",
        "right_role": "monthly_payment",
    }


def test_visual_plan_engine_selects_split_comparison_with_traceable_props() -> None:
    semantic_scene, _visual_event_sequence, visual_plan = make_visual_plan()
    roles = {entity.role: entity for entity in semantic_scene.entities}

    assert visual_plan.component == "SplitComparison"
    assert visual_plan.scene_id == "scene_01"
    assert visual_plan.props.left.role == "product_price"
    assert visual_plan.props.left.semantic_entity_id == roles["product_price"].id
    assert visual_plan.props.left.raw == "₹80,000"
    assert visual_plan.props.left.value == 80000
    assert visual_plan.props.right.role == "monthly_payment"
    assert visual_plan.props.right.semantic_entity_id == roles["monthly_payment"].id
    assert visual_plan.props.right.raw == "₹6,667"
    assert visual_plan.props.right.value == 6667
    assert visual_plan.props.attention_shift_event_id == "event_attention_shift"
    assert "Selected SplitComparison" in visual_plan.selection_reason


def test_visual_plan_validator_accepts_mvp_plan() -> None:
    semantic_scene, visual_event_sequence, visual_plan = make_visual_plan()

    result = VisualPlanValidator(ComponentRegistry()).validate(
        visual_plan,
        semantic_scene=semantic_scene,
        visual_event_sequence=visual_event_sequence,
    )

    assert result.status == "valid"
    assert result.errors == []


def test_visual_plan_validator_blocks_invented_number() -> None:
    semantic_scene, visual_event_sequence, visual_plan = make_visual_plan()
    visual_plan.props.left.value = 79000

    result = VisualPlanValidator(ComponentRegistry()).validate(
        visual_plan,
        semantic_scene=semantic_scene,
        visual_event_sequence=visual_event_sequence,
    )

    assert result.status == "blocked"
    assert "VisualPlan left value must match SemanticScene." in result.errors


def test_visual_plan_validator_blocks_swapped_roles() -> None:
    semantic_scene, visual_event_sequence, visual_plan = make_visual_plan()
    visual_plan.props.left.role = "monthly_payment"

    result = VisualPlanValidator(ComponentRegistry()).validate(
        visual_plan,
        semantic_scene=semantic_scene,
        visual_event_sequence=visual_event_sequence,
    )

    assert result.status == "blocked"
    assert "VisualPlan left role must be product_price." in result.errors


def test_visual_plan_validator_blocks_unlinked_semantic_number() -> None:
    semantic_scene, visual_event_sequence, visual_plan = make_visual_plan()
    semantic_scene.entities.append(
        SemanticEntity(
            id="entity_fee",
            role="unknown_money",
            raw="₹2,000",
            value=2000,
            unit="INR",
            source_text="A case is ₹2,000.",
        )
    )

    result = VisualPlanValidator(ComponentRegistry()).validate(
        visual_plan,
        semantic_scene=semantic_scene,
        visual_event_sequence=visual_event_sequence,
    )

    assert result.status == "blocked"
    assert "VisualPlan cannot proceed with unlinked semantic money entities." in result.errors


def test_visual_plan_validator_blocks_missing_required_event() -> None:
    semantic_scene, visual_event_sequence, visual_plan = make_visual_plan()
    visual_event_sequence.events = visual_event_sequence.events[:2]

    result = VisualPlanValidator(ComponentRegistry()).validate(
        visual_plan,
        semantic_scene=semantic_scene,
        visual_event_sequence=visual_event_sequence,
    )

    assert result.status == "blocked"
    assert "VisualPlan missing required visual event primitive: attention_shift." in result.errors
    assert "VisualPlan attention_shift_event_id must reference a visual event." in result.errors


def test_visual_plan_rejects_downstream_fields() -> None:
    semantic_scene, _visual_event_sequence, visual_plan = make_visual_plan()
    payload = visual_plan.model_dump()
    payload["frames"] = 240

    with pytest.raises(ValidationError):
        VisualPlan.model_validate(payload)
