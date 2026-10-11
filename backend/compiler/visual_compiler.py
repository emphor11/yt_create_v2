"""Isolated Deterministic Visual Compiler.

Compiles a ProjectStoryboardSpec and authoritative VoiceTrack into validated PrimitiveTreeSpecs.
Transforms high-level semantic storyboard structures, macro zones, micro auto-layout containers,
design tokens, and spoken trigger words into exact Remotion primitive trees and spring animations.
"""
from __future__ import annotations

from typing import Any
from compiler.action_compiler import ActionCompiler
from compiler.connector_resolver import ConnectorResolver
from compiler.macro_layout import MacroLayoutResolver
from compiler.micro_layout import MicroLayoutEngine
from compiler.models import (
    CanvasConfig,
    CompiledProjectResult,
    CompiledSceneResult,
    Rect,
    VisualCompilerError,
)
from compiler.persistence_manager import PersistenceManager
from compiler.timing_resolver import TimingResolver
from compiler.token_resolver import TokenResolver
from domain.primitives.common import (
    CANONICAL_CAPABILITY_TYPES,
    FORBIDDEN_COMPOSITION_TYPES,
    CanonicalCapabilityType,
    PrimitiveIdentity,
    PrimitiveLayout,
    PrimitiveStyle,
    PrimitiveTiming,
)
from domain.primitives.spec import PrimitiveSpec, PrimitiveTreeSpec
from domain.storyboard import (
    MacroScreenZone,
    MicroLayoutFlow,
    ProjectStoryboardSpec,
    SceneStoryboardSpec,
    StoryboardNode,
    VisualAction,
    VisualActionType,
)
from domain.voice_track import VoiceTrack
from registries.primitive_registry import PrimitiveRegistry


