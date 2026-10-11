"""Isolated compiler for the world-scoped visual architecture.

This compiler is intentionally independent from ``VisualCompiler``.  It emits
one global compiled world, resolves all timing and geometry before rendering,
and never produces a scene-local render tree.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
import re
from typing import Any

from compiler.models import CanvasConfig
from compiler.token_resolver import TokenResolver
from domain.primitives.common import CanonicalCapabilityType, PrimitiveStyle, SpringConfig
from domain.storyboard import (
    ContainerFlow,
    FlowAlignment,
    FlowJustification,
    MacroScreenZone,
    MicroLayoutFlow,
    MotionPreset,
    SemanticSpacing,
    SemanticStyleIntent,
    VisualActionType,
)
from domain.voice_track import VoiceTrack
from domain.visual_world import (
    SourceReference,
    StateChangeEvent,
    StateChangeKind,
    StoryboardBeat,
    VisualWorldSpec,
    WorldObjectSpec,
)
from registries.primitive_registry import PrimitiveRegistry

from compiler.world_models import (
    CompiledAnimationTrack,
    CompiledBeatInterval,
    CompiledLifecycleTrack,
    CompiledMacroZoneAllocation,
    CompiledObjectKind,
    CompiledPrimitive,
    CompiledSpeechAnchor,
    CompiledStateChange,
    CompiledStateTrack,
    CompiledTerminalHold,
    CompiledTransitionEvent,
    CompiledVisibilityInterval,
    CompiledVisualInstance,
    CompiledWorld,
    LocalRect,
    Point2D,
    ResolvedConnectorPath,
)
try:
    from registries.visual_component_registry import ComponentCategory, VisualComponentRegistry
except ImportError:
    from backend.registries.visual_component_registry import ComponentCategory, VisualComponentRegistry
from domain.timing_contract import (
    CanonicalVoiceTrack,
    NarrationSpanAmbiguousError,
    NarrationSpanNotFoundError,
    ResolvedNarrationSpan,
    ResolvedTriggerAnchor,
    TimedSpokenSpan,
    TimingResolutionError,
    TriggerWordAmbiguousError,
    TriggerWordNotFoundError,
)


class WorldCompilerError(TimingResolutionError):
    """Raised when a world cannot be deterministically compiled."""
    pass


class CompilerNarrationSpanNotFoundError(WorldCompilerError, NarrationSpanNotFoundError):
    pass


class CompilerNarrationSpanAmbiguousError(WorldCompilerError, NarrationSpanAmbiguousError):
    pass


class CompilerTriggerWordNotFoundError(WorldCompilerError, TriggerWordNotFoundError):
    pass


class CompilerTriggerWordAmbiguousError(WorldCompilerError, TriggerWordAmbiguousError):
    pass


@dataclass(frozen=True)
class _Box:
    x: float
    y: float
    width: float
    height: float

    @property
    def right(self) -> float:
        return self.x + self.width

    @property
    def bottom(self) -> float:
        return self.y + self.height

    @property
    def center_x(self) -> float:
        return self.x + self.width / 2.0

    @property
    def center_y(self) -> float:
        return self.y + self.height / 2.0


@dataclass(frozen=True)
class _WordSpan:
    index: int
    word: str
    start_ms: int
    end_ms: int


@dataclass(frozen=True)
class _BeatResolution:
    beat: StoryboardBeat
    start_ms: int
    end_ms: int
    start_frame: int
    end_frame: int
    first_word_index: int
    last_word_index: int


@dataclass(frozen=True)
class _ResolvedAnchor:
    anchor_id: str
    beat_id: str
    text: str
    occurrence: int
    start_ms: int
    end_ms: int
    global_frame: int


class WorldCompiler:
    """Deterministic compiler for one continuous ``VisualWorldSpec``."""

    def __init__(
        self,
        *,
        canvas_config: CanvasConfig | None = None,
        token_resolver: TokenResolver | None = None,
    ) -> None:
        self.canvas_config = canvas_config or CanvasConfig()
        self.token_resolver = token_resolver or TokenResolver()

        self._world: VisualWorldSpec | None = None
        self._beat_resolutions: dict[str, _BeatResolution] = {}
        self._objects: dict[str, WorldObjectSpec] = {}
        self._children: dict[str | None, list[str]] = {}
        # Base geometry is the object's geometry at its first active beat.
        # Later layout changes are represented as state/animation tracks.
        self._geometry: dict[str, _Box] = {}
        # Effective geometry per beat, used for deterministic validation and diagnostics.
        self._beat_geometry: dict[tuple[str, str], _Box] = {}
        self._world_origins: dict[str, tuple[float, float]] = {}
        self._compiled_primitives: dict[str, CompiledPrimitive] = {}
        self._compiled_objects: dict[str, CompiledVisualInstance] = {}
        self._resolved_anchors: dict[str, _ResolvedAnchor] = {}
        self._all_state_events: dict[str, StateChangeEvent] = {}
        self._state_initials: dict[str, dict[str, Any]] = {}
        self._macro_zone_allocations: list[CompiledMacroZoneAllocation] = []
        self._total_duration_frames = 0

    def compile(self, world: VisualWorldSpec, voice_track: VoiceTrack) -> CompiledWorld:
        """Compile one semantic world into one globally timed result."""
        self._reset(world)
        total_duration_frames = round(voice_track.duration_seconds * self.canvas_config.fps)
        if total_duration_frames <= 0:
            raise WorldCompilerError("VoiceTrack duration must resolve to at least one frame.")
        self._total_duration_frames = total_duration_frames
        self._resolve_beat_timeline(voice_track)
        self._collect_state_events()
        self._resolve_speech_anchors(voice_track)
        self._resolve_geometry()
        self._resolve_connector_paths()
        self._resolve_primitives()
        lifecycle_tracks = self._compile_lifecycle_tracks()
        visibility_intervals = self._compile_visibility_intervals(lifecycle_tracks)
        state_tracks, animation_tracks = self._compile_state_and_animation_tracks()
        transition_events = self._compile_transition_events()
        if any(
            resolution.end_frame > total_duration_frames
            for resolution in self._beat_resolutions.values()
        ):
            raise WorldCompilerError("A beat timestamp exceeds the authoritative VoiceTrack duration.")

        compiled = CompiledWorld(
            world_id=world.world_id,
            canvas_config=self.canvas_config,
            total_duration_frames=total_duration_frames,
            beat_intervals=[
                CompiledBeatInterval(
                    beat_id=resolution.beat.beat_id,
                    start_ms=resolution.start_ms,
                    end_ms=resolution.end_ms,
                    start_frame=resolution.start_frame,
                    end_frame=resolution.end_frame,
                )
                for resolution in self._beat_resolutions.values()
            ],
            speech_anchors=[
                CompiledSpeechAnchor(
                    anchor_id=anchor.anchor_id,
                    beat_id=anchor.beat_id,
                    text=anchor.text,
                    occurrence=anchor.occurrence,
                    start_ms=anchor.start_ms,
                    end_ms=anchor.end_ms,
                    global_frame=anchor.global_frame,
                )
                for anchor in self._resolved_anchors.values()
            ],
            transition_events=transition_events,
            objects=self._compiled_objects,
            primitives=self._compiled_primitives,
            lifecycle_tracks=lifecycle_tracks,
            visibility_intervals=visibility_intervals,
            state_tracks=state_tracks,
            animation_tracks=animation_tracks,
            terminal_hold=self._compile_terminal_hold(),
            macro_zone_allocations=self._macro_zone_allocations,
            semantic_lineage=self._lineage(world),
        )
        return compiled

    def _reset(self, world: VisualWorldSpec) -> None:
        self._world = world
        self._canonical_voice_track = None
        self._beat_span_resolutions = {}
        self._beat_resolutions = {}
        self._objects = {obj.object_id: obj for obj in world.objects}
        self._children = {None: []}
        for obj in world.objects:
            self._children.setdefault(obj.parent_object_id, []).append(obj.object_id)
        self._geometry = {}
        self._beat_geometry = {}
        self._world_origins = {}
        self._compiled_primitives = {}
        self._compiled_objects = {}
        self._resolved_anchors = {}
        self._all_state_events = {}
        self._state_initials = {obj.object_id: dict(obj.initial_state) for obj in world.objects}
        for track in world.object_state_tracks:
            if track.initial_state:
                self._state_initials[track.object_id] = dict(track.initial_state)
        self._macro_zone_allocations = []
        self._total_duration_frames = 0
        from collections import Counter

        item_counts = Counter(
            (obj.primitive_type.value if obj.primitive_type else f"component:{obj.component_type}")
            for obj in world.objects
        )

        print("\n=== WORLD COMPILER INPUT ===")
        print(f"world_id: {world.world_id}")
        print(f"object_count: {len(world.objects)}")
        print(f"item_counts: {dict(item_counts)}")

        for obj in world.objects:
            kind_str = obj.primitive_type.value if obj.primitive_type else f"component:{obj.component_type}"
            print(
                f"  {obj.object_id} | "
                f"{kind_str} | "
                f"parent={obj.parent_object_id}"
            )

        print("============================\n")

    def _resolve_beat_timeline(self, voice_track: VoiceTrack) -> None:
        assert self._world is not None
        canonical_vt = CanonicalVoiceTrack.from_voice_track(voice_track)
        self._canonical_voice_track = canonical_vt

        if not canonical_vt.spans:
            raise WorldCompilerError("World compilation requires VoiceTrack word timestamps.")

        search_start_char = 0
        for beat in self._world.beats:
            try:
                span_res = canonical_vt.resolve_narration_span(
                    beat_id=beat.beat_id,
                    narration=beat.narration,
                    search_start_char=search_start_char,
                    world_id=self._world.world_id,
                )
            except NarrationSpanNotFoundError as exc:
                raise CompilerNarrationSpanNotFoundError(
                    requested_text=exc.requested_text,
                    canonical_search_text=exc.canonical_search_text,
                    beat_id=exc.beat_id,
                    world_id=exc.world_id,
                    source_span=exc.source_span,
                    message=str(exc),
                ) from exc
            except NarrationSpanAmbiguousError as exc:
                raise CompilerNarrationSpanAmbiguousError(
                    requested_text=exc.requested_text,
                    canonical_search_text=exc.canonical_search_text,
                    match_count=exc.match_count,
                    beat_id=exc.beat_id,
                    world_id=exc.world_id,
                    source_span=exc.source_span,
                    message=str(exc),
                ) from exc

            self._beat_span_resolutions[beat.beat_id] = span_res
            search_start_char = span_res.end_char

            start_frame = self._ms_to_frame(span_res.start_ms)
            end_frame = self._ms_to_frame(span_res.end_ms)
            if end_frame < start_frame:
                raise WorldCompilerError(f"Beat '{beat.beat_id}' resolved to an inverted frame span.")

            self._beat_resolutions[beat.beat_id] = _BeatResolution(
                beat=beat,
                start_ms=span_res.start_ms,
                end_ms=span_res.end_ms,
                start_frame=start_frame,
                end_frame=end_frame,
                first_word_index=span_res.first_span_index,
                last_word_index=span_res.last_span_index,
            )

    def _collect_state_events(self) -> None:
        assert self._world is not None
        for beat in self._world.beats:
            for event in beat.state_change_events:
                self._all_state_events[event.event_id] = event
        for track in self._world.object_state_tracks:
            for event in track.state_changes:
                self._all_state_events[event.event_id] = event

    def _resolve_speech_anchors(self, voice_track: VoiceTrack) -> None:
        assert self._world is not None
        assert self._canonical_voice_track is not None

        for resolution in self._beat_resolutions.values():
            beat_start = resolution.start_frame
            beat_end = resolution.end_frame
            beat_duration = beat_end - beat_start

            # Check if any objects are preserved from a previous beat into this beat
            has_preserved_objects = bool(
                resolution.beat.transition_intent and resolution.beat.transition_intent.preserve_object_ids
            )

            # Identify the first enter/appear action in this beat
            first_enter_action_id: str | None = None
            for action in resolution.beat.actions:
                if action.action_type in {VisualActionType.ENTER, VisualActionType.APPEAR}:
                    first_enter_action_id = action.action_id
                    break

            for action in resolution.beat.actions:
                anchor_id = f"action:{resolution.beat.beat_id}:{action.action_id}"
                if anchor_id in self._resolved_anchors:
                    raise WorldCompilerError(f"Duplicate resolved speech anchor '{anchor_id}'.")
                anchor = self._resolve_word_anchor(
                    anchor_id=anchor_id,
                    beat_resolution=resolution,
                    text=action.trigger_word,
                    occurrence=action.trigger_occurrence,
                )

                clamped_frame = anchor.global_frame
                # Black void elimination: The first visual element entering this beat must never
                # leave the audience staring at an empty black canvas. If its enter action
                # anchor resolved later than beat_start + 15 frames (>0.5s into the beat),
                # anchor it immediately at beat_start.
                if action.action_id == first_enter_action_id and action.action_type in {VisualActionType.ENTER, VisualActionType.APPEAR}:
                    if clamped_frame > beat_start + 15:
                        clamped_frame = beat_start
                elif action.action_type in {VisualActionType.ENTER, VisualActionType.APPEAR}:
                    # Secondary enter actions should not exceed the beat's end minus readability window
                    if beat_duration >= 90 and clamped_frame > beat_end - 60:
                        clamped_frame = max(beat_start + 15, beat_end - 60)

                if clamped_frame != anchor.global_frame:
                    anchor = _ResolvedAnchor(
                        anchor_id=anchor.anchor_id,
                        beat_id=anchor.beat_id,
                        text=anchor.text,
                        occurrence=anchor.occurrence,
                        start_ms=self._frame_to_ms(clamped_frame),
                        end_ms=anchor.end_ms,
                        global_frame=clamped_frame,
                    )

                self._resolved_anchors[anchor_id] = anchor

            for event in resolution.beat.state_change_events:
                if event.speech_anchor is None:
                    continue
                if event.speech_anchor.beat_id != resolution.beat.beat_id:
                    raise WorldCompilerError(
                        f"Speech anchor '{event.speech_anchor.anchor_id}' belongs to "
                        f"beat '{event.speech_anchor.beat_id}', not '{resolution.beat.beat_id}'."
                    )
                anchor = self._resolve_declared_anchor(
                    event.speech_anchor.anchor_id,
                    resolution,
                    event.speech_anchor.text,
                    event.speech_anchor.occurrence,
                )
                if anchor.anchor_id in self._resolved_anchors:
                    raise WorldCompilerError(
                        f"Duplicate resolved speech anchor '{anchor.anchor_id}'."
                    )
                self._resolved_anchors[anchor.anchor_id] = anchor

            for track in self._world.object_state_tracks:
                for event in track.state_changes:
                    if event.beat_id != resolution.beat.beat_id or event.speech_anchor is None:
                        continue
                    if event.speech_anchor.beat_id != resolution.beat.beat_id:
                        raise WorldCompilerError(
                            f"Speech anchor '{event.speech_anchor.anchor_id}' belongs to "
                            f"beat '{event.speech_anchor.beat_id}', not '{resolution.beat.beat_id}'."
                        )
                    anchor = self._resolve_declared_anchor(
                        event.speech_anchor.anchor_id,
                        resolution,
                        event.speech_anchor.text,
                        event.speech_anchor.occurrence,
                    )
                    if anchor.anchor_id in self._resolved_anchors:
                        raise WorldCompilerError(
                            f"Duplicate resolved speech anchor '{anchor.anchor_id}'."
                        )
                    self._resolved_anchors[anchor.anchor_id] = anchor

    def _resolve_declared_anchor(
        self,
        anchor_id: str,
        resolution: _BeatResolution,
        text: str,
        occurrence: int,
        words: list[_WordSpan] | None = None,
    ) -> _ResolvedAnchor:
        return self._resolve_word_anchor(
            anchor_id=anchor_id,
            beat_resolution=resolution,
            text=text,
            occurrence=occurrence,
        )

    def _resolve_word_anchor(
        self,
        *,
        anchor_id: str,
        beat_resolution: _BeatResolution,
        text: str,
        occurrence: int,
        words: list[_WordSpan] | None = None,
    ) -> _ResolvedAnchor:
        assert self._canonical_voice_track is not None
        span_res = self._beat_span_resolutions.get(beat_resolution.beat.beat_id)
        if span_res is None:
            span_res = self._canonical_voice_track.resolve_narration_span(
                beat_id=beat_resolution.beat.beat_id,
                narration=beat_resolution.beat.narration,
                search_start_char=0,
                world_id=self._world.world_id if self._world else None,
            )

        try:
            anchor_res = self._canonical_voice_track.resolve_trigger_anchor(
                action_id=anchor_id,
                beat_id=beat_resolution.beat.beat_id,
                trigger_word=text,
                occurrence=occurrence,
                beat_span=span_res,
                world_id=self._world.world_id if self._world else None,
            )
        except TriggerWordNotFoundError as exc:
            raise CompilerTriggerWordNotFoundError(
                trigger_word=exc.trigger_word,
                canonical_search_text=exc.canonical_search_text,
                action_id=exc.action_id,
                beat_id=exc.beat_id,
                world_id=exc.world_id,
                source_span=exc.source_span,
                message=str(exc),
            ) from exc
        except TriggerWordAmbiguousError as exc:
            if exc.match_count > 0 and exc.occurrence > exc.match_count:
                # Resilient fallback: clamp to the latest available match rather than hard-crashing
                anchor_res = self._canonical_voice_track.resolve_trigger_anchor(
                    action_id=anchor_id,
                    beat_id=beat_resolution.beat.beat_id,
                    trigger_word=text,
                    occurrence=exc.match_count,
                    beat_span=span_res,
                    world_id=self._world.world_id if self._world else None,
                )
            else:
                raise CompilerTriggerWordAmbiguousError(
                    trigger_word=exc.trigger_word,
                    canonical_search_text=exc.canonical_search_text,
                    occurrence=exc.occurrence,
                    match_count=exc.match_count,
                    action_id=exc.action_id,
                    beat_id=exc.beat_id,
                    world_id=exc.world_id,
                    source_span=exc.source_span,
                    message=str(exc),
                ) from exc

        return _ResolvedAnchor(
            anchor_id=anchor_id,
            beat_id=beat_resolution.beat.beat_id,
            text=text,
            occurrence=occurrence,
            start_ms=anchor_res.start_ms,
            end_ms=anchor_res.end_ms,
            global_frame=self._ms_to_frame(anchor_res.start_ms),
        )

    @staticmethod
    def _find_exact_sequence(
        words: list[_WordSpan], target: list[str], start_index: int
    ) -> int | None:
        for index in range(start_index, len(words) - len(target) + 1):
            if [word.word for word in words[index : index + len(target)]] == target:
                return index
        return None

    def _ms_to_frame(self, milliseconds: int) -> int:
        return round(milliseconds / 1000.0 * self.canvas_config.fps)

    def _frame_to_ms(self, frame: int) -> int:
        return round(frame / self.canvas_config.fps * 1000.0)

    def _resolve_geometry(self) -> None:
        """Resolve stable base geometry and per-beat effective root geometry.

        Important contract:
        - base ``_geometry`` is the first active placement of each object; it is
          the geometry stored on the compiled primitive.
        - layout state changes do not mutate the base geometry. They become
          animation/state tracks later in the pipeline.
        - collision validation uses the effective geometry at each beat, so
          broad macro-zone rectangles never create false positives.
        """
        assert self._world is not None
        self._validate_membership_and_zone_consistency()

        roots = self._children.get(None, [])
        if not roots:
            raise WorldCompilerError("World must contain at least one root object.")

        # Allocate the initial/root geometry from the first beat of each root.
        root_zones: dict[str, MacroScreenZone] = {}
        for root_id in roots:
            beat = self._first_beat_for_object(root_id)
            zone = self._zone_for_object(root_id, beat)
            root_zones[root_id] = zone
            self._macro_zone_allocations.append(
                CompiledMacroZoneAllocation(
                    object_id=root_id,
                    zone=zone,
                    rect=_local_rect(self._zone_rect(zone)),
                )
            )

        root_boxes: dict[str, _Box] = {}
        for root_id in roots:
            if root_id in root_boxes:
                continue
            beat = self._first_beat_for_object(root_id)
            zone = root_zones[root_id]
            region = self._zone_rect(zone)

            # Only roots that are simultaneously active in this first beat and in the same zone share space.
            coactive_roots = [
                r
                for r in roots
                if beat.beat_id in self._objects[r].beat_ids
                and self._zone_for_object(r, beat) == zone
            ]

            if len(coactive_roots) == 1:
                if self._objects[root_id].primitive_type == CanonicalCapabilityType.GROUP:
                    box = region
                else:
                    intrinsic = self._intrinsic_size(root_id, beat)
                    if intrinsic[0] > region.width or intrinsic[1] > region.height:
                        safe = self.canvas_config.safe_rect
                        if intrinsic[0] > safe.width or intrinsic[1] > safe.height:
                            raise WorldCompilerError(
                                f"Root object '{root_id}' overflows macro zone '{zone.value}' "
                                f"[world={self._world.world_id}, zone={zone.value}]: "
                                f"available=({region.width:.1f}x{region.height:.1f}), "
                                f"required=({intrinsic[0]:.1f}x{intrinsic[1]:.1f})."
                            )
                        new_w = max(region.width, min(safe.width, intrinsic[0]))
                        new_h = max(region.height, min(safe.height, intrinsic[1]))
                        new_x = max(safe.x, min(region.x, safe.right - new_w))
                        new_y = max(safe.y, min(region.y, safe.bottom - new_h))
                        region = _Box(new_x, new_y, new_w, new_h)
                    box = self._root_box_for_intrinsic(root_id, region, intrinsic)
                root_boxes[root_id] = box
            else:
                shared = self._compute_shared_root_boxes(coactive_roots, region)
                root_boxes.update(shared)

        self._geometry.update(root_boxes)

        # Walk the world in temporal order. A layout event changes the current
        # effective box for that object from this beat onward.
        current_boxes = dict(root_boxes)
        for beat in self._world.beats:
            active_roots = [
                root_id
                for root_id in roots
                if beat.beat_id in self._objects[root_id].beat_ids
            ]

            effective_boxes: dict[str, _Box] = {}

            for root_id in active_roots:
                layout_events = [
                    event
                    for event in beat.state_change_events
                    if event.object_id == root_id
                    and event.kind == StateChangeKind.LAYOUT
                ]
                if len(layout_events) > 1:
                    raise WorldCompilerError(
                        f"Object '{root_id}' has multiple layout events in beat '{beat.beat_id}'."
                    )

                if layout_events:
                    current_boxes[root_id] = self._resolve_layout_event_geometry(
                        layout_events[0]
                    )

                if root_id not in current_boxes:
                    raise WorldCompilerError(
                        f"No root geometry resolved for '{root_id}' in beat '{beat.beat_id}'."
                    )

                effective_boxes[root_id] = current_boxes[root_id]

            # Detect multiple active roots co-located in the same zone in this beat
            roots_by_zone: dict[MacroScreenZone, list[str]] = {}
            for root_id in active_roots:
                evs = [
                    e for e in beat.state_change_events
                    if e.object_id == root_id and e.kind == StateChangeKind.LAYOUT
                ]
                if evs and evs[0].layout_intent and evs[0].layout_intent.macro_zone:
                    z = evs[0].layout_intent.macro_zone
                else:
                    z = self._zone_for_object(root_id, beat)
                roots_by_zone.setdefault(z, []).append(root_id)

            for z, z_roots in roots_by_zone.items():
                if len(z_roots) > 1:
                    region = self._zone_rect(z)
                    shared = self._compute_shared_root_boxes(z_roots, region, beat, z)
                    for rid, sbox in shared.items():
                        current_boxes[rid] = sbox
                        effective_boxes[rid] = sbox

            for root_id in active_roots:
                self._beat_geometry[(beat.beat_id, root_id)] = current_boxes[root_id]

            self._reject_overlapping_root_allocations(effective_boxes, beat)

            # Child layout remains parent-local to the stable root box. A root
            # layout transition moves the whole subtree through the state track.
            for root_id in active_roots:
                self._layout_node(root_id, root_boxes[root_id], beat)

        self._compute_world_origins()

    def _validate_membership_and_zone_consistency(self) -> None:
        """Validate persistent layout transitions before geometry compilation."""
        assert self._world is not None

        beat_index = {beat.beat_id: index for index, beat in enumerate(self._world.beats)}

        for obj in self._world.objects:
            if not obj.beat_ids:
                raise WorldCompilerError(f"Object '{obj.object_id}' has no beat membership.")

            ordered = sorted(obj.beat_ids, key=lambda beat_id: beat_index[beat_id])
            if ordered != obj.beat_ids:
                raise WorldCompilerError(
                    f"Object '{obj.object_id}' beat membership must follow world order."
                )

    def _zone_for_object(
        self,
        object_id: str,
        beat: StoryboardBeat,
    ) -> MacroScreenZone:
        obj = self._objects[object_id]

        # 1. Explicit layout in the current beat wins.
        element_layout = beat.element_layouts.get(object_id)
        if element_layout and element_layout.macro_zone:
            raw_zone = element_layout.macro_zone
        else:
            # 2. No new layout instruction means the object keeps
            #    its most recently known position.
            assert self._world is not None

            current_index = next(
                index
                for index, candidate in enumerate(self._world.beats)
                if candidate.beat_id == beat.beat_id
            )

            previous_zone = None

            for previous_beat in reversed(self._world.beats[:current_index]):
                if previous_beat.beat_id not in obj.beat_ids:
                    continue

                previous_layout = previous_beat.element_layouts.get(object_id)
                if previous_layout and previous_layout.macro_zone:
                    previous_zone = previous_layout.macro_zone
                    break

            if previous_zone is not None:
                raw_zone = previous_zone
            else:
                # 3. Object has never had an explicit layout yet.
                raw_zone = (
                    obj.semantic_content.get("macro_zone")
                    or beat.macro_zone
                    or MacroScreenZone.CENTER
                )

        try:
            return (
                raw_zone
                if isinstance(raw_zone, MacroScreenZone)
                else MacroScreenZone(str(raw_zone))
            )
        except ValueError as error:
            raise WorldCompilerError(
                f"Invalid macro zone '{raw_zone}' for '{object_id}'."
            ) from error
        
    def _zone_rect(self, zone: MacroScreenZone) -> _Box:
        safe = self.canvas_config.safe_rect
        sx, sy, sw, sh = safe.x, safe.y, safe.width, safe.height
        gap = 32.0
        half_w = (sw - gap) / 2.0
        half_h = (sh - gap) / 2.0

        content_y = sy + sh * 0.18
        content_h = sh * 0.64

        if zone == MacroScreenZone.CENTER:
            return _Box(sx + sw * 0.14, content_y, sw * 0.72, content_h)
        if zone in (MacroScreenZone.LEFT, MacroScreenZone.SPLIT_LEFT):
            return _Box(sx, content_y, half_w, content_h)
        if zone in (MacroScreenZone.RIGHT, MacroScreenZone.SPLIT_RIGHT):
            return _Box(sx + half_w + gap, content_y, half_w, content_h)
        if zone in (MacroScreenZone.TOP, MacroScreenZone.SPLIT_TOP):
            return _Box(sx, sy, sw, half_h)
        if zone in (MacroScreenZone.BOTTOM, MacroScreenZone.SPLIT_BOTTOM):
            return _Box(sx, sy + sh - half_h, sw, half_h)
        if zone in {
            MacroScreenZone.TOP_LEFT,
            MacroScreenZone.TOP_RIGHT,
            MacroScreenZone.BOTTOM_LEFT,
            MacroScreenZone.BOTTOM_RIGHT,
        }:
            width, height = sw * 0.45, sh * 0.45
            x = sx if zone in {MacroScreenZone.TOP_LEFT, MacroScreenZone.BOTTOM_LEFT} else sx + sw - width
            y = sy if zone in {MacroScreenZone.TOP_LEFT, MacroScreenZone.TOP_RIGHT} else sy + sh - height
            return _Box(x, y, width, height)
        if zone == MacroScreenZone.FULL_SCREEN:
            full = self.canvas_config.full_rect
            return _Box(full.x, full.y, full.width, full.height)
        raise WorldCompilerError(f"Unsupported macro zone '{zone}'.")

    def _reject_overlapping_root_allocations(
        self,
        boxes: dict[str, _Box],
        beat: StoryboardBeat,
    ) -> None:
        """Resolve residual object-box collisions or log diagnostics."""
        root_ids = list(boxes)
        for index, first_id in enumerate(root_ids):
            first = boxes[first_id]
            for second_id in root_ids[index + 1 :]:
                second = boxes[second_id]
                if _boxes_overlap(first, second):
                    gap = 16.0
                    # Try horizontal shift within safe canvas bounds
                    if first.right + gap + second.width <= self.canvas_config.width - self.canvas_config.safe_margin_x:
                        shifted = _Box(first.right + gap, second.y, second.width, second.height)
                        boxes[second_id] = shifted
                        self._beat_geometry[(beat.beat_id, second_id)] = shifted
                    # Try vertical shift within safe canvas bounds
                    elif first.bottom + gap + second.height <= self.canvas_config.height - self.canvas_config.safe_margin_y:
                        shifted = _Box(second.x, first.bottom + gap, second.width, second.height)
                        boxes[second_id] = shifted
                        self._beat_geometry[(beat.beat_id, second_id)] = shifted
                    else:
                        raise WorldCompilerError(
                            f"Root objects '{first_id}' and '{second_id}' "
                            f"overlap while both are active in beat '{beat.beat_id}'."
                        )

    def _compute_shared_root_boxes(
        self,
        roots: list[str],
        region: _Box,
        beat: StoryboardBeat | None = None,
        zone: MacroScreenZone | None = None,
    ) -> dict[str, _Box]:
        if beat is None:
            beat = self._first_beat_for_object(roots[0])
        flow = beat.layout_flow or MicroLayoutFlow()
        flow_type = flow.flow
        if zone in (MacroScreenZone.TOP, MacroScreenZone.BOTTOM) or (
            region.width > region.height * 2.0 and flow_type == ContainerFlow.COLUMN
        ):
            flow_type = ContainerFlow.ROW
        gap = self.token_resolver.resolve_spacing(flow.gap)
        padding = self.token_resolver.resolve_spacing(flow.padding)
        sizes = [self._intrinsic_size(root_id, beat) for root_id in roots]
        inner_w = region.width - 2 * padding
        inner_h = region.height - 2 * padding
        if inner_w <= 0 or inner_h <= 0:
            inner_w = max(10.0, region.width)
            inner_h = max(10.0, region.height)

        result: dict[str, _Box] = {}
        if flow_type == ContainerFlow.ROW:
            required_w = sum(size[0] for size in sizes) + gap * max(0, len(sizes) - 1)
            required_h = max(size[1] for size in sizes)
            if required_w > inner_w + 0.01:
                available_for_items = max(10.0, inner_w - gap * max(0, len(sizes) - 1))
                total_w = sum(size[0] for size in sizes) or 1.0
                sizes = [
                    (size[0] * (available_for_items / total_w), min(size[1], inner_h))
                    for size in sizes
                ]
            current_x = region.x + padding
            for root_id, (width, height) in zip(roots, sizes):
                y = self._cross_axis_position(flow.alignment, region.y + padding, inner_h, height)
                result[root_id] = _Box(current_x, y, width, height)
                current_x += width + gap
        else:
            required_w = max(size[0] for size in sizes)
            required_h = sum(size[1] for size in sizes) + gap * max(0, len(sizes) - 1)
            if required_h > inner_h + 0.01:
                available_for_items = max(10.0, inner_h - gap * max(0, len(sizes) - 1))
                total_h = sum(size[1] for size in sizes) or 1.0
                sizes = [
                    (min(size[0], inner_w), size[1] * (available_for_items / total_h))
                    for size in sizes
                ]
            current_y = region.y + padding
            for root_id, (width, height) in zip(roots, sizes):
                x = self._cross_axis_position(flow.alignment, region.x + padding, inner_w, width)
                result[root_id] = _Box(x, current_y, width, height)
                current_y += height + gap
        return result

    def _layout_shared_roots(self, roots: list[str], region: _Box) -> None:
        beat = self._first_beat_for_object(roots[0])
        shared = self._compute_shared_root_boxes(roots, region)
        for root_id, box in shared.items():
            self._layout_node(root_id, box, beat)

    def _is_fill_parent(self, obj: WorldObjectSpec) -> bool:
        data = obj.semantic_content
        if bool(data.get("fill_parent", False)):
            return True
        layout_role = str(data.get("layout_role", "")).lower()
        if layout_role in {"fill_parent", "background", "surface"}:
            return True
        fill_role = str(data.get("fill_role", "")).lower()
        if fill_role in {"surface", "background", "surface_elevated"}:
            return True
        role = str(data.get("role", "")).lower()
        if role in {"background", "surface"}:
            return True
        if obj.primitive_type == CanonicalCapabilityType.SHAPE:
            obj_lower = obj.object_id.lower()
            if any(term in obj_lower for term in ("surface", "background")):
                return True
        return False

    def _is_overlay(self, obj: WorldObjectSpec) -> bool:
        if obj.primitive_type == CanonicalCapabilityType.CONNECTOR:
            return True
        data = obj.semantic_content
        if bool(data.get("overlay", False)):
            return True
        layout_role = str(data.get("layout_role", "")).lower()
        if layout_role == "overlay":
            return True
        return False

    @staticmethod
    def _cross_axis_position(alignment: FlowAlignment, origin: float, available: float, size: float) -> float:
        if alignment == FlowAlignment.CENTER:
            return origin + (available - size) / 2.0
        if alignment == FlowAlignment.END:
            return origin + available - size
        return origin

    def _is_container(self, obj: WorldObjectSpec) -> bool:
        if obj.primitive_type == CanonicalCapabilityType.GROUP:
            return True
        if obj.component_type:
            desc = VisualComponentRegistry.get_descriptor(obj.component_type)
            return desc.category == ComponentCategory.STRUCTURAL_CONTAINER
        return False

    def _layout_node(self, object_id: str, box: _Box, beat: StoryboardBeat) -> None:
        obj = self._objects[object_id]
        if object_id not in self._geometry:
            self._geometry[object_id] = box
        if not self._is_container(obj):
            return

        all_children = self._children.get(object_id, [])
        active_children = [
            child_id
            for child_id in all_children
            if beat.beat_id in self._objects[child_id].beat_ids
        ]
        if not active_children:
            return

        if obj.component_type == "SurfaceCard":
            padding = 24.0
            gap = 16.0
            card_flow = obj.semantic_content.get("layout_flow", "column")
            flow = MicroLayoutFlow(
                flow=ContainerFlow.ROW if card_flow == "row" else ContainerFlow.COLUMN,
                gap=SemanticSpacing.MD,
                padding=SemanticSpacing.LG,
            )
        else:
            flow = self._flow_for_object(obj, beat)
            gap = self.token_resolver.resolve_spacing(flow.gap)
            padding = self.token_resolver.resolve_spacing(flow.padding)
        inner_w = box.width - 2 * padding
        inner_h = box.height - 2 * padding
        if inner_w <= 0 or inner_h <= 0:
            assert self._world is not None
            raise WorldCompilerError(
                f"Group '{object_id}' in beat '{beat.beat_id}' has no usable content area "
                f"[world={self._world.world_id}, beat={beat.beat_id}, group={object_id}]: "
                f"box=({box.width:.1f}x{box.height:.1f}), padding={padding:.1f}."
            )

        fill_children = [
            child_id
            for child_id in active_children
            if self._is_fill_parent(self._objects[child_id])
        ]
        overlay_children = [
            child_id
            for child_id in active_children
            if self._is_overlay(self._objects[child_id]) and child_id not in fill_children
        ]
        normal_children = [
            child_id
            for child_id in active_children
            if child_id not in fill_children and child_id not in overlay_children
        ]
        raw_sizes = [self._intrinsic_size(child_id, beat) for child_id in normal_children]
        sizes: list[tuple[float, float]] = []
        for child_id, (w, h) in zip(normal_children, raw_sizes):
            child_obj = self._objects[child_id]
            if flow.flow != ContainerFlow.ROW and child_obj.primitive_type == CanonicalCapabilityType.TEXT and w > inner_w:
                lines = math.ceil(w / inner_w)
                sizes.append((inner_w, h * lines))
            else:
                sizes.append((w, h))

        if flow.flow == ContainerFlow.ROW:
            required_w = sum(size[0] for size in sizes) + gap * max(0, len(sizes) - 1)
            required_h = max([size[1] for size in sizes] or [0.0])
            if required_w > inner_w + 0.01 or required_h > inner_h + 0.01:
                assert self._world is not None
                raise WorldCompilerError(
                    f"Group '{object_id}' in beat '{beat.beat_id}' overflows its allocated bounds "
                    f"[world={self._world.world_id}, beat={beat.beat_id}, group={object_id}]: "
                    f"available=({inner_w:.1f}x{inner_h:.1f}), required=({required_w:.1f}x{required_h:.1f}), "
                    f"participating_children={normal_children}."
                )
            current_x = padding
            for child_id, (width, height) in zip(normal_children, sizes):
                if child_id in self._geometry:
                    existing = self._geometry[child_id]
                    if existing.x < current_x:
                        self._geometry[child_id] = _Box(current_x, existing.y, existing.width, existing.height)
                        existing = self._geometry[child_id]
                    current_x = max(current_x, existing.right + gap)
                    child_box = existing
                else:
                    child_y = self._cross_axis_position(flow.alignment, padding, inner_h, height)
                    child_box = _Box(current_x, child_y, width, height)
                    self._geometry[child_id] = child_box
                    current_x += width + gap
                self._layout_node(child_id, child_box, beat)
        elif flow.flow == ContainerFlow.FREE:
            for child_id, (width, height) in zip(normal_children, sizes):
                if child_id in self._geometry:
                    child_box = self._geometry[child_id]
                else:
                    child_box = _Box(padding, padding, width, height)
                    self._geometry[child_id] = child_box
                self._layout_node(child_id, child_box, beat)
        else:
            required_w = max([size[0] for size in sizes] or [0.0])
            required_h = sum(size[1] for size in sizes) + gap * max(0, len(sizes) - 1)
            if required_w > inner_w + 0.01 or required_h > inner_h + 0.01:
                assert self._world is not None
                raise WorldCompilerError(
                    f"Group '{object_id}' in beat '{beat.beat_id}' overflows its allocated bounds "
                    f"[world={self._world.world_id}, beat={beat.beat_id}, group={object_id}]: "
                    f"available=({inner_w:.1f}x{inner_h:.1f}), required=({required_w:.1f}x{required_h:.1f}), "
                    f"participating_children={normal_children}."
                )
            current_y = padding
            for child_id, (width, height) in zip(normal_children, sizes):
                if child_id in self._geometry:
                    existing = self._geometry[child_id]
                    if existing.y < current_y:
                        self._geometry[child_id] = _Box(existing.x, current_y, existing.width, existing.height)
                        existing = self._geometry[child_id]
                    current_y = max(current_y, existing.bottom + gap)
                    child_box = existing
                else:
                    child_x = self._cross_axis_position(flow.alignment, padding, inner_w, width)
                    child_box = _Box(child_x, current_y, width, height)
                    self._geometry[child_id] = child_box
                    current_y += height + gap
                self._layout_node(child_id, child_box, beat)

        for child_id in fill_children:
            fill_box = _Box(0.0, 0.0, box.width, box.height)
            self._geometry[child_id] = fill_box
            self._layout_node(child_id, fill_box, beat)

        for child_id in overlay_children:
            if self._objects[child_id].primitive_type == CanonicalCapabilityType.CONNECTOR:
                if child_id not in self._geometry:
                    self._geometry[child_id] = _Box(0.0, 0.0, 1.0, 1.0)
            else:
                width, height = self._intrinsic_size(child_id, beat)
                if child_id in self._geometry:
                    overlay_box = self._geometry[child_id]
                else:
                    overlay_box = _Box(padding, padding, width, height)
                    self._geometry[child_id] = overlay_box
                self._layout_node(child_id, overlay_box, beat)

    def _flow_for_object(self, obj: WorldObjectSpec, beat: StoryboardBeat) -> MicroLayoutFlow:
        element_layout = beat.element_layouts.get(obj.object_id)

        if element_layout and element_layout.flow is not None:
            return element_layout.flow

        raw_flow = obj.semantic_content.get("layout_flow")

        if raw_flow is None:
            return beat.layout_flow or MicroLayoutFlow()

        try:
            return MicroLayoutFlow.model_validate(raw_flow)
        except Exception as error:
            raise WorldCompilerError(
                f"Invalid layout_flow for group '{obj.object_id}'."
            ) from error

    def _intrinsic_size(self, object_id: str, beat: StoryboardBeat) -> tuple[float, float]:
        obj = self._objects[object_id]
        data = obj.semantic_content
        state = self._state_initials[obj.object_id]

        if obj.component_type:
            props = {**data}
            for k, v in state.items():
                if k in {"display_value", "raw_value", "subtext", "label"}:
                    props[k] = v
                elif k == "value" and "raw_value" not in props:
                    try:
                        props["raw_value"] = float(v)
                    except (ValueError, TypeError):
                        pass

            child_sizes: list[tuple[float, float]] | None = None
            if obj.component_type == "SurfaceCard":
                all_children = self._children.get(object_id, [])
                active_children = [
                    child_id
                    for child_id in all_children
                    if beat.beat_id in self._objects[child_id].beat_ids
                ]
                child_sizes = [self._intrinsic_size(child_id, beat) for child_id in active_children]

            if "width" in data:
                available_width = float(data["width"])
            elif obj.parent_object_id and self._objects[obj.parent_object_id].component_type == "SurfaceCard":
                parent_data = self._objects[obj.parent_object_id].semantic_content
                parent_w = float(parent_data.get("width", 520.0))
                available_width = max(200.0, parent_w - 48.0)
            else:
                try:
                    zone = self._zone_for_object(object_id, beat)
                    available_width = self._zone_rect(zone).width
                except Exception:
                    available_width = 640.0

            return VisualComponentRegistry.measure(
                obj.component_type,
                props=props,
                child_sizes=child_sizes,
                available_width=available_width,
            )

        primitive_type = obj.primitive_type
        if primitive_type == CanonicalCapabilityType.TEXT:
            content = str(state.get("content", data.get("content", obj.object_id)))
            font_size = self._font_size(obj)
            return max(40.0, len(content) * font_size * 0.58), font_size * 1.4
        if primitive_type == CanonicalCapabilityType.NUMBER:
            value = state.get("value", data.get("value", 0))
            prefix = str(state.get("prefix", data.get("prefix", "")) or "")
            suffix = str(state.get("suffix", data.get("suffix", "")) or "")
            font_size = self._font_size(obj)
            return max(60.0, len(f"{prefix}{value}{suffix}") * font_size * 0.62), font_size * 1.2
        if primitive_type == CanonicalCapabilityType.SHAPE:
            if self._is_fill_parent(obj):
                return 1.0, 1.0
            shape_type = str(data.get("shape_type", "rectangle"))
            if shape_type == "circle":
                return 80.0, 80.0
            if shape_type in {"pill", "capsule"}:
                return 160.0, 48.0
            return float(data.get("intrinsic_width", 320.0)), float(data.get("intrinsic_height", 200.0))
        if primitive_type == CanonicalCapabilityType.ICON:
            size = float(data.get("size", 40.0))
            return size, size
        if primitive_type == CanonicalCapabilityType.BAR:
            orientation = str(data.get("orientation", "horizontal"))
            length = float(data.get("max_length", 320.0))
            thickness = float(data.get("thickness", 28.0))
            return (length, thickness) if orientation == "horizontal" else (thickness, length)
        if primitive_type == CanonicalCapabilityType.PROGRESS:
            radius = float(data.get("radius", 64.0))
            return radius * 2, radius * 2
        if primitive_type in {CanonicalCapabilityType.IMAGE, CanonicalCapabilityType.VIDEO}:
            return 480.0, 270.0
        if primitive_type == CanonicalCapabilityType.CONNECTOR:
            return 1.0, 1.0
        if primitive_type == CanonicalCapabilityType.POINT:
            radius = float(data.get("radius", 8.0))
            return radius * 2, radius * 2
        if primitive_type == CanonicalCapabilityType.SEGMENT:
            return 280.0, 24.0
        if primitive_type == CanonicalCapabilityType.LINE:
            return 400.0, 240.0
        if primitive_type == CanonicalCapabilityType.GROUP:
            all_children = self._children.get(object_id, [])
            if not all_children:
                return 200.0, 100.0
            active_flow_children = [
                child_id
                for child_id in all_children
                if beat.beat_id in self._objects[child_id].beat_ids
                and not self._is_fill_parent(self._objects[child_id])
                and not self._is_overlay(self._objects[child_id])
            ]
            flow = self._flow_for_object(obj, beat)
            gap = self.token_resolver.resolve_spacing(flow.gap)
            padding = self.token_resolver.resolve_spacing(flow.padding)
            if not active_flow_children:
                return 2 * padding, 2 * padding
            sizes = [self._intrinsic_size(child_id, beat) for child_id in active_flow_children]
            if flow.flow == ContainerFlow.ROW:
                return (
                    sum(width for width, _ in sizes) + gap * max(0, len(sizes) - 1) + 2 * padding,
                    max(height for _, height in sizes) + 2 * padding,
                )
            if flow.flow == ContainerFlow.FREE:
                return max(width for width, _ in sizes) + 2 * padding, max(height for _, height in sizes) + 2 * padding
            return (
                max(width for width, _ in sizes) + 2 * padding,
                sum(height for _, height in sizes) + gap * max(0, len(sizes) - 1) + 2 * padding,
            )
        return 200.0, 100.0

    def _font_size(self, obj: WorldObjectSpec) -> float:
        intent = self._style_intent(obj)
        typography = self.token_resolver.resolve_typography(intent.typography_role if intent else None)
        return float(obj.semantic_content.get("font_size", typography["font_size"]))

    def _root_box_for_intrinsic(self, object_id: str, region: _Box, intrinsic: tuple[float, float]) -> _Box:
        if self._objects[object_id].primitive_type == CanonicalCapabilityType.GROUP:
            return region
        width, height = intrinsic
        return _Box(region.center_x - width / 2.0, region.center_y - height / 2.0, width, height)

    def _first_beat_for_object(self, object_id: str) -> StoryboardBeat:
        obj = self._objects[object_id]
        if not obj.beat_ids:
            raise WorldCompilerError(f"Object '{object_id}' has no beat membership.")
        return self._beat_resolutions[obj.beat_ids[0]].beat

    def _compute_world_origins(self) -> None:
        def visit(object_id: str, parent_origin: tuple[float, float]) -> None:
            box = self._geometry[object_id]
            origin = (parent_origin[0] + box.x, parent_origin[1] + box.y)
            self._world_origins[object_id] = origin
            for child_id in self._children.get(object_id, []):
                visit(child_id, origin)

        for root_id in self._children.get(None, []):
            visit(root_id, (0.0, 0.0))

    def _resolve_connector_paths(self) -> None:
        for object_id, obj in self._objects.items():
            is_primitive_connector = (obj.primitive_type == CanonicalCapabilityType.CONNECTOR)
            is_flow_connector = (obj.component_type == "FlowConnector")
            if not (is_primitive_connector or is_flow_connector):
                continue
            data = obj.semantic_content
            from_anchor = data.get("from_anchor")
            to_anchor = data.get("to_anchor")

            from_target = None
            from_side = "center"
            to_target = None
            to_side = "center"

            if isinstance(from_anchor, dict):
                from_target = str(from_anchor.get("target_id", ""))
                from_side = str(from_anchor.get("side", "center"))
            elif "source_id" in data:
                from_target = str(data["source_id"])
                from_side = str(data.get("source_side", "auto"))

            if isinstance(to_anchor, dict):
                to_target = str(to_anchor.get("target_id", ""))
                to_side = str(to_anchor.get("side", "center"))
            elif "target_id" in data:
                to_target = str(data["target_id"])
                to_side = str(data.get("target_side", "auto"))

            if not from_target or not to_target:
                raise WorldCompilerError(
                    f"Connector '{object_id}' requires valid source/target or from_anchor/to_anchor intents."
                )
            if from_target not in self._objects or to_target not in self._objects:
                raise WorldCompilerError(f"Connector '{object_id}' references an unknown target object.")

            if from_side == "auto" or to_side == "auto":
                source_world = self._anchor_point(from_target, "center")
                target_world = self._anchor_point(to_target, "center")
                dx = target_world[0] - source_world[0]
                dy = target_world[1] - source_world[1]
                if abs(dx) >= abs(dy):
                    if from_side == "auto":
                        from_side = "right" if dx >= 0 else "left"
                    if to_side == "auto":
                        to_side = "left" if dx >= 0 else "right"
                else:
                    if from_side == "auto":
                        from_side = "bottom" if dy >= 0 else "top"
                    if to_side == "auto":
                        to_side = "top" if dy >= 0 else "bottom"

            from_world = self._anchor_point(from_target, from_side)
            to_world = self._anchor_point(to_target, to_side)
            parent_id = obj.parent_object_id
            common = self._lowest_common_ancestor(from_target, to_target)
            from_common = self._point_in_space(from_world, common)
            to_common = self._point_in_space(to_world, common)
            from_parent = self._convert_between_spaces(from_common, common, parent_id)
            to_parent = self._convert_between_spaces(to_common, common, parent_id)

            routing = str(data.get("routing", "orthogonal_elbow" if is_flow_connector else "straight"))
            points = self._route_points(from_parent, to_parent, routing)
            min_x = min(point[0] for point in points)
            min_y = min(point[1] for point in points)
            max_x = max(point[0] for point in points)
            max_y = max(point[1] for point in points)
            padding = 8.0
            local_box = _Box(
                min_x - padding,
                min_y - padding,
                max(1.0, max_x - min_x + 2 * padding),
                max(1.0, max_y - min_y + 2 * padding),
            )
            self._geometry[object_id] = local_box

            path = ResolvedConnectorPath(
                parent_object_id=parent_id,
                from_point=Point2D(x=from_parent[0], y=from_parent[1]),
                to_point=Point2D(x=to_parent[0], y=to_parent[1]),
                points=[Point2D(x=x, y=y) for x, y in points],
                routing=routing,
            )

            if is_primitive_connector:
                self._compiled_primitives[object_id] = self._compiled_connector_placeholder(
                    object_id,
                    obj,
                    path,
                )
                self._compiled_objects[object_id] = CompiledVisualInstance(
                    object_id=object_id,
                    kind=CompiledObjectKind.PRIMITIVE,
                    primitive_type=CanonicalCapabilityType.CONNECTOR,
                    parent_object_id=parent_id,
                    child_object_ids=[],
                    local_geometry=_local_rect(local_box),
                    style=self._resolve_style(obj),
                    properties={"has_arrow": bool(data.get("has_arrow", True))},
                    connector_path=path,
                )
            else:
                self._compiled_objects[object_id] = CompiledVisualInstance(
                    object_id=object_id,
                    kind=CompiledObjectKind.COMPONENT,
                    component_type="FlowConnector",
                    parent_object_id=parent_id,
                    child_object_ids=[],
                    local_geometry=_local_rect(local_box),
                    style=self._resolve_style(obj),
                    properties={
                        "source_id": from_target,
                        "target_id": to_target,
                        "relationship_type": data.get("relationship_type", "causes"),
                        "routing": routing,
                        "has_arrow": bool(data.get("has_arrow", True)),
                        "label": data.get("label"),
                        "style_intent": data.get("style_intent", "solid"),
                    },
                    connector_path=path,
                )

        self._compute_world_origins()

    def _anchor_point(self, object_id: str, side: str) -> tuple[float, float]:
        box = self._geometry[object_id]
        origin = self._world_origins[object_id]
        world = _Box(origin[0], origin[1], box.width, box.height)
        side = side.lower()
        if side == "left":
            return world.x, world.center_y
        if side == "right":
            return world.right, world.center_y
        if side == "top":
            return world.center_x, world.y
        if side == "bottom":
            return world.center_x, world.bottom
        if side == "center":
            return world.center_x, world.center_y
        raise WorldCompilerError(f"Unsupported connector anchor side '{side}'.")

    def _lowest_common_ancestor(self, first: str, second: str) -> str | None:
        first_ancestors: set[str | None] = set()
        current: str | None = first
        while current is not None:
            first_ancestors.add(current)
            current = self._objects[current].parent_object_id
        current = second
        while current is not None:
            if current in first_ancestors:
                return current
            current = self._objects[current].parent_object_id
        return None

    def _point_in_space(self, world_point: tuple[float, float], space_id: str | None) -> tuple[float, float]:
        if space_id is None:
            return world_point
        origin = self._world_origins[space_id]
        return world_point[0] - origin[0], world_point[1] - origin[1]

    def _convert_between_spaces(
        self,
        point: tuple[float, float],
        from_space: str | None,
        to_space: str | None,
    ) -> tuple[float, float]:
        if from_space == to_space:
            return point
        if from_space is None:
            world_point = point
        else:
            origin = self._world_origins[from_space]
            world_point = point[0] + origin[0], point[1] + origin[1]
        if to_space is None:
            return world_point
        origin = self._world_origins[to_space]
        return world_point[0] - origin[0], world_point[1] - origin[1]

    @staticmethod
    def _route_points(
        first: tuple[float, float], second: tuple[float, float], routing: str
    ) -> list[tuple[float, float]]:
        if routing == "straight":
            return [first, second]
        if routing == "orthogonal_elbow":
            middle_x = first[0] + (second[0] - first[0]) / 2.0
            return [first, (middle_x, first[1]), (middle_x, second[1]), second]
        if routing == "curved":
            middle_x = first[0] + (second[0] - first[0]) / 2.0
            return [first, (middle_x, first[1]), (middle_x, second[1]), second]
        raise WorldCompilerError(f"Unsupported connector routing '{routing}'.")

    def _resolve_primitives(self) -> None:
        for object_id, obj in self._objects.items():
            if obj.primitive_type == CanonicalCapabilityType.CONNECTOR or obj.component_type == "FlowConnector":
                if object_id not in self._compiled_objects:
                    raise WorldCompilerError(f"Connector '{object_id}' has no resolved path.")
                continue
            children = self._children.get(object_id, [])
            style = self._resolve_style(obj)

            if obj.primitive_type:
                if obj.primitive_type == CanonicalCapabilityType.GROUP and _style_is_painted(style):
                    raise WorldCompilerError(
                        f"Group '{object_id}' has painted styles; add an explicit shape child."
                    )
                properties = self._resolve_properties(obj, children)
                registry_properties = properties
                if obj.primitive_type == CanonicalCapabilityType.GROUP:
                    registry_properties = {"child_ids": children}
                elif obj.primitive_type == CanonicalCapabilityType.NUMBER:
                    state = self._state_initials[obj.object_id]
                    raw_value = state.get("value", obj.semantic_content.get("value", 0.0))
                    registry_properties = {
                        **properties,
                        "value": float(raw_value),
                        "start_value": float(state.get("start_value", raw_value)),
                        "prefix": state.get("prefix", obj.semantic_content.get("prefix")),
                        "suffix": state.get("suffix", obj.semantic_content.get("suffix")),
                        "precision": state.get("precision", obj.semantic_content.get("precision")),
                    }
                try:
                    PrimitiveRegistry.validate_primitive_props(obj.primitive_type, registry_properties)
                except Exception as error:
                    raise WorldCompilerError(
                        f"Invalid compiled properties for '{object_id}' ({obj.primitive_type.value})."
                    ) from error

                self._compiled_primitives[object_id] = CompiledPrimitive(
                    object_id=object_id,
                    primitive_type=obj.primitive_type,
                    parent_object_id=obj.parent_object_id,
                    child_object_ids=children,
                    local_geometry=_local_rect(self._geometry[object_id]),
                    style=style,
                    properties=properties,
                )
                self._compiled_objects[object_id] = CompiledVisualInstance(
                    object_id=object_id,
                    kind=CompiledObjectKind.PRIMITIVE,
                    primitive_type=obj.primitive_type,
                    parent_object_id=obj.parent_object_id,
                    child_object_ids=children,
                    local_geometry=_local_rect(self._geometry[object_id]),
                    style=style,
                    properties=properties,
                )
            elif obj.component_type:
                data = obj.semantic_content
                state = self._state_initials[obj.object_id]
                merged_props = {**data}
                for k, v in state.items():
                    if k in {"display_value", "raw_value", "subtext", "label"}:
                        merged_props[k] = v
                    elif k == "value" and "raw_value" not in merged_props:
                        try:
                            merged_props["raw_value"] = float(v)
                        except (ValueError, TypeError):
                            pass

                if obj.component_type == "SurfaceCard":
                    merged_props.setdefault("layout_flow", "column")

                try:
                    validated_props = VisualComponentRegistry.validate_props(obj.component_type, merged_props)
                except Exception as error:
                    raise WorldCompilerError(
                        f"Invalid component props for '{object_id}' ({obj.component_type}): {error}"
                    ) from error

                self._compiled_objects[object_id] = CompiledVisualInstance(
                    object_id=object_id,
                    kind=CompiledObjectKind.COMPONENT,
                    component_type=obj.component_type,
                    parent_object_id=obj.parent_object_id,
                    child_object_ids=children,
                    local_geometry=_local_rect(self._geometry[object_id]),
                    style=style,
                    properties=validated_props.model_dump(),
                )

    def _compiled_connector_placeholder(
        self,
        object_id: str,
        obj: WorldObjectSpec,
        path: ResolvedConnectorPath,
    ) -> CompiledPrimitive:
        data = obj.semantic_content
        stroke_role = self._style_intent(obj).stroke_role if self._style_intent(obj) else None
        stroke = self.token_resolver.resolve_color(stroke_role, "#3b82f6")
        routing = str(data.get("routing", "straight"))
        registry_properties = {
            "from_anchor": {"x": path.from_point.x, "y": path.from_point.y, "side": "center"},
            "to_anchor": {"x": path.to_point.x, "y": path.to_point.y, "side": "center"},
            "routing": routing,
            "has_arrow": bool(data.get("has_arrow", True)),
            "stroke": stroke,
            "stroke_width": float(data.get("stroke_width", 2.0)),
        }
        PrimitiveRegistry.validate_primitive_props(CanonicalCapabilityType.CONNECTOR, registry_properties)
        style = self._resolve_style(obj).model_copy(
            update={
                "stroke": stroke,
                "stroke_width": registry_properties["stroke_width"],
            }
        )
        return CompiledPrimitive(
            object_id=object_id,
            primitive_type=CanonicalCapabilityType.CONNECTOR,
            parent_object_id=obj.parent_object_id,
            child_object_ids=[],
            local_geometry=_local_rect(self._geometry[object_id]),
            style=style,
            properties={"has_arrow": registry_properties["has_arrow"]},
            connector_path=path,
        )

    def _resolve_properties(self, obj: WorldObjectSpec, children: list[str]) -> dict[str, Any]:
        data = obj.semantic_content
        state = self._state_initials[obj.object_id]
        primitive_type = obj.primitive_type
        if primitive_type == CanonicalCapabilityType.GROUP:
            return {}
        if primitive_type == CanonicalCapabilityType.TEXT:
            typography = self.token_resolver.resolve_typography(self._style_intent(obj).typography_role if self._style_intent(obj) else None)
            return {
                "content": str(state.get("content", data.get("content", obj.object_id))),
                "font_size": float(data.get("font_size", typography["font_size"])),
                "font_weight": int(data.get("font_weight", typography["font_weight"])),
                "line_height": float(data.get("line_height", typography["line_height"])),
                "letter_spacing": float(data.get("letter_spacing", typography["letter_spacing"])),
                "align": str(data.get("align", "left")),
                "text_transform": str(data.get("text_transform", typography["text_transform"])),
                "wrap": bool(data.get("wrap", True)),
            }
        if primitive_type == CanonicalCapabilityType.NUMBER:
            typography = self.token_resolver.resolve_typography(self._style_intent(obj).typography_role if self._style_intent(obj) else None)
            raw_value = state.get("value", data.get("value", 0.0))
            try:
                value = float(raw_value)
            except (TypeError, ValueError) as error:
                raise WorldCompilerError(f"Number '{obj.object_id}' requires a numeric initial value.") from error
            return {
                "tabular_nums": True,
                "font_size": float(data.get("font_size", typography["font_size"])),
                "font_weight": int(data.get("font_weight", typography["font_weight"])),
            }
        if primitive_type == CanonicalCapabilityType.SHAPE:
            return {
                "shape_type": str(data.get("shape_type", "rectangle")),
                "corner_radius": data.get("corner_radius", self._resolve_style(obj).corner_radius),
            }
        if primitive_type == CanonicalCapabilityType.ICON:
            return {
                "name": str(data.get("name", "info")),
                "size": float(data.get("size", 32.0)),
                "color": str(data.get("color", "#ffffff")),
                "stroke_width": float(data.get("stroke_width", 2.0)),
            }
        if primitive_type == CanonicalCapabilityType.IMAGE:
            return {"source": str(data.get("source", "")), "object_fit": str(data.get("object_fit", "cover")), "border_radius": 0.0}
        if primitive_type == CanonicalCapabilityType.VIDEO:
            return {"source": str(data.get("source", "")), "loop": True, "muted": True, "playback_rate": 1.0}
        if primitive_type == CanonicalCapabilityType.BAR:
            return {"orientation": str(data.get("orientation", "horizontal")), "fill_percentage": float(data.get("fill_percentage", 1.0)), "max_length": float(data.get("max_length", 320.0)), "thickness": float(data.get("thickness", 28.0)), "corner_radius": 6.0, "foreground_color": "#3b82f6", "background_track_color": "rgba(255, 255, 255, 0.08)"}
        if primitive_type == CanonicalCapabilityType.LINE:
            box = self._geometry.get(obj.object_id, _Box(0.0, 0.0, 320.0, 160.0))
            raw_points = list(data.get("points", []))
            if not raw_points or len(raw_points) < 2:
                w = max(box.width, 60.0)
                h = max(box.height, 40.0)
                trend = str(data.get("trend", "")).lower()
                if any(k in trend for k in ("down", "fall", "drop", "decrease", "negative", "loss")):
                    points = [{"x": 10.0, "y": 10.0}, {"x": w - 10.0, "y": h - 10.0}]
                elif any(k in trend for k in ("flat", "constant", "stable")):
                    points = [{"x": 10.0, "y": h / 2.0}, {"x": w - 10.0, "y": h / 2.0}]
                else:
                    points = [{"x": 10.0, "y": h - 10.0}, {"x": w - 10.0, "y": 10.0}]
            else:
                points = raw_points
            style = self._resolve_style(obj)
            stroke_color = style.stroke or str(data.get("stroke", "#3b82f6"))
            stroke_w = style.stroke_width or float(data.get("stroke_width", 3.0))
            return {
                "points": points,
                "curve_type": str(data.get("curve_type", "linear")),
                "stroke": stroke_color,
                "stroke_width": stroke_w,
                "area_fill": data.get("area_fill"),
            }
        if primitive_type == CanonicalCapabilityType.POINT:
            return {"x": 0.0, "y": 0.0, "radius": float(data.get("radius", 6.0)), "fill": "#3b82f6", "stroke_width": 0.0}
        if primitive_type == CanonicalCapabilityType.SEGMENT:
            return {"parent_track_id": str(data.get("parent_track_id", "")), "start_ratio": float(data.get("start_ratio", 0.0)), "length_ratio": float(data.get("length_ratio", 1.0)), "fill": "#3b82f6"}
        if primitive_type == CanonicalCapabilityType.PROGRESS:
            return {"variant": str(data.get("variant", "radial_ring")), "progress_ratio": float(data.get("progress_ratio", 0.5)), "radius": float(data.get("radius", 60.0)), "stroke_width": 8.0, "track_color": "rgba(255,255,255,0.1)", "fill_color": "#3b82f6"}
        raise WorldCompilerError(f"Unsupported primitive type '{primitive_type}'.")

    def _style_intent(self, obj: WorldObjectSpec) -> SemanticStyleIntent | None:
        raw = obj.semantic_content.get("style_intent")
        if raw is None:
            return None
        try:
            return SemanticStyleIntent.model_validate(raw)
        except Exception as error:
            raise WorldCompilerError(f"Invalid style_intent for '{obj.object_id}'.") from error

    def _resolve_style(self, obj: WorldObjectSpec) -> PrimitiveStyle:
        style = self.token_resolver.resolve_style(self._style_intent(obj))
        if obj.primitive_type in {CanonicalCapabilityType.TEXT, CanonicalCapabilityType.NUMBER}:
            intent = self._style_intent(obj)
            if intent and intent.text_color_role:
                style.fill = self.token_resolver.resolve_color(intent.text_color_role)
        return style

    def _compile_lifecycle_tracks(self) -> list[CompiledLifecycleTrack]:
        assert self._world is not None
        tracks: list[CompiledLifecycleTrack] = []
        for obj in self._world.objects:
            introduced_beat = obj.lifecycle.introduced_in_beat or obj.beat_ids[0]
            introduced_frame = self._beat_resolutions[introduced_beat].start_frame
            exit_frame: int | None = None
            if obj.lifecycle.mode == "beat_local":
                exit_frame = self._beat_resolutions[introduced_beat].end_frame
            elif obj.lifecycle.mode == "until_exit":
                event = self._all_state_events[obj.lifecycle.exit_event_id or ""]
                exit_frame = self._event_frame(event)
            elif obj.lifecycle.mode == "persistent":
                last_beat = obj.beat_ids[-1]
                if last_beat != self._world.beats[-1].beat_id:
                    exit_frame = self._beat_resolutions[last_beat].end_frame
            tracks.append(
                CompiledLifecycleTrack(
                    object_id=obj.object_id,
                    introduced_frame=introduced_frame,
                    exit_frame=exit_frame,
                    mode=obj.lifecycle.mode,
                )
            )
        return tracks

    def _compile_visibility_intervals(
        self, lifecycle_tracks: list[CompiledLifecycleTrack]
    ) -> list[CompiledVisibilityInterval]:
        """Compile visibility as explicit half-open intervals.

        ENTER/APPEAR actions mean hidden-before-enter.  EXIT actions and
        visibility state events close an interval at their resolved global
        frame.  No renderer inference is needed from animation behavior.
        """
        assert self._world is not None
        lifecycle_by_object = {track.object_id: track for track in lifecycle_tracks}
        intervals: list[CompiledVisibilityInterval] = []

        for obj in self._world.objects:
            lifecycle = lifecycle_by_object[obj.object_id]
            start = lifecycle.introduced_frame
            end = (
                lifecycle.exit_frame
                if lifecycle.exit_frame is not None
                else self._total_duration_frames
            )
            if end <= start:
                continue

            visibility_events: list[tuple[int, bool, str]] = []
            for beat in self._world.beats:
                for action in beat.actions:
                    if action.target_node_id != obj.object_id:
                        continue
                    frame = self._resolved_anchors[
                        f"action:{beat.beat_id}:{action.action_id}"
                    ].global_frame
                    if action.action_type in {VisualActionType.ENTER, VisualActionType.APPEAR, VisualActionType.HOLD}:
                        visibility_events.append((frame, True, action.action_id))
                    elif action.action_type == VisualActionType.EXIT:
                        visibility_events.append((frame, False, action.action_id))
            for event in self._all_state_events.values():
                if event.object_id != obj.object_id or event.kind != StateChangeKind.VISIBILITY:
                    continue
                visibility_events.append((self._event_frame(event), bool(event.visible), event.event_id))

            visibility_events.sort(key=lambda item: (item[0], item[2]))
            initially_visible = bool(self._state_initials[obj.object_id].get("visible", True))
            if visibility_events and visibility_events[0][1] and visibility_events[0][0] > start:
                initially_visible = False

            current_visible = initially_visible
            cursor = start
            for frame, visible, _event_id in visibility_events:
                if frame <= start:
                    current_visible = visible
                    continue
                if frame >= end:
                    break
                if current_visible and frame > cursor:
                    intervals.append(
                        CompiledVisibilityInterval(
                            object_id=obj.object_id,
                            start_frame=cursor,
                            end_frame=frame,
                        )
                    )
                current_visible = visible
                cursor = frame
            if current_visible and end > cursor:
                intervals.append(
                    CompiledVisibilityInterval(
                        object_id=obj.object_id,
                        start_frame=cursor,
                        end_frame=end,
                    )
                )

        return intervals

    def _compile_terminal_hold(self) -> CompiledTerminalHold | None:
        if not self._beat_resolutions:
            return None
        last_end = max(resolution.end_frame for resolution in self._beat_resolutions.values())
        if last_end >= self._total_duration_frames:
            return None
        return CompiledTerminalHold(start_frame=last_end, end_frame=self._total_duration_frames)

    def _compile_state_and_animation_tracks(
        self,
    ) -> tuple[list[CompiledStateTrack], list[CompiledAnimationTrack]]:
        assert self._world is not None
        events_by_object: dict[str, list[StateChangeEvent]] = {object_id: [] for object_id in self._objects}
        for event in self._all_state_events.values():
            events_by_object[event.object_id].append(event)
        beat_order = {beat.beat_id: index for index, beat in enumerate(self._world.beats)}
        state_tracks: list[CompiledStateTrack] = []
        animations: list[CompiledAnimationTrack] = []
        current_layout_boxes = dict(self._geometry)

        for obj in self._world.objects:
            obj_events = events_by_object[obj.object_id]
            obj_actions: list[tuple[StoryboardBeat, VisualAction]] = []
            for beat in self._world.beats:
                for action in beat.actions:
                    if action.target_node_id == obj.object_id and action.action_type != VisualActionType.HOLD:
                        obj_actions.append((beat, action))

            # Interleave events and actions in chronological order so state & layout continuity are preserved
            operations: list[tuple[int, int, int, int, str, Any]] = []
            for event in obj_events:
                frame = self._event_frame(event)
                b_idx = beat_order[event.beat_id]
                operations.append((frame, b_idx, 0, 0, "event", event))
            for beat, action in obj_actions:
                anchor_id = f"action:{beat.beat_id}:{action.action_id}"
                anchor = self._resolved_anchors[anchor_id]
                b_idx = beat_order[beat.beat_id]
                operations.append((anchor.global_frame, b_idx, 1, getattr(action, "order", 0), "action", (beat, action)))

            operations.sort(key=lambda op: (op[0], op[1], op[2], op[3]))

            changes: list[CompiledStateChange] = []
            current_state = dict(self._state_initials[obj.object_id])
            if "layout" not in current_state and obj.object_id in current_layout_boxes:
                current_state["layout"] = _local_rect(current_layout_boxes[obj.object_id]).model_dump()

            for op in operations:
                op_type = op[4]
                if op_type == "event":
                    event: StateChangeEvent = op[5]
                    frame = self._event_frame(event)
                    target_property = self._target_property(event)

                    if event.kind == StateChangeKind.LAYOUT:
                        from_box = current_layout_boxes[obj.object_id]
                        to_box = self._resolve_layout_event_geometry(event)

                        from_value = _local_rect(from_box).model_dump()
                        to_value = _local_rect(to_box).model_dump()

                        current_layout_boxes[obj.object_id] = to_box
                    else:
                        from_value, to_value = self._state_change_values(
                            event,
                            obj.object_id,
                            target_property,
                            current_state,
                            current_layout_boxes,
                        )
                    changes.append(
                        CompiledStateChange(
                            event_id=event.event_id,
                            object_id=event.object_id,
                            beat_id=event.beat_id,
                            global_frame=frame,
                            kind=event.kind.value,
                            target_property=target_property,
                            from_value=from_value,
                            to_value=to_value,
                            visible=event.visible,
                        )
                    )
                    event_duration = self._state_duration(event.kind)
                    event_trigger = min(frame, max(0, self._total_duration_frames - 1))
                    avail_event_frames = max(1, self._total_duration_frames - event_trigger)
                    event_duration = min(event_duration, avail_event_frames)
                    st_easing = "spring" if event.kind in {StateChangeKind.VALUE, StateChangeKind.LAYOUT} else "ease-out"
                    st_spring = SpringConfig(damping=15.0, stiffness=100.0, mass=1.0) if st_easing == "spring" else None
                    animations.append(
                        CompiledAnimationTrack(
                            animation_id=event.event_id,
                            object_id=event.object_id,
                            trigger_frame=event_trigger,
                            duration_frames=max(1, event_duration),
                            easing=st_easing,
                            spring_config=st_spring,
                            motion_preset="reveal",
                            behavior=event.kind.value,
                            target_property=target_property,
                            from_value=from_value,
                            to_value=to_value,
                        )
                    )
                    if to_value is not None:
                        _set_state_value(current_state, target_property, to_value)
                        if target_property == "layout" or (isinstance(to_value, dict) and "x" in to_value and "y" in to_value):
                            b = _box_from_dict(to_value)
                            if b is not None:
                                current_layout_boxes[obj.object_id] = b

                elif op_type == "action":
                    beat, action = op[5]
                    anchor_id = f"action:{beat.beat_id}:{action.action_id}"
                    anchor = self._resolved_anchors[anchor_id]
                    target_property = action.target_property or self._action_property(action.action_type)
                    if target_property in {"number_value", "numeric_value"}:
                        target_property = "value"

                    if target_property == "layout":
                        from_box = current_layout_boxes[obj.object_id]
                        from_value = _local_rect(from_box).model_dump()
                        if action.new_value is not None:
                            if isinstance(action.new_value, dict) and "x" in action.new_value and "y" in action.new_value:
                                to_value = action.new_value
                                b = _box_from_dict(to_value)
                                if b is not None:
                                    current_layout_boxes[obj.object_id] = b
                            elif isinstance(action.new_value, str):
                                try:
                                    zone = MacroScreenZone(action.new_value)
                                    region = self._zone_rect(zone)
                                    intrinsic = self._intrinsic_size(obj.object_id, beat)
                                    to_box = self._root_box_for_intrinsic(obj.object_id, region, intrinsic)
                                    to_value = _local_rect(to_box).model_dump()
                                    current_layout_boxes[obj.object_id] = to_box
                                except Exception:
                                    to_value = action.new_value
                            else:
                                to_value = action.new_value
                        else:
                            to_value = self._action_to_value(action.action_type)
                    else:
                        from_value = self._action_from_value(
                            obj.object_id,
                            target_property,
                            action.action_type,
                            current_state,
                            current_layout_boxes,
                        )
                        to_value = (
                            action.new_value
                            if action.new_value is not None
                            else self._action_to_value(action.action_type)
                        )

                    preset_duration, easing, spring_cfg, preset_name = self._action_preset_config(
                        action.action_type, getattr(action, "motion_preset", None)
                    )
                    action_trigger = min(anchor.global_frame, max(0, self._total_duration_frames - 1))
                    avail_action_frames = max(1, self._total_duration_frames - action_trigger)
                    action_duration = min(preset_duration, avail_action_frames) if preset_duration > 0 else 1
                    animations.append(
                        CompiledAnimationTrack(
                            animation_id=action.action_id,
                            object_id=obj.object_id,
                            trigger_frame=action_trigger,
                            duration_frames=max(1, action_duration),
                            easing=easing,
                            spring_config=spring_cfg,
                            motion_preset=preset_name,
                            behavior=action.action_type.value,
                            target_property=target_property,
                            from_value=from_value,
                            to_value=to_value,
                        )
                    )
                    if to_value is not None:
                        _set_state_value(current_state, target_property, to_value)
                        if target_property == "layout" or (isinstance(to_value, dict) and "x" in to_value and "y" in to_value):
                            b = _box_from_dict(to_value)
                            if b is not None:
                                current_layout_boxes[obj.object_id] = b

            state_tracks.append(
                CompiledStateTrack(
                    object_id=obj.object_id,
                    initial_state=dict(self._state_initials[obj.object_id]),
                    changes=changes,
                )
            )
        return state_tracks, animations

    def _state_change_values(
        self,
        event: StateChangeEvent,
        object_id: str,
        target_property: str,
        current_state: dict[str, Any],
        current_layout_boxes: dict[str, _Box] | None = None,
    ) -> tuple[Any, Any]:
        from_value = event.from_value
        if from_value is None:
            from_value = _get_state_value(current_state, target_property)
        if from_value is None:
            from_value = self._derived_initial_value(
                object_id, target_property, current_layout_boxes
            )
        if from_value is None:
            raise WorldCompilerError(
                f"State event '{event.event_id}' has no resolvable from_value for "
                f"'{object_id}.{target_property}'."
            )
        to_value = event.to_value
        if event.kind == StateChangeKind.VISIBILITY:
            return from_value, bool(event.visible)
        if event.kind == StateChangeKind.STYLE and event.style_intent is not None:
            return from_value, self.token_resolver.resolve_style(event.style_intent).model_dump()
        if event.kind == StateChangeKind.LAYOUT and event.layout_intent is not None:
            target = self._resolve_layout_event_geometry(event)
            boxes = current_layout_boxes if current_layout_boxes is not None else self._geometry
            current_box = boxes.get(event.object_id, self._geometry[event.object_id])
            return (
                _local_rect(current_box).model_dump(),
                _local_rect(target).model_dump(),
            )
        if event.kind == StateChangeKind.RELATIONSHIP and event.relationship is not None:
            return from_value, event.relationship.model_dump()
        if to_value is None:
            raise WorldCompilerError(
                f"State event '{event.event_id}' has no compiler-resolved to_value."
            )
        return from_value, to_value

    @staticmethod
    def _target_property(event: StateChangeEvent) -> str:
        if event.target_property:
            if event.target_property in {"number_value", "numeric_value"}:
                return "value"
            return event.target_property
        return {
            StateChangeKind.VALUE: "value",
            StateChangeKind.VISIBILITY: "visible",
            StateChangeKind.STYLE: "style",
            StateChangeKind.LAYOUT: "layout",
            StateChangeKind.RELATIONSHIP: "relationship",
        }[event.kind]

    def _derived_initial_value(
        self,
        object_id: str,
        target_property: str,
        current_layout_boxes: dict[str, _Box] | None = None,
    ) -> Any | None:
        if target_property == "visible":
            return bool(self._state_initials[object_id].get("visible", True))
        inst = self._compiled_objects.get(object_id) or self._compiled_primitives.get(object_id)
        if target_property == "style":
            return inst.style.model_dump() if inst else {}
        if target_property == "layout":
            boxes = current_layout_boxes if current_layout_boxes is not None else self._geometry
            box = boxes.get(object_id, self._geometry[object_id])
            return _local_rect(box).model_dump()
        if target_property == "opacity":
            return inst.style.opacity if inst else 1.0
        if target_property.startswith("style."):
            sub = target_property.split(".", 1)[1]
            return (getattr(inst.style, sub, None) if inst else None) or "transparent"
        if target_property == "scale":
            return 1.0
        if target_property == "transform":
            return "none"
        return None

    def _action_from_value(
        self,
        object_id: str,
        target_property: str,
        action_type: VisualActionType,
        current_state: dict[str, Any] | None = None,
        current_layout_boxes: dict[str, _Box] | None = None,
    ) -> Any:
        if action_type in {VisualActionType.ENTER, VisualActionType.APPEAR} and target_property == "opacity":
            return 0.0
        if action_type in {VisualActionType.EXIT, VisualActionType.HOLD} and target_property == "opacity":
            return 1.0
        value = None
        if current_state is not None:
            value = _get_state_value(current_state, target_property)
        if value is None:
            value = _get_state_value(self._state_initials[object_id], target_property)
        if value is None:
            value = self._derived_initial_value(
                object_id, target_property, current_layout_boxes
            )
        if value is None:
            raise WorldCompilerError(
                f"Action for '{object_id}' has no compiler-resolved from_value for "
                f"'{target_property}'."
            )
        return value

    @staticmethod
    def _action_to_value(action_type: VisualActionType) -> Any:
        if action_type in {VisualActionType.ENTER, VisualActionType.APPEAR, VisualActionType.HIGHLIGHT, VisualActionType.HOLD}:
            return 1.0
        if action_type == VisualActionType.EXIT:
            return 0.0
        return 1.0

    def _resolve_layout_event_geometry(self, event: StateChangeEvent) -> _Box:
        """Resolve a semantic layout event into a concrete destination box."""
        assert event.layout_intent is not None
        obj = self._objects[event.object_id]

        if obj.parent_object_id is not None:
            raise WorldCompilerError(
                f"Layout event '{event.event_id}' targets nested object '{event.object_id}'. "
                "Nested parent-local layout transitions are not yet supported."
            )

        if event.layout_intent.macro_zone is None:
            raise WorldCompilerError(
                f"Layout event '{event.event_id}' requires a resolvable macro zone."
            )

        # Macro-zone is the concrete placement authority for now.
        # ``relative_to_object_id`` / ``anchor`` remain semantic metadata until
        # a dedicated relative-placement compiler is introduced. They must not
        # make an otherwise resolvable macro-zone transition fail compilation.
        region = self._zone_rect(event.layout_intent.macro_zone)
        beat = self._beat_resolutions[event.beat_id].beat
        intrinsic = self._intrinsic_size(event.object_id, beat)
        return self._root_box_for_intrinsic(event.object_id, region, intrinsic)

    def _event_frame(self, event: StateChangeEvent) -> int:
        if event.speech_anchor is not None:
            anchor = self._resolved_anchors.get(event.speech_anchor.anchor_id)
            if anchor is None:
                raise WorldCompilerError(
                    f"State event '{event.event_id}' references an unresolved speech anchor."
                )
            return anchor.global_frame
        return self._beat_resolutions[event.beat_id].start_frame

    @staticmethod
    def _state_duration(kind: StateChangeKind) -> int:
        return {StateChangeKind.VISIBILITY: 1, StateChangeKind.RELATIONSHIP: 15}.get(kind, 20)

    @staticmethod
    def _action_preset_config(
        action_type: VisualActionType,
        preset: MotionPreset | str | None,
    ) -> tuple[int, str, SpringConfig | None, str]:
        """Returns (duration_frames, easing, spring_config, motion_preset_name)."""
        if action_type == VisualActionType.HOLD:
            return 1, "linear", None, "hold"
        if action_type == VisualActionType.PULSE:
            return 15, "spring", SpringConfig(damping=12.0, stiffness=140.0, mass=1.0), "impact"

        p_str = preset.value if hasattr(preset, "value") else str(preset or "reveal").strip().lower()
        if p_str == MotionPreset.IMPACT.value:
            return 15, "spring", SpringConfig(damping=12.0, stiffness=140.0, mass=1.0), "impact"
        elif p_str == MotionPreset.SETTLE.value:
            return 22, "spring", SpringConfig(damping=18.0, stiffness=90.0, mass=1.0), "settle"
        elif p_str == MotionPreset.GENTLE.value:
            return 30, "ease-out", None, "gentle"
        else:  # REVEAL / default
            return 20, "spring", SpringConfig(damping=15.0, stiffness=100.0, mass=1.0), "reveal"

    @staticmethod
    def _action_duration(action_type: VisualActionType) -> int:
        return {
            VisualActionType.APPEAR: 20,
            VisualActionType.ENTER: 20,
            VisualActionType.EXIT: 20,
            VisualActionType.HIGHLIGHT: 20,
            VisualActionType.TRANSFORM: 20,
            VisualActionType.UPDATE_VALUE: 20,
            VisualActionType.PULSE: 15,
            VisualActionType.HOLD: 0,
        }[action_type]

    @staticmethod
    def _action_property(action_type: VisualActionType) -> str:
        if action_type in {VisualActionType.APPEAR, VisualActionType.ENTER, VisualActionType.EXIT, VisualActionType.HOLD}:
            return "opacity"
        if action_type == VisualActionType.HIGHLIGHT:
            return "style.stroke"
        if action_type == VisualActionType.PULSE:
            return "scale"
        if action_type == VisualActionType.UPDATE_VALUE:
            return "value"
        return "transform"

    def _compile_transition_events(self) -> list[CompiledTransitionEvent]:
        assert self._world is not None
        events: list[CompiledTransitionEvent] = []
        for index, beat in enumerate(self._world.beats):
            if index == 0 or beat.transition_intent is None:
                continue
            previous = self._world.beats[index - 1]
            events.append(
                CompiledTransitionEvent(
                    event_id=f"transition:{previous.beat_id}:{beat.beat_id}",
                    from_beat_id=previous.beat_id,
                    to_beat_id=beat.beat_id,
                    global_frame=self._beat_resolutions[beat.beat_id].start_frame,
                    kind=beat.transition_intent.kind,
                    preserve_object_ids=list(beat.transition_intent.preserve_object_ids),
                )
            )
        return events

    def _lineage(self, world: VisualWorldSpec) -> list[SourceReference]:
        seen: set[tuple[str, str]] = set()
        lineage: list[SourceReference] = []
        for beat in world.beats:
            refs = list(beat.source_references)
            refs.extend(
                SourceReference(kind="visual_intent", reference_id=intent_id)
                for intent_id in beat.source_intent_ids
            )
            for reference in refs:
                key = (reference.kind, reference.reference_id)
                if key not in seen:
                    lineage.append(reference)
                    seen.add(key)
        return lineage


def _clean_word(token: str) -> str:
    return re.sub(r"[^\w₹$%]", "", token.strip()).lower()


def _local_rect(box: _Box) -> LocalRect:
    return LocalRect(x=round(box.x, 2), y=round(box.y, 2), width=round(box.width, 2), height=round(box.height, 2))


def _box_from_dict(val: Any) -> _Box | None:
    if isinstance(val, dict) and "x" in val and "y" in val and "width" in val and "height" in val:
        return _Box(float(val["x"]), float(val["y"]), float(val["width"]), float(val["height"]))
    return None


def _boxes_overlap(first: _Box, second: _Box) -> bool:
    return first.x < second.right and first.right > second.x and first.y < second.bottom and first.bottom > second.y


def _get_state_value(state: dict[str, Any], target_property: str) -> Any | None:
    """Read a simple or dotted state property without renderer inference."""
    current: Any = state
    for part in target_property.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def _set_state_value(state: dict[str, Any], target_property: str, value: Any) -> None:
    parts = target_property.split(".")
    current = state
    for part in parts[:-1]:
        nested = current.setdefault(part, {})
        if not isinstance(nested, dict):
            raise WorldCompilerError(
                f"Cannot resolve nested state property '{target_property}'."
            )
        current = nested
    current[parts[-1]] = value


def _style_is_painted(style: PrimitiveStyle) -> bool:
    return style.fill is not None or style.stroke is not None or style.corner_radius is not None or style.shadow is not None
