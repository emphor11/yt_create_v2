import pytest
from pydantic import ValidationError

from domain.render_spec import RenderSpec
from domain.semantic_scene import SemanticEntity, SemanticRelationship, SemanticScene
from domain.timed_scene_plan import TimedScenePlan
from domain.validators.render_spec_validator import RenderSpecValidator
from domain.visual_event_sequence import VisualEvent, VisualEventSequence
from domain.visual_plan import VisualPlan
from engines.render_spec_engine import RenderSpecEngine
from engines.timing_engine import TimingEngine
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


def make_render_spec() -> tuple[VisualPlan, TimedScenePlan, RenderSpec]:
    semantic_scene = make_semantic_scene()
    visual_event_sequence = make_visual_event_sequence()
    visual_plan = VisualPlanEngine(ComponentRegistry()).run(
        semantic_scene=semantic_scene,
        visual_event_sequence=visual_event_sequence,
    )
    timed_scene_plan = TimingEngine().run(
        visual_plan=visual_plan,
        visual_event_sequence=visual_event_sequence,
    )
    render_spec = RenderSpecEngine().run(
        visual_plan=visual_plan,
        timed_scene_plan=timed_scene_plan,
    )
    return visual_plan, timed_scene_plan, render_spec


def test_render_spec_engine_converts_timing_to_frames_and_copies_visual_plan() -> None:
    visual_plan, _timed_scene_plan, render_spec = make_render_spec()

    assert render_spec.scene_id == "scene_01"
    assert render_spec.composition == "SplitComparison"
    assert render_spec.composition == visual_plan.component
    assert render_spec.props == visual_plan.props
    assert render_spec.fps == 30
    assert render_spec.duration_frames == 240
    assert [
        (span.event_id, span.start_frame, span.end_frame, span.duration_frames)
        for span in render_spec.frame_spans
    ] == [
        ("event_full_price", 0, 80, 80),
        ("event_monthly_payment", 80, 160, 80),
        ("event_attention_shift", 160, 240, 80),
    ]


def test_render_spec_validator_accepts_mvp_spec() -> None:
    visual_plan, timed_scene_plan, render_spec = make_render_spec()

    result = RenderSpecValidator().validate(
        render_spec,
        visual_plan=visual_plan,
        timed_scene_plan=timed_scene_plan,
    )

    assert result.status == "valid"
    assert result.errors == []


def test_render_spec_validator_blocks_component_change() -> None:
    visual_plan, timed_scene_plan, render_spec = make_render_spec()
    render_spec.composition = "OtherComposition"

    result = RenderSpecValidator().validate(
        render_spec,
        visual_plan=visual_plan,
        timed_scene_plan=timed_scene_plan,
    )

    assert result.status == "blocked"
    assert "RenderSpec composition must be copied from VisualPlan component." in result.errors


def test_render_spec_validator_blocks_prop_change() -> None:
    visual_plan, timed_scene_plan, render_spec = make_render_spec()
    render_spec.props.left.value = 79000

    result = RenderSpecValidator().validate(
        render_spec,
        visual_plan=visual_plan,
        timed_scene_plan=timed_scene_plan,
    )

    assert result.status == "blocked"
    assert "RenderSpec props must exactly match VisualPlan props." in result.errors


def test_render_spec_validator_blocks_wrong_frame_conversion() -> None:
    visual_plan, timed_scene_plan, render_spec = make_render_spec()
    render_spec.frame_spans[1].start_frame = 81
    render_spec.frame_spans[1].duration_frames = (
        render_spec.frame_spans[1].end_frame - render_spec.frame_spans[1].start_frame
    )

    result = RenderSpecValidator().validate(
        render_spec,
        visual_plan=visual_plan,
        timed_scene_plan=timed_scene_plan,
    )

    assert result.status == "blocked"
    assert "RenderSpec frame spans must be contiguous and non-overlapping." in result.errors
    assert (
        "Render frame span event_monthly_payment start_frame must match TimedScenePlan."
        in result.errors
    )


def test_render_spec_validator_blocks_partial_frame_coverage() -> None:
    visual_plan, timed_scene_plan, render_spec = make_render_spec()
    render_spec.frame_spans[-1].end_frame = 239
    render_spec.frame_spans[-1].duration_frames = (
        render_spec.frame_spans[-1].end_frame
        - render_spec.frame_spans[-1].start_frame
    )

    result = RenderSpecValidator().validate(
        render_spec,
        visual_plan=visual_plan,
        timed_scene_plan=timed_scene_plan,
    )

    assert result.status == "blocked"
    assert "RenderSpec frame spans must cover the full render duration." in result.errors


def test_render_spec_rejects_video_output_fields() -> None:
    _visual_plan, _timed_scene_plan, render_spec = make_render_spec()
    payload = render_spec.model_dump()
    payload["storage_key"] = "projects/p1/runs/r1/scene_01.mp4"

    with pytest.raises(ValidationError):
        RenderSpec.model_validate(payload)


def test_render_spec_rejects_semantic_payload_fields() -> None:
    _visual_plan, _timed_scene_plan, render_spec = make_render_spec()
    payload = render_spec.model_dump()
    payload["semantic_scene"] = {"scene_id": "scene_01"}

    with pytest.raises(ValidationError):
        RenderSpec.model_validate(payload)
