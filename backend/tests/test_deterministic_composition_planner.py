"""
Tests for Deterministic Composition Planner Engine.

Validates the full deterministic Python composition planning migration:
1. Dynamic iteration across all VALID_RELATIONSHIP_TYPES.
2. Disambiguation logic for multi-target relationships (comparison, trend).
3. Authoritative builder and Pydantic validation across all 12 registered compositions.
4. Strict factual non-fabrication.
5. Absolute zero-provider execution (no LLM calls, works with provider=None or crashing provider).
6. Open-Closed extensibility (future compositions register cleanly without modifying the engine).
"""
import pytest
from typing import Any
from pydantic import ValidationError
from domain.visual_intent import (
    VisualIntent,
    VALID_RELATIONSHIP_TYPES,
    SemanticEntity,
    QuantitativeMeasurement,
    TemporalContext,
    CausalStructure,
    ComparisonStructure,
    VisualDynamics,
)
from engines.composition_planner_engine import (
    CompositionPlannerEngine,
    CompositionPlannerResult,
    CompositionPlannerEngineError,
)
from registries.composition_registry import (
    CompositionRegistry,
    CompositionDefinition,
    AssetRequirement,
)
from pydantic import BaseModel, Field


class ExplodingLLMProvider:
    """Mock provider that raises an exception if any method is called."""
    def generate_json(self, *args: Any, **kwargs: Any) -> Any:
        raise AssertionError("Deterministic CompositionPlannerEngine must NEVER call llm_provider!")


# ===========================================================================
# 1. Zero-Provider Execution Guarantees
# ===========================================================================

def test_planner_runs_with_none_provider() -> None:
    """Planner must operate completely without any LLM provider instance."""
    engine = CompositionPlannerEngine(llm_provider=None)
    intent = VisualIntent(
        intent_id="test_zero_prov",
        narration_excerpt="Retire with ₹50 lakh in investments.",
        what_viewer_must_understand="₹50 lakh is the opening portfolio target.",
        key_values=["₹50 lakh"],
        relationship_type="metric",
        measurements=[
            QuantitativeMeasurement(raw_value="₹50 lakh", metric_name="Portfolio Target", role="input")
        ],
    )
    result = engine.run(intent=intent, beat_id="beat_zero_01")
    assert isinstance(result, CompositionPlannerResult)
    assert result.beat.composition_id == "metric_hero"
    assert result.provider_metadata.provider == "deterministic_python"
    assert result.used_fallback is False


def test_planner_never_invokes_exploding_provider() -> None:
    """Planner must never call any method on llm_provider when one is supplied."""
    exploding_provider = ExplodingLLMProvider()
    engine = CompositionPlannerEngine(llm_provider=exploding_provider)  # type: ignore[arg-type]
    intent = VisualIntent(
        intent_id="test_exploding",
        narration_excerpt="Save ₹10 lakh for financial freedom.",
        what_viewer_must_understand="₹10 lakh milestone.",
        key_values=["₹10 lakh"],
        relationship_type="metric",
        measurements=[
            QuantitativeMeasurement(raw_value="₹10 lakh", metric_name="Milestone Target", role="input")
        ],
    )
    # Should not raise AssertionError
    result = engine.run(intent=intent, beat_id="beat_exploding_01")
    assert result.beat.composition_id == "metric_hero"


# ===========================================================================
# 2. Dynamic Iteration Across All VALID_RELATIONSHIP_TYPES
# ===========================================================================

