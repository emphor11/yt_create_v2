"""Contracts for the single-pass Visual World Storyboarder.

The Storyboarder is the visual director. It receives the complete narrative
context and produces an ordered beat plan describing the continuous visual world.

The model intentionally stops at medium-level visual intent:
- visual elements and hierarchy on first appearance
- semantic screen regions
- actions and spoken triggers
- beat-to-beat state changes

It does not own pixels, exact spacing, frame timing, or renderer details.
Those remain compiler/runtime responsibilities.
"""
from __future__ import annotations

import re
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from domain.primitives.common import CanonicalCapabilityType
from domain.storyboard import MacroScreenZone, MotionPreset, SemanticRelationship, VisualActionType
from domain.visual_world import StateChangeKind


KNOWN_COMPONENT_PROPERTIES = frozenset({
    "label", "display_value", "raw_value", "tag", "badge_text", "header", "subtext",
    "left_label", "left_value", "left_tag", "left_intent",
    "right_label", "right_value", "right_tag", "right_intent",
    "title", "steps", "text", "attribution",
    "source_id", "target_id", "relationship_type", "routing", "has_arrow", "style_intent",
    "data_points", "trend", "highlight_point",
    "bars", "benchmark_value", "benchmark_label",
    "slices", "center_label", "center_value", "segments",
    "content", "value", "prefix", "suffix", "precision", "variant", "intent",
})


class DonutSliceItemPayload(BaseModel):
    """A single allocation slice inside AllocationDonut."""

    model_config = ConfigDict(extra="ignore")

    label: str = Field(..., min_length=1, description="Slice category label, e.g. 'Equities'")
    value: float = Field(..., description="Numeric value or percentage")
    display_value: str | None = Field(default=None, description="Optional formatted display text, e.g. '55%'")
    intent: str | None = Field(default=None, description="Color intent: 'neutral', 'accent', 'danger', 'success', 'warning'")
    color: str | None = Field(default=None, description="Optional custom hex color")
    tag: str | None = Field(default=None, description="Optional pill tag, e.g. 'Core'")


class RankedBarItemPayload(BaseModel):
    """A single comparative bar item inside RankedBarChart."""

    model_config = ConfigDict(extra="ignore")

    label: str = Field(..., min_length=1, description="Category name, e.g. 'India'")
    value: float = Field(..., description="Numeric value for proportional scaling")
    display_value: str | None = Field(default=None, description="Optional formatted display text, e.g. '87%'")
    intent: str | None = Field(default=None, description="Color intent: 'neutral', 'accent', 'danger', 'success', 'warning'")
    tag: str | None = Field(default=None, description="Optional status pill tag, e.g. 'HIGHEST RISK'")


class TrendLineDataPointPayload(BaseModel):
    """A single coordinate point inside TrendLineChart."""

    model_config = ConfigDict(extra="ignore")

    label: str = Field(..., min_length=1, description="Point label, e.g. '2020', 'Q1'")
    value: float = Field(..., description="Numeric value for point")


class TrendLineHighlightPayload(BaseModel):
    """Optional highlight annotation marker on TrendLineChart."""

    model_config = ConfigDict(extra="ignore")

    label: str = Field(..., min_length=1, description="Highlight label, e.g. '2024 PEAK'")
    value: str | float | None = Field(default=None, description="Optional formatted or numeric value, e.g. '₹88.50'")


class WaterfallStepPayload(BaseModel):
    """A single sequential step or delta inside WaterfallBridge."""

    model_config = ConfigDict(extra="ignore")

    label: str = Field(..., min_length=1, description="Step name, e.g. 'Gross Revenue', 'COGS', 'Net Profit'")
    value: float = Field(..., description="Numeric value or delta")
    display_value: str | None = Field(default=None, description="Optional formatted display text, e.g. '₹100 Cr', '-₹40 Cr'")
    is_total: bool = Field(default=False, description="Whether this column represents a cumulative total rather than a delta")
    intent: str | None = Field(default=None, description="Color intent: 'neutral', 'accent', 'danger', 'success', 'warning'")


