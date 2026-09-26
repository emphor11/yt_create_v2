"""Tests for Cash Flow Waterfall composition."""
import pytest
from typing import Any

from domain.visual_intent import (
    VisualIntent,
    QuantitativeMeasurement,
    VisualDynamics,
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


def test_cash_flow_waterfall_contract_final_value_is_required() -> None:
    """CRITICAL CONTRACT: final_value and final_label must be required in CashFlowWaterfallData."""
    with pytest.raises(Exception):
        CashFlowWaterfallData(
            starting_label="Total Inflow",
            starting_value="₹3,00,000",
            steps=[
                WaterfallStep(label="Taxes", value="-₹60,000"),
                WaterfallStep(label="Debt Service", value="-₹80,000"),
            ],
        )


def test_cash_flow_waterfall_registered_in_composition_registry() -> None:
    defn = CompositionRegistry.get("cash_flow_waterfall")
    assert defn is not None
    assert defn.remotion_component_id == "CashFlowWaterfall"
    assert defn.asset_requirement == AssetRequirement.NONE
    assert "waterfall" in defn.supported_relationship_types
    assert "standard" in defn.allowed_variants
    assert "detailed" in defn.allowed_variants
    assert "compact" in defn.allowed_variants








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
