from typing import Any
import pytest
from registries.composition_registry import CompositionRegistry, CauseEffectData, CauseItem
from engines.composition_planner_engine import (
    build_candidate_composition_data,
    merge_factual_and_presentation_data,
)
from engines.video_assembly.composition_resolver import CompositionResolver
from domain.visual_intent import (
    VisualIntent,
    CausalStructure,
    QuantitativeMeasurement,
)


def test_cause_effect_data_accepts_all_new_fields() -> None:
    data = CauseEffectData(
        causes=[
            CauseItem(label="High Expense Ratio", value="2.25%", icon="fee"),
            CauseItem(label="Market Volatility", value="High Beta", icon="chart"),
        ],
        connector="combine to create",
        outcome_label="Premature Portfolio Depletion",
        outcome_value="Year 14",
        outcome_severity="critical",
        outcome_header_label="Systemic Risk Exposure",
        outcome_note="Compounding fee drag amplifies sequence-of-returns erosion",
        variant="dual_cause",
        polarity="critical",
    )
    assert len(data.causes) == 2
    assert data.connector == "combine to create"
    assert data.outcome_label == "Premature Portfolio Depletion"
    assert data.outcome_value == "Year 14"
    assert data.outcome_severity == "critical"
    assert data.outcome_header_label == "Systemic Risk Exposure"
    assert data.outcome_note == "Compounding fee drag amplifies sequence-of-returns erosion"
    assert data.variant == "dual_cause"
    assert data.polarity == "critical"


def test_cause_effect_backward_compatibility() -> None:
    data = CauseEffectData(
        causes=[CauseItem(label="Inflation")],
        connector="leads to",
        outcome_label="Loss of Purchasing Power",
    )
    assert len(data.causes) == 1
    assert data.connector == "leads to"
    assert data.outcome_label == "Loss of Purchasing Power"
    assert data.outcome_value is None
    assert data.outcome_severity is None
    assert data.outcome_header_label is None
    assert data.outcome_note is None
    assert data.variant is None
    assert data.polarity is None


def test_cause_effect_allowed_variants_in_registry() -> None:
    defn = CompositionRegistry.get("cause_effect")
    assert defn is not None
    assert "single_cause" in defn.allowed_variants
    assert "dual_cause" in defn.allowed_variants
    assert "multi_cause" in defn.allowed_variants
    assert "standard" in defn.allowed_variants


def test_candidate_fact_extraction_single_dual_multi_cause() -> None:
    # 1 Cause
    intent1 = VisualIntent(
        intent_id="intent_01",
        narration_excerpt="Disciplined monthly SIP leads to massive corpus.",
        what_viewer_must_understand="Power of compounding.",
        relationship_type="cause_effect",
        causal=CausalStructure(
            causes=["Monthly ₹20,000 SIP"],
            mechanism="Exponential compound interest over 25 years",
            outcome="₹1.5 Crore Corpus",
            outcome_severity="positive",
        ),
        measurements=[
            QuantitativeMeasurement(entity_name="Monthly SIP", raw_value="₹20,000/mo", numeric_value=20000.0, unit="₹/mo", role="input"),
            QuantitativeMeasurement(entity_name="Corpus", raw_value="₹1.5 Cr", numeric_value=1.5, unit=" Cr", role="result"),
        ],
    )
    cand1 = build_candidate_composition_data("cause_effect", intent1)
    assert cand1["variant"] == "single_cause"
    assert cand1["polarity"] == "positive"
    assert cand1["outcome_severity"] == "positive"
    assert cand1["outcome_note"] == "Exponential compound interest over 25 years"
    assert cand1["outcome_value"] == "₹1.5 Cr"
    assert len(cand1["causes"]) == 1

    # 2 Causes
    intent2 = VisualIntent(
        intent_id="intent_02",
        narration_excerpt="High fees combined with inflation erode returns.",
        what_viewer_must_understand="Dual drag on wealth.",
        relationship_type="cause_effect",
        causal=CausalStructure(
            causes=["2.5% Active Fund Fee", "7% Core Inflation"],
            outcome="Real Wealth Destruction",
            outcome_severity="high",
        ),
    )
    cand2 = build_candidate_composition_data("cause_effect", intent2)
    assert cand2["variant"] == "dual_cause"
    assert cand2["polarity"] == "negative"
    assert len(cand2["causes"]) == 2

    # 3 Causes
    intent3 = VisualIntent(
        intent_id="intent_03",
        narration_excerpt="Market drop, inflation surge, and emergency liquidity crunch cause failure.",
        what_viewer_must_understand="Triple risk factor.",
        relationship_type="cause_effect",
        causal=CausalStructure(
            causes=["Market Drawdown", "Inflation Surge", "Emergency Liquidity Crunch"],
            outcome="Premature Capital Depletion",
            outcome_severity="critical",
        ),
    )
    cand3 = build_candidate_composition_data("cause_effect", intent3)
    assert cand3["variant"] == "multi_cause"
    assert cand3["polarity"] == "negative"
    assert len(cand3["causes"]) == 3


