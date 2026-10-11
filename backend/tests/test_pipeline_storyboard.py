"""Tests for StoryboardHandler and WorldCompilerHandler pipeline stages."""
from __future__ import annotations

import tempfile
from pathlib import Path
import pytest

from app.stage_handlers.storyboard_handler import StoryboardHandler
from app.stage_handlers.world_compiler_handler import WorldCompilerHandler
from artifact_store.sqlite_store import ArtifactStore
from app.stage_logger import StageLogger
from domain.validation import ValidationResult
from providers.media_storage import LocalMediaStorage
from domain.visual_intent_artifact import VisualIntentArtifact
from domain.visual_intent import VisualIntentSequence, VisualIntent, QuantitativeMeasurement
from domain.narrative_plan import NarrativePlan, SceneBeat
from domain.research_packet import ResearchPacket
from domain.voice_track import VoiceTrack, WordTimestamp
from domain.visual_world import VisualWorldSpec
from compiler.world_compiler import WorldCompiler
from compiler.world_models import CompiledWorld
from domain.storyboard_foundation import WorldFoundationSpec
from engines.scene_storyboarder_engine import SceneStoryboarderEngine, StoryboardResult
from providers.llm_provider import LLMJsonRequest, LLMJsonResponse, LLMProviderMetadata


class MockStoryboardLLMProvider:
    def __init__(self, foundation_payload: dict):
        self.foundation_payload = foundation_payload

    def generate_json(self, request: LLMJsonRequest) -> LLMJsonResponse:
        assert request.schema_name == "WorldFoundationSpec"

        return LLMJsonResponse(
            payload=self.foundation_payload,
            metadata=LLMProviderMetadata(provider="mock", model="mock"),
        )


@pytest.fixture
def test_setup():
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        db_path = tmp_path / "test.db"
        media_path = tmp_path / "media"
        media_path.mkdir(parents=True, exist_ok=True)

        store = ArtifactStore(db_path)
        store.initialize()
        media_storage = LocalMediaStorage(media_path)
        stage_logger = StageLogger()

        project = store.create_project("Test Storyboard Project")
        project_id = project.id
        run = store.create_run(project_id, "ai")
        run_id = run.id

        yield {
            "store": store,
            "media_storage": media_storage,
            "stage_logger": stage_logger,
            "project_id": project_id,
            "run_id": run_id,
        }


