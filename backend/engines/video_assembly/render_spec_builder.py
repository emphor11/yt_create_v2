from domain.render_spec import RenderSpec, RenderFrameSpan
from domain.video_assembly_props import VideoAssemblyProps, SceneSpec, AudioSpec, AssetReference, TimedBeatSegment
from engines.video_assembly.component_resolver import ComponentSpec

class RenderSpecBuilder:
    def __init__(self, fps: int = 30):
        self.fps = fps

    def build_render_spec(
        self,
        *,
        scene_id: str,
        timed_segments: list[TimedBeatSegment],
        resolved_components: list[ComponentSpec],
        resolved_assets: list[AssetReference | None],
        audio_file_name: str,
        audio_local_path: str,
        audio_duration_seconds: float,
    ) -> RenderSpec:
        scenes: list[SceneSpec] = []
        frame_spans: list[RenderFrameSpan] = []
        
        total_duration_frames = int(round(audio_duration_seconds * self.fps))

        for idx, segment in enumerate(timed_segments):
            comp_spec = resolved_components[idx]
            asset_ref = resolved_assets[idx]

            # 1. Construct SceneSpec
            unique_scene_id = f"scene_{idx + 1:03d}"
            scene_spec = SceneSpec(
                scene_id=unique_scene_id,
                start_frame=segment.start_frame,
                end_frame=segment.end_frame,
                duration_frames=segment.duration_frames,
                component=comp_spec,
                asset=asset_ref,
                narration_text=segment.narration_text,
            )
            scenes.append(scene_spec)

            # 2. Construct RenderFrameSpan
            frame_span = RenderFrameSpan(
                event_id=unique_scene_id,
                start_frame=segment.start_frame,
                end_frame=segment.end_frame,
                duration_frames=segment.duration_frames,
            )
            frame_spans.append(frame_span)

        # 3. Construct AudioSpec
        audio_spec = AudioSpec(
            audio_file_name=audio_file_name,
            local_path=audio_local_path,
            duration_seconds=audio_duration_seconds,
        )

        # 4. Construct VideoAssemblyProps
        props = VideoAssemblyProps(
            scenes=scenes,
            audio=audio_spec,
        )

        # 5. Return final RenderSpec
        return RenderSpec(
            schema_version="1",
            scene_id=scene_id,
            composition="VideoAssembly",  # Abstract renderer-agnostic sequencer composition name
            fps=self.fps,
            duration_frames=total_duration_frames,
            props=props,
            frame_spans=frame_spans,
        )