def make_valid_intent_for_rel_type(rel_type: str) -> VisualIntent:
    if rel_type == "metric":
        return VisualIntent(
            intent_id=f"intent_{rel_type}",
            narration_excerpt="Save ₹50 lakh for retirement.",
            what_viewer_must_understand="₹50 lakh retirement target.",
            relationship_type=rel_type,
            measurements=[QuantitativeMeasurement(raw_value="₹50 lakh", metric_name="Retirement Target", role="input")],
        )
    elif rel_type == "calculation":
        return VisualIntent(
            intent_id=f"intent_{rel_type}",
            narration_excerpt="₹10 lakh compounded at 12% gives ₹31 lakh.",
            what_viewer_must_understand="Calculation story.",
            relationship_type=rel_type,
            measurements=[
                QuantitativeMeasurement(raw_value="₹10 lakh", metric_name="Principal", role="input"),
                QuantitativeMeasurement(raw_value="₹31 lakh", metric_name="Final Balance", role="result"),
            ],
        )
    elif rel_type == "cause_effect":
        return VisualIntent(
            intent_id=f"intent_{rel_type}",
            narration_excerpt="Delaying investing reduces wealth.",
            what_viewer_must_understand="Delay causes wealth reduction.",
            relationship_type=rel_type,
            causal=CausalStructure(causes=["Delaying 5 years"], outcome="40% Wealth Drop", outcome_severity="critical"),
        )
    elif rel_type == "multi_factor":
        return VisualIntent(
            intent_id=f"intent_{rel_type}",
            narration_excerpt="Inflation and taxes erode portfolio returns.",
            what_viewer_must_understand="Multiple factors erode returns.",
            relationship_type=rel_type,
            causal=CausalStructure(causes=["Inflation Drag", "Tax Drag"], outcome="Negative Return", outcome_severity="critical"),
        )
    elif rel_type == "comparison":
        return VisualIntent(
            intent_id=f"intent_{rel_type}",
            narration_excerpt="FD at 6% versus Equity at 12%.",
            what_viewer_must_understand="Comparison of options.",
            relationship_type=rel_type,
            comparison=ComparisonStructure(
                subject_a="FD",
                value_a="6%",
                subject_b="Equity",
                value_b="12%",
                comparison_dimension="Annual Return",
            ),
        )
    elif rel_type == "trend":
        return VisualIntent(
            intent_id=f"intent_{rel_type}",
            narration_excerpt="Purchasing power erodes over time.",
            what_viewer_must_understand="Erosion over time.",
            relationship_type=rel_type,
            temporal=TemporalContext(horizon="10 Years", is_decay_over_time=True),
            measurements=[
                QuantitativeMeasurement(raw_value="₹10 Lakh", role="baseline", entity_name="Purchasing Power"),
                QuantitativeMeasurement(raw_value="40%", role="delta", direction="down"),
            ],
        )
    elif rel_type == "growth":
        return VisualIntent(
            intent_id=f"intent_{rel_type}",
            narration_excerpt="₹1 lakh grows to ₹10 lakh.",
            what_viewer_must_understand="Growth trajectory.",
            relationship_type=rel_type,
            measurements=[
                QuantitativeMeasurement(raw_value="₹1 lakh", metric_name="Starting Point", role="input"),
                QuantitativeMeasurement(raw_value="₹10 lakh", metric_name="Ending Corpus", role="result"),
            ],
        )
    elif rel_type == "divergence":
        return VisualIntent(
            intent_id=f"intent_{rel_type}",
            narration_excerpt="Investing diverges from spending over 20 years.",
            what_viewer_must_understand="Divergence over time.",
            relationship_type=rel_type,
            temporal=TemporalContext(horizon="20 years"),
            comparison=ComparisonStructure(
                subject_a="Investing",
                value_a="₹1.5 Crore",
                subject_b="Spending",
                value_b="₹0",
                comparison_dimension="Net Wealth",
            ),
        )
    elif rel_type == "waterfall":
        return VisualIntent(
            intent_id=f"intent_{rel_type}",
            narration_excerpt="Salary of ₹1 lakh minus expenses.",
            what_viewer_must_understand="Waterfall depletion.",
            relationship_type=rel_type,
            measurements=[
                QuantitativeMeasurement(raw_value="₹1,00,000", role="baseline", metric_name="Salary", numeric_value=100000),
                QuantitativeMeasurement(raw_value="₹30,000", role="delta", metric_name="Expenses", numeric_value=30000, direction="down"),
            ],
        )
    elif rel_type == "decline":
        return VisualIntent(
            intent_id=f"intent_{rel_type}",
            narration_excerpt="Value decays over 10 years.",
            what_viewer_must_understand="Value decay.",
            relationship_type=rel_type,
            temporal=TemporalContext(horizon="10 Years", is_decay_over_time=True),
            measurements=[
                QuantitativeMeasurement(raw_value="₹50,000", role="baseline", entity_name="Pension"),
                QuantitativeMeasurement(raw_value="50%", role="delta", direction="down"),
            ],
        )
    elif rel_type == "ranking":
        return VisualIntent(
            intent_id=f"intent_{rel_type}",
            narration_excerpt="Ranking assets.",
            what_viewer_must_understand="Asset rankings.",
            relationship_type=rel_type,
            entities=[SemanticEntity(name="Asset A"), SemanticEntity(name="Asset B")],
        )
    elif rel_type == "process":
        return VisualIntent(
            intent_id=f"intent_{rel_type}",
            narration_excerpt="Steps in investing.",
            what_viewer_must_understand="Process steps.",
            relationship_type=rel_type,
            entities=[SemanticEntity(name="Step 1"), SemanticEntity(name="Step 2")],
        )
    elif rel_type in ("statement", "quote", "definition", "broll"):
        return VisualIntent(
            intent_id=f"intent_{rel_type}",
            narration_excerpt=f"This is a {rel_type} narrative.",
            what_viewer_must_understand=f"Understand {rel_type}.",
            relationship_type=rel_type,
        )
    else:
        # Unsupported relationship type
        return VisualIntent(
            intent_id=f"intent_{rel_type}",
            narration_excerpt=f"Testing {rel_type}.",
            what_viewer_must_understand=f"Understand {rel_type}.",
            relationship_type=rel_type,
        )


def test_all_relationship_types_produce_valid_result() -> None:
    """Every supported relationship type must execute cleanly; unsupported types must fail fast."""
    engine = CompositionPlannerEngine()
    registered_ids = set(CompositionRegistry.all_ids())

    unsupported_types = {"amortization", "accumulation"}

    for rel_type in VALID_RELATIONSHIP_TYPES:
        intent = make_valid_intent_for_rel_type(rel_type)
        if rel_type in unsupported_types:
            with pytest.raises(CompositionPlannerEngineError) as exc_info:
                engine.run(intent=intent, beat_id=f"beat_{rel_type}")
            assert "unsupported" in str(exc_info.value).lower()
        else:
            result = engine.run(intent=intent, beat_id=f"beat_{rel_type}")
            assert isinstance(result, CompositionPlannerResult)
            assert result.beat.composition_id in registered_ids
            assert result.used_fallback is False
            assert result.beat.composition_data is not None
            assert isinstance(result.beat.composition_data, dict)


# ===========================================================================
# 3. Disambiguation Logic: comparison & trend
# ===========================================================================

def test_comparison_with_temporal_and_dual_paths_routes_to_trajectory_divergence() -> None:
    """explicit divergence relationship_type + temporal horizon + dual paths -> trajectory_divergence."""
    engine = CompositionPlannerEngine()
    intent = VisualIntent(
        intent_id="cmp_div_01",
        narration_excerpt="Over 25 years, investing in equity creates ₹2 Crore while spending leaves zero.",
        what_viewer_must_understand="Equity compounding diverges massively from spending.",
        key_values=["25 years", "₹2 Crore", "₹0"],
        relationship_type="divergence",
        temporal=TemporalContext(horizon="25 years"),
        comparison=ComparisonStructure(
            subject_a="Equity Investing",
            value_a="₹2 Crore",
            subject_b="Uncontrolled Spending",
            value_b="₹0",
            comparison_dimension="Long-Term Wealth",
            delta="₹2 Crore Gap",
            winner="Equity Investing",
        ),
    )
    result = engine.run(intent=intent, beat_id="beat_div_01")
    assert result.used_fallback is False
    assert result.beat.composition_id == "trajectory_divergence"
    defn = CompositionRegistry.get("trajectory_divergence")
    assert defn is not None
    # Validate against Pydantic data_model
    defn.data_model(**result.beat.composition_data)


