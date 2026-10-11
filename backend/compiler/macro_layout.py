"""Deterministic Macro Layout Resolver.

Resolves the Scene Storyboarder's semantic macro screen zones into exact 2D canvas bounding regions.
The Storyboarder never calculates geometry; the compiler owns all actual coordinates, dimensions,
margins, and safe-area boundaries.
"""
from __future__ import annotations

from compiler.models import CanvasConfig, Rect, VisualCompilerError
from domain.storyboard import MacroScreenZone


class MacroLayoutResolver:
    """Calculates deterministic canvas regions for all 14 canonical macro screen zones."""

    @classmethod
    def resolve_zone(cls, zone: MacroScreenZone | str, canvas_config: CanvasConfig) -> Rect:
        """Returns the bounding Rect for the specified macro zone."""
        zone_str = zone.value if hasattr(zone, "value") else str(zone).strip().lower()

        safe = canvas_config.safe_rect
        sx = safe.x
        sy = safe.y
        sw = safe.width
        sh = safe.height

        if zone_str == MacroScreenZone.CENTER.value:
            # Centered focal region (70% width, 80% height, centered)
            w = round(sw * 0.70, 2)
            h = round(sh * 0.80, 2)
            x = round(sx + (sw - w) / 2.0, 2)
            y = round(sy + (sh - h) / 2.0, 2)
            return Rect(x=x, y=y, width=w, height=h)

        elif zone_str == MacroScreenZone.LEFT.value:
            # Left half of safe canvas
            w = round(sw * 0.48, 2)
            h = round(sh, 2)
            x = round(sx, 2)
            y = round(sy, 2)
            return Rect(x=x, y=y, width=w, height=h)

        elif zone_str == MacroScreenZone.RIGHT.value:
            # Right half of safe canvas
            w = round(sw * 0.48, 2)
            h = round(sh, 2)
            x = round(sx + sw - w, 2)
            y = round(sy, 2)
            return Rect(x=x, y=y, width=w, height=h)

        elif zone_str == MacroScreenZone.TOP.value:
            # Top headline banner
            w = round(sw, 2)
            h = round(sh * 0.25, 2)
            x = round(sx, 2)
            y = round(sy, 2)
            return Rect(x=x, y=y, width=w, height=h)

        elif zone_str == MacroScreenZone.BOTTOM.value:
            # Bottom ticker or consequence bar
            w = round(sw, 2)
            h = round(sh * 0.28, 2)
            x = round(sx, 2)
            y = round(sy + sh - h, 2)
            return Rect(x=x, y=y, width=w, height=h)

        elif zone_str == MacroScreenZone.SPLIT_LEFT.value:
            # Left side of balanced 50/50 comparison
            w = round(sw * 0.47, 2)
            h = round(sh * 0.65, 2)
            x = round(sx, 2)
            y = round(sy + sh * 0.05, 2)
            return Rect(x=x, y=y, width=w, height=h)

        elif zone_str == MacroScreenZone.SPLIT_RIGHT.value:
            # Right side of balanced 50/50 comparison
            w = round(sw * 0.47, 2)
            h = round(sh * 0.65, 2)
            x = round(sx + sw - w, 2)
            y = round(sy + sh * 0.05, 2)
            return Rect(x=x, y=y, width=w, height=h)

        elif zone_str == MacroScreenZone.SPLIT_TOP.value:
            # Top half of vertical split
            w = round(sw, 2)
            h = round(sh * 0.46, 2)
            x = round(sx, 2)
            y = round(sy, 2)
            return Rect(x=x, y=y, width=w, height=h)

        elif zone_str == MacroScreenZone.SPLIT_BOTTOM.value:
            # Bottom half of vertical split
            w = round(sw, 2)
            h = round(sh * 0.46, 2)
            x = round(sx, 2)
            y = round(sy + sh - h, 2)
            return Rect(x=x, y=y, width=w, height=h)

        elif zone_str == MacroScreenZone.TOP_LEFT.value:
            w = round(sw * 0.45, 2)
            h = round(sh * 0.45, 2)
            return Rect(x=sx, y=sy, width=w, height=h)

        elif zone_str == MacroScreenZone.TOP_RIGHT.value:
            w = round(sw * 0.45, 2)
            h = round(sh * 0.45, 2)
            return Rect(x=round(sx + sw - w, 2), y=sy, width=w, height=h)

        elif zone_str == MacroScreenZone.BOTTOM_LEFT.value:
            w = round(sw * 0.45, 2)
            h = round(sh * 0.45, 2)
            return Rect(x=sx, y=round(sy + sh - h, 2), width=w, height=h)

        elif zone_str == MacroScreenZone.BOTTOM_RIGHT.value:
            w = round(sw * 0.45, 2)
            h = round(sh * 0.45, 2)
            return Rect(x=round(sx + sw - w, 2), y=round(sy + sh - h, 2), width=w, height=h)

        elif zone_str == MacroScreenZone.FULL_SCREEN.value:
            return canvas_config.full_rect

        else:
            valid_zones = [z.value for z in MacroScreenZone]
            raise VisualCompilerError(
                f"Unknown macro screen zone '{zone}'. Must be one of: {valid_zones}"
            )
