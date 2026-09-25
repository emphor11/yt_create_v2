from typing import Any
import pytest
from registries.composition_registry import CompositionRegistry, ComparisonSplitData
from engines.video_assembly.composition_resolver import CompositionResolver
from domain.visual_intent import (
    VisualIntent,
    SemanticEntity,
    ComparisonStructure,
)


def test_comparison_split_data_accepts_all_fields() -> None:
    data = ComparisonSplitData(
        left_role="Traditional FD",
        left_value="6.5%",
        left_label="Fixed Deposit",
        left_unit="p.a.",
        right_role="Nifty 50 Index",
        right_value="12.2%",
        right_label="Index Fund SIP",
        right_unit="CAGR",
        comparison_label="20-YEAR WEALTH OUTCOME",
        header_label="STRATEGY BENCHMARK",
        delta="+5.7% Real Alpha",
        winner="right",
        tone="superiority",
        variant="editorial",
    )
    assert data.left_role == "Traditional FD"
    assert data.left_value == "6.5%"
    assert data.right_role == "Nifty 50 Index"
    assert data.right_value == "12.2%"
    assert data.comparison_label == "20-YEAR WEALTH OUTCOME"
    assert data.header_label == "STRATEGY BENCHMARK"
    assert data.delta == "+5.7% Real Alpha"
    assert data.winner == "right"
    assert data.tone == "superiority"
    assert data.variant == "editorial"


def test_comparison_split_backward_compatibility() -> None:
    data = ComparisonSplitData(
        left_role="Option A",
        left_value="₹10,000",
        right_role="Option B",
        right_value="₹25,000",
    )
    assert data.left_role == "Option A"
    assert data.left_value == "₹10,000"
    assert data.right_role == "Option B"
    assert data.right_value == "₹25,000"
    assert data.header_label is None
    assert data.variant is None
    assert data.delta is None
    assert data.winner is None
    assert data.tone is None


def test_comparison_split_registry_variants() -> None:
    defn = CompositionRegistry.get("comparison_split")
    assert defn is not None
    assert "editorial" in defn.allowed_variants
    assert "cards" in defn.allowed_variants
    assert "versus" in defn.allowed_variants
    assert "metric_compare" in defn.allowed_variants


def test_comparison_split_resolver_disambiguates_labels() -> None:
    resolver = CompositionResolver()
    
    # Case 1: Header label explicitly provided, comparison_label provided
    spec1 = resolver.resolve_composition(
        composition_id="comparison_split",
        composition_data={
            "left_role": "Active Fund",
            "left_value": "10.1%",
            "right_role": "Direct Index",
            "right_value": "12.4%",
            "header_label": "FEE DRAG ANALYSIS",
            "comparison_label": "NET COMPOUNDED RETURN",
            "winner": "right",
            "delta": "+2.3% Net Spread",
        },
    )
    assert spec1.props["headerLabel"] == "FEE DRAG ANALYSIS"
    assert spec1.props["comparisonLabel"] == "NET COMPOUNDED RETURN"
    assert spec1.props["winner"] == "right"
    assert spec1.props["delta"] == "+2.3% Net Spread"

    # Case 2: Only comparison_label provided -> headerLabel defaults to disambiguated string
    spec2 = resolver.resolve_composition(
        composition_id="comparison_split",
        composition_data={
            "left_role": "Active Fund",
            "left_value": "10.1%",
            "right_role": "Direct Index",
            "right_value": "12.4%",
            "comparison_label": "NET COMPOUNDED RETURN",
        },
    )
    assert spec2.props["headerLabel"] == "HEAD-TO-HEAD COMPARISON"
    assert spec2.props["comparisonLabel"] == "NET COMPOUNDED RETURN"

    # Case 3: header_label equals comparison_label -> disambiguated
    spec3 = resolver.resolve_composition(
        composition_id="comparison_split",
        composition_data={
            "left_role": "Active Fund",
            "left_value": "10.1%",
            "right_role": "Direct Index",
            "right_value": "12.4%",
            "header_label": "ANNUAL WEALTH",
            "comparison_label": "ANNUAL WEALTH",
        },
    )
    assert spec3.props["headerLabel"] == "HEAD-TO-HEAD COMPARISON"
    assert spec3.props["comparisonLabel"] == "ANNUAL WEALTH"



