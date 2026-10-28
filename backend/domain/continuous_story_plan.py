"""
continuous_story_plan.py — Atomic AI Draft Domain Models + 5-Layout Composition Architecture.

Defines the exact, minimal schema that an AI (Gemini) produces for continuous
storytelling choreography using atomic visual elements and 5 professional composition layouts.

Architectural Principles:
1. Atomic Elements: No parent-child hierarchies. A card is a complete, self-contained visual unit.
2. 5-Layout Spatial Canvas: center, split_left, split_right, full_screen, full_bottom.
   Raw pixel coordinates (x, y, width, height) and relative chains (right_of, below, gap) are strictly forbidden.
3. Strict Pydantic Enforcement: ConfigDict(extra="forbid") ensures zero hallucinations.
4. Fact Grounding: Every numeric value and chart is bound to an approved fact ID.
5. Speech-Anchored Events: Every event is bound to spoken audio phrases.
"""
from __future__ import annotations

from typing import Any, Literal
from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator, model_validator


class StrictBaseModel(BaseModel):
    """Base model that strictly forbids any undeclared fields."""
    model_config = ConfigDict(extra="forbid")


ZoneName = Literal[
    "center",
    "split_left",
    "split_right",
    "full_screen",
    "full_bottom",
]

VALID_ZONES: set[str] = {
    "center",
    "split_left",
    "split_right",
    "full_screen",
    "full_bottom",
}

# Backward compatibility alias
LayoutType = ZoneName

VisualStateKind = Literal[
    "normal",
    "dimmed",
    "warning",
    "danger",
    "success",
    "stamped",
    "eroded",
]
VALID_VISUAL_STATES = (
    "normal",
    "dimmed",
    "warning",
    "danger",
    "success",
    "stamped",
    "eroded",
)

ChartType = Literal[
    "trajectory_area",
    "split_bar",
    "multi_bar",
    "stack",
]
VALID_CHART_TYPES = (
    "trajectory_area",
    "split_bar",
    "multi_bar",
    "stack",
)

CharacterStyle = Literal["futuristic_stick"]
VALID_CHARACTER_STYLES = ("futuristic_stick",)

CharacterPose = Literal["idle", "walk", "point", "think", "worried", "celebrate"]
VALID_CHARACTER_POSES = ("idle", "walk", "point", "think", "worried", "celebrate")

CharacterEmotion = Literal["neutral", "focused", "concerned", "surprised", "happy"]
VALID_CHARACTER_EMOTIONS = ("neutral", "focused", "concerned", "surprised", "happy")

CharacterFacing = Literal["left", "right"]
VALID_CHARACTER_FACINGS = ("left", "right")

AtmospherePreset = Literal[
    "paper_clean",
    "blueprint",
    "vault",
    "newsroom",
]
VALID_ATMOSPHERE_PRESETS = (
    "paper_clean",
    "blueprint",
    "vault",
    "newsroom",
)

ObjectType = Literal[
    "card",
    "number",
    "text",
    "chart",
    "image",
    "connector",
    "character",
    "stock_video",
    "scale",
    "money_stack",
    "document",
    "waterfall",
    "capital_flow",
]


