from __future__ import annotations

import pytest
from pathlib import Path
import tempfile

from artifact_store.sqlite_store import ArtifactStore
from domain.generate_video_request import GenerateVideoRequest, VisualMode
from domain.research_packet import ResearchPacket
from domain.script_visual_strategy import ScriptVisualStrategy, VideoIdea
from domain.voice_track import VoiceTrack, WordTimestamp
from domain.validation import ValidationResult
from domain.pipeline_stage import PipelineStage
from app.pipeline_service import build_pipeline_service
from app.stage_handlers.continuous_story_handler import ContinuousStoryHandler


@pytest.fixture
def temp_store():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_pipeline.db"
        store = ArtifactStore(db_path)
        store.initialize()
        yield store


@pytest.fixture
def sample_draft_dict():
    return {
        "story_id": "test_loan_story",
        "objects": [
            {
                "id": "loan_card",
                "type": "card",
                "layout": "center",
                "purpose": "Context card",
                "value_fact_id": "loan_principal",
                "title": "Home Loan Principal",
            },
        ],
        "events": [
            {
                "action": "enter",
                "target_id": "loan_card",
                "anchor": "50 lakh",
            }
        ],
    }


def seed_prerequisite_artifacts(store: ArtifactStore, visual_mode: VisualMode = VisualMode.CONTINUOUS_STORY) -> tuple[str, str]:
    project = store.create_project("Test Project")
    run = store.create_run(project.id)
    project_id = project.id
    run_id = run.id

    # 1. GenerateVideoRequest
    gen_req = GenerateVideoRequest(
        topic="Home Loan Rate Hike",
        visual_mode=visual_mode,
    )
    store.save_artifact(
        project_id=project_id,
        run_id=run_id,
        artifact_type="generate_video_request",
        schema_version=gen_req.schema_version,
        payload_json=gen_req.model_dump(),
        parent_artifact_roles_json={},
        validation_json=ValidationResult(status="valid"),
    )

    # 2. ResearchPacket with approved_facts
    approved_facts = {
        "loan_principal": {
            "label": "Home Loan Principal",
            "value": 5000000,
            "format": "currency_inr",
        }
    }
    research = ResearchPacket(
        topic="Home Loan Rate Hike",
        audience="borrowers",
        channel="Finance",
        verified_facts=["50 Lakh home loan starts at 8.5%"],
    )
    res_payload = research.model_dump()
    res_payload["approved_facts"] = approved_facts
    store.save_artifact(
        project_id=project_id,
        run_id=run_id,
        artifact_type="research_packet",
        schema_version=research.schema_version,
        payload_json=res_payload,
        parent_artifact_roles_json={},
        validation_json=ValidationResult(status="valid"),
    )

    # 3. ScriptVisualStrategy
    strategy = ScriptVisualStrategy(
        thesis="Rate hikes severely increase interest costs.",
        ideas=[
            VideoIdea(
                idea_id="idea_01",
                title="Loan baseline",
                focus_concept="Principal",
                core_teaching_point="Starting loan amount",
                narration="A 50 lakh rupee home loan starts at 8.5 percent interest.",
            )
        ],
    )
    strat_payload = strategy.model_dump()
    strat_payload["approved_facts"] = approved_facts
    store.save_artifact(
        project_id=project_id,
        run_id=run_id,
        artifact_type="script_visual_strategy",
        schema_version=strategy.schema_version,
        payload_json=strat_payload,
        parent_artifact_roles_json={},
        validation_json=ValidationResult(status="valid"),
    )

    # 4. VoiceTrack
    voice_track = VoiceTrack(
        voice_id="Matthew",
        audio_file_name="narration.mp3",
        storage_key=f"projects/{project_id}/runs/{run_id}/narration.mp3",
        duration_seconds=5.0,
        full_script_text="A 50 lakh rupee home loan starts at 8.5 percent interest.",
        word_timestamps=[
            WordTimestamp(word="A", start_ms=0, end_ms=300),
            WordTimestamp(word="50", start_ms=300, end_ms=600),
            WordTimestamp(word="lakh", start_ms=600, end_ms=1000),
            WordTimestamp(word="rupee", start_ms=1000, end_ms=1400),
            WordTimestamp(word="home", start_ms=1400, end_ms=1800),
            WordTimestamp(word="loan", start_ms=1800, end_ms=2200),
            WordTimestamp(word="starts", start_ms=2200, end_ms=2600),
            WordTimestamp(word="at", start_ms=2600, end_ms=3000),
            WordTimestamp(word="8.5", start_ms=3000, end_ms=3500),
            WordTimestamp(word="percent", start_ms=3500, end_ms=4000),
            WordTimestamp(word="interest", start_ms=4000, end_ms=4500),
        ],
    )
    store.save_artifact(
        project_id=project_id,
        run_id=run_id,
        artifact_type="voice_track",
        schema_version=voice_track.schema_version,
        payload_json=voice_track.model_dump(),
        parent_artifact_roles_json={},
        validation_json=ValidationResult(status="valid"),
    )
    return project_id, run_id


def test_continuous_story_handler_direct_run(temp_store: ArtifactStore, sample_draft_dict: dict):
    project_id, run_id = seed_prerequisite_artifacts(temp_store)

    handler = ContinuousStoryHandler(store=temp_store)
    record = handler.run(project_id, run_id, mock_draft=sample_draft_dict)

    assert record.artifact_type == "continuous_story_plan"
    assert record.status == "valid"

    # Lineage verification
    parents = record.parent_artifact_roles_json
    assert "voice_track" in parents
    assert "script_visual_strategy" in parents
    assert "research_packet" in parents

    # Payload verification
    payload = record.payload_json
    assert "plan" in payload
    assert "draft" in payload
    assert "raw_gemini_draft" in payload
    assert payload["plan"]["durationInFrames"] >= 150
    assert payload["audio_storage_key"] == f"projects/{project_id}/runs/{run_id}/narration.mp3"


def test_pipeline_routing_mode_resolution(temp_store: ArtifactStore):
    project_id_cont, run_id_cont = seed_prerequisite_artifacts(temp_store, visual_mode=VisualMode.CONTINUOUS_STORY)

    service = build_pipeline_service(temp_store)

    # In continuous mode: voice_track advances to continuous_story
    next_stage_cont = service._resolve_next_stage(project_id_cont, run_id_cont, "voice_track")
    assert next_stage_cont == "continuous_story"

    # continuous_story_plan advances to render
    next_stage_after_plan = service._resolve_next_stage(project_id_cont, run_id_cont, "continuous_story_plan")
    assert next_stage_after_plan == "render"

    # In standard/composition mode: voice_track advances to video_assembly
    project_id_std, run_id_std = seed_prerequisite_artifacts(temp_store, visual_mode=VisualMode.COMPOSITION)
    next_stage_std = service._resolve_next_stage(project_id_std, run_id_std, "voice_track")
    assert next_stage_std == "video_assembly"


def test_pipeline_service_executes_continuous_story_stage(temp_store: ArtifactStore, sample_draft_dict: dict):
    project_id, run_id = seed_prerequisite_artifacts(temp_store, visual_mode=VisualMode.CONTINUOUS_STORY)

    service = build_pipeline_service(temp_store)

    # Execute continuous_story stage via pipeline_service router
    record = service.run_stage("continuous_story", project_id, run_id, mock_draft=sample_draft_dict)

    assert record.artifact_type == "continuous_story_plan"
    assert record.status == "valid"

    # Verify run state updated cleanly
    run_record = temp_store.get_run(project_id, run_id)
    assert run_record.current_stage == "continuous_story"
    assert run_record.state == "running"
