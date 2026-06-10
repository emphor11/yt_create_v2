from pathlib import Path

from domain.render_spec import RenderFrameSpan, RenderSpec
from domain.validators.video_validator import VideoValidator
from domain.video import Video
from domain.visual_plan import SplitComparisonProps, VisualPlanSide
from engines.render_engine import RenderEngine
from providers.media_storage import LocalMediaStorage
from providers.remotion_provider import RemotionProviderError, RemotionRenderOutput


class SuccessfulProvider:
    def render(self, *, render_spec: RenderSpec, output_path: Path) -> RemotionRenderOutput:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(b"fake mp4")
        return RemotionRenderOutput(output_path=output_path, size_bytes=8)


class FailingProvider:
    def render(self, *, render_spec: RenderSpec, output_path: Path) -> RemotionRenderOutput:
        raise RemotionProviderError("renderer unavailable")


def make_render_spec() -> RenderSpec:
    return RenderSpec(
        scene_id="scene_01",
        composition="SplitComparison",
        fps=30,
        duration_frames=240,
        props=SplitComparisonProps(
            left=VisualPlanSide(
                role="product_price",
                semantic_entity_id="entity_price",
                label="Full price",
                raw="₹80,000",
                value=80000,
                unit="INR",
            ),
            right=VisualPlanSide(
                role="monthly_payment",
                semantic_entity_id="entity_emi",
                label="Monthly payment",
                raw="₹6,667",
                value=6667,
                unit="INR",
            ),
            attention_shift_event_id="event_attention_shift",
        ),
        frame_spans=[
            RenderFrameSpan(
                event_id="event_full_price",
                start_frame=0,
                end_frame=80,
                duration_frames=80,
            ),
            RenderFrameSpan(
                event_id="event_monthly_payment",
                start_frame=80,
                end_frame=160,
                duration_frames=80,
            ),
            RenderFrameSpan(
                event_id="event_attention_shift",
                start_frame=160,
                end_frame=240,
                duration_frames=80,
            ),
        ],
    )


def test_render_engine_creates_successful_video_with_storage_key(tmp_path) -> None:
    render_spec = make_render_spec()
    media_storage = LocalMediaStorage(tmp_path / "media")
    engine = RenderEngine(
        media_storage=media_storage,
        remotion_provider=SuccessfulProvider(),
    )

    video = engine.run(render_spec=render_spec, project_id="project_1", run_id="run_1")

    assert video.render_status == "succeeded"
    assert video.storage_key == "projects/project_1/runs/run_1/scene_01.mp4"
    assert video.size_bytes == 8
    assert media_storage.path_for_key(video.storage_key or "").exists()


def test_video_validator_accepts_successful_video() -> None:
    render_spec = make_render_spec()
    video = Video(
        scene_id="scene_01",
        render_status="succeeded",
        file_name="scene_01.mp4",
        content_type="video/mp4",
        fps=30,
        duration_frames=240,
        storage_key="projects/project_1/runs/run_1/scene_01.mp4",
        size_bytes=8,
    )

    result = VideoValidator().validate(video, render_spec=render_spec)

    assert result.status == "valid"
    assert result.errors == []


def test_video_validator_blocks_absolute_storage_key() -> None:
    render_spec = make_render_spec()
    video = Video(
        scene_id="scene_01",
        render_status="succeeded",
        file_name="scene_01.mp4",
        content_type="video/mp4",
        fps=30,
        duration_frames=240,
        storage_key="/Users/example/scene_01.mp4",
        size_bytes=8,
    )

    result = VideoValidator().validate(video, render_spec=render_spec)

    assert result.status == "blocked"
    assert "Video storage_key must be relative." in result.errors


def test_render_engine_returns_failed_video_when_provider_fails(tmp_path) -> None:
    render_spec = make_render_spec()
    engine = RenderEngine(
        media_storage=LocalMediaStorage(tmp_path / "media"),
        remotion_provider=FailingProvider(),
    )

    video = engine.run(render_spec=render_spec, project_id="project_1", run_id="run_1")
    result = VideoValidator().validate(video, render_spec=render_spec)

    assert video.render_status == "failed"
    assert video.storage_key is None
    assert "renderer unavailable" in (video.error_message or "")
    assert result.status == "failed"