def test_static_comparison_routes_to_comparison_split() -> None:
    """comparison without temporal horizon -> comparison_split."""
    engine = CompositionPlannerEngine()
    intent = VisualIntent(
        intent_id="cmp_split_01",
        narration_excerpt="Comparing Gold at 8% against Equities at 12%.",
        what_viewer_must_understand="Equities yield 4% more than Gold annually.",
        key_values=["8%", "12%"],
        relationship_type="comparison",
        comparison=ComparisonStructure(
            subject_a="Gold",
            value_a="8%",
            subject_b="Equities",
            value_b="12%",
            comparison_dimension="Annual Return",
            delta="+4%",
            winner="Equities",
        ),
    )
    result = engine.run(intent=intent, beat_id="beat_split_01")
    assert result.used_fallback is False
    assert result.beat.composition_id == "comparison_split"
    defn = CompositionRegistry.get("comparison_split")
    assert defn is not None
    defn.data_model(**result.beat.composition_data)


def test_insufficient_comparison_fails_fast() -> None:
    """comparison lacking structured entities or values -> fails fast with CompositionPlannerEngineError or ValidationError."""
    engine = CompositionPlannerEngine()
    with pytest.raises((CompositionPlannerEngineError, ValidationError)):
        intent = VisualIntent(
            intent_id="cmp_empty_01",
            narration_excerpt="Consider comparing the two options available to you.",
            what_viewer_must_understand="Both choices carry consequences.",
            key_values=[],
            relationship_type="comparison",
        )
        engine.run(intent=intent, beat_id="beat_cmp_empty")


def test_declining_trend_routes_to_time_decay() -> None:
    """trend with decline semantics -> time_decay."""
    engine = CompositionPlannerEngine()
    intent = VisualIntent(
        intent_id="trend_dec_01",
        narration_excerpt="Inflation causes purchasing power to erode sharply over 10 years.",
        what_viewer_must_understand="Purchasing power erodes downward over the decade.",
        key_values=["₹10 Lakh", "10 Years"],
        relationship_type="trend",
        temporal=TemporalContext(horizon="10 Years", is_decay_over_time=True),
        measurements=[
            QuantitativeMeasurement(raw_value="₹10 Lakh", role="baseline", entity_name="Purchasing Power"),
            QuantitativeMeasurement(raw_value="40%", role="delta", direction="down"),
        ],
    )
    result = engine.run(intent=intent, beat_id="beat_trend_dec")
    assert result.used_fallback is False
    assert result.beat.composition_id == "time_decay"
    defn = CompositionRegistry.get("time_decay")
    assert defn is not None
    defn.data_model(**result.beat.composition_data)


def test_growing_trend_routes_to_growth_trajectory() -> None:
    """trend with growth semantics -> growth_trajectory."""
    engine = CompositionPlannerEngine()
    intent = VisualIntent(
        intent_id="trend_growth_01",
        narration_excerpt="Your portfolio grows from ₹10 Lakh to ₹1 Crore over 15 years.",
        what_viewer_must_understand="Wealth compounds exponentially over time.",
        key_values=["₹10 Lakh", "₹1 Crore"],
        relationship_type="trend",
        measurements=[
            QuantitativeMeasurement(raw_value="₹10 Lakh", role="baseline", entity_name="Portfolio"),
            QuantitativeMeasurement(raw_value="₹1 Crore", role="result", entity_name="Portfolio", direction="up"),
        ],
    )
    result = engine.run(intent=intent, beat_id="beat_trend_growth")
    assert result.used_fallback is False
    assert result.beat.composition_id == "growth_trajectory"
    defn = CompositionRegistry.get("growth_trajectory")
    assert defn is not None
    defn.data_model(**result.beat.composition_data)


def test_ambiguous_trend_fails_fast() -> None:
    """trend without clear upward or downward direction -> fails fast with CompositionPlannerEngineError."""
    engine = CompositionPlannerEngine()
    intent = VisualIntent(
        intent_id="trend_amb_01",
        narration_excerpt="Market cycles shift back and forth unpredictably.",
        what_viewer_must_understand="Cycles fluctuate over the horizon.",
        key_values=[],
        relationship_type="trend",
        temporal=TemporalContext(horizon="10 years"),
    )
    with pytest.raises(CompositionPlannerEngineError) as exc_info:
        engine.run(intent=intent, beat_id="beat_trend_amb")
    assert "trend direction is ambiguous" in str(exc_info.value)


# ===========================================================================
# 4. Authoritative Builders for All 12 Registered Compositions
# ===========================================================================

def test_builder_metric_hero() -> None:
    engine = CompositionPlannerEngine()
    intent = VisualIntent(
        intent_id="int_metric",
        narration_excerpt="Your starting capital is ₹25 Lakh.",
        what_viewer_must_understand="₹25 Lakh initial capital.",
        key_values=["₹25 Lakh"],
        relationship_type="metric",
        measurements=[
            QuantitativeMeasurement(raw_value="₹25 Lakh", entity_name="Initial Capital", role="input")
        ],
    )
    result = engine.run(intent=intent, beat_id="beat_metric")
    assert result.beat.composition_id == "metric_hero"
    assert result.beat.composition_data["value"] == "₹25 Lakh"
    defn = CompositionRegistry.get("metric_hero")
    assert defn is not None
    defn.data_model(**result.beat.composition_data)


