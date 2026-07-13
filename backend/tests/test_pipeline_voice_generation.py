from pathlib import Path
from fastapi.testclient import TestClient

from app.dependencies import get_artifact_store, get_pipeline_service
from app.main import create_app
from app.pipeline_service import build_pipeline_service
from artifact_store.sqlite_store import ArtifactStore
from domain.validation import ValidationResult
from providers.media_storage import LocalMediaStorage


def make_client(tmp_path) -> tuple[TestClient, ArtifactStore, LocalMediaStorage]:
    store = ArtifactStore(tmp_path / "voice_api.db")
    store.initialize()
    
    media_path = tmp_path / "media"
    media_storage = LocalMediaStorage(media_path)
    
    app = create_app()
    app.dependency_overrides[get_artifact_store] = lambda: store
    app.dependency_overrides[get_pipeline_service] = lambda: build_pipeline_service(
        store,
        llm_provider=None,
    )
    return TestClient(app), store, media_storage


def setup_project_ready_for_voice(store: ArtifactStore) -> tuple[str, str]:
    project = store.create_project("Voice Integration Project")
    run = store.create_run(project.id, mode="ai")

    # 1. Save ResearchPacket
    res_art = store.save_artifact(
        project_id=project.id,
        run_id=run.id,
        artifact_type="research_packet",
        schema_version="1",
        payload_json={
            "topic": "Voice Test Topic",
            "audience": "employees",
            "channel": "Mindshift",
            "verified_facts": ["Fact standard description showing 80000 phone price."],
            "statistics": [],
            "concepts": ["Opportunity Cost"],
            "trusted_sources": ["Source"],
        },
        parent_artifact_roles_json={},
        validation_json=ValidationResult(status="valid"),
    )

    # 2. Save NarrativePlan
    plan_art = store.save_artifact(
        project_id=project.id,
        run_id=run.id,
        artifact_type="narrative_plan",
        schema_version="1",
        payload_json={
            "thesis": "Thesis description",
            "target_pain_point": "Complacency",
            "conceptual_hook": "Hook theme",
            "narrative_arc_type": "PAS",
            "scene_beats": [{"scene_id": "scene_01", "title": "Title", "focus_concept": "Opportunity Cost", "core_teaching_point": "Point"}],
        },
        parent_artifact_roles_json={"research_packet": res_art.id},
        validation_json=ValidationResult(status="valid"),
    )

    # 3. Save Hook
    hook_art = store.save_artifact(
        project_id=project.id,
        run_id=run.id,
        artifact_type="hook",
        schema_version="1",
        payload_json={
            "conceptual_hook": "Hook",
            "script_text": "Is salary a drug?",
            "visual_directives": [{"beat_id": "beat_01", "visual_instruction": "Instruction", "onscreen_text": "TEXT"}],
        },
        parent_artifact_roles_json={"research_packet": res_art.id, "narrative_plan": plan_art.id},
        validation_json=ValidationResult(status="valid"),
    )

    # 4. Save ScriptVisualStrategy
    strat_art = store.save_artifact(
        project_id=project.id,
        run_id=run.id,
        artifact_type="script_visual_strategy",
        schema_version="1",
        payload_json={
            "thesis": "Thesis body",
            "ideas": [
                {
                    "idea_id": "idea_01",
                    "title": "Title",
                    "focus_concept": "Opportunity Cost",
                    "core_teaching_point": "Point",
                    "narration": "Yes, it is a reward or a drug.",
                    "visual_sequence": [
                        {
                            "beat_id": "beat_01_01",
                            "preferred_component": "SplitComparison",
                            "visual_goal": "Goal",
                            "component_data": {
                                "left_role": "product_price",
                                "left_label": "Left label",
                                "left_value": 80000,
                                "left_unit": "INR",
                                "right_role": "monthly_payment",
                                "right_label": "Right label",
                                "right_value": 160000,
                                "right_unit": "INR",
                            },
                        }
                    ],
                }
            ],
        },
        parent_artifact_roles_json={
            "hook": hook_art.id,
            "narrative_plan": plan_art.id,
            "research_packet": res_art.id,
        },
        validation_json=ValidationResult(status="valid"),
    )

    # 5. Save ReviewResult (Stage 6)
    store.save_artifact(
        project_id=project.id,
        run_id=run.id,
        artifact_type="review_result",
        schema_version="1",
        payload_json={
            "approved": True,
            "checks": [{"name": "Concept Alignment", "status": "passed", "message": "Ok"}],
        },
        parent_artifact_roles_json={"script_visual_strategy": strat_art.id},
        validation_json=ValidationResult(status="valid"),
    )

    return project.id, run.id


def test_voice_generation_requires_parents(tmp_path) -> None:
    client, _store, _media = make_client(tmp_path)
    response = client.post(
        "/projects",
        json={
            "topic": "Home buying",
            "mode": "ai",
            "audience": "investors",
            "language": "English",
            "style": "educational",
            "channel": "Mindshift",
        },
    )
    created = response.json()
    project_id = created["project"]["id"]
    run_id = created["run"]["id"]

    response = client.post(f"/projects/{project_id}/runs/{run_id}/run/voice_generation")
    assert response.status_code == 409
    assert "required 'review_result' artifact is missing" in response.json()["detail"]


def test_voice_generation_synthesizes_and_saves(tmp_path) -> None:
    store = ArtifactStore(tmp_path / "voice_api.db")
    store.initialize()
    
    media_path = tmp_path / "media"
    media = LocalMediaStorage(media_path)
    
    app = create_app()
    app_service = build_pipeline_service(store, llm_provider=None)
    from domain.pipeline_stage import PipelineStage
    handler = app_service.router._handlers[PipelineStage.VOICE_GENERATION]
    handler.media_storage = media

    app.dependency_overrides[get_artifact_store] = lambda: store
    app.dependency_overrides[get_pipeline_service] = lambda: app_service

    client = TestClient(app)
    project_id, run_id = setup_project_ready_for_voice(store)

    response = client.post(f"/projects/{project_id}/runs/{run_id}/run/voice_generation")
    assert response.status_code == 200
    artifact = response.json()["artifact"]
    assert artifact["artifact_type"] == "voice_track"
    assert artifact["status"] == "valid"
    
    payload = artifact["payload_json"]
    assert payload["voice_id"] == "FallbackVoice"
    assert payload["audio_file_name"] == "narration.mp3"
    assert payload["duration_seconds"] > 0
    assert len(payload["word_timestamps"]) > 0

    # Assert local file exists in our media storage path!
    local_path = media.path_for_key(payload["storage_key"])
    assert local_path.exists()
    assert local_path.stat().st_size > 0

    # Verify run state transitioned correctly to timing stage
    run = store.get_run(project_id, run_id)
    assert run.state == "running"
    assert run.current_stage == "voice_generation"
