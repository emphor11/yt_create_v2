from pathlib import Path
from unittest.mock import MagicMock
import pytest
from fastapi.testclient import TestClient

from app.dependencies import get_artifact_store, get_media_storage, get_pipeline_service
from app.main import create_app
from app.pipeline_service import (
    NEXT_STAGE_BY_ARTIFACT_TYPE,
    OPTIONAL_STAGES,
    build_pipeline_service,
)
from artifact_store.models import is_advanceable_status
from artifact_store.sqlite_store import ArtifactStore
from domain.render_spec import RenderFrameSpan, RenderSpec
from domain.validation import ValidationResult
from domain.video import Video
from domain.video_assembly_props import AudioSpec, ComponentSpec, SceneSpec, VideoAssemblyProps
from domain.youtube_metadata import YoutubeMetadata
from providers.llm_provider import LLMJsonResponse, LLMProviderMetadata
from providers.media_storage import LocalMediaStorage


def test_next_stage_routes_youtube_metadata_directly_to_youtube_upload():
    """Verify that automated pipeline progression routes youtube_metadata directly to youtube_upload, bypassing thumbnail."""
    assert NEXT_STAGE_BY_ARTIFACT_TYPE["video"] == "youtube_metadata"
    assert NEXT_STAGE_BY_ARTIFACT_TYPE["youtube_metadata"] == "youtube_upload"
    assert NEXT_STAGE_BY_ARTIFACT_TYPE["thumbnail"] == "youtube_upload"
    assert "thumbnail" in OPTIONAL_STAGES


def test_skipped_status_is_advanceable():
    """Verify that skipped status does not block pipeline runs."""
    assert is_advanceable_status("valid")
    assert is_advanceable_status("warning")
    assert is_advanceable_status("skipped")
    assert not is_advanceable_status("blocked")
    assert not is_advanceable_status("failed")


def test_thumbnail_handler_disabled_by_default_creates_skipped_artifact(tmp_path: Path):
    """When thumbnail generation is disabled (default), running thumbnail stage creates a skipped artifact without calling image providers."""
    store = ArtifactStore(tmp_path / "test_store.db")
    store.initialize()

    # Create project and metadata prerequisite
    project = store.create_project("Test Topic")
    run = store.create_run(project.id, mode="ai")

    metadata = YoutubeMetadata(
        title="Test Title",
        description="Test Desc",
        tags=["test"],
        category_id="27",
        thumbnail_concept="TEST THUMB",
    )
    store.save_artifact(
        project_id=project.id,
        run_id=run.id,
        artifact_type="youtube_metadata",
        schema_version="1",
        payload_json=metadata.model_dump(),
        parent_artifact_roles_json={},
        validation_json=ValidationResult(status="valid"),
    )

    mock_image_provider = MagicMock()
    mock_thumbnail_engine = MagicMock()

    from app.stage_handlers.thumbnail_handler import ThumbnailHandler
    from app.stage_logger import StageLogger
    from domain.validators.thumbnail_validator import ThumbnailValidator

    handler = ThumbnailHandler(
        store=store,
        thumbnail_engine=mock_thumbnail_engine,
        thumbnail_validator=ThumbnailValidator(),
        stage_logger=StageLogger(),
        enabled=False,
    )

    artifact = handler.run(project.id, run.id)

    assert artifact.artifact_type == "thumbnail"
    assert artifact.status == "skipped"
    assert artifact.payload_json.get("status") == "skipped"
    assert "disabled" in artifact.payload_json.get("reason", "").lower()
    mock_thumbnail_engine.run.assert_not_called()
    mock_image_provider.generate_image.assert_not_called()


