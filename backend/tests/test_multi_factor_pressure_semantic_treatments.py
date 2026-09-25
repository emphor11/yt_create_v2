from typing import Any
import pytest
from registries.composition_registry import CompositionRegistry, MultiFactorPressureData, FactorItem
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
