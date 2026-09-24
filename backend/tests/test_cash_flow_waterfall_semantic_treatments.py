"""Tests for Cash Flow Waterfall composition."""
import pytest
from typing import Any

from domain.visual_intent import (
    VisualIntent,
    QuantitativeMeasurement,
    VisualDynamics,
)
from engines.composition_planner_engine import (
    build_candidate_composition_data,
    merge_factual_and_presentation_data,
)
from engines.video_assembly.composition_resolver import CompositionResolver
try:
    from registries.composition_registry import (
        AssetRequirement,
        CompositionRegistry,
        CashFlowWaterfallData,
        WaterfallStep,
    )
except ImportError:
    pytest.skip("CashFlowWaterfallData not yet registered", allow_module_level=True)


def test_cash_flow_waterfall_schema_accepts_valid_payload() -> None:
    data = CashFlowWaterfallData(
        starting_label="Gross Monthly Salary",
        starting_value="₹5,00,000",
        steps=[
            WaterfallStep(
                label="Income Tax",
                value="-₹1,50,000",
                direction="subtract",
                subtext="Old Regime 30%",
                numeric_amount=150000.0,
            ),
            WaterfallStep(
                label="Car & Home EMI",
                value="-₹1,20,000",
                direction="subtract",
                subtext="Fixed Debt Obligations",
                numeric_amount=120000.0,
            ),
            WaterfallStep(
                label="Living Expenses",
                value="-₹1,50,000",
                direction="subtract",
                subtext="Rent, Food, Utilities",
                numeric_amount=150000.0,
            ),
        ],
        final_label="Investable Surplus",
        final_value="₹80,000",
        header_label="MONTHLY CASH FLOW",
        variant="standard",
    )
    assert data.starting_value == "₹5,00,000"
    assert len(data.steps) == 3
    assert data.final_value == "₹80,000"
    assert data.steps[0].direction == "subtract"


def test_cash_flow_waterfall_contract_final_value_not_required() -> None:
    """CRITICAL CONTRACT: final_value must NOT be required in CashFlowWaterfallData."""
    data = CashFlowWaterfallData(
        starting_label="Total Inflow",
        starting_value="₹3,00,000",
        steps=[
            WaterfallStep(label="Taxes", value="-₹60,000"),
            WaterfallStep(label="Debt Service", value="-₹80,000"),
        ],
    )
    assert data.starting_value == "₹3,00,000"
    assert data.final_value is None
    assert data.final_label == "Remaining Balance"


def test_cash_flow_waterfall_registered_in_composition_registry() -> None:
    defn = CompositionRegistry.get("cash_flow_waterfall")
    assert defn is not None
    assert defn.remotion_component_id == "CashFlowWaterfall"
    assert defn.asset_requirement == AssetRequirement.NONE
    assert "waterfall" in defn.supported_relationship_types
    assert "standard" in defn.allowed_variants
    assert "detailed" in defn.allowed_variants
    assert "compact" in defn.allowed_variants


def test_build_candidate_waterfall_derives_final_balance_deterministically() -> None:
    """If starting value and all adjustments are numeric, backend deterministically derives final balance."""
    intent = VisualIntent(
        intent_id="intent_waterfall_01",
        chunk_index=1,
        narration_excerpt="From ₹5,00,000 gross salary, ₹1,50,000 goes to taxes, ₹1,20,000 to EMIs, and ₹1,50,000 to living expenses, leaving ₹80,000 surplus.",
        what_viewer_must_understand="Cash flow depletion leaves small investable surplus",
        relationship_type="waterfall",
        measurements=[
            QuantitativeMeasurement(
                raw_value="₹5,00,000",
                metric_name="Gross Monthly Salary",
                numeric_value=500000.0,
                role="baseline",
            ),
            QuantitativeMeasurement(
                raw_value="₹1,50,000",
                metric_name="Taxes",
                numeric_value=150000.0,
                role="delta",
            ),
            QuantitativeMeasurement(
                raw_value="₹1,20,000",
                metric_name="EMI Obligations",
                numeric_value=120000.0,
                role="delta",
            ),
            QuantitativeMeasurement(
                raw_value="₹1,50,000",
                metric_name="Living Costs",
                numeric_value=150000.0,
                role="delta",
            ),
        ],
        visual_dynamics=VisualDynamics(
            focal_point="SALARY DRAIN BREAKDOWN",
            visual_priority="high",
        ),
    )

    candidate = build_candidate_composition_data("cash_flow_waterfall", intent)
    assert candidate["starting_value"] == "₹5,00,000"
    assert candidate["starting_label"] == "Gross Monthly Salary"
    assert len(candidate["steps"]) == 3
    # Deterministic derivation: 5,00,000 - 1,50,000 - 1,20,000 - 1,50,000 = 80,000
    assert candidate["final_value"] == "₹80,000"
    assert candidate["final_label"] == "Remaining Balance"
    assert candidate["header_label"] == "SALARY DRAIN BREAKDOWN"