def test_pipeline_end_to_end_without_thumbnail(tmp_path: Path):
    """Test full flow: render -> youtube_metadata -> youtube_upload without thumbnail.
    Verifies that:
    1. Video is automatically uploaded by the system.
    2. Upload succeeds with thumbnail_attached=False.
    3. Pipeline status reports thumbnail as skipped.
    4. No thumbnail API is called.
    """
    store = ArtifactStore(tmp_path / "flow_store.db")
    store.initialize()
    media_storage = LocalMediaStorage(tmp_path / "media")

    mock_llm = MagicMock()
    mock_llm.generate_json.return_value = LLMJsonResponse(
        payload={
            "title": "Why Buying a Home Too Early Destroys Wealth",
            "description": "Full breakdown of real estate hidden costs.\n\n00:00 Intro\n00:05 The Hidden Costs\n\n#Finance",
            "tags": ["real estate", "finance", "money"],
            "category_id": "27",
            "thumbnail_concept": "THE HOME TRAP",
        },
        metadata=LLMProviderMetadata(provider="gemini", model="mock-gemini"),
    )

    mock_yt_provider = MagicMock()
    mock_yt_provider.upload_video.return_value = {
        "video_id": "yt_video_999",
        "video_url": "https://youtu.be/yt_video_999",
    }

    mock_image_provider = MagicMock()

    app = create_app()
    app.dependency_overrides[get_artifact_store] = lambda: store
    app.dependency_overrides[get_media_storage] = lambda: media_storage

    # Build pipeline service with mock LLM and mock YouTube provider, thumbnail disabled
    service = build_pipeline_service(
        store,
        llm_provider=mock_llm,
        image_generation_provider=mock_image_provider,
        media_storage=media_storage,
    )
    # Inject mock YouTube provider into upload handler
    from domain.pipeline_stage import PipelineStage
    service.router._handlers[PipelineStage.YOUTUBE_UPLOAD].upload_engine.youtube_provider = mock_yt_provider

    app.dependency_overrides[get_pipeline_service] = lambda: service
    client = TestClient(app)

    # 1. Create project
    res = client.post("/projects", json={"topic": "First Home Trap"})
    assert res.status_code == 200
    p_data = res.json()
    project_id = p_data["project"]["id"]
    run_id = p_data["run"]["id"]

    # 2. Add render_spec & video artifacts (simulating finished render)
    render_spec = RenderSpec(
        scene_id="scene_home",
        composition="VideoAssembly",
        fps=30,
        duration_frames=300,
        props=VideoAssemblyProps(
            scenes=[
                SceneSpec(
                    scene_id="s1",
                    start_frame=0,
                    end_frame=300,
                    duration_frames=300,
                    component=ComponentSpec(component_id="Typography", props={}),
                    narration_text="Intro text",
                )
            ],
            audio=AudioSpec(audio_file_name="a.mp3", local_path="/tmp/a.mp3", duration_seconds=10.0),
        ),
        frame_spans=[RenderFrameSpan(event_id="s1", start_frame=0, end_frame=300, duration_frames=300)],
    )
    store.save_artifact(
        project_id=project_id,
        run_id=run_id,
        artifact_type="render_spec",
        schema_version="1",
        payload_json=render_spec.model_dump(),
        parent_artifact_roles_json={},
        validation_json=ValidationResult(status="valid"),
    )

    video = Video(
        scene_id="scene_home",
        render_status="succeeded",
        file_name="scene_home.mp4",
        content_type="video/mp4",
        fps=30,
        duration_frames=300,
        storage_key=f"projects/{project_id}/runs/{run_id}/scene_home.mp4",
        size_bytes=2048,
    )
    # Create physical video file on disk
    video_path = media_storage.ensure_parent(video.storage_key)
    video_path.write_bytes(b"mock mp4 content")

    store.save_artifact(
        project_id=project_id,
        run_id=run_id,
        artifact_type="video",
        schema_version="1",
        payload_json=video.model_dump(),
        parent_artifact_roles_json={},
        validation_json=ValidationResult(status="valid"),
    )

    # 3. Run youtube_metadata stage
    meta_res = client.post(f"/projects/{project_id}/runs/{run_id}/run/youtube_metadata")
    assert meta_res.status_code == 200
    meta_json = meta_res.json()
    assert meta_json["validation"]["status"] == "valid"

    # Verify status reports thumbnail as "skipped" before upload
    status_res1 = client.get(f"/projects/{project_id}/runs/{run_id}/status")
    stages1 = {s["stage"]: s["status"] for s in status_res1.json()["stages"]}
    assert stages1["youtube_metadata"] == "valid"
    assert stages1["thumbnail"] == "skipped"
    assert stages1["youtube_upload"] == "missing"

    # 4. Run youtube_upload stage directly without running thumbnail
    upload_res = client.post(f"/projects/{project_id}/runs/{run_id}/run/youtube_upload")
    assert upload_res.status_code == 200
    upload_json = upload_res.json()
    assert upload_json["validation"]["status"] == "valid"
    assert upload_json["artifact"]["payload_json"]["upload_status"] == "succeeded"
    assert upload_json["artifact"]["payload_json"]["youtube_video_id"] == "yt_video_999"
    assert upload_json["artifact"]["payload_json"]["thumbnail_attached"] is False

    # Verify YouTubeProvider was called to upload the MP4 video
    mock_yt_provider.upload_video.assert_called_once()
    call_kwargs = mock_yt_provider.upload_video.call_args[1]
    assert call_kwargs["title"] == "Why Buying a Home Too Early Destroys Wealth"
    assert call_kwargs["video_path"] == video_path
    mock_yt_provider.set_thumbnail.assert_not_called()

    # Verify no image generation API was called
    mock_image_provider.generate_image.assert_not_called()

    # 5. Verify final status: video, metadata, upload valid; thumbnail skipped
    status_res2 = client.get(f"/projects/{project_id}/runs/{run_id}/status")
    stages2 = {s["stage"]: s["status"] for s in status_res2.json()["stages"]}
    assert stages2["render"] == "valid"
    assert stages2["youtube_metadata"] == "valid"
    assert stages2["thumbnail"] == "skipped"
    assert stages2["youtube_upload"] == "valid"