class ProcessStepPayload(BaseModel):
    """A single sequential step inside ProcessCard."""

    model_config = ConfigDict(extra="ignore")

    step: int | None = Field(default=None, description="Sequential step integer starting at 1")
    title: str = Field(..., min_length=1, description="Concise name of the step")
    detail: str | None = Field(default=None, description="Optional grounded explanation")


class SemanticContentPayload(BaseModel):
    """Authoritative schema for element semantic content across rich components and primitives.

    Exposes explicit properties to the LLM response schema so that constrained decoding
    grammar forces the model to emit actual component props instead of empty objects.
    """

    model_config = ConfigDict(extra="allow")

    # MetricCard & HeroStat
    label: str | None = Field(default=None, description="Metric dimension label, e.g. 'TOTAL ADDITIONAL INTEREST' or 'RBI REPO RATE'")
    display_value: str | None = Field(default=None, description="Formatted prominent stat, e.g. '8.50%', '₹45,390', '500M', 'FREE'")
    raw_value: float | None = Field(default=None, description="Numeric target for count-up animation, e.g. 8.5")
    tag: str | None = Field(default=None, description="Category or status badge pill text, e.g. 'IMMEDIATE', 'POLICY BENCHMARK'")
    header: str | None = Field(default=None, description="Top header band text, e.g. 'LOAN BENCHMARK', 'HOW THE HIKE TRAVELS'")
    subtext: str | None = Field(default=None, description="Secondary citation or contextual proof")
    intent: str | None = Field(default=None, description="Visual intent: 'neutral', 'accent', 'danger', 'success', 'warning', 'insight', 'takeaway'")
    variant: str | None = Field(default=None, description="Card styling variant: 'elevated', 'outlined', 'glass', 'accent_top'")

    # ComparisonCard
    left_label: str | None = Field(default=None, description="Left category label, e.g. 'LOAN EMI (BORROWERS)'")
    left_value: str | None = Field(default=None, description="Left prominent stat, e.g. '+2.50%', '₹48,900'")
    left_tag: str | None = Field(default=None, description="Left status pill, e.g. 'IMMEDIATE'")
    left_intent: str | None = Field(default=None, description="Left intent: 'neutral', 'accent', 'danger', 'success', 'warning'")
    right_label: str | None = Field(default=None, description="Right category label, e.g. 'SAVINGS FD (DEPOSITORS)'")
    right_value: str | None = Field(default=None, description="Right prominent stat, e.g. '0.00%', 'UNCHANGED'")
    right_tag: str | None = Field(default=None, description="Right status pill, e.g. 'LAGGING'")
    right_intent: str | None = Field(default=None, description="Right intent: 'neutral', 'accent', 'danger', 'success', 'warning'")

    # ProcessCard & WaterfallBridge
    title: str | None = Field(default=None, description="Title, e.g. 'HOW THE HIKE TRAVELS' or 'REVENUE BRIDGE'")
    steps: list[ProcessStepPayload] | list[WaterfallStepPayload] | None = Field(default=None, description="Sequential steps for ProcessCard or WaterfallBridge")

    # Callout & Badge
    text: str | None = Field(default=None, description="Editorial thesis or deduction statement")
    attribution: str | None = Field(default=None, description="Optional attribution or source label")

    # FlowConnector
    source_id: str | None = Field(default=None, description="ID of source visual object")
    target_id: str | None = Field(default=None, description="ID of target visual object")
    relationship_type: Literal["causes", "flows_to", "subtracts", "absorbs", "contrasts_with"] | None = Field(default=None, description="Relationship type")
    routing: Literal["orthogonal_elbow", "curved", "straight"] | None = Field(default=None, description="Routing type")
    has_arrow: bool | None = Field(default=None, description="Whether connector has directional arrow")
    style_intent: Literal["solid", "dashed", "animated_pulse"] | None = Field(default=None, description="Line style")

    # TrendLineChart
    data_points: list[TrendLineDataPointPayload] | None = Field(default=None, description="Optional 2 to 12 sequential coordinates for TrendLineChart")
    trend: Literal["up", "down", "neutral"] | None = Field(default=None, description="Trajectory direction: 'up', 'down', 'neutral'")
    highlight_point: TrendLineHighlightPayload | None = Field(default=None, description="Optional highlight label and value, e.g. {'label': '2024 PEAK', 'value': '₹88.50'}")

    # RankedBarChart
    bars: list[RankedBarItemPayload] | None = Field(default=None, description="2 to 6 comparative bars for RankedBarChart")
    benchmark_value: float | None = Field(default=None, description="Optional vertical benchmark value for RankedBarChart")
    benchmark_label: str | None = Field(default=None, description="Optional label for the benchmark, e.g. 'Global Average'")

    # AllocationDonut
    slices: list[DonutSliceItemPayload] | None = Field(default=None, description="2 to 6 allocation slices for AllocationDonut")
    center_label: str | None = Field(default=None, description="Subtitle inside donut center, e.g. 'TOTAL ASSETS'")
    center_value: str | None = Field(default=None, description="Primary stat inside donut center, e.g. '100%' or '₹10L'")

    # Canonical low-level primitives (text, number, etc.)
    content: str | None = Field(default=None, description="Text string for low-level text primitive")
    value: float | None = Field(default=None, description="Numeric value for low-level number primitive")
    prefix: str | None = Field(default=None, description="Prefix symbol, e.g. '₹', '$'")
    suffix: str | None = Field(default=None, description="Suffix symbol, e.g. '%', 'bps'")
    precision: int | None = Field(default=None, description="Decimal precision")


