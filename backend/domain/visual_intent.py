"""
Visual Intent domain models.

A VisualIntent represents what the viewer must understand from a segment of narration —
expressed semantically, without any reference to rendering components or layout.

The LLM's job is to extract rich semantic meaning:
- participating entities and their roles
- quantitative measurements bound to those entities
- temporal horizons and decay dynamics
- causal mechanisms and converging factors
- structured comparisons (subject A vs subject B, dimension, delta, winner)
- semantic visual dynamics (focal point, desired visual outcome, motion intent)

Each semantic sub-structure is populated ONLY when supported by the narration.
"""
from __future__ import annotations

import re
from typing import Any, Literal
from pydantic import BaseModel, Field, field_validator, model_validator


# Closed set of semantic relationship types.
# The LLM must choose one of these for every VisualIntent.
# This drives deterministic composition selection — no open-ended LLM invention.
VALID_RELATIONSHIP_TYPES: list[str] = [
    "metric",         # A single important number/value the viewer must register
    "calculation",    # input + operation → result (math story)
    "cause_effect",   # A causes/leads to B
    "multi_factor",   # multiple independent causes → combined outcome/pressure
    "comparison",     # A vs B side-by-side
    "trend",          # a value changes over time (direction unspecified)
    "growth",         # a single quantity or financial state evolves upward over time (accumulation, compounding, accelerating wealth)
    "divergence",      # two quantities/paths evolving in opposite directions over time (investing vs spending, equity vs debt)
    "waterfall",       # a starting total sequentially reduced by labeled deductions to a final balance
    "amortization",    # a debt/loan principal declining over time with interest/principal decomposition per period
    "accumulation",    # total builds from multiple labeled contribution streams over time
    "decline",        # a value specifically decreases over time
    "ranking",        # ordered list by magnitude or priority
    "process",        # sequential steps in a procedure
    "statement",      # key claim or thesis — no data needed
    "quote",          # attributed quote from a person
    "definition",     # explain what X is / means
    "broll",          # atmospheric/contextual moment — no infographic appropriate
]

VALID_COMPOSITION_IDS: list[str] = [
    "metric_hero",
    "calculation_story",
    "cause_effect",
    "comparison_split",
    "ranked_list",
    "process_flow",
    "time_decay",
    "growth_trajectory",
    "multi_factor_pressure",
    "trajectory_divergence",
    "cash_flow_waterfall",
    "accumulation_decomposition",
    "debt_amortization_schedule",
    "broll_caption",
]

# Closed set of semantic visual representations.
VALID_VISUAL_REPRESENTATIONS: list[str] = [
    "single_value",
    "trend",
    "comparison",
    "calculation",
    "cause_effect",
    "multi_factor",
    "process",
    "timeline",
    "ranking",
    "statement",
    "definition",
    "quote",
    "context",
]

# Closed set of evidence modes indicating actual factual data present in narration.
VALID_EVIDENCE_MODES: list[str] = [
    "none",
    "qualitative",
    "single_value",
    "multiple_values",
    "time_series",
    "calculation_inputs",
    "process_steps",
    "ranked_items",
]

COMPOSITION_TO_RELATIONSHIP_MAP: dict[str, str] = {
    "metric_hero": "metric",
    "calculation_story": "calculation",
    "cause_effect": "cause_effect",
    "multi_factor_pressure": "multi_factor",
    "comparison_split": "comparison",
    "ranked_list": "ranking",
    "process_flow": "process",
    "time_decay": "decline",
    "growth_trajectory": "growth",
    "trajectory_divergence": "divergence",
    "cash_flow_waterfall": "waterfall",
    "accumulation_decomposition": "accumulation",
    "debt_amortization_schedule": "amortization",
    "broll_caption": "broll",
}

RELATIONSHIP_TO_COMPOSITION_MAP: dict[str, str] = {
    "metric": "metric_hero",
    "calculation": "calculation_story",
    "cause_effect": "cause_effect",
    "multi_factor": "multi_factor_pressure",
    "comparison": "comparison_split",
    "ranking": "ranked_list",
    "process": "process_flow",
    "decline": "time_decay",
    "growth": "growth_trajectory",
    "divergence": "trajectory_divergence",
    "waterfall": "cash_flow_waterfall",
    "accumulation": "accumulation_decomposition",
    "amortization": "debt_amortization_schedule",
    "broll": "broll_caption",
    "statement": "broll_caption",
    "quote": "broll_caption",
    "definition": "broll_caption",
    "trend": "growth_trajectory",
}


