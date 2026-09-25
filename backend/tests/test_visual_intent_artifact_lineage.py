"""Focused tests for the persisted VisualIntent source-of-truth contract."""
from pathlib import Path

import pytest

from app.stage_handlers.script_visual_strategy_handler import ScriptVisualStrategyHandler
from app.stage_logger import StageLogger
from artifact_store.sqlite_store import ArtifactStore
from domain.composition_plan import CompositionBeat
from domain.script_visual_strategy import ScriptVisualStrategy, VideoIdea
from domain.validation import ValidationResult
from domain.visual_intent import (
    ComparisonStructure,
    QuantitativeMeasurement,
    VisualIntent,
    VisualIntentSequence,
)
from domain.visual_intent_artifact import (
    VisualIntentArtifact,
    build_visual_intent_provenance,
)
from engines.composition_planner_engine import (
    CompositionPlannerEngine,
    CompositionPlannerEngineError,
)
from engines.script_visual_strategy_engine import ScriptVisualStrategyResult
from engines.visual_intent_engine import VisualIntentResult
from providers.llm_provider import LLMJsonRequest, LLMJsonResponse, LLMProviderMetadata
from domain.validators.script_visual_strategy_validator import ScriptVisualStrategyValidator


def _metadata() -> LLMProviderMetadata:
    return LLMProviderMetadata(provider="test", model="test")


class _CompositionFiller:
    def generate_json(self, request: LLMJsonRequest) -> LLMJsonResponse:
        if request.schema_name.endswith("metric_hero"):
            payload = {"value": "₹50 lakh", "label": "Starting Portfolio"}
        elif request.schema_name.endswith("calculation_story"):
            payload = {
                "input_label": "Investment",
                "input_value": "₹10 lakh",
                "result_label": "Ending Value",
                "result_value": "₹20 lakh",
            }
        else:
            payload = {"caption": "Numbers matter"}
        return LLMJsonResponse(payload=payload, metadata=_metadata())


def _save_prerequisites(store: ArtifactStore, project_id: str, run_id: str) -> None:
    store.save_artifact(
        project_id=project_id,
        run_id=run_id,
        artifact_type="generate_video_request",
        schema_version="1",
        payload_json={"visual_mode": "composition", "duration_profile": "short_2min"},
        parent_artifact_roles_json={},
        validation_json=ValidationResult(status="valid"),
    )
    store.save_artifact(
        project_id=project_id,
        run_id=run_id,
        artifact_type="hook",
        schema_version="1",
        payload_json={
            "conceptual_hook": "A measurable starting point",
            "script_text": "Start with ₹50 lakh.",
            "visual_directives": [],
        },
        parent_artifact_roles_json={},
        validation_json=ValidationResult(status="valid"),
    )
    store.save_artifact(
        project_id=project_id,
        run_id=run_id,
        artifact_type="narrative_plan",
        schema_version="1",
        payload_json={
            "thesis": "Numbers matter",
            "target_pain_point": "Unclear math",
            "conceptual_hook": "A measurable starting point",
            "narrative_arc_type": "educational",
            "scene_beats": [],
        },
        parent_artifact_roles_json={},
        validation_json=ValidationResult(status="valid"),
    )
    store.save_artifact(
        project_id=project_id,
        run_id=run_id,
        artifact_type="research_packet",
        schema_version="1",
        payload_json={
            "topic": "Financial math",
            "audience": "investors",
            "channel": "Wealth Unpacked",
            "concepts": ["calculation"],
        },
        parent_artifact_roles_json={},
        validation_json=ValidationResult(status="valid"),
    )


