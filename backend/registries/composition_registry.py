"""
CompositionRegistry — the closed catalog of authored visual compositions.

Each CompositionDefinition specifies:
  - What relationship types it can serve
  - The Pydantic data model that validates its composition_data
  - Which Remotion component renders it
  - A safe fallback component if rendering fails
  - The asset requirement level

The LLM planner selects from this catalog only.
It cannot invent new composition IDs.

Adding a new composition requires:
1. Define a Pydantic data model below
2. Create a CompositionDefinition
3. Call CompositionRegistry.register() at module load time
4. Create the corresponding Remotion .tsx component (Phase 5)
5. Add dispatch to VideoAssembly.tsx (Phase 6)
6. Update the planner prompt (auto-generated from this registry)
"""
from __future__ import annotations

from collections.abc import Callable
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from domain.visual_intent import VisualIntent
from registries.composition_builders import (
    build_broll_caption_data,
    build_calculation_story_data,
    build_cash_flow_waterfall_data,
    build_cause_effect_data,
    build_comparison_split_data,
    build_growth_trajectory_data,
    build_metric_hero_data,
    build_multi_factor_pressure_data,
    build_process_flow_data,
    build_ranked_list_data,
    build_time_decay_data,
    build_trajectory_divergence_data,
    is_eligible_broll_caption,
    is_eligible_calculation_story,
    is_eligible_cash_flow_waterfall,
    is_eligible_cause_effect,
    is_eligible_comparison_split,
    is_eligible_growth_trajectory,
    is_eligible_metric_hero,
    is_eligible_multi_factor_pressure,
    is_eligible_process_flow,
    is_eligible_ranked_list,
    is_eligible_time_decay,
    is_eligible_trajectory_divergence,
)


# ---------------------------------------------------------------------------
# Asset requirement levels
# ---------------------------------------------------------------------------

class AssetRequirement(str, Enum):
    NONE = "none"
    OPTIONAL_BROLL = "optional_broll"
    REQUIRED_IMAGE = "required_image"


# ---------------------------------------------------------------------------
# Composition data models (one per composition)
# ---------------------------------------------------------------------------

class StrictCompositionData(BaseModel):
    """Composition payload base: filler responses may not contain extra fields."""

    model_config = ConfigDict(extra="forbid")

class MetricHeroData(StrictCompositionData):
    """
    A single important number/metric the viewer must register.

    Use for: hero metrics, key statistics, important quantities.
    relationship_types: metric
    """
    value: str = Field(description="The metric value, e.g. '₹50 lakh', '$1.02T', '4%'")
    label: str = Field(description="Short label, e.g. 'Starting Retirement Portfolio'")
    context: str | None = Field(
        default=None,
        description="Optional qualifier, e.g. 'as of 2024', 'per year', 'annually'",
    )
    emphasis: str | None = Field(
        default=None,
        description="'hero' for climax/central moments, 'supporting' for secondary metrics. "
                    "Default treatment applied when null.",
    )
    variant: str | None = Field(
        default=None,
        description="'hero_milestone' | 'supporting_metric' | 'warning_metric' | 'before_after_metric'",
    )
    polarity: str | None = Field(
        default=None,
        description="'positive' | 'negative' | 'neutral' | 'warning'",
    )
    direction: str | None = Field(
        default=None,
        description="'up' | 'down' | 'flat' | 'neutral'",
    )
    baseline_value: str | None = Field(
        default=None,
        description="Optional baseline value for before/after comparison",
    )
    delta: str | None = Field(
        default=None,
        description="Optional change indicator, e.g. '+40%', '-₹5 lakh'",
    )


class CalculationStoryData(StrictCompositionData):
    """
    Shows an input × rate → result math argument, or input → result financial transformation.

    Use for: percentage calculations, rate applications, compounding growth, addition/subtraction.
    relationship_types: calculation
    """
    input_label: str = Field(description="Label for the input, e.g. 'Portfolio', 'Initial Investment', 'Gross Income'")
    input_value: str = Field(description="Value of the input, e.g. '₹50 lakh', '₹10,000/month'")
    operation_label: str | None = Field(
        default=None,
        description="Optional operation symbol or word, e.g. '×', '÷', 'minus', '+', '→'. Defaults to '→' or operation type symbol.",
    )
    rate_label: str | None = Field(
        default=None,
        description="Optional label for the rate/modifier or second operand, e.g. '4% withdrawal rate', '₹10,000 bonus', '20 years'",
    )
    result_label: str = Field(description="Label for the result, e.g. 'Annual Income', 'Total Corpus', 'Net Savings'")
    result_value: str = Field(description="Value of the result, e.g. '₹2 lakh', '₹1.2 Crore'")
    note: str | None = Field(
        default=None,
        description="Optional supporting note below the result, e.g. 'Safe Withdrawal Rate', 'Compounded at 12%'",
    )
    operation_type: str | None = Field(
        default="multiplication",
        description="'multiplication' | 'addition' | 'subtraction' | 'allocation' | 'growth' | 'neutral'",
    )
    variant: str | None = Field(
        default=None,
        description="'multiplication' | 'addition' | 'subtraction' | 'allocation' | 'growth' | 'neutral'",
    )
    polarity: str | None = Field(
        default=None,
        description="'positive' | 'negative' | 'neutral' | 'warning'",
    )
    timeframe: str | None = Field(
        default=None,
        description="Optional timeframe context, e.g. 'over 20 years', 'per year', '15 Years'",
    )
    secondary_label: str | None = Field(
        default=None,
        description="Optional secondary metric label (e.g. 'Total Invested')",
    )
    secondary_value: str | None = Field(
        default=None,
        description="Optional secondary metric value (e.g. '₹18 Lakh')",
    )


