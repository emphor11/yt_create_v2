from pathlib import Path
from unittest.mock import MagicMock

import pytest

from artifact_store.sqlite_store import ArtifactStore
from domain.generate_video_request import GenerateVideoRequest
from domain.hook import Hook
from domain.render_spec import RenderFrameSpan, RenderSpec
from domain.thumbnail import Thumbnail
from domain.validators.thumbnail_validator import ThumbnailValidator
from domain.validators.youtube_metadata_validator import YoutubeMetadataValidator
from domain.validators.youtube_upload_validator import YoutubeUploadValidator
from domain.video import Video
from domain.youtube_metadata import YoutubeMetadata
from domain.youtube_upload import YoutubeUpload
from engines.thumbnail_engine import ThumbnailEngine
from engines.youtube_metadata_engine import YoutubeMetadataEngine, YoutubeMetadataResult
from engines.youtube_upload_engine import YoutubeUploadEngine
from providers.llm_provider import LLMJsonResponse, LLMProviderMetadata
from providers.media_storage import LocalMediaStorage
from providers.remotion_provider import RemotionRenderOutput


def test_youtube_metadata_validator_valid():
    validator = YoutubeMetadataValidator()
    metadata = YoutubeMetadata(
        title="Why the Rule of 72 Changes Everything",
        description="Learn how compound interest works.\n\n00:00 Intro\n01:00 Math Behind It\n02:00 Summary\n\n#Finance #Investing",
        tags=["finance", "investing", "rule of 72"],
        category_id="27",
        thumbnail_concept="THE $100T REVOLUTION",
    )
    res = validator.validate(metadata)
    assert res.status == "valid"
    assert not res.errors


def test_youtube_metadata_validator_invalid_title_length():
    validator = YoutubeMetadataValidator()
    metadata = YoutubeMetadata(
        title="A" * 105,
        description="00:00 Intro\n01:00 End",
        tags=["tag1", "tag2", "tag3"],
        category_id="27",
        thumbnail_concept="BIG CONCEPT",
    )
    res = validator.validate(metadata)
    assert res.status == "blocked"
    assert any("cannot exceed 100 characters" in e for e in res.errors)


def test_youtube_metadata_validator_missing_chapters():
    validator = YoutubeMetadataValidator()
    metadata = YoutubeMetadata(
        title="Valid Title",
        description="Description without any timestamp markers whatsoever",
        tags=["tag1", "tag2", "tag3"],
        category_id="27",
        thumbnail_concept="BIG CONCEPT",
    )
    res = validator.validate(metadata)
    assert res.status == "blocked"
    assert any("timestamps starting at 00:00" in e for e in res.errors)



def test_thumbnail_validator_valid():
    validator = ThumbnailValidator()
    thumb = Thumbnail(
        storage_key="projects/p1/runs/r1/thumbnail.png",
        width=1280,
        height=720,
        size_bytes=45000,
    )
    res = validator.validate(thumb)
    assert res.status == "valid"
    assert not res.errors


def test_thumbnail_validator_invalid_dimensions():
    validator = ThumbnailValidator()
    thumb = Thumbnail(
        storage_key="projects/p1/runs/r1/thumbnail.png",
        width=1920,
        height=1080,
        size_bytes=45000,
    )
    res = validator.validate(thumb)
    assert res.status == "blocked"
    assert any("must be 1280x720" in e for e in res.errors)


def test_youtube_upload_validator_valid():
    validator = YoutubeUploadValidator()
    upload = YoutubeUpload(
        youtube_video_id="abc123xyz",
        youtube_url="https://youtu.be/abc123xyz",
        title="Test Title",
    )
    res = validator.validate(upload)
    assert res.status == "valid"
    assert not res.errors


def test_youtube_upload_validator_invalid_url():
    validator = YoutubeUploadValidator()
    upload = YoutubeUpload(
        youtube_video_id="abc123xyz",
        youtube_url="https://vimeo.com/abc123xyz",
        title="Test Title",
    )
    res = validator.validate(upload)
    assert res.status == "blocked"
    assert any("youtube_url must start with" in e for e in res.errors)


