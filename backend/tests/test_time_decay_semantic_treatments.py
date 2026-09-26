from typing import Any
import pytest
from registries.composition_registry import CompositionRegistry, TimeDecayData
from engines.video_assembly.composition_resolver import CompositionResolver
from domain.visual_intent import (
    VisualIntent,
    QuantitativeMeasurement,
    TemporalContext,
    VisualDynamics,
)


def test_time_decay_data_accepts_all_new_variants_and_fields() -> None:
    data = TimeDecayData(
        fixed_amount="₹50,000",
        amount_label="Monthly Pension",
        time_period="25 Years",
        emphasis="purchasing_power_decline",
        annotation="Erodes to ₹13,000 in real terms",
        show_chart=True,
        end_value="₹13,000",
        end_label="Real Purchasing Power",
        drop_rate="74%",
        severity="severe",
        variant="severe_decay",
        rate_label="7.0% Average Annual Inflation",
    )
    assert data.fixed_amount == "₹50,000"
    assert data.end_value == "₹13,000"
    assert data.drop_rate == "74%"
    assert data.severity == "severe"
    assert data.variant == "severe_decay"
    assert data.rate_label == "7.0% Average Annual Inflation"


def test_time_decay_backward_compatibility() -> None:
    data = TimeDecayData(
        fixed_amount="₹2 lakh",
        amount_label="Annual Withdrawal",
        time_period="15 years",
        end_value="₹1.2 lakh",
        emphasis="purchasing_power_decline",
    )
    assert data.fixed_amount == "₹2 lakh"
    assert data.end_value == "₹1.2 lakh"
    assert data.show_chart is True
    assert data.severity is None
    assert data.variant is None


def test_time_decay_allowed_variants_in_registry() -> None:
    defn = CompositionRegistry.get("time_decay")
    assert defn is not None
    assert "mild_decay" in defn.allowed_variants
    assert "severe_decay" in defn.allowed_variants
    assert "inflation_erosion" in defn.allowed_variants
    assert "standard" in defn.allowed_variants






def test_composition_resolver_maps_time_decay_semantic_props() -> None:
    resolver = CompositionResolver()
    spec = resolver.resolve_composition(
        composition_id="time_decay",
        composition_data={
            "fixed_amount": "₹1,00,000",
            "amount_label": "Bond Yield",
            "time_period": "5 Years",
            "emphasis": "real_vs_nominal",
            "annotation": "Mild real purchasing power erosion",
            "end_value": "₹82,000",
            "end_label": "Residual Purchasing Power",
            "drop_rate": "18%",
            "severity": "mild",
            "variant": "mild_decay",
            "rate_label": "3.5% Annual Inflation",
        },
    )

    assert spec.component_id == "TimeDecay"
    props = spec.props
    assert props["fixedAmount"] == "₹1,00,000"
    assert props["amountLabel"] == "Bond Yield"
    assert props["timePeriod"] == "5 Years"
    assert props["endValue"] == "₹82,000"
    assert props["endLabel"] == "Residual Purchasing Power"
    assert props["dropRate"] == "18%"
    assert props["severity"] == "mild"
    assert props["variant"] == "mild_decay"
    assert props["rateLabel"] == "3.5% Annual Inflation"
    assert props["decayType"] == "standard"




def test_time_decay_single_period_resolver_mapping() -> None:
    resolver = CompositionResolver()
    spec = resolver.resolve_composition(
        composition_id="time_decay",
        composition_data={
            "fixed_amount": "₹20 Lakh",
            "amount_label": "New Vehicle Value",
            "time_period": "First Year",
            "end_value": "₹17 Lakh",
            "emphasis": "single_period_drop",
            "drop_rate": "15%",
            "variant": "single_period_drop",
            "decay_type": "single_period",
        },
    )

    assert spec.component_id == "TimeDecay"
    props = spec.props
    assert props["fixedAmount"] == "₹20 Lakh"
    assert props["amountLabel"] == "New Vehicle Value"
    assert props["timePeriod"] == "First Year"
    assert props["endValue"] == "₹17 Lakh"
    assert props["dropRate"] == "15%"
    assert props["decayType"] == "single_period"
    assert props["variant"] == "single_period_drop"