def test_builder_calculation_story() -> None:
    engine = CompositionPlannerEngine()
    intent = VisualIntent(
        intent_id="int_calc",
        narration_excerpt="Starting with ₹10 Lakh, a 12% annual return compounds into ₹31 Lakh.",
        what_viewer_must_understand="₹10 Lakh compounded at 12% equals ₹31 Lakh.",
        key_values=["₹10 Lakh", "12%", "₹31 Lakh"],
        relationship_type="calculation",
        measurements=[
            QuantitativeMeasurement(raw_value="₹10 Lakh", role="input", metric_name="Principal"),
            QuantitativeMeasurement(raw_value="12%", role="rate", metric_name="CAGR"),
            QuantitativeMeasurement(raw_value="₹31 Lakh", role="result", metric_name="Ending Balance"),
        ],
    )
    result = engine.run(intent=intent, beat_id="beat_calc")
    assert result.beat.composition_id == "calculation_story"
    assert result.beat.composition_data["input_value"] == "₹10 Lakh"
    assert result.beat.composition_data["result_value"] == "₹31 Lakh"
    defn = CompositionRegistry.get("calculation_story")
    assert defn is not None
    defn.data_model(**result.beat.composition_data)


def test_builder_cause_effect() -> None:
    engine = CompositionPlannerEngine()
    intent = VisualIntent(
        intent_id="int_ce",
        narration_excerpt="Delaying investing by 5 years reduces your retirement corpus by 40%.",
        what_viewer_must_understand="5-year delay leads to massive corpus reduction.",
        key_values=["5 years", "40%"],
        relationship_type="cause_effect",
        causal=CausalStructure(
            causes=["5-Year Delay in SIP"],
            outcome="40% Reduction in Retirement Wealth",
            outcome_severity="critical",
        ),
        trigger_word="leads to",
    )
    result = engine.run(intent=intent, beat_id="beat_ce")
    assert result.beat.composition_id == "cause_effect"
    assert result.beat.composition_data["outcome_label"] == "40% Reduction in Retirement Wealth"
    defn = CompositionRegistry.get("cause_effect")
    assert defn is not None
    defn.data_model(**result.beat.composition_data)


def test_builder_multi_factor_pressure() -> None:
    engine = CompositionPlannerEngine()
    intent = VisualIntent(
        intent_id="int_mf",
        narration_excerpt="Inflation at 6% and taxes at 30% erode portfolio real returns.",
        what_viewer_must_understand="Dual pressures erode net wealth.",
        key_values=["6%", "30%"],
        relationship_type="multi_factor",
        causal=CausalStructure(
            causes=["Inflation Drag (6%)", "Tax Leakage (30%)"],
            outcome="Sub-Zero Real Return",
            outcome_severity="critical",
        ),
    )
    result = engine.run(intent=intent, beat_id="beat_mf")
    assert result.beat.composition_id == "multi_factor_pressure"
    assert len(result.beat.composition_data["factors"]) >= 2
    defn = CompositionRegistry.get("multi_factor_pressure")
    assert defn is not None
    defn.data_model(**result.beat.composition_data)


def test_builder_ranked_list() -> None:
    engine = CompositionPlannerEngine()
    intent = VisualIntent(
        intent_id="int_rnk",
        narration_excerpt="Here are the top three wealth-building assets: Equities, Real Estate, and Gold.",
        what_viewer_must_understand="Equities rank highest in wealth creation.",
        key_values=["Equities", "Real Estate", "Gold"],
        relationship_type="ranking",
        entities=[
            SemanticEntity(name="Equities", role="subject"),
            SemanticEntity(name="Real Estate", role="subject"),
            SemanticEntity(name="Gold", role="subject"),
        ],
    )
    result = engine.run(intent=intent, beat_id="beat_rnk")
    assert result.beat.composition_id == "ranked_list"
    assert len(result.beat.composition_data["items"]) == 3
    defn = CompositionRegistry.get("ranked_list")
    assert defn is not None
    defn.data_model(**result.beat.composition_data)


def test_builder_process_flow() -> None:
    engine = CompositionPlannerEngine()
    intent = VisualIntent(
        intent_id="int_proc",
        narration_excerpt="First earn, second automate savings, third reinvest all dividends.",
        what_viewer_must_understand="A clear three-step compounding cycle.",
        key_values=["Step 1", "Step 2"],
        relationship_type="process",
        entities=[
            SemanticEntity(name="Earn Income"),
            SemanticEntity(name="Automate Savings"),
            SemanticEntity(name="Reinvest Dividends"),
        ],
    )
    result = engine.run(intent=intent, beat_id="beat_proc")
    assert result.beat.composition_id == "process_flow"
    assert len(result.beat.composition_data["steps"]) == 3
    defn = CompositionRegistry.get("process_flow")
    assert defn is not None
    defn.data_model(**result.beat.composition_data)


def test_builder_time_decay() -> None:
    engine = CompositionPlannerEngine()
    intent = VisualIntent(
        intent_id="int_decay",
        narration_excerpt="Over 20 years, a fixed ₹50,000 monthly pension loses half its real value.",
        what_viewer_must_understand="Value erodes significantly over 20 years.",
        key_values=["₹50,000", "20 Years"],
        relationship_type="decline",
        temporal=TemporalContext(horizon="20 Years", is_decay_over_time=True),
        measurements=[
            QuantitativeMeasurement(raw_value="₹50,000", entity_name="Monthly Pension", role="baseline"),
            QuantitativeMeasurement(raw_value="50%", role="delta", direction="down"),
        ],
    )
    result = engine.run(intent=intent, beat_id="beat_decay")
    assert result.beat.composition_id == "time_decay"
    assert result.beat.composition_data["fixed_amount"] == "₹50,000"
    defn = CompositionRegistry.get("time_decay")
    assert defn is not None
    defn.data_model(**result.beat.composition_data)


