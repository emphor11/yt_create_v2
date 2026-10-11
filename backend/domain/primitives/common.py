from __future__ import annotations

from enum import Enum
from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field


class CanonicalCapabilityType(str, Enum):
    TEXT = "text"
    NUMBER = "number"
    SHAPE = "shape"
    ICON = "icon"
    CONNECTOR = "connector"
    IMAGE = "image"
    VIDEO = "video"
    BAR = "bar"
    LINE = "line"
    POINT = "point"
    SEGMENT = "segment"
    PROGRESS = "progress"
    GROUP = "group"


CANONICAL_CAPABILITY_TYPES: list[str] = [c.value for c in CanonicalCapabilityType]

FORBIDDEN_COMPOSITION_TYPES: frozenset[str] = frozenset({
    "card", "kpi", "kpigrid", "comparison", "splitcomparison",
    "calculation", "calculationstory", "timeline", "waterfall",
    "cashflowwaterfall", "hero", "metrichero", "causaldiagram",
    "causeeffect", "brollcaption", "growthtrajectory", "timedecay",
    "multifactorpressure", "rankedlist", "progressivelist", "datatable",
    "beforeafter", "quotecallout"
})


class PrimitiveIdentity(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., description="Unique primitive ID within the scene tree")
    type: CanonicalCapabilityType = Field(..., description="Canonical primitive type")
    parent_id: str | None = Field(default=None, description="Parent group ID or None if root")
    z_index: int = Field(default=0, ge=0, description="Stacking order in coordinate space")


class MarginPadding(BaseModel):
    model_config = ConfigDict(extra="forbid")

    top: float | None = 0
    right: float | None = 0
    bottom: float | None = 0
    left: float | None = 0


class PrimitiveLayout(BaseModel):
    model_config = ConfigDict(extra="forbid")

    position_mode: Literal["absolute", "relative", "flex_item"] = "relative"
    x: float | None = Field(default=None, description="X coordinate (px or normalized)")
    y: float | None = Field(default=None, description="Y coordinate (px or normalized)")
    width: float | str | None = Field(default=None, description="Width (px, 'auto', '100%')")
    height: float | str | None = Field(default=None, description="Height (px, 'auto', '100%')")
    anchor_origin: Literal["top-left", "center", "bottom-center", "top-right"] | None = "top-left"
    margin: MarginPadding | None = None
    padding: MarginPadding | None = None


class BoxShadow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    color: str = "rgba(0, 0, 0, 0.4)"
    blur: float = 12
    x: float = 0
    y: float = 4


class PrimitiveStyle(BaseModel):
    model_config = ConfigDict(extra="forbid")

    fill: str | None = Field(default=None, description="Fill background / surface color")
    stroke: str | None = Field(default=None, description="Border / stroke color")
    stroke_width: float | None = Field(default=None, ge=0, description="Stroke width in px")
    stroke_style: Literal["solid", "dashed", "dotted"] | None = "solid"
    corner_radius: float | list[float] | None = Field(default=None, description="Border radius in px")
    opacity: float | None = Field(default=1.0, ge=0.0, le=1.0, description="Alpha opacity")
    shadow: BoxShadow | None = None
    blur_backdrop: float | None = Field(default=None, ge=0, description="Backdrop filter blur in px")
    blend_mode: Literal["normal", "multiply", "screen", "overlay"] | None = "normal"


class PrimitiveTiming(BaseModel):
    model_config = ConfigDict(extra="forbid")

    enter_frame: int = Field(default=0, ge=0, description="Frame index where primitive enters")
    exit_frame: int | None = Field(default=None, ge=0, description="Frame index where primitive exits")
    visible: bool = Field(default=True, description="Master visibility toggle")


class SpringConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    damping: float = 14
    stiffness: float = 100
    mass: float = 1.0


class PrimitiveAnimation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action_id: str = Field(..., description="Unique action identifier")
    trigger_frame: int = Field(..., ge=0, description="Frame index when animation triggers")
    duration_frames: int = Field(default=30, gt=0, description="Transition duration in frames")
    easing: Literal["spring", "ease-out", "linear", "bezier"] = "spring"
    spring_config: SpringConfig | None = None
    behavior: str = Field(..., description="Visual behavior name (e.g. appear, transform, highlight)")
    target_property: str = Field(..., description="Target property path to animate (e.g. value, style.fill)")
    from_value: Any | None = Field(default=None, description="Initial value before transition")
    to_value: Any = Field(..., description="Target value after transition")