def test_merge_factual_and_presentation_preserves_new_fields() -> None:
    intent = VisualIntent(
        intent_id="intent_04",
        narration_excerpt="Direct Fact Cause triggers Factual Outcome.",
        what_viewer_must_understand="Causal mechanism.",
        relationship_type="cause_effect",
        causal=CausalStructure(
            causes=["Direct Fact Cause"],
            outcome="Factual Outcome",
        ),
    )
    candidate_facts = {
        "causes": [{"label": "Direct Fact Cause", "value": "10%"}],
        "outcome_label": "Factual Outcome",
        "outcome_value": "₹50 Lakh",
        "outcome_severity": "negative",
        "outcome_header_label": "Severe Downside",
        "outcome_note": "Factual mechanism from intent",
        "variant": "single_cause",
        "polarity": "negative",
    }
    llm_presentation = {
        "causes": [{"label": "LLM Refined Label", "icon": "trending-down"}],
        "connector": "triggers catastrophic",
    }
    merged = merge_factual_and_presentation_data("cause_effect", candidate_facts, llm_presentation, intent)

    assert merged["outcome_label"] == "Factual Outcome"
    assert merged["outcome_value"] == "₹50 Lakh"
    assert merged["outcome_severity"] == "negative"
    assert merged["outcome_header_label"] == "Severe Downside"
    assert merged["outcome_note"] == "Factual mechanism from intent"
    assert merged["variant"] == "single_cause"
    assert merged["polarity"] == "negative"
    assert merged["connector"] == "triggers catastrophic"
    # Preserved fact value and incorporated presentation icon
    assert merged["causes"][0]["value"] == "10%"
    assert merged["causes"][0]["icon"] == "trending-down"


def test_resolver_maps_all_cause_effect_props() -> None:
    resolver = CompositionResolver()
    spec = resolver.resolve_composition(
        composition_id="cause_effect",
        composition_data={
            "causes": [
                {"label": "Underinsurance", "value": "₹5 Lakh Cover"},
                {"label": "Medical Inflation", "value": "14% p.a."},
            ],
            "connector": "combines to create",
            "outcome_label": "Total Savings Wipeout",
            "outcome_value": "100% Depleted",
            "outcome_severity": "critical",
            "outcome_header_label": "Catastrophic Risk",
            "outcome_note": "Single hospitalization wipes out 10 years of disciplined savings",
            "variant": "dual_cause",
            "polarity": "critical",
        },
    )
    assert spec.component_id == "CauseEffect"
    assert len(spec.props["causes"]) == 2
    assert spec.props["causes"][0]["label"] == "Underinsurance"
    assert spec.props["causes"][0]["value"] == "₹5 Lakh Cover"
    assert spec.props["connector"] == "combines to create"
    assert spec.props["outcomeLabel"] == "Total Savings Wipeout"
    assert spec.props["outcomeValue"] == "100% Depleted"
    assert spec.props["outcomeSeverity"] == "critical"
    assert spec.props["outcomeHeaderLabel"] == "Catastrophic Risk"
    assert spec.props["outcomeNote"] == "Single hospitalization wipes out 10 years of disciplined savings"
    assert spec.props["variant"] == "dual_cause"
    assert spec.props["polarity"] == "critical"


def test_schema_stability_remains_required_causes_connector_outcome() -> None:
    schema = CompositionRegistry.get_data_schema("cause_effect")
    assert schema is not None
    required = schema["required"]
    assert "causes" in required
    assert "connector" in required
    assert "outcome_label" in required
    # Verify new fields are optional
    assert "outcome_header_label" not in required
    assert "outcome_note" not in required
    assert "variant" not in required
    assert "polarity" not in required
    assert "outcome_value" not in required
    assert "outcome_severity" not in required
