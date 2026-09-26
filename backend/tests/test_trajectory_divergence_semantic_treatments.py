"""Tests for Trajectory Divergence composition."""
import pytest
from typing import Any

try:
    from domain.visual_intent import (
        VisualIntent,
        ComparisonContext,
        QuantitativeMeasurement,
        TemporalContext,
        VisualDynamics,
    )
    from registries.composition_registry import (
        AssetRequirement,
        CompositionRegistry,
        TrajectoryDivergenceData,
        TrajectoryPath,
    )
    from engines.video_assembly.composition_resolver import CompositionResolver
except ImportError:
    pytest.skip("TrajectoryDivergenceData or ComparisonContext not yet registered", allow_module_level=True)


def test_trajectory_divergence_schema_accepts_valid_payload() -> None:
    data = TrajectoryDivergenceData(
        time_horizon="10 Years",
        baseline_label="₹30,000 Monthly Commitment",
        path_a=TrajectoryPath(
            label="Investor (Equity SIP)",
            start_value="₹0",
            end_value="₹38 Lakh",
            rate="12% CAGR",
            direction="up",
            tone="positive",
        ),
        path_b=TrajectoryPath(
            label="Spender (Car Loan EMI)",
            start_value="₹15 Lakh Car",
            end_value="₹6 Lakh Resale",
            rate="15% Depreciation",
            direction="down",
            tone="negative",
        ),
        divergence_gap="₹32 Lakh Wealth Gap",
        header_label="WEALTH ACCUMULATION DIVERGENCE",
        variant="wealth_gap",
    )
    assert data.time_horizon == "10 Years"
    assert data.path_a.end_value == "₹38 Lakh"
    assert data.path_b.end_value == "₹6 Lakh Resale"
    assert data.divergence_gap == "₹32 Lakh Wealth Gap"
    assert data.variant == "wealth_gap"



def test_trajectory_divergence_contract_gap_not_required() -> None:
    """CRITICAL CONTRACT: divergence_gap must NOT be required in TrajectoryDivergenceData."""
    data = TrajectoryDivergenceData(
        time_horizon="7 Years",
        baseline_label="Career Starting Point",
        path_a=TrajectoryPath(
            label="High Growth Portfolio",
            end_value="₹50 Lakh",
        ),
        path_b=TrajectoryPath(
            label="Conservative Debt",
            end_value="₹22 Lakh",
        ),
    )
    assert data.time_horizon == "7 Years"
    assert data.divergence_gap is None
    assert data.header_label == "COMPOUNDING DIVERGENCE"


def test_trajectory_divergence_registered_in_composition_registry() -> None:
    defn = CompositionRegistry.get("trajectory_divergence")
    assert defn is not None
    assert defn.remotion_component_id == "TrajectoryDivergence"
    assert defn.asset_requirement == AssetRequirement.NONE
    assert "divergence" in defn.supported_relationship_types
    assert "divergence" in defn.allowed_variants
    assert "wealth_gap" in defn.allowed_variants
    assert "cost_opportunity" in defn.allowed_variants
    assert "standard" in defn.allowed_variants






def test_composition_resolver_maps_trajectory_divergence_props() -> None:
    resolver = CompositionResolver()
    spec = resolver.resolve_composition(
        composition_id="trajectory_divergence",
        composition_data={
            "time_horizon": "10 Years",
            "baseline_label": "Monthly ₹25,000",
            "path_a": {
                "label": "Equity Mutual Fund",
                "start_value": "₹0",
                "end_value": "₹55 Lakh",
                "rate": "12% CAGR",
                "direction": "up",
                "tone": "positive",
            },
            "path_b": {
                "label": "New Luxury Car",
                "start_value": "₹20 Lakh",
                "end_value": "₹5 Lakh",
                "rate": "18% Depreciation",
                "direction": "down",
                "tone": "negative",
            },
            "divergence_gap": "₹50 Lakh Wealth Gap",
            "header_label": "TEN YEAR TRAJECTORY",
            "variant": "wealth_gap",
        },
    )

    assert spec.component_id == "TrajectoryDivergence"
    props = spec.props
    assert props["timeHorizon"] == "10 Years"
    assert props["baselineLabel"] == "Monthly ₹25,000"
    assert props["pathA"]["label"] == "Equity Mutual Fund"
    assert props["pathA"]["endValue"] == "₹55 Lakh"
    assert props["pathA"]["rate"] == "12% CAGR"
    assert props["pathA"]["direction"] == "up"
    assert props["pathB"]["label"] == "New Luxury Car"
    assert props["pathB"]["endValue"] == "₹5 Lakh"
    assert props["pathB"]["rate"] == "18% Depreciation"
    assert props["pathB"]["direction"] == "down"
    assert props["divergenceGap"] == "₹50 Lakh Wealth Gap"
    assert props["headerLabel"] == "TEN YEAR TRAJECTORY"
    assert props["variant"] == "wealth_gap"


def test_trajectory_divergence_baseline_label_optional_and_safe() -> None:
    """Verifies that baseline_label is optional, defaults to None, and passes data filler grounding."""
    from engines.composition_data_filler_engine import _validate_grounding

    data = TrajectoryDivergenceData(
        time_horizon="10 Years",
        path_a=TrajectoryPath(label="Investor", end_value="₹38 Lakh"),
        path_b=TrajectoryPath(label="Spender", end_value="₹6 Lakh"),
    )
    assert data.baseline_label is None

    # Verify validation passes when baseline_label is omitted
    is_valid, errors, normalized = CompositionRegistry.validate_composition_data(
        "trajectory_divergence",
        data.model_dump(),
    )
    assert is_valid is True
    assert errors == []
    assert normalized.get("baseline_label") is None

    # Verify grounding check passes with no placeholder error
    intent = VisualIntent(
        intent_id="intent_div",
        narration_excerpt="Investing vs car emi divergence",
        what_viewer_must_understand="Wealth gap widens over 10 years",
        key_values=[],
        relationship_type="divergence",
    )
    _validate_grounding(intent=intent, composition_id="trajectory_divergence", data=normalized)
