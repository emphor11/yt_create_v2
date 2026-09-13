"""
Tests for the complete end-to-end composition pipeline path:
ScriptVisualStrategyHandler (composition mode) -> VideoAssemblyHandler -> RenderSpec.
"""
from pathlib import Path
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

from app.dependencies import get_artifact_store, get_pipeline_service
from app.main import create_app
from app.pipeline_service import build_pipeline_service
from artifact_store.sqlite_store import ArtifactStore
from domain.composition_plan import (
    CompositionBeat,
    FullCompositionPlan,
    HookCompositionPlan,
    IdeaCompositionPlan,
)
from domain.validation import ValidationResult
from domain.validators.render_spec_validator import RenderSpecValidator
from providers.media_storage import LocalMediaStorage


def test_composition_path_produces_valid_renderspec(tmp_path: Path):
    store = ArtifactStore(tmp_path / "comp_pipeline_test.db")
    store.initialize()

    media_path = tmp_path / "media"
    media_storage = LocalMediaStorage(media_path)

    app = create_app()
    app.dependency_overrides[get_artifact_store] = lambda: store
    app.dependency_overrides[get_pipeline_service] = lambda: build_pipeline_service(
        store,
        media_storage=media_storage,
        llm_provider=None,
    )
    client = TestClient(app)

    # 1. Create project
    project = store.create_project("Composition Pipeline Test")
    run = store.create_run(project.id, mode="ai")

    # 2. Save GenerateVideoRequest with visual_mode=composition
    store.save_artifact(
        project_id=project.id,
        run_id=run.id,
        artifact_type="generate_video_request",
        schema_version="1",
        payload_json={
            "topic": "Retirement Math",
            "audience": "retail investors",
            "language": "English",
            "style": "educational",
            "channel": "FinanceChannel",
            "duration_profile": "short_2min",
            "visual_mode": "composition",
        },
        parent_artifact_roles_json={},
        validation_json=ValidationResult(status="valid"),
    )

    # 3. Save Hook
    store.save_artifact(
        project_id=project.id,
        run_id=run.id,
        artifact_type="hook",
        schema_version="1",
        payload_json={
            "conceptual_hook": "The Safe Withdrawal Rule",
            "script_text": "Imagine retiring with fifty lakh.",
            "visual_directives": [
                {
                    "beat_id": "hook_beat_1",
                    "preferred_component": "Typography",
                    "visual_instruction": "Show starting retirement portfolio",
                    "component_data": {
                        "text": "The 4% Retirement Rule",
                        "subtitle": "Is your nest egg truly safe?",
                    },
                }
            ],
        },
        parent_artifact_roles_json={},
        validation_json=ValidationResult(status="valid"),
    )

    # 4. Save ScriptVisualStrategy with composition_plan
    comp_plan = FullCompositionPlan(
        thesis="Retirement calculations require real-world stress testing.",
        visual_mode="composition",
        hook_plan=HookCompositionPlan(
            hook_id="hook",
            narration="Imagine retiring with fifty lakh.",
            beats=[
                CompositionBeat(
                    beat_id="hook_beat_1",
                    composition_id="metric_hero",
                    variant="hero",
                    composition_data={
                        "value": "₹50 Lakh",
                        "label": "Starting Retirement Portfolio",
                        "context": "Is your nest egg safe?",
                        "emphasis": "hero",
                    },
                    trigger_word=None,
                    visual_goal="Opening metric hero",
                )
            ],
        ),
        ideas=[
            IdeaCompositionPlan(
                idea_id="idea_01",
                narration="You retire with fifty lakh. A four percent withdrawal yields two lakh annually. But inflation eats away at this purchasing power.",
                beats=[
                    CompositionBeat(
                        beat_id="beat_01_01",
                        composition_id="metric_hero",
                        variant="hero",
                        composition_data={
                            "value": "₹50 lakh",
                            "label": "Starting Retirement Portfolio",
                            "context": "Initial Nest Egg",
                            "emphasis": "hero",
                        },
                        trigger_word=None,
                        visual_goal="Show ₹50 lakh hero opening metric",
                    ),
                    CompositionBeat(
                        beat_id="beat_01_02",
                        composition_id="calculation_story",
                        variant=None,
                        composition_data={
                            "input_label": "Portfolio",
                            "input_value": "₹50 lakh",
                            "operation_label": "×",
                            "rate_label": "4% withdrawal rate",
                            "result_label": "Annual Income",
                            "result_value": "₹2 lakh / yr",
                            "note": "Safe Withdrawal Benchmark",
                        },
                        trigger_word="four",
                        visual_goal="Show the 4% calculation",
                    ),
                    CompositionBeat(
                        beat_id="beat_01_03",
                        composition_id="time_decay",
                        variant=None,
                        composition_data={
                            "fixed_amount": "₹2 lakh",
                            "amount_label": "Annual Withdrawal",
                            "time_period": "15 Years Later",
                            "emphasis": "purchasing_power_decline",
                            "annotation": "Purchasing power drops by 48%",
                            "show_chart": True,
                        },
                        trigger_word="inflation",
                        visual_goal="Show purchasing power decline",
                    ),
                ],
            )
        ],
    )

    store.save_artifact(
        project_id=project.id,
        run_id=run.id,
        artifact_type="script_visual_strategy",
        schema_version="1",
        payload_json={
            "schema_version": "1",
            "visual_mode": "composition",
            "thesis": "Retirement calculations require real-world stress testing.",
            "ideas": [
                {
                    "idea_id": "idea_01",
                    "title": "The Math",
                    "focus_concept": "4% Rule",
                    "core_teaching_point": "Inflation decays fixed withdrawals.",
                    "narration": "You retire with fifty lakh. A four percent withdrawal yields two lakh annually. But inflation eats away at this purchasing power.",
                    "visual_sequence": [
                        {
                            "beat_id": "beat_01_01",
                            "preferred_component": "Typography",
                            "visual_goal": "Opening metric",
                            "trigger_word": None,
                            "component_data": {"text": "₹50 lakh"},
                        },
                        {
                            "beat_id": "beat_01_02",
                            "preferred_component": "Typography",
                            "visual_goal": "Calculation",
                            "trigger_word": "four",
                            "component_data": {"text": "4% = ₹2L"},
                        },
                        {
                            "beat_id": "beat_01_03",
                            "preferred_component": "Typography",
                            "visual_goal": "Decay",
                            "trigger_word": "inflation",
                            "component_data": {"text": "Decay"},
                        },
                    ],
                }
            ],
            "composition_plan": comp_plan.model_dump(),
        },
        parent_artifact_roles_json={},
        validation_json=ValidationResult(status="valid"),
    )

    # 5. Create dummy voice track file via media_storage
    audio_path = media_storage.path_for_key("narration.mp3")
    audio_path.parent.mkdir(parents=True, exist_ok=True)
    audio_path.write_bytes(b"\x00" * 1000)

    store.save_artifact(
        project_id=project.id,
        run_id=run.id,
        artifact_type="voice_track",
        schema_version="1",
        payload_json={
            "voice_id": "Joanna",
            "audio_file_name": "narration.mp3",
            "storage_key": "narration.mp3",
            "duration_seconds": 12.0,
            "full_script_text": "Imagine retiring with fifty lakh. You retire with fifty lakh. A four percent withdrawal yields two lakh annually. But inflation eats away at this purchasing power.",
            "word_timestamps": [
                {"word": "You", "start_ms": 0, "end_ms": 300},
                {"word": "retire", "start_ms": 400, "end_ms": 800},
                {"word": "with", "start_ms": 900, "end_ms": 1100},
                {"word": "fifty", "start_ms": 1200, "end_ms": 1500},
                {"word": "lakh", "start_ms": 1600, "end_ms": 2000},
                {"word": "A", "start_ms": 2200, "end_ms": 2400},
                {"word": "four", "start_ms": 2500, "end_ms": 2900},
                {"word": "percent", "start_ms": 3000, "end_ms": 3400},
                {"word": "withdrawal", "start_ms": 3500, "end_ms": 4100},
                {"word": "yields", "start_ms": 4200, "end_ms": 4600},
                {"word": "two", "start_ms": 4700, "end_ms": 5000},
                {"word": "lakh", "start_ms": 5100, "end_ms": 5500},
                {"word": "annually", "start_ms": 5600, "end_ms": 6200},
                {"word": "But", "start_ms": 6400, "end_ms": 6600},
                {"word": "inflation", "start_ms": 6700, "end_ms": 7300},
                {"word": "eats", "start_ms": 7400, "end_ms": 7700},
                {"word": "away", "start_ms": 7800, "end_ms": 8100},
                {"word": "at", "start_ms": 8200, "end_ms": 8400},
                {"word": "this", "start_ms": 8500, "end_ms": 8800},
                {"word": "purchasing", "start_ms": 8900, "end_ms": 9500},
                {"word": "power", "start_ms": 9600, "end_ms": 10200},
            ],
        },
        parent_artifact_roles_json={},
        validation_json=ValidationResult(status="valid"),
    )

    # 6. Execute VideoAssembly stage
    service = build_pipeline_service(store, media_storage=media_storage)
    result_artifact = service.run_stage("video_assembly", project.id, run.id)

    assert result_artifact.status == "valid"
    assert result_artifact.artifact_type == "render_spec"

    payload = result_artifact.payload_json
    assert payload["composition"] == "VideoAssembly"

    scenes = payload["props"]["scenes"]
    # 1 hook scene + 3 composition idea scenes = 4 scenes total
    assert len(scenes) == 4

    # Scene 0: Hook scene resolved through CompositionResolver
    assert scenes[0]["component"]["component_id"] == "MetricHero"
    assert scenes[0]["component"]["props"]["value"] == "₹50 Lakh"
    assert scenes[0]["component"]["props"]["context"] == "Is your nest egg safe?"

    # Scene 1: MetricHero
    assert scenes[1]["component"]["component_id"] == "MetricHero"
    assert scenes[1]["component"]["props"]["value"] == "₹50 lakh"
    assert scenes[1]["component"]["props"]["context"] == "Initial Nest Egg"

    # Scene 2: CalculationStory
    assert scenes[2]["component"]["component_id"] == "CalculationStory"
    assert scenes[2]["component"]["props"]["inputLabel"] == "Portfolio"
    assert scenes[2]["component"]["props"]["resultValue"] == "₹2 lakh / yr"

    # Scene 3: TimeDecay
    assert scenes[3]["component"]["component_id"] == "TimeDecay"
    assert scenes[3]["component"]["props"]["fixedAmount"] == "₹2 lakh"
    assert scenes[3]["component"]["props"]["timePeriod"] == "15 Years Later"
    assert scenes[3]["component"]["props"]["annotation"] == "Purchasing power drops by 48%"

    # Validate the full RenderSpec structure with the official validator
    from domain.render_spec import RenderSpec
    render_spec_model = RenderSpec.model_validate(payload)
    validation = RenderSpecValidator().validate(render_spec_model)
    assert validation.status == "valid"
    assert len(validation.errors) == 0


