from typing import Any
import pytest
from registries.composition_registry import CompositionRegistry, TimeDecayData
from engines.composition_planner_engine import (
    build_candidate_composition_data,
    merge_factual_and_presentation_data,
)
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
        emphasis="purchasing_power_decline",
    )
    assert data.fixed_amount == "₹2 lakh"
    assert data.show_chart is True
    assert data.end_value is None
    assert data.severity is None
    assert data.variant is None


def test_time_decay_allowed_variants_in_registry() -> None:
    defn = CompositionRegistry.get("time_decay")
    assert defn is not None
    assert "mild_decay" in defn.allowed_variants
    assert "severe_decay" in defn.allowed_variants
    assert "inflation_erosion" in defn.allowed_variants
    assert "standard" in defn.allowed_variants


def test_build_candidate_composition_data_extracts_time_decay_semantics() -> None:
    intent = VisualIntent(
        intent_id="intent_decay_01",
        chunk_index=1,
        narration_excerpt="A fixed monthly pension of ₹50,000 loses 74% purchasing power to ₹13,000 over 25 years.",
        what_viewer_must_understand="Inflation severely erodes fixed income",
        relationship_type="decline",
        measurements=[
            QuantitativeMeasurement(
                raw_value="₹50,000",
                entity_name="Monthly Pension",
                role="baseline",
            ),
            QuantitativeMeasurement(
                raw_value="₹13,000",
                entity_name="Real Purchasing Power",
                role="result",
            ),
            QuantitativeMeasurement(
                raw_value="7.0% Annual Inflation",
                metric_name="Inflation Rate",
                role="rate",
            ),
        ],
        temporal=TemporalContext(
            horizon="25 Years",
            is_decay_over_time=True,
        ),
        visual_dynamics=VisualDynamics(
            focal_point="₹13,000 terminal value",
            visual_priority="high",
        ),
    )

    candidate = build_candidate_composition_data("time_decay", intent)
    assert candidate["fixed_amount"] == "₹50,000"
    assert candidate["amount_label"] == "Monthly Pension"
    assert candidate["time_period"] == "25 Years"
    assert candidate["end_value"] == "₹13,000"
    assert candidate["end_label"] == "Real Purchasing Power"
    assert candidate["drop_rate"] == "7.0% Annual Inflation"
    assert candidate["severity"] == "severe"


def test_merge_preserves_time_decay_semantics() -> None:
    candidate_facts = {
        "fixed_amount": "₹50,000",
        "amount_label": "Fixed Income",
        "time_period": "20 Years",
        "emphasis": "purchasing_power_decline",
        "end_value": "₹15,000",
        "drop_rate": "70%",
        "severity": "severe",
        "rate_label": "7% Inflation",
    }
    llm_data: dict[str, Any] = {
        "fixed_amount": "₹50,000",
        "annotation": "Critical loss of purchasing power",
    }
    intent = VisualIntent(
        intent_id="intent_decay_02",
        chunk_index=1,
        narration_excerpt="Inflation decays purchasing power.",
        what_viewer_must_understand="Loss",
        relationship_type="decline",
    )

    merged = merge_factual_and_presentation_data(
        composition_id="time_decay",
        candidate_facts=candidate_facts,
        llm_data=llm_data,
        intent=intent,
    )
    assert merged["fixed_amount"] == "₹50,000"
    assert merged["amount_label"] == "Fixed Income"
    assert merged["time_period"] == "20 Years"
    assert merged["end_value"] == "₹15,000"
    assert merged["drop_rate"] == "70%"
    assert merged["severity"] == "severe"
    assert merged["rate_label"] == "7% Inflation"
    assert merged["annotation"] == "Critical loss of purchasing power"


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