class CauseItem(StrictCompositionData):
    label: str = Field(description="Short label for this cause, e.g. 'High Inflation'")
    value: str | None = Field(default=None, description="Optional value, e.g. '7%'")
    icon: str | None = Field(
        default=None,
        description="Optional emoji or icon name hint, e.g. '📈', 'inflation'",
    )


class CauseEffectData(StrictCompositionData):
    """
    Shows 1–3 causes converging to a single outcome.

    Use for: causal chains, root cause leading to an outcome.
    relationship_types: cause_effect
    """
    causes: list[CauseItem] = Field(
        description="List of 1–3 cause items. Each becomes a card on the left.",
    )
    connector: str = Field(
        description="Relationship word shown on the arrow: 'leads to', 'causes', "
                    "'combine to create', 'produces'",
    )
    outcome_label: str = Field(description="The outcome label, e.g. 'Retirement Risk'")
    outcome_value: str | None = Field(default=None, description="Optional outcome value")
    outcome_severity: str | None = Field(
        default=None,
        description="'negative' | 'positive' | 'neutral' — controls outcome card color",
    )
    outcome_header_label: str | None = Field(
        default=None,
        description="Optional eyebrow or header label above outcome, e.g. 'Ultimate Consequence', 'Causal Payoff'",
    )
    outcome_note: str | None = Field(
        default=None,
        description="Optional mechanism or explanatory note shown inside the outcome card",
    )
    variant: str | None = Field(
        default=None,
        description="Visual treatment variant: 'single_cause' | 'dual_cause' | 'multi_cause' | 'standard'",
    )
    polarity: str | None = Field(
        default=None,
        description="Outcome polarity override: 'positive' | 'negative' | 'neutral' | 'warning'",
    )


class TimeDecayData(StrictCompositionData):
    """
    Shows how a fixed amount or asset loses purchasing power or value over time.

    Use for: inflation impact, currency erosion, purchasing power decay, real vs nominal value, single-period depreciation.
    relationship_types: decline, trend (strictly decline/erosion over time)
    """
    fixed_amount: str | None = Field(
        default=None,
        description="The fixed nominal amount or baseline label, e.g. '₹2 lakh' or 'Original Value'. Optional if percentage drop is stated without nominal currency.",
    )
    amount_label: str = Field(description="Label for the amount or asset, e.g. 'Annual Withdrawal', 'New Car Value', 'Purchasing Power'")
    time_period: str = Field(description="Time horizon, e.g. '15 years', 'first year', 'over a decade'")
    emphasis: str = Field(
        default="value_erosion",
        description="'purchasing_power_decline' | 'value_erosion' | 'real_vs_nominal' | 'single_period_drop'",
    )
    annotation: str | None = Field(
        default=None,
        description="Callout text at end of the decay curve, e.g. 'Buys 40% less than today' or 'Immediate 15% depreciation'",
    )
    show_chart: bool = Field(
        default=True,
        description="Whether to show a decline curve. False = text-only version.",
    )
    end_value: str | None = Field(
        default=None,
        description="Optional terminal/ending value after decay, e.g. '₹26,000' or '85% Value'",
    )
    end_label: str | None = Field(
        default=None,
        description="Optional label for ending value, e.g. 'Real Purchasing Power', 'Residual Value'",
    )
    drop_rate: str | None = Field(
        default=None,
        description="Optional percentage drop, e.g. '60%', '74%', '15%'",
    )
    severity: str | None = Field(
        default=None,
        description="'mild' | 'moderate' | 'severe' | 'catastrophic'",
    )
    variant: str | None = Field(
        default=None,
        description="'mild_decay' | 'severe_decay' | 'inflation_erosion' | 'single_period_drop' | 'standard'",
    )
    rate_label: str | None = Field(
        default=None,
        description="Optional inflation rate or annual decay rate, e.g. '6.8% Inflation' or '15% First-Year Depreciation'",
    )
    decay_type: str | None = Field(
        default="standard",
        description="'single_period' | 'recurring_annual' | 'purchasing_power' | 'standard'",
    )


