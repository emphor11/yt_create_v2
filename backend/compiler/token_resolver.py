"""Deterministic Semantic Design-Token Resolver.

Translates high-level semantic design tokens (colors, typography, radius, elevation, spacing)
into exact pixel, hex, and CSS-compatible values for Remotion primitives.
The compiler/design system owns all actual values; the Storyboarder never invents arbitrary styling.
"""
from __future__ import annotations

from typing import Any
from domain.primitives.common import BoxShadow, PrimitiveStyle
from domain.storyboard import (
    SemanticColorRole,
    SemanticElevationRole,
    SemanticRadiusRole,
    SemanticSpacing,
    SemanticStyleIntent,
    SemanticTypographyRole,
)


class TokenResolver:
    """Central deterministic resolver for all semantic visual tokens."""

    COLOR_MAP: dict[str, str] = {
        SemanticColorRole.SURFACE.value: "#18181b",
        SemanticColorRole.SURFACE_ELEVATED.value: "#27272a",
        SemanticColorRole.BORDER.value: "#3f3f46",
        SemanticColorRole.PRIMARY_TEXT.value: "#f4f4f5",
        SemanticColorRole.SECONDARY_TEXT.value: "#a1a1aa",
        SemanticColorRole.MUTED.value: "#71717a",
        SemanticColorRole.ACCENT.value: "#3b82f6",
        SemanticColorRole.WARNING.value: "#f59e0b",
        SemanticColorRole.SUCCESS.value: "#10b981",
        SemanticColorRole.DANGER.value: "#ef4444",
        SemanticColorRole.INFO.value: "#06b6d4",
    }

    TYPOGRAPHY_MAP: dict[str, dict[str, Any]] = {
        SemanticTypographyRole.DISPLAY.value: {
            "font_size": 96.0,
            "font_weight": 800,
            "line_height": 1.1,
            "letter_spacing": -1.0,
            "text_transform": "none",
        },
        SemanticTypographyRole.HEADLINE.value: {
            "font_size": 56.0,
            "font_weight": 700,
            "line_height": 1.2,
            "letter_spacing": -0.5,
            "text_transform": "none",
        },
        SemanticTypographyRole.SUBHEADLINE.value: {
            "font_size": 36.0,
            "font_weight": 600,
            "line_height": 1.25,
            "letter_spacing": 0.0,
            "text_transform": "none",
        },
        SemanticTypographyRole.BODY.value: {
            "font_size": 28.0,
            "font_weight": 400,
            "line_height": 1.4,
            "letter_spacing": 0.0,
            "text_transform": "none",
        },
        SemanticTypographyRole.CAPTION.value: {
            "font_size": 20.0,
            "font_weight": 500,
            "line_height": 1.3,
            "letter_spacing": 0.0,
            "text_transform": "none",
        },
        SemanticTypographyRole.EYEBROW.value: {
            "font_size": 18.0,
            "font_weight": 700,
            "line_height": 1.2,
            "letter_spacing": 1.5,
            "text_transform": "uppercase",
        },
    }

    RADIUS_MAP: dict[str, float] = {
        SemanticRadiusRole.NONE.value: 0.0,
        SemanticRadiusRole.SM.value: 6.0,
        SemanticRadiusRole.CARD.value: 16.0,
        SemanticRadiusRole.CHIP.value: 24.0,
        SemanticRadiusRole.PILL.value: 9999.0,
    }

    ELEVATION_MAP: dict[str, BoxShadow | None] = {
        SemanticElevationRole.NONE.value: None,
        SemanticElevationRole.SUBTLE.value: BoxShadow(color="rgba(0, 0, 0, 0.2)", blur=8.0, x=0.0, y=2.0),
        SemanticElevationRole.CARD.value: BoxShadow(color="rgba(0, 0, 0, 0.4)", blur=16.0, x=0.0, y=6.0),
        SemanticElevationRole.GLOW.value: BoxShadow(color="rgba(59, 130, 246, 0.35)", blur=24.0, x=0.0, y=0.0),
    }

    SPACING_MAP: dict[str, float] = {
        SemanticSpacing.NONE.value: 0.0,
        SemanticSpacing.XS.value: 8.0,
        SemanticSpacing.SM.value: 16.0,
        SemanticSpacing.MD.value: 24.0,
        SemanticSpacing.LG.value: 32.0,
        SemanticSpacing.XL.value: 48.0,
    }

    def resolve_color(self, role: SemanticColorRole | str | None, default: str | None = None) -> str | None:
        """Resolves a semantic color role into an authoritative hex string."""
        if role is None:
            return default
        role_str = role.value if hasattr(role, "value") else str(role).strip().lower()
        return self.COLOR_MAP.get(role_str, default or role_str)

    def resolve_typography(self, role: SemanticTypographyRole | str | None) -> dict[str, Any]:
        """Resolves a semantic typography role into font sizes, weights, and letter-spacing."""
        if role is None:
            return self.TYPOGRAPHY_MAP[SemanticTypographyRole.BODY.value]
        role_str = role.value if hasattr(role, "value") else str(role).strip().lower()
        return self.TYPOGRAPHY_MAP.get(role_str, self.TYPOGRAPHY_MAP[SemanticTypographyRole.BODY.value])

    def resolve_radius(self, role: SemanticRadiusRole | str | None) -> float:
        """Resolves a semantic radius role into pixels."""
        if role is None:
            return 0.0
        role_str = role.value if hasattr(role, "value") else str(role).strip().lower()
        return self.RADIUS_MAP.get(role_str, 0.0)

    def resolve_elevation(self, role: SemanticElevationRole | str | None) -> BoxShadow | None:
        """Resolves a semantic elevation role into a BoxShadow specification."""
        if role is None:
            return None
        role_str = role.value if hasattr(role, "value") else str(role).strip().lower()
        return self.ELEVATION_MAP.get(role_str, None)

    def resolve_spacing(self, spacing: SemanticSpacing | str | None, default: float = 0.0) -> float:
        """Resolves a semantic spacing token into pixel padding or gap."""
        if spacing is None:
            return default
        spacing_str = spacing.value if hasattr(spacing, "value") else str(spacing).strip().lower()
        return self.SPACING_MAP.get(spacing_str, default)

    def resolve_style(self, style_intent: SemanticStyleIntent | None) -> PrimitiveStyle:
        """Compiles a high-level SemanticStyleIntent into an exact PrimitiveStyle."""
        if style_intent is None:
            return PrimitiveStyle()

        fill_color = self.resolve_color(style_intent.fill_role)
        stroke_color = self.resolve_color(style_intent.stroke_role)
        stroke_width = 2.0 if stroke_color else None
        corner_radius = self.resolve_radius(style_intent.radius_role)
        shadow = self.resolve_elevation(style_intent.elevation_role)
        opacity = style_intent.opacity if style_intent.opacity is not None else 1.0

        return PrimitiveStyle(
            fill=fill_color,
            stroke=stroke_color,
            stroke_width=stroke_width,
            corner_radius=corner_radius,
            opacity=opacity,
            shadow=shadow,
        )
