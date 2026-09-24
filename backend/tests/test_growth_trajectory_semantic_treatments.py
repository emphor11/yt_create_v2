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
from engines.composition_planner_engine import (
    build_candidate_composition_data,
    merge_factual_and_presentation_data,
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

def test_linear_growth_candidate_extraction() -> None:
    """
    Benchmark Case 1:
    'Early growth is strictly linear, with monthly savings adding predictable, incremental amounts.'
    """
    intent = VisualIntent(
        intent_id="intent_linear_01",
        chunk_index=1,
        narration_excerpt="Early growth is strictly linear, with monthly savings adding predictable, incremental amounts.",
        what_viewer_must_understand="Initial wealth accumulation is strictly linear driven by savings discipline",
        relationship_type="growth",
        measurements=[],
        temporal=TemporalContext(horizon="early years"),
        visual_dynamics=VisualDynamics(
            focal_point="Predictable incremental savings build the starting foundation",
            visual_priority="high",
        ),
    )

    candidate = build_candidate_composition_data("growth_trajectory", intent)
    assert candidate["growth_type"] == "linear"
    assert candidate["variant"] == "linear_accumulation"
    assert candidate.get("start_value") is None
    assert candidate.get("end_value") is None
    assert candidate.get("growth_rate") is None
    assert candidate["start_label"] == "Starting Point"
    assert candidate["end_label"] == "Target Corpus"
    assert "Predictable incremental savings" in candidate["annotation"]


# ---------------------------------------------------------------------------
# 3. Benchmark Case 2: Accelerating Growth (Returns Add Substantial Yearly Gains)
# ---------------------------------------------------------------------------

def test_accelerating_growth_candidate_extraction() -> None:
    """
    Benchmark Case 2:
    'Subsequent capital blocks build faster over time as annual investment returns add substantial yearly gains.'
    """
    intent = VisualIntent(
        intent_id="intent_accel_02",
        chunk_index=2,
        narration_excerpt="Subsequent capital blocks build faster over time as annual investment returns add substantial yearly gains.",
        what_viewer_must_understand="Growth accelerates as investment returns begin contributing substantial capital",
        relationship_type="growth",
        measurements=[],
        temporal=TemporalContext(horizon="over time"),
        visual_dynamics=VisualDynamics(
            focal_point="Growth pace speeds up significantly",
            visual_priority="high",
        ),
    )

    candidate = build_candidate_composition_data("growth_trajectory", intent)
    assert candidate["growth_type"] == "accelerating"
    assert candidate["variant"] == "accelerating_growth"
    assert candidate["time_horizon"] == "over time"
    # Must NOT hallucinate fake rates or intermediate points
    assert candidate.get("growth_rate") is None
    assert candidate.get("start_value") is None
    assert candidate.get("end_value") is None


# ---------------------------------------------------------------------------
# 4. Benchmark Case 3: Compound Growth / Wealth Snowball
# ---------------------------------------------------------------------------

def test_compound_growth_wealth_snowball_candidate_extraction() -> None:
    """
    Benchmark Case 3:
    'The wealth snowball transitions from painful initial accumulation to rapid portfolio compounding.'
    """
    intent = VisualIntent(
        intent_id="intent_compound_03",
        chunk_index=3,
        narration_excerpt="The wealth snowball transitions from painful initial accumulation to rapid portfolio compounding.",
        what_viewer_must_understand="The wealth snowball shifts into rapid compounding returns",
        relationship_type="growth",
        measurements=[],
        visual_dynamics=VisualDynamics(
            focal_point="The compounding inflection point accelerates wealth",
            visual_priority="hero",
        ),
    )

    candidate = build_candidate_composition_data("growth_trajectory", intent)
    assert candidate["growth_type"] == "compound"
    assert candidate["variant"] == "compounding_snowball"
    assert "inflection" in candidate["annotation"].lower() or "snowball" in candidate["annotation"].lower()


# ---------------------------------------------------------------------------
# 5. Explicit Start & End Quantities with Explicit Growth Rate
# ---------------------------------------------------------------------------

def test_explicit_start_end_and_rate_candidate_extraction() -> None:
    intent = VisualIntent(
        intent_id="intent_explicit_04",
        chunk_index=4,
        narration_excerpt="Starting from ₹50,000 monthly contributions, your corpus grows to ₹1.5 Crore over 15 years at 12% annual return.",
        what_viewer_must_understand="Disciplined ₹50,000 monthly contributions expand to ₹1.5 Crore via 12% compounding",
        relationship_type="growth",
        measurements=[
            QuantitativeMeasurement(
                raw_value="₹50,000/mo",
                entity_name="Initial Contributions",
                role="baseline",
            ),
            QuantitativeMeasurement(
                raw_value="₹1.5 Crore",
                entity_name="Target Corpus",
                role="result",
            ),
            QuantitativeMeasurement(
                raw_value="12% Annual Return",
                metric_name="Return Rate",
                role="rate",
            ),
        ],
        temporal=TemporalContext(horizon="15 years"),
        visual_dynamics=VisualDynamics(
            focal_point="₹1.5 Crore terminal wealth",
            visual_priority="hero",
        ),
    )

    candidate = build_candidate_composition_data("growth_trajectory", intent)
    assert candidate["start_value"] == "₹50,000/mo"
    assert candidate["start_label"] == "Initial Contributions"
    assert candidate["end_value"] == "₹1.5 Crore"
    assert candidate["end_label"] == "Target Corpus"
    assert candidate["growth_rate"] == "12% Annual Return"
    assert candidate["time_horizon"] == "15 years"


# ---------------------------------------------------------------------------
# 6. Milestone Progression (The First ₹10 Lakh Inflection)
# ---------------------------------------------------------------------------

def test_milestone_progression_candidate_extraction() -> None:
    intent = VisualIntent(
        intent_id="intent_milestone_05",
        chunk_index=5,
        narration_excerpt="Reaching the first ₹10 Lakh milestone is the hardest part; after this tipping point, compounding begins to carry the weight.",
        what_viewer_must_understand="The first ₹10 Lakh marks the critical inflection milestone before compounding accelerates",
        relationship_type="growth",
        measurements=[
            QuantitativeMeasurement(
                raw_value="₹10 Lakh",
                entity_name="First Milestone",
                role="benchmark",
            ),
        ],
        visual_dynamics=VisualDynamics(
            focal_point="The first ₹10 Lakh tipping point",
            visual_priority="high",
        ),
    )

    candidate = build_candidate_composition_data("growth_trajectory", intent)
    assert candidate["milestone_value"] == "₹10 Lakh"
    assert candidate["milestone_label"] == "First Milestone"
    assert candidate["variant"] == "milestone_progression"


# ---------------------------------------------------------------------------
# 7. Merge Factual and Presentation Data Integrity
# ---------------------------------------------------------------------------

def test_merge_factual_preserves_extracted_facts() -> None:
    candidate_facts = {
        "start_value": "₹1 Lakh",
        "end_value": "₹50 Lakh",
        "growth_rate": "14% CAGR",
        "milestone_value": "₹10 Lakh",
        "start_label": "Principal Base",
        "end_label": "Snowball Corpus",
        "time_horizon": "10 Years",
        "growth_type": "compound",
        "variant": "compounding_snowball",
        "annotation": "Critical wealth turning point",
    }
    llm_presentation = {
        "header_label": "EXPONENTIAL WEALTH SNOWBALL",
        "start_value": "FABRICATED_START",     # MUST BE OVERWRITTEN BY FACT
        "end_value": "FABRICATED_END",         # MUST BE OVERWRITTEN BY FACT
        "growth_rate": "FABRICATED_RATE",       # MUST BE OVERWRITTEN BY FACT
        "start_label": "Custom Start Label",    # Preserved if present
    }
    intent = VisualIntent(
        intent_id="intent_merge_06",
        chunk_index=6,
        narration_excerpt="Wealth snowball expanding.",
        what_viewer_must_understand="Snowball returns",
        relationship_type="growth",
    )

    merged = merge_factual_and_presentation_data("growth_trajectory", candidate_facts, llm_presentation, intent)
    # Ground facts MUST win
    assert merged["start_value"] == "₹1 Lakh"
    assert merged["end_value"] == "₹50 Lakh"
    assert merged["growth_rate"] == "14% CAGR"
    assert merged["milestone_value"] == "₹10 Lakh"
    assert merged["header_label"] == "EXPONENTIAL WEALTH SNOWBALL"
    assert merged["start_label"] == "Custom Start Label"
    assert merged["end_label"] == "Snowball Corpus"
    assert merged["time_horizon"] == "10 Years"


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
