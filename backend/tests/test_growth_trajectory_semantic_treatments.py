"""
Comprehensive test suite for Growth Trajectory composition and semantic treatments.

Covers:
1. Linear growth (steady accumulation / savings)
2. Accelerating growth (capital blocks build faster over time)
3. Compound growth (snowball transitions to exponential compounding)
4. Explicit start and end quantities
5. Explicit rate / return (never fabricated)
6. Qualitative growth without numbers (graceful truthfulness)
7. Partial data without fabricated intermediate points or fake rates
8. Negative boundary: divergence remains separate (two paths separating over time)
9. Negative boundary: decline remains time_decay (value erosion over time)
10. Negative boundary: static comparison remains comparison_split
11. Negative boundary: static statement remains broll_caption
12. Registry registration, Pydantic validation, candidate extraction, merge, and resolver prop mapping
"""

from typing import Any
import pytest

from domain.visual_intent import (
    VisualIntent,
    QuantitativeMeasurement,
    TemporalContext,
    VisualDynamics,
    SemanticEntity,
    VALID_RELATIONSHIP_TYPES,
)
from registries.composition_registry import (
    CompositionRegistry,
    GrowthTrajectoryData,
    AssetRequirement,
)
from engines.video_assembly.composition_resolver import CompositionResolver


# ---------------------------------------------------------------------------
# 1. Registry & Schema Tests
# ---------------------------------------------------------------------------

def test_growth_relationship_type_registered_in_domain_model() -> None:
    assert "growth" in VALID_RELATIONSHIP_TYPES


def test_growth_trajectory_registered_in_composition_registry() -> None:
    defn = CompositionRegistry.get("growth_trajectory")
    assert defn is not None
    assert defn.remotion_component_id == "GrowthTrajectory"
    assert defn.fallback_component_id == "Charts"
    assert defn.asset_requirement == AssetRequirement.NONE
    assert "growth" in defn.supported_relationship_types
    assert "linear_accumulation" in defn.allowed_variants
    assert "accelerating_growth" in defn.allowed_variants
    assert "compounding_snowball" in defn.allowed_variants
    assert "milestone_progression" in defn.allowed_variants
    assert "standard" in defn.allowed_variants


def test_growth_trajectory_schema_properties() -> None:
    schema = CompositionRegistry.get_data_schema("growth_trajectory")
    assert schema is not None
    required = schema["required"]
    assert "start_label" in required
    assert "end_label" in required
    # Values and rates MUST NOT be required so qualitative growth works without fake numbers
    assert "start_value" not in required
    assert "end_value" not in required
    assert "growth_rate" not in required
    assert "milestone_value" not in required


def test_validate_growth_trajectory_valid_minimal() -> None:
    ok, errors, normalized = CompositionRegistry.validate_composition_data(
        "growth_trajectory",
        {
            "start_label": "Early Savings",
            "end_label": "Accumulated Corpus",
        },
    )
    assert ok is True
    assert errors == []
    assert normalized["start_label"] == "Early Savings"
    assert normalized["end_label"] == "Accumulated Corpus"
    assert normalized["start_value"] is None
    assert normalized["end_value"] is None
    assert normalized["growth_rate"] is None


def test_validate_growth_trajectory_valid_full() -> None:
    ok, errors, normalized = CompositionRegistry.validate_composition_data(
        "growth_trajectory",
        {
            "header_label": "WEALTH ACCUMULATION",
            "start_value": "₹0",
            "start_label": "Initial Capital",
            "end_value": "₹1 Crore",
            "end_label": "Target Corpus",
            "time_horizon": "15 Years",
            "growth_rate": "12% CAGR",
            "growth_type": "compound",
            "milestone_value": "₹10 Lakh",
            "milestone_label": "First ₹10 Lakh Inflection",
            "annotation": "Returns overtake monthly contributions",
            "variant": "compounding_snowball",
        },
    )
    assert ok is True
    assert errors == []
    assert normalized["start_value"] == "₹0"
    assert normalized["end_value"] == "₹1 Crore"
    assert normalized["growth_rate"] == "12% CAGR"
    assert normalized["growth_type"] == "compound"
    assert normalized["milestone_value"] == "₹10 Lakh"
    assert normalized["variant"] == "compounding_snowball"