class SemanticEntity(BaseModel):
    """
    An explicit entity involved in the visual narrative (e.g. 'Fixed Deposit', 'S&P 500').

    Contract for Ordered Compositions:
    - In relationship_type='ranking': entities are declared in authoritative order from highest rank (rank 1 at index 0) to lowest rank.
    - In relationship_type='process': entities are declared in authoritative sequential execution order (step 1 at index 0, step 2 at index 1, ...).
    """

    name: str = Field(description="Name or title of the entity")
    role: str | None = Field(
        default=None,
        description="Role in narrative, e.g. 'baseline', 'alternative', 'risk_factor', 'subject', 'benchmark'",
    )
    category: str | None = Field(
        default=None,
        description="Category, e.g. 'investment', 'asset', 'person', 'metric', 'institution', 'concept'",
    )


class QuantitativeMeasurement(BaseModel):
    """A numerical or quantitative data point explicitly bound to an entity or metric."""

    raw_value: str = Field(
        description="Original verbatim representation, e.g. '₹50 lakh', '6%', '15 years', '₹2 lakh'"
    )
    entity_name: str | None = Field(
        default=None,
        description="The entity this value belongs to, e.g. 'Fixed Deposit', 'Retirement Portfolio'",
    )
    metric_name: str | None = Field(
        default=None,
        description="The metric dimension, e.g. 'Annual Return', 'Portfolio Size', 'Horizon', 'Annual Withdrawal'",
    )
    unit: str | None = Field(
        default=None,
        description="Extracted unit, e.g. '%', 'years', 'lakh', '₹', '$', '€'",
    )
    numeric_value: float | None = Field(
        default=None,
        description=(
            "Numeric magnitude extracted from raw_value — unit-stripped. "
            "For '₹50 lakh' this is 50.0 (not 5000000). "
            "For '6%' this is 6.0. "
            "Unit semantics are authoritative only via raw_value and the unit field. "
            "Do not use numeric_value alone to reconstruct the factual quantity."
        ),
    )
    direction: Literal["up", "down", "flat", "neutral"] | None = Field(
        default=None,
        description="Directional movement if applicable: 'up', 'down', 'flat', 'neutral'",
    )
    polarity: Literal["positive", "negative", "neutral", "warning"] | None = Field(
        default=None,
        description="Semantic sentiment: 'positive', 'negative', 'neutral', 'warning'",
    )
    role: Literal["input", "rate", "result", "baseline", "delta", "benchmark", "context"] | None = Field(
        default=None,
        description="Functional semantic role: 'input', 'rate', 'result', 'baseline', 'delta', 'benchmark', 'context'",
    )

    @field_validator("numeric_value", mode="before")
    @classmethod
    def coerce_numeric(cls, v: Any) -> float | None:
        if v is None or v == "":
            return None
        if isinstance(v, (int, float)):
            return float(v)
        if isinstance(v, str):
            clean = re.sub(r"[^\d.-]", "", v)
            try:
                return float(clean) if clean else None
            except ValueError:
                return None
        return None

    @field_validator("direction", mode="before")
    @classmethod
    def normalize_direction(cls, v: Any) -> str | None:
        if not v or not isinstance(v, str):
            return None
        val = v.strip().lower()
        if val in ("up", "increase", "rising", "gain", "higher", "grow"):
            return "up"
        if val in ("down", "decrease", "falling", "loss", "lower", "decline", "drop"):
            return "down"
        if val in ("flat", "constant", "unchanged", "same"):
            return "flat"
        if val in ("neutral",):
            return "neutral"
        return val

    @field_validator("polarity", mode="before")
    @classmethod
    def normalize_polarity(cls, v: Any) -> str | None:
        if not v or not isinstance(v, str):
            return None
        val = v.strip().lower()
        if val in ("positive", "good", "gain"):
            return "positive"
        if val in ("negative", "bad", "loss", "danger"):
            return "negative"
        if val in ("warning", "caution", "risk"):
            return "warning"
        if val in ("neutral",):
            return "neutral"
        return val

    @field_validator("role", mode="before")
    @classmethod
    def normalize_role(cls, v: Any) -> str | None:
        if not v or not isinstance(v, str):
            return None
        val = v.strip().lower()
        if val in ("input", "start", "principal", "corpus", "base_corpus", "starting"):
            return "input"
        if val in ("rate", "percentage", "multiplier", "annual_rate", "fee", "growth_rate"):
            return "rate"
        if val in ("result", "output", "final", "outcome", "ending", "end"):
            return "result"
        if val in ("baseline", "initial", "original", "reference"):
            return "baseline"
        if val in ("delta", "spread", "difference", "margin", "gap"):
            return "delta"
        if val in ("benchmark", "index", "market"):
            return "benchmark"
        if val in ("context", "qualifier", "supporting"):
            return "context"
        return val