def test_builder_growth_trajectory() -> None:
    engine = CompositionPlannerEngine()
    intent = VisualIntent(
        intent_id="int_growth",
        narration_excerpt="Starting with ₹1 Lakh, disciplined monthly SIPs compound to ₹1 Crore in 20 years.",
        what_viewer_must_understand="The portfolio grows from ₹1 Lakh to ₹1 Crore.",
        key_values=["₹1 Lakh", "₹1 Crore"],
        relationship_type="growth",
        temporal=TemporalContext(horizon="20 years"),
        measurements=[
            QuantitativeMeasurement(raw_value="₹1 Lakh", role="baseline", entity_name="Starting Principal"),
            QuantitativeMeasurement(raw_value="₹1 Crore", role="result", entity_name="Final Corpus"),
        ],
    )
    result = engine.run(intent=intent, beat_id="beat_growth")
    assert result.beat.composition_id == "growth_trajectory"
    assert result.beat.composition_data["start_value"] == "₹1 Lakh"
    assert result.beat.composition_data["end_value"] == "₹1 Crore"
    defn = CompositionRegistry.get("growth_trajectory")
    assert defn is not None
    defn.data_model(**result.beat.composition_data)


def test_builder_cash_flow_waterfall() -> None:
    engine = CompositionPlannerEngine()
    intent = VisualIntent(
        intent_id="int_wf",
        narration_excerpt="From a ₹1,00,000 gross salary, taxes take ₹20,000 and living expenses take ₹50,000, leaving ₹30,000.",
        what_viewer_must_understand="Gross income is reduced by taxes and expenses into net savings.",
        key_values=["₹1,00,000", "₹20,000", "₹50,000", "₹30,000"],
        relationship_type="waterfall",
        measurements=[
            QuantitativeMeasurement(raw_value="₹1,00,000", role="baseline", metric_name="Gross Salary", numeric_value=100000),
            QuantitativeMeasurement(raw_value="₹20,000", role="delta", metric_name="Taxes", numeric_value=20000, direction="down"),
            QuantitativeMeasurement(raw_value="₹50,000", role="delta", metric_name="Living Costs", numeric_value=50000, direction="down"),
            QuantitativeMeasurement(raw_value="₹30,000", role="result", metric_name="Net Savings", numeric_value=30000),
        ],
    )
    result = engine.run(intent=intent, beat_id="beat_wf")
    assert result.beat.composition_id == "cash_flow_waterfall"
    assert result.beat.composition_data["starting_value"] == "₹1,00,000"
    assert len(result.beat.composition_data["steps"]) >= 2
    defn = CompositionRegistry.get("cash_flow_waterfall")
    assert defn is not None
    defn.data_model(**result.beat.composition_data)


def test_builder_broll_caption() -> None:
    engine = CompositionPlannerEngine()
    intent = VisualIntent(
        intent_id="int_broll",
        narration_excerpt="Rule number one of investing: never lose money.",
        what_viewer_must_understand="Capital preservation is paramount.",
        key_values=[],
        relationship_type="quote",
        trigger_word="rule",
    )
    result = engine.run(intent=intent, beat_id="beat_broll")
    assert result.beat.composition_id == "broll_caption"
    assert result.beat.composition_data["caption"] == "Capital preservation is paramount."
    defn = CompositionRegistry.get("broll_caption")
    assert defn is not None
    defn.data_model(**result.beat.composition_data)


def test_builder_trajectory_divergence() -> None:
    engine = CompositionPlannerEngine()
    intent = VisualIntent(
        intent_id="int_diverge",
        narration_excerpt="Over 20 years, investing compounds to ₹1.5 Crore while saving cash yields only ₹25 Lakh.",
        what_viewer_must_understand="The compounding path diverges from the cash path.",
        key_values=["₹1.5 Crore", "₹25 Lakh", "20 years"],
        relationship_type="divergence",
        temporal=TemporalContext(horizon="20 years"),
        comparison=ComparisonStructure(
            subject_a="Investing Path",
            value_a="₹1.5 Crore",
            subject_b="Cash Savings Path",
            value_b="₹25 Lakh",
            comparison_dimension="Net Corpus",
            delta="₹1.25 Crore Advantage",
            winner="Investing Path",
        ),
    )
    result = engine.run(intent=intent, beat_id="beat_div")
    assert result.beat.composition_id == "trajectory_divergence"
    assert result.beat.composition_data["path_a"]["label"] == "Investing Path"
    assert result.beat.composition_data["path_a"]["end_value"] == "₹1.5 Crore"
    assert result.beat.composition_data["path_b"]["label"] == "Cash Savings Path"
    assert result.beat.composition_data["path_b"]["end_value"] == "₹25 Lakh"
    defn = CompositionRegistry.get("trajectory_divergence")
    assert defn is not None
    defn.data_model(**result.beat.composition_data)


# ===========================================================================
# 5. Strict Factual Non-Fabrication
# ===========================================================================

def test_factual_non_fabrication_guarantee() -> None:
    """Numbers in composition_data must come strictly from intent measurements or key_values."""
    engine = CompositionPlannerEngine()
    explicit_num_1 = "₹7,89,123"
    explicit_num_2 = "14.7%"
    intent = VisualIntent(
        intent_id="fact_lock_01",
        narration_excerpt=f"Starting with {explicit_num_1} at an annual return of {explicit_num_2}.",
        what_viewer_must_understand=f"Starting capital is {explicit_num_1}.",
        key_values=[explicit_num_1, explicit_num_2],
        relationship_type="metric",
        measurements=[
            QuantitativeMeasurement(raw_value=explicit_num_1, role="baseline", entity_name="Portfolio"),
            QuantitativeMeasurement(raw_value=explicit_num_2, role="rate", metric_name="Return"),
        ],
    )
    result = engine.run(intent=intent, beat_id="beat_fact_01")
    assert result.beat.composition_id == "metric_hero"
    # Value must strictly be the exact string, not hallucinated
    assert result.beat.composition_data["value"] == explicit_num_1


# ===========================================================================
# 6. Open-Closed Extensibility (Future Compositions)
# ===========================================================================

class MockFutureCompositionData(BaseModel):
    custom_field: str
    numeric_stat: int = Field(default=42)


