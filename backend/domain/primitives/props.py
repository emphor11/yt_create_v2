from __future__ import annotations

from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field


# -----------------------------------------------------------------------------
# 1. Text
# -----------------------------------------------------------------------------
class TextHighlightSpan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    word: str
    color: str | None = None
    background: str | None = None


class TextProps(BaseModel):
    model_config = ConfigDict(extra="forbid")

    content: str
    font_size: float = 32
    font_weight: int = 500
    line_height: float = 1.3
    letter_spacing: float = 0
    align: Literal["left", "center", "right"] = "left"
    text_transform: Literal["none", "uppercase", "lowercase", "capitalize"] = "none"
    wrap: bool = True
    highlight_spans: list[TextHighlightSpan] = Field(default_factory=list)


class TextState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    content: str | None = None
    active_highlights: list[str] = Field(default_factory=list)


# -----------------------------------------------------------------------------
# 2. Number
# -----------------------------------------------------------------------------
class NumberProps(BaseModel):
    model_config = ConfigDict(extra="forbid")

    value: float
    start_value: float = 0
    prefix: str | None = None
    suffix: str | None = None
    precision: int | None = None
    tabular_nums: bool = True
    font_size: float = 48
    font_weight: int = 700


class NumberState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    current_value: float | None = None
    delta: str | None = None


# -----------------------------------------------------------------------------
# 3. Shape
# -----------------------------------------------------------------------------
class ShapeProps(BaseModel):
    model_config = ConfigDict(extra="forbid")

    shape_type: Literal["rectangle", "circle", "pill", "capsule"] = "rectangle"
    corner_radius: float | list[float] | None = None


class ShapeState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scale: float | None = 1.0
    fill: str | None = None
    stroke: str | None = None
    elevation: int | None = 0


# -----------------------------------------------------------------------------
# 4. Icon
# -----------------------------------------------------------------------------
class IconProps(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    size: float = 32
    color: str = "#ffffff"
    stroke_width: float = 2.0


class IconState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = None
    color: str | None = None
    bloom_scale: float | None = 1.0


# -----------------------------------------------------------------------------
# 5. Connector
# -----------------------------------------------------------------------------
class ConnectorAnchor(BaseModel):
    model_config = ConfigDict(extra="forbid")

    target_id: str | None = None
    side: Literal["left", "right", "top", "bottom", "center"] | None = "center"
    x: float | None = None
    y: float | None = None


class ConnectorLabel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str
    font_size: float = 16
    background: str | None = "rgba(0, 0, 0, 0.8)"


class ConnectorProps(BaseModel):
    model_config = ConfigDict(extra="forbid")

    from_anchor: ConnectorAnchor
    to_anchor: ConnectorAnchor
    routing: Literal["straight", "curved", "orthogonal_elbow"] = "curved"
    has_arrow: bool = True
    stroke: str = "#3b82f6"
    stroke_width: float = 2.0
    stroke_dasharray: str | None = None
    label: ConnectorLabel | None = None


class ConnectorState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    active: bool = False
    draw_progress: float = 1.0


# -----------------------------------------------------------------------------
# 6. Image
# -----------------------------------------------------------------------------
class ImageProps(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source: str
    object_fit: Literal["cover", "contain", "fill"] = "cover"
    border_radius: float = 0


class ImageState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source: str | None = None
    scale: float = 1.0


# -----------------------------------------------------------------------------
# 7. Video
# -----------------------------------------------------------------------------
class VideoProps(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source: str
    loop: bool = True
    muted: bool = True
    playback_rate: float = 1.0
    loop_duration_frames: int | None = None


class VideoState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    seek_frame: int = 0
    is_playing: bool = True


# -----------------------------------------------------------------------------
# 8. Bar
# -----------------------------------------------------------------------------
class BarProps(BaseModel):
    model_config = ConfigDict(extra="forbid")

    orientation: Literal["horizontal", "vertical"] = "horizontal"
    fill_percentage: float = Field(default=1.0, ge=0.0, le=1.0)
    max_length: float = 300.0
    thickness: float = 24.0
    corner_radius: float = 6.0
    foreground_color: str = "#3b82f6"
    background_track_color: str | None = "rgba(255, 255, 255, 0.08)"


class BarState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    current_fill: float | None = None
    color: str | None = None


# -----------------------------------------------------------------------------
# 9. Line
# -----------------------------------------------------------------------------
class LinePoint(BaseModel):
    model_config = ConfigDict(extra="forbid")

    x: float
    y: float


class LineProps(BaseModel):
    model_config = ConfigDict(extra="forbid")

    points: list[LinePoint] = Field(default_factory=list)
    curve_type: Literal["linear", "monotone_cubic", "step"] = "monotone_cubic"
    stroke: str = "#3b82f6"
    stroke_width: float = 3.0
    area_fill: str | None = None


class LineState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    points: list[LinePoint] | None = None
    draw_progress: float = 1.0


# -----------------------------------------------------------------------------
# 10. Point
# -----------------------------------------------------------------------------
class PointProps(BaseModel):
    model_config = ConfigDict(extra="forbid")

    x: float
    y: float
    radius: float = 6.0
    fill: str = "#3b82f6"
    stroke: str | None = None
    stroke_width: float = 0
    label: str | None = None


class PointState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    x: float | None = None
    y: float | None = None
    pulse_scale: float = 1.0


# -----------------------------------------------------------------------------
# 11. Segment
# -----------------------------------------------------------------------------
class SegmentProps(BaseModel):
    model_config = ConfigDict(extra="forbid")

    parent_track_id: str
    start_ratio: float = Field(default=0.0, ge=0.0, le=1.0)
    length_ratio: float = Field(default=1.0, ge=0.0, le=1.0)
    fill: str = "#3b82f6"
    label: str | None = None


class SegmentState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    start_ratio: float | None = None
    length_ratio: float | None = None


# -----------------------------------------------------------------------------
# 12. Progress
# -----------------------------------------------------------------------------
class ProgressProps(BaseModel):
    model_config = ConfigDict(extra="forbid")

    variant: Literal["radial_ring", "linear_meter"] = "radial_ring"
    progress_ratio: float = Field(default=0.5, ge=0.0, le=1.0)
    radius: float = 60.0
    stroke_width: float = 8.0
    track_color: str = "rgba(255, 255, 255, 0.1)"
    fill_color: str = "#3b82f6"
    center_label: str | None = None


class ProgressState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    progress_ratio: float | None = None


# -----------------------------------------------------------------------------
# 13. Group
# -----------------------------------------------------------------------------
class GroupProps(BaseModel):
    model_config = ConfigDict(extra="forbid")

    child_ids: list[str] = Field(default_factory=list)
    layout_flow: Literal["none", "row", "column"] = "none"
    gap: float = 0
    align_items: Literal["flex-start", "center", "flex-end", "stretch"] = "flex-start"
    justify_content: Literal["flex-start", "center", "flex-end", "space-between", "space-around"] = "flex-start"


class GroupState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    shift_x: float = 0
    shift_y: float = 0
    group_opacity: float = 1.0
