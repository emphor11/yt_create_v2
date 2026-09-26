"""Tests for Debt Amortization Schedule composition."""
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
    DebtAmortizationScheduleData,
    AmortizationPeriod,
)
from registries.composition_builders import (
    build_debt_amortization_schedule_data,
    is_eligible_debt_amortization_schedule,
)


def test_debt_amortization_schedule_schema_accepts_valid_payload() -> None:
    data = DebtAmortizationScheduleData(
        header_label="LOAN AMORTIZATION SCHEDULE",
        loan_amount="₹50 Lakh",
        loan_label="Home Loan Principal",
        interest_rate="8.5% p.a.",
        tenure="20 Years",
        payment_amount="₹43,400/month",
        total_interest="₹54.1 Lakh",
        periods=[
            AmortizationPeriod(
                period_label="Year 1 (Early Phase)",
                principal_share="₹8,000 (18%)",
                interest_share="₹35,400 (82%)",
                remaining_balance="₹49.0 Lakh",
                principal_numeric=8000.0,
                interest_numeric=35400.0,
            ),
            AmortizationPeriod(
                period_label="Year 15 (Late Phase)",
                principal_share="₹32,000 (74%)",
                interest_share="₹11,400 (26%)",
                remaining_balance="₹18.2 Lakh",
                principal_numeric=32000.0,
                interest_numeric=11400.0,
            ),
        ],
        annotation="In early years, over 80% of your EMI goes toward bank interest, not paying down principal.",
        variant="interest_front_loaded",
    )
    assert data.loan_amount == "₹50 Lakh"
    assert data.tenure == "20 Years"
    assert len(data.periods) == 2
    assert data.periods[0].period_label == "Year 1 (Early Phase)"
    assert data.variant == "interest_front_loaded"


def test_debt_amortization_schedule_registered_in_composition_registry() -> None:
    defn = CompositionRegistry.get("debt_amortization_schedule")
    assert defn is not None
    assert defn.remotion_component_id == "DebtAmortizationSchedule"
    assert defn.asset_requirement == AssetRequirement.NONE
    assert "amortization" in defn.supported_relationship_types
    assert "standard" in defn.allowed_variants
    assert "interest_front_loaded" in defn.allowed_variants
    assert "prepayment_impact" in defn.allowed_variants
    assert "balance_paydown" in defn.allowed_variants


def test_debt_amortization_schedule_builder_and_eligibility() -> None:
    intent = VisualIntent(
        intent_id="intent_amort_01",
        narration_excerpt="On a ₹50 lakh home loan at 8.5% over 20 years, your ₹43,400 EMI is mostly interest upfront.",
        what_viewer_must_understand="Early loan payments go primarily to interest rather than reducing the debt balance.",
        relationship_type="amortization",
        temporal=TemporalContext(horizon="20 Years"),
        measurements=[
            QuantitativeMeasurement(raw_value="₹50 Lakh", role="baseline", metric_name="Home Loan Principal"),
            QuantitativeMeasurement(raw_value="8.5%", role="rate", metric_name="Interest Rate"),
            QuantitativeMeasurement(raw_value="₹43,400/month", role="input", metric_name="Monthly EMI"),
            QuantitativeMeasurement(raw_value="₹54 Lakh", role="result", metric_name="Total Lifetime Interest"),
        ],
        visual_dynamics=VisualDynamics(focal_point="MORTGAGE AMORTIZATION BREAKDOWN"),
    )

    assert is_eligible_debt_amortization_schedule(intent) is True
    built = build_debt_amortization_schedule_data(intent)

    assert built["loan_amount"] == "₹50 Lakh"
    assert built["loan_label"] == "Home Loan Principal"
    assert built["interest_rate"] == "8.5%"
    assert built["payment_amount"] == "₹43,400/month"
    assert built["total_interest"] == "₹54 Lakh"
    assert built["tenure"] == "20 Years"
    assert built["header_label"] == "MORTGAGE AMORTIZATION BREAKDOWN"


def test_composition_resolver_maps_debt_amortization_schedule_props() -> None:
    resolver = CompositionResolver()
    spec = resolver.resolve_composition(
        composition_id="debt_amortization_schedule",
        composition_data={
            "header_label": "CAR LOAN AMORTIZATION",
            "loan_amount": "₹15 Lakh",
            "loan_label": "Vehicle Loan",
            "interest_rate": "9.5% p.a.",
            "tenure": "5 Years",
            "payment_amount": "₹31,500/month",
            "total_interest": "₹3.9 Lakh",
            "periods": [
                {
                    "period_label": "Year 1",
                    "principal_share": "₹18,000",
                    "interest_share": "₹13,500",
                    "remaining_balance": "₹12.5 Lakh",
                }
            ],
            "annotation": "Depreciation and interest cost double the effective price.",
            "variant": "standard",
        },
    )

    assert spec.component_id == "DebtAmortizationSchedule"
    props = spec.props
    assert props["headerLabel"] == "CAR LOAN AMORTIZATION"
    assert props["loanAmount"] == "₹15 Lakh"
    assert props["loanLabel"] == "Vehicle Loan"
    assert props["interestRate"] == "9.5% p.a."
    assert props["tenure"] == "5 Years"
    assert props["paymentAmount"] == "₹31,500/month"
    assert len(props["periods"]) == 1
    assert props["periods"][0]["periodLabel"] == "Year 1"
    assert props["variant"] == "standard"