class VisualCompiler:
    """Deterministic visual compiler for declarative storyboard trees."""

    def __init__(
        self,
        canvas_config: CanvasConfig | None = None,
        token_resolver: TokenResolver | None = None,
    ) -> None:
        self.canvas_config = canvas_config or CanvasConfig()
        self.token_resolver = token_resolver or TokenResolver()
        self.macro_resolver = MacroLayoutResolver()
        self.micro_layout_engine = MicroLayoutEngine(self.token_resolver)
        self.action_compiler = ActionCompiler(self.token_resolver)

    def _collect_and_validate_nodes(
        self,
        scene_id: str,
        root_nodes: list[StoryboardNode],
    ) -> tuple[dict[str, StoryboardNode], dict[str, str | None], dict[str, list[str]]]:
        """Flattens and validates storyboard nodes in the scene.

        Returns:
            all_nodes: dict[node_id, StoryboardNode]
            parent_ids: dict[node_id, parent_node_id | None]
            children_ids: dict[group_node_id, list[child_node_id]]
        """
        all_nodes: dict[str, StoryboardNode] = {}
        parent_ids: dict[str, str | None] = {}
        children_ids: dict[str, list[str]] = {}

        def traverse(node: StoryboardNode, parent_id: str | None) -> None:
            nid = node.id
            if nid in all_nodes:
                raise VisualCompilerError(
                    f"Duplicate primitive ID '{nid}' found in scene '{scene_id}'."
                )

            # Validate capability type
            ntype_str = node.type.value if hasattr(node.type, "value") else str(node.type)
            clean_ntype = ntype_str.lower().replace("_", "").replace("-", "")
            if (
                ntype_str in FORBIDDEN_COMPOSITION_TYPES
                or clean_ntype in FORBIDDEN_COMPOSITION_TYPES
                or any(f in clean_ntype for f in FORBIDDEN_COMPOSITION_TYPES)
            ):
                raise VisualCompilerError(
                    f"Disallowed composition type '{ntype_str}' in node '{nid}'. "
                    "All high-level components must be assembled from canonical primitives."
                )
            if ntype_str not in CANONICAL_CAPABILITY_TYPES:
                raise VisualCompilerError(
                    f"Unknown capability type '{ntype_str}' in node '{nid}'. "
                    f"Must be one of: {sorted(CANONICAL_CAPABILITY_TYPES)}"
                )

            all_nodes[nid] = node
            parent_ids[nid] = parent_id

            if ntype_str == CanonicalCapabilityType.GROUP.value:
                child_list: list[str] = []
                for child in node.children:
                    child_list.append(child.id)
                    traverse(child, parent_id=nid)
                children_ids[nid] = child_list
            elif node.children:
                raise VisualCompilerError(
                    f"Non-group primitive '{nid}' of type '{ntype_str}' cannot contain children."
                )

        for root in root_nodes:
            traverse(root, parent_id=None)

        return all_nodes, parent_ids, children_ids

    def _normalize_primitive_props(
        self,
        node: StoryboardNode,
        style: PrimitiveStyle,
        child_ids: list[str],
    ) -> dict[str, Any]:
        """Normalizes and extracts canonical properties for Remotion primitives."""
        ntype = node.type.value if hasattr(node.type, "value") else str(node.type)
        props = node.props

        if ntype == CanonicalCapabilityType.TEXT.value:
            typo = self.token_resolver.resolve_typography(node.style.typography_role)
            return {
                "content": str(props.get("content", node.name or "")),
                "font_size": float(props.get("font_size", typo["font_size"])),
                "font_weight": int(props.get("font_weight", typo["font_weight"])),
                "line_height": float(props.get("line_height", typo["line_height"])),
                "letter_spacing": float(props.get("letter_spacing", typo["letter_spacing"])),
                "align": str(props.get("align", "left")),
                "text_transform": str(props.get("text_transform", typo["text_transform"])),
                "wrap": bool(props.get("wrap", True)),
                "highlight_spans": list(props.get("highlight_spans", [])),
            }

        elif ntype == CanonicalCapabilityType.NUMBER.value:
            typo = self.token_resolver.resolve_typography(node.style.typography_role)
            raw_val = props.get("value", 0.0)
            try:
                val = float(raw_val)
            except (ValueError, TypeError):
                val = 0.0

            raw_start = props.get("start_value", 0.0)
            try:
                start_val = float(raw_start)
            except (ValueError, TypeError):
                start_val = 0.0

            precision = props.get("precision")
            if precision is not None:
                precision = int(precision)

            return {
                "value": val,
                "start_value": start_val,
                "prefix": props.get("prefix"),
                "suffix": props.get("suffix"),
                "precision": precision,
                "tabular_nums": bool(props.get("tabular_nums", True)),
                "font_size": float(props.get("font_size", typo["font_size"])),
                "font_weight": int(props.get("font_weight", typo["font_weight"])),
            }

        elif ntype == CanonicalCapabilityType.SHAPE.value:
            return {
                "shape_type": str(props.get("shape_type", "rectangle")),
                "corner_radius": props.get("corner_radius", style.corner_radius),
            }

        elif ntype == CanonicalCapabilityType.ICON.value:
            icon_color = (
                self.token_resolver.resolve_color(node.style.text_color_role)
                or style.fill
                or style.stroke
                or "#ffffff"
            )
            return {
                "name": str(props.get("name", "info")),
                "size": float(props.get("size", 32.0)),
                "color": str(props.get("color", icon_color)),
                "stroke_width": float(props.get("stroke_width", 2.0)),
            }

        elif ntype == CanonicalCapabilityType.CONNECTOR.value:
            from_a = dict(props.get("from_anchor", {}))
            to_a = dict(props.get("to_anchor", {}))
            stroke_col = (
                self.token_resolver.resolve_color(node.style.stroke_role)
                or props.get("stroke")
                or "#3b82f6"
            )
            return {
                "from_anchor": from_a,
                "to_anchor": to_a,
                "routing": str(props.get("routing", "curved")),
                "has_arrow": bool(props.get("has_arrow", True)),
                "stroke": str(stroke_col),
                "stroke_width": float(props.get("stroke_width", 2.0)),
                "stroke_dasharray": props.get("stroke_dasharray"),
                "label": props.get("label"),
            }

        elif ntype == CanonicalCapabilityType.GROUP.value:
            flow_spec = node.flow or MicroLayoutFlow()
            flow_val = flow_spec.flow.value if hasattr(flow_spec.flow, "value") else str(flow_spec.flow)
            align_val = flow_spec.alignment.value if hasattr(flow_spec.alignment, "value") else str(flow_spec.alignment)
            justify_val = flow_spec.justification.value if hasattr(flow_spec.justification, "value") else str(flow_spec.justification)

            flow_map = {"row": "row", "column": "column", "free": "none"}
            align_map = {"start": "flex-start", "center": "center", "end": "flex-end", "stretch": "stretch"}
            justify_map = {"start": "flex-start", "center": "center", "end": "flex-end", "space_between": "space-between"}

            return {
                "child_ids": child_ids,
                "layout_flow": flow_map.get(flow_val, "none"),
                "gap": self.token_resolver.resolve_spacing(flow_spec.gap),
                "align_items": align_map.get(align_val, "flex-start"),
                "justify_content": justify_map.get(justify_val, "flex-start"),
            }

        elif ntype == CanonicalCapabilityType.IMAGE.value:
            return {
                "source": str(props.get("source", "")),
                "object_fit": str(props.get("object_fit", "cover")),
                "border_radius": float(props.get("border_radius", style.corner_radius or 0.0)),
            }

        elif ntype == CanonicalCapabilityType.VIDEO.value:
            return {
                "source": str(props.get("source", "")),
                "loop": bool(props.get("loop", True)),
                "muted": bool(props.get("muted", True)),
                "playback_rate": float(props.get("playback_rate", 1.0)),
                "loop_duration_frames": props.get("loop_duration_frames"),
            }

        elif ntype == CanonicalCapabilityType.BAR.value:
            fg_color = (
                self.token_resolver.resolve_color(node.style.fill_role)
                or props.get("foreground_color")
                or "#3b82f6"
            )
            return {
                "orientation": str(props.get("orientation", "horizontal")),
                "fill_percentage": float(props.get("fill_percentage", 1.0)),
                "max_length": float(props.get("max_length", 300.0)),
                "thickness": float(props.get("thickness", 24.0)),
                "corner_radius": float(props.get("corner_radius", 6.0)),
                "foreground_color": str(fg_color),
                "background_track_color": props.get("background_track_color", "rgba(255, 255, 255, 0.08)"),
            }

        elif ntype == CanonicalCapabilityType.LINE.value:
            stroke_col = (
                self.token_resolver.resolve_color(node.style.stroke_role)
                or props.get("stroke")
                or "#3b82f6"
            )
            return {
                "points": list(props.get("points", [])),
                "curve_type": str(props.get("curve_type", "monotone_cubic")),
                "stroke": str(stroke_col),
                "stroke_width": float(props.get("stroke_width", 3.0)),
                "area_fill": props.get("area_fill"),
            }

        elif ntype == CanonicalCapabilityType.POINT.value:
            fill_col = (
                self.token_resolver.resolve_color(node.style.fill_role)
                or props.get("fill")
                or "#3b82f6"
            )
            return {
                "x": float(props.get("x", 0.0)),
                "y": float(props.get("y", 0.0)),
                "radius": float(props.get("radius", 6.0)),
                "fill": str(fill_col),
                "stroke": props.get("stroke"),
                "stroke_width": float(props.get("stroke_width", 0.0)),
                "label": props.get("label"),
            }

        elif ntype == CanonicalCapabilityType.SEGMENT.value:
            fill_col = (
                self.token_resolver.resolve_color(node.style.fill_role)
                or props.get("fill")
                or "#3b82f6"
            )
            return {
                "parent_track_id": str(props.get("parent_track_id", "")),
                "start_ratio": float(props.get("start_ratio", 0.0)),
                "length_ratio": float(props.get("length_ratio", 1.0)),
                "fill": str(fill_col),
                "label": props.get("label"),
            }

        elif ntype == CanonicalCapabilityType.PROGRESS.value:
            fill_col = (
                self.token_resolver.resolve_color(node.style.fill_role)
                or props.get("fill_color")
                or "#3b82f6"
            )
            return {
                "variant": str(props.get("variant", "radial_ring")),
                "progress_ratio": float(props.get("progress_ratio", 0.5)),
                "radius": float(props.get("radius", 60.0)),
                "stroke_width": float(props.get("stroke_width", 8.0)),
                "track_color": str(props.get("track_color", "rgba(255, 255, 255, 0.1)")),
                "fill_color": str(fill_col),
                "center_label": props.get("center_label"),
            }

        return dict(props)

    def compile_scene(
        self,
        scene: SceneStoryboardSpec,
        voice_track: VoiceTrack,
        persistence_manager: PersistenceManager | None = None,
        scene_start_ms: int = 0,
        scene_end_ms: int | None = None,
        relative_timing: bool = True,
    ) -> CompiledSceneResult:
        """Deterministically compiles a single SceneStoryboardSpec into a PrimitiveTreeSpec."""
        p_mgr = persistence_manager or PersistenceManager()
        timing_resolver = TimingResolver(voice_track, fps=self.canvas_config.fps)

        narration = getattr(scene, "narration", None) or getattr(scene, "scene_narration", "")
        root_nodes = getattr(scene, "root_nodes", None) or getattr(scene, "nodes", [])

        # 1. Determine scene duration
        if scene_end_ms is None:
            calc_start, calc_end, _ = timing_resolver.resolve_scene_time_span(
                scene.scene_id, narration, 0
            )
            scene_start_ms = calc_start
            scene_end_ms = calc_end

        duration_ms = max(100, scene_end_ms - scene_start_ms)
        duration_frames = max(1, round(duration_ms / 1000.0 * self.canvas_config.fps))
        duration_seconds = round(duration_frames / self.canvas_config.fps, 2)

        # 2. Collect, validate, and index all nodes
        all_nodes, parent_ids, children_ids = self._collect_and_validate_nodes(
            scene.scene_id, root_nodes
        )

        # 3. Macro and Micro Layout Resolution
        resolved_layouts: dict[str, PrimitiveLayout] = {}
        scene_zone = getattr(scene, "macro_zone", MacroScreenZone.CENTER)
        for root in root_nodes:
            zone = root.macro_zone or scene_zone or MacroScreenZone.CENTER
            allocated_bounds = self.macro_resolver.resolve_zone(zone, self.canvas_config)
            node_layouts = self.micro_layout_engine.layout_node_tree(root, allocated_bounds)
            resolved_layouts.update(node_layouts)

        # 4. Construct initial PrimitiveSpecs
        primitives: dict[str, PrimitiveSpec] = {}
        node_persistence_keys: dict[str, str] = {}

        for nid, node in all_nodes.items():
            cap_type = CanonicalCapabilityType(
                node.type.value if hasattr(node.type, "value") else str(node.type)
            )

            # Style resolution
            style = self.token_resolver.resolve_style(node.style)
            # Text and number color mapping
            if cap_type in (CanonicalCapabilityType.TEXT, CanonicalCapabilityType.NUMBER):
                if node.style.text_color_role:
                    style.fill = self.token_resolver.resolve_color(node.style.text_color_role)
                elif node.style.fill_role:
                    style.fill = self.token_resolver.resolve_color(node.style.fill_role)
                else:
                    style.fill = style.fill or "#f4f4f5"

            # Layout resolution fallback if not captured
            layout = resolved_layouts.get(
                nid,
                PrimitiveLayout(
                    position_mode="relative" if parent_ids[nid] else "absolute",
                    x=self.canvas_config.safe_margin_x,
                    y=self.canvas_config.safe_margin_y,
                    width=200.0,
                    height=100.0,
                ),
            )

            # Props normalization
            child_list = children_ids.get(nid, [])
            normalized_props = self._normalize_primitive_props(node, style, child_list)

            # Persistence tracking
            initial_state: dict[str, Any] = {}
            if cap_type == CanonicalCapabilityType.NUMBER:
                initial_state["current_value"] = normalized_props.get("value", 0.0)

            pkey = p_mgr.register_node(scene.scene_id, node, initial_state)
            if pkey:
                node_persistence_keys[nid] = pkey

            # Default timing
            is_established = p_mgr.is_established(pkey, scene.scene_id) if pkey else False
            timing = PrimitiveTiming(
                enter_frame=0,
                exit_frame=None,
                visible=True,
            )

            try:
                prim_spec = PrimitiveSpec(
                    identity=PrimitiveIdentity(
                        id=nid,
                        type=cap_type,
                        parent_id=parent_ids[nid],
                        z_index=0,
                    ),
                    layout=layout,
                    style=style,
                    timing=timing,
                    props=normalized_props,
                    current_state=initial_state,
                    animations=[],
                )
            except Exception as e:
                raise VisualCompilerError(
                    f"Failed to create primitive '{nid}' of type '{cap_type}': {e}"
                ) from e

            primitives[nid] = prim_spec

        # 5. Connector Anchor Resolution
        ConnectorResolver.resolve_connectors(scene.scene_id, primitives)

        # 6. Action and Timing Compilation
        for action in scene.actions:
            target_nid = action.target_node_id
            if target_nid not in primitives:
                raise VisualCompilerError(
                    f"Visual action '{action.action_id}' targets non-existent primitive '{target_nid}' "
                    f"in scene '{scene.scene_id}'."
                )

            target_prim = primitives[target_nid]
            target_node = all_nodes[target_nid]

            # Check cross-scene persistence suppression
            if p_mgr.should_suppress_entrance(target_node, scene.scene_id):
                act_type = action.action_type.value if hasattr(action.action_type, "value") else str(action.action_type)
                if act_type in (VisualActionType.APPEAR.value, VisualActionType.ENTER.value):
                    # Suppress appearance action on established persistent object
                    continue

            # Resolve spoken trigger word
            ref_start_ms = scene_start_ms if relative_timing else 0
            resolved_trigger = timing_resolver.resolve_trigger(
                scene_id=scene.scene_id,
                scene_narration=narration,
                trigger_word=action.trigger_word,
                trigger_occurrence=action.trigger_occurrence,
                scene_start_ms=ref_start_ms,
            )

            # Compile into PrimitiveAnimation
            anim = self.action_compiler.compile_action(
                scene_id=scene.scene_id,
                action=action,
                target_prim=target_prim,
                resolved_trigger=resolved_trigger,
            )
            target_prim.animations.append(anim)

        # 7. Construct and validate final PrimitiveTreeSpec
        root_ids = [node.id for node in root_nodes]
        try:
            tree_spec = PrimitiveTreeSpec(
                scene_id=scene.scene_id,
                duration_frames=duration_frames,
                root_primitive_ids=root_ids,
                primitives=primitives,
            )
        except Exception as e:
            raise VisualCompilerError(
                f"Validation error in PrimitiveTreeSpec for scene '{scene.scene_id}': {e}"
            ) from e

        return CompiledSceneResult(
            scene_id=scene.scene_id,
            duration_frames=duration_frames,
            duration_seconds=duration_seconds,
            tree_spec=tree_spec,
            relationships=list(scene.relationships),
            persistent_keys=node_persistence_keys,
        )

    def compile(
        self,
        storyboard: ProjectStoryboardSpec,
        voice_track: VoiceTrack,
        relative_timing: bool = True,
    ) -> CompiledProjectResult:
        """Deterministically compiles an entire ProjectStoryboardSpec against a VoiceTrack."""
        persistence_mgr = PersistenceManager()
        timing_resolver = TimingResolver(voice_track, fps=self.canvas_config.fps)

        compiled_scenes: list[CompiledSceneResult] = []
        scene_trees: dict[str, PrimitiveTreeSpec] = {}
        search_offset = 0

        for scene in storyboard.scenes:
            # Resolve time span for this scene
            narration = getattr(scene, "narration", None) or getattr(scene, "scene_narration", "")
            s_start, s_end, next_offset = timing_resolver.resolve_scene_time_span(
                scene.scene_id, narration, search_offset
            )
            search_offset = next_offset

            compiled_scene = self.compile_scene(
                scene=scene,
                voice_track=voice_track,
                persistence_manager=persistence_mgr,
                scene_start_ms=s_start,
                scene_end_ms=s_end,
                relative_timing=relative_timing,
            )
            compiled_scenes.append(compiled_scene)
            scene_trees[scene.scene_id] = compiled_scene.tree_spec

        total_frames = sum(s.duration_frames for s in compiled_scenes)
        total_seconds = round(total_frames / self.canvas_config.fps, 2)

        return CompiledProjectResult(
            canvas_config=self.canvas_config,
            scenes=compiled_scenes,
            scene_trees=scene_trees,
            total_duration_frames=total_frames,
            total_duration_seconds=total_seconds,
        )