def test_visual_intent_artifact_persists_and_beats_reference_it(tmp_path: Path) -> None:
    store = ArtifactStore(tmp_path / "lineage.db")
    store.initialize()
    project = store.create_project("Intent lineage")
    run = store.create_run(project.id)
    _save_prerequisites(store, project.id, run.id)

    hook_sequence = VisualIntentSequence(
        idea_id="hook",
        narration="Start with ₹50 lakh.",
        intents=[
            VisualIntent(
                intent_id="hook_intent_01",
                narration_excerpt="Start with ₹50 lakh.",
                what_viewer_must_understand="The starting portfolio is ₹50 lakh.",
                relationship_type="metric",
                measurements=[
                    QuantitativeMeasurement(
                        raw_value="₹50 lakh",
                        metric_name="Starting Portfolio",
                        role="input",
                    )
                ],
            )
        ],
    )
    body_sequence = VisualIntentSequence(
        idea_id="idea_01",
        narration="Invest ₹10 lakh and reach ₹20 lakh.",
        intents=[
            VisualIntent(
                intent_id="intent_01",
                narration_excerpt="Invest ₹10 lakh and reach ₹20 lakh.",
                what_viewer_must_understand="₹10 lakh becomes ₹20 lakh.",
                relationship_type="calculation",
                measurements=[
                    QuantitativeMeasurement(
                        raw_value="₹10 lakh",
                        metric_name="Investment",
                        role="input",
                    ),
                    QuantitativeMeasurement(
                        raw_value="₹20 lakh",
                        metric_name="Ending Value",
                        role="result",
                    ),
                ],
            )
        ],
    )

    class StubIntentEngine:
        def run(self, *, idea_id: str, **_: object) -> VisualIntentResult:
            sequence = hook_sequence if idea_id == "hook" else body_sequence
            return VisualIntentResult(
                sequence=sequence,
                provider_metadata=_metadata(),
                raw_payload=sequence.model_dump(),
            )

    strategy = ScriptVisualStrategy(
        thesis="Numbers matter",
        ideas=[
            VideoIdea(
                idea_id="idea_01",
                title="The math",
                focus_concept="calculation",
                core_teaching_point="Show the transformation",
                narration=body_sequence.narration,
            )
        ],
    )

    class StubStrategyEngine:
        def run(self, *_: object, **__: object) -> ScriptVisualStrategyResult:
            return ScriptVisualStrategyResult(
                strategy=strategy,
                provider_metadata=_metadata(),
                raw_payload=strategy.model_dump(),
            )

    artifact = ScriptVisualStrategyHandler(
        store=store,
        strategy_engine=StubStrategyEngine(),  # type: ignore[arg-type]
        strategy_validator=ScriptVisualStrategyValidator(),
        stage_logger=StageLogger(),
        visual_intent_engine=StubIntentEngine(),  # type: ignore[arg-type]
        composition_planner_engine=CompositionPlannerEngine(llm_provider=_CompositionFiller()),  # type: ignore[arg-type]
    ).run(project.id, run.id)

    visual_artifact = store.find_artifact_by_type(project.id, run.id, "visual_intent")
    assert visual_artifact is not None
    persisted = VisualIntentArtifact.model_validate(visual_artifact.payload_json)
    assert {sequence.idea_id for sequence in persisted.sequences} == {"hook", "idea_01"}
    assert persisted.provenance[1].source_text_sha256
    assert artifact.parent_artifact_roles_json["visual_intent"] == visual_artifact.id

    plan = artifact.payload_json["composition_plan"]
    hook_beat = plan["hook_plan"]["beats"][0]
    body_beat = plan["ideas"][0]["beats"][0]
    for beat, intent_id, idea_id in (
        (hook_beat, "hook_intent_01", "hook"),
        (body_beat, "intent_01", "idea_01"),
    ):
        assert beat["source_intent_id"] == intent_id
        assert beat["source_idea_id"] == idea_id
        assert beat["source_visual_intent_artifact_id"] == visual_artifact.id

    assert body_beat["source_narration_excerpt"] == body_sequence.intents[0].narration_excerpt

    assert body_beat["composition_data"]["input_value"] == "₹10 lakh"
    assert body_beat["composition_data"]["result_value"] == "₹20 lakh"


def test_visual_intent_provenance_rejects_non_verbatim_source_span() -> None:
    sequence = VisualIntentSequence(
        idea_id="idea_01",
        narration="Invest ₹10 lakh.",
        intents=[
            VisualIntent(
                intent_id="intent_01",
                narration_excerpt="Invest ₹10 lakh.",
                what_viewer_must_understand="Invest ₹10 lakh.",
                relationship_type="statement",
            )
        ],
    )
    provenance = build_visual_intent_provenance(sequence, source_kind="idea")
    provenance[0].excerpt_start = 1
    with pytest.raises(ValueError, match="does not match"):
        VisualIntentArtifact(sequences=[sequence], provenance=provenance)


def test_missing_calculation_fact_is_rejected_without_placeholder() -> None:
    with pytest.raises(ValueError, match="calculation.*result"):
        VisualIntent(
            intent_id="calc_01",
            narration_excerpt="Invest ₹10 lakh and reach an amount.",
            what_viewer_must_understand="The result is not stated.",
            relationship_type="calculation",
            measurements=[
                QuantitativeMeasurement(
                    raw_value="₹10 lakh",
                    metric_name="Investment",
                    role="input",
                )
            ],
        )


def test_composition_beat_rejects_partial_source_reference() -> None:
    with pytest.raises(ValueError, match="source reference"):
        CompositionBeat(
            beat_id="beat_01",
            composition_id="metric_hero",
            source_intent_id="intent_01",
        )


def test_comparison_with_missing_values_is_rejected_without_fabrication() -> None:
    intent = VisualIntent(
        intent_id="comparison_01",
        narration_excerpt="A and B are different.",
        what_viewer_must_understand="The values are not stated.",
        relationship_type="comparison",
        comparison=ComparisonStructure(
            subject_a="A",
            value_a="",
            subject_b="B",
            value_b="",
            comparison_dimension="Return",
        ),
    )

    with pytest.raises(CompositionPlannerEngineError, match="comparison"):
        CompositionPlannerEngine().run(
            intent=intent,
            beat_id="beat_01",
            source_idea_id="idea_01",
            source_visual_intent_artifact_id="artifact_intent",
        )