def test_build_candidate_waterfall_does_not_invent_when_numbers_missing() -> None:
    """When adjustments are qualitative/missing numbers, final_value is NOT invented."""
    intent = VisualIntent(
        intent_id="intent_waterfall_qualitative",
        chunk_index=1,
        narration_excerpt="From your starting corpus, taxes and hidden fees eat away the balance.",
        what_viewer_must_understand="Corpus depletion",
        relationship_type="waterfall",
        measurements=[
            QuantitativeMeasurement(
                raw_value="₹50 Lakh",
                metric_name="Initial Corpus",
                role="baseline",
            ),
            QuantitativeMeasurement(
                raw_value="Substantial Cut",
                metric_name="Taxes",
                role="delta",
            ),
        ],
    )

    candidate = build_candidate_composition_data("cash_flow_waterfall", intent)
    assert candidate["starting_value"] == "₹50 Lakh"
    assert candidate["starting_label"] == "Initial Corpus"
    assert len(candidate["steps"]) == 1
    # No synthetic final value!
    assert "final_value" not in candidate or candidate.get("final_value") is None


def test_merge_preserves_waterfall_facts_and_allows_presentation_subtext() -> None:
    candidate_facts = {
        "starting_value": "₹5,00,000",
        "starting_label": "Gross Income",
        "steps": [
            {"label": "Taxes", "value": "-₹1,50,000", "direction": "subtract"},
            {"label": "Debt", "value": "-₹1,20,000", "direction": "subtract"},
        ],
        "final_value": "₹2,30,000",
        "final_label": "Remaining Balance",
    }
    llm_data = {
        "starting_value": "₹99,99,999",  # Drift from LLM
        "steps": [
            {"subtext": "Direct Tax Code"},
            {"subtext": "Car & Personal Loans"},
        ],
        "final_label": "Investable Cash Flow",
        "header_label": "CASH FLOW ANALYSIS",
    }
    intent = VisualIntent(
        intent_id="intent_wf_merge",
        chunk_index=1,
        narration_excerpt="Salary cash flow",
        what_viewer_must_understand="Cash flow",
        relationship_type="waterfall",
    )

    merged = merge_factual_and_presentation_data(
        "cash_flow_waterfall",
        candidate_facts,
        llm_data,
        intent,
    )
    # Numerical facts locked
    assert merged["starting_value"] == "₹5,00,000"
    assert merged["final_value"] == "₹2,30,000"
    assert merged["steps"][0]["value"] == "-₹1,50,000"
    # Presentation fields merged
    assert merged["steps"][0]["subtext"] == "Direct Tax Code"
    assert merged["steps"][1]["subtext"] == "Car & Personal Loans"
    assert merged["final_label"] == "Investable Cash Flow"
    assert merged["header_label"] == "CASH FLOW ANALYSIS"


def test_composition_resolver_maps_cash_flow_waterfall_props() -> None:
    resolver = CompositionResolver()
    spec = resolver.resolve_composition(
        composition_id="cash_flow_waterfall",
        composition_data={
            "starting_label": "Gross Inflow",
            "starting_value": "₹10 Lakh",
            "steps": [
                {
                    "label": "Taxes (30%)",
                    "value": "-₹3 Lakh",
                    "direction": "subtract",
                    "subtext": "Highest Bracket",
                    "numeric_amount": 300000.0,
                },
                {
                    "label": "Operating Expenses",
                    "value": "-₹4 Lakh",
                    "direction": "subtract",
                    "subtext": "Salaries & Rent",
                    "numeric_amount": 400000.0,
                },
            ],
            "final_label": "Net Operating Cash",
            "final_value": "₹3 Lakh",
            "header_label": "BUSINESS WATERFALL",
            "variant": "detailed",
        },
    )

    assert spec.component_id == "CashFlowWaterfall"
    props = spec.props
    assert props["startingLabel"] == "Gross Inflow"
    assert props["startingValue"] == "₹10 Lakh"
    assert len(props["steps"]) == 2
    assert props["steps"][0]["label"] == "Taxes (30%)"
    assert props["steps"][0]["direction"] == "subtract"
    assert props["steps"][0]["subtext"] == "Highest Bracket"
    assert props["finalLabel"] == "Net Operating Cash"
    assert props["finalValue"] == "₹3 Lakh"
    assert props["headerLabel"] == "BUSINESS WATERFALL"
    assert props["variant"] == "detailed"
