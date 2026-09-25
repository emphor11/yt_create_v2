"""Targeted tests for composition routing fixes and new composition coverage.

Covers:
- Task 1: cause_effect vs multi_factor semantic ownership
- Task 2: comparison_split composition registration, planner, and resolver
- Task 3: ranked_list composition registration, planner, and resolver
- Task 4: process_flow composition registration, planner, and resolver
- Task 5: trend vs time_decay semantic guardrails (decline vs upward vs neutral)
- Task 6: fallback classification (intentional vs no_suitable vs error)
- Task 7: legacy mode preservation
"""
import pytest

from domain.visual_intent import (
    VisualIntent,
    CausalStructure,
    ComparisonStructure,
    SemanticEntity,
    TemporalContext,
    QuantitativeMeasurement,
)
from domain.video_assembly_props import ComponentSpec
from engines.composition_planner_engine import CompositionPlannerEngine, CompositionPlannerResult
from engines.video_assembly.composition_resolver import CompositionResolver
from engines.video_assembly.component_resolver import ComponentResolver
from registries.composition_registry import CompositionRegistry
from registries.component_registry import ComponentRegistry
from providers.llm_provider import LLMJsonRequest, LLMJsonResponse, LLMProviderMetadata, LLMProviderError


class StaticLLMProvider:
    def __init__(self, payload: dict | Exception):
        self.payload = payload
        self.last_request: LLMJsonRequest | None = None

    def generate_json(self, request: LLMJsonRequest) -> LLMJsonResponse:
        self.last_request = request
        if isinstance(self.payload, Exception):
            raise self.payload
        return LLMJsonResponse(
            payload=self.payload,
            metadata=LLMProviderMetadata(provider="static-test", model="static-test"),
        )


# ===========================================================================
# A. cause_effect relationship
# ===========================================================================

def test_cause_effect_relationship_ownership() -> None:
    """cause_effect should be the ONLY candidate for relationship_type='cause_effect'."""
    eligible = CompositionRegistry.get_for_relationship_type("cause_effect")
    eligible_ids = [d.composition_id for d in eligible]
    assert "cause_effect" in eligible_ids
    assert "multi_factor_pressure" not in eligible_ids
    assert len(eligible_ids) == 1


def test_planner_routes_cause_effect_successfully() -> None:
    response = {
        "status": "ok",
        "composition_id": "cause_effect",
        "variant": None,
        "composition_data": {
            "causes": [{"label": "Lifestyle Creep", "value": "15% annual"}],
            "connector": "causes",
            "outcome_label": "Zero Savings Rate",
            "outcome_value": "0%",
            "outcome_severity": "negative",
        },
        "asset_requirement": "none",
        "asset_query": None,
        "trigger_word": "causes",
        "visual_goal": "Show lifestyle creep destroying savings.",
    }
    intent = VisualIntent(
        intent_id="intent_ce",
        narration_excerpt="Lifestyle inflation directly causes your savings to hit zero.",
        what_viewer_must_understand="Lifestyle creep drives savings to zero.",
        key_values=["15%", "0%"],
        relationship_type="cause_effect",
        trigger_word="causes",
        causal=CausalStructure(
            causes=["Lifestyle inflation"],
            outcome="Savings hit zero",
            outcome_severity="critical",
        ),
    )
    engine = CompositionPlannerEngine(StaticLLMProvider(response))
    result = engine._run_legacy_llm(intent=intent, beat_id="beat_ce_01")
    assert result.used_fallback is False
    assert result.fallback_reason is None
    assert result.beat.composition_id == "cause_effect"
    assert result.beat.relationship_type == "cause_effect"


# ===========================================================================
# B. multi_factor relationship
# ===========================================================================

def test_multi_factor_relationship_ownership() -> None:
    """multi_factor_pressure should be the ONLY candidate for relationship_type='multi_factor'."""
    eligible = CompositionRegistry.get_for_relationship_type("multi_factor")
    eligible_ids = [d.composition_id for d in eligible]
    assert "multi_factor_pressure" in eligible_ids
    assert "cause_effect" not in eligible_ids
    assert len(eligible_ids) == 1