class GrowthTrajectoryData(StrictCompositionData):
    """
    Shows a single quantity, asset, corpus, or financial state evolving upward over time.
    Especially for illustrating the trajectory from early linear savings accumulation to
    accelerating / compounding growth or milestone progression.

    Use for: linear savings accumulation, investment growth, compounding, accelerating wealth,
    corpus growth, SIP accumulation, wealth snowball, linear -> compounding transitions.
    relationship_types: growth
    """
    header_label: str = Field(
        default="GROWTH TRAJECTORY",
        description="Header label, e.g. 'WEALTH ACCUMULATION', 'CORPUS GROWTH', 'COMPOUNDING TRAJECTORY'",
    )
    start_value: str | None = Field(
        default=None,
        description="Starting value or quantity, e.g. '₹0', '₹50,000/mo', '₹10 Lakh'",
    )
    start_label: str = Field(
        description="Label for starting point, e.g. 'Initial Savings', 'Base Corpus', 'Monthly Contribution'",
    )
    end_value: str | None = Field(
        default=None,
        description="Ending or target value, e.g. '₹10 Lakh', '₹1 Crore', '₹38 Lakh'",
    )
    end_label: str = Field(
        description="Label for ending value, e.g. 'Target Corpus', 'Accumulated Wealth', 'Eventual Corpus'",
    )
    time_horizon: str | None = Field(
        default=None,
        description="Time horizon, e.g. '7 years', '10 years', '20 years', 'over time'",
    )
    growth_rate: str | None = Field(
        default=None,
        description="Optional explicit growth rate if stated in narration, e.g. '12% Annual Return', '10% CAGR'. Never fabricate.",
    )
    growth_type: Literal["linear", "accelerating", "compound", "unspecified"] = Field(
        default="unspecified",
        description="Growth regime: 'linear' (steady accumulation/savings), 'accelerating' (snowballing returns), 'compound' (exponential growth), 'unspecified'",
    )
    milestone_value: str | None = Field(
        default=None,
        description="Optional intermediate milestone value, e.g. '₹10 Lakh', 'First ₹10 Lakh'",
    )
    milestone_label: str | None = Field(
        default=None,
        description="Optional milestone label, e.g. 'Inflection Point', 'Tipping Point', 'Snowball Begins'",
    )
    annotation: str | None = Field(
        default=None,
        description="Callout note or key insight, e.g. 'Returns begin outpacing monthly savings', 'Linear savings → compounding snowball'",
    )
    variant: str | None = Field(
        default="standard",
        description="'linear_accumulation' | 'accelerating_growth' | 'compounding_snowball' | 'milestone_progression' | 'standard'",
    )



class TrajectoryPath(StrictCompositionData):
    """
    One of two diverging paths in a TrajectoryDivergence composition.
    """
    label: str = Field(
        description="Name for this path, e.g. 'Investor (Equity SIP)', 'Spender (Car EMI)'",
    )
    start_value: str | None = Field(
        default=None,
        description="Starting value if stated, e.g. '₹0', '₹15 Lakh Car'",
    )
    end_value: str | None = Field(
        default=None,
        description="Terminal value of this path, e.g. '₹38 Lakh', '₹6 Lakh Resale'",
    )
    rate: str | None = Field(
        default=None,
        description="Growth or decay rate, e.g. '12% CAGR', '15% Depreciation'. Never fabricate.",
    )
    direction: Literal["up", "down", "neutral"] | None = Field(
        default=None,
        description="'up' for growing value, 'down' for declining value, 'neutral' for flat",
    )
    tone: Literal["positive", "negative", "neutral"] | None = Field(
        default=None,
        description="Editorial tone: 'positive' (desirable outcome), 'negative' (undesirable), 'neutral'",
    )


class TrajectoryDivergenceData(StrictCompositionData):
    """
    Shows two financial paths or strategies evolving in opposite directions over time.
    One path improves (investing, equity, SIP) and one deteriorates (spending, debt, depreciation).
    The visual grammar shows the growing gap between them.

    Use for: invest vs spend, equity vs debt, saving vs spending, opportunity cost,
    real vs nominal, inflation-adjusted vs nominal, two competing strategies.
    relationship_types: divergence
    """
    time_horizon: str = Field(
        description="Duration over which the divergence unfolds, e.g. '10 Years', '7 Years', '20 Years'",
    )
    baseline_label: str = Field(
        default="Common Starting Point",
        description="What both paths start from, e.g. '₹30,000 Monthly Commitment', 'Monthly Salary ₹50,000'",
    )
    path_a: TrajectoryPath = Field(
        description="First diverging path (typically the favorable/positive direction)",
    )
    path_b: TrajectoryPath = Field(
        description="Second diverging path (typically the unfavorable/negative direction)",
    )
    divergence_gap: str | None = Field(
        default=None,
        description="The explicit gap between path_a and path_b at the horizon, e.g. '₹32 Lakh Wealth Gap'. Only populate if stated in narration.",
    )
    header_label: str = Field(
        default="COMPOUNDING DIVERGENCE",
        description="Category eyebrow label, e.g. 'WEALTH ACCUMULATION DIVERGENCE', 'COMPOUNDING DIVERGENCE'",
    )
    variant: str | None = Field(
        default="standard",
        description="'divergence' | 'wealth_gap' | 'cost_opportunity' | 'standard'",
    )