def test_youtube_metadata_engine_generates_metadata():
    mock_llm = MagicMock()
    mock_llm.generate_json.return_value = LLMJsonResponse(
        payload={
            "title": "Unlocking Exponential Wealth: The Rule of 72",
            "description": "Here is how money doubles.\n\n00:00 Intro\n00:08 The Formula\n00:20 Conclusion\n\n#Money #Finance",
            "tags": ["wealth", "investing", "rule of 72", "money"],
            "category_id": "27",
            "thumbnail_concept": "DOUBLE YOUR MONEY",
        },
        metadata=LLMProviderMetadata(provider="gemini", model="mock-gemini"),
    )

    from domain.video_assembly_props import AudioSpec, ComponentSpec, SceneSpec, VideoAssemblyProps

    engine = YoutubeMetadataEngine(llm_provider=mock_llm)
    spec = RenderSpec(
        scene_id="scene_test",
        composition="VideoAssembly",
        fps=30,
        duration_frames=600,
        props=VideoAssemblyProps(
            scenes=[
                SceneSpec(
                    scene_id="scene_01",
                    start_frame=0,
                    end_frame=240,
                    duration_frames=240,
                    component=ComponentSpec(component_id="Typography", props={}),
                    narration_text="Intro",
                ),
                SceneSpec(
                    scene_id="scene_02",
                    start_frame=240,
                    end_frame=600,
                    duration_frames=360,
                    component=ComponentSpec(component_id="Typography", props={}),
                    narration_text="Formula",
                ),
            ],
            audio=AudioSpec(
                audio_file_name="audio.mp3",
                local_path="/tmp/audio.mp3",
                duration_seconds=20.0,
            ),
        ),
        frame_spans=[
            RenderFrameSpan(event_id="e1", start_frame=0, end_frame=240, duration_frames=240)
        ],
    )
    res = engine.run(render_spec=spec, topic="Investing")
    assert res.metadata.title == "Unlocking Exponential Wealth: The Rule of 72"
    assert "00:00 Intro" in res.metadata.description
    assert res.metadata.thumbnail_concept == "DOUBLE YOUR MONEY"



def test_thumbnail_engine_renders_thumbnail(tmp_path: Path):
    from io import BytesIO
    from PIL import Image
    from engines.thumbnail_prompt_engine import ThumbnailPromptConcept

    mock_storage = LocalMediaStorage(tmp_path)

    buf = BytesIO()
    Image.new("RGB", (800, 600), color="blue").save(buf, format="PNG")
    fake_png_bytes = buf.getvalue()

    mock_image_provider = MagicMock()
    mock_image_provider.generate_image.return_value = fake_png_bytes
    mock_image_provider.last_provider_used = "huggingface_flux"

    mock_prompt_engine = MagicMock()
    mock_prompt_engine.run.return_value = ThumbnailPromptConcept(
        headline="DOUBLE WEALTH",
        visual_concept="A dramatic visual concept",
        image_prompt="Cinematic 16:9 shot of gold bars",
        negative_prompt="blurry",
    )

    engine = ThumbnailEngine(
        media_storage=mock_storage,
        image_provider=mock_image_provider,
        prompt_engine=mock_prompt_engine,
    )
    metadata = YoutubeMetadata(
        title="Test Title",
        description="00:00 Intro",
        tags=["a", "b", "c"],
        category_id="27",
        thumbnail_concept="TEST CONCEPT",
    )

    thumb = engine.run(
        metadata=metadata,
        hook_line="Catchy hook line",
        topic="Finance",
        thesis="Wealth over spending",
        project_id="p1",
        run_id="r1",
    )

    assert thumb.storage_key == "projects/p1/runs/r1/thumbnail.png"
    assert thumb.size_bytes > 0
    assert thumb.width == 1280
    assert thumb.height == 720
    assert thumb.headline == "DOUBLE WEALTH"
    assert thumb.provider_used == "huggingface_flux"
    mock_image_provider.generate_image.assert_called_once()
    mock_prompt_engine.run.assert_called_once()


def test_youtube_upload_engine(tmp_path: Path):
    mock_storage = LocalMediaStorage(tmp_path)
    video_path = tmp_path / "projects/p1/runs/r1/scene.mp4"
    video_path.parent.mkdir(parents=True, exist_ok=True)
    video_path.write_bytes(b"fake video data")

    thumb_path = tmp_path / "projects/p1/runs/r1/thumbnail.png"
    thumb_path.write_bytes(b"fake thumb data")

    mock_yt_provider = MagicMock()
    mock_yt_provider.upload_video.return_value = {
        "video_id": "test_id_123",
        "video_url": "https://youtu.be/test_id_123",
    }
    mock_yt_provider.set_thumbnail.return_value = True

    engine = YoutubeUploadEngine(youtube_provider=mock_yt_provider, media_storage=mock_storage)
    metadata = YoutubeMetadata(
        title="Test Video",
        description="00:00 Intro",
        tags=["test", "video", "yt"],
        category_id="27",
        thumbnail_concept="THUMB",
    )

    upload = engine.run(
        video_storage_key="projects/p1/runs/r1/scene.mp4",
        metadata=metadata,
        thumbnail_storage_key="projects/p1/runs/r1/thumbnail.png",
    )

    assert upload.youtube_video_id == "test_id_123"
    assert upload.youtube_url == "https://youtu.be/test_id_123"
    assert upload.thumbnail_attached is True
    mock_yt_provider.upload_video.assert_called_once()
    mock_yt_provider.set_thumbnail.assert_called_once_with(
        video_id="test_id_123", thumbnail_path=thumb_path
    )


