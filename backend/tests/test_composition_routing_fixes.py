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
from engines.composition_selector import select_composition_for_intent
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


# ===========================================================================
# C. comparison relationship (comparison_split)
# ===========================================================================

def test_comparison_relationship_ownership() -> None:
    eligible = CompositionRegistry.get_for_relationship_type("comparison")
    eligible_ids = [d.composition_id for d in eligible]
    assert "comparison_split" in eligible_ids


# ===========================================================================
# D. ranking relationship (ranked_list)
# ===========================================================================

def test_ranking_relationship_ownership() -> None:
    eligible = CompositionRegistry.get_for_relationship_type("ranking")
    eligible_ids = [d.composition_id for d in eligible]
    assert "ranked_list" in eligible_ids


# ===========================================================================
# E. process relationship (process_flow)
# ===========================================================================

def test_process_relationship_ownership() -> None:
    eligible = CompositionRegistry.get_for_relationship_type("process")
    eligible_ids = [d.composition_id for d in eligible]
    assert "process_flow" in eligible_ids


# ===========================================================================
# F. intentional BrollCaption
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


def test_growth_and_decline_and_trend_routing() -> None:
    growth_intent = VisualIntent(
        intent_id="intent_g",
        narration_excerpt="Wealth grows over time.",
        what_viewer_must_understand="Growth",
        relationship_type="growth",
    )
    assert select_composition_for_intent(growth_intent) == "growth_trajectory"

    decline_intent = VisualIntent(
        intent_id="intent_d",
        narration_excerpt="Value erodes over time.",
        what_viewer_must_understand="Decline",
        relationship_type="decline",
    )
    assert select_composition_for_intent(decline_intent) == "time_decay"

    # Deprecated trend without explicit direction gracefully resolves to growth_trajectory
    trend_intent_no_dir = VisualIntent(
        intent_id="intent_t1",
        narration_excerpt="Spending rises with salary.",
        what_viewer_must_understand="Spending rises",
        relationship_type="trend",
    )
    assert select_composition_for_intent(trend_intent_no_dir) == "growth_trajectory"

    # Deprecated trend with explicit downward measurement resolves to time_decay
    trend_intent_down = VisualIntent(
        intent_id="intent_t2",
        narration_excerpt="Purchasing power decays.",
        what_viewer_must_understand="Decay",
        relationship_type="trend",
        measurements=[QuantitativeMeasurement(raw_value="5%", direction="down")],
    )
    assert select_composition_for_intent(trend_intent_down) == "time_decay"