class WaterfallStep(StrictCompositionData):
    """
    A single deduction or adjustment step in a cash flow waterfall.
    """
    label: str = Field(
        description="Name of this deduction, e.g. 'Taxes', 'EMI Obligations', 'Living Expenses'",
    )
    value: str = Field(
        description="Signed value string, e.g. '-₹1,50,000', '-₹80,000'. Negative = subtract, positive = add.",
    )
    direction: Literal["subtract", "add"] = Field(
        default="subtract",
        description="'subtract' for deductions, 'add' for inflows or reversals",
    )
    subtext: str | None = Field(
        default=None,
        description="Optional clarifying note, e.g. 'Direct Tax Code', 'Car & Personal Loans'. Never fabricate.",
    )
    numeric_amount: float | None = Field(
        default=None,
        description="Optional numeric amount for deterministic final-balance calculation",
    )


class CashFlowWaterfallData(StrictCompositionData):
    """
    Tracks a starting total resource (salary, corpus, capital) as it is depleted or
    adjusted by a sequence of labeled deductions, producing a final remaining balance.

    Use for: salary depletion (tax → EMI → expenses → surplus), corpus distributions,
    business revenue → expenses → profit, loan proceeds → fees → net disbursement.
    relationship_types: waterfall
    """
    starting_label: str = Field(
        description="Label for the initial total, e.g. 'Gross Monthly Salary', 'Starting Corpus', 'Total Inflow'",
    )
    starting_value: str = Field(
        description="Starting total value, e.g. '₹5,00,000', '₹50 Lakh'",
    )
    steps: list[WaterfallStep] = Field(
        description="Ordered list of deductions/adjustments. Must follow narration order. 2–6 steps.",
    )
    final_label: str = Field(
        default="Remaining Balance",
        description="Label for the final remaining amount, e.g. 'Investable Surplus', 'Net Operating Cash'",
    )
    final_value: str | None = Field(
        default=None,
        description="Final balance after all deductions. Only populate if derivable from source values or stated in narration.",
    )
    header_label: str = Field(
        default="CASH FLOW BREAKDOWN",
        description="Category eyebrow label, e.g. 'MONTHLY CASH FLOW', 'SALARY DRAIN BREAKDOWN'",
    )
    variant: str | None = Field(
        default="standard",
        description="'standard' | 'detailed' | 'compact'",
    )


class FactorItem(StrictCompositionData):
    label: str = Field(description="Short label, e.g. 'High Inflation', 'Weak Returns'")
    value: str | None = Field(default=None, description="Optional value, e.g. '7%', '3%'")
    severity: str | None = Field(
        default=None,
        description="'high' | 'medium' | 'low' — controls card accent color",
    )
    icon: str | None = Field(
        default=None,
        description="Optional icon identifier or emoji representing the factor",
    )


class MultiFactorPressureData(StrictCompositionData):
    """
    Shows 2–4 independent factors converging to create combined pressure/risk.

    Use for: retirement risks, market forces, systemic pressures.
    relationship_types: multi_factor
    """
    factors: list[FactorItem] = Field(
        description="List of 2–4 factor items. Each becomes a card that converges into the center.",
    )
    combined_label: str = Field(
        description="The combined outcome label, e.g. 'Combined Retirement Risk'",
    )
    combined_severity: str = Field(
        description="'critical' | 'high' | 'medium' — controls the central callout styling",
    )
    outcome_note: str | None = Field(
        default=None,
        description="Optional brief outcome statement shown below the combined callout.",
    )
    outcome_value: str | None = Field(
        default=None,
        description="Optional high-impact hero outcome value (e.g. '-42% Real Wealth', '$180K Gap')",
    )
    outcome_header_label: str | None = Field(
        default=None,
        description="Optional category or header label above the outcome (e.g. 'SYSTEMIC CONVERGENCE')",
    )
    variant: str | None = Field(
        default=None,
        description="'dual_factor' | 'tri_factor' | 'quad_factor' | 'standard'",
    )
    polarity: str | None = Field(
        default=None,
        description="'negative' | 'positive' | 'neutral' | 'critical' | 'high' | 'medium'",
    )


class BrollCaptionData(StrictCompositionData):
    """
    Fallback composition: B-roll/stock image with a caption.

    Used when no specific composition fits the visual intent,
    or when relationship_type is 'broll', 'statement', or 'quote'.
    """
    caption: str = Field(description="The main caption text shown on screen.")
    emphasis_phrase: str | None = Field(
        default=None,
        description="Optional key phrase to emphasize visually within or below the caption.",
    )
    author: str | None = Field(
        default=None,
        description="For quote intents: the person being quoted.",
    )
    header_label: str | None = Field(
        default=None,
        description="Optional eyebrow or category header, e.g. 'CORE PRINCIPLE'.",
    )
    variant: str | None = Field(
        default=None,
        description="'statement' | 'quote' | 'ambient_broll' | 'standard'.",
    )
    source_context: str | None = Field(
        default=None,
        description="Optional publication, book title, or year for quotes/statements.",
    )
    polarity: str | None = Field(
        default=None,
        description="'critical' | 'high' | 'medium' | 'positive' | 'neutral'.",
    )