def test_pipeline_youtube_publishing_flow(tmp_path: Path):
    from fastapi.testclient import TestClient
    from app.dependencies import get_artifact_store, get_media_storage, get_pipeline_service
    from app.main import create_app
    from app.pipeline_service import build_pipeline_service
    from domain.validation import ValidationResult

    store = ArtifactStore(tmp_path / "yt_test.db")
    store.initialize()
    media_storage = LocalMediaStorage(tmp_path / "media")

    mock_llm = MagicMock()
    mock_llm.generate_json.return_value = LLMJsonResponse(
        payload={
            "title": "Unlocking Exponential Wealth: The Rule of 72",
            "description": "Here is how money doubles.\n\n00:00 Intro\n00:08 The Formula\n00:20 Conclusion\n\n#Money #Finance",
            "tags": ["wealth", "investing", "rule of 72", "money"],
            "category_id": "27",
            "thumbnail_concept": "DOUBLE YOUR MONEY",
        },
        metadata=LLMProviderMetadata(provider="gemini", model="mock-gemini"),
    )

    app = create_app()
    app.dependency_overrides[get_artifact_store] = lambda: store
    app.dependency_overrides[get_media_storage] = lambda: media_storage
    app.dependency_overrides[get_pipeline_service] = lambda: build_pipeline_service(
        store,
        llm_provider=mock_llm,
    )
    client = TestClient(app)

    # 1. Create project
    res = client.post("/projects", json={"topic": "Compound Interest"})
    assert res.status_code == 200
    p_data = res.json()
    project_id = p_data["project"]["id"]
    run_id = p_data["run"]["id"]

    # 2. Add prerequisite render_spec and video artifacts
    from domain.video_assembly_props import AudioSpec, ComponentSpec, SceneSpec, VideoAssemblyProps
    render_spec = RenderSpec(
        scene_id="scene_01",
        composition="VideoAssembly",
        fps=30,
        duration_frames=240,
        props=VideoAssemblyProps(
            scenes=[
                SceneSpec(
                    scene_id="s1",
                    start_frame=0,
                    end_frame=240,
                    duration_frames=240,
                    component=ComponentSpec(component_id="Typography", props={}),
                    narration_text="Intro",
                )
            ],
            audio=AudioSpec(audio_file_name="a.mp3", local_path="/tmp/a.mp3", duration_seconds=8.0),
        ),
        frame_spans=[RenderFrameSpan(event_id="s1", start_frame=0, end_frame=240, duration_frames=240)],
    )
    spec_art = store.save_artifact(
        project_id=project_id,
        run_id=run_id,
        artifact_type="render_spec",
        schema_version="1",
        payload_json=render_spec.model_dump(),
        parent_artifact_roles_json={},
        validation_json=ValidationResult(status="valid"),
    )

    video = Video(
        scene_id="scene_01",
        render_status="succeeded",
        file_name="scene_01.mp4",
        content_type="video/mp4",
        fps=30,
        duration_frames=240,
        storage_key=f"projects/{project_id}/runs/{run_id}/scene_01.mp4",
        size_bytes=1024,
    )
    # Create fake video file on disk
    video_path = media_storage.ensure_parent(video.storage_key)
    video_path.write_bytes(b"fake video data")

    video_art = store.save_artifact(
        project_id=project_id,
        run_id=run_id,
        artifact_type="video",
        schema_version="1",
        payload_json=video.model_dump(),
        parent_artifact_roles_json={"render_spec": spec_art.id},
        validation_json=ValidationResult(status="valid"),
    )

    # 3. Test running youtube_metadata stage
    meta_res = client.post(f"/projects/{project_id}/runs/{run_id}/run/youtube_metadata")
    assert meta_res.status_code == 200
    meta_body = meta_res.json()
    assert meta_body["validation"]["status"] == "valid"
    assert meta_body["artifact"]["artifact_type"] == "youtube_metadata"
    assert meta_body["artifact"]["payload_json"]["title"] == "Unlocking Exponential Wealth: The Rule of 72"

    # 4. Test run status includes new stages
    status_res = client.get(f"/projects/{project_id}/runs/{run_id}/status")
    assert status_res.status_code == 200
    stages = {s["stage"]: s["status"] for s in status_res.json()["stages"]}
    assert stages["youtube_metadata"] == "valid"
    assert stages["thumbnail"] == "missing"
    assert stages["youtube_upload"] == "missing"