class TemporalContext(BaseModel):
    """Time horizons, compounding frequency, or decay dynamics."""

    horizon: str | None = Field(
        default=None,
        description="Time duration or period, e.g. '15 years', 'annual', '3 decades'",
    )
    frequency: str | None = Field(
        default=None,
        description="Frequency of occurrence, e.g. 'yearly', 'monthly', 'one-time'",
    )
    is_decay_over_time: bool = Field(
        default=False,
        description="Whether this describes erosion, purchasing power loss, or decay over time",
    )


class CausalStructure(BaseModel):
    """Causal relationship or multi-factor convergence."""

    causes: list[str] = Field(
        default_factory=list,
        description="List of driving causes or converging factors",
    )
    mechanism: str | None = Field(
        default=None,
        description="How the causes produce the effect, e.g. 'compounding fee drag', 'purchasing power erosion'",
    )
    outcome: str | None = Field(
        default=None,
        description="The resulting state or effect, e.g. 'portfolio shortfall', 'wealth destruction'",
    )
    outcome_severity: Literal["critical", "high", "medium", "low", "positive", "neutral"] | None = Field(
        default=None,
        description="Severity or impact of the outcome",
    )

    @field_validator("outcome_severity", mode="before")
    @classmethod
    def normalize_outcome_severity(cls, v: Any) -> str | None:
        if not v or not isinstance(v, str):
            return None
        val = v.strip().lower()
        if val in ("critical", "high", "medium", "low", "positive", "neutral"):
            return val
        return val


class ComparisonStructure(BaseModel):
    """Structured comparison between two subjects."""

    subject_a: str = Field(description="First subject/entity in the comparison")
    value_a: str = Field(description="Value, metric, or characteristic of subject A")
    subject_b: str = Field(description="Second subject/entity in the comparison")
    value_b: str = Field(description="Value, metric, or characteristic of subject B")
    comparison_dimension: str = Field(
        description="The dimension being compared, e.g. 'Annual Return', 'Risk', 'Cost', 'Corpus at 60'"
    )
    delta: str | None = Field(
        default=None,
        description="The quantitative or qualitative difference, e.g. '+6% spread', '2x higher', '₹1.2 Cr difference'",
    )
    winner: str | None = Field(
        default=None,
        description="Which subject wins or is highlighted as advantageous, if applicable",
    )


class VisualDynamics(BaseModel):
    """
    Semantic visual focus, motion, and layout intent.
    Purely semantic visual behavior — NOT a taxonomy of React component names or Remotion templates.
    """

    focal_point: str | None = Field(
        default=None,
        description="Primary visual anchor, e.g. 'net return delta', 'portfolio hero', 'danger zone'",
    )
    desired_visual_outcome: str | None = Field(
        default=None,
        description="What the viewer's eye should experience, e.g. 'instant contrast between safe vs growth', 'feeling of rapid erosion'",
    )
    motion_intent: str | None = Field(
        default=None,
        description="Dynamic behavior, e.g. 'side_by_side_reveal', 'countdown_decay', 'convergence_inward', 'counter_increment'",
    )
    visual_priority: str | None = Field(
        default=None,
        description="Visual weight: 'high', 'primary', 'secondary', 'context'",
    )