def test_planner_routes_multi_factor_successfully() -> None:
    response = {
        "status": "ok",
        "composition_id": "multi_factor_pressure",
        "variant": None,
        "composition_data": {
            "factors": [
                {"label": "Inflation", "value": "7%", "severity": "high"},
                {"label": "Taxes", "value": "30%", "severity": "high"},
                {"label": "Weak Returns", "value": "4%", "severity": "medium"},
            ],
            "combined_label": "Compounded Capital Erosion",
            "combined_severity": "critical",
            "outcome_note": "Tri-factor destruction of purchasing power",
        },
        "asset_requirement": "none",
        "asset_query": None,
        "trigger_word": "converge",
        "visual_goal": "Show 3 independent factors crushing returns.",
    }
    intent = VisualIntent(
        intent_id="intent_mf",
        narration_excerpt="High taxes, inflation, and weak returns converge to create capital erosion.",
        what_viewer_must_understand="Three independent pressures combine to destroy wealth.",
        key_values=["7%", "30%", "4%"],
        relationship_type="multi_factor",
        trigger_word="converge",
        causal=CausalStructure(
            causes=["High taxes", "Inflation", "Weak returns"],
            outcome="Capital erosion",
            outcome_severity="critical",
        ),
    )
    engine = CompositionPlannerEngine(StaticLLMProvider(response))
    result = engine._run_legacy_llm(intent=intent, beat_id="beat_mf_01")
    assert result.used_fallback is False
    assert result.fallback_reason is None
    assert result.beat.composition_id == "multi_factor_pressure"
    assert result.beat.relationship_type == "multi_factor"


# ===========================================================================
# C. comparison relationship (comparison_split)
# ===========================================================================

def test_comparison_relationship_ownership() -> None:
    eligible = CompositionRegistry.get_for_relationship_type("comparison")
    eligible_ids = [d.composition_id for d in eligible]
    assert "comparison_split" in eligible_ids


def test_planner_routes_comparison_split_successfully() -> None:
    response = {
        "status": "ok",
        "composition_id": "comparison_split",
        "variant": "versus",
        "composition_data": {
            "left_role": "Fixed Deposit",
            "left_value": "6.5%",
            "left_label": "Post-Tax Return",
            "left_unit": "%",
            "right_role": "Nifty Index",
            "right_value": "12.0%",
            "right_label": "Long-Term CAGR",
            "right_unit": "%",
            "comparison_label": "ANNUAL RETURN COMPARISON",
            "delta": "+5.5% Advantage",
            "winner": "right",
            "tone": "positive_negative",
        },
        "asset_requirement": "none",
        "asset_query": None,
        "trigger_word": "versus",
        "visual_goal": "Compare FD return of 6.5% versus Equity return of 12%.",
    }
    intent = VisualIntent(
        intent_id="intent_cmp",
        narration_excerpt="Comparing fixed deposits at six percent versus equity index funds at twelve percent.",
        what_viewer_must_understand="Equity outperforms FD by 5.5% annually.",
        key_values=["6.5%", "12.0%"],
        relationship_type="comparison",
        trigger_word="versus",
        comparison=ComparisonStructure(
            subject_a="Fixed Deposit",
            value_a="6.5%",
            subject_b="Nifty Index",
            value_b="12.0%",
            comparison_dimension="Annual Return",
            delta="+5.5% Advantage",
            winner="Nifty Index",
        ),
    )
    engine = CompositionPlannerEngine(StaticLLMProvider(response))
    result = engine._run_legacy_llm(intent=intent, beat_id="beat_cmp_01")
    assert result.used_fallback is False
    assert result.fallback_reason is None
    assert result.beat.composition_id == "comparison_split"
    assert result.beat.variant == "versus"
    assert result.beat.composition_data["left_role"] == "Fixed Deposit"
    assert result.beat.composition_data["right_role"] == "Nifty Index"


# ===========================================================================
# D. ranking relationship (ranked_list)
# ===========================================================================

def test_ranking_relationship_ownership() -> None:
    eligible = CompositionRegistry.get_for_relationship_type("ranking")
    eligible_ids = [d.composition_id for d in eligible]
    assert "ranked_list" in eligible_ids