class ComparisonSplitData(StrictCompositionData):
    """
    Shows a side-by-side comparison of two options, strategies, or values.

    Use for: A vs B comparisons, old vs new, before vs after, options analysis.
    relationship_types: comparison
    """
    left_role: str = Field(description="Name or title of left option, e.g. 'Traditional FD', 'Option A'")
    left_value: str = Field(description="Value or metric for left option, e.g. '6%', '₹50,000'")
    left_label: str | None = Field(default=None, description="Optional supporting label for left option")
    left_unit: str | None = Field(default=None, description="Optional unit for left option, e.g. '%', 'yr'")
    right_role: str = Field(description="Name or title of right option, e.g. 'Mutual Fund SIP', 'Option B'")
    right_value: str = Field(description="Value or metric for right option, e.g. '12%', '₹1,50,000'")
    right_label: str | None = Field(default=None, description="Optional supporting label for right option")
    right_unit: str | None = Field(default=None, description="Optional unit for right option, e.g. '%', 'yr'")
    comparison_label: str | None = Field(default=None, description="Optional comparison title or category, e.g. 'ANNUAL WEALTH'")
    delta: str | None = Field(default=None, description="Optional difference or advantage, e.g. '+6%', '2.5x Growth'")
    winner: str | None = Field(default=None, description="Optional winner: 'left' | 'right'")
    tone: str | None = Field(
        default=None,
        description="Optional color tone: 'neutral' | 'positive_negative' | 'before_after' | 'superiority'",
    )
    header_label: str | None = Field(
        default=None,
        description="Optional category or eyebrow label, e.g. 'HEAD-TO-HEAD COMPARISON', 'STRATEGY BENCHMARK'",
    )
    variant: str | None = Field(
        default=None,
        description="'cards' | 'versus' | 'metric_compare' | 'editorial'",
    )


class RankedItem(StrictCompositionData):
    title: str = Field(description="Item title or name, e.g. 'Housing', 'Automobile'")
    rank: int | str | None = Field(default=None, description="Rank number or label, e.g. 1, 2, '#1'")
    value: str | None = Field(default=None, description="Value or metric display string, e.g. '₹45,000', '40%'")
    subtitle: str | None = Field(default=None, description="Optional brief explanation or detail")
    numeric_value: float | None = Field(default=None, description="Optional raw number for relative bar scaling")
    badge: str | None = Field(default=None, description="Optional badge, e.g. 'Top Expense', 'Highest'")
    change: str | None = Field(default=None, description="Optional change indicator, e.g. '+2', '-1', 'NEW'")


class RankedListData(StrictCompositionData):
    """
    Shows an ordered list of items ranked by magnitude, priority, or importance.

    Use for: top expenses, asset class returns, priority rankings, top contributors.
    relationship_types: ranking
    """
    items: list[RankedItem] = Field(description="List of 2–5 ranked items ordered by rank or value.")
    header_label: str | None = Field(default=None, description="Optional title or category, e.g. 'TOP HOUSEHOLD EXPENSES'")
    show_bars: bool = Field(default=True, description="Whether to show relative proportional comparison bars.")
    variant: str | None = Field(
        default=None,
        description="'standard' | 'dominance' | 'compact'",
    )
    footer_label: str | None = Field(
        default=None,
        description="Optional footer summary or note",
    )


class ProcessStepItem(StrictCompositionData):
    title: str = Field(description="Step title or action name, e.g. 'Earn Income', 'Auto-Debit'")
    subtitle: str | None = Field(default=None, description="Optional brief detail about this step")
    type: str | None = Field(default="step", description="'step' | 'cause' | 'outcome'")
    value: str | None = Field(default=None, description="Optional value or amount, e.g. '₹25,000'")
    connector_label: str | None = Field(
        default=None,
        description="Optional action word connecting to next step, e.g. 'transfers to', 'compounds into'",
    )


class ProcessFlowData(StrictCompositionData):
    """
    Shows sequential steps in a procedure, workflow, or execution process.

    Use for: sequential processes, step-by-step methods, execution flows.
    relationship_types: process
    """
    steps: list[ProcessStepItem] = Field(description="List of 2–5 ordered steps in the process.")
    header_label: str | None = Field(default=None, description="Optional title or category, e.g. 'WEALTH ACCUMULATION PROCESS'")
    layout: str | None = Field(default="auto", description="'horizontal' | 'vertical' | 'auto'")
    variant: str | None = Field(
        default=None,
        description="'horizontal' | 'vertical' | 'auto'",
    )
    footer_label: str | None = Field(
        default=None,
        description="Optional footer summary or note",
    )


# ---------------------------------------------------------------------------
# CompositionDefinition
# ---------------------------------------------------------------------------