def test_composition_path_hook_legacy_fallback_when_hook_plan_none(tmp_path: Path):
    """When hook_plan is None, CompositionAssemblyEngine falls back to legacy component resolution for Hook."""
    store = ArtifactStore(tmp_path / "comp_fallback_test.db")
    store.initialize()

    media_path = tmp_path / "media"
    media_storage = LocalMediaStorage(media_path)

    project = store.create_project("Composition Pipeline Fallback Test")
    run = store.create_run(project.id, mode="ai")

    store.save_artifact(
        project_id=project.id,
        run_id=run.id,
        artifact_type="generate_video_request",
        schema_version="1",
        payload_json={
            "topic": "Retirement Math",
            "audience": "retail investors",
            "language": "English",
            "style": "educational",
            "channel": "FinanceChannel",
            "duration_profile": "short_2min",
            "visual_mode": "composition",
        },
        parent_artifact_roles_json={},
        validation_json=ValidationResult(status="valid"),
    )

    store.save_artifact(
        project_id=project.id,
        run_id=run.id,
        artifact_type="hook",
        schema_version="1",
        payload_json={
            "conceptual_hook": "The Safe Withdrawal Rule",
            "script_text": "Imagine retiring with fifty lakh.",
            "visual_directives": [
                {
                    "beat_id": "hook_beat_1",
                    "preferred_component": "Typography",
                    "visual_instruction": "Show starting retirement portfolio",
                    "component_data": {
                        "text": "The 4% Retirement Rule",
                        "subtitle": "Is your nest egg truly safe?",
                    },
                }
            ],
        },
        parent_artifact_roles_json={},
        validation_json=ValidationResult(status="valid"),
    )

    comp_plan = FullCompositionPlan(
        thesis="Retirement calculations require real-world stress testing.",
        visual_mode="composition",
        hook_plan=None,  # Legacy fallback: no hook_plan
        ideas=[
            IdeaCompositionPlan(
                idea_id="idea_01",
                narration="You retire with fifty lakh.",
                beats=[
                    CompositionBeat(
                        beat_id="beat_01_01",
                        composition_id="metric_hero",
                        variant="hero",
                        composition_data={
                            "value": "₹50 lakh",
                            "label": "Starting Retirement Portfolio",
                            "context": "Initial Nest Egg",
                            "emphasis": "hero",
                        },
                        trigger_word=None,
                        visual_goal="Show ₹50 lakh hero opening metric",
                    ),
                ],
            )
        ],
    )

    store.save_artifact(
        project_id=project.id,
        run_id=run.id,
        artifact_type="script_visual_strategy",
        schema_version="1",
        payload_json={
            "schema_version": "1",
            "visual_mode": "composition",
            "thesis": "Retirement calculations require real-world stress testing.",
            "ideas": [
                {
                    "idea_id": "idea_01",
                    "title": "The Math",
                    "focus_concept": "4% Rule",
                    "core_teaching_point": "Inflation decays fixed withdrawals.",
                    "narration": "You retire with fifty lakh.",
                    "visual_sequence": [
                        {
                            "beat_id": "beat_01_01",
                            "preferred_component": "Typography",
                            "visual_goal": "Opening metric",
                            "trigger_word": None,
                            "component_data": {"text": "₹50 lakh"},
                        },
                    ],
                }
            ],
            "composition_plan": comp_plan.model_dump(),
        },
        parent_artifact_roles_json={},
        validation_json=ValidationResult(status="valid"),
    )

    audio_path = media_storage.path_for_key("narration.mp3")
    audio_path.parent.mkdir(parents=True, exist_ok=True)
    audio_path.write_bytes(b"\x00" * 1000)

    store.save_artifact(
        project_id=project.id,
        run_id=run.id,
        artifact_type="voice_track",
        schema_version="1",
        payload_json={
            "voice_id": "Joanna",
            "audio_file_name": "narration.mp3",
            "storage_key": "narration.mp3",
            "duration_seconds": 6.0,
            "full_script_text": "Imagine retiring with fifty lakh. You retire with fifty lakh.",
            "word_timestamps": [
                {"word": "Imagine", "start_ms": 0, "end_ms": 300},
                {"word": "retiring", "start_ms": 400, "end_ms": 800},
                {"word": "with", "start_ms": 900, "end_ms": 1100},
                {"word": "fifty", "start_ms": 1200, "end_ms": 1500},
                {"word": "lakh", "start_ms": 1600, "end_ms": 2000},
                {"word": "You", "start_ms": 2200, "end_ms": 2500},
                {"word": "retire", "start_ms": 2600, "end_ms": 2900},
                {"word": "with", "start_ms": 3000, "end_ms": 3300},
                {"word": "fifty", "start_ms": 3400, "end_ms": 3700},
                {"word": "lakh", "start_ms": 3800, "end_ms": 4200},
            ],
        },
        parent_artifact_roles_json={},
        validation_json=ValidationResult(status="valid"),
    )

    service = build_pipeline_service(store, media_storage=media_storage)
    result_artifact = service.run_stage("video_assembly", project.id, run.id)
    assert result_artifact.status == "valid"

    scenes = result_artifact.payload_json["props"]["scenes"]
    assert len(scenes) == 2
    # Scene 0: Hook scene should fall back to legacy Typography
    assert scenes[0]["component"]["component_id"] == "Typography"
    # Scene 1: Idea scene should be MetricHero
    assert scenes[1]["component"]["component_id"] == "MetricHero"