def test_planner_routes_ranked_list_successfully() -> None:
    response = {
        "status": "ok",
        "composition_id": "ranked_list",
        "variant": None,
        "composition_data": {
            "header_label": "TOP LIFESTYLE EXPENSES",
            "show_bars": True,
            "items": [
                {"title": "Luxury Rent", "rank": 1, "value": "₹45,000", "numeric_value": 45000, "badge": "Highest"},
                {"title": "Car EMI", "rank": 2, "value": "₹25,000", "numeric_value": 25000},
                {"title": "Dining & Travel", "rank": 3, "value": "₹15,000", "numeric_value": 15000},
            ],
        },
        "asset_requirement": "none",
        "asset_query": None,
        "trigger_word": "ranked",
        "visual_goal": "Rank the top 3 monthly expenses by size.",
    }
    intent = VisualIntent(
        intent_id="intent_rnk",
        narration_excerpt="Ranked by size, luxury rent takes the top spot followed by car EMIs.",
        what_viewer_must_understand="Rent is the single largest expense, followed by EMIs.",
        key_values=["₹45,000", "₹25,000"],
        relationship_type="ranking",
        trigger_word="ranked",
        entities=[
            SemanticEntity(name="Luxury Rent", role="subject"),
            SemanticEntity(name="Car EMI", role="subject"),
            SemanticEntity(name="Dining & Travel", role="subject"),
        ],
    )
    engine = CompositionPlannerEngine(StaticLLMProvider(response))
    result = engine._run_legacy_llm(intent=intent, beat_id="beat_rnk_01")
    assert result.used_fallback is False
    assert result.fallback_reason is None
    assert result.beat.composition_id == "ranked_list"
    assert len(result.beat.composition_data["items"]) == 3


# ===========================================================================
# E. process relationship (process_flow)
# ===========================================================================

def test_process_relationship_ownership() -> None:
    eligible = CompositionRegistry.get_for_relationship_type("process")
    eligible_ids = [d.composition_id for d in eligible]
    assert "process_flow" in eligible_ids


def test_planner_routes_process_flow_successfully() -> None:
    response = {
        "status": "ok",
        "composition_id": "process_flow",
        "variant": "horizontal",
        "composition_data": {
            "header_label": "WEALTH CREATION WORKFLOW",
            "layout": "horizontal",
            "steps": [
                {"title": "Earn Income", "type": "step", "connector_label": "saves 30%"},
                {"title": "Auto-Debit", "type": "step", "connector_label": "invests into"},
                {"title": "Index Fund", "type": "step", "connector_label": "compounds into"},
                {"title": "Financial Freedom", "type": "outcome"},
            ],
        },
        "asset_requirement": "none",
        "asset_query": None,
        "trigger_word": "process",
        "visual_goal": "Illustrate the 4-step wealth creation workflow.",
    }
    intent = VisualIntent(
        intent_id="intent_prc",
        narration_excerpt="The process follows four systematic steps from earning to automated compounding.",
        what_viewer_must_understand="Automation turns monthly income into long-term compounding.",
        key_values=["four steps"],
        relationship_type="process",
        trigger_word="process",
        entities=[
            SemanticEntity(name="Earn Income", role="step"),
            SemanticEntity(name="Auto-Debit", role="step"),
            SemanticEntity(name="Index Fund", role="step"),
            SemanticEntity(name="Financial Freedom", role="outcome"),
        ],
    )
    engine = CompositionPlannerEngine(StaticLLMProvider(response))
    result = engine._run_legacy_llm(intent=intent, beat_id="beat_prc_01")
    assert result.used_fallback is False
    assert result.fallback_reason is None
    assert result.beat.composition_id == "process_flow"
    assert result.beat.variant == "horizontal"
    assert len(result.beat.composition_data["steps"]) == 4


# ===========================================================================
# F, G, H. decline vs trend semantics (TimeDecay guardrails)
# ===========================================================================

