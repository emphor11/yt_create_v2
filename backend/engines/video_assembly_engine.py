from domain.hook import Hook
from domain.script_visual_strategy import ScriptVisualStrategy
from domain.voice_track import VoiceTrack
from domain.render_spec import RenderSpec
from domain.video_assembly_props import TimedBeatSegment

from engines.video_assembly.timeline_builder import TimelineBuilder
from engines.video_assembly.asset_resolver import AssetResolver
from engines.video_assembly.component_resolver import ComponentResolver
from engines.video_assembly.render_spec_builder import RenderSpecBuilder

class VideoAssemblyEngine:
    def __init__(self, fps: int = 30):
        self.fps = fps
        self.timeline_builder = TimelineBuilder(fps=fps)
        self.asset_resolver = AssetResolver()
        self.component_resolver = ComponentResolver()
        self.render_spec_builder = RenderSpecBuilder(fps=fps)

    def run(
        self,
        *,
        scene_id: str,
        hook: Hook,
        strategy: ScriptVisualStrategy,
        voice_track: VoiceTrack,
    ) -> RenderSpec:
        # 1. Timeline Builder: build visual beat timing intervals
        timed_intervals = self.timeline_builder.build_timeline(
            hook=hook,
            strategy=strategy,
            voice_track=voice_track,
        )

        # 2. Map intervals to segments and resolve assets + components
        timed_segments = []
        resolved_assets = []
        resolved_components = []

        for interval in timed_intervals:
            if interval.section_type == "hook":
                directive = hook.visual_directives[interval.beat_index]
                preferred_component = None  # ComponentResolver dynamically resolves component
                visual_goal = directive.visual_instruction
                asset_query = None
                notes = directive.visual_instruction
                component_data = {"onscreen_text": directive.onscreen_text} if directive.onscreen_text else {}
                narration_text = hook.script_text
            else:
                idea = strategy.ideas[interval.section_index]
                beat = idea.visual_sequence[interval.beat_index]
                preferred_component = beat.preferred_component
                visual_goal = beat.visual_goal
                asset_query = beat.asset_query
                notes = beat.notes
                component_data = beat.component_data
                narration_text = idea.narration

            # Download/Cache background assets if needed
            asset_ref = self.asset_resolver.resolve_asset(
                asset_id=f"asset_{interval.beat_id}",
                preferred_component=preferred_component or "Typography",
                asset_query=asset_query,
            )
            resolved_assets.append(asset_ref)

            # Resolve visual component specification props
            comp_spec = self.component_resolver.resolve_component(
                preferred_component=preferred_component,
                visual_goal=visual_goal,
                component_data=component_data,
                narration_text=narration_text,
            )
            resolved_components.append(comp_spec)

            # Construct TimedBeatSegment
            segment = TimedBeatSegment(
                beat_id=interval.beat_id,
                start_frame=interval.start_frame,
                end_frame=interval.end_frame,
                duration_frames=interval.duration_frames,
                preferred_component=preferred_component,
                visual_goal=visual_goal,
                asset_query=asset_query,
                notes=notes,
                component_data=component_data,
                narration_text=narration_text
            )
            timed_segments.append(segment)

        # 3. RenderSpec Builder: compile final RenderSpec payload
        render_spec = self.render_spec_builder.build_render_spec(
            scene_id=scene_id,
            timed_segments=timed_segments,
            resolved_components=resolved_components,
            resolved_assets=resolved_assets,
            audio_file_name=voice_track.audio_file_name,
            audio_local_path=voice_track.storage_key,
            audio_duration_seconds=voice_track.duration_seconds,
        )

        return render_spec
