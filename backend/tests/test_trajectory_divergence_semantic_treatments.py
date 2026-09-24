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
    from engines.composition_planner_engine import (
        build_candidate_composition_data,
        merge_factual_and_presentation_data,
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


def test_build_candidate_trajectory_divergence_extracts_comparison_semantics() -> None:
    intent = VisualIntent(
        intent_id="intent_div_01",
        chunk_index=1,
        narration_excerpt="Over 10 years, putting ₹30,000 into an equity SIP creates ₹38 Lakh, while paying that same ₹30,000 as car EMI leaves you with a depreciated car worth just ₹6 Lakh—a ₹32 Lakh gap.",
        what_viewer_must_understand="Investing vs spending creates a ₹32 Lakh divergence gap over 10 years",
        relationship_type="divergence",
        comparison=ComparisonContext(
            subject_a="Investor (Equity SIP)",
            value_a="₹38 Lakh",
            subject_b="Spender (Car EMI)",
            value_b="₹6 Lakh",
            comparison_dimension="₹30,000 Monthly Allocation",
            delta="₹32 Lakh Wealth Gap",
        ),
        temporal=TemporalContext(
            horizon="10 Years",
        ),
        measurements=[
            QuantitativeMeasurement(
                raw_value="₹32 Lakh Wealth Gap",
                role="delta",
            ),
            QuantitativeMeasurement(
                raw_value="12% Return",
                role="rate",
            ),
        ],
        visual_dynamics=VisualDynamics(
            focal_point="THE COMPOUNDING SPREAD",
            visual_priority="high",
        ),
    )

    candidate = build_candidate_composition_data("trajectory_divergence", intent)
    assert candidate["time_horizon"] == "10 Years"
    assert candidate["baseline_label"] == "₹30,000 Monthly Allocation"
    assert candidate["path_a"]["label"] == "Investor (Equity SIP)"
    assert candidate["path_a"]["end_value"] == "₹38 Lakh"
    assert candidate["path_b"]["label"] == "Spender (Car EMI)"
    assert candidate["path_b"]["end_value"] == "₹6 Lakh"
    assert candidate["divergence_gap"] == "₹32 Lakh Wealth Gap"
    assert candidate["header_label"] == "THE COMPOUNDING SPREAD"


def test_merge_preserves_trajectory_divergence_facts() -> None:
    candidate_facts = {
        "time_horizon": "15 Years",
        "baseline_label": "Starting Investment",
        "path_a": {
            "label": "Strategy A",
            "end_value": "₹1 Crore",
            "rate": "14% CAGR",
            "direction": "up",
            "tone": "positive",
        },
        "path_b": {
            "label": "Strategy B",
            "end_value": "₹35 Lakh",
            "rate": "7% FD",
            "direction": "up",
            "tone": "neutral",
        },
        "divergence_gap": "₹65 Lakh Difference",
    }
    llm_data = {
        "time_horizon": "20 Years",  # Drift from LLM
        "path_a": {
            "label": "Index Fund SIP",  # Refined label
        },
        "path_b": {
            "label": "Fixed Deposit",   # Refined label
        },
        "header_label": "THE 15-YEAR WEALTH GAP",
    }
    intent = VisualIntent(
        intent_id="intent_div_merge",
        chunk_index=1,
        narration_excerpt="Wealth divergence over 15 years",
        what_viewer_must_understand="Wealth divergence",
        relationship_type="divergence",
    )

    merged = merge_factual_and_presentation_data(
        "trajectory_divergence",
        candidate_facts,
        llm_data,
        intent,
    )
    # Facts locked
    assert merged["time_horizon"] == "15 Years"
    assert merged["divergence_gap"] == "₹65 Lakh Difference"
    assert merged["path_a"]["end_value"] == "₹1 Crore"
    assert merged["path_b"]["end_value"] == "₹35 Lakh"
    assert merged["path_a"]["rate"] == "14% CAGR"
    # Refined presentation labels merged
    assert merged["path_a"]["label"] == "Index Fund SIP"
    assert merged["path_b"]["label"] == "Fixed Deposit"
    assert merged["header_label"] == "THE 15-YEAR WEALTH GAP"


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