def test_decline_relationship_allows_time_decay() -> None:
    response = {
        "status": "ok",
        "composition_id": "time_decay",
        "variant": None,
        "composition_data": {
            "fixed_amount": "₹2 Lakh",
            "amount_label": "Annual Income",
            "time_period": "15 Years",
            "emphasis": "purchasing_power_decline",
            "annotation": "Loses 40% real value",
            "show_chart": True,
        },
        "asset_requirement": "none",
        "asset_query": None,
        "trigger_word": "erosion",
        "visual_goal": "Show purchasing power falling over 15 years.",
    }
    intent = VisualIntent(
        intent_id="intent_dec",
        narration_excerpt="Over fifteen years, purchasing power drops drastically under constant inflation.",
        what_viewer_must_understand="Fixed income loses 40% of its real value over time.",
        key_values=["₹2 Lakh", "15 Years"],
        relationship_type="decline",
        trigger_word="erosion",
        temporal=TemporalContext(horizon="15 Years", is_decay_over_time=True),
    )
    engine = CompositionPlannerEngine(StaticLLMProvider(response))
    result = engine._run_legacy_llm(intent=intent, beat_id="beat_dec_01")
    assert result.used_fallback is False
    assert result.beat.composition_id == "time_decay"


def test_declining_trend_allows_time_decay() -> None:
    response = {
        "status": "ok",
        "composition_id": "time_decay",
        "variant": None,
        "composition_data": {
            "fixed_amount": "₹1 Lakh",
            "amount_label": "Monthly Pension",
            "time_period": "20 Years",
            "emphasis": "value_erosion",
            "annotation": "Depleted by 50%",
            "show_chart": True,
        },
        "asset_requirement": "none",
        "asset_query": None,
        "trigger_word": "decay",
        "visual_goal": "Show real value erosion over 20 years.",
    }
    intent = VisualIntent(
        intent_id="intent_trend_dec",
        narration_excerpt="The trend shows real purchasing power decaying each decade.",
        what_viewer_must_understand="Purchasing power erodes downward over the decade.",
        key_values=["20 Years"],
        relationship_type="trend",
        emphasis="value_erosion",
        trigger_word="decay",
        temporal=TemporalContext(horizon="20 Years", is_decay_over_time=True),
    )
    engine = CompositionPlannerEngine(StaticLLMProvider(response))
    result = engine._run_legacy_llm(intent=intent, beat_id="beat_trend_01")
    assert result.used_fallback is False
    assert result.beat.composition_id == "time_decay"


def test_upward_trend_rejects_time_decay() -> None:
    """An upward trend must NEVER use TimeDecay, even if LLM attempts it."""
    response = {
        "status": "ok",
        "composition_id": "time_decay",
        "variant": None,
        "composition_data": {
            "fixed_amount": "₹10 Lakh",
            "amount_label": "Portfolio",
            "time_period": "15 Years",
            "emphasis": "growth",
        },
        "visual_goal": "Show wealth growing over time.",
    }
    intent = VisualIntent(
        intent_id="intent_trend_up",
        narration_excerpt="Over the next decade, your investments grow exponentially upwards.",
        what_viewer_must_understand="Your portfolio surges higher year after year.",
        key_values=["₹10 Lakh", "15 Years"],
        relationship_type="trend",
        emphasis="show_growth",
        temporal=TemporalContext(horizon="15 Years"),
    )
    engine = CompositionPlannerEngine(StaticLLMProvider(response))
    result = engine._run_legacy_llm(intent=intent, beat_id="beat_trend_up")
    assert result.used_fallback is True
    assert result.beat.composition_id == "broll_caption"
    assert "time_decay rejected: trend does not indicate decline" in result.fallback_reason


def test_neutral_trend_rejects_time_decay() -> None:
    """A neutral trend without decline indicators must NOT use TimeDecay."""
    response = {
        "status": "ok",
        "composition_id": "time_decay",
        "composition_data": {
            "fixed_amount": "Interest Rates",
            "amount_label": "Cycle",
            "time_period": "5 Years",
            "emphasis": "cycle",
        },
        "visual_goal": "Show interest rates moving across economic cycles.",
    }
    intent = VisualIntent(
        intent_id="intent_trend_neutral",
        narration_excerpt="Historically, interest rates fluctuate up and down across economic cycles.",
        what_viewer_must_understand="Rate trends vary across market cycles.",
        key_values=["5 Years"],
        relationship_type="trend",
        temporal=TemporalContext(horizon="5 Years"),
    )
    engine = CompositionPlannerEngine(StaticLLMProvider(response))
    result = engine._run_legacy_llm(intent=intent, beat_id="beat_trend_neu")
    assert result.used_fallback is True
    assert result.beat.composition_id == "broll_caption"
    assert "time_decay rejected" in result.fallback_reason


