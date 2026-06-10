from pathlib import Path

from fastapi.testclient import TestClient

from app.dependencies import get_artifact_store, get_media_storage, get_pipeline_service
from app.main import create_app
from app.pipeline_service import build_pipeline_service
from artifact_store.sqlite_store import ArtifactStore
from engines.render_engine import RenderEngine
from providers.media_storage import LocalMediaStorage
from providers.remotion_provider import RemotionProviderError, RemotionRenderOutput


class SuccessfulProvider:
    def render(self, *, render_spec, output_path: Path) -> RemotionRenderOutput:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(b"fake mp4")
        return RemotionRenderOutput(output_path=output_path, size_bytes=8)


class FailingProvider:
    def render(self, *, render_spec, output_path: Path) -> RemotionRenderOutput:
        raise RemotionProviderError("render failed")


def make_client(tmp_path, provider=None) -> tuple[TestClient, ArtifactStore, LocalMediaStorage]:
    store = ArtifactStore(tmp_path / "render.db")
    store.initialize()
    media_storage = LocalMediaStorage(tmp_path / "media")
    render_engine = RenderEngine(
        media_storage=media_storage,
        remotion_provider=provider or SuccessfulProvider(),
    )
    app = create_app()
    app.dependency_overrides[get_artifact_store] = lambda: store
    app.dependency_overrides[get_media_storage] = lambda: media_storage
    app.dependency_overrides[get_pipeline_service] = lambda: build_pipeline_service(
        store,
        render_engine=render_engine,
    )
    return TestClient(app), store, media_storage


def create_valid_project(client: TestClient) -> dict:
    response = client.post(
        "/projects",
        json={
            "topic": "Why Monthly Payments Feel Cheap",
            "angle": "How EMIs hide total cost",
        },
    )
    assert response.status_code == 200
    return response.json()


def run_stage(client: TestClient, created: dict, stage: str) -> dict:
    response = client.post(
        f"/projects/{created['project']['id']}/runs/{created['run']['id']}/run/{stage}"
    )
    assert response.status_code == 200
    return response.json()


def run_to_render_spec(client: TestClient, created: dict) -> dict:
    run_stage(client, created, "script_brief")
    run_stage(client, created, "narrative_arc")
    run_stage(client, created, "script_draft")
    run_stage(client, created, "scene_script")
    run_stage(client, created, "semantic_scene")
    run_stage(client, created, "visual_event_sequence")
    run_stage(client, created, "visual_plan")
    run_stage(client, created, "timing")
    return run_stage(client, created, "render_spec")


def test_run_render_creates_video_artifact_and_media_file(tmp_path) -> None:
    client, _store, media_storage = make_client(tmp_path)
    created = create_valid_project(client)
    render_spec_response = run_to_render_spec(client, created)

    response = client.post(
        f"/projects/{created['project']['id']}/runs/{created['run']['id']}/run/render"
    )

    assert response.status_code == 200
    body = response.json()
    artifact = body["artifact"]
    payload = artifact["payload_json"]
    assert body["validation"]["status"] == "valid"
    assert artifact["artifact_type"] == "video"
    assert artifact["parent_artifact_roles_json"] == {
        "render_spec": render_spec_response["artifact_id"]
    }
    assert payload["render_status"] == "succeeded"
    assert payload["storage_key"].endswith("/scene_01.mp4")
    assert not payload["storage_key"].startswith("/")
    assert payload["size_bytes"] == 8
    assert media_storage.path_for_key(payload["storage_key"]).exists()

    media_response = client.get(f"/media/{payload['storage_key']}")

    assert media_response.status_code == 200
    assert media_response.content == b"fake mp4"
    assert media_response.headers["content-type"].startswith("video/mp4")


def test_run_render_twice_returns_existing_artifact(tmp_path) -> None:
    client, _store, _media_storage = make_client(tmp_path)
    created = create_valid_project(client)
    run_to_render_spec(client, created)
    path = f"/projects/{created['project']['id']}/runs/{created['run']['id']}/run/render"

    first = client.post(path)
    second = client.post(path)
    artifacts = client.get(
        f"/projects/{created['project']['id']}/runs/{created['run']['id']}/artifacts"
    )

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["artifact_id"] == second.json()["artifact_id"]
    assert [artifact["artifact_type"] for artifact in artifacts.json()].count("video") == 1


def test_render_requires_render_spec(tmp_path) -> None:
    client, _store, _media_storage = make_client(tmp_path)
    created = create_valid_project(client)

    response = client.post(
        f"/projects/{created['project']['id']}/runs/{created['run']['id']}/run/render"
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Cannot run render without a render_spec artifact."


def test_render_failure_is_stored_as_failed_video_artifact(tmp_path) -> None:
    client, _store, _media_storage = make_client(tmp_path, provider=FailingProvider())
    created = create_valid_project(client)
    run_to_render_spec(client, created)

    response = client.post(
        f"/projects/{created['project']['id']}/runs/{created['run']['id']}/run/render"
    )

    assert response.status_code == 200
    body = response.json()
    artifact = body["artifact"]
    payload = artifact["payload_json"]
    assert body["validation"]["status"] == "failed"
    assert artifact["status"] == "failed"
    assert payload["render_status"] == "failed"
    assert payload["storage_key"] is None
    assert "render failed" in payload["error_message"]