class ImageAssetRequest(StrictBaseModel):
    """Visual asset specification requested by Gemini for real-world photo grounding."""
    query: str = Field(description="Search query describing the real-world image.")
    orientation: Literal["landscape", "portrait", "square"] = Field(
        default="landscape",
        description="Image orientation: 'landscape', 'portrait', or 'square'."
    )
    style: Literal["photo", "illustration"] = Field(
        default="photo",
        description="Visual style: 'photo' or 'illustration'."
    )
    composition: str | None = Field(
        default=None,
        description="Short visual composition instruction (e.g. 'subject on the left with empty space on the right')."
    )
    mood: str | None = Field(
        default=None,
        description="Optional visual mood (e.g. 'serious institutional finance documentary')."
    )
    avoid: list[str] = Field(
        default_factory=list,
        description="Optional list of unwanted visual properties (e.g. ['logos', 'watermarks', 'text-heavy signs', 'identifiable faces'])."
    )

    @field_validator("query")
    @classmethod
    def validate_query(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("ImageAssetRequest 'query' must be a non-empty string.")
        return v.strip()


class VideoAssetRequest(StrictBaseModel):
    """Visual asset specification requested by Gemini for real-world documentary/B-roll video grounding."""
    query: str = Field(description="Search query describing the real-world video.")
    orientation: Literal["landscape", "portrait", "square"] = Field(
        default="landscape",
        description="Video orientation: 'landscape', 'portrait', or 'square'."
    )
    mood: str | None = Field(
        default=None,
        description="Optional visual mood (e.g. 'serious institutional finance documentary')."
    )
    composition: str | None = Field(
        default=None,
        description="Short visual composition instruction (e.g. 'cinematic wide tracking shot of bank exterior')."
    )
    avoid: list[str] = Field(
        default_factory=list,
        description="Optional list of unwanted visual properties (e.g. ['logos', 'watermarks', 'text-heavy signs', 'identifiable faces'])."
    )
    minimum_duration_seconds: float | int | None = Field(
        default=None,
        description="Optional minimum required duration in seconds."
    )

    @field_validator("query")
    @classmethod
    def validate_query(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("VideoAssetRequest 'query' must be a non-empty string.")
        return v.strip()


class WaterfallStepDraft(StrictBaseModel):
    """A deduction or addition step in a financial cash flow waterfall funnel."""
    label: str = Field(description="Step name (e.g. 'Operating Expenses', 'Direct Taxes', 'Loan EMI').")
    value: float = Field(description="Numeric amount for math calculations.")
    display_value: str = Field(description="Formatted human display string (e.g. '-₹60,000', '-₹2,500 Cr').")
    step_type: Literal["deduction", "addition", "subtotal"] = Field(
        default="deduction",
        description="Step type: 'deduction' (leakage/cost), 'addition' (revenue/inflow), or 'subtotal'."
    )


class StoryObjectDraft(StrictBaseModel):
    """
    An independent, atomic visual element declared by the AI.
    Never uses parent_id or nested children.
    """
    id: str = Field(description="Unique identifier for the element.")
    type: ObjectType = Field(description="Visual element type.")
    layout: ZoneName = Field(
        default="center",
        description="Canvas zone placement: one of the 9 grid zones or 3 macro layouts."
    )
    purpose: str = Field(
        default="",
        description="Editorial purpose of this visual element."
    )

    # Card-specific atomic fields
    title: str | None = Field(
        default=None,
        description="Card header title (card elements only)."
    )
    display_value: str | None = Field(
        default=None,
        validation_alias=AliasChoices("display_value", "displayValue", "value_display", "formatted_value"),
        description="Formatted human-friendly display string authored directly by AI (e.g. '₹50 Lakhs', '8.5%', '₹1.38 Cr', '₹5,000')."
    )
    numeric_value: float | None = Field(
        default=None,
        validation_alias=AliasChoices("numeric_value", "numericValue", "raw_value"),
        description="Raw numeric value for animated counters and mathematical grounding."
    )
    value_fact_id: str | None = Field(
        default=None,
        description="Required for numeric cards. Identifies the approved fact for verification and provenance; it does not replace the directly authored display_value or numeric_value."
    )
    subtitle: str | None = Field(
        default=None,
        description="Card explanatory subtitle or context (card elements only)."
    )
    badge: str | None = Field(
        default=None,
        description="Status badge text (e.g. '+2.0% HIKE', 'BURDEN SURGE') (card elements only)."
    )
    visual_state: VisualStateKind | None = Field(
        default=None,
        validation_alias=AliasChoices("visual_state", "state"),
        description="Initial visual/emotional state ('normal', 'warning', 'danger', 'dimmed', 'success')."
    )
    accent: str | None = Field(
        default=None,
        description="Optional accent color hex code (e.g. '#3B82F6')."
    )

    # Standalone Number fields
    fact_id: str | None = Field(
        default=None,
        description="Reference to an approved fact ID. Required for standalone 'number' and 'chart'."
    )

    # Standalone Text fields
    text: str | None = Field(
        default=None,
        description="Display text content for standalone 'text' element."
    )

    # Chart-specific fields (Directly Authored)
    chart_type: ChartType | None = Field(
        default=None,
        description="Chart visualization subtype ('trajectory_area', 'split_bar', 'multi_bar', 'stack')."
    )
    series: list[dict[str, Any]] | None = Field(
        default=None,
        description="Direct chart series list: [{id, name, color, points: [{xLabel, yValue}]}]."
    )
    points: list[dict[str, Any]] | None = Field(
        default=None,
        description="Direct chart points for simple single-series charts: [{xLabel, yValue}]."
    )

    # Image and Stock Video fields
    asset_request: ImageAssetRequest | VideoAssetRequest | dict[str, Any] | None = Field(
        default=None,
        description="Visual specification requested by AI to search and resolve a real-world image or stock video."
    )
    asset_id: str | None = Field(
        default=None,
        description="Asset reference identifier for 'image' or 'stock_video' element."
    )
    alt: str | None = Field(
        default=None,
        description="Alternative descriptive text for media accessibility."
    )
    caption: str | None = Field(
        default=None,
        description="Optional caption text displayed with media."
    )
    fit: Literal["cover", "contain"] | None = Field(
        default="cover",
        description="Object fit scaling mode ('cover' or 'contain')."
    )
    overlay_tint: str | None = Field(
        default=None,
        description="Optional dark overlay tint for subtitle and visual readability."
    )
    border_color: str | None = Field(
        default=None,
        description="Optional border color hex code for image frame."
    )
    border_radius: float | int | None = Field(
        default=None,
        description="Optional border radius in pixels for image frame (default: 16)."
    )

    # Connector-specific fields
    from_id: str | None = Field(
        default=None,
        validation_alias=AliasChoices("from_id", "fromId", "from", "source"),
        description="Source card ID for 'connector' element."
    )
    to_id: str | None = Field(
        default=None,
        validation_alias=AliasChoices("to_id", "toId", "to", "target"),
        description="Target card ID for 'connector' element."
    )
    label: str | None = Field(
        default=None,
        description="Optional label on the connector arrow (e.g. 'Drives payment')."
    )

    # Character-specific fields
    character_style: CharacterStyle | None = Field(
        default=None,
        description="Character visual style (must be 'futuristic_stick')."
    )
    role: str | None = Field(
        default=None,
        description="Character narrative role (e.g. 'salaried employee')."
    )
    pose: CharacterPose | None = Field(
        default=None,
        description="Initial character pose ('idle', 'walk', 'point', 'think', 'worried', 'celebrate')."
    )
    emotion: CharacterEmotion | None = Field(
        default=None,
        description="Initial character emotion ('neutral', 'focused', 'concerned', 'surprised', 'happy'). Defaults to 'neutral' for characters."
    )
    facing: CharacterFacing | None = Field(
        default=None,
        description="Direction character faces ('left' or 'right')."
    )

    # Scale-specific fields (Directly Authored)
    left_title: str | None = Field(
        default=None,
        description="Left pan label/title (scale elements only)."
    )
    left_display_value: str | None = Field(
        default=None,
        description="Left pan formatted value string, e.g. '₹50 Lakhs' (scale elements only)."
    )
    left_numeric_value: float | None = Field(
        default=None,
        description="Left pan raw numeric weight for physics calculation (scale elements only)."
    )
    left_badge: str | None = Field(
        default=None,
        description="Left pan status badge text (scale elements only)."
    )
    right_title: str | None = Field(
        default=None,
        description="Right pan label/title (scale elements only)."
    )
    right_display_value: str | None = Field(
        default=None,
        description="Right pan formatted value string, e.g. '₹88.4 Lakhs' (scale elements only)."
    )
    right_numeric_value: float | None = Field(
        default=None,
        description="Right pan raw numeric weight for physics calculation (scale elements only)."
    )
    right_badge: str | None = Field(
        default=None,
        description="Right pan status badge text (scale elements only)."
    )
    tilt_direction: Literal["left", "right", "balanced"] | None = Field(
        default=None,
        description="Optional explicit tilt override ('left', 'right', 'balanced'). If omitted, computed from left vs right numeric values."
    )

    # Money Stack-specific fields (Directly Authored)
    stack_mode: Literal["single_tower", "comparison"] | None = Field(
        default=None,
        description="Stack mode: 'single_tower' (one skyscraper) or 'comparison' (side-by-side divide piles)."
    )
    unit_label: str | None = Field(
        default=None,
        description="Human label for each brick/bundle, e.g. '₹1,000 Cr per brick' or '₹50,000 per bundle'."
    )
    unit_value: float | None = Field(
        default=None,
        description="Numeric value represented by one brick/bundle."
    )
    total_display_value: str | None = Field(
        default=None,
        description="Total formatted value string, e.g. '₹25,000 Cr'."
    )
    total_numeric_value: float | None = Field(
        default=None,
        description="Total numeric value represented by the entire stack."
    )
    comparison_left_label: str | None = Field(
        default=None,
        description="Comparison mode: left pile label (e.g. 'Monthly Savings')."
    )
    comparison_left_value: str | None = Field(
        default=None,
        description="Comparison mode: left pile display value (e.g. '₹25,000')."
    )
    comparison_right_label: str | None = Field(
        default=None,
        description="Comparison mode: right pile label (e.g. 'Daily Profit')."
    )
    comparison_right_value: str | None = Field(
        default=None,
        description="Comparison mode: right pile display value (e.g. '₹4.8 Crore')."
    )
    show_human_scale: bool | None = Field(
        default=None,
        description="Whether to show the stick-figure silhouette at the base for human scale reference."
    )

    # Document-specific fields (Directly Authored)
    doc_title: str | None = Field(
        default=None,
        description="Headline document title (e.g. 'SEBI CIRCULAR // OCT 2024', 'RESERVE BANK OF INDIA')."
    )
    doc_reference: str | None = Field(
        default=None,
        description="Reference / circular serial number (e.g. 'CIRC-8924/2024', 'NOTIFICATION NO. 45')."
    )
    doc_body: str | None = Field(
        default=None,
        description="Verbatim or summarized legal/regulatory text excerpt inside the proof document."
    )
    highlight_phrase: str | None = Field(
        default=None,
        description="Key excerpt phrase within doc_body that receives an animated yellow highlighter swipe."
    )
    watermark: str | None = Field(
        default=None,
        description="Optional background security watermark (e.g. 'OFFICIAL', 'CONFIDENTIAL', 'CIRCULAR')."
    )
    stamp_text: str | None = Field(
        default=None,
        description="Optional rubber stamp overlay text (e.g. 'VERIFIED', 'MANDATORY', 'WARNING', 'APPROVED')."
    )

    # Waterfall-specific fields (Directly Authored)
    initial_label: str | None = Field(
        default=None,
        description="Starting capital or gross revenue label (e.g. 'Gross Corporate Revenue', 'Monthly Salary')."
    )
    initial_value: float | None = Field(
        default=None,
        description="Starting numeric value."
    )
    initial_display_value: str | None = Field(
        default=None,
        description="Starting formatted string (e.g. '₹1,00,000', '₹10,000 Cr')."
    )
    steps: list[WaterfallStepDraft] | None = Field(
        default=None,
        description="List of cascading deduction/addition steps in the waterfall."
    )
    final_label: str | None = Field(
        default=None,
        description="Label for surviving bottom cash (e.g. 'Net Operating Cash', 'Surviving Savings')."
    )
    final_value: float | None = Field(
        default=None,
        description="Final surviving numeric value."
    )
    final_display_value: str | None = Field(
        default=None,
        description="Final surviving formatted string (e.g. '₹12,000', '₹1,200 Cr')."
    )

    # Capital Flow-specific fields (Directly Authored)
    source_label: str | None = Field(
        default=None,
        description="Source entity/location label (e.g. 'MUMBAI // BSE', 'Domestic Retail Accounts')."
    )
    source_sublabel: str | None = Field(
        default=None,
        description="Optional source subtext (e.g. 'Emerging Market Equity')."
    )
    target_label: str | None = Field(
        default=None,
        description="Destination entity/location label (e.g. 'NEW YORK // WALL ST', 'US 10-Yr Treasuries')."
    )
    target_sublabel: str | None = Field(
        default=None,
        description="Optional destination subtext (e.g. 'Safe Haven Yield (4.5%)')."
    )
    flow_label: str | None = Field(
        default=None,
        description="Label describing the capital movement (e.g. 'Capital Flight', 'FII Net Drain', 'SIP Pipeline')."
    )
    flow_display_value: str | None = Field(
        default=None,
        description="Formatted monetary value in flight (e.g. '₹1.14 Lakh Crore', '$15 Billion')."
    )
    flow_direction: Literal["left_to_right", "right_to_left", "bidirectional"] | None = Field(
        default=None,
        description="Direction of capital flow particles/arrow ('left_to_right', 'right_to_left', 'bidirectional')."
    )

    @model_validator(mode="after")
    def validate_atomic_object_rules(self) -> StoryObjectDraft:
        # 1. Non-empty ID
        if not self.id or not self.id.strip():
            raise ValueError("Object 'id' must be a non-empty string.")

        # 2. Type-specific field exclusivity and requirements
        if self.type == "card":
            # Card requires title
            if not self.title or not self.title.strip():
                raise ValueError(f"Card '{self.id}' requires non-empty 'title'.")
            # Cards use title, value_fact_id, subtitle, badge, visual_state, accent, display_value, numeric_value
            if self.from_id is not None or self.to_id is not None or self.label is not None:
                raise ValueError(f"Card '{self.id}' cannot specify connector fields ('from_id', 'to_id', 'label').")
            if self.chart_type is not None or self.series is not None or self.points is not None:
                raise ValueError(f"Card '{self.id}' cannot specify chart fields ('chart_type', 'series', 'points').")
            if self.asset_id is not None:
                raise ValueError(f"Card '{self.id}' cannot specify 'asset_id' (images only).")
            if self.text is not None:
                raise ValueError(f"Card '{self.id}' cannot specify standalone 'text' (use 'title' or 'subtitle').")

        elif self.type == "number":
            # Standalone number requires display_value or numeric_value
            effective_has_number = (
                (self.display_value is not None and bool(str(self.display_value).strip()))
                or self.numeric_value is not None
                or (self.fact_id is not None and bool(str(self.fact_id).strip()))
                or (self.value_fact_id is not None and bool(str(self.value_fact_id).strip()))
            )
            if not effective_has_number:
                raise ValueError(f"Standalone number '{self.id}' requires 'display_value' or 'numeric_value'.")
            if self.from_id is not None or self.to_id is not None or self.label is not None:
                raise ValueError(f"Number '{self.id}' cannot specify connector fields.")
            if self.chart_type is not None or self.series is not None or self.points is not None or self.asset_id is not None:
                raise ValueError(f"Number '{self.id}' cannot specify chart or image fields.")

        elif self.type == "text":
            # Standalone text requires 'text'
            if not self.text or not self.text.strip():
                raise ValueError(f"Standalone text '{self.id}' requires non-empty 'text'.")
            if self.from_id is not None or self.to_id is not None or self.label is not None:
                raise ValueError(f"Text '{self.id}' cannot specify connector fields.")
            if self.chart_type is not None or self.series is not None or self.points is not None or self.asset_id is not None or self.value_fact_id is not None:
                raise ValueError(f"Text '{self.id}' cannot specify chart, image, or fact fields.")

        elif self.type == "chart":
            # Chart requires chart_type and direct data (series or points).
            if not self.chart_type:
                raise ValueError(f"Chart '{self.id}' requires 'chart_type' (e.g. 'trajectory_area', 'split_bar', 'multi_bar', 'stack').")
            if not self.series and not self.points:
                raise ValueError(f"Chart '{self.id}' requires directly authored 'series' or 'points'.")
            if self.from_id is not None or self.to_id is not None or self.label is not None:
                raise ValueError(f"Chart '{self.id}' cannot specify connector fields.")
            if self.asset_id is not None:
                raise ValueError(f"Chart '{self.id}' cannot specify 'asset_id'.")

        elif self.type == "image":
            # Image requires asset_request or asset_id
            if not self.asset_request and (not self.asset_id or not self.asset_id.strip()):
                raise ValueError(f"IMAGE_ASSET_REQUEST_MISSING: Image '{self.id}' requires 'asset_request' or 'asset_id'.")
            if self.from_id is not None or self.to_id is not None or self.label is not None:
                raise ValueError(f"Image '{self.id}' cannot specify connector fields.")
            if self.chart_type is not None or self.series is not None or self.points is not None:
                raise ValueError(f"Image '{self.id}' cannot specify chart fields.")
            if self.fact_id is not None or self.value_fact_id is not None:
                raise ValueError(f"Image '{self.id}' cannot specify fact fields.")
            if self.display_value is not None or self.numeric_value is not None:
                raise ValueError(f"Image '{self.id}' cannot specify number fields.")
            if self.character_style is not None or self.role is not None or self.pose is not None or self.facing is not None or self.emotion is not None:
                raise ValueError(f"Image '{self.id}' cannot specify character fields.")
            if self.text is not None:
                raise ValueError(f"Image '{self.id}' cannot specify text field.")
            if self.title is not None:
                raise ValueError(f"Image '{self.id}' cannot specify card field 'title'.")
            if self.subtitle is not None:
                raise ValueError(f"Image '{self.id}' cannot specify card field 'subtitle'.")
            if self.visual_state is not None:
                raise ValueError(f"Image '{self.id}' cannot specify card field 'visual_state'.")

        elif self.type == "stock_video":
            # 1. Layout must be strictly 'full_screen'
            if self.layout != "full_screen":
                raise ValueError(
                    f"STOCK_VIDEO_INVALID_LAYOUT: stock_video '{self.id}' layout must be 'full_screen', got '{self.layout}'."
                )

            # 2. Must contain asset_request or resolved asset_id
            if not self.asset_request and (not self.asset_id or not self.asset_id.strip()):
                raise ValueError(
                    f"VIDEO_ASSET_REQUEST_MISSING: stock_video '{self.id}' requires 'asset_request' or 'asset_id'."
                )
            if isinstance(self.asset_request, ImageAssetRequest):
                object.__setattr__(
                    self,
                    "asset_request",
                    VideoAssetRequest(
                        query=self.asset_request.query,
                        orientation=self.asset_request.orientation,
                        mood=self.asset_request.mood,
                        composition=self.asset_request.composition,
                        avoid=self.asset_request.avoid,
                    ),
                )

            # 3. Forbid raw external URLs or invalid asset IDs
            if self.asset_id:
                if self.asset_id.startswith("http://") or self.asset_id.startswith("https://"):
                    raise ValueError(f"stock_video '{self.id}' cannot specify external URL as asset_id.")

            # 4. Forbid card, number, chart, connector, character, relative fields
            if self.from_id is not None or self.to_id is not None or self.label is not None:
                raise ValueError(f"stock_video '{self.id}' cannot specify connector fields.")
            if self.chart_type is not None or self.series is not None or self.points is not None:
                raise ValueError(f"stock_video '{self.id}' cannot specify chart fields.")
            if self.fact_id is not None or self.value_fact_id is not None:
                raise ValueError(f"stock_video '{self.id}' cannot specify fact fields.")
            if self.display_value is not None or self.numeric_value is not None:
                raise ValueError(f"stock_video '{self.id}' cannot specify number fields.")
            if (
                self.character_style is not None
                or self.role is not None
                or self.pose is not None
                or self.facing is not None
                or self.emotion is not None
            ):
                raise ValueError(f"stock_video '{self.id}' cannot specify character fields.")
            if self.text is not None:
                raise ValueError(f"stock_video '{self.id}' cannot specify text field.")
            if self.title is not None:
                raise ValueError(f"stock_video '{self.id}' cannot specify card field 'title'.")
            if self.subtitle is not None:
                raise ValueError(f"stock_video '{self.id}' cannot specify card field 'subtitle'.")
            if self.visual_state is not None:
                raise ValueError(f"stock_video '{self.id}' cannot specify card field 'visual_state'.")
            if self.badge is not None:
                raise ValueError(f"stock_video '{self.id}' cannot specify card field 'badge'.")
            if self.border_color is not None:
                raise ValueError(f"stock_video '{self.id}' cannot specify image field 'border_color'.")
            if self.border_radius is not None:
                raise ValueError(f"stock_video '{self.id}' cannot specify image field 'border_radius'.")

        elif self.type == "connector":
            # Connector requires from_id and to_id
            if not self.from_id or not self.from_id.strip() or not self.to_id or not self.to_id.strip():
                raise ValueError(f"CONTINUOUS_STORY_CONTRACT_ERROR: Connector '{self.id}' requires valid from_id and to_id.")
            if self.from_id == self.to_id:
                raise ValueError(f"CONTINUOUS_STORY_CONTRACT_ERROR: Connector '{self.id}' cannot connect element to itself ('{self.from_id}').")
            # Forbid card, fact, chart, number, or visual-state fields on connector
            if self.visual_state is not None:
                raise ValueError(f"CONTINUOUS_STORY_CONTRACT_ERROR: Connector '{self.id}' cannot specify card field 'visual_state'.")
            if self.badge is not None:
                raise ValueError(f"CONTINUOUS_STORY_CONTRACT_ERROR: Connector '{self.id}' cannot specify card field 'badge'.")
            if self.value_fact_id is not None or self.fact_id is not None:
                raise ValueError(f"CONTINUOUS_STORY_CONTRACT_ERROR: Connector '{self.id}' cannot specify fact fields.")
            if self.title is not None:
                raise ValueError(f"CONTINUOUS_STORY_CONTRACT_ERROR: Connector '{self.id}' cannot specify card field 'title'.")
            if self.subtitle is not None:
                raise ValueError(f"CONTINUOUS_STORY_CONTRACT_ERROR: Connector '{self.id}' cannot specify card field 'subtitle'.")
            if self.display_value is not None or self.numeric_value is not None:
                raise ValueError(f"CONTINUOUS_STORY_CONTRACT_ERROR: Connector '{self.id}' cannot specify number fields.")
            if self.chart_type is not None or self.series is not None or self.points is not None or self.asset_id is not None or self.text is not None:
                raise ValueError(f"CONTINUOUS_STORY_CONTRACT_ERROR: Connector '{self.id}' cannot specify chart, image, or text fields.")

        elif self.type == "character":
            if not self.character_style or self.character_style != "futuristic_stick":
                raise ValueError(f"Character '{self.id}' requires 'character_style' to be 'futuristic_stick'.")
            if not self.role or not self.role.strip():
                raise ValueError(f"Character '{self.id}' requires non-empty 'role'.")
            if not self.pose or self.pose not in VALID_CHARACTER_POSES:
                raise ValueError(f"Character '{self.id}' requires valid 'pose' ({', '.join(VALID_CHARACTER_POSES)}).")
            if not self.facing or self.facing not in VALID_CHARACTER_FACINGS:
                raise ValueError(f"Character '{self.id}' requires valid 'facing' ({', '.join(VALID_CHARACTER_FACINGS)}).")
            if self.emotion is not None and self.emotion not in VALID_CHARACTER_EMOTIONS:
                raise ValueError(f"Character '{self.id}' specifies invalid 'emotion' ('{self.emotion}').")
            if self.emotion is None:
                self.emotion = "neutral"

            # Strictly forbid non-character fields
            leaked_fields = []
            if self.title is not None:
                leaked_fields.append("title")
            if self.subtitle is not None:
                leaked_fields.append("subtitle")
            if self.display_value is not None:
                leaked_fields.append("display_value")
            if self.numeric_value is not None:
                leaked_fields.append("numeric_value")
            if self.value_fact_id is not None:
                leaked_fields.append("value_fact_id")
            if self.fact_id is not None:
                leaked_fields.append("fact_id")
            if self.chart_type is not None:
                leaked_fields.append("chart_type")
            if self.series is not None:
                leaked_fields.append("series")
            if self.points is not None:
                leaked_fields.append("points")
            if self.asset_id is not None:
                leaked_fields.append("asset_id")
            if self.from_id is not None:
                leaked_fields.append("from_id")
            if self.to_id is not None:
                leaked_fields.append("to_id")
            if self.text is not None:
                leaked_fields.append("text")
            if leaked_fields:
                raise ValueError(
                    f"Character '{self.id}' cannot specify non-character fields: {', '.join(leaked_fields)}."
                )

        elif self.type == "scale":
            has_label = bool(
                (self.left_title and self.left_title.strip())
                or (self.right_title and self.right_title.strip())
                or (self.title and self.title.strip())
            )
            if not has_label:
                raise ValueError(f"Scale '{self.id}' requires at least 'left_title', 'right_title', or 'title'.")
            if self.from_id is not None or self.to_id is not None or self.label is not None:
                raise ValueError(f"Scale '{self.id}' cannot specify connector fields.")
            if self.chart_type is not None or self.series is not None or self.points is not None:
                raise ValueError(f"Scale '{self.id}' cannot specify chart fields.")
            if self.asset_id is not None or self.asset_request is not None:
                raise ValueError(f"Scale '{self.id}' cannot specify media asset fields.")

        elif self.type == "money_stack":
            has_val = bool(
                (self.total_display_value and self.total_display_value.strip())
                or (self.comparison_left_value and self.comparison_left_value.strip())
                or (self.display_value and str(self.display_value).strip())
                or (self.title and self.title.strip())
            )
            if not has_val:
                raise ValueError(f"MoneyStack '{self.id}' requires 'total_display_value', 'comparison_left_value', or 'display_value'.")
            if self.from_id is not None or self.to_id is not None or self.label is not None:
                raise ValueError(f"MoneyStack '{self.id}' cannot specify connector fields.")
            if self.chart_type is not None or self.series is not None or self.points is not None:
                raise ValueError(f"MoneyStack '{self.id}' cannot specify chart fields.")
            if self.asset_id is not None or self.asset_request is not None:
                raise ValueError(f"MoneyStack '{self.id}' cannot specify media asset fields.")

        elif self.type == "document":
            has_title = bool(
                (self.doc_title and self.doc_title.strip())
                or (self.title and self.title.strip())
            )
            if not has_title:
                raise ValueError(f"Document '{self.id}' requires 'doc_title' or 'title'.")
            if not self.doc_body or not self.doc_body.strip():
                raise ValueError(f"Document '{self.id}' requires non-empty 'doc_body' text excerpt.")
            if self.from_id is not None or self.to_id is not None or self.label is not None:
                raise ValueError(f"Document '{self.id}' cannot specify connector fields.")
            if self.chart_type is not None or self.series is not None or self.points is not None:
                raise ValueError(f"Document '{self.id}' cannot specify chart fields.")
            if self.asset_id is not None or self.asset_request is not None:
                raise ValueError(f"Document '{self.id}' cannot specify media asset fields.")

        elif self.type == "waterfall":
            if not self.initial_label or not self.initial_label.strip():
                raise ValueError(f"Waterfall '{self.id}' requires 'initial_label'.")
            if not self.initial_display_value or not self.initial_display_value.strip():
                raise ValueError(f"Waterfall '{self.id}' requires 'initial_display_value'.")
            if not self.steps:
                raise ValueError(f"Waterfall '{self.id}' requires at least one step in 'steps'.")
            if not self.final_label or not self.final_label.strip():
                raise ValueError(f"Waterfall '{self.id}' requires 'final_label'.")
            if not self.final_display_value or not self.final_display_value.strip():
                raise ValueError(f"Waterfall '{self.id}' requires 'final_display_value'.")
            if self.from_id is not None or self.to_id is not None or self.label is not None:
                raise ValueError(f"Waterfall '{self.id}' cannot specify connector fields.")
            if self.chart_type is not None or self.series is not None or self.points is not None:
                raise ValueError(f"Waterfall '{self.id}' cannot specify chart fields.")

        elif self.type == "capital_flow":
            if not self.source_label or not self.source_label.strip():
                raise ValueError(f"CapitalFlow '{self.id}' requires 'source_label'.")
            if not self.target_label or not self.target_label.strip():
                raise ValueError(f"CapitalFlow '{self.id}' requires 'target_label'.")
            if not self.flow_display_value or not self.flow_display_value.strip():
                raise ValueError(f"CapitalFlow '{self.id}' requires 'flow_display_value'.")
            if self.from_id is not None or self.to_id is not None or self.label is not None:
                raise ValueError(f"CapitalFlow '{self.id}' cannot specify connector fields.")
            if self.chart_type is not None or self.series is not None or self.points is not None:
                raise ValueError(f"CapitalFlow '{self.id}' cannot specify chart fields.")

        # Forbid character fields on other element types
        if self.type != "character":
            if (
                self.character_style is not None
                or self.role is not None
                or self.pose is not None
                or self.facing is not None
                or self.emotion is not None
            ):
                raise ValueError(
                    f"{self.type.title()} '{self.id}' cannot specify character fields ('character_style', 'role', 'pose', 'facing', 'emotion')."
                )

        # Forbid scale fields on other element types
        if self.type != "scale":
            if (
                self.left_title is not None
                or self.left_display_value is not None
                or self.left_numeric_value is not None
                or self.left_badge is not None
                or self.right_title is not None
                or self.right_display_value is not None
                or self.right_numeric_value is not None
                or self.right_badge is not None
                or self.tilt_direction is not None
            ):
                raise ValueError(
                    f"{self.type.title()} '{self.id}' cannot specify scale fields ('left_title', 'right_title', 'tilt_direction', etc.)."
                )

        # Forbid money_stack fields on other element types
        if self.type != "money_stack":
            if (
                self.stack_mode is not None
                or self.unit_label is not None
                or self.unit_value is not None
                or self.total_display_value is not None
                or self.total_numeric_value is not None
                or self.comparison_left_label is not None
                or self.comparison_left_value is not None
                or self.comparison_right_label is not None
                or self.comparison_right_value is not None
                or self.show_human_scale is not None
            ):
                raise ValueError(
                    f"{self.type.title()} '{self.id}' cannot specify money_stack fields ('unit_label', 'total_display_value', etc.)."
                )

        # Forbid document fields on other element types
        if self.type != "document":
            if (
                self.doc_title is not None
                or self.doc_reference is not None
                or self.doc_body is not None
                or self.highlight_phrase is not None
                or self.watermark is not None
            ):
                raise ValueError(
                    f"{self.type.title()} '{self.id}' cannot specify document fields ('doc_title', 'doc_body', 'highlight_phrase', etc.)."
                )

        # Forbid waterfall fields on other element types
        if self.type != "waterfall":
            if (
                self.initial_label is not None
                or self.initial_value is not None
                or self.initial_display_value is not None
                or self.steps is not None
                or self.final_label is not None
                or self.final_value is not None
                or self.final_display_value is not None
            ):
                raise ValueError(
                    f"{self.type.title()} '{self.id}' cannot specify waterfall fields ('initial_label', 'steps', 'final_label', etc.)."
                )

        # Forbid capital_flow fields on other element types
        if self.type != "capital_flow":
            if (
                self.source_label is not None
                or self.source_sublabel is not None
                or self.target_label is not None
                or self.target_sublabel is not None
                or self.flow_label is not None
                or self.flow_display_value is not None
                or self.flow_direction is not None
            ):
                raise ValueError(
                    f"{self.type.title()} '{self.id}' cannot specify capital_flow fields ('source_label', 'target_label', 'flow_display_value', etc.)."
                )

        return self


class StoryEventDraft(StrictBaseModel):
    """
    A choreography action declared by the AI.
    """
    action: Literal[
        "enter",
        "move",
        "connect",
        "transform_number",
        "transform_text",
        "highlight",
        "change_visual_state",
        "exit",
        "change_pose",
        "stamp",
    ] = Field(description="The motion behavior to trigger.")
    target_id: str = Field(
        validation_alias=AliasChoices("target_id", "target"),
        description="The ID of the visual element this action targets (or 'canvas' for canvas-level stamps)."
    )
    anchor: str = Field(description="The exact spoken phrase in narration where this action occurs.")

    @field_validator("anchor", mode="before")
    @classmethod
    def _coerce_anchor(cls, v: Any) -> str:
        if isinstance(v, list):
            return " ".join(str(item) for item in v)
        return str(v)
    to: ZoneName | None = Field(
        default=None,
        validation_alias=AliasChoices("to", "position", "destination", "layout"),
        description="Target destination zone for 'move' action (e.g. 'split_left', 'split_right', 'center'). Required for move."
    )
    to_display_value: str | None = Field(
        default=None,
        validation_alias=AliasChoices("to_display_value", "toDisplayValue", "to_value_display"),
        description="New formatted display string for 'transform_number' action (e.g. '₹5,000', '₹0', '3 Years')."
    )
    to_numeric_value: float | None = Field(
        default=None,
        validation_alias=AliasChoices("to_numeric_value", "toNumericValue", "to_value"),
        description="New numeric float value for 'transform_number' action."
    )
    to_fact_id: str | None = Field(
        default=None,
        description="Required approved fact ID for the new numeric value in a transform_number action."
    )
    to_text: str | None = Field(
        default=None,
        description="New text for 'transform_text' action (on text or card subtitle)."
    )
    from_id: str | None = Field(
        default=None,
        validation_alias=AliasChoices("from_id", "fromId"),
        description="Optional source card ID if action is 'connect'."
    )
    to_id: str | None = Field(
        default=None,
        validation_alias=AliasChoices("to_id", "toId"),
        description="Optional target card ID if action is 'connect'."
    )
    state: VisualStateKind | None = Field(
        default=None,
        validation_alias=AliasChoices("state", "visual_state", "visualState", "to_state"),
        description="Visual state for 'change_visual_state' action ('warning', 'danger', 'dimmed', 'success', 'normal')."
    )
    badge: str | None = Field(
        default=None,
        description="Optional visual badge label displayed on the card (e.g. '+2.0% HIKE', 'BURDEN SURGE')."
    )
    style: Literal["fade", "fade_slide_up", "pop", "cut"] | None = Field(
        default=None,
        description="Entrance animation style for 'enter' action ('fade', 'fade_slide_up', 'pop', 'cut')."
    )
    direction: Literal["left", "right", "up", "down", "fade", "cut"] | None = Field(
        default=None,
        description="Exit animation direction for 'exit' action ('left', 'right', 'up', 'down', 'fade', 'cut')."
    )
    pose: CharacterPose | None = Field(
        default=None,
        description="Target pose for 'change_pose' action ('idle', 'walk', 'point', 'think', 'worried', 'celebrate')."
    )
    emotion: CharacterEmotion | None = Field(
        default=None,
        description="Optional target emotion for 'change_pose' action ('neutral', 'focused', 'concerned', 'surprised', 'happy')."
    )
    facing: CharacterFacing | None = Field(
        default=None,
        description="Optional target facing for 'change_pose' action ('left', 'right')."
    )
    stamp_text: str | None = Field(
        default=None,
        validation_alias=AliasChoices("stamp_text", "stampText", "text_stamp"),
        description="Text displayed inside the rubber impact stamp for 'stamp' action (e.g. 'OVERVALUED', 'PRICED FOR PERFECTION')."
    )
    stamp_tone: Literal["verdict", "warning", "classified", "amount"] | None = Field(
        default="verdict",
        validation_alias=AliasChoices("stamp_tone", "stampTone", "tone"),
        description="Visual tone for the rubber stamp: 'verdict' (crimson), 'warning' (amber), 'classified' (slate), 'amount' (green)."
    )
    stamp_color: str | None = Field(
        default=None,
        description="Optional custom hex color for the rubber stamp."
    )
    rotation_deg: float | None = Field(
        default=None,
        validation_alias=AliasChoices("rotation_deg", "rotationDeg", "angle"),
        description="Resting rotation angle in degrees for the rubber stamp (default -6.5)."
    )
    shake: bool = Field(
        default=True,
        description="Whether camera receives a transient physical shake on stamp impact."
    )

    @model_validator(mode="after")
    def validate_action_rules(self) -> StoryEventDraft:
        # 1. Non-empty target_id and anchor
        if not self.target_id or not self.target_id.strip():
            raise ValueError("Event 'target_id' must be a non-empty string.")
        if not self.anchor or not self.anchor.strip():
            raise ValueError(f"Event '{self.action}' on '{self.target_id}' requires a non-empty spoken 'anchor'.")

        # 2. 'move' requires 'to'
        if self.action == "move" and self.to is None:
            raise ValueError(f"Action 'move' targeting '{self.target_id}' requires 'to' destination zone.")

        # 3. 'transform_number' requires both 'to_display_value' and 'to_numeric_value'
        if self.action == "transform_number":
            if not self.to_display_value or not self.to_display_value.strip():
                raise ValueError(f"Action 'transform_number' targeting '{self.target_id}' requires 'to_display_value'.")
            if self.to_numeric_value is None:
                raise ValueError(f"Action 'transform_number' targeting '{self.target_id}' requires 'to_numeric_value'.")

        # 4. 'change_visual_state' requires 'state'
        if self.action == "change_visual_state" and not self.state:
            raise ValueError(f"Action 'change_visual_state' on '{self.target_id}' requires 'state' (e.g. 'warning', 'danger', 'dimmed').")

        # 5. Only 'change_visual_state' may specify 'state' or 'badge'
        if self.action != "change_visual_state":
            if self.state is not None:
                raise ValueError(f"Action '{self.action}' on '{self.target_id}' cannot specify 'state' (only for 'change_visual_state').")
            if self.badge is not None:
                raise ValueError(f"Action '{self.action}' on '{self.target_id}' cannot specify 'badge' (only for 'change_visual_state').")

        # 6. Only 'connect' may specify from_id or to_id
        if self.action != "connect":
            if self.from_id is not None or self.to_id is not None:
                raise ValueError(f"Action '{self.action}' cannot specify 'from_id' or 'to_id' (only allowed for 'connect').")

        # 7. 'exit.direction' optional with deterministic default 'fade', non-exit forbids 'direction'
        if self.action == "exit":
            if self.direction is None:
                self.direction = "fade"
        elif self.direction is not None:
            raise ValueError(f"Action '{self.action}' on '{self.target_id}' cannot specify 'direction' (only for 'exit').")

        # 8. 'change_pose' requires valid 'pose'
        if self.action == "change_pose":
            if not self.pose or self.pose not in VALID_CHARACTER_POSES:
                raise ValueError(f"Action 'change_pose' on '{self.target_id}' requires valid 'pose' ({', '.join(VALID_CHARACTER_POSES)}).")
            if (
                self.to is not None
                or self.to_display_value is not None
                or self.to_numeric_value is not None
                or self.to_text is not None
                or self.to_fact_id is not None
            ):
                raise ValueError(f"Action 'change_pose' on '{self.target_id}' cannot specify move, transform, or fact fields.")
            if self.direction is not None or self.from_id is not None or self.to_id is not None:
                raise ValueError(f"Action 'change_pose' on '{self.target_id}' cannot specify direction or connector fields.")
            if self.emotion is not None and self.emotion not in VALID_CHARACTER_EMOTIONS:
                raise ValueError(f"Action 'change_pose' on '{self.target_id}' specifies invalid 'emotion' ('{self.emotion}').")
            if self.facing is not None and self.facing not in VALID_CHARACTER_FACINGS:
                raise ValueError(f"Action 'change_pose' on '{self.target_id}' specifies invalid 'facing' ('{self.facing}').")
        else:
            if self.pose is not None:
                raise ValueError(f"Action '{self.action}' on '{self.target_id}' cannot specify 'pose' (only for 'change_pose').")
            if self.emotion is not None:
                raise ValueError(f"Action '{self.action}' on '{self.target_id}' cannot specify 'emotion' (only for 'change_pose').")
            if self.facing is not None:
                raise ValueError(f"Action '{self.action}' on '{self.target_id}' cannot specify 'facing' (only for 'change_pose').")

        # 9. 'stamp' requires non-empty 'stamp_text'
        if self.action == "stamp":
            if not self.stamp_text or not self.stamp_text.strip():
                raise ValueError(f"Action 'stamp' targeting '{self.target_id}' requires non-empty 'stamp_text'.")
        else:
            if self.stamp_text is not None:
                raise ValueError(f"Action '{self.action}' on '{self.target_id}' cannot specify 'stamp_text' (only for 'stamp').")

        return self


class ContinuousStoryDraft(StrictBaseModel):
    """
    The complete AI-authored story choreography draft using atomic visual elements.
    """
    story_id: str = Field(description="Identifier of the story (e.g. 'loan_rate_hike').")
    atmosphere: AtmospherePreset | None = Field(
        default="paper_clean",
        description="The aesthetic material atmosphere preset for the canvas ('paper_clean', 'blueprint', 'vault', 'newsroom')."
    )
    objects: list[StoryObjectDraft] = Field(
        description="Independent, atomic visual elements that participate in the continuous scene."
    )
    events: list[StoryEventDraft] = Field(
        validation_alias=AliasChoices("events", "timeline"),
        description="Sequential list of choreographic events bound to speech anchors."
    )

    @model_validator(mode="after")
    def validate_story_integrity(self) -> ContinuousStoryDraft:
        if not self.story_id or not self.story_id.strip():
            raise ValueError("story_id must be a non-empty string.")
        if not self.objects:
            raise ValueError("ContinuousStoryDraft must contain at least one object.")
        if not self.events:
            raise ValueError("ContinuousStoryDraft must contain at least one event.")

        # Validate connector endpoints at story draft level
        obj_map = {obj.id: obj for obj in self.objects}
        for obj in self.objects:
            if obj.type == "connector":
                if not obj.from_id or obj.from_id not in obj_map:
                    raise ValueError(
                        f"CONTINUOUS_STORY_CONTRACT_ERROR: Connector '{obj.id}' requires valid from_id that exists in declared objects (found '{obj.from_id}')."
                    )
                if not obj.to_id or obj.to_id not in obj_map:
                    raise ValueError(
                        f"CONTINUOUS_STORY_CONTRACT_ERROR: Connector '{obj.id}' requires valid to_id that exists in declared objects (found '{obj.to_id}')."
                    )
                if obj_map[obj.from_id].type == "connector":
                    raise ValueError(
                        f"CONTINUOUS_STORY_CONTRACT_ERROR: Connector '{obj.id}' source 'from_id' ('{obj.from_id}') cannot be another connector."
                    )
                if obj_map[obj.to_id].type == "connector":
                    raise ValueError(
                        f"CONTINUOUS_STORY_CONTRACT_ERROR: Connector '{obj.id}' target 'to_id' ('{obj.to_id}') cannot be another connector."
                    )
                if obj.from_id == obj.to_id:
                    raise ValueError(
                        f"CONTINUOUS_STORY_CONTRACT_ERROR: Connector '{obj.id}' cannot connect element to itself ('{obj.from_id}')."
                    )
        return self

    @classmethod
    def model_json_schema(cls, *args: Any, **kwargs: Any) -> dict[str, Any]:
        """Returns the primary grammar contract JSON schema enforcing action-specific and object-specific required fields."""
        return build_continuous_story_contract_schema()


def build_continuous_story_contract_schema() -> dict[str, Any]:
    """Generates the strict, action-and-object contract JSON schema for Gemini constrained decoding."""
    zone_enum = [
        "center",
        "split_left",
        "split_right",
        "full_screen",
        "full_bottom",
    ]
    state_enum = ["normal", "dimmed", "warning", "danger", "success", "stamped", "eroded"]
    chart_enum = ["trajectory_area", "split_bar", "multi_bar", "stack"]
    direction_enum = ["left", "right", "up", "down", "fade", "cut"]
    character_style_enum = ["futuristic_stick"]
    pose_enum = ["idle", "walk", "point", "think", "worried", "celebrate"]
    emotion_enum = ["neutral", "focused", "concerned", "surprised", "happy"]
    facing_enum = ["left", "right"]

    return {
        "type": "object",
        "properties": {
            "story_id": {
                "type": "string",
                "description": "Identifier of the story (e.g. 'loan_rate_hike')."
            },
            "objects": {
                "type": "array",
                "description": "Independent, atomic visual elements that participate in the continuous scene.",
                "items": {
                    "anyOf": [
                        {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string", "description": "Unique identifier for the card element."},
                                "type": {"type": "string", "enum": ["card"]},
                                "layout": {"type": "string", "enum": zone_enum, "description": "One of the 12 spatial zone names."},
                                "purpose": {"type": "string", "description": "Editorial purpose of this visual element."},
                                "title": {"type": "string", "description": "MANDATORY card header title."},
                                "display_value": {"type": "string", "description": "Direct human-friendly display value (e.g. '₹50 Lakhs', '8.5%', '₹1.38 Cr', '₹5,000')."},
                                "numeric_value": {"type": "number", "description": "Raw numeric value for animated counters and math validation."},
                                "value_fact_id": {"type": "string", "description": "Required for numeric cards: approved fact identity used for verification and provenance."},
                                "subtitle": {"type": "string", "description": "Card explanatory subtitle authored directly by AI (concise 3-6 words)."},
                                "badge": {"type": "string", "description": "Status badge text."},
                                "visual_state": {"type": "string", "enum": state_enum, "description": "Visual state."}
                            },
                            "required": ["id", "type", "layout", "title", "display_value", "subtitle"]
                        },
                        {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string", "description": "Unique identifier for the number element."},
                                "type": {"type": "string", "enum": ["number"]},
                                "layout": {"type": "string", "enum": zone_enum, "description": "One of the 12 spatial zone names."},
                                "purpose": {"type": "string", "description": "Editorial purpose."},
                                "display_value": {"type": "string", "description": "Direct formatted number string (e.g. '₹1.38 Cr', '8.5%')."},
                                "numeric_value": {"type": "number", "description": "Numeric float value."},
                                "fact_id": {"type": "string", "description": "Optional reference to approved fact ID."}
                            },
                            "required": ["id", "type", "layout", "display_value"]
                        },
                        {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string", "description": "Unique identifier for the text element."},
                                "type": {"type": "string", "enum": ["text"]},
                                "layout": {"type": "string", "enum": zone_enum, "description": "One of the 12 spatial zone names."},
                                "purpose": {"type": "string", "description": "Editorial purpose."},
                                "text": {"type": "string", "description": "Display text content."}
                            },
                            "required": ["id", "type", "layout", "text"]
                        },
                        {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string", "description": "Unique identifier for the chart element."},
                                "type": {"type": "string", "enum": ["chart"]},
                                "layout": {"type": "string", "enum": zone_enum, "description": "One of the 12 spatial zone names."},
                                "purpose": {"type": "string", "description": "Editorial purpose."},
                                "chart_type": {"type": "string", "enum": chart_enum, "description": "Chart visualization subtype ('trajectory_area', 'split_bar', 'multi_bar', 'stack')."},
                                "title": {"type": "string", "description": "Chart title."},
                                "subtitle": {"type": "string", "description": "Chart subtitle."},
                                "series": {
                                    "type": "array",
                                    "description": "Optional list of chart data series: [{id, name, color, points: [{xLabel, yValue}]}].",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "id": {"type": "string"},
                                            "name": {"type": "string"},
                                            "color": {"type": "string"},
                                            "points": {
                                                "type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "xLabel": {"type": "string"},
                                                        "yValue": {"type": "number"}
                                                    },
                                                    "required": ["xLabel", "yValue"]
                                                }
                                            }
                                        },
                                        "required": ["name", "points"]
                                    }
                                },
                                "points": {
                                    "type": "array",
                                    "description": "Optional direct chart data points for simple trajectory: [{xLabel, yValue}].",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "xLabel": {"type": "string"},
                                            "yValue": {"type": "number"}
                                        },
                                        "required": ["xLabel", "yValue"]
                                    }
                                },
                                "fact_id": {"type": "string", "description": "Optional reference to approved fact ID."}
                            },
                            "required": ["id", "type", "layout", "chart_type", "points"]
                        },
                        {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string", "description": "Unique identifier for the image element."},
                                "type": {"type": "string", "enum": ["image"]},
                                "layout": {"type": "string", "enum": zone_enum, "description": "One of the 12 spatial zone names."},
                                "purpose": {"type": "string", "description": "Editorial purpose."},
                                "asset_request": {
                                    "type": "object",
                                    "description": "Visual specification describing the real-world image to resolve.",
                                    "properties": {
                                        "query": {"type": "string", "description": "MANDATORY search query describing the real-world image (e.g. 'modern bank exterior, no visible logo')."},
                                        "orientation": {"type": "string", "enum": ["landscape", "portrait", "square"], "description": "Image orientation."},
                                        "style": {"type": "string", "enum": ["photo", "illustration"], "description": "Visual style."},
                                        "composition": {"type": "string", "description": "Short visual composition instruction."},
                                        "mood": {"type": "string", "description": "Optional visual mood."},
                                        "avoid": {
                                            "type": "array",
                                            "items": {"type": "string"},
                                            "description": "Optional list of unwanted visual properties."
                                        }
                                    },
                                    "required": ["query"]
                                },
                                "alt": {"type": "string", "description": "Alternative text description for accessibility."},
                                "caption": {"type": "string", "description": "Optional caption text shown beneath image."},
                                "badge": {"type": "string", "description": "Optional badge text overlay on image."},
                                "fit": {"type": "string", "enum": ["cover", "contain"], "description": "Image fit style."},
                                "border_color": {"type": "string", "description": "Optional border hex color."},
                                "border_radius": {"type": "number", "description": "Optional border radius in pixels (default: 16)."},
                                "asset_id": {"type": "string", "description": "Asset reference identifier (set after resolution)."}
                            },
                            "required": ["id", "type", "layout", "asset_request"]
                        },
                        {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string", "description": "Unique identifier for the stock video element."},
                                "type": {"type": "string", "enum": ["stock_video"]},
                                "layout": {"type": "string", "enum": ["full_screen"], "description": "Layout must be strictly 'full_screen'."},
                                "purpose": {"type": "string", "description": "Editorial documentary/B-roll purpose."},
                                "asset_request": {
                                    "type": "object",
                                    "description": "Visual specification describing the real-world documentary/B-roll video to resolve.",
                                    "properties": {
                                        "query": {"type": "string", "description": "MANDATORY search query describing the real-world footage (e.g. 'commercial bank exterior with people entering')."},
                                        "orientation": {"type": "string", "enum": ["landscape", "portrait", "square"], "description": "Video orientation."},
                                        "mood": {"type": "string", "description": "Optional visual mood."},
                                        "composition": {"type": "string", "description": "Optional visual composition instruction."},
                                        "avoid": {
                                            "type": "array",
                                            "items": {"type": "string"},
                                            "description": "Optional list of unwanted visual properties."
                                        },
                                        "minimum_duration_seconds": {"type": "number", "description": "Optional minimum duration in seconds."}
                                    },
                                    "required": ["query"]
                                },
                                "alt": {"type": "string", "description": "Alternative text description for accessibility."},
                                "caption": {"type": "string", "description": "Optional caption text shown with video."},
                                "fit": {"type": "string", "enum": ["cover", "contain"], "description": "Video fit style (default: 'cover')."},
                                "overlay_tint": {"type": "string", "description": "Optional dark overlay tint hex/rgba string."},
                                "asset_id": {"type": "string", "description": "Asset reference identifier (set after resolution)."}
                            },
                            "required": ["id", "type", "layout", "asset_request"]
                        },
                        {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string", "description": "Unique identifier for the connector element."},
                                "type": {"type": "string", "enum": ["connector"]},
                                "layout": {"type": "string", "enum": zone_enum, "description": "One of the 12 spatial zone names."},
                                "purpose": {"type": "string", "description": "Editorial purpose."},
                                "from_id": {"type": "string", "description": "MANDATORY source card ID."},
                                "to_id": {"type": "string", "description": "MANDATORY target card ID."},
                                "label": {"type": "string", "description": "Optional label on the connector arrow."}
                            },
                            "required": ["id", "type", "layout", "from_id", "to_id"]
                        },
                        {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string", "description": "Unique identifier for the character element."},
                                "type": {"type": "string", "enum": ["character"]},
                                "layout": {"type": "string", "enum": zone_enum, "description": "One of the 12 spatial zone names."},
                                "purpose": {"type": "string", "description": "Editorial purpose of this visual element."},
                                "character_style": {"type": "string", "enum": character_style_enum, "description": "Character style ('futuristic_stick')."},
                                "role": {"type": "string", "description": "Story role of the character (e.g. 'salaried employee', 'home buyer', 'investor')."},
                                "label": {"type": "string", "description": "Optional human-readable label."},
                                "pose": {"type": "string", "enum": pose_enum, "description": "Initial character pose ('idle', 'walk', 'point', 'think', 'worried', 'celebrate')."},
                                "emotion": {"type": "string", "enum": emotion_enum, "description": "Initial character emotion ('neutral', 'focused', 'concerned', 'surprised', 'happy')."},
                                "facing": {"type": "string", "enum": facing_enum, "description": "Facing direction ('left' or 'right')."}
                            },
                            "required": ["id", "type", "layout", "character_style", "role", "pose", "facing"]
                        },
                        {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string", "description": "Unique identifier for the scale element."},
                                "type": {"type": "string", "enum": ["scale"]},
                                "layout": {"type": "string", "enum": zone_enum, "description": "Spatial zone name ('center', 'split_left', or 'split_right')."},
                                "purpose": {"type": "string", "description": "Editorial purpose of the balance scale visualizer."},
                                "title": {"type": "string", "description": "Optional overall headline title for the balance scale."},
                                "left_title": {"type": "string", "description": "Title label for the left pan force (e.g. 'Monthly Cash Flow')."},
                                "left_display_value": {"type": "string", "description": "Display value on left pan (e.g. '₹1.2 Lakh')."},
                                "left_numeric_value": {"type": "number", "description": "Numeric weight value for left pan."},
                                "left_badge": {"type": "string", "description": "Status badge for left side (e.g. 'HEALTHY')."},
                                "right_title": {"type": "string", "description": "Title label for the right pan force (e.g. 'Total EMI Burden')."},
                                "right_display_value": {"type": "string", "description": "Display value on right pan (e.g. '₹2.8 Lakh')."},
                                "right_numeric_value": {"type": "number", "description": "Numeric weight value for right pan."},
                                "right_badge": {"type": "string", "description": "Status badge for right side (e.g. 'DANGER // DEFICIT')."},
                                "tilt_direction": {"type": "string", "enum": ["left", "right", "balanced"], "description": "Which side is heavier/tipping downwards ('left', 'right', or 'balanced')."},
                                "visual_state": {"type": "string", "enum": state_enum, "description": "Visual state."}
                            },
                            "required": ["id", "type", "layout", "left_title", "right_title"]
                        },
                        {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string", "description": "Unique identifier for the money_stack element."},
                                "type": {"type": "string", "enum": ["money_stack"]},
                                "layout": {"type": "string", "enum": zone_enum, "description": "Spatial zone name ('center', 'split_left', or 'split_right')."},
                                "purpose": {"type": "string", "description": "Editorial purpose of this tangible money stack visualizer."},
                                "title": {"type": "string", "description": "Optional title for the stack visualizer."},
                                "stack_mode": {"type": "string", "enum": ["single_tower", "comparison"], "description": "Visualization mode: 'single_tower' (monumental scale) or 'comparison' (wealth divide)."},
                                "unit_label": {"type": "string", "description": "Legend label per brick (e.g. '₹1,000 Cr per brick')."},
                                "unit_value": {"type": "number", "description": "Numeric denomination per brick."},
                                "total_display_value": {"type": "string", "description": "Formatted total value for single_tower mode (e.g. '₹25,000 Crore')."},
                                "total_numeric_value": {"type": "number", "description": "Raw numeric total value for single_tower mode."},
                                "comparison_left_label": {"type": "string", "description": "Label for left stack in comparison mode (e.g. 'Monthly Retail Salary')."},
                                "comparison_left_value": {"type": "string", "description": "Formatted display value for left stack (e.g. '₹35,000')."},
                                "comparison_right_label": {"type": "string", "description": "Label for right stack in comparison mode (e.g. 'Top 1% Daily Gain')."},
                                "comparison_right_value": {"type": "string", "description": "Formatted display value for right stack (e.g. '₹4.8 Crore')."},
                                "show_human_scale": {"type": "boolean", "description": "Whether to render stick figure silhouette next to the stack for human grounding."},
                                "badge": {"type": "string", "description": "Status badge text overlay."},
                                "visual_state": {"type": "string", "enum": state_enum, "description": "Visual state."}
                            },
                            "required": ["id", "type", "layout"]
                        },
                        {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string", "description": "Unique identifier for the document element."},
                                "type": {"type": "string", "enum": ["document"]},
                                "layout": {"type": "string", "enum": zone_enum, "description": "Spatial zone name ('center', 'split_left', or 'split_right')."},
                                "purpose": {"type": "string", "description": "Editorial purpose of this investigative proof document."},
                                "doc_title": {"type": "string", "description": "Headline document title (e.g. 'SEBI CIRCULAR // OCT 2024', 'RESERVE BANK OF INDIA')."},
                                "title": {"type": "string", "description": "Fallback document title."},
                                "doc_reference": {"type": "string", "description": "Reference / circular serial number (e.g. 'CIRC-8924/2024', 'NOTIFICATION NO. 45')."},
                                "doc_body": {"type": "string", "description": "MANDATORY verbatim or summarized legal/regulatory text excerpt inside the proof document."},
                                "highlight_phrase": {"type": "string", "description": "Key phrase within doc_body that receives an animated yellow highlighter mark."},
                                "watermark": {"type": "string", "description": "Optional background security watermark (e.g. 'OFFICIAL', 'CONFIDENTIAL', 'CIRCULAR')."},
                                "stamp_text": {"type": "string", "description": "Optional rubber stamp overlay text (e.g. 'VERIFIED', 'MANDATORY', 'WARNING', 'APPROVED')."},
                                "visual_state": {"type": "string", "enum": state_enum, "description": "Visual state."}
                            },
                            "required": ["id", "type", "layout", "doc_body"]
                        },
                        {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string", "description": "Unique identifier for the waterfall element."},
                                "type": {"type": "string", "enum": ["waterfall"]},
                                "layout": {"type": "string", "enum": zone_enum, "description": "Spatial zone name ('center', 'split_left', or 'split_right')."},
                                "purpose": {"type": "string", "description": "Editorial purpose of the financial cash flow waterfall funnel."},
                                "title": {"type": "string", "description": "Optional title for the waterfall funnel."},
                                "initial_label": {"type": "string", "description": "Starting capital or gross revenue label (e.g. 'Gross Corporate Revenue', 'Monthly Salary')."},
                                "initial_display_value": {"type": "string", "description": "Starting formatted string (e.g. '₹1,00,000', '₹10,000 Cr')."},
                                "initial_value": {"type": "number", "description": "Starting numeric value."},
                                "steps": {
                                    "type": "array",
                                    "description": "List of cascading deduction/addition steps in the waterfall.",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "label": {"type": "string", "description": "Step name (e.g. 'Operating Expenses', 'Direct Taxes', 'Loan EMI')."},
                                            "display_value": {"type": "string", "description": "Formatted human display string (e.g. '-₹60,000', '-₹2,500 Cr')."},
                                            "value": {"type": "number", "description": "Numeric amount for math calculations."},
                                            "step_type": {"type": "string", "enum": ["deduction", "addition", "subtotal"], "description": "Step type."}
                                        },
                                        "required": ["label", "display_value", "value"]
                                    }
                                },
                                "final_label": {"type": "string", "description": "Label for surviving bottom cash (e.g. 'Net Operating Cash', 'Surviving Savings')."},
                                "final_display_value": {"type": "string", "description": "Final surviving formatted string (e.g. '₹12,000', '₹1,200 Cr')."},
                                "final_value": {"type": "number", "description": "Final surviving numeric value."},
                                "visual_state": {"type": "string", "enum": state_enum, "description": "Visual state."}
                            },
                            "required": ["id", "type", "layout", "initial_label", "initial_display_value", "steps", "final_label", "final_display_value"]
                        },
                        {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string", "description": "Unique identifier for the capital_flow element."},
                                "type": {"type": "string", "enum": ["capital_flow"]},
                                "layout": {"type": "string", "enum": zone_enum, "description": "Spatial zone name ('center', 'split_left', or 'split_right')."},
                                "purpose": {"type": "string", "description": "Editorial purpose of this capital flow route visualizer."},
                                "title": {"type": "string", "description": "Optional overarching title."},
                                "source_label": {"type": "string", "description": "Source entity/location label (e.g. 'MUMBAI // BSE', 'Domestic Retail Accounts')."},
                                "source_sublabel": {"type": "string", "description": "Optional source subtext (e.g. 'Emerging Market Equity')."},
                                "target_label": {"type": "string", "description": "Destination entity/location label (e.g. 'NEW YORK // WALL ST', 'US 10-Yr Treasuries')."},
                                "target_sublabel": {"type": "string", "description": "Optional destination subtext (e.g. 'Safe Haven Yield (4.5%)')."},
                                "flow_label": {"type": "string", "description": "Label describing the capital movement (e.g. 'Capital Flight', 'FII Net Drain', 'SIP Pipeline')."},
                                "flow_display_value": {"type": "string", "description": "Formatted monetary value in flight (e.g. '₹1.14 Lakh Crore', '$15 Billion')."},
                                "flow_direction": {"type": "string", "enum": ["left_to_right", "right_to_left", "bidirectional"], "description": "Flow direction."},
                                "visual_state": {"type": "string", "enum": state_enum, "description": "Visual state."}
                            },
                            "required": ["id", "type", "layout", "source_label", "target_label", "flow_display_value"]
                        }
                    ]
                }
            },
            "events": {
                "type": "array",
                "description": "Sequential list of choreographic events bound to speech anchors.",
                "items": {
                    "anyOf": [
                        {
                            "type": "object",
                            "properties": {
                                "action": {"type": "string", "enum": ["enter"]},
                                "target_id": {"type": "string", "description": "ID of visual element to enter."},
                                "style": {"type": "string", "enum": ["fade", "fade_slide_up", "pop", "cut"], "description": "Entrance animation style. Must be 'cut' for stock_video."},
                                "anchor": {"type": "string", "description": "Exact spoken phrase in narration where action occurs."}
                            },
                            "required": ["action", "target_id", "anchor"]
                        },
                        {
                            "type": "object",
                            "properties": {
                                "action": {"type": "string", "enum": ["move"]},
                                "target_id": {"type": "string", "description": "ID of visual element to move."},
                                "to": {"type": "string", "enum": zone_enum, "description": "MANDATORY destination zone name."},
                                "anchor": {"type": "string", "description": "Exact spoken phrase in narration where action occurs."}
                            },
                            "required": ["action", "target_id", "to", "anchor"]
                        },
                        {
                            "type": "object",
                            "properties": {
                                "action": {"type": "string", "enum": ["transform_number"]},
                                "target_id": {"type": "string", "description": "ID of visual element whose number transforms (targets card, number, scale, or money_stack)."},
                                "to_display_value": {"type": "string", "description": "MANDATORY new formatted display string authored directly (e.g. '₹5,000', '₹0', '3 Years')."},
                                "to_numeric_value": {"type": "number", "description": "MANDATORY new numeric value authored directly."},
                                "to_fact_id": {"type": "string", "description": "Optional approved fact ID for the transformed value."},
                                "anchor": {"type": "string", "description": "Exact spoken phrase in narration where action occurs."}
                            },
                            "required": ["action", "target_id", "to_display_value", "to_numeric_value", "anchor"]
                        },
                        {
                            "type": "object",
                            "properties": {
                                "action": {"type": "string", "enum": ["transform_text"]},
                                "target_id": {"type": "string", "description": "ID of visual element whose text transforms."},
                                "to_text": {"type": "string", "description": "MANDATORY replacement text string."},
                                "anchor": {"type": "string", "description": "Exact spoken phrase in narration where action occurs."}
                            },
                            "required": ["action", "target_id", "to_text", "anchor"]
                        },
                        {
                            "type": "object",
                            "properties": {
                                "action": {"type": "string", "enum": ["change_visual_state"]},
                                "target_id": {"type": "string", "description": "ID of visual element whose state changes (targets card, character, scale, or money_stack)."},
                                "state": {"type": "string", "enum": state_enum, "description": "MANDATORY target visual state."},
                                "badge": {"type": "string", "description": "Optional badge label."},
                                "anchor": {"type": "string", "description": "Exact spoken phrase in narration where action occurs."}
                            },
                            "required": ["action", "target_id", "state", "anchor"]
                        },
                        {
                            "type": "object",
                            "properties": {
                                "action": {"type": "string", "enum": ["highlight"]},
                                "target_id": {"type": "string", "description": "ID of visual element to highlight."},
                                "anchor": {"type": "string", "description": "Exact spoken phrase in narration where action occurs."}
                            },
                            "required": ["action", "target_id", "anchor"]
                        },
                        {
                            "type": "object",
                            "properties": {
                                "action": {"type": "string", "enum": ["connect"]},
                                "target_id": {"type": "string", "description": "ID of connector element to activate."},
                                "anchor": {"type": "string", "description": "Exact spoken phrase in narration where action occurs."}
                            },
                            "required": ["action", "target_id", "anchor"]
                        },
                        {
                            "type": "object",
                            "properties": {
                                "action": {"type": "string", "enum": ["exit"]},
                                "target_id": {"type": "string", "description": "ID of visual element to exit."},
                                "direction": {"type": "string", "enum": direction_enum, "description": "Exit animation direction ('left', 'right', 'up', 'down', 'fade'). Defaults to 'fade'."},
                                "anchor": {"type": "string", "description": "Exact spoken phrase in narration where action occurs."}
                            },
                            "required": ["action", "target_id", "anchor"]
                        },
                        {
                            "type": "object",
                            "properties": {
                                "action": {"type": "string", "enum": ["change_pose"]},
                                "target_id": {"type": "string", "description": "ID of character element whose pose changes."},
                                "pose": {"type": "string", "enum": pose_enum, "description": "Target pose ('idle', 'walk', 'point', 'think', 'worried', 'celebrate')."},
                                "emotion": {"type": "string", "enum": emotion_enum, "description": "Optional target emotion."},
                                "facing": {"type": "string", "enum": facing_enum, "description": "Optional updated facing direction ('left' or 'right')."},
                                "anchor": {"type": "string", "description": "Exact spoken phrase in narration where action occurs."}
                            },
                            "required": ["action", "target_id", "pose", "anchor"]
                        }
                    ]
                }
            }
        },
        "required": ["story_id", "objects", "events"]
    }