class StoryboardVisualElement(BaseModel):
    """How a stable object participates in one beat.

    Layout intentionally stops at semantic region. The compiler owns the
    concrete geometry and all parent-local spacing.
    """

    model_config = ConfigDict(extra="forbid")

    object_id: str = Field(..., min_length=1)
    primitive_type: CanonicalCapabilityType | None = None
    component_type: str | None = None
    parent_object_id: str | None = None
    semantic_content: dict[str, Any] = Field(default_factory=dict)
    lifecycle_mode: Literal["persistent", "beat_local"] = "beat_local"
    source_intent_ids: list[str] = Field(default_factory=list)
    role: Literal[
        "primary",
        "secondary",
        "supporting",
        "context",
        "relationship",
    ] | None = None
    macro_zone: MacroScreenZone | None = None
    actions: list[StoryboardActionPlan] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def rescue_root_props(cls, data: Any) -> Any:
        if isinstance(data, dict):
            sem = data.get("semantic_content")
            if not isinstance(sem, dict):
                sem = {}
            else:
                sem = dict(sem)

            # Rescue any component props placed at the root level of element
            for k in list(data.keys()):
                if k in KNOWN_COMPONENT_PROPERTIES:
                    if k not in sem or sem[k] is None:
                        sem[k] = data[k]
                    del data[k]

            # Common LLM alias mappings
            if "badge_text" in sem:
                if "tag" not in sem:
                    sem["tag"] = sem["badge_text"]
                del sem["badge_text"]

            if data.get("component_type") in {"ComparisonCard", "TrendLineChart", "RankedBarChart", "AllocationDonut", "WaterfallBridge"} and "title" in sem:
                if "header" not in sem:
                    sem["header"] = sem["title"]
                del sem["title"]

            if data.get("component_type") == "AllocationDonut" and "segments" in sem:
                if "slices" not in sem:
                    sem["slices"] = sem["segments"]
                del sem["segments"]

            comp_type = data.get("component_type")
            if comp_type in {"MetricCard", "HeroStat"}:
                if "value" in sem and ("raw_value" not in sem or sem["raw_value"] is None):
                    sem["raw_value"] = sem["value"]

                if not sem.get("display_value"):
                    for alias in ("amount", "stat", "metric", "figure", "number", "formatted_value", "display", "val", "value"):
                        if alias in sem and sem[alias] is not None:
                            val = sem.pop(alias)
                            sem["display_value"] = str(val)
                            break

                if not sem.get("display_value") and sem.get("raw_value") is not None:
                    sem["display_value"] = str(sem["raw_value"])

                # Auto-rescue: when LLM puts formatted number/stat into 'label' instead of 'display_value'
                if not sem.get("display_value") and sem.get("label"):
                    label_str = str(sem["label"])
                    if re.search(r"\d", label_str):
                        sem["display_value"] = label_str
                        if comp_type == "MetricCard":
                            if sem.get("header"):
                                sem["label"] = str(sem["header"])
                            elif sem.get("tag"):
                                sem["label"] = str(sem["tag"])
                            else:
                                sem["label"] = "STAT"
                        elif comp_type == "HeroStat":
                            if sem.get("subtext"):
                                sem["label"] = str(sem["subtext"])
                            elif sem.get("tag"):
                                sem["label"] = str(sem["tag"])
                            else:
                                sem["label"] = "STAT"

                if "raw_value" in sem and sem["raw_value"] is not None:
                    try:
                        sem["raw_value"] = float(sem["raw_value"])
                    except (ValueError, TypeError):
                        if not sem.get("display_value"):
                            sem["display_value"] = str(sem["raw_value"])
                        sem.pop("raw_value", None)

            data["semantic_content"] = sem
        return data

    @model_validator(mode="after")
    def validate_type(self) -> "StoryboardVisualElement":
        if self.primitive_type is not None and self.component_type is not None:
            raise ValueError(f"Element '{self.object_id}' cannot specify both primitive_type and component_type.")
        if self.component_type is not None:
            from registries.visual_component_registry import VisualComponentRegistry
            if not VisualComponentRegistry.is_registered(self.component_type):
                raise ValueError(f"Element '{self.object_id}' has unknown component_type '{self.component_type}'.")
            if self.semantic_content:
                try:
                    VisualComponentRegistry.validate_props(self.component_type, self.semantic_content)
                except Exception as e:
                    raise ValueError(
                        f"Element '{self.object_id}' of component_type '{self.component_type}' has invalid semantic_content: {e}"
                    ) from e
        return self


