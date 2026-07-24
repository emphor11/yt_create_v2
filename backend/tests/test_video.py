from pathlib import Path

from domain.render_spec import RenderFrameSpan, RenderSpec
from domain.validators.video_validator import VideoValidator
from domain.video import Video
from domain.video_assembly_props import VideoAssemblyProps, SceneSpec, ComponentSpec, AudioSpec
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
                        props={"text": "Hello world"}
                    ),
                    asset=None,
                    narration_text="Hello world"
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


def test_timeline_builder_trigger_words() -> None:
    from engines.video_assembly.timeline_builder import TimelineBuilder
    from domain.hook import Hook, VisualDirective as HookVisualDirective
    from domain.script_visual_strategy import ScriptVisualStrategy, VideoIdea, VisualStrategyBeat
    from domain.voice_track import VoiceTrack, WordTimestamp

    builder = TimelineBuilder(fps=30)
    hook = Hook(
        conceptual_hook="Hook",
        script_text="Is salary a drug?",
        visual_directives=[
            HookVisualDirective(beat_id="hook_beat_1", visual_instruction="Intro visual")
        ]
    )
    strategy = ScriptVisualStrategy(
        thesis="Thesis",
        ideas=[
            VideoIdea(
                idea_id="idea_01",
                title="Security",
                focus_concept="Opportunity Cost",
                core_teaching_point="Explain cost",
                narration="You think paycheck is safety, but it's a trap.",
                visual_sequence=[
                    VisualStrategyBeat(
                        beat_id="body_beat_1",
                        preferred_component="Typography",
                        visual_goal="Goal 1",
                        trigger_word=None,
                    ),
                    VisualStrategyBeat(
                        beat_id="body_beat_2",
                        preferred_component="Typography",
                        visual_goal="Goal 2",
                        trigger_word="safety",
                    ),
                    VisualStrategyBeat(
                        beat_id="body_beat_3",
                        preferred_component="Typography",
                        visual_goal="Goal 3",
                        trigger_word="trap",
                    )
                ]
            )
        ]
    )
    voice_track = VoiceTrack(
        voice_id="Matthew",
        audio_file_name="narration.mp3",
        storage_key="runs/run_xxx/narration.mp3",
        duration_seconds=5.0,
        full_script_text="Is salary a drug?\n\nYou think paycheck is safety, but it's a trap.",
        word_timestamps=[
            # Hook
            WordTimestamp(word="Is", start_ms=0, end_ms=200),
            WordTimestamp(word="salary", start_ms=200, end_ms=400),
            WordTimestamp(word="a", start_ms=400, end_ms=500),
            WordTimestamp(word="drug", start_ms=500, end_ms=800),
            # Body
            WordTimestamp(word="You", start_ms=1000, end_ms=1200),
            WordTimestamp(word="think", start_ms=1200, end_ms=1400),
            WordTimestamp(word="paycheck", start_ms=1400, end_ms=1800),
            WordTimestamp(word="is", start_ms=1800, end_ms=2000),
            WordTimestamp(word="safety", start_ms=2000, end_ms=2500), # Cut 1
            WordTimestamp(word="but", start_ms=2500, end_ms=2800),
            WordTimestamp(word="it's", start_ms=2800, end_ms=3000),
            WordTimestamp(word="a", start_ms=3000, end_ms=3200),
            WordTimestamp(word="trap", start_ms=3200, end_ms=3800), # Cut 2
        ]
    )

    timeline = builder.build_timeline(hook=hook, strategy=strategy, voice_track=voice_track)

    assert len(timeline) == 4
    # Hook beat
    assert timeline[0].beat_id == "hook_beat_1"
    assert timeline[0].start_frame == 0
    # body_beat_1 (starts at start of body section, i.e. "You" at 1000ms -> frame 30)
    assert timeline[1].beat_id == "body_beat_1"
    assert timeline[1].start_frame == timeline[0].end_frame # contiguous hook border
    # body_beat_2 (starts at trigger_word "safety" at 2000ms -> frame 60)
    assert timeline[2].beat_id == "body_beat_2"
    assert timeline[2].start_frame == timeline[1].end_frame
    # body_beat_3 (starts at trigger_word "trap" at 3200ms -> frame 96)
    assert timeline[3].beat_id == "body_beat_3"
    assert timeline[3].start_frame == timeline[2].end_frame


def test_timeline_builder_throws_on_missing_trigger() -> None:
    import pytest
    from engines.video_assembly.timeline_builder import TimelineBuilder, TimelineBuilderError
    from domain.hook import Hook, VisualDirective as HookVisualDirective
    from domain.script_visual_strategy import ScriptVisualStrategy, VideoIdea, VisualStrategyBeat
    from domain.voice_track import VoiceTrack, WordTimestamp

    builder = TimelineBuilder(fps=30)
    hook = Hook(
        conceptual_hook="Hook",
        script_text="Is salary a drug?",
        visual_directives=[
            HookVisualDirective(beat_id="hook_beat_1", visual_instruction="Intro visual")
        ]
    )
    strategy = ScriptVisualStrategy(
        thesis="Thesis",
        ideas=[
            VideoIdea(
                idea_id="idea_01",
                title="Security",
                focus_concept="Opportunity Cost",
                core_teaching_point="Explain cost",
                narration="You think paycheck is safety, but it's a trap.",
                visual_sequence=[
                    VisualStrategyBeat(
                        beat_id="body_beat_1",
                        preferred_component="Typography",
                        visual_goal="Goal 1",
                        trigger_word=None,
                    ),
                    VisualStrategyBeat(
                        beat_id="body_beat_2",
                        preferred_component="Typography",
                        visual_goal="Goal 2",
                        trigger_word="nonexistentword", # not present in narration
                    )
                ]
            )
        ]
    )
    voice_track = VoiceTrack(
        voice_id="Matthew",
        audio_file_name="narration.mp3",
        storage_key="runs/run_xxx/narration.mp3",
        duration_seconds=5.0,
        full_script_text="Is salary a drug?\n\nYou think paycheck is safety.",
        word_timestamps=[
            WordTimestamp(word="Is", start_ms=0, end_ms=200),
            WordTimestamp(word="salary", start_ms=200, end_ms=400),
            WordTimestamp(word="a", start_ms=400, end_ms=500),
            WordTimestamp(word="drug", start_ms=500, end_ms=800),
            WordTimestamp(word="You", start_ms=1000, end_ms=1200)
        ]
    )

    with pytest.raises(TimelineBuilderError) as exc_info:
        builder.build_timeline(hook=hook, strategy=strategy, voice_track=voice_track)
    assert "was not found in the voice track words" in str(exc_info.value)

