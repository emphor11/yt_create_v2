import pytest
from domain.visual_intent import VisualIntent, QuantitativeMeasurement, TemporalContext
from engines.video_assembly.composition_resolver import CompositionResolver
from registries.composition_registry import CompositionRegistry, CalculationStoryData


def test_calculation_story_data_accepts_new_variants():
    for var in ["multiplication", "addition", "subtraction", "allocation", "growth", "neutral"]:
        data = CalculationStoryData(
            input_label="Starting Corpus",
            input_value="₹10 lakh",
            operation_label="+" if var == "addition" else "-" if var == "subtraction" else "→",
            rate_label="40%" if var == "allocation" else "₹20,000",
            result_label="Ending Value",
            result_value="₹1 crore" if var == "growth" else "₹80,000",
            operation_type=var,
            variant=var,
            timeframe="over 20 years" if var == "growth" else None,
        )
        assert data.variant == var
        assert data.operation_type == var
        assert data.input_value == "₹10 lakh"


def test_calculation_story_backwards_compatibility_with_old_payload():
    old_payload = {
        "input_label": "Portfolio",
        "input_value": "₹50 lakh",
        "operation_label": "×",
        "rate_label": "4% withdrawal rate",
        "result_label": "Annual Income",
        "result_value": "₹2 lakh",
        "note": "Safe Withdrawal Rate",
    }
    data = CalculationStoryData(**old_payload)
    assert data.input_value == "₹50 lakh"
    assert data.operation_label == "×"
    assert data.operation_type == "multiplication"










def test_composition_resolver_does_not_invent_multiplication():
    resolver = CompositionResolver()
    # Scenario: operation_label is neutral transformation symbol "→", not "×"
    spec = resolver.resolve_composition(
        composition_id="calculation_story",
        composition_data={
            "input_label": "Starting Salary",
            "input_value": "₹50,000",
            "operation_label": "→",
            "rate_label": "over 15 years",
            "result_label": "Final Value",
            "result_value": "₹1.2 Cr",
            "operation_type": "growth",
            "timeframe": "15 Years",
        },
    )
    assert spec.component_id == "CalculationStory"
    props = spec.props
    # operationLabel must NOT be "×"
    assert props["operationLabel"] == "→"
    assert props["operationType"] == "growth"
    assert props["timeframe"] == "15 Years"


def test_composition_resolver_defaults_operation_symbols():
    resolver = CompositionResolver()
    # When operation_label is omitted, resolver derives from operation_type
    spec_growth = resolver.resolve_composition(
        composition_id="calculation_story",
        composition_data={
            "input_label": "Capital",
            "input_value": "₹10L",
            "result_label": "Corpus",
            "result_value": "₹1Cr",
            "operation_type": "growth",
        },
    )
    assert spec_growth.props["operationLabel"] == "→"

    spec_sub = resolver.resolve_composition(
        composition_id="calculation_story",
        composition_data={
            "input_label": "Gross",
            "input_value": "₹1,00,000",
            "result_label": "Net",
            "result_value": "₹80,000",
            "operation_type": "subtraction",
        },
    )
    assert spec_sub.props["operationLabel"] == "−"

    spec_add = resolver.resolve_composition(
        composition_id="calculation_story",
        composition_data={
            "input_label": "Salary",
            "input_value": "₹1,00,000",
            "result_label": "Total",
            "result_value": "₹1,20,000",
            "operation_type": "addition",
        },
    )
    assert spec_add.props["operationLabel"] == "+"


def test_composition_resolver_maps_calculation_story_props():
    resolver = CompositionResolver()
    spec = resolver.resolve_composition(
        composition_id="calculation_story",
        composition_data={
            "input_label": "Base Salary",
            "input_value": "₹1,00,000",
            "operation_label": "+",
            "rate_label": "₹10,000 Bonus",
            "result_label": "Total Compensation",
            "result_value": "₹1,10,000",
            "operation_type": "addition",
            "variant": "addition",
            "polarity": "positive",
            "secondary_label": "Fixed Component",
            "secondary_value": "₹90,000",
        },
        variant="addition",
    )
    assert spec.component_id == "CalculationStory"
    props = spec.props
    assert props["inputValue"] == "₹1,00,000"
    assert props["operationLabel"] == "+"
    assert props["rateLabel"] == "₹10,000 Bonus"
    assert props["resultValue"] == "₹1,10,000"
    assert props["operationType"] == "addition"
    assert props["variant"] == "addition"
    assert props["polarity"] == "positive"
    assert props["secondaryLabel"] == "Fixed Component"
    assert props["secondaryValue"] == "₹90,000"