class StoryboardActionPlan(BaseModel):
    """A creative visual action chosen directly by the Storyboard LLM."""

    model_config = ConfigDict(extra="forbid")

    action_id: str | None = None
    action_type: VisualActionType
    motion_preset: MotionPreset = MotionPreset.REVEAL
    order: int | None = Field(default=None, ge=1)

    # The Storyboard LLM chooses a meaningful spoken anchor. Python validates it
    # against the beat narration and derives the occurrence deterministically.
    trigger_word: str | None = None

    target_property: str | None = None
    new_value: Any | None = None
    description: str | None = None


class StoryboardStateChange(BaseModel):
    """A semantic state change that the compiler can execute deterministically."""

    model_config = ConfigDict(extra="forbid")

    event_id: str | None = None
    object_id: str = Field(..., min_length=1)
    kind: StateChangeKind
    target_property: str | None = None
    from_value: Any | None = None
    to_value: Any | None = None
    visible: bool | None = None

    relationship: SemanticRelationship | None = None
    relationship_operation: Literal["add", "remove", "update"] | None = None

    # Only required for layout events. This keeps the LLM contract semantic:
    # a destination region, not a full compiler LayoutIntentState.
    macro_zone: MacroScreenZone | None = None

    description: str | None = None

    @model_validator(mode="after")
    def validate_shape(self) -> "StoryboardStateChange":
        if self.kind == StateChangeKind.LAYOUT and self.macro_zone is None:
            raise ValueError(
                f"Layout state change requires macro_zone."
            )
        if self.kind != StateChangeKind.LAYOUT and self.macro_zone is not None:
            raise ValueError(
                f"State change cannot set macro_zone unless kind='layout'."
            )
        if self.kind == StateChangeKind.RELATIONSHIP:
            if self.relationship is None or self.relationship_operation is None:
                raise ValueError(
                    "Relationship state change requires relationship and relationship_operation."
                )
        elif self.relationship is not None or self.relationship_operation is not None:
            raise ValueError(
                "relationship and relationship_operation are only valid for relationship changes."
            )
        if not self.event_id:
            self.event_id = f"evt_{self.kind.value}_{self.object_id}"
        if not self.description:
            self.description = f"{self.kind.value.capitalize()} for {self.object_id}."
        return self