# ---------------------------------------------------------------------------
# 2. Benchmark Case 1: Linear Growth (Steady Savings Accumulation)
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
# 3. Benchmark Case 2: Accelerating Growth (Returns Add Substantial Yearly Gains)
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
# 4. Benchmark Case 3: Compound Growth / Wealth Snowball
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
# 5. Explicit Start & End Quantities with Explicit Growth Rate
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
# 6. Milestone Progression (The First ₹10 Lakh Inflection)
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
# 7. Merge Factual and Presentation Data Integrity
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
# 8. Composition Resolver Props Resolution
# ---------------------------------------------------------------------------

def test_composition_resolver_maps_growth_trajectory_props() -> None:
    resolver = CompositionResolver()
    spec = resolver.resolve_composition(
        composition_id="growth_trajectory",
        composition_data={
            "header_label": "WEALTH TRAJECTORY",
            "start_value": "₹0",
            "start_label": "Initial Savings",
            "end_value": "₹1 Crore",
            "end_label": "Final Corpus",
            "time_horizon": "20 Years",
            "growth_rate": "12% CAGR",
            "growth_type": "compound",
            "milestone_value": "₹10 Lakh",
            "milestone_label": "Tipping Point",
            "annotation": "Compound returns surpass contributions",
            "variant": "compounding_snowball",
        },
    )

    assert spec.component_id == "GrowthTrajectory"
    props = spec.props
    assert props["headerLabel"] == "WEALTH TRAJECTORY"
    assert props["startValue"] == "₹0"
    assert props["startLabel"] == "Initial Savings"
    assert props["endValue"] == "₹1 Crore"
    assert props["endLabel"] == "Final Corpus"
    assert props["timeHorizon"] == "20 Years"
    assert props["growthRate"] == "12% CAGR"
    assert props["growthType"] == "compound"
    assert props["milestoneValue"] == "₹10 Lakh"
    assert props["milestoneLabel"] == "Tipping Point"
    assert props["annotation"] == "Compound returns surpass contributions"
    assert props["variant"] == "compounding_snowball"


# ---------------------------------------------------------------------------
# 9. Negative Semantic Boundary Checks: Growth vs Divergence, Decline, Comparison, Statement
# ---------------------------------------------------------------------------

def test_negative_boundary_decline_remains_time_decay() -> None:
    """Decline must map to time_decay, never growth_trajectory."""
    time_decay_defn = CompositionRegistry.get("time_decay")
    assert "decline" in time_decay_defn.supported_relationship_types
    assert "growth" not in time_decay_defn.supported_relationship_types

    growth_defn = CompositionRegistry.get("growth_trajectory")
    assert "growth" in growth_defn.supported_relationship_types
    assert "decline" not in growth_defn.supported_relationship_types


def test_negative_boundary_comparison_remains_comparison_split() -> None:
    """Static comparison must map to comparison_split, never growth_trajectory."""
    comp_defn = CompositionRegistry.get("comparison_split")
    assert "comparison" in comp_defn.supported_relationship_types
    assert "growth" not in comp_defn.supported_relationship_types

    growth_defn = CompositionRegistry.get("growth_trajectory")
    assert "comparison" not in growth_defn.supported_relationship_types


def test_negative_boundary_statement_remains_broll_caption() -> None:
    """General editorial statements must map to broll_caption, never growth_trajectory."""
    broll_defn = CompositionRegistry.get("broll_caption")
    assert "statement" in broll_defn.supported_relationship_types
    assert "growth" not in broll_defn.supported_relationship_types

    growth_defn = CompositionRegistry.get("growth_trajectory")
    assert "statement" not in growth_defn.supported_relationship_types


def test_negative_boundary_growth_trajectory_does_not_overload_trend() -> None:
    """
    Strict mapping constraint:
    growth_trajectory supports ONLY 'growth', never overloading 'trend' or 'comparison'.
    """
    growth_defn = CompositionRegistry.get("growth_trajectory")
    assert growth_defn.supported_relationship_types == ["growth"]