class CompositionDefinition(BaseModel):
    """Describes a registered composition in the catalog."""

    composition_id: str
    display_name: str
    description: str  # one-sentence description for the LLM planner prompt
    supported_relationship_types: list[str]  # which intent types this composition serves
    data_model: type[BaseModel]  # Pydantic class for composition_data validation
    allowed_variants: list[str]  # empty = no variants
    asset_requirement: AssetRequirement
    remotion_component_id: str  # matching TSX component name
    fallback_component_id: str  # legacy component used if composition fails
    builder: Callable[[VisualIntent], dict[str, Any]] | None = None
    is_eligible: Callable[[VisualIntent], bool] | None = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def get_data_schema(self) -> dict[str, Any]:
        """
        Generates a clean, dereferenced JSON Schema for this composition's data_model.
        Resolves internal $defs and $ref, removes unsupported fields (additionalProperties),
        and returns a self-contained schema ready for LLM structured output.
        """
        raw_schema = self.data_model.model_json_schema()
        return _clean_and_dereference_schema(raw_schema)

    def describe_for_prompt(self) -> str:
        """Returns the catalog entry string used in the LLM planner system prompt."""
        variants_str = (
            f"  variants: {', '.join(self.allowed_variants)}\n"
            if self.allowed_variants
            else ""
        )
        schema_fields = []
        for name, field in self.data_model.model_fields.items():
            desc = field.description or ""
            required = field.is_required()
            schema_fields.append(
                f"    {name}{'*' if required else '?'}: {desc[:80]}"
            )
        schema_str = "\n".join(schema_fields)
        return (
            f"composition_id: {self.composition_id}\n"
            f"  description: {self.description}\n"
            f"  suits: {', '.join(self.supported_relationship_types)}\n"
            f"{variants_str}"
            f"  data fields (* = required, ? = optional):\n{schema_str}\n"
        )


def _clean_and_dereference_schema(schema: dict[str, Any]) -> dict[str, Any]:
    """Recursively dereference '$ref' pointers, inline '$defs'/'definitions',
    and remove 'additionalProperties' and schema metadata where appropriate.
    """
    defs_map: dict[str, dict[str, Any]] = {}

    def _collect_defs(node: Any) -> None:
        if isinstance(node, dict):
            for def_key in ("$defs", "definitions"):
                if def_key in node and isinstance(node[def_key], dict):
                    for k, v in node[def_key].items():
                        if isinstance(v, dict):
                            defs_map[k] = v
            for v in node.values():
                _collect_defs(v)
        elif isinstance(node, list):
            for item in node:
                _collect_defs(item)

    _collect_defs(schema)

    def _resolve_and_clean(node: Any, visited: set[str] | None = None) -> Any:
        if visited is None:
            visited = set()

        if not isinstance(node, dict):
            if isinstance(node, list):
                return [_resolve_and_clean(item, set(visited)) for item in node]
            return node

        if "$ref" in node and isinstance(node["$ref"], str):
            ref_str = node["$ref"]
            ref_name = ref_str.split("/")[-1]
            if ref_name in defs_map and ref_name not in visited:
                target_def = defs_map[ref_name]
                merged_node = {k: v for k, v in node.items() if k != "$ref"}
                for k, v in target_def.items():
                    if k not in merged_node:
                        merged_node[k] = v
                return _resolve_and_clean(merged_node, visited | {ref_name})

        cleaned: dict[str, Any] = {}
        for k, v in node.items():
            if k in ("additionalProperties", "$defs", "definitions"):
                continue
            cleaned[k] = _resolve_and_clean(v, set(visited))

        return cleaned

    cleaned_schema = _resolve_and_clean(schema)
    return cleaned_schema if isinstance(cleaned_schema, dict) else {}


# ---------------------------------------------------------------------------
# CompositionRegistry
# ---------------------------------------------------------------------------