def mock_custom_builder(intent: VisualIntent) -> dict[str, Any]:
    return {"custom_field": intent.what_viewer_must_understand, "numeric_stat": 100}


def mock_custom_eligibility(intent: VisualIntent) -> bool:
    return intent.relationship_type == "amortization"


def test_open_closed_extensibility_requires_zero_engine_changes() -> None:
    """Registering a new composition dynamically works with CompositionPlannerEngine without edits."""
    mock_definition = CompositionDefinition(
        composition_id="mock_future_comp",
        display_name="Mock Future Comp",
        description="A test composition for future extensibility.",
        supported_relationship_types=["amortization"],
        data_model=MockFutureCompositionData,
        allowed_variants=[],
        asset_requirement=AssetRequirement.NONE,
        remotion_component_id="MockFutureComp",
        fallback_component_id="BrollCaption",
        builder=mock_custom_builder,
        is_eligible=mock_custom_eligibility,
    )
    CompositionRegistry.register(mock_definition)
    try:
        engine = CompositionPlannerEngine()
        intent = VisualIntent(
            intent_id="int_future",
            narration_excerpt="Testing a new amortization composition.",
            what_viewer_must_understand="Loan principal amortization structure.",
            key_values=[],
            relationship_type="amortization",
        )
        from engines import composition_selector
        composition_selector.PRIMARY_RELATIONSHIP_MAP["amortization"] = "mock_future_comp"
        try:
            result = engine.run(intent=intent, beat_id="beat_future")
            assert result.used_fallback is False
            assert result.beat.composition_id == "mock_future_comp"
            assert result.beat.composition_data["custom_field"] == "Loan principal amortization structure."
            assert result.beat.composition_data["numeric_stat"] == 100
        finally:
            composition_selector.PRIMARY_RELATIONSHIP_MAP.pop("amortization", None)
    finally:
        CompositionRegistry._registry.pop("mock_future_comp", None)


# ===========================================================================
# 7. Adversarial Fail-Fast Tests (A–K)
#    Each test verifies the system RAISES rather than fabricates.
# ===========================================================================

# --- A. calculation: 2+ measurements without input/result roles → FAIL ---

def test_A_calculation_no_input_result_roles_fails() -> None:
    """calculation with 2 measurements of ambiguous role must FAIL — no positional guessing."""
    engine = CompositionPlannerEngine()
    with pytest.raises((CompositionPlannerEngineError, ValidationError)):
        intent = VisualIntent(
            intent_id="adv_A",
            narration_excerpt="₹10 lakh at 12% becomes ₹31 lakh.",
            what_viewer_must_understand="Compound growth.",
            relationship_type="calculation",
            measurements=[
                QuantitativeMeasurement(raw_value="₹10 lakh", metric_name="Principal", role="context"),
                QuantitativeMeasurement(raw_value="₹31 lakh", metric_name="Final", role="context"),
            ],
        )
        engine.run(intent=intent, beat_id="adv_A")


# --- B. growth: 2 measurements without start/end roles → FAIL; end_value cannot be copied from start ---

def test_B_growth_no_start_end_roles_fails() -> None:
    """growth with measurements missing input/result roles must FAIL — positional selection is prohibited."""
    engine = CompositionPlannerEngine()
    with pytest.raises((CompositionPlannerEngineError, ValidationError)):
        intent = VisualIntent(
            intent_id="adv_B1",
            narration_excerpt="₹10 lakh grows over time.",
            what_viewer_must_understand="Growth.",
            relationship_type="growth",
            measurements=[
                QuantitativeMeasurement(raw_value="₹10 lakh", metric_name="Principal", role="context"),
                QuantitativeMeasurement(raw_value="₹31 lakh", metric_name="Corpus", role="context"),
            ],
        )
        engine.run(intent=intent, beat_id="adv_B1")


def test_B_growth_identical_start_end_value_fails() -> None:
    """growth where start_value == end_value must FAIL — copying start to end is prohibited."""
    engine = CompositionPlannerEngine()
    intent = VisualIntent(
        intent_id="adv_B2",
        narration_excerpt="₹10 lakh accumulates.",
        what_viewer_must_understand="First ₹10 lakh.",
        relationship_type="growth",
        measurements=[
            QuantitativeMeasurement(raw_value="₹10 lakh", metric_name="Start", role="input"),
            QuantitativeMeasurement(raw_value="₹10 lakh", metric_name="End", role="result"),
        ],
    )
    with pytest.raises(CompositionPlannerEngineError):
        engine.run(intent=intent, beat_id="adv_B2")


# --- C. metric: multiple measurements with no authoritative primary role → FAIL ---

def test_C_metric_multiple_ambiguous_input_measurements_fails() -> None:
    """metric with 2 input measurements must FAIL — key_values cannot substitute for a single primary."""
    engine = CompositionPlannerEngine()
    intent = VisualIntent(
        intent_id="adv_C",
        narration_excerpt="₹10 lakh and ₹25 lakh are key milestones.",
        what_viewer_must_understand="Dual milestones.",
        relationship_type="metric",
        key_values=["₹10 lakh", "₹25 lakh"],
        measurements=[
            QuantitativeMeasurement(raw_value="₹10 lakh", metric_name="First Milestone", role="input"),
            QuantitativeMeasurement(raw_value="₹25 lakh", metric_name="Second Milestone", role="input"),
        ],
    )
    with pytest.raises(CompositionPlannerEngineError):
        engine.run(intent=intent, beat_id="adv_C")


# --- D. time_decay: missing temporal.horizon → FAIL; focal_point alone is NOT sufficient ---