def test_re_enabling_thumbnail_generation_preserves_existing_behavior(tmp_path: Path):
    """When enabled=True, thumbnail generation runs normally using existing thumbnail code."""
    from app.stage_handlers.thumbnail_handler import ThumbnailHandler
    from app.stage_logger import StageLogger
    from domain.thumbnail import Thumbnail
    from domain.validators.thumbnail_validator import ThumbnailValidator

    store = ArtifactStore(tmp_path / "enable_store.db")
    store.initialize()

    project = store.create_project("Enabled Test")
    run = store.create_run(project.id, mode="ai")

    metadata = YoutubeMetadata(
        title="Enabled Title",
        description="Enabled Desc",
        tags=["test"],
        category_id="27",
        thumbnail_concept="ENABLED THUMB",
    )
    store.save_artifact(
        project_id=project.id,
        run_id=run.id,
        artifact_type="youtube_metadata",
        schema_version="1",
        payload_json=metadata.model_dump(),
        parent_artifact_roles_json={},
        validation_json=ValidationResult(status="valid"),
    )

    mock_thumb = Thumbnail(
        file_name="thumbnail.png",
        content_type="image/png",
        width=1280,
        height=720,
        storage_key=f"projects/{project.id}/runs/{run.id}/thumbnail.png",
        size_bytes=5000,
        headline="ENABLED THUMB",
    )
    mock_engine = MagicMock()
    mock_engine.run.return_value = mock_thumb

    handler = ThumbnailHandler(
        store=store,
        thumbnail_engine=mock_engine,
        thumbnail_validator=ThumbnailValidator(),
        stage_logger=StageLogger(),
        enabled=True,
    )

    artifact = handler.run(project.id, run.id)

    assert artifact.artifact_type == "thumbnail"
    assert artifact.status == "valid"
    assert artifact.payload_json["headline"] == "ENABLED THUMB"
    mock_engine.run.assert_called_once()