class CompositionRegistry:
    """
    The closed catalog of authored visual compositions.

    The LLM planner selects from this catalog only.
    New compositions must be explicitly registered here.
    """

    _registry: dict[str, CompositionDefinition] = {}

    @classmethod
    def register(cls, defn: CompositionDefinition) -> None:
        cls._registry[defn.composition_id] = defn

    @classmethod
    def get(cls, composition_id: str) -> CompositionDefinition | None:
        return cls._registry.get(composition_id)

    @classmethod
    def all_ids(cls) -> list[str]:
        return list(cls._registry.keys())

    @classmethod
    def is_registered(cls, composition_id: str) -> bool:
        return composition_id in cls._registry

    @classmethod
    def get_for_relationship_type(cls, rel_type: str) -> list[CompositionDefinition]:
        """Returns all registered compositions that list rel_type in supported_relationship_types."""
        return [
            defn for defn in cls._registry.values()
            if rel_type in defn.supported_relationship_types
        ]

    @classmethod
    def get_data_schema(cls, composition_id: str) -> dict[str, Any] | None:
        """Returns the concrete JSON schema for a registered composition's data model."""
        defn = cls.get(composition_id)
        if defn is None:
            return None
        return defn.get_data_schema()

    @classmethod
    def validate_composition_data(
        cls,
        composition_id: str,
        raw_data: dict[str, Any],
        visual_goal: str = "",
    ) -> tuple[bool, list[str], dict[str, Any]]:
        """
        Validate composition_data against the registered Pydantic model.

        Returns:
            (is_valid, errors, normalized_data)
            normalized_data is the model_dump() on success, or the original raw_data on failure.
        """
        defn = cls.get(composition_id)
        if defn is None:
            return False, [f"Unknown composition_id '{composition_id}'."], raw_data

        try:
            validated = defn.data_model.model_validate(raw_data)
            return True, [], validated.model_dump()
        except Exception as exc:
            errors = [str(exc)]
            return False, errors, raw_data

    @classmethod
    def get_planner_prompt_section(cls) -> str:
        """
        Generates the closed-catalog section injected into the planner system prompt.
        Automatically stays in sync with registered compositions.
        """
        lines = [
            "AVAILABLE COMPOSITIONS (you may ONLY use these composition_ids):\n",
            "=" * 70,
        ]
        for defn in cls._registry.values():
            lines.append(defn.describe_for_prompt())
            lines.append("-" * 40)
        return "\n".join(lines)

    @classmethod
    def build_planner_response_schema(cls) -> dict[str, Any]:
        """
        Generates the JSON Schema for LLM structured output.
        Exposes concrete composition_data schemas for every registered composition
        in a discriminated union (anyOf).
        """
        branches: list[dict[str, Any]] = []

        for defn in cls._registry.values():
            variant_prop: dict[str, Any] = (
                {"type": "string", "enum": defn.allowed_variants, "nullable": True}
                if defn.allowed_variants
                else {"type": "string", "nullable": True}
            )
            if defn.composition_id == "broll_caption":
                asset_query_prop: dict[str, Any] = {
                    "type": "string",
                    "description": (
                        "Concrete 2-6 word stock media visual search query containing physical nouns or visible actions "
                        "(e.g. 'car dealership showroom', 'person reviewing loan documents', 'mechanic replacing tire'). "
                        "Used ONLY to search stock footage providers (Pexels/Pixabay). "
                        "Must NOT be null, must NOT be a full sentence, must NOT contain 'viewer', and must NOT explain concepts."
                    ),
                }
                required_props = [
                    "status",
                    "composition_id",
                    "composition_data",
                    "visual_goal",
                    "asset_query",
                ]
            else:
                asset_query_prop = {"type": "string", "nullable": True}
                required_props = [
                    "status",
                    "composition_id",
                    "composition_data",
                    "visual_goal",
                ]

            branches.append({
                "type": "object",
                "properties": {
                    "status": {"type": "string", "enum": ["ok"]},
                    "composition_id": {
                        "type": "string",
                        "enum": [defn.composition_id],
                    },
                    "variant": variant_prop,
                    "composition_data": defn.get_data_schema(),
                    "asset_requirement": {
                        "type": "string",
                        "enum": [e.value for e in AssetRequirement],
                    },
                    "asset_query": asset_query_prop,
                    "trigger_word": {"type": "string", "nullable": True},
                    "visual_goal": {"type": "string"},
                },
                "required": required_props,
            })

        branches.append({
            "type": "object",
            "properties": {
                "status": {"type": "string", "enum": ["no_suitable_composition"]},
                "reason": {"type": "string"},
            },
            "required": ["status", "reason"],
        })

        return {"anyOf": branches}


# ---------------------------------------------------------------------------
# Registration — initial catalog
# ---------------------------------------------------------------------------

CompositionRegistry.register(
    CompositionDefinition(
        composition_id="metric_hero",
        display_name="Metric Hero",
        description="A single important metric displayed with strong visual emphasis.",
        supported_relationship_types=["metric"],
        data_model=MetricHeroData,
        allowed_variants=[
            "hero_milestone",
            "supporting_metric",
            "warning_metric",
            "before_after_metric",
            "hero",
            "supporting",
        ],
        asset_requirement=AssetRequirement.NONE,
        remotion_component_id="MetricHero",
        fallback_component_id="NumberCounter",
        builder=build_metric_hero_data,
        is_eligible=is_eligible_metric_hero,
    )
)

CompositionRegistry.register(
    CompositionDefinition(
        composition_id="calculation_story",
        display_name="Calculation Story",
        description="Shows an input × rate → result math argument, or an input → result financial transformation.",
        supported_relationship_types=["calculation"],
        data_model=CalculationStoryData,
        allowed_variants=[
            "multiplication",
            "addition",
            "subtraction",
            "allocation",
            "growth",
            "neutral",
        ],
        asset_requirement=AssetRequirement.NONE,
        remotion_component_id="CalculationStory",
        fallback_component_id="SplitComparison",
        builder=build_calculation_story_data,
        is_eligible=is_eligible_calculation_story,
    )
)

CompositionRegistry.register(
    CompositionDefinition(
        composition_id="cause_effect",
        display_name="Cause & Effect",
        description="Shows 1–3 causes converging via arrows into a single outcome.",
        supported_relationship_types=["cause_effect"],
        data_model=CauseEffectData,
        allowed_variants=["single_cause", "dual_cause", "multi_cause", "standard"],
        asset_requirement=AssetRequirement.NONE,
        remotion_component_id="CauseEffect",
        fallback_component_id="ProcessFlow",
        builder=build_cause_effect_data,
        is_eligible=is_eligible_cause_effect,
    )
)

CompositionRegistry.register(
    CompositionDefinition(
        composition_id="comparison_split",
        display_name="Comparison Split",
        description="Shows a side-by-side comparison of two options, strategies, or values.",
        supported_relationship_types=["comparison"],
        data_model=ComparisonSplitData,
        allowed_variants=["cards", "versus", "metric_compare", "editorial"],
        asset_requirement=AssetRequirement.NONE,
        remotion_component_id="SplitComparison",
        fallback_component_id="Typography",
        builder=build_comparison_split_data,
        is_eligible=is_eligible_comparison_split,
    )
)

