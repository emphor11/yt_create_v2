"""Deterministic Action and Animation Compiler.

Compiles semantic Storyboarder visual actions (appear, enter, transform, update_value, highlight, pulse, exit)
into concrete PrimitiveAnimation specifications with deterministic durations and spring dynamics.
"""
from __future__ import annotations

from typing import Any
from compiler.models import VisualCompilerError
from compiler.timing_resolver import ResolvedTrigger
from compiler.token_resolver import TokenResolver
from domain.primitives.common import PrimitiveAnimation, SpringConfig
from domain.primitives.spec import PrimitiveSpec
from domain.storyboard import MotionPreset, VisualAction, VisualActionType


class ActionCompiler:
    """Compiles high-level VisualAction definitions into primitive animations and timing."""

    def __init__(self, token_resolver: TokenResolver | None = None):
        self.token_resolver = token_resolver or TokenResolver()

    def get_preset_config(self, preset: MotionPreset | str | None) -> tuple[int, str, SpringConfig | None]:
        """Returns (duration_frames, easing, spring_config) for a motion preset."""
        p_str = preset.value if hasattr(preset, "value") else str(preset or "reveal").strip().lower()

        if p_str == MotionPreset.IMPACT.value:
            return 15, "spring", SpringConfig(damping=12.0, stiffness=140.0, mass=1.0)
        elif p_str == MotionPreset.SETTLE.value:
            return 22, "spring", SpringConfig(damping=18.0, stiffness=90.0, mass=1.0)
        elif p_str == MotionPreset.GENTLE.value:
            return 30, "ease-out", None
        else:  # REVEAL / default
            return 20, "spring", SpringConfig(damping=15.0, stiffness=100.0, mass=1.0)

    def compile_action(
        self,
        scene_id: str,
        action: VisualAction,
        target_prim: PrimitiveSpec,
        resolved_trigger: ResolvedTrigger,
    ) -> PrimitiveAnimation:
        """Translates a VisualAction into a PrimitiveAnimation attached to the target primitive."""
        act_type = action.action_type.value if hasattr(action.action_type, "value") else str(action.action_type).strip().lower()
        duration_frames, easing, spring_cfg = self.get_preset_config(action.motion_preset)
        trigger_frame = resolved_trigger.trigger_frame

        if act_type in (VisualActionType.APPEAR.value, VisualActionType.ENTER.value):
            target_prim.timing.enter_frame = trigger_frame
            target_prim.timing.visible = True
            
            # If new_value is supplied on number appear (e.g. initial count-up)
            if action.new_value is not None and "value" in target_prim.props:
                target_prim.props["value"] = float(action.new_value)
                target_prim.current_state["current_value"] = float(action.new_value)

            return PrimitiveAnimation(
                action_id=action.action_id,
                trigger_frame=trigger_frame,
                duration_frames=duration_frames,
                easing=easing,
                spring_config=spring_cfg,
                behavior="appear",
                target_property="opacity",
                from_value=0.0,
                to_value=1.0,
            )

        elif act_type == VisualActionType.UPDATE_VALUE.value:
            if action.new_value is None:
                raise VisualCompilerError(
                    f"Action '{action.action_id}' of type 'update_value' requires an explicit 'new_value'."
                )
            
            old_val = target_prim.props.get("value", target_prim.current_state.get("current_value", 0.0))
            new_val = float(action.new_value)
            target_prim.current_state["current_value"] = new_val
            target_prim.current_state["delta"] = f"{new_val - float(old_val):+}"

            return PrimitiveAnimation(
                action_id=action.action_id,
                trigger_frame=trigger_frame,
                duration_frames=duration_frames,
                easing=easing,
                spring_config=spring_cfg,
                behavior="update_value",
                target_property=action.target_property or "value",
                from_value=old_val,
                to_value=new_val,
            )

        elif act_type == VisualActionType.HIGHLIGHT.value:
            highlight_color = (
                self.token_resolver.resolve_color(action.new_value)
                if action.new_value
                else self.token_resolver.resolve_color("accent")
            )
            old_stroke = target_prim.style.stroke or "rgba(255, 255, 255, 0.0)"
            target_prim.style.stroke = highlight_color
            target_prim.style.stroke_width = max(2.0, target_prim.style.stroke_width or 2.0)

            return PrimitiveAnimation(
                action_id=action.action_id,
                trigger_frame=trigger_frame,
                duration_frames=duration_frames,
                easing=easing,
                spring_config=spring_cfg,
                behavior="highlight",
                target_property=action.target_property or "style.stroke",
                from_value=old_stroke,
                to_value=highlight_color,
            )

        elif act_type == VisualActionType.TRANSFORM.value:
            if action.new_value is None and not action.target_property:
                raise VisualCompilerError(
                    f"Action '{action.action_id}' of type 'transform' requires target_property or new_value."
                )

            prop = action.target_property or "scale"
            to_val = action.new_value if action.new_value is not None else 1.1

            return PrimitiveAnimation(
                action_id=action.action_id,
                trigger_frame=trigger_frame,
                duration_frames=duration_frames,
                easing=easing,
                spring_config=spring_cfg,
                behavior="transform",
                target_property=prop,
                from_value=1.0 if prop == "scale" else None,
                to_value=to_val,
            )

        elif act_type == VisualActionType.PULSE.value:
            return PrimitiveAnimation(
                action_id=action.action_id,
                trigger_frame=trigger_frame,
                duration_frames=duration_frames,
                easing=easing,
                spring_config=spring_cfg,
                behavior="pulse",
                target_property=action.target_property or "scale",
                from_value=1.0,
                to_value=1.15,
            )

        elif act_type == VisualActionType.EXIT.value:
            target_prim.timing.exit_frame = trigger_frame + duration_frames
            return PrimitiveAnimation(
                action_id=action.action_id,
                trigger_frame=trigger_frame,
                duration_frames=duration_frames,
                easing=easing,
                spring_config=spring_cfg,
                behavior="exit",
                target_property="opacity",
                from_value=1.0,
                to_value=0.0,
            )

        elif act_type == VisualActionType.HOLD.value:
            target_prim.timing.visible = True
            return PrimitiveAnimation(
                action_id=action.action_id,
                trigger_frame=trigger_frame,
                duration_frames=0,
                easing="linear",
                spring_config=spring_cfg,
                behavior="hold",
                target_property="opacity",
                from_value=1.0,
                to_value=1.0,
            )

        else:
            raise VisualCompilerError(
                f"Unsupported visual action type '{action.action_type}' in action '{action.action_id}'."
            )
