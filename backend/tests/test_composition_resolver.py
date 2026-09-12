"""Tests for CompositionResolver."""
import pytest

from engines.video_assembly.composition_resolver import CompositionResolver


def test_resolve_metric_hero():
    resolver = CompositionResolver()
    spec = resolver.resolve_composition(
        composition_id="metric_hero",
        composition_data={
            "value": "₹50 lakh",
            "label": "Starting Corpus",
            "context": "as of 2024",
            "emphasis": "hero",
        },
        variant="hero",
    )
    assert spec.component_id == "MetricHero"
    assert spec.props["value"] == "₹50 lakh"
    assert spec.props["label"] == "Starting Corpus"
    assert spec.props["context"] == "as of 2024"
    assert spec.props["variant"] == "hero"


def test_resolve_calculation_story():
    resolver = CompositionResolver()
    spec = resolver.resolve_composition(
        composition_id="calculation_story",
        composition_data={
            "input_label": "Portfolio",
            "input_value": "₹50 lakh",
            "operation_label": "×",
            "rate_label": "4% rate",
            "result_label": "Annual Income",
            "result_value": "₹2 lakh",
            "note": "4% Rule",
        },
    )
    assert spec.component_id == "CalculationStory"
    assert spec.props["inputLabel"] == "Portfolio"
    assert spec.props["inputValue"] == "₹50 lakh"
    assert spec.props["operationLabel"] == "×"
    assert spec.props["rateLabel"] == "4% rate"
    assert spec.props["resultLabel"] == "Annual Income"
    assert spec.props["resultValue"] == "₹2 lakh"
    assert spec.props["note"] == "4% Rule"


def test_resolve_cause_effect():
    resolver = CompositionResolver()
    spec = resolver.resolve_composition(
        composition_id="cause_effect",
        composition_data={
            "causes": [
                {"label": "Inflation", "value": "7%"},
                {"label": "Low Yield", "value": "3%"},
            ],
            "connector": "combine to cause",
            "outcome_label": "Corpus Depletion",
            "outcome_value": "Year 15",
            "outcome_severity": "negative",
        },
    )
    assert spec.component_id == "CauseEffect"
    assert len(spec.props["causes"]) == 2
    assert spec.props["causes"][0]["label"] == "Inflation"
    assert spec.props["connector"] == "combine to cause"
    assert spec.props["outcomeLabel"] == "Corpus Depletion"
    assert spec.props["outcomeValue"] == "Year 15"
    assert spec.props["outcomeSeverity"] == "negative"


def test_resolve_time_decay():
    resolver = CompositionResolver()
    spec = resolver.resolve_composition(
        composition_id="time_decay",
        composition_data={
            "fixed_amount": "₹2 lakh",
            "amount_label": "Annual Withdrawal",
            "time_period": "15 years",
            "emphasis": "purchasing_power_decline",
            "annotation": "Buys 40% less",
            "show_chart": True,
        },
    )
    assert spec.component_id == "TimeDecay"
    assert spec.props["fixedAmount"] == "₹2 lakh"
    assert spec.props["amountLabel"] == "Annual Withdrawal"
    assert spec.props["timePeriod"] == "15 years"
    assert spec.props["emphasis"] == "purchasing_power_decline"
    assert spec.props["annotation"] == "Buys 40% less"
    assert spec.props["showChart"] is True


def test_resolve_multi_factor_pressure():
    resolver = CompositionResolver()
    spec = resolver.resolve_composition(
        composition_id="multi_factor_pressure",
        composition_data={
            "factors": [
                {"label": "Inflation", "value": "7%", "severity": "high"},
                {"label": "Healthcare", "value": "12%", "severity": "high"},
            ],
            "combined_label": "Retirement Hazard",
            "combined_severity": "critical",
            "outcome_note": "Immediate Action Required",
        },
    )
    assert spec.component_id == "MultiFactorPressure"
    assert len(spec.props["factors"]) == 2
    assert spec.props["combinedLabel"] == "Retirement Hazard"
    assert spec.props["combinedSeverity"] == "critical"
    assert spec.props["outcomeNote"] == "Immediate Action Required"


def test_resolve_broll_caption():
    resolver = CompositionResolver()
    spec = resolver.resolve_composition(
        composition_id="broll_caption",
        composition_data={
            "caption": "Inflation silently eats your capital.",
            "emphasis_phrase": "Lost purchasing power",
            "author": "Financial Proverb",
        },
    )
    assert spec.component_id == "BrollCaption"
    assert spec.props["caption"] == "Inflation silently eats your capital."
    assert spec.props["emphasisPhrase"] == "Lost purchasing power"
    assert spec.props["author"] == "Financial Proverb"


def test_resolve_unknown_composition_fallback():
    resolver = CompositionResolver()
    spec = resolver.resolve_composition(
        composition_id="non_existent_comp",
        composition_data={},
        visual_goal="Key visual takeaway",
    )
    assert spec.component_id == "Typography"
    assert spec.props["text"] == "Key visual takeaway"
    assert spec.props["variant"] == "statement"


def test_resolve_invalid_data_fallback():
    resolver = CompositionResolver()
    spec = resolver.resolve_composition(
        composition_id="calculation_story",
        composition_data={"invalid": "no required fields"},
        visual_goal="Calculation of interest",
    )
    assert spec.component_id == "Typography"
    assert spec.props["text"] == "Calculation of interest"