CompositionRegistry.register(
    CompositionDefinition(
        composition_id="ranked_list",
        display_name="Ranked List",
        description="Shows an ordered list of items by rank, magnitude, or priority.",
        supported_relationship_types=["ranking"],
        data_model=RankedListData,
        allowed_variants=["standard", "dominance", "compact"],
        asset_requirement=AssetRequirement.NONE,
        remotion_component_id="RankedList",
        fallback_component_id="Typography",
        builder=build_ranked_list_data,
        is_eligible=is_eligible_ranked_list,
    )
)

CompositionRegistry.register(
    CompositionDefinition(
        composition_id="process_flow",
        display_name="Process Flow",
        description="Shows sequential steps in a procedure, workflow, or timeline of actions.",
        supported_relationship_types=["process"],
        data_model=ProcessFlowData,
        allowed_variants=["horizontal", "vertical", "auto"],
        asset_requirement=AssetRequirement.NONE,
        remotion_component_id="ProcessFlow",
        fallback_component_id="Typography",
        builder=build_process_flow_data,
        is_eligible=is_eligible_process_flow,
    )
)

CompositionRegistry.register(
    CompositionDefinition(
        composition_id="time_decay",
        display_name="Time Decay",
        description="Shows a fixed value losing purchasing power or real value over time (strictly decline/erosion).",
        supported_relationship_types=["decline", "trend"],
        data_model=TimeDecayData,
        allowed_variants=[
            "mild_decay",
            "severe_decay",
            "inflation_erosion",
            "single_period_drop",
            "standard",
        ],
        asset_requirement=AssetRequirement.NONE,
        remotion_component_id="TimeDecay",
        fallback_component_id="Charts",
        builder=build_time_decay_data,
        is_eligible=is_eligible_time_decay,
    )
)

CompositionRegistry.register(
    CompositionDefinition(
        composition_id="growth_trajectory",
        display_name="Growth Trajectory",
        description="Shows a single quantity, corpus, or asset growing upward over time (linear savings, compounding snowball, accelerating returns).",
        supported_relationship_types=["growth"],
        data_model=GrowthTrajectoryData,
        allowed_variants=[
            "linear_accumulation",
            "accelerating_growth",
            "compounding_snowball",
            "milestone_progression",
            "standard",
        ],
        asset_requirement=AssetRequirement.NONE,
        remotion_component_id="GrowthTrajectory",
        fallback_component_id="Charts",
        builder=build_growth_trajectory_data,
        is_eligible=is_eligible_growth_trajectory,
    )
)

CompositionRegistry.register(
    CompositionDefinition(
        composition_id="multi_factor_pressure",
        display_name="Multi-Factor Pressure",
        description="Shows 2–4 independent risk factors converging into combined pressure.",
        supported_relationship_types=["multi_factor"],
        data_model=MultiFactorPressureData,
        allowed_variants=["dual_factor", "tri_factor", "quad_factor", "standard"],
        asset_requirement=AssetRequirement.NONE,
        remotion_component_id="MultiFactorPressure",
        fallback_component_id="ProgressiveList",
        builder=build_multi_factor_pressure_data,
        is_eligible=is_eligible_multi_factor_pressure,
    )
)

CompositionRegistry.register(
    CompositionDefinition(
        composition_id="trajectory_divergence",
        display_name="Trajectory Divergence",
        description="Shows two financial paths evolving in opposite directions over time — investing vs spending, equity vs debt — revealing a growing wealth gap.",
        supported_relationship_types=["divergence"],
        data_model=TrajectoryDivergenceData,
        allowed_variants=["divergence", "wealth_gap", "cost_opportunity", "standard"],
        asset_requirement=AssetRequirement.NONE,
        remotion_component_id="TrajectoryDivergence",
        fallback_component_id="Charts",
        builder=build_trajectory_divergence_data,
        is_eligible=is_eligible_trajectory_divergence,
    )
)

CompositionRegistry.register(
    CompositionDefinition(
        composition_id="cash_flow_waterfall",
        display_name="Cash Flow Waterfall",
        description="Shows a starting resource (salary, corpus) being sequentially depleted by labeled deductions to reveal a final remaining balance.",
        supported_relationship_types=["waterfall"],
        data_model=CashFlowWaterfallData,
        allowed_variants=["standard", "detailed", "compact"],
        asset_requirement=AssetRequirement.NONE,
        remotion_component_id="CashFlowWaterfall",
        fallback_component_id="Charts",
        builder=build_cash_flow_waterfall_data,
        is_eligible=is_eligible_cash_flow_waterfall,
    )
)

CompositionRegistry.register(
    CompositionDefinition(
        composition_id="broll_caption",
        display_name="B-Roll Caption",
        description=(
            "Safe fallback: B-roll/stock image with a text caption. "
            "Use when no specific composition fits, or for atmospheric/statement/quote moments."
        ),
        supported_relationship_types=["broll", "statement", "quote", "definition"],
        data_model=BrollCaptionData,
        allowed_variants=["statement", "quote", "ambient_broll", "standard"],
        asset_requirement=AssetRequirement.OPTIONAL_BROLL,
        remotion_component_id="BrollCaption",
        fallback_component_id="Typography",
        builder=build_broll_caption_data,
        is_eligible=is_eligible_broll_caption,
    )
)