# ===========================================================================
# I. intentional BrollCaption
# ===========================================================================

def test_intentional_broll_caption_has_fallback_false() -> None:
    response = {
        "status": "ok",
        "composition_id": "broll_caption",
        "variant": None,
        "composition_data": {
            "caption": "Patience is the ultimate edge in investing.",
            "emphasis_phrase": "ultimate edge",
            "author": "Warren Buffett",
        },
        "asset_requirement": "optional_broll",
        "asset_query": "clock ticking desk",
        "trigger_word": "patience",
        "visual_goal": "Highlight patience as an investing virtue.",
    }
    intent = VisualIntent(
        intent_id="intent_stmt",
        narration_excerpt="Patience is the ultimate edge in investing, as legendary investors remind us.",
        what_viewer_must_understand="Patience matters more than speed.",
        key_values=[],
        relationship_type="statement",
        trigger_word="patience",
    )
    engine = CompositionPlannerEngine(StaticLLMProvider(response))
    result = engine.run(intent=intent, beat_id="beat_stmt_01")
    assert result.used_fallback is False
    assert result.fallback_reason is None
    assert result.beat.composition_id == "broll_caption"
    assert result.beat.used_fallback is False
    assert result.beat.fallback_reason is None


# ===========================================================================
# J. unsupported relationship / no_suitable_composition fallback
# ===========================================================================

def test_no_suitable_composition_returns_explicit_fallback_metadata() -> None:
    response = {
        "status": "no_suitable_composition",
        "reason": "This is an abstract philosophical transition with no data.",
    }
    intent = VisualIntent(
        intent_id="intent_abs",
        narration_excerpt="Now let us step back and reconsider everything from first principles.",
        what_viewer_must_understand="A reset of perspective.",
        key_values=[],
        relationship_type="statement",
    )
    engine = CompositionPlannerEngine(StaticLLMProvider(response))
    result = engine._run_legacy_llm(intent=intent, beat_id="beat_abs_01")
    assert result.used_fallback is True
    assert result.beat.composition_id == "broll_caption"
    assert result.fallback_reason.startswith("no_suitable_composition:")
    assert "abstract philosophical" in result.fallback_reason
    assert result.beat.used_fallback is True
    assert result.beat.fallback_reason == result.fallback_reason


# ===========================================================================
# K. validation / provider error fallbacks
# ===========================================================================

def test_missing_required_fields_produces_validation_error_fallback() -> None:
    response = {
        "status": "ok",
        "composition_id": "metric_hero",
        "composition_data": {
            # Missing required fields: value, label
        },
        "visual_goal": "Incomplete metric",
    }
    intent = VisualIntent(
        intent_id="intent_err",
        narration_excerpt="A significant financial milestone.",
        what_viewer_must_understand="Metric test",
        key_values=["₹50 lakh"],
        relationship_type="metric",
    )
    engine = CompositionPlannerEngine(StaticLLMProvider(response))
    result = engine._run_legacy_llm(intent=intent, beat_id="beat_err_01")
    assert result.used_fallback is True
    assert result.fallback_reason.startswith("validation_error:")
    assert result.beat.composition_id == "broll_caption"


def test_provider_error_produces_provider_error_fallback() -> None:
    intent = VisualIntent(
        intent_id="intent_prov_err",
        narration_excerpt="Network error simulation.",
        what_viewer_must_understand="Network error",
        key_values=["10%"],
        relationship_type="metric",
    )
    engine = CompositionPlannerEngine(StaticLLMProvider(LLMProviderError("Connection timeout")))
    result = engine._run_legacy_llm(intent=intent, beat_id="beat_prov_err")
    assert result.used_fallback is True
    assert result.fallback_reason.startswith("provider_error:")
    assert "Connection timeout" in result.fallback_reason


