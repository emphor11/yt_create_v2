import pytest
from domain.visual_intent import VisualIntent, QuantitativeMeasurement, TemporalContext
from engines.composition_planner_engine import (
    build_candidate_composition_data,
    merge_factual_and_presentation_data,
)
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


def test_build_candidate_composition_data_extracts_calculation_story_semantics():
    intent = VisualIntent(
        intent_id="calc_intent_01",
        narration_excerpt="₹10 lakh grows to ₹1 crore over 20 years.",
        what_viewer_must_understand="₹10 lakh grows to ₹1 crore over 20 years.",
        relationship_type="calculation",
        measurements=[
            QuantitativeMeasurement(
                raw_value="₹10 lakh",
                metric_name="Initial Corpus",
                role="input",
            ),
            QuantitativeMeasurement(
                raw_value="12% CAGR",
                role="rate",
            ),
            QuantitativeMeasurement(
                raw_value="₹1 crore",
                metric_name="Accumulated Wealth",
                polarity="positive",
                role="result",
            ),
        ],
        temporal=TemporalContext(
            horizon="over 20 years",
        ),
    )
    facts = build_candidate_composition_data("calculation_story", intent)
    assert facts["input_value"] == "₹10 lakh"
    assert facts["input_label"] == "Initial Corpus"
    assert facts["rate_label"] == "12% CAGR"
    assert facts["result_value"] == "₹1 crore"
    assert facts["result_label"] == "Accumulated Wealth"
    assert facts["polarity"] == "positive"
    assert facts["timeframe"] == "over 20 years"


def test_build_candidate_without_explicit_rate_label():
    """Verify calculation_story succeeds when only input and result exist (transformation)."""
    intent = VisualIntent(
        intent_id="calc_intent_transform",
        narration_excerpt="Starting salary of ₹50,000 grows to ₹2,00,000.",
        what_viewer_must_understand="Income quadrupled over career.",
        relationship_type="calculation",
        measurements=[
            QuantitativeMeasurement(
                raw_value="₹50,000",
                metric_name="Starting Salary",
                role="input",
            ),
            QuantitativeMeasurement(
                raw_value="₹2,00,000",
                metric_name="Final Salary",
                role="result",
            ),
        ],
    )
    facts = build_candidate_composition_data("calculation_story", intent)
    assert facts["input_value"] == "₹50,000"
    assert facts["input_label"] == "Starting Salary"
    assert facts["result_value"] == "₹2,00,000"
    assert facts["result_label"] == "Final Salary"
    assert facts["operation_type"] == "growth"
    assert "operation_label" not in facts
    assert facts.get("rate_label") is None
    spec = CompositionResolver().resolve_composition(
        composition_id="calculation_story",
        composition_data=facts,
    )
    assert spec.props["operationLabel"] == "→"


def test_build_candidate_subtraction_operation():
    """Verify subtraction keyword detection maps operation to subtraction."""
    intent = VisualIntent(
        intent_id="calc_intent_sub",
        narration_excerpt="Gross revenue minus ₹15 lakh operating expenses leaves ₹35 lakh EBITDA.",
        what_viewer_must_understand="Operating expenses reduce profit.",
        relationship_type="calculation",
        measurements=[
            QuantitativeMeasurement(
                raw_value="₹50 lakh",
                metric_name="Gross Revenue",
                role="input",
            ),
            QuantitativeMeasurement(
                raw_value="₹15 lakh",
                metric_name="Operating Expenses",
                role="delta",
            ),
            QuantitativeMeasurement(
                raw_value="₹35 lakh",
                metric_name="EBITDA",
                role="result",
            ),
        ],
    )
    facts = build_candidate_composition_data("calculation_story", intent)
    assert facts["input_value"] == "₹50 lakh"
    assert facts["result_value"] == "₹35 lakh"
    assert facts["operation_type"] == "subtraction"
    assert "operation_label" not in facts
    assert facts["rate_label"] == "₹15 lakh"
    assert facts["secondary_label"] == "Operating Expenses"
    spec = CompositionResolver().resolve_composition(
        composition_id="calculation_story",
        composition_data=facts,
    )
    assert spec.props["operationLabel"] == "−"


def test_merge_preserves_calculation_story_semantics_and_facts():
    candidate_facts = {
        "input_value": "₹1,00,000",
        "input_label": "Gross Income",
        "rate_label": "₹20,000 Tax",
        "result_value": "₹80,000",
        "result_label": "Net Take-Home",
        "polarity": "negative",
    }
    llm_data = {
        "input_value": "wrong_input",
        "result_value": "wrong_result",
        "operation_label": "-",
        "operation_type": "subtraction",
        "variant": "subtraction",
    }
    intent = VisualIntent(
        intent_id="intent_calc_sub",
        narration_excerpt="Gross income minus tax leaves net take home.",
        what_viewer_must_understand="Taxes reduce take home pay.",
        relationship_type="calculation",
    )
    merged = merge_factual_and_presentation_data("calculation_story", candidate_facts, llm_data, intent)
    # Numerical facts locked
    assert merged["input_value"] == "₹1,00,000"
    assert merged["result_value"] == "₹80,000"
    # Semantic fields passed through
    assert merged["operation_label"] == "-"
    assert merged["operation_type"] == "subtraction"
    assert merged["variant"] == "subtraction"
    assert merged["polarity"] == "negative"


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

