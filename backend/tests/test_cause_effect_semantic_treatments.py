from typing import Any
import pytest
from registries.composition_registry import CompositionRegistry, CauseEffectData, CauseItem
from engines.video_assembly.composition_resolver import CompositionResolver


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
