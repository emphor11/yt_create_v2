import pytest
from pydantic import ValidationError

from domain.semantic_scene import SemanticEntity, SemanticRelationship, SemanticScene
from domain.timed_scene_plan import TimedScenePlan
from domain.validators.timed_scene_plan_validator import TimedScenePlanValidator
from domain.visual_event_sequence import VisualEvent, VisualEventSequence
from domain.visual_plan import VisualPlan
from engines.visual_plan_engine import VisualPlanEngine
from engines.timing_engine import TimingEngine
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


def make_visual_plan() -> tuple[VisualEventSequence, VisualPlan]:
    semantic_scene = make_semantic_scene()
    visual_event_sequence = make_visual_event_sequence()
    visual_plan = VisualPlanEngine(ComponentRegistry()).run(
        semantic_scene=semantic_scene,
        visual_event_sequence=visual_event_sequence,
    )
    return visual_event_sequence, visual_plan


def make_timed_scene_plan() -> tuple[VisualEventSequence, VisualPlan, TimedScenePlan]:
    visual_event_sequence, visual_plan = make_visual_plan()
    timed_scene_plan = TimingEngine().run(
        visual_plan=visual_plan,
        visual_event_sequence=visual_event_sequence,
    )
    return visual_event_sequence, visual_plan, timed_scene_plan


def test_timing_engine_assigns_fixed_duration_and_event_spans() -> None:
    visual_event_sequence, _visual_plan, timed_scene_plan = make_timed_scene_plan()

    assert timed_scene_plan.scene_id == "scene_01"
    assert timed_scene_plan.duration_seconds == 8.0
    assert timed_scene_plan.fps == 30
    assert [span.event_id for span in timed_scene_plan.spans] == [
        event.event_id for event in visual_event_sequence.events
    ]
    assert timed_scene_plan.spans[0].start_seconds == 0.0
    assert timed_scene_plan.spans[-1].end_seconds == 8.0
    assert [span.duration_seconds for span in timed_scene_plan.spans] == [
        2.667,
        2.666,
        2.667,
    ]


def test_timed_scene_plan_validator_accepts_mvp_timing() -> None:
    visual_event_sequence, visual_plan, timed_scene_plan = make_timed_scene_plan()

    result = TimedScenePlanValidator().validate(
        timed_scene_plan,
        visual_plan=visual_plan,
        visual_event_sequence=visual_event_sequence,
    )

    assert result.status == "valid"
    assert result.errors == []


def test_timed_scene_plan_validator_blocks_missing_event_span() -> None:
    visual_event_sequence, visual_plan, timed_scene_plan = make_timed_scene_plan()
    timed_scene_plan.spans = timed_scene_plan.spans[:2]
    timed_scene_plan.spans[-1].end_seconds = 8.0
    timed_scene_plan.spans[-1].duration_seconds = 5.333

    result = TimedScenePlanValidator().validate(
        timed_scene_plan,
        visual_plan=visual_plan,
        visual_event_sequence=visual_event_sequence,
    )

    assert result.status == "blocked"
    assert (
        "TimedScenePlan spans must match VisualEventSequence event order exactly."
        in result.errors
    )


def test_timed_scene_plan_validator_blocks_overlapping_spans() -> None:
    visual_event_sequence, visual_plan, timed_scene_plan = make_timed_scene_plan()
    timed_scene_plan.spans[1].start_seconds = 2.0
    timed_scene_plan.spans[1].duration_seconds = round(
        timed_scene_plan.spans[1].end_seconds - timed_scene_plan.spans[1].start_seconds,
        3,
    )

    result = TimedScenePlanValidator().validate(
        timed_scene_plan,
        visual_plan=visual_plan,
        visual_event_sequence=visual_event_sequence,
    )

    assert result.status == "blocked"
    assert "TimedScenePlan spans must be contiguous and non-overlapping." in result.errors


def test_timed_scene_plan_validator_blocks_partial_duration_coverage() -> None:
    visual_event_sequence, visual_plan, timed_scene_plan = make_timed_scene_plan()
    timed_scene_plan.spans[-1].end_seconds = 7.5
    timed_scene_plan.spans[-1].duration_seconds = round(
        timed_scene_plan.spans[-1].end_seconds
        - timed_scene_plan.spans[-1].start_seconds,
        3,
    )

    result = TimedScenePlanValidator().validate(
        timed_scene_plan,
        visual_plan=visual_plan,
        visual_event_sequence=visual_event_sequence,
    )

    assert result.status == "blocked"
    assert "TimedScenePlan spans must cover the full scene duration." in result.errors


def test_timed_scene_plan_validator_blocks_wrong_fps() -> None:
    visual_event_sequence, visual_plan, timed_scene_plan = make_timed_scene_plan()
    timed_scene_plan.fps = 24

    result = TimedScenePlanValidator().validate(
        timed_scene_plan,
        visual_plan=visual_plan,
        visual_event_sequence=visual_event_sequence,
    )

    assert result.status == "blocked"
    assert "TimedScenePlan fps must be 30 for the MVP." in result.errors


def test_timed_scene_plan_rejects_render_fields() -> None:
    _visual_event_sequence, _visual_plan, timed_scene_plan = make_timed_scene_plan()
    payload = timed_scene_plan.model_dump()
    payload["frames"] = 240

    with pytest.raises(ValidationError):
        TimedScenePlan.model_validate(payload)
