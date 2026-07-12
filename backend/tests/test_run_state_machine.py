from app.dependencies import get_artifact_store, get_media_storage, get_pipeline_service
from app.main import create_app
from artifact_store.sqlite_store import ArtifactStore
from engines.render_engine import RenderEngine
from fastapi.testclient import TestClient
from pathlib import Path
from providers.media_storage import LocalMediaStorage
from providers.remotion_provider import RemotionRenderOutput


class SuccessfulProvider:
    def render(self, *, render_spec, output_path: Path) -> RemotionRenderOutput:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(b"fake mp4")
        return RemotionRenderOutput(output_path=output_path, size_bytes=8)


def make_client(tmp_path) -> tuple[TestClient, ArtifactStore]:
    store = ArtifactStore(tmp_path / "run_state.db")
    store.initialize()
    media_storage = LocalMediaStorage(tmp_path / "media")
    render_engine = RenderEngine(
        media_storage=media_storage,
        remotion_provider=SuccessfulProvider(),
    )
    app = create_app()
    app.dependency_overrides[get_artifact_store] = lambda: store
    app.dependency_overrides[get_media_storage] = lambda: media_storage
    app.dependency_overrides[get_pipeline_service] = lambda: get_pipeline_service()
    # Wait, we want to construct a clean pipeline service for testing
    from app.pipeline_service import build_pipeline_service
    app.dependency_overrides[get_pipeline_service] = lambda: build_pipeline_service(
        store,
        render_engine=render_engine,
    )
    return TestClient(app), store


def test_run_state_transitions(tmp_path) -> None:
    client, store = make_client(tmp_path)
    
    # 1. Start a project. Run should be 'pending'
    proj_resp = client.post(
        "/projects",
        json={
            "topic": "Why Monthly Payments Feel Cheap",
            "angle": "How EMIs hide total cost",
        },
    ).json()
    
    project_id = proj_resp["project"]["id"]
    run_id = proj_resp["run"]["id"]
    
    run = store.get_run(project_id, run_id)
    assert run.state == "pending"
    assert run.current_stage is None
    assert run.started_at is None
    assert run.completed_at is None
    
    # 2. Run first stage. State should become 'running'
    client.post(f"/projects/{project_id}/runs/{run_id}/run/script_brief")
    run = store.get_run(project_id, run_id)
    assert run.state == "running"
    assert run.current_stage == "script_brief"
    assert run.started_at is not None
    assert run.completed_at is None

    # 3. Run rest of deterministic pipeline
    for stage in [
        "narrative_arc",
        "script_draft",
        "scene_script",
        "semantic_scene",
        "visual_event_sequence",
        "visual_plan",
        "timing",
        "render_spec",
    ]:
        client.post(f"/projects/{project_id}/runs/{run_id}/run/{stage}")
        
    run = store.get_run(project_id, run_id)
    assert run.state == "running"
    
    # 4. Render final stage. State should transition to 'completed'
    client.post(f"/projects/{project_id}/runs/{run_id}/run/render")
    run = store.get_run(project_id, run_id)
    assert run.state == "completed"
    assert run.current_stage == "render"
    assert run.completed_at is not None


def test_run_state_transitions_to_failed_on_exception(tmp_path) -> None:
    client, store = make_client(tmp_path)
    
    proj_resp = client.post(
        "/projects",
        json={
            "topic": "Why Monthly Payments Feel Cheap",
            "angle": "How EMIs hide total cost",
        },
    ).json()
    
    project_id = proj_resp["project"]["id"]
    run_id = proj_resp["run"]["id"]
    
    # Run a stage out of order (narrative_arc is missing script_brief), which raises exception
    response = client.post(f"/projects/{project_id}/runs/{run_id}/run/narrative_arc")
    assert response.status_code == 409
    
    run = store.get_run(project_id, run_id)
    assert run.state == "failed"
    assert run.current_stage == "narrative_arc"
    assert "required 'script_brief' artifact is missing" in run.error_message