def test_D_time_decay_missing_horizon_fails() -> None:
    """time_decay without temporal.horizon must FAIL — no narration keyword detection allowed."""
    engine = CompositionPlannerEngine()
    intent = VisualIntent(
        intent_id="adv_D1",
        narration_excerpt="Over many years, value erodes away.",
        what_viewer_must_understand="Value erodes over time.",
        relationship_type="decline",
        measurements=[
            QuantitativeMeasurement(raw_value="₹50,000", entity_name="Pension", role="baseline"),
            QuantitativeMeasurement(raw_value="50%", role="delta", direction="down"),
        ],
    )
    with pytest.raises(CompositionPlannerEngineError):
        engine.run(intent=intent, beat_id="adv_D1")


def test_D_time_decay_focal_point_alone_not_sufficient() -> None:
    """time_decay with only a focal_point (no temporal.horizon, no baseline measurement) must FAIL."""
    engine = CompositionPlannerEngine()
    with pytest.raises((CompositionPlannerEngineError, ValidationError)):
        intent = VisualIntent(
            intent_id="adv_D2",
            narration_excerpt="Pension loses value.",
            what_viewer_must_understand="Value decay.",
            relationship_type="decline",
            visual_dynamics=VisualDynamics(focal_point="₹50,000 monthly pension"),
        )
        engine.run(intent=intent, beat_id="adv_D2")


# --- E. multi_factor: entities alone cannot construct factors; <2 causal causes → FAIL ---

def test_E_multi_factor_entities_only_fails() -> None:
    """multi_factor with only entities (no causal.causes) must FAIL."""
    engine = CompositionPlannerEngine()
    with pytest.raises((CompositionPlannerEngineError, ValidationError)):
        intent = VisualIntent(
            intent_id="adv_E1",
            narration_excerpt="Inflation, taxes, and fees erode returns.",
            what_viewer_must_understand="Multiple pressures.",
            relationship_type="multi_factor",
            entities=[
                SemanticEntity(name="Inflation"),
                SemanticEntity(name="Taxes"),
                SemanticEntity(name="Fees"),
            ],
        )
        engine.run(intent=intent, beat_id="adv_E1")


def test_E_multi_factor_single_cause_fails() -> None:
    """multi_factor with only 1 causal cause must FAIL — minimum 2 causes required."""
    engine = CompositionPlannerEngine()
    with pytest.raises((CompositionPlannerEngineError, ValidationError)):
        intent = VisualIntent(
            intent_id="adv_E2",
            narration_excerpt="Inflation erodes returns.",
            what_viewer_must_understand="Single pressure.",
            relationship_type="multi_factor",
            causal=CausalStructure(causes=["Inflation Drag"], outcome="Reduced Return", outcome_severity="high"),
        )
        engine.run(intent=intent, beat_id="adv_E2")


# --- F. comparison: missing ComparisonStructure → FAIL; entities/measurements cannot replace it ---

def test_F_comparison_missing_structure_fails() -> None:
    """comparison without ComparisonStructure must FAIL — entities/measurements cannot silently replace it."""
    engine = CompositionPlannerEngine()
    with pytest.raises((CompositionPlannerEngineError, ValidationError)):
        intent = VisualIntent(
            intent_id="adv_F",
            narration_excerpt="FD gives 6%, Equity gives 12%.",
            what_viewer_must_understand="FD vs Equity.",
            relationship_type="comparison",
            entities=[
                SemanticEntity(name="FD"),
                SemanticEntity(name="Equity"),
            ],
            measurements=[
                QuantitativeMeasurement(raw_value="6%", metric_name="FD Return", role="input"),
                QuantitativeMeasurement(raw_value="12%", metric_name="Equity Return", role="result"),
            ],
        )
        engine.run(intent=intent, beat_id="adv_F")


# --- G. ranking: no entities with names → FAIL; key_values cannot substitute ---

def test_G_ranking_no_entity_names_fails() -> None:
    """ranking with only key_values (no entities) must FAIL — key_values cannot substitute for entity names."""
    engine = CompositionPlannerEngine()
    with pytest.raises((CompositionPlannerEngineError, ValidationError)):
        intent = VisualIntent(
            intent_id="adv_G",
            narration_excerpt="Top assets are Equities, Gold, FD.",
            what_viewer_must_understand="Ranked asset list.",
            relationship_type="ranking",
            key_values=["Equities", "Gold", "FD"],
        )
        engine.run(intent=intent, beat_id="adv_G")


# --- H. process: fewer than 2 entities → FAIL ---

def test_H_process_single_entity_fails() -> None:
    """process with only 1 entity must FAIL — a process requires at least 2 distinct steps."""
    engine = CompositionPlannerEngine()
    with pytest.raises((CompositionPlannerEngineError, ValidationError)):
        intent = VisualIntent(
            intent_id="adv_H",
            narration_excerpt="Step 1: Invest.",
            what_viewer_must_understand="Single step only.",
            relationship_type="process",
            entities=[SemanticEntity(name="Invest")],
        )
        engine.run(intent=intent, beat_id="adv_H")


# --- I. waterfall: missing role/direction requirements → FAIL ---

def test_I_waterfall_missing_baseline_fails() -> None:
    """waterfall without role='baseline' measurement must FAIL — measurements[0] positional fallback is prohibited."""
    engine = CompositionPlannerEngine()
    intent = VisualIntent(
        intent_id="adv_I1",
        narration_excerpt="₹1,00,000 minus expenses.",
        what_viewer_must_understand="Cash flow.",
        relationship_type="waterfall",
        measurements=[
            QuantitativeMeasurement(raw_value="₹1,00,000", metric_name="Gross Salary", role="input"),
            QuantitativeMeasurement(raw_value="₹30,000", metric_name="Expenses", role="delta", direction="down"),
        ],
    )
    with pytest.raises(CompositionPlannerEngineError):
        engine.run(intent=intent, beat_id="adv_I1")


