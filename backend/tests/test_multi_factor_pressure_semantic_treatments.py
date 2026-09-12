from typing import Any
import pytest
from registries.composition_registry import CompositionRegistry, MultiFactorPressureData, FactorItem
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


def test_multi_factor_pressure_data_accepts_all_new_fields() -> None:
    data = MultiFactorPressureData(
        factors=[
            FactorItem(label="High Inflation", value="7.2%", severity="critical", icon="inflation"),
            FactorItem(label="Fee Drag", value="2.5%", severity="high", icon="fee"),
            FactorItem(label="Sequence Risk", value="Drawdown", severity="medium", icon="chart"),
        ],
        combined_label="Premature Corpus Depletion",
        combined_severity="critical",
        outcome_note="Triple convergence accelerates portfolio failure",
        outcome_value="-42% Real Capital",
        outcome_header_label="SYSTEMIC RISK EXPOSURE",
        variant="tri_factor",
        polarity="critical",
    )
    assert len(data.factors) == 3
    assert data.factors[0].icon == "inflation"
    assert data.combined_label == "Premature Corpus Depletion"
    assert data.combined_severity == "critical"
    assert data.outcome_note == "Triple convergence accelerates portfolio failure"
    assert data.outcome_value == "-42% Real Capital"
    assert data.outcome_header_label == "SYSTEMIC RISK EXPOSURE"
    assert data.variant == "tri_factor"
    assert data.polarity == "critical"


def test_multi_factor_pressure_backward_compatibility() -> None:
    data = MultiFactorPressureData(
        factors=[FactorItem(label="High Inflation")],
        combined_label="Loss of Purchasing Power",
        combined_severity="high",
    )
    assert len(data.factors) == 1
    assert data.factors[0].value is None
    assert data.factors[0].severity is None
    assert data.factors[0].icon is None
    assert data.combined_label == "Loss of Purchasing Power"
    assert data.combined_severity == "high"
    assert data.outcome_note is None
    assert data.outcome_value is None
    assert data.outcome_header_label is None
    assert data.variant is None
    assert data.polarity is None


def test_multi_factor_pressure_allowed_variants_in_registry() -> None:
    defn = CompositionRegistry.get("multi_factor_pressure")
    assert defn is not None
    assert "dual_factor" in defn.allowed_variants
    assert "tri_factor" in defn.allowed_variants
    assert "quad_factor" in defn.allowed_variants
    assert "standard" in defn.allowed_variants


def test_candidate_fact_extraction_dual_tri_quad_factor() -> None:
    # 2 Factors
    intent2 = VisualIntent(
        intent_id="intent_01",
        narration_excerpt="High inflation and low fixed yields threaten savings.",
        what_viewer_must_understand="Dual pressure on capital.",
        relationship_type="multi_factor",
        causal=CausalStructure(
            causes=["High Inflation", "Low Fixed Yield"],
            outcome="Purchasing Power Collapse",
            outcome_severity="critical",
            mechanism="Real returns drop into negative territory",
        ),
        measurements=[
            QuantitativeMeasurement(entity_name="High Inflation", raw_value="7.2%", numeric_value=7.2, unit="%", role="input"),
            QuantitativeMeasurement(entity_name="Purchasing Power", raw_value="-38% Real Loss", numeric_value=-38.0, unit="%", role="result"),
        ],
    )
    cand2 = build_candidate_composition_data("multi_factor_pressure", intent2)
    assert cand2["variant"] == "dual_factor"
    assert cand2["combined_severity"] == "critical"
    assert cand2["polarity"] == "critical"
    assert cand2["outcome_header_label"] == "CRITICAL THREAT"
    assert cand2["outcome_note"] == "Real returns drop into negative territory"
    assert cand2["outcome_value"] == "-38% Real Loss"
    assert len(cand2["factors"]) == 2
    assert cand2["factors"][0]["value"] == "7.2%"

    # 3 Factors
    intent3 = VisualIntent(
        intent_id="intent_02",
        narration_excerpt="Three risk factors hit simultaneously.",
        what_viewer_must_understand="Triple risk factor.",
        relationship_type="multi_factor",
        causal=CausalStructure(
            causes=["Factor A", "Factor B", "Factor C"],
            outcome="Systemic Stress",
            outcome_severity="high",
        ),
    )
    cand3 = build_candidate_composition_data("multi_factor_pressure", intent3)
    assert cand3["variant"] == "tri_factor"
    assert cand3["combined_severity"] == "high"
    assert cand3["polarity"] == "high"
    assert len(cand3["factors"]) == 3

    # 4 Factors
    intent4 = VisualIntent(
        intent_id="intent_03",
        narration_excerpt="Four forces squeeze retirement margins.",
        what_viewer_must_understand="Quadruple convergence.",
        relationship_type="multi_factor",
        causal=CausalStructure(
            causes=["Market Drawdown", "Rising Debt Service", "Expense Drag", "Emergency Outflow"],
            outcome="Severe Capital Drain",
            outcome_severity="critical",
        ),
    )
    cand4 = build_candidate_composition_data("multi_factor_pressure", intent4)
    assert cand4["variant"] == "quad_factor"
    assert cand4["combined_severity"] == "critical"
    assert len(cand4["factors"]) == 4