class VisualIntent(BaseModel):
    """
    A single semantic visual intent derived from one or more narration sentences.

    Multiple sentences that together express one viewer understanding should produce
    a single VisualIntent. Filler or transitional sentences produce no VisualIntent.
    """

    intent_id: str = Field(
        description="Sequential identifier: intent_01, intent_02, ..."
    )
    narration_excerpt: str = Field(
        description="Verbatim narration sentences this intent covers."
    )
    what_viewer_must_understand: str = Field(
        description="One sentence describing what the viewer must understand after seeing this visual."
    )
    key_values: list[str] = Field(
        default_factory=list,
        description="Explicit values or quantities mentioned, e.g. '₹50 lakh', '4%', '15 years'.",
    )
    composition_id: str | None = Field(
        default=None,
        description=f"Direct Remotion composition ID. Must be one of: {', '.join(VALID_COMPOSITION_IDS)}",
    )
    relationship_type: str | None = Field(
        default=None,
        description=f"Semantic relationship type. Must be one of: {', '.join(VALID_RELATIONSHIP_TYPES)}",
    )
    visual_representation: str | None = Field(
        default=None,
        description=f"Semantic visual representation. Must be one of: {', '.join(VALID_VISUAL_REPRESENTATIONS)}",
    )
    evidence_mode: str | None = Field(
        default=None,
        description=f"Actual evidence available in narration. Must be one of: {', '.join(VALID_EVIDENCE_MODES)}",
    )
    composition_id: str | None = Field(
        default=None,
        description=f"Direct Remotion composition ID. Must be one of: {', '.join(VALID_COMPOSITION_IDS)}",
    )
    emphasis: str | None = Field(
        default=None,
        description=(
            "Optional emphasis hint: e.g. 'hero', 'headline', 'show_result', 'show_decline', "
            "'show_scale', 'highlight_risk', 'highlight_spread'."
        ),
    )
    trigger_word: str | None = Field(
        default=None,
        description=(
            "A single verbatim word from the narration that triggers this visual switch. "
            "Must be null for the first intent of an idea. "
            "Must appear verbatim in narration_excerpt."
        ),
    )
    visual_priority: str | None = Field(
        default=None,
        description="Visual priority: 'primary', 'secondary', 'context'.",
    )

    # Rich semantic fields (populated ONLY when supported by narration)
    entities: list[SemanticEntity] = Field(
        default_factory=list,
        description=(
            "Explicit entities involved in this visual intent. "
            "For composition_id='ranked_list', list order is authoritative (index 0 = rank 1). "
            "For composition_id='process_flow', list order is authoritative (index 0 = step 1)."
        ),
    )
    measurements: list[QuantitativeMeasurement] = Field(
        default_factory=list,
        description="Quantitative values bound to entities and metrics.",
    )
    temporal: TemporalContext | None = Field(
        default=None,
        description="Temporal context, duration, compounding frequency, or decay dynamics.",
    )
    causal: CausalStructure | None = Field(
        default=None,
        description="Causal linkages or converging drivers.",
    )
    comparison: ComparisonStructure | None = Field(
        default=None,
        description="Direct comparison structure between subjects.",
    )
    visual_dynamics: VisualDynamics | None = Field(
        default=None,
        description="Semantic visual dynamics and focal intent.",
    )

    @model_validator(mode="before")
    @classmethod
    def sync_composition_and_relationship(cls, data: Any) -> Any:
        if isinstance(data, dict):
            comp_id = data.get("composition_id")
            rel_type = data.get("relationship_type")
            ev_mode = data.get("evidence_mode")
            if comp_id and not rel_type:
                data["relationship_type"] = COMPOSITION_TO_RELATIONSHIP_MAP.get(comp_id, "broll")
            elif rel_type and not comp_id:
                if ev_mode:
                    if rel_type == "growth":
                        if ev_mode in ("qualitative", "none"):
                            data["composition_id"] = "broll_caption"
                        elif ev_mode == "single_value":
                            data["composition_id"] = "metric_hero"
                        else:
                            data["composition_id"] = "growth_trajectory"
                    elif rel_type == "decline":
                        if ev_mode in ("qualitative", "none"):
                            data["composition_id"] = "broll_caption"
                        elif ev_mode == "single_value":
                            data["composition_id"] = "metric_hero"
                        else:
                            data["composition_id"] = "time_decay"
                    elif rel_type == "calculation":
                        if ev_mode in ("qualitative", "none"):
                            data["composition_id"] = "broll_caption"
                        elif ev_mode == "single_value":
                            data["composition_id"] = "metric_hero"
                        else:
                            data["composition_id"] = "calculation_story"
                    elif rel_type == "metric":
                        data["composition_id"] = "broll_caption" if ev_mode in ("qualitative", "none") else "metric_hero"
                    elif rel_type == "comparison":
                        data["composition_id"] = "broll_caption" if ev_mode == "none" else "comparison_split"
                    elif rel_type == "divergence":
                        data["composition_id"] = "broll_caption" if ev_mode == "none" else "trajectory_divergence"
                    else:
                        data["composition_id"] = RELATIONSHIP_TO_COMPOSITION_MAP.get(rel_type, "broll_caption")
                elif rel_type != "trend":
                    data["composition_id"] = RELATIONSHIP_TO_COMPOSITION_MAP.get(rel_type, "broll_caption")
            elif not comp_id and not rel_type:
                data["composition_id"] = "broll_caption"
                data["relationship_type"] = "broll"
        return data

    @field_validator("composition_id")
    @classmethod
    def composition_id_must_be_valid(cls, value: str | None) -> str | None:
        if value is not None and value not in VALID_COMPOSITION_IDS:
            raise ValueError(
                f"composition_id '{value}' is not allowed. "
                f"Must be one of: {', '.join(VALID_COMPOSITION_IDS)}"
            )
        return value

    @field_validator("relationship_type")
    @classmethod
    def relationship_type_must_be_valid(cls, value: str | None) -> str | None:
        if value is not None and value not in VALID_RELATIONSHIP_TYPES:
            raise ValueError(
                f"relationship_type '{value}' is not allowed. "
                f"Must be one of: {', '.join(VALID_RELATIONSHIP_TYPES)}"
            )
        return value

    @field_validator("visual_representation")
    @classmethod
    def visual_representation_must_be_valid(cls, value: str | None) -> str | None:
        if value is not None and value not in VALID_VISUAL_REPRESENTATIONS:
            raise ValueError(
                f"visual_representation '{value}' is not allowed. "
                f"Must be one of: {', '.join(VALID_VISUAL_REPRESENTATIONS)}"
            )
        return value

    @field_validator("evidence_mode")
    @classmethod
    def evidence_mode_must_be_valid(cls, value: str | None) -> str | None:
        if value is not None and value not in VALID_EVIDENCE_MODES:
            raise ValueError(
                f"evidence_mode '{value}' is not allowed. "
                f"Must be one of: {', '.join(VALID_EVIDENCE_MODES)}"
            )
        return value

    @field_validator("visual_priority")
    @classmethod
    def visual_priority_must_be_valid(cls, value: str | None) -> str | None:
        if value is not None and value not in ("primary", "secondary", "context"):
            return "primary"
        return value

    @field_validator("entities", "measurements", mode="before")
    @classmethod
    def normalize_lists(cls, v: Any) -> Any:
        if v is None:
            return []
        return v

    @field_validator("temporal", "causal", "comparison", "visual_dynamics", mode="before")
    @classmethod
    def normalize_optional_objects(cls, v: Any) -> Any:
        if v is None:
            return None
        if isinstance(v, dict) and not any(v.values()):
            return None
        return v

class VisualIntentSequence(BaseModel):
    """
    The ordered sequence of VisualIntents for one narrative idea.
    Output of VisualIntentEngine.run() for a single idea.
    """

    schema_version: str = "1"
    idea_id: str = Field(description="Matches the idea_id from ScriptVisualStrategy.ideas.")
    narration: str = Field(description="The full narration text this sequence covers.")
    intents: list[VisualIntent] = Field(
        description=(
            "Ordered visual intents. May be empty if narration "
            "contains only filler/transitions."
        )
    )

ComparisonContext = ComparisonStructure
