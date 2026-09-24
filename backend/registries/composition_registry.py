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

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


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

class MetricHeroData(BaseModel):
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


class CalculationStoryData(BaseModel):
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


class CauseItem(BaseModel):
    label: str = Field(description="Short label for this cause, e.g. 'High Inflation'")
    value: str | None = Field(default=None, description="Optional value, e.g. '7%'")
    icon: str | None = Field(
        default=None,
        description="Optional emoji or icon name hint, e.g. '📈', 'inflation'",
    )


class CauseEffectData(BaseModel):
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


class TimeDecayData(BaseModel):
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


class FactorItem(BaseModel):
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


class MultiFactorPressureData(BaseModel):
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


class BrollCaptionData(BaseModel):
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


class ComparisonSplitData(BaseModel):
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


class RankedItem(BaseModel):
    title: str = Field(description="Item title or name, e.g. 'Housing', 'Automobile'")
    rank: int | str | None = Field(default=None, description="Rank number or label, e.g. 1, 2, '#1'")
    value: str | None = Field(default=None, description="Value or metric display string, e.g. '₹45,000', '40%'")
    subtitle: str | None = Field(default=None, description="Optional brief explanation or detail")
    numeric_value: float | None = Field(default=None, description="Optional raw number for relative bar scaling")
    badge: str | None = Field(default=None, description="Optional badge, e.g. 'Top Expense', 'Highest'")


class RankedListData(BaseModel):
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


class ProcessStepItem(BaseModel):
    title: str = Field(description="Step title or action name, e.g. 'Earn Income', 'Auto-Debit'")
    subtitle: str | None = Field(default=None, description="Optional brief detail about this step")
    type: str | None = Field(default="step", description="'step' | 'cause' | 'outcome'")
    value: str | None = Field(default=None, description="Optional value or amount, e.g. '₹25,000'")
    connector_label: str | None = Field(
        default=None,
        description="Optional action word connecting to next step, e.g. 'transfers to', 'compounds into'",
    )


class ProcessFlowData(BaseModel):
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
    )
)
