from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import MagicMock
import pytest

from artifact_store.sqlite_store import ArtifactStore
from domain.generate_video_request import GenerateVideoRequest, VisualMode
from domain.continuous_story_plan import ContinuousStoryPlanArtifact
from domain.render_spec import RenderSpec
from domain.video_assembly_props import VideoAssemblyProps, AudioSpec
from domain.validation import ValidationResult
from domain.validators.video_validator import VideoValidator
from engines.render_engine import RenderEngine
from providers.media_storage import LocalMediaStorage
from providers.remotion_provider import RemotionProvider, RemotionRenderOutput
from app.pipeline_service import build_pipeline_service
from app.stage_handlers.render_handler import RenderHandler
from app.stage_logger import StageLogger


@pytest.fixture
def temp_env():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        db_path = tmp_path / "test.db"
        store = ArtifactStore(db_path)
        store.initialize()

        media_root = tmp_path / "media"
        media_storage = LocalMediaStorage(media_root)

        renderer_root = tmp_path / "renderer"
        remotion_provider = RemotionProvider(renderer_root)

        yield {
            "tmp_path": tmp_path,
            "store": store,
            "media_storage": media_storage,
            "remotion_provider": remotion_provider,
        }


def test_render_handler_continuous_mode(temp_env):
    store: ArtifactStore = temp_env["store"]
    media_storage: LocalMediaStorage = temp_env["media_storage"]
    remotion_provider: RemotionProvider = temp_env["remotion_provider"]

    project = store.create_project("Continuous Render Test")
    run = store.create_run(project.id)
    project_id, run_id = project.id, run.id

    # 1. Save GenerateVideoRequest with visual_mode=continuous_story
    gen_req = GenerateVideoRequest(
        topic="Home Loan Hike",
        visual_mode=VisualMode.CONTINUOUS_STORY,
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

    # 2. Create actual dummy audio file in media storage
    audio_storage_key = f"projects/{project_id}/runs/{run_id}/loan_narration.mp3"
    audio_path = media_storage.ensure_parent(audio_storage_key)
    audio_path.write_bytes(b"dummy audio content")

    # 3. Save ContinuousStoryPlanArtifact
    story_plan = {
        "id": "loan_story",
        "fps": 30,
        "durationInFrames": 505,
        "width": 1920,
        "height": 1080,
        "safeMargin": 80,
        "audioFileName": "loan_narration.mp3",
        "narration": {"text": "A 50 lakh loan...", "audioFile": "loan_narration.mp3", "wordTimestamps": []},
        "objects": [{"id": "loan_card", "type": "card", "layout": "center"}],
        "events": [{"action": "enter", "targetId": "loan_card", "startFrame": 10, "durationFrames": 25}],
    }
    csp = ContinuousStoryPlanArtifact.from_compiled_plan(
        plan=story_plan,
        audio_storage_key=audio_storage_key,
    )
    csp_artifact = store.save_artifact(
        project_id=project_id,
        run_id=run_id,
        artifact_type="continuous_story_plan",
        schema_version=csp.schema_version,
        payload_json=csp.model_dump(),
        parent_artifact_roles_json={},
        validation_json=ValidationResult(status="valid"),
    )

    # Mock RemotionProvider.render so it generates a dummy mp4
    def mock_render(*, render_spec=None, story_plan=None, output_path=None):
        output_path.write_bytes(b"dummy mp4 video bytes")
        return RemotionRenderOutput(output_path=output_path, size_bytes=len(b"dummy mp4 video bytes"))

    remotion_provider.render = MagicMock(side_effect=mock_render)

    render_engine = RenderEngine(
        media_storage=media_storage,
        remotion_provider=remotion_provider,
    )
    render_handler = RenderHandler(
        store=store,
        render_engine=render_engine,
        video_validator=VideoValidator(),
        stage_logger=StageLogger(),
    )

    # 4. Execute render stage
    video_record = render_handler.run(project_id, run_id)

    assert video_record.artifact_type == "video"
    assert video_record.status == "valid"
    assert video_record.parent_artifact_roles_json == {"continuous_story_plan": csp_artifact.id}

    # Verify Remotion was called with story_plan and StoryScene
    remotion_provider.render.assert_called_once()
    call_kwargs = remotion_provider.render.call_args.kwargs
    assert call_kwargs["story_plan"] == story_plan

    # Verify audio was staged to renderer public folder
    staged_audio = remotion_provider.renderer_root / "public" / "loan_narration.mp3"
    assert staged_audio.exists()
    assert staged_audio.read_bytes() == b"dummy audio content"

    # 5. Verify get_run_status reports video_assembly as skipped
    service = build_pipeline_service(store, render_engine=render_engine, media_storage=media_storage)
    status_list = service.get_run_status(project_id, run_id)
    status_by_stage = {s["stage"]: s["status"] for s in status_list}

    assert status_by_stage["continuous_story"] == "valid"
    assert status_by_stage["video_assembly"] == "skipped"
    assert status_by_stage["render"] == "valid"


def test_render_handler_composition_mode_preservation(temp_env):
    store: ArtifactStore = temp_env["store"]
    media_storage: LocalMediaStorage = temp_env["media_storage"]
    remotion_provider: RemotionProvider = temp_env["remotion_provider"]

    project = store.create_project("Composition Render Test")
    run = store.create_run(project.id)
    project_id, run_id = project.id, run.id

    # 1. Save GenerateVideoRequest with visual_mode=composition
    gen_req = GenerateVideoRequest(
        topic="Inflation Story",
        visual_mode=VisualMode.COMPOSITION,
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

    # 2. Save RenderSpec artifact
    render_spec = RenderSpec(
        scene_id="scene_comp_01",
        composition="VideoAssembly",
        fps=30,
        duration_frames=180,
        props=VideoAssemblyProps(
            scenes=[],
            audio=AudioSpec(audio_file_name="narration.mp3", local_path="narration.mp3", duration_seconds=6.0),
        ),
        frame_spans=[],
    )
    render_spec_artifact = store.save_artifact(
        project_id=project_id,
        run_id=run_id,
        artifact_type="render_spec",
        schema_version=render_spec.schema_version,
        payload_json=render_spec.model_dump(),
        parent_artifact_roles_json={},
        validation_json=ValidationResult(status="valid"),
    )

    def mock_render(*, render_spec=None, story_plan=None, output_path=None):
        output_path.write_bytes(b"dummy composition mp4")
        return RemotionRenderOutput(output_path=output_path, size_bytes=len(b"dummy composition mp4"))

    remotion_provider.render = MagicMock(side_effect=mock_render)

    render_engine = RenderEngine(
        media_storage=media_storage,
        remotion_provider=remotion_provider,
    )
    render_handler = RenderHandler(
        store=store,
        render_engine=render_engine,
        video_validator=VideoValidator(),
        stage_logger=StageLogger(),
    )

    # 3. Execute render stage
    video_record = render_handler.run(project_id, run_id)

    assert video_record.artifact_type == "video"
    assert video_record.status == "valid"
    assert video_record.parent_artifact_roles_json == {"render_spec": render_spec_artifact.id}

    # Verify Remotion was called with render_spec
    remotion_provider.render.assert_called_once()
    call_kwargs = remotion_provider.render.call_args.kwargs
    assert call_kwargs["render_spec"] == render_spec

    # 4. Verify get_run_status reports continuous_story as skipped
    service = build_pipeline_service(store, render_engine=render_engine, media_storage=media_storage)
    status_list = service.get_run_status(project_id, run_id)
    status_by_stage = {s["stage"]: s["status"] for s in status_list}

    assert status_by_stage["continuous_story"] == "skipped"
    assert status_by_stage["video_assembly"] == "valid"
    assert status_by_stage["render"] == "valid"
