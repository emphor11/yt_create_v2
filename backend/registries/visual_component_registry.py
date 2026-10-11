from __future__ import annotations

import math
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator


class ComponentCategory(str, Enum):
    STRUCTURAL_CONTAINER = "structural_container"
    VISUAL_LEAF = "visual_leaf"
    RELATIONAL_LINK = "relational_link"


# -----------------------------------------------------------------------------
# Component Props Models
# -----------------------------------------------------------------------------

class SurfaceCardProps(BaseModel):
    model_config = ConfigDict(extra="forbid")

    variant: Literal["elevated", "outlined", "glass", "accent_top"] = "elevated"
    intent: Literal["neutral", "accent", "danger", "success", "warning"] = "neutral"
    header_label: str | None = None
    layout_flow: Literal["column", "row"] = "column"
    macro_zone: str | None = None


class MetricCardProps(BaseModel):
    """Self-contained metric card combining header, prominent stat, label, status badge, and citation."""
    model_config = ConfigDict(extra="forbid")

    header: str | None = Field(default=None, description="Top header band, e.g. 'WHAT YOU OWE', 'LOAN BENCHMARK'")
    label: str = Field(..., min_length=1, description="Metric dimension label, e.g. 'HOME LOAN RATE', 'REPRICING SPEED'")
    display_value: str = Field(..., min_length=1, description="Formatted prominent stat, e.g. '8.50%', '₹45,390', '>57%'")
    raw_value: float | None = Field(default=None, description="Numeric target for count-up animation, e.g. 8.5")
    tag: str | None = Field(default=None, description="Optional status badge pill in corner, e.g. 'IMMEDIATE', 'LAGGING'")
    subtext: str | None = Field(default=None, description="Optional citation or explanatory proof, e.g. 'Linked to RBI repo rate'")
    intent: Literal["neutral", "accent", "danger", "success", "warning"] = "neutral"
    variant: Literal["elevated", "outlined", "glass", "accent_top"] = "elevated"

    @model_validator(mode="before")
    @classmethod
    def normalize_value_field(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # Check common aliases for display_value
            if not data.get("display_value"):
                for alias in ("amount", "stat", "metric", "figure", "number", "formatted_value", "display", "val", "value"):
                    if alias in data and data[alias] is not None:
                        data["display_value"] = str(data.pop(alias))
                        break

            if "value" in data and "raw_value" not in data:
                data["raw_value"] = data.pop("value")

            if not data.get("display_value") and data.get("raw_value") is not None:
                data["display_value"] = str(data["raw_value"])

            # Auto-rescue: when LLM puts formatted number/stat into 'label' instead of 'display_value'
            if not data.get("display_value") and data.get("label"):
                label_str = str(data["label"])
                if re.search(r"\d", label_str):
                    data["display_value"] = label_str
                    if data.get("header"):
                        data["label"] = str(data["header"])
                    elif data.get("tag"):
                        data["label"] = str(data["tag"])
                    else:
                        data["label"] = "STAT"

            if "display_value" in data and data["display_value"] is not None:
                data["display_value"] = str(data["display_value"])

            # Handle raw_value safely (must be float or None)
            if "raw_value" in data and data["raw_value"] is not None:
                try:
                    data["raw_value"] = float(data["raw_value"])
                except (ValueError, TypeError):
                    if not data.get("display_value"):
                        data["display_value"] = str(data["raw_value"])
                    data["raw_value"] = None
            elif ("raw_value" not in data or data["raw_value"] is None) and data.get("display_value"):
                try:
                    clean_num = str(data["display_value"]).strip().strip("$₹€%").strip()
                    data["raw_value"] = float(clean_num)
                except (ValueError, TypeError):
                    pass

        return data


class HeroStatProps(BaseModel):
    """Prominent standalone hero metric for focal screen moments."""
    model_config = ConfigDict(extra="forbid")

    label: str = Field(..., min_length=1, description="Metric dimension label, e.g. 'TOTAL ADDITIONAL INTEREST'")
    display_value: str = Field(..., min_length=1, description="Formatted prominent stat, e.g. '₹2.5 LAKH'")
    raw_value: float | None = Field(default=None, description="Numeric target for count-up animation")
    tag: str | None = Field(default=None, description="Optional pill badge, e.g. '20-YEAR TENURE'")
    subtext: str | None = Field(default=None, description="Secondary citation or explanation")
    intent: Literal["neutral", "accent", "danger", "success", "warning"] = "neutral"

    @model_validator(mode="before")
    @classmethod
    def normalize_value_field(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if not data.get("display_value"):
                for alias in ("amount", "stat", "metric", "figure", "number", "formatted_value", "display", "val", "value"):
                    if alias in data and data[alias] is not None:
                        data["display_value"] = str(data.pop(alias))
                        break

            if "value" in data and "raw_value" not in data:
                data["raw_value"] = data.pop("value")

            if not data.get("display_value") and data.get("raw_value") is not None:
                data["display_value"] = str(data["raw_value"])

            # Auto-rescue: when LLM puts formatted number/stat into 'label' instead of 'display_value'
            if not data.get("display_value") and data.get("label"):
                label_str = str(data["label"])
                if re.search(r"\d", label_str):
                    data["display_value"] = label_str
                    if data.get("subtext"):
                        data["label"] = str(data["subtext"])
                    elif data.get("tag"):
                        data["label"] = str(data["tag"])
                    else:
                        data["label"] = "STAT"

            if "display_value" in data and data["display_value"] is not None:
                data["display_value"] = str(data["display_value"])

            if "raw_value" in data and data["raw_value"] is not None:
                try:
                    data["raw_value"] = float(data["raw_value"])
                except (ValueError, TypeError):
                    if not data.get("display_value"):
                        data["display_value"] = str(data["raw_value"])
                    data["raw_value"] = None
            elif ("raw_value" not in data or data["raw_value"] is None) and data.get("display_value"):
                try:
                    clean_num = str(data["display_value"]).strip().strip("$₹€%").strip()
                    data["raw_value"] = float(clean_num)
                except (ValueError, TypeError):
                    pass

            if not data.get("label") and data.get("tag"):
                data["label"] = data["tag"]
        return data


class ComparisonCardProps(BaseModel):
    """Self-contained comparison card displaying two contrasting sides (e.g. Loans vs Deposits, Before vs After)."""
    model_config = ConfigDict(extra="forbid")

    header: str | None = Field(default=None, description="Top header band, e.g. 'RATE HIKE TRANSMISSION'")
    left_label: str = Field(..., min_length=1, description="Left category label, e.g. 'LOAN EMI (BORROWERS)'")
    left_value: str = Field(..., min_length=1, description="Left prominent stat, e.g. '+2.50%', '₹48,900'")
    left_tag: str | None = Field(default=None, description="Left status pill, e.g. 'IMMEDIATE'")
    left_intent: Literal["neutral", "accent", "danger", "success", "warning"] = "danger"

    right_label: str = Field(..., min_length=1, description="Right category label, e.g. 'SAVINGS FD (DEPOSITORS)'")
    right_value: str = Field(..., min_length=1, description="Right prominent stat, e.g. '0.00%', 'UNCHANGED'")
    right_tag: str | None = Field(default=None, description="Right status pill, e.g. 'LAGGING'")
    right_intent: Literal["neutral", "accent", "danger", "success", "warning"] = "neutral"

    subtext: str | None = Field(default=None, description="Bottom citation or takeaway note")
    intent: Literal["neutral", "accent", "danger", "success", "warning"] = "neutral"


class ProcessStepItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    step: int | None = Field(default=None, ge=1, le=5, description="Sequential step number (derived from list index if omitted)")
    title: str = Field(..., min_length=1, description="Step title, e.g. 'RBI Repo Hike'")
    detail: str | None = Field(default=None, description="Short detail, e.g. '+50 bps'")


class ProcessCardProps(BaseModel):
    """Self-contained causal process card showing 2 to 4 sequential steps."""
    model_config = ConfigDict(extra="forbid")

    header: str | None = Field(default=None, description="Top header band, e.g. 'TRANSMISSION TIMELINE'")
    title: str | None = Field(default=None, description="Process title, e.g. 'HOW THE HIKE TRAVELS'")
    steps: list[ProcessStepItem] = Field(..., min_length=2, max_length=4)
    subtext: str | None = Field(default=None, description="Bottom citation or explanation")
    intent: Literal["neutral", "accent", "danger", "success", "warning"] = "accent"

    @model_validator(mode="after")
    def derive_step_numbers(self) -> "ProcessCardProps":
        for idx, step_item in enumerate(self.steps, start=1):
            if step_item.step is None:
                step_item.step = idx
        return self


class TrendLineDataPoint(BaseModel):
    model_config = ConfigDict(extra="forbid")

    label: str = Field(..., min_length=1, description="Label for point, e.g. '2020' or 'Q1'")
    value: float = Field(..., description="Numeric value for point")


class TrendLineHighlightPoint(BaseModel):
    model_config = ConfigDict(extra="forbid")

    label: str = Field(..., min_length=1, description="Highlight label, e.g. '2024 PEAK'")
    value: str | float | None = Field(default=None, description="Optional formatted or numeric value, e.g. '₹88.50'")


class TrendLineChartProps(BaseModel):
    """Animated time-series or trend line chart with area gradient and highlight marker."""
    model_config = ConfigDict(extra="forbid")

    header: str = Field(..., min_length=1, description="Chart title, e.g. 'USD / INR 5-YEAR TRAJECTORY'")
    data_points: list[TrendLineDataPoint] = Field(default_factory=list, max_length=12, description="Optional list of sequential coordinates")
    trend: Literal["up", "down", "neutral"] = Field(default="neutral", description="Macro trend direction")
    intent: Literal["neutral", "accent", "danger", "success", "warning"] = Field(default="neutral", description="Optional visual color intent")
    highlight_point: TrendLineHighlightPoint | None = Field(default=None, description="Optional highlight pill marker")
    subtext: str | None = Field(default=None, description="Optional secondary note or citation")

    @model_validator(mode="before")
    @classmethod
    def auto_derive_intent_and_points(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # Resolve aliases for data_points
            if not data.get("data_points"):
                for alias in ("points", "series", "data", "values", "items", "chart_data"):
                    if alias in data and data[alias] is not None:
                        data["data_points"] = data.pop(alias)
                        break

            if data.get("data_points") is None:
                data["data_points"] = []
            elif isinstance(data.get("data_points"), list) and len(data["data_points"]) == 1:
                raise ValueError("TrendLineChart data_points, if provided, must contain at least 2 points.")

            if not data.get("intent") or data.get("intent") == "neutral":
                trend = data.get("trend")
                if trend == "down":
                    data["intent"] = "danger"
                elif trend == "up":
                    data["intent"] = "accent"
            if "title" in data and not data.get("header"):
                data["header"] = data["title"]
        return data


class RankedBarItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    label: str = Field(..., min_length=1, description="Category name, e.g. 'India'")
    value: float = Field(..., description="Numeric value for proportional bar scaling")
    display_value: str | None = Field(default=None, description="Optional formatted display text, e.g. '87%'")
    intent: Literal["neutral", "accent", "danger", "success", "warning"] = Field(default="neutral", description="Color intent")
    tag: str | None = Field(default=None, description="Optional status pill tag, e.g. 'HIGHEST RISK'")

    @model_validator(mode="before")
    @classmethod
    def auto_derive_display_value(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if not data.get("display_value") and data.get("value") is not None:
                val = data["value"]
                data["display_value"] = str(int(val)) if isinstance(val, (int, float)) and val % 1 == 0 else str(val)
        return data


class RankedBarChartProps(BaseModel):
    """Self-contained horizontal comparative bar chart for 2 to 5 ranked items."""
    model_config = ConfigDict(extra="forbid")

    header: str = Field(..., min_length=1, description="Ranking title, e.g. 'CRUDE OIL IMPORT DEPENDENCY'")
    bars: list[RankedBarItem] = Field(..., min_length=2, max_length=6, description="List of comparative bar items")
    benchmark_value: float | None = Field(default=None, description="Optional vertical benchmark value")
    benchmark_label: str | None = Field(default=None, description="Optional label for the benchmark, e.g. 'Global Average'")
    subtext: str | None = Field(default=None, description="Bottom citation or context note")
    intent: Literal["neutral", "accent", "danger", "success", "warning"] = "neutral"

    @model_validator(mode="before")
    @classmethod
    def normalize_title_and_bars(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "title" in data and not data.get("header"):
                data["header"] = data["title"]
        return data


class DonutSliceItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    label: str = Field(..., min_length=1, description="Slice category label, e.g. 'Equities'")
    value: float = Field(..., gt=0, description="Positive numeric value or percentage")
    display_value: str | None = Field(default=None, description="Optional formatted display text, e.g. '55%'")
    intent: Literal["neutral", "accent", "danger", "success", "warning"] | None = Field(default=None, description="Color intent")
    color: str | None = Field(default=None, description="Optional custom hex color")
    tag: str | None = Field(default=None, description="Optional pill tag, e.g. 'Core'")

    @model_validator(mode="before")
    @classmethod
    def auto_derive_display_value(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if not data.get("display_value") and data.get("value") is not None:
                val = data["value"]
                data["display_value"] = str(int(val)) if isinstance(val, (int, float)) and val % 1 == 0 else str(val)
        return data


class AllocationDonutProps(BaseModel):
    """Self-contained asset allocation or revenue breakdown donut chart."""
    model_config = ConfigDict(extra="forbid")

    header: str = Field(..., min_length=1, description="Chart title, e.g. 'PORTFOLIO ASSET ALLOCATION'")
    slices: list[DonutSliceItem] = Field(..., min_length=2, max_length=6, description="List of 2 to 6 allocation slices")
    center_label: str | None = Field(default=None, description="Subtitle inside donut center, e.g. 'TOTAL ASSETS'")
    center_value: str | None = Field(default=None, description="Primary stat inside donut center, e.g. '100%' or '₹10L'")
    subtext: str | None = Field(default=None, description="Secondary citation or explanatory note")
    intent: Literal["neutral", "accent", "danger", "success", "warning"] = "neutral"

    @model_validator(mode="before")
    @classmethod
    def normalize_title_and_slices(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "title" in data and not data.get("header"):
                data["header"] = data["title"]
            if "segments" in data and not data.get("slices"):
                data["slices"] = data["segments"]
        return data


class WaterfallStepItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    label: str = Field(..., min_length=1, description="Step label, e.g. 'Gross Revenue', 'COGS', 'Net Profit'")
    value: float = Field(..., description="Numeric delta or total value (positive or negative)")
    display_value: str | None = Field(default=None, description="Optional formatted display text, e.g. '₹100 Cr', '-₹40 Cr'")
    is_total: bool = Field(default=False, description="Whether this column represents a cumulative total rather than a delta")
    intent: Literal["neutral", "accent", "danger", "success", "warning"] | None = Field(default=None, description="Color intent")

    @model_validator(mode="before")
    @classmethod
    def auto_derive_display_value(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if not data.get("display_value") and data.get("value") is not None:
                val = data["value"]
                formatted = str(int(val)) if isinstance(val, (int, float)) and val % 1 == 0 else str(val)
                data["display_value"] = f"+{formatted}" if isinstance(val, (int, float)) and val > 0 and not data.get("is_total") else formatted
        return data


class WaterfallBridgeProps(BaseModel):
    """Self-contained financial waterfall bridge chart from initial value to final outcome."""
    model_config = ConfigDict(extra="forbid")

    header: str = Field(..., min_length=1, description="Chart title, e.g. 'REVENUE TO NET PROFIT BRIDGE'")
    steps: list[WaterfallStepItem] = Field(..., min_length=3, max_length=7, description="List of 3 to 7 sequential steps/deltas")
    subtext: str | None = Field(default=None, description="Optional secondary note or citation")
    intent: Literal["neutral", "accent", "danger", "success", "warning"] = "neutral"

    @model_validator(mode="before")
    @classmethod
    def normalize_title(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "title" in data and not data.get("header"):
                data["header"] = data["title"]
        return data


class MetricBlockProps(BaseModel):
    model_config = ConfigDict(extra="forbid")

    qualifier: str | None = Field(default=None, description="Verbatim qualifier, e.g. '>', '<', '~'")
    raw_value: float | None = Field(default=None, description="Numeric target for counter animations")
    display_value: str = Field(..., description="Authoritative verbatim display string")
    start_value: float = Field(default=0.0, description="Counter starting value")
    unit: str | None = Field(default=None, description="Unit symbol, e.g. '%', 'LPA'")
    prefix: str | None = Field(default=None, description="Prefix symbol, e.g. '₹', '$'")
    label: str = Field(..., description="Category label")
    subtext: str | None = Field(default=None, description="Secondary citation or contextual proof")
    trend: Literal["up", "down", "flat"] | None = None
    emphasis: Literal["hero", "standard", "compact", "danger", "positive", "secondary", "supporting"] = "standard"


class BadgeProps(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str = Field(..., min_length=1, description="Short uppercase label")
    variant: Literal["filled", "subtle", "outline"] = "filled"
    intent: Literal["neutral", "danger", "warning", "success", "accent", "positive", "negative"] = "neutral"
    icon_name: str | None = None


class CalloutProps(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str = Field(..., min_length=1, description="Editorial thesis or deduction")
    attribution: str | None = None
    intent: Literal["insight", "warning", "danger", "positive", "takeaway"] = "insight"


class FlowConnectorProps(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_id: str = Field(..., min_length=1, description="ID of source visual object")
    target_id: str = Field(..., min_length=1, description="ID of target visual object")
    relationship_type: Literal["causes", "flows_to", "subtracts", "absorbs", "contrasts_with"] = "causes"
    routing: Literal["orthogonal_elbow", "curved", "straight"] = "orthogonal_elbow"
    has_arrow: bool = True
    label: str | None = None
    style_intent: Literal["solid", "dashed", "animated_pulse"] = "solid"


# -----------------------------------------------------------------------------
# Deterministic Component Sizing Rules
# -----------------------------------------------------------------------------

class ComponentSizingRules:
    """Computes layout bounding boxes deterministically without expanding into primitives."""

    @staticmethod
    def measure_badge(props: dict[str, Any]) -> tuple[float, float]:
        text_len = len(str(props.get("text", "")))
        width = max(110.0, text_len * 9.5 + 36.0)
        return (width, 32.0)

    @staticmethod
    def measure_metric_block(props: dict[str, Any], available_width: float = 472.0) -> tuple[float, float]:
        emphasis = str(props.get("emphasis", "standard"))
        subtext = props.get("subtext")
        height = 140.0
        if emphasis == "hero":
            height = 180.0
        elif emphasis == "compact":
            height = 100.0
        if subtext:
            height += 30.0
        return (available_width, height)

    @staticmethod
    def measure_callout(props: dict[str, Any], available_width: float = 540.0) -> tuple[float, float]:
        text_len = len(str(props.get("text", "")))
        content_width = max(200.0, available_width - 80.0)
        lines = max(1, math.ceil((text_len * 10.0) / content_width))
        height = max(90.0, lines * 28.0 + 44.0)
        return (available_width, height)

    @staticmethod
    def measure_metric_card(props: dict[str, Any], available_width: float = 520.0) -> tuple[float, float]:
        width = min(available_width, 620.0)
        subtext = props.get("subtext")
        header = props.get("header")
        height = 200.0
        if header:
            height += 30.0
        if subtext:
            height += 24.0
        return (width, height)

    @staticmethod
    def measure_hero_stat(props: dict[str, Any], available_width: float = 640.0) -> tuple[float, float]:
        return (min(available_width, 820.0), 240.0)

    @staticmethod
    def measure_comparison_card(props: dict[str, Any], available_width: float = 640.0) -> tuple[float, float]:
        return (min(available_width, 840.0), 270.0)

    @staticmethod
    def measure_process_card(props: dict[str, Any], available_width: float = 640.0) -> tuple[float, float]:
        steps = props.get("steps") or []
        step_count = len(steps) if isinstance(steps, list) else 3
        base_h = 250.0 if step_count <= 2 else 280.0
        if props.get("header"):
            base_h += 24.0
        if props.get("subtext"):
            base_h += 20.0
        return (min(available_width, 840.0), base_h)

    @staticmethod
    def measure_trend_line_chart(props: dict[str, Any], available_width: float = 640.0) -> tuple[float, float]:
        width = min(available_width, 860.0)
        height = 380.0
        if props.get("subtext"):
            height += 20.0
        return (width, height)

    @staticmethod
    def measure_ranked_bar_chart(props: dict[str, Any], available_width: float = 640.0) -> tuple[float, float]:
        bars = props.get("bars") or []
        bar_count = len(bars) if isinstance(bars, list) else 3
        height = 100.0 + max(2, bar_count) * 48.0
        if props.get("subtext"):
            height += 20.0
        if props.get("benchmark_value") is not None:
            height += 15.0
        return (min(available_width, 860.0), height)

    @staticmethod
    def measure_allocation_donut(props: dict[str, Any], available_width: float = 640.0) -> tuple[float, float]:
        slices = props.get("slices") or []
        slice_count = len(slices) if isinstance(slices, list) else 3
        height = max(360.0, 120.0 + slice_count * 46.0)
        if props.get("subtext"):
            height += 20.0
        return (min(available_width, 860.0), height)

    @staticmethod
    def measure_waterfall_bridge(props: dict[str, Any], available_width: float = 640.0) -> tuple[float, float]:
        width = min(available_width, 880.0)
        height = 400.0
        if props.get("subtext"):
            height += 20.0
        return (width, height)

    @staticmethod
    def measure_surface_card(
        child_sizes: list[tuple[float, float]] | None = None,
        available_width: float = 520.0,
    ) -> tuple[float, float]:
        pad_y = 48.0  # 24px top + 24px bottom
        gap = 16.0
        if not child_sizes:
            return (available_width, 240.0)
        total_child_h = sum(h for _, h in child_sizes)
        total_gaps = gap * max(0, len(child_sizes) - 1)
        card_h = pad_y + total_child_h + total_gaps
        return (available_width, max(240.0, card_h))


# -----------------------------------------------------------------------------
# Registry Descriptors
# -----------------------------------------------------------------------------

@dataclass(frozen=True)
class VisualComponentDescriptor:
    component_type: str
    category: ComponentCategory
    description: str
    props_model: type[BaseModel]
    supported_children: tuple[str, ...]
    supported_actions: tuple[str, ...]
    remotion_component: str


class VisualComponentRegistryError(Exception):
    """Raised when an invalid visual component operation is encountered."""


class VisualComponentRegistry:
    """Dedicated registry for high-level React/Remotion visual components.

    Keeps the canonical PrimitiveRegistry strictly focused on low-level primitives.
    """

    COMPONENTS: dict[str, VisualComponentDescriptor] = {
        "MetricCard": VisualComponentDescriptor(
            component_type="MetricCard",
            category=ComponentCategory.VISUAL_LEAF,
            description="Self-contained card combining header, prominent stat, label, status badge, and citation.",
            props_model=MetricCardProps,
            supported_children=(),
            supported_actions=("enter", "exit", "update_value", "highlight", "pulse", "hold"),
            remotion_component="MetricCard",
        ),
        "HeroStat": VisualComponentDescriptor(
            component_type="HeroStat",
            category=ComponentCategory.VISUAL_LEAF,
            description="Prominent standalone hero metric for focal screen moments.",
            props_model=HeroStatProps,
            supported_children=(),
            supported_actions=("enter", "exit", "update_value", "highlight", "pulse", "hold"),
            remotion_component="HeroStat",
        ),
        "ComparisonCard": VisualComponentDescriptor(
            component_type="ComparisonCard",
            category=ComponentCategory.VISUAL_LEAF,
            description="Self-contained comparison card displaying two contrasting sides (e.g. Loans vs Deposits).",
            props_model=ComparisonCardProps,
            supported_children=(),
            supported_actions=("enter", "exit", "update_value", "highlight", "pulse", "hold"),
            remotion_component="ComparisonCard",
        ),
        "ProcessCard": VisualComponentDescriptor(
            component_type="ProcessCard",
            category=ComponentCategory.VISUAL_LEAF,
            description="Self-contained causal process card showing 2 to 4 sequential steps.",
            props_model=ProcessCardProps,
            supported_children=(),
            supported_actions=("enter", "exit", "highlight", "pulse", "hold"),
            remotion_component="ProcessCard",
        ),
        "TrendLineChart": VisualComponentDescriptor(
            component_type="TrendLineChart",
            category=ComponentCategory.VISUAL_LEAF,
            description="Animated time-series or trend line chart with area gradient and highlight marker.",
            props_model=TrendLineChartProps,
            supported_children=(),
            supported_actions=("enter", "exit", "highlight", "pulse", "hold"),
            remotion_component="TrendLineChart",
        ),
        "RankedBarChart": VisualComponentDescriptor(
            component_type="RankedBarChart",
            category=ComponentCategory.VISUAL_LEAF,
            description="Self-contained horizontal comparative bar chart for 2 to 5 ranked items.",
            props_model=RankedBarChartProps,
            supported_children=(),
            supported_actions=("enter", "exit", "highlight", "pulse", "hold"),
            remotion_component="RankedBarChart",
        ),
        "AllocationDonut": VisualComponentDescriptor(
            component_type="AllocationDonut",
            category=ComponentCategory.VISUAL_LEAF,
            description="Self-contained asset allocation or revenue breakdown donut chart.",
            props_model=AllocationDonutProps,
            supported_children=(),
            supported_actions=("enter", "exit", "highlight", "pulse", "hold"),
            remotion_component="AllocationDonut",
        ),
        "WaterfallBridge": VisualComponentDescriptor(
            component_type="WaterfallBridge",
            category=ComponentCategory.VISUAL_LEAF,
            description="Self-contained financial waterfall bridge chart from initial value to final outcome.",
            props_model=WaterfallBridgeProps,
            supported_children=(),
            supported_actions=("enter", "exit", "highlight", "pulse", "hold"),
            remotion_component="WaterfallBridge",
        ),
        "SurfaceCard": VisualComponentDescriptor(
            component_type="SurfaceCard",
            category=ComponentCategory.STRUCTURAL_CONTAINER,
            description="Elevated card container providing contrast, border, padding, and layout flow.",
            props_model=SurfaceCardProps,
            supported_children=("MetricBlock", "Badge", "Callout"),
            supported_actions=("enter", "exit", "highlight", "pulse", "hold"),
            remotion_component="SurfaceCard",
        ),
        "MetricBlock": VisualComponentDescriptor(
            component_type="MetricBlock",
            category=ComponentCategory.VISUAL_LEAF,
            description="Quantitative indicator displaying formatted value, qualifier, label, and counter motion.",
            props_model=MetricBlockProps,
            supported_children=(),
            supported_actions=("enter", "exit", "update_value", "highlight", "pulse", "hold"),
            remotion_component="MetricBlock",
        ),
        "Badge": VisualComponentDescriptor(
            component_type="Badge",
            category=ComponentCategory.VISUAL_LEAF,
            description="Compact pill capsule for categorization, status, or polarity.",
            props_model=BadgeProps,
            supported_children=(),
            supported_actions=("enter", "exit", "highlight", "hold"),
            remotion_component="Badge",
        ),
        "Callout": VisualComponentDescriptor(
            component_type="Callout",
            category=ComponentCategory.VISUAL_LEAF,
            description="Editorial deduction or takeaway commentary box with left accent border.",
            props_model=CalloutProps,
            supported_children=(),
            supported_actions=("enter", "exit", "pulse", "hold"),
            remotion_component="Callout",
        ),
        "FlowConnector": VisualComponentDescriptor(
            component_type="FlowConnector",
            category=ComponentCategory.RELATIONAL_LINK,
            description="Directed relational link between components expressing causality, flow, or divergence.",
            props_model=FlowConnectorProps,
            supported_children=(),
            supported_actions=("appear", "enter", "exit", "pulse", "hold"),
            remotion_component="FlowConnector",
        ),
    }

    @classmethod
    def is_registered(cls, component_type: str) -> bool:
        return component_type in cls.COMPONENTS

    @classmethod
    def get_descriptor(cls, component_type: str) -> VisualComponentDescriptor:
        if component_type not in cls.COMPONENTS:
            raise VisualComponentRegistryError(
                f"Unknown visual component type '{component_type}'. "
                f"Registered components: {sorted(cls.COMPONENTS.keys())}"
            )
        return cls.COMPONENTS[component_type]

    SHARED_METADATA_KEYS: frozenset[str] = frozenset({
        "macro_zone",
        "layout_flow",
        "role",
        "lifecycle_mode",
        "parent_object_id",
        "object_id",
        "component_type",
        "primitive_type",
    })

    PROPERTY_ALIASES: dict[str, dict[str, str]] = {
        "HeroStat": {
            "badge_text": "tag",
            "value": "raw_value",
            "amount": "display_value",
            "stat": "display_value",
            "metric": "display_value",
            "figure": "display_value",
            "number": "display_value",
        },
        "MetricCard": {
            "badge_text": "tag",
            "title": "header",
            "value": "raw_value",
            "amount": "display_value",
            "stat": "display_value",
            "metric": "display_value",
            "figure": "display_value",
            "number": "display_value",
        },
        "ComparisonCard": {"title": "header"},
        "TrendLineChart": {
            "title": "header",
            "points": "data_points",
            "series": "data_points",
            "data": "data_points",
            "values": "data_points",
            "items": "data_points",
            "chart_data": "data_points",
        },
        "RankedBarChart": {"title": "header"},
        "AllocationDonut": {"title": "header", "segments": "slices", "center_stat": "center_value", "total_value": "center_value"},
        "WaterfallBridge": {"title": "header"},
    }

    @classmethod
    def validate_props(cls, component_type: str, props: dict[str, Any]) -> BaseModel:
        desc = cls.get_descriptor(component_type)
        model_fields = desc.props_model.model_fields

        clean_props = dict(props)

        # Normalize known aliases for component props
        aliases = cls.PROPERTY_ALIASES.get(component_type, {})
        for alias, canonical in aliases.items():
            if alias in clean_props:
                if canonical not in clean_props or clean_props[canonical] is None:
                    clean_props[canonical] = clean_props[alias]
                del clean_props[alias]

        # Separate shared layout/lifecycle metadata not declared by the component model,
        # and ignore None-valued keys that belong to other schema definitions
        clean_props = {
            k: v for k, v in clean_props.items()
            if (k in model_fields) or (k not in cls.SHARED_METADATA_KEYS and v is not None)
        }

        # Validate that no unknown/unsupported properties remain
        unknown_keys = set(clean_props.keys()) - set(model_fields.keys())
        if unknown_keys:
            raise VisualComponentRegistryError(
                f"Component '{component_type}' received unsupported properties: {sorted(unknown_keys)}. "
                f"Supported properties are: {sorted(model_fields.keys())}."
            )

        return desc.props_model.model_validate(clean_props)

    @classmethod
    def measure(
        cls,
        component_type: str,
        props: dict[str, Any],
        child_sizes: list[tuple[float, float]] | None = None,
        available_width: float = 520.0,
    ) -> tuple[float, float]:
        if component_type == "MetricCard":
            return ComponentSizingRules.measure_metric_card(props, available_width)
        if component_type == "HeroStat":
            return ComponentSizingRules.measure_hero_stat(props, available_width)
        if component_type == "ComparisonCard":
            return ComponentSizingRules.measure_comparison_card(props, available_width)
        if component_type == "ProcessCard":
            return ComponentSizingRules.measure_process_card(props, available_width)
        if component_type == "TrendLineChart":
            return ComponentSizingRules.measure_trend_line_chart(props, available_width)
        if component_type == "RankedBarChart":
            return ComponentSizingRules.measure_ranked_bar_chart(props, available_width)
        if component_type == "AllocationDonut":
            return ComponentSizingRules.measure_allocation_donut(props, available_width)
        if component_type == "WaterfallBridge":
            return ComponentSizingRules.measure_waterfall_bridge(props, available_width)
        if component_type == "Badge":
            return ComponentSizingRules.measure_badge(props)
        if component_type == "MetricBlock":
            return ComponentSizingRules.measure_metric_block(props, available_width)
        if component_type == "Callout":
            return ComponentSizingRules.measure_callout(props, available_width)
        if component_type == "SurfaceCard":
            return ComponentSizingRules.measure_surface_card(child_sizes, available_width)
        if component_type == "FlowConnector":
            return (0.0, 0.0)
        raise VisualComponentRegistryError(f"No sizing rule defined for component '{component_type}'.")
