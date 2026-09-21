"""
CompositionAssemblyEngine — assembles RenderSpec using the Composition visual pipeline.

Reuses TimelineBuilder, AssetResolver, and RenderSpecBuilder.
Uses CompositionResolver for mapping composition beats into ComponentSpecs.
"""
from __future__ import annotations

from typing import Any

from domain.hook import Hook
from domain.script_visual_strategy import ScriptVisualStrategy
from domain.composition_plan import FullCompositionPlan
from domain.voice_track import VoiceTrack
from domain.render_spec import RenderSpec
from domain.video_assembly_props import TimedBeatSegment

from engines.video_assembly.timeline_builder import TimelineBuilder
from engines.video_assembly.asset_resolver import AssetResolver
from engines.video_assembly.component_resolver import ComponentResolver
from engines.video_assembly.composition_resolver import CompositionResolver
from engines.video_assembly.render_spec_builder import RenderSpecBuilder


class CompositionAssemblyEngine:
    def __init__(self, fps: int = 30):
        self.fps = fps
        self.timeline_builder = TimelineBuilder(fps=fps)
        self.asset_resolver = AssetResolver()
        self.legacy_component_resolver = ComponentResolver()
        self.composition_resolver = CompositionResolver()
        self.render_spec_builder = RenderSpecBuilder(fps=fps)

    def _resolve_safe_stock_query(
        self,
        asset_query: str | None,
        narration_text: str | None,
    ) -> str:
        """
        Ensures that stock media queries sent to AssetResolver are concrete 2-6 word visual phrases.
        NEVER sends 'Viewer understands...', explanatory sentences, or truncated narration fragments.
        """
        if asset_query and isinstance(asset_query, str):
            q = asset_query.strip()
            q_lower = q.lower()
            if (
                not any(pat in q_lower for pat in ("viewer ", "viewer's", "viewers", "understand", "realize", "grasp"))
                and not any(punct in q for punct in (".", ";", "?", "!"))
                and len(q.split()) <= 8
            ):
                return q

        # Extract concrete physical phrase from narration if available
        if narration_text:
            nt = narration_text.lower()
            if any(k in nt for k in ("tire", "tires", "mechanic", "servicing", "maintenance", "detailing")):
                return "mechanic changing car tire"
            if any(k in nt for k in ("dealership", "showroom", "salesperson", "sales pitch")):
                return "car dealership showroom"
            if any(k in nt for k in ("insurance", "totaled", "accident", "stolen")):
                return "car insurance paperwork"
            if any(k in nt for k in ("fuel", "gas station", "petrol")):
                return "driver filling car fuel"
            if any(k in nt for k in ("luxury", "valet", "lifestyle creep", "premium vehicle")):
                return "luxury car interior"
            if any(k in nt for k in ("pre-owned", "used car")):
                return "used car showroom"
            if any(k in nt for k in ("loan", "emi", "bank", "interest", "financing", "underwater")):
                return "car loan paperwork"
            if any(k in nt for k in ("invest", "portfolio", "index fund", "compound")):
                return "person reviewing investments"
            if any(k in nt for k in ("budget", "expenses", "cash flow", "cannibalize", "savings")):
                return "person calculating expenses"
            if any(k in nt for k in ("car", "vehicle", "drive", "driving", "road")):
                return "car driving on road"

        return "car finance paperwork"

    def run(
        self,
        *,
        scene_id: str,
        hook: Hook,
        strategy: ScriptVisualStrategy,
        composition_plan: FullCompositionPlan,
        voice_track: VoiceTrack,
    ) -> RenderSpec:
        # Build timeline using Composition Plan for accurate interval alignment
        timed_intervals = self.timeline_builder.build_timeline(
            hook=hook,
            strategy=strategy,
            composition_plan=composition_plan,
            voice_track=voice_track,
        )

        timed_segments: list[TimedBeatSegment] = []
        resolved_assets: list[Any] = []
        resolved_components: list[Any] = []

        for interval in timed_intervals:
            if interval.section_type == "hook":
                if (
                    composition_plan.hook_plan is not None
                    and len(composition_plan.hook_plan.beats) > interval.beat_index
                ):
                    comp_beat = composition_plan.hook_plan.beats[interval.beat_index]
                    preferred_component = comp_beat.composition_id
                    visual_goal = comp_beat.visual_goal
                    asset_query = comp_beat.asset_query
                    notes = visual_goal
                    component_data = comp_beat.composition_data
                    narration_text = hook.script_text

                    # Resolve asset if required
                    unique_asset_id = f"asset_comp_hook_{interval.beat_index}_{interval.beat_id}"
                    asset_component = "StockVideo" if comp_beat.asset_requirement != "none" else "Typography"
                    safe_query = self._resolve_safe_stock_query(asset_query, narration_text)
                    asset_ref = self.asset_resolver.resolve_asset(
                        asset_id=unique_asset_id,
                        preferred_component=asset_component,
                        asset_query=safe_query,
                    )
                    resolved_assets.append(asset_ref)

                    comp_spec = self.composition_resolver.resolve_composition(
                        composition_id=comp_beat.composition_id,
                        composition_data=comp_beat.composition_data,
                        variant=comp_beat.variant,
                        visual_goal=visual_goal,
                        narration_text=narration_text,
                    )
                    resolved_components.append(comp_spec)
                else:
                    # Legacy hook fallback
                    directive = hook.visual_directives[interval.beat_index]
                    preferred_component = directive.preferred_component or "Typography"
                    visual_goal = directive.visual_goal or directive.visual_instruction or ""
                    asset_query = directive.asset_query
                    notes = directive.notes or visual_goal
                    component_data = directive.component_data
                    narration_text = hook.script_text

                    unique_asset_id = f"asset_hook_0_{interval.beat_index}_{interval.beat_id}"
                    safe_query = self._resolve_safe_stock_query(asset_query, narration_text)
                    asset_ref = self.asset_resolver.resolve_asset(
                        asset_id=unique_asset_id,
                        preferred_component=preferred_component,
                        asset_query=safe_query,
                    )
                    resolved_assets.append(asset_ref)

                    comp_spec = self.legacy_component_resolver.resolve_component(
                        preferred_component=preferred_component,
                        visual_goal=visual_goal,
                        component_data=component_data,
                        narration_text=narration_text,
                    )
                    resolved_components.append(comp_spec)

            else:
                comp_idea = composition_plan.ideas[interval.section_index]
                comp_beat = comp_idea.beats[interval.beat_index]
                narration_text = comp_idea.narration

                preferred_component = comp_beat.composition_id
                visual_goal = comp_beat.visual_goal
                asset_query = comp_beat.asset_query
                notes = visual_goal
                component_data = comp_beat.composition_data

                # Resolve asset if required
                unique_asset_id = f"asset_comp_{interval.section_index}_{interval.beat_index}_{interval.beat_id}"
                asset_component = "StockVideo" if comp_beat.asset_requirement != "none" else "Typography"
                safe_query = self._resolve_safe_stock_query(asset_query, narration_text)
                asset_ref = self.asset_resolver.resolve_asset(
                    asset_id=unique_asset_id,
                    preferred_component=asset_component,
                    asset_query=safe_query,
                )
                resolved_assets.append(asset_ref)

                comp_spec = self.composition_resolver.resolve_composition(
                    composition_id=comp_beat.composition_id,
                    composition_data=comp_beat.composition_data,
                    variant=comp_beat.variant,
                    visual_goal=visual_goal,
                    narration_text=narration_text,
                )
                resolved_components.append(comp_spec)

            segment = TimedBeatSegment(
                beat_id=interval.beat_id,
                start_frame=interval.start_frame,
                end_frame=interval.end_frame,
                duration_frames=interval.duration_frames,
                preferred_component=preferred_component,
                visual_goal=visual_goal,
                asset_query=safe_query,
                notes=notes,
                component_data=component_data,
                narration_text=narration_text,
            )
            timed_segments.append(segment)

        # 3. Build final RenderSpec
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