def test_storyboard_and_world_compiler_pipeline(test_setup):
    store = test_setup["store"]
    media_storage = test_setup["media_storage"]
    stage_logger = test_setup["stage_logger"]
    project_id = test_setup["project_id"]
    run_id = test_setup["run_id"]

    # 1. Seed prerequisite artifacts: research_packet, narrative_plan, visual_intent, voice_track
    rp = ResearchPacket(
        topic="Salary Inflation",
        audience="General",
        channel="Finance Channel",
        core_question="Why does money feel worthless?",
        verified_facts=["In 2024, living costs increased by 15%."],
    )
    store.save_artifact(
        project_id=project_id,
        run_id=run_id,
        artifact_type="research_packet",
        schema_version="1",
        payload_json=rp.model_dump(),
        parent_artifact_roles_json={},
        validation_json=ValidationResult(status="valid"),
    )

    np = NarrativePlan(
        thesis="Your salary isn't keeping up.",
        target_pain_point="Stagnant wage",
        conceptual_hook="The raise paradox",
        narrative_arc_type="expository",
        beats=[
            SceneBeat(
                beat_id="beat_01",
                scene_id="scene_01",
                title="Hook",
                focus_concept="Salary Raise",
                core_teaching_point="Explain 10% raise",
                narrative_function="hook",
                emotional_tone="curious",
            )
        ],
    )
    store.save_artifact(
        project_id=project_id,
        run_id=run_id,
        artifact_type="narrative_plan",
        schema_version="1",
        payload_json=np.model_dump(),
        parent_artifact_roles_json={},
        validation_json=ValidationResult(status="valid"),
    )

    from domain.visual_intent_artifact import build_visual_intent_provenance
    seq = VisualIntentSequence(
        idea_id="idea_01",
        narration="Your salary increases by ten percent today.",
        intents=[
            VisualIntent(
                intent_id="intent_01",
                narration_excerpt="Your salary increases by ten percent today.",
                what_viewer_must_understand="Salary grows less than costs.",
                measurements=[QuantitativeMeasurement(raw_value="10%", numeric_value=10.0, unit="%")],
            )
        ],
    )
    vi = VisualIntentArtifact(
        sequences=[seq],
        provenance=build_visual_intent_provenance(seq, source_kind="idea"),
    )
    store.save_artifact(
        project_id=project_id,
        run_id=run_id,
        artifact_type="visual_intent",
        schema_version="1",
        payload_json=vi.model_dump(),
        parent_artifact_roles_json={},
        validation_json=ValidationResult(status="valid"),
    )

    vt = VoiceTrack(
        voice_id="Matthew",
        audio_file_name="narration.mp3",
        storage_key="test_audio.mp3",
        duration_seconds=4.0,
        full_script_text="Your salary increases by ten percent today.",
        word_timestamps=[
            WordTimestamp(word="Your", start_ms=0, end_ms=300),
            WordTimestamp(word="salary", start_ms=300, end_ms=800),
            WordTimestamp(word="increases", start_ms=800, end_ms=1400),
            WordTimestamp(word="by", start_ms=1400, end_ms=1600),
            WordTimestamp(word="ten", start_ms=1600, end_ms=2000),
            WordTimestamp(word="percent", start_ms=2000, end_ms=2600),
            WordTimestamp(word="today", start_ms=2600, end_ms=3200),
        ],
    )
    store.save_artifact(
        project_id=project_id,
        run_id=run_id,
        artifact_type="voice_track",
        schema_version="1",
        payload_json=vt.model_dump(),
        parent_artifact_roles_json={},
        validation_json=ValidationResult(status="valid"),
    )

    foundation_payload = {
        "world_id": "salary_inflation_world",
        "beats": [
            {
                "beat_id": "beat_01",
                "narration": "Your salary increases by ten percent today.",
                "visual_goal": "Show the salary increase clearly.",
                "visual_strategy": "Keep the salary metric prominent inside the existing visual world.",
                "source_intent_ids": ["intent_01"],
                "elements": [
                    {
                        "object_id": "root_card",
                        "primitive_type": "group",
                        "parent_object_id": None,
                        "semantic_content": {},
                        "lifecycle_mode": "persistent",
                        "role": "primary",
                        "macro_zone": "center",
                        "actions": [
                            {
                                "action_id": "enter_card",
                                "action_type": "enter",
                                "motion_preset": "reveal",
                                "order": 1,
                                "trigger_word": "Your",
                                "target_property": None,
                                "new_value": None,
                                "description": "Reveal root card container.",
                            }
                        ],
                    },
                    {
                        "object_id": "salary_metric",
                        "primitive_type": "number",
                        "parent_object_id": "root_card",
                        "semantic_content": {"value": 10.0, "suffix": "%"},
                        "lifecycle_mode": "persistent",
                        "role": "primary",
                        "macro_zone": "center",
                        "actions": [
                            {
                                "action_id": "enter_salary",
                                "action_type": "enter",
                                "motion_preset": "impact",
                                "order": 2,
                                "trigger_word": "salary",
                                "target_property": None,
                                "new_value": None,
                                "description": "Reveal the salary metric when the narration reaches the word salary.",
                            }
                        ],
                    },
                ],
                "state_change_events": [],
                "transition_kind": "introduce_world",
            }
        ],
    }

    
    mock_llm = MockStoryboardLLMProvider(foundation_payload)

    # 2. Run StoryboardHandler
    sb_handler = StoryboardHandler(
        store=store,
        llm_provider=mock_llm,
        stage_logger=stage_logger,
    )
    sb_artifact = sb_handler.run(project_id, run_id)
    assert sb_artifact.artifact_type == "storyboard"
    assert sb_artifact.status == "valid"
    assert sb_artifact.payload_json["world_id"] == "salary_inflation_world"

    # 3. Run WorldCompilerHandler
    compiler_handler = WorldCompilerHandler(
        store=store,
        media_storage=media_storage,
        stage_logger=stage_logger,
    )
    compiled_artifact = compiler_handler.run(project_id, run_id)
    assert compiled_artifact.artifact_type == "compiled_world"
    assert compiled_artifact.status == "valid"
    assert compiled_artifact.payload_json["world_id"] == "salary_inflation_world"
    assert len(compiled_artifact.payload_json["primitives"]) >= 2
    assert len(compiled_artifact.payload_json["speech_anchors"]) >= 1