class ContinuousStoryPlanArtifact(BaseModel):
    """
    Persisted pipeline artifact for a compiled Continuous Story Plan.
    
    Represents the output of the 'continuous_story' pipeline stage,
    storing the compiled Remotion StoryPlan along with the original AI draft
    and metadata for downstream rendering and artifact lineage.
    """
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    schema_version: str = "1"
    story_id: str = Field(validation_alias=AliasChoices("story_id", "id"))
    fps: int = 30
    duration_in_frames: int = Field(validation_alias=AliasChoices("duration_in_frames", "durationInFrames"))
    width: int = 1920
    height: int = 1080
    safe_margin: int = Field(default=80, validation_alias=AliasChoices("safe_margin", "safeMargin"))
    audio_file_name: str = Field(validation_alias=AliasChoices("audio_file_name", "audioFileName"))
    audio_storage_key: str | None = None
    plan: dict[str, Any] = Field(
        description="The fully-compiled, deterministic Remotion StoryPlan dictionary."
    )
    raw_gemini_draft: dict[str, Any] | None = Field(
        default=None,
        description="The raw provider payload preserved for debugging and lineage.",
    )
    draft: ContinuousStoryDraft | None = Field(
        default=None,
        description="The validated AI-authored continuous story draft (for provenance & lineage)."
    )
    resolved_assets: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Metadata for resolved real-world image assets."
    )

    def to_remotion_props(self) -> dict[str, Any]:
        """Returns the inputProps dictionary formatted for Remotion StoryScene."""
        return {"plan": self.plan}

    @classmethod
    def from_compiled_plan(
        cls,
        plan: dict[str, Any],
        draft: ContinuousStoryDraft | None = None,
        audio_storage_key: str | None = None,
        resolved_assets: list[dict[str, Any]] | None = None,
    ) -> ContinuousStoryPlanArtifact:
        """Constructs an artifact instance from a compiled Remotion StoryPlan dictionary."""
        return cls(
            story_id=plan.get("id") or plan.get("story_id", "unknown_story"),
            fps=plan.get("fps", 30),
            duration_in_frames=plan.get("durationInFrames") or plan.get("duration_in_frames", 380),
            width=plan.get("width", 1920),
            height=plan.get("height", 1080),
            safe_margin=plan.get("safeMargin") or plan.get("safe_margin", 80),
            audio_file_name=plan.get("audioFileName") or plan.get("audio_file_name", "narration.mp3"),
            audio_storage_key=audio_storage_key,
            plan=plan,
            draft=draft,
            resolved_assets=resolved_assets or [],
        )
