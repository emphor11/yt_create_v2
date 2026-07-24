from pathlib import Path

from fastapi.testclient import TestClient

from app.dependencies import get_artifact_store, get_media_storage, get_pipeline_service
from app.main import create_app
from app.pipeline_service import build_pipeline_service
from artifact_store.sqlite_store import ArtifactStore
from engines.render_engine import RenderEngine
from providers.media_storage import LocalMediaStorage
from providers.remotion_provider import RemotionProviderError, RemotionRenderOutput
from domain.render_spec import RenderSpec, RenderFrameSpan
from domain.video_assembly_props import VideoAssemblyProps, SceneSpec, ComponentSpec, AudioSpec
from domain.validation import ValidationResult


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
        },
    )
    assert response.status_code == 200
    return response.json()


def save_mock_render_spec(store: ArtifactStore, project_id: str, run_id: str):
    spec = RenderSpec(
        scene_id="scene_01",
        composition="VideoAssembly",
        fps=30,
        duration_frames=240,
        props=VideoAssemblyProps(
            scenes=[
                SceneSpec(
                    scene_id="scene_001",
                    start_frame=0,
                    end_frame=240,
                    duration_frames=240,
                    component=ComponentSpec(
                        component_id="Typography",
                        props={"text": "Hello"}
                    ),
                    asset=None,
                    narration_text="Hello"
                )
            ],
            audio=AudioSpec(
                audio_file_name="narration.mp3",
                local_path="narration.mp3",
                duration_seconds=8.0
            )
        ),
        frame_spans=[
            RenderFrameSpan(
                event_id="scene_001",
                start_frame=0,
                end_frame=240,
                duration_frames=240,
            )
        ]
    )
    return store.save_artifact(
        project_id=project_id,
        run_id=run_id,
        artifact_type="render_spec",
        schema_version="1",
        payload_json=spec.model_dump(),
        parent_artifact_roles_json={},
        validation_json=ValidationResult(status="valid"),
    )


def test_run_render_creates_video_artifact_and_media_file(tmp_path) -> None:
    client, store, media_storage = make_client(tmp_path)
    created = create_valid_project(client)
    project_id = created["project"]["id"]
    run_id = created["run"]["id"]
    render_spec_art = save_mock_render_spec(store, project_id, run_id)

    response = client.post(
        f"/projects/{project_id}/runs/{run_id}/run/render"
    )

    assert response.status_code == 200
    body = response.json()
    artifact = body["artifact"]
    payload = artifact["payload_json"]
    assert body["validation"]["status"] == "valid"
    assert artifact["artifact_type"] == "video"
    assert artifact["parent_artifact_roles_json"] == {
        "render_spec": render_spec_art.id
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
    client, store, _media_storage = make_client(tmp_path)
    created = create_valid_project(client)
    project_id = created["project"]["id"]
    run_id = created["run"]["id"]
    save_mock_render_spec(store, project_id, run_id)
    path = f"/projects/{project_id}/runs/{run_id}/run/render"

    first = client.post(path)
    second = client.post(path)
    artifacts = client.get(
        f"/projects/{project_id}/runs/{run_id}/artifacts"
    )

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["artifact_id"] == second.json()["artifact_id"]
    assert [artifact["artifact_type"] for artifact in artifacts.json()].count("video") == 1


def test_render_requires_render_spec(tmp_path) -> None:
    client, _store, _media_storage = make_client(tmp_path)
    created = create_valid_project(client)
    project_id = created["project"]["id"]
    run_id = created["run"]["id"]

    response = client.post(
        f"/projects/{project_id}/runs/{run_id}/run/render"
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Cannot run 'render': required 'render_spec' artifact is missing."


def test_render_failure_is_stored_as_failed_video_artifact(tmp_path) -> None:
    client, store, _media_storage = make_client(tmp_path, provider=FailingProvider())
    created = create_valid_project(client)
    project_id = created["project"]["id"]
    run_id = created["run"]["id"]
    save_mock_render_spec(store, project_id, run_id)

    response = client.post(
        f"/projects/{project_id}/runs/{run_id}/run/render"
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