def test_merge_factual_and_presentation_preserves_new_fields() -> None:
    intent = VisualIntent(
        intent_id="intent_04",
        narration_excerpt="Factual factors converge into severe deficit.",
        what_viewer_must_understand="Causal convergence.",
        relationship_type="multi_factor",
    )
    candidate_facts = {
        "factors": [
            {"label": "Inflation Force", "value": "7%"},
            {"label": "Tax Drag", "value": "30%"},
        ],
        "combined_label": "Severe Deficit",
        "combined_severity": "critical",
        "outcome_value": "$180K Gap",
        "outcome_header_label": "SYSTEMIC SQUEEZE",
        "outcome_note": "Compounding drag drains portfolio",
        "variant": "dual_factor",
        "polarity": "critical",
    }
    llm_presentation = {
        "composition_id": "multi_factor_pressure",
        "factors": [
            {"label": "Inflation Force (Styled)", "severity": "high", "icon": "trending_down"},
            {"label": "Tax Drag (Styled)", "severity": "critical", "icon": "receipt"},
        ],
        "combined_label": "Severe Deficit (Enhanced)",
    }
    merged = merge_factual_and_presentation_data("multi_factor_pressure", candidate_facts, llm_presentation, intent)
    assert merged["outcome_value"] == "$180K Gap"
    assert merged["outcome_header_label"] == "SYSTEMIC SQUEEZE"
    assert merged["outcome_note"] == "Compounding drag drains portfolio"
    assert merged["variant"] == "dual_factor"
    assert merged["polarity"] == "critical"
    assert len(merged["factors"]) == 2
    assert merged["factors"][0]["value"] == "7%"
    assert merged["factors"][0]["severity"] == "high"
    assert merged["factors"][0]["icon"] == "trending_down"
    assert merged["factors"][1]["value"] == "30%"
    assert merged["factors"][1]["severity"] == "critical"
    assert merged["factors"][1]["icon"] == "receipt"


def test_composition_resolver_multi_factor_pressure_maps_all_props() -> None:
    resolver = CompositionResolver()
    spec = resolver.resolve_composition(
        composition_id="multi_factor_pressure",
        composition_data={
            "factors": [
                {"label": "Inflation", "value": "7%", "severity": "critical", "icon": "flame"},
                {"label": "Fee Drag", "value": "2.5%", "severity": "high", "icon": "percent"},
            ],
            "combined_label": "Corpus Depletion",
            "combined_severity": "critical",
            "outcome_note": "Simultaneous erosion speeds depletion",
            "outcome_value": "-45% Real Assets",
            "outcome_header_label": "CRITICAL RISK",
            "variant": "dual_factor",
            "polarity": "critical",
        },
    )
    assert spec.component_id == "MultiFactorPressure"
    assert spec.props["combinedLabel"] == "Corpus Depletion"
    assert spec.props["combinedSeverity"] == "critical"
    assert spec.props["outcomeNote"] == "Simultaneous erosion speeds depletion"
    assert spec.props["outcomeValue"] == "-45% Real Assets"
    assert spec.props["outcomeHeaderLabel"] == "CRITICAL RISK"
    assert spec.props["variant"] == "dual_factor"
    assert spec.props["polarity"] == "critical"
    assert len(spec.props["factors"]) == 2
    assert spec.props["factors"][0]["icon"] == "flame"
    assert spec.props["factors"][1]["icon"] == "percent"


def test_multi_factor_pressure_schema_required_invariants() -> None:
    schema = CompositionRegistry.get_data_schema("multi_factor_pressure")
    assert schema is not None
    required = schema["required"]
    assert set(required) == {"factors", "combined_label", "combined_severity"}
    for optional_field in ["outcome_value", "outcome_header_label", "outcome_note", "variant", "polarity"]:
        assert optional_field not in required
        assert optional_field in schema["properties"]