def test_I_waterfall_missing_direction_on_delta_fails() -> None:
    """waterfall with delta measurement missing explicit direction must FAIL — assuming subtract is prohibited."""
    engine = CompositionPlannerEngine()
    intent = VisualIntent(
        intent_id="adv_I2",
        narration_excerpt="₹1,00,000 minus expenses.",
        what_viewer_must_understand="Cash flow.",
        relationship_type="waterfall",
        measurements=[
            QuantitativeMeasurement(raw_value="₹1,00,000", metric_name="Gross Salary", role="baseline", numeric_value=100000),
            QuantitativeMeasurement(raw_value="₹30,000", metric_name="Expenses", role="delta", numeric_value=30000),
        ],
    )
    with pytest.raises(CompositionPlannerEngineError):
        engine.run(intent=intent, beat_id="adv_I2")


def test_I_waterfall_missing_delta_fails() -> None:
    """waterfall with only a baseline and no delta measurements must FAIL."""
    engine = CompositionPlannerEngine()
    intent = VisualIntent(
        intent_id="adv_I3",
        narration_excerpt="₹1,00,000 salary.",
        what_viewer_must_understand="Baseline only.",
        relationship_type="waterfall",
        measurements=[
            QuantitativeMeasurement(raw_value="₹1,00,000", metric_name="Gross Salary", role="baseline", numeric_value=100000),
        ],
    )
    with pytest.raises(CompositionPlannerEngineError):
        engine.run(intent=intent, beat_id="adv_I3")


# --- J. trajectory_divergence: comparison relationship_type must NOT route to trajectory_divergence ---

def test_J_comparison_does_not_route_to_divergence() -> None:
    """comparison relationship_type must route to comparison_split, NEVER trajectory_divergence."""
    engine = CompositionPlannerEngine()
    intent = VisualIntent(
        intent_id="adv_J",
        narration_excerpt="Over 25 years, investing vs spending.",
        what_viewer_must_understand="Two paths diverge.",
        relationship_type="comparison",
        temporal=TemporalContext(horizon="25 years"),
        comparison=ComparisonStructure(
            subject_a="Equity Investing",
            value_a="₹2 Crore",
            subject_b="Spending",
            value_b="₹0",
            comparison_dimension="Net Wealth",
        ),
    )
    result = engine.run(intent=intent, beat_id="adv_J")
    assert result.beat.composition_id == "comparison_split", (
        f"comparison relationship_type must always route to comparison_split, got {result.beat.composition_id}"
    )


# --- K. Fabrication prohibition tests ---

def test_K_growth_must_not_fabricate_missing_start_value() -> None:
    """growth_trajectory must FAIL rather than insert ₹0 or copy end_value as start_value."""
    engine = CompositionPlannerEngine()
    intent = VisualIntent(
        intent_id="adv_K1",
        narration_excerpt="Corpus grows to ₹10 lakh.",
        what_viewer_must_understand="Growth to ₹10 lakh.",
        relationship_type="growth",
        measurements=[
            QuantitativeMeasurement(raw_value="₹10 lakh", metric_name="Target Corpus", role="result", direction="up"),
        ],
    )
    with pytest.raises(CompositionPlannerEngineError):
        engine.run(intent=intent, beat_id="adv_K1")


def test_K_divergence_must_not_fabricate_path_labels_from_entities() -> None:
    """trajectory_divergence must FAIL rather than use entities[0/1].name as path labels."""
    engine = CompositionPlannerEngine()
    with pytest.raises((CompositionPlannerEngineError, ValidationError)):
        intent = VisualIntent(
            intent_id="adv_K2",
            narration_excerpt="Over 20 years, two paths diverge.",
            what_viewer_must_understand="Divergence.",
            relationship_type="divergence",
            temporal=TemporalContext(horizon="20 years"),
            entities=[
                SemanticEntity(name="Investing"),
                SemanticEntity(name="Spending"),
            ],
            measurements=[
                QuantitativeMeasurement(raw_value="₹1.5 Crore", role="result", metric_name="Corpus"),
                QuantitativeMeasurement(raw_value="₹0", role="result", metric_name="Net Worth"),
            ],
        )
        engine.run(intent=intent, beat_id="adv_K2")


def test_K_divergence_must_not_fabricate_values_from_comparison_with_blank_fields() -> None:
    """trajectory_divergence must FAIL when comparison value_a/value_b are empty strings."""
    engine = CompositionPlannerEngine()
    intent = VisualIntent(
        intent_id="adv_K3",
        narration_excerpt="Over 20 years, two paths diverge.",
        what_viewer_must_understand="Divergence.",
        relationship_type="divergence",
        temporal=TemporalContext(horizon="20 years"),
        comparison=ComparisonStructure(
            subject_a="Path A",
            value_a="",    # blank — must not fabricate
            subject_b="Path B",
            value_b="",    # blank — must not fabricate
            comparison_dimension="Net Wealth",
        ),
    )
    with pytest.raises(CompositionPlannerEngineError):
        engine.run(intent=intent, beat_id="adv_K3")


def test_K_broll_caption_must_not_absorb_metric_intent() -> None:
    """broll_caption must not silently absorb intents with relationship_type='metric' (no measurements)."""
    engine = CompositionPlannerEngine()
    with pytest.raises((CompositionPlannerEngineError, ValidationError)):
        intent = VisualIntent(
            intent_id="adv_K4",
            narration_excerpt="Inflation is 6% and erodes purchasing power.",
            what_viewer_must_understand="Inflation erodes value.",
            relationship_type="metric",
        )
        engine.run(intent=intent, beat_id="adv_K4")


def test_K_waterfall_must_not_use_key_values_as_baseline() -> None:
    """cash_flow_waterfall must FAIL rather than use key_values[0] as starting_value."""
    engine = CompositionPlannerEngine()
    intent = VisualIntent(
        intent_id="adv_K5",
        narration_excerpt="₹1,00,000 salary with expenses.",
        what_viewer_must_understand="Waterfall.",
        relationship_type="waterfall",
        key_values=["₹1,00,000", "₹30,000"],
    )
    with pytest.raises(CompositionPlannerEngineError):
        engine.run(intent=intent, beat_id="adv_K5")