class StoryboardBeatPlan(BaseModel):
    """The actual medium-level visual plan for one editorial beat."""

    model_config = ConfigDict(extra="forbid")

    beat_id: str = Field(..., min_length=1)
    narration: str = Field(..., min_length=1)
    visual_goal: str = Field(..., min_length=1)
    visual_strategy: str = Field(..., min_length=1)
    source_intent_ids: list[str] = Field(default_factory=list)

    # Objects that are visually participating/present in this beat.
    # Parent/child hierarchy is defined by the element itself.
    elements: list[StoryboardVisualElement] = Field(..., min_length=1)

    state_change_events: list[StoryboardStateChange] = Field(default_factory=list)

    transition_kind: Literal[
        "continue",
        "transform",
        "hold",
        "focus",
        "cut",
        "introduce_world",
    ] | None = None


class WorldFoundationSpec(BaseModel):
    """Complete single-pass visual world storyboard."""

    model_config = ConfigDict(extra="forbid")

    world_id: str = Field(..., min_length=1)
    beats: list[StoryboardBeatPlan] = Field(..., min_length=1)

    @model_validator(mode="after")
    def validate_foundation(self) -> "WorldFoundationSpec":
        from registries.visual_component_registry import VisualComponentRegistry
        from domain.storyboard import extract_narration_words

        seen_objects: dict[str, StoryboardVisualElement] = {}
        distinct_beats_by_object: dict[str, set[str]] = {}

        # 1. Track distinct beats where each object participates to infer persistence
        for beat in self.beats:
            for element in beat.elements:
                distinct_beats_by_object.setdefault(element.object_id, set()).add(beat.beat_id)

        for beat in self.beats:
            words = extract_narration_words(beat.narration)
            words_lower = [w.lower() for w in words]
            first_word = words[0] if words else "start"
            beat_object_ids = {element.object_id for element in beat.elements}

            for element in beat.elements:
                if element.component_type == "FlowConnector":
                    source_id = element.semantic_content.get("source_id")
                    target_id = element.semantic_content.get("target_id")
                    if source_id not in beat_object_ids or target_id not in beat_object_ids:
                        raise ValueError(
                            f"FlowConnector '{element.object_id}' in beat '{beat.beat_id}' "
                            "must reference source_id and target_id elements in the same beat."
                        )

            for event in beat.state_change_events:
                if event.object_id not in beat_object_ids:
                    raise ValueError(
                        f"State change '{event.event_id}' in beat '{beat.beat_id}' "
                        f"targets '{event.object_id}', which is not present in that beat."
                    )

            # 2. Derive role deterministically if omitted
            has_primary = any(el.role == "primary" for el in beat.elements)
            for element in beat.elements:
                if element.role is None:
                    if (
                        element.component_type == "FlowConnector"
                        or element.primitive_type == CanonicalCapabilityType.CONNECTOR
                    ):
                        element.role = "relationship"
                    elif not has_primary:
                        element.role = "primary"
                        has_primary = True
                    else:
                        element.role = "supporting"

            # 3. Macro zone fallback
            for element in beat.elements:
                if element.macro_zone is None:
                    if element.object_id in seen_objects and seen_objects[element.object_id].macro_zone:
                        element.macro_zone = seen_objects[element.object_id].macro_zone
                    elif element.component_type != "FlowConnector":
                        element.macro_zone = MacroScreenZone.CENTER

            # 4. First appearance vs Reappearance
            for element in beat.elements:
                # If object appears across multiple distinct beats, mark it persistent
                if len(distinct_beats_by_object[element.object_id]) > 1:
                    element.lifecycle_mode = "persistent"

                if element.object_id not in seen_objects:
                    # First appearance
                    if element.primitive_type is None and element.component_type is None:
                        raise ValueError(
                            f"Object '{element.object_id}' first appears in beat '{beat.beat_id}' "
                            "without a primitive_type or component_type."
                        )
                    # Validate first-appearance component or primitive content
                    if element.component_type is not None:
                        if not VisualComponentRegistry.is_registered(element.component_type):
                            raise ValueError(
                                f"Object '{element.object_id}' has unknown component_type '{element.component_type}'."
                            )
                        try:
                            VisualComponentRegistry.validate_props(element.component_type, element.semantic_content)
                        except Exception as e:
                            raise ValueError(
                                f"Object '{element.object_id}' first appears in beat '{beat.beat_id}' "
                                f"with invalid semantic_content for '{element.component_type}': {e}"
                            ) from e
                    elif element.primitive_type is not None:
                        from registries.primitive_registry import PrimitiveRegistry
                        try:
                            PrimitiveRegistry.validate_primitive_props(element.primitive_type, element.semantic_content)
                        except Exception as e:
                            raise ValueError(
                                f"Object '{element.object_id}' first appears in beat '{beat.beat_id}' "
                                f"with invalid semantic_content for primitive '{element.primitive_type.value}': {e}"
                            ) from e

                    # If actions empty, generate default enter action
                    if not element.actions:
                        element.actions = [
                            StoryboardActionPlan(
                                action_id=f"auto_enter_{element.object_id}",
                                action_type=VisualActionType.ENTER,
                                motion_preset=(
                                    MotionPreset.IMPACT
                                    if element.role == "primary"
                                    else MotionPreset.REVEAL
                                ),
                                trigger_word=first_word,
                                description=f"Auto-introduced {element.object_id}.",
                            )
                        ]
                    else:
                        first_action = element.actions[0]
                        if first_action.action_type not in {VisualActionType.ENTER, VisualActionType.APPEAR}:
                            if first_action.action_type in {
                                VisualActionType.UPDATE_VALUE,
                                VisualActionType.HIGHLIGHT,
                                VisualActionType.PULSE,
                            }:
                                enter_action = StoryboardActionPlan(
                                    action_id=f"auto_enter_{element.object_id}",
                                    action_type=VisualActionType.ENTER,
                                    motion_preset=first_action.motion_preset,
                                    trigger_word=first_word,
                                    description=f"Auto-introduced {element.object_id}.",
                                )
                                element.actions.insert(0, enter_action)
                            else:
                                raise ValueError(
                                    f"Object '{element.object_id}' first appears in beat '{beat.beat_id}' with action "
                                    f"'{first_action.action_type.value}', but must start with 'enter' or 'appear'."
                                )
                    seen_objects[element.object_id] = element
                else:
                    # Reappearance / reuse
                    prev_element = seen_objects[element.object_id]
                    if element.component_type is None and prev_element.component_type is not None:
                        element.component_type = prev_element.component_type
                    if element.primitive_type is None and prev_element.primitive_type is not None:
                        element.primitive_type = prev_element.primitive_type

                    if not element.semantic_content and prev_element.semantic_content:
                        element.semantic_content = prev_element.semantic_content
                    elif element.semantic_content and prev_element.semantic_content:
                        merged = dict(prev_element.semantic_content)
                        merged.update(element.semantic_content)
                        element.semantic_content = merged

                    # Update seen_objects with latest element so subsequent beats inherit the updated state
                    seen_objects[element.object_id] = element

                    # Validate updated props if present
                    if element.component_type is not None and VisualComponentRegistry.is_registered(element.component_type):
                        try:
                            VisualComponentRegistry.validate_props(element.component_type, element.semantic_content)
                        except Exception as e:
                            raise ValueError(
                                f"Object '{element.object_id}' re-appears in beat '{beat.beat_id}' "
                                f"with invalid semantic_content for '{element.component_type}': {e}"
                            ) from e
                    elif element.primitive_type is not None:
                        from registries.primitive_registry import PrimitiveRegistry
                        try:
                            PrimitiveRegistry.validate_primitive_props(element.primitive_type, element.semantic_content)
                        except Exception as e:
                            raise ValueError(
                                f"Object '{element.object_id}' re-appears in beat '{beat.beat_id}' "
                                f"with invalid semantic_content for primitive '{element.primitive_type.value}': {e}"
                            ) from e

                    # If no actions on reused object, generate default hold action
                    if not element.actions:
                        element.actions = [
                            StoryboardActionPlan(
                                action_id=f"auto_hold_{element.object_id}_{beat.beat_id}",
                                action_type=VisualActionType.HOLD,
                                motion_preset=MotionPreset.REVEAL,
                                trigger_word=first_word,
                                description=f"Hold {element.object_id}.",
                            )
                        ]
                    else:
                        for action in element.actions:
                            if action.action_type in {VisualActionType.ENTER, VisualActionType.APPEAR}:
                                raise ValueError(
                                    f"Object '{element.object_id}' re-appears in beat '{beat.beat_id}' with "
                                    f"'{action.action_type.value}'. Reused persistent objects must use 'hold', "
                                    "'highlight', 'pulse', 'update_value', 'transform', or 'exit'."
                                )

                # Validate component actions against registry
                comp_type = element.component_type
                if comp_type and VisualComponentRegistry.is_registered(comp_type):
                    desc = VisualComponentRegistry.get_descriptor(comp_type)
                    for act in element.actions:
                        if act.action_type.value not in desc.supported_actions:
                            raise ValueError(
                                f"Component '{comp_type}' on '{element.object_id}' does not support action '{act.action_type.value}'. "
                                f"Supported actions are: {desc.supported_actions}"
                            )

            # 5. Populate action fields and validate chronological trigger order
            all_actions_with_meta: list[tuple[int, int, StoryboardActionPlan, str]] = []
            for el_idx, element in enumerate(beat.elements):
                for act_idx, action in enumerate(element.actions):
                    if action.action_id is None:
                        action.action_id = f"act_{element.object_id}_{action.action_type.value}_{act_idx + 1}"
                    if action.description is None:
                        action.description = f"{action.action_type.value.capitalize()} on {element.object_id}."
                    if action.trigger_word is None:
                        action.trigger_word = first_word
                    else:
                        clean_trigger = action.trigger_word.strip().strip(".,!?;:\"'()[]{}").lower()
                        if clean_trigger not in words_lower:
                            import difflib
                            matches = difflib.get_close_matches(clean_trigger, words_lower, n=1, cutoff=0.55)
                            if matches:
                                clean_trigger = matches[0]
                            else:
                                stem_matches = [w for w in words_lower if w.startswith(clean_trigger) or clean_trigger.startswith(w)]
                                if stem_matches:
                                    clean_trigger = stem_matches[0]
                                else:
                                    raise ValueError(
                                        f"Action '{action.action_id}' on '{element.object_id}' in beat '{beat.beat_id}' has trigger word "
                                        f"'{action.trigger_word}' which does not appear in the beat narration: \"{beat.narration}\""
                                    )
                        action.trigger_word = clean_trigger

                    pos = words_lower.index(action.trigger_word) if action.trigger_word in words_lower else 0
                    all_actions_with_meta.append((pos, el_idx, action, element.object_id))

            # Handle ordering
            any_order_missing = any(act.order is None for _, _, act, _ in all_actions_with_meta)
            if any_order_missing:
                all_actions_with_meta.sort(key=lambda item: (item[0], item[1]))
                for order_idx, (_, _, action, _) in enumerate(all_actions_with_meta, start=1):
                    action.order = order_idx
            else:
                # All actions have explicit order -> validate chronological trigger order
                sorted_by_order = sorted(all_actions_with_meta, key=lambda item: item[2].order)
                for i in range(len(sorted_by_order) - 1):
                    pos_curr, _, act_curr, obj_curr = sorted_by_order[i]
                    pos_next, _, act_next, obj_next = sorted_by_order[i + 1]
                    if pos_curr > pos_next:
                        raise ValueError(
                            f"Chronological trigger order violation in beat '{beat.beat_id}': "
                            f"Action '{act_curr.action_id}' on '{obj_curr}' (order {act_curr.order}, trigger '{act_curr.trigger_word}') "
                            f"is ordered before Action '{act_next.action_id}' on '{obj_next}' (order {act_next.order}, trigger '{act_next.trigger_word}'), "
                            f"but '{act_next.trigger_word}' appears earlier in narration."
                        )

        return self