# ===========================================================================
# L. legacy mode preservation
# ===========================================================================

def test_legacy_mode_component_registry_and_resolver_unbroken() -> None:
    """ComponentRegistry must still support legacy components and resolve them."""
    assert ComponentRegistry.is_supported("SplitComparison") is True
    assert ComponentRegistry.is_supported("RankedList") is True
    assert ComponentRegistry.is_supported("ProcessFlow") is True

    resolver = ComponentResolver()
    spec = resolver.resolve_component(
        preferred_component="SplitComparison",
        visual_goal="Compare two items",
        component_data={
            "left_role": "Option A",
            "left_value": 100,
            "right_role": "Option B",
            "right_value": 200,
        },
    )
    assert isinstance(spec, ComponentSpec)
    assert spec.component_id == "SplitComparison"
    assert spec.props["leftRole"] == "Option A"
    assert spec.props["rightRole"] == "Option B"


# ===========================================================================
# M. resolver tests for newly registered compositions
# ===========================================================================

def test_resolve_comparison_split() -> None:
    resolver = CompositionResolver()
    spec = resolver.resolve_composition(
        composition_id="comparison_split",
        composition_data={
            "left_role": "Traditional FD",
            "left_value": "6.5%",
            "left_label": "Post-Tax Return",
            "left_unit": "%",
            "right_role": "Mutual Fund SIP",
            "right_value": "12.0%",
            "right_label": "Long-Term CAGR",
            "right_unit": "%",
            "comparison_label": "WEALTH ACCUMULATION",
            "delta": "+5.5% Advantage",
            "winner": "right",
            "tone": "positive_negative",
        },
        variant="versus",
    )
    assert spec.component_id == "SplitComparison"
    assert spec.props["comparisonLabel"] == "WEALTH ACCUMULATION"
    assert spec.props["variant"] == "versus"
    assert spec.props["tone"] == "positive_negative"
    assert spec.props["leftRole"] == "Traditional FD"
    assert spec.props["leftValue"] == "6.5%"
    assert spec.props["rightRole"] == "Mutual Fund SIP"
    assert spec.props["rightValue"] == "12.0%"
    assert spec.props["winner"] == "right"
    assert spec.props["delta"] == "+5.5% Advantage"


def test_resolve_ranked_list() -> None:
    resolver = CompositionResolver()
    spec = resolver.resolve_composition(
        composition_id="ranked_list",
        composition_data={
            "header_label": "MONTHLY EXPENDITURE",
            "show_bars": True,
            "items": [
                {"title": "Rent", "rank": 1, "value": "₹45,000", "numeric_value": 45000, "badge": "High"},
                {"title": "EMI", "rank": 2, "value": "₹20,000", "numeric_value": 20000},
            ],
        },
    )
    assert spec.component_id == "RankedList"
    assert spec.props["headerLabel"] == "MONTHLY EXPENDITURE"
    assert spec.props["showBars"] is True
    assert len(spec.props["items"]) == 2
    assert spec.props["items"][0]["title"] == "Rent"
    assert spec.props["items"][0]["numericValue"] == 45000
    assert spec.props["items"][1]["title"] == "EMI"


def test_resolve_process_flow() -> None:
    resolver = CompositionResolver()
    spec = resolver.resolve_composition(
        composition_id="process_flow",
        composition_data={
            "header_label": "EXECUTION STEPS",
            "layout": "horizontal",
            "steps": [
                {"title": "Set Budget", "subtitle": "50/30/20 Rule", "connector_label": "leads to"},
                {"title": "Automate SIP", "subtitle": "Day 1 of month", "connector_label": "compounds"},
                {"title": "Review Annually", "subtitle": "Rebalance portfolio"},
            ],
        },
        variant="horizontal",
    )
    assert spec.component_id == "ProcessFlow"
    assert spec.props["headerLabel"] == "EXECUTION STEPS"
    assert spec.props["layout"] == "horizontal"
    assert len(spec.props["steps"]) == 3
    assert spec.props["steps"][0]["title"] == "Set Budget"
    assert spec.props["steps"][0]["connectorLabel"] == "leads to"
    assert spec.props["steps"][1]["title"] == "Automate SIP"
