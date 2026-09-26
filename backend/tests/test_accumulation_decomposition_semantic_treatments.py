"""Tests for Accumulation Decomposition composition."""
import pytest
from typing import Any

from domain.visual_intent import (
    VisualIntent,
    QuantitativeMeasurement,
    TemporalContext,
    VisualDynamics,
)
from engines.video_assembly.composition_resolver import CompositionResolver
from registries.composition_registry import (
    AssetRequirement,
    CompositionRegistry,
    AccumulationDecompositionData,
    AccumulationStream,
)
from registries.composition_builders import (
    build_accumulation_decomposition_data,
    is_eligible_accumulation_decomposition,
)


def test_accumulation_decomposition_schema_accepts_valid_payload() -> None:
    data = AccumulationDecompositionData(
        header_label="WEALTH ACCUMULATION",
        total_value="₹30 Lakh",
        total_label="Total Corpus after 10 Years",
        time_horizon="10 Years",
        streams=[
            AccumulationStream(
                label="Direct SIP Contributions",
                value="₹12 Lakh",
                color_token="emerald",
                numeric_amount=1200000.0,
            ),
            AccumulationStream(
                label="Compound Returns",
                value="₹18 Lakh",
                rate="12% CAGR",
                color_token="cyan",
                numeric_amount=1800000.0,
            ),
        ],
        annotation="Investment returns exceed total salary contributions by year 8.",
        variant="contributions_vs_returns",
    )
    assert data.total_value == "₹30 Lakh"
    assert len(data.streams) == 2
    assert data.streams[0].label == "Direct SIP Contributions"
    assert data.streams[1].rate == "12% CAGR"
    assert data.variant == "contributions_vs_returns"


def test_accumulation_decomposition_registered_in_composition_registry() -> None:
    defn = CompositionRegistry.get("accumulation_decomposition")
    assert defn is not None
    assert defn.remotion_component_id == "AccumulationDecomposition"
    assert defn.asset_requirement == AssetRequirement.NONE
    assert "accumulation" in defn.supported_relationship_types
    assert "standard" in defn.allowed_variants
    assert "contributions_vs_returns" in defn.allowed_variants
    assert "milestone_layers" in defn.allowed_variants


def test_accumulation_decomposition_builder_and_eligibility() -> None:
    intent = VisualIntent(
        intent_id="intent_accum_01",
        narration_excerpt="After 10 years of ₹10,000 monthly investing, your ₹12 lakh principal grows into a ₹30 lakh corpus.",
        what_viewer_must_understand="Contributions build a total corpus where compounding returns account for the majority of wealth.",
        relationship_type="accumulation",
        temporal=TemporalContext(horizon="10 Years"),
        measurements=[
            QuantitativeMeasurement(raw_value="₹12 Lakh", role="input", metric_name="Your Contributions", numeric_value=12.0),
            QuantitativeMeasurement(raw_value="₹30 Lakh", role="result", metric_name="Total Corpus", numeric_value=30.0),
        ],
        visual_dynamics=VisualDynamics(focal_point="SIP WEALTH DECOMPOSITION"),
    )

    assert is_eligible_accumulation_decomposition(intent) is True
    built = build_accumulation_decomposition_data(intent)

    assert built["total_value"] == "₹30 Lakh"
    assert built["total_label"] == "Total Corpus"
    assert built["time_horizon"] == "10 Years"
    assert len(built["streams"]) == 2
    assert built["streams"][0]["label"] == "Your Contributions"
    assert built["streams"][0]["value"] == "₹12 Lakh"
    assert built["streams"][1]["label"] == "Investment Returns"
    assert "18" in built["streams"][1]["value"]
    assert built["header_label"] == "SIP WEALTH DECOMPOSITION"


def test_composition_resolver_maps_accumulation_decomposition_props() -> None:
    resolver = CompositionResolver()
    spec = resolver.resolve_composition(
        composition_id="accumulation_decomposition",
        composition_data={
            "header_label": "WEALTH ACCUMULATION",
            "total_value": "₹1 Crore",
            "total_label": "Retirement Target",
            "time_horizon": "15 Years",
            "streams": [
                {
                    "label": "Personal Savings",
                    "value": "₹36 Lakh",
                    "color_token": "emerald",
                    "numeric_amount": 3600000.0,
                },
                {
                    "label": "Employer PF",
                    "value": "₹24 Lakh",
                    "color_token": "amber",
                    "numeric_amount": 2400000.0,
                },
                {
                    "label": "Equity Returns",
                    "value": "₹40 Lakh",
                    "rate": "12% CAGR",
                    "color_token": "cyan",
                    "numeric_amount": 4000000.0,
                },
            ],
            "annotation": "Compound returns generate 40% of the target.",
            "variant": "milestone_layers",
        },
    )

    assert spec.component_id == "AccumulationDecomposition"
    props = spec.props
    assert props["headerLabel"] == "WEALTH ACCUMULATION"
    assert props["totalValue"] == "₹1 Crore"
    assert props["totalLabel"] == "Retirement Target"
    assert props["timeHorizon"] == "15 Years"
    assert len(props["streams"]) == 3
    assert props["streams"][0]["label"] == "Personal Savings"
    assert props["streams"][0]["colorToken"] == "emerald"
    assert props["streams"][2]["rate"] == "12% CAGR"
    assert props["variant"] == "milestone_layers"
