"""
Tests for CompositionPlannerEngine Rich VisualIntent Semantic Mapping.

Verifies:
1. CalculationStory uses measurement roles (input, rate, result) not list order.
2. Does NOT automatically invent values (e.g. operation_label is not assumed to be '×', severity is not assumed to be 'high').
3. TimeDecay uses baseline and result roles rather than list positions.
4. ComparisonSplit maps factual data directly from ComparisonStructure without re-parsing narration.
5. Deterministic facts override LLM hallucinated numbers while preserving LLM presentation labels.
6. Narration independence: dummy narration with rich intent yields complete, accurate composition_data.
"""
import pytest

from domain.composition_plan import CompositionBeat
from domain.visual_intent import (
    CausalStructure,
    ComparisonStructure,
    QuantitativeMeasurement,
    SemanticEntity,
    TemporalContext,
    VisualDynamics,
    VisualIntent,
)
from engines.composition_planner_engine import (
    CompositionPlannerEngine,
    build_candidate_composition_data,
    merge_factual_and_presentation_data,
)
from providers.llm_provider import (
    LLMJsonRequest,
    LLMJsonResponse,
    LLMProviderMetadata,
)


class MockLLMProvider:
    def __init__(self, payload: dict):
        self.payload = payload
        self.last_request: LLMJsonRequest | None = None

    def generate_json(self, request: LLMJsonRequest) -> LLMJsonResponse:
        self.last_request = request
        return LLMJsonResponse(
            payload=self.payload,
            metadata=LLMProviderMetadata(provider="mock-llm", model="mock-test"),
        )


# ============================================================================
# 1. CalculationStory Tests (Roles vs Positional Guessing & No Invented '×')
# ============================================================================

def test_calculation_story_uses_measurement_roles_not_positions() -> None:
    """
    Measurements passed in REVERSED order (result first, then rate, then input).
    The candidate mapper must identify input, rate, and result by role, not position!
    """
    intent = VisualIntent(
        intent_id="intent_01",
        narration_excerpt="Completely arbitrary text.",
        what_viewer_must_understand="Withdrawal math.",
        relationship_type="calculation",
        measurements=[
            # Deliberately reversed order:
            QuantitativeMeasurement(raw_value="₹2 lakh", role="result", metric_name="Annual Cash Flow"),
            QuantitativeMeasurement(raw_value="4%", role="rate", metric_name="Withdrawal Rate"),
            QuantitativeMeasurement(raw_value="₹50 lakh", role="input", metric_name="Retirement Corpus"),
        ],
    )

    candidate = build_candidate_composition_data("calculation_story", intent)

    assert candidate["input_value"] == "₹50 lakh"
    assert candidate["input_label"] == "Retirement Corpus"
    assert candidate["rate_label"] == "4%"
    assert candidate["result_value"] == "₹2 lakh"
    assert candidate["result_label"] == "Annual Cash Flow"
    # Proves operation_label was NOT invented as '×'
    assert "operation_label" not in candidate


def test_calculation_story_preserves_llm_refined_operation_wording() -> None:
    """
    Candidate mapper leaves operation_label un-invented.
    LLM refinement supplies 'compounds to' (e.g. compounding growth, not multiplication).
    The merge must adopt the LLM's operation wording!
    """
    intent = VisualIntent(
        intent_id="intent_01",
        narration_excerpt="₹50,000 becomes ₹1 crore over 15 years.",
        what_viewer_must_understand="Growth from ₹50,000 to ₹1 crore.",
        relationship_type="calculation",
        measurements=[
            QuantitativeMeasurement(raw_value="₹50,000", role="input", metric_name="Initial Investment"),
            QuantitativeMeasurement(raw_value="15% CAGR", role="rate", metric_name="Compounding Rate"),
            QuantitativeMeasurement(raw_value="₹1 crore", role="result", metric_name="Final Corpus"),
        ],
    )

    candidate = build_candidate_composition_data("calculation_story", intent)
    assert "operation_label" not in candidate

    llm_payload = {
        "status": "ok",
        "composition_id": "calculation_story",
        "composition_data": {
            "input_label": "Initial Capital",
            "operation_label": "compounds to",  # NOT '×'!
            "rate_label": "15% annual return",
            "result_label": "Accumulated Wealth",
            "note": "Power of 15 years compounding",
        },
        "visual_goal": "Growth story",
    }

    engine = CompositionPlannerEngine(MockLLMProvider(llm_payload))
    result = engine._run_legacy_llm(intent=intent, beat_id="beat_01")

    assert result.used_fallback is False
    beat_data = result.beat.composition_data
    assert beat_data["input_value"] == "₹50,000"
    assert beat_data["operation_label"] == "compounds to"  # Preserved!
    assert beat_data["result_value"] == "₹1 crore"


# ============================================================================
# 2. TimeDecay Tests (Meaning-Based Baseline vs Result Roles)
# ============================================================================

def test_time_decay_uses_baseline_and_result_roles_not_positions() -> None:
    """
    For: '₹100 falls to ₹26 over 20 years.'
    The intent explicitly marks ₹100 as baseline and ₹26 as result.
    Mapper extracts fixed_amount from baseline and annotation from result, regardless of order.
    """
    intent = VisualIntent(
        intent_id="intent_01",
        narration_excerpt="Random filler text without mentioning numbers.",
        what_viewer_must_understand="Purchasing power erosion.",
        relationship_type="decline",
        measurements=[
            # Result passed BEFORE baseline in the array
            QuantitativeMeasurement(raw_value="₹26", role="result", entity_name="Purchasing Power"),
            QuantitativeMeasurement(raw_value="7%", role="rate", entity_name="Inflation"),
            QuantitativeMeasurement(raw_value="₹100", role="baseline", entity_name="₹100 Note"),
        ],
        temporal=TemporalContext(horizon="20 years", is_decay_over_time=True),
    )

    candidate = build_candidate_composition_data("time_decay", intent)

    assert candidate["fixed_amount"] == "₹100"  # From baseline role!
    assert candidate["amount_label"] == "₹100 Note"
    assert candidate["time_period"] == "20 years"
    assert "₹26" in candidate["annotation"]  # From result role!
    assert candidate["emphasis"] == "purchasing_power_decline"


# ============================================================================
# 3. ComparisonSplit Tests (Structured Comparison & Narration Independence)
# ============================================================================

def test_comparison_split_maps_factual_data_from_comparison_structure() -> None:
    """
    Proves subject names, values, delta, and winner originate from intent.comparison
    even when narration is completely unrelated prose.
    """
    intent = VisualIntent(
        intent_id="intent_01",
        narration_excerpt="Let's examine these two different paths forward.",
        what_viewer_must_understand="Equity outperforms Fixed Deposit.",
        relationship_type="comparison",
        comparison=ComparisonStructure(
            subject_a="Fixed Deposit",
            value_a="6%",
            subject_b="Equity Fund",
            value_b="12%",
            comparison_dimension="Annual Return",
            delta="+6% spread",
            winner="Equity Fund",
        ),
    )

    candidate = build_candidate_composition_data("comparison_split", intent)

    assert candidate["left_role"] == "Fixed Deposit"
    assert candidate["left_value"] == "6%"
    assert candidate["right_role"] == "Equity Fund"
    assert candidate["right_value"] == "12%"
    assert candidate["comparison_label"] == "Annual Return"
    assert candidate["delta"] == "+6% spread"
    assert candidate["winner"] == "right"  # Mapped from 'Equity Fund' matching subject_b


# ============================================================================
# 4. Multi-Factor & Cause-Effect Tests (No Invented Severities)
# ============================================================================

def test_multi_factor_does_not_invent_severity_when_absent() -> None:
    """
    When causal.outcome_severity is None, candidate mapper must NOT guess 'high' or 'critical'.
    """
    intent = VisualIntent(
        intent_id="intent_01",
        narration_excerpt="Several factors converge here.",
        what_viewer_must_understand="Multiple factors acting together.",
        relationship_type="multi_factor",
        causal=CausalStructure(
            causes=["Factor One", "Factor Two"],
            outcome="Combined Pressure",
            outcome_severity=None,  # No severity stated in narration!
        ),
    )

    candidate = build_candidate_composition_data("multi_factor_pressure", intent)

    assert candidate["combined_label"] == "Combined Pressure"
    assert "combined_severity" not in candidate  # NOT invented!
    for f in candidate["factors"]:
        assert "severity" not in f  # NOT invented!


def test_cause_effect_maps_causal_structure() -> None:
    """Proves causes and outcome are mapped directly from causal structure."""
    intent = VisualIntent(
        intent_id="intent_01",
        narration_excerpt="Aggressive fee structure leads to lower corpus.",
        what_viewer_must_understand="Fee impact.",
        relationship_type="cause_effect",
        causal=CausalStructure(
            causes=["1.5% Annual Fee"],
            outcome="30% Corpus Shortfall",
            outcome_severity="high",
        ),
    )

    candidate = build_candidate_composition_data("cause_effect", intent)

    assert candidate["causes"] == [{"label": "1.5% Annual Fee"}]
    assert candidate["outcome_label"] == "30% Corpus Shortfall"
    assert candidate["outcome_severity"] == "negative"
    assert "connector" not in candidate  # Connector left for LLM refinement


# ============================================================================
# 5. Factual Integrity Merge vs LLM Presentation Refinement
# ============================================================================

def test_deterministic_facts_override_llm_hallucinated_numbers() -> None:
    """
    If the LLM generates a hallucinated metric number (e.g. '₹999 lakh'),
    the factual integrity merge restores the verified fact ('₹50 lakh') from candidate.
    """
    intent = VisualIntent(
        intent_id="intent_01",
        narration_excerpt="Imagine you retire with ₹50 lakh.",
        what_viewer_must_understand="₹50 lakh is starting corpus.",
        relationship_type="metric",
        measurements=[
            QuantitativeMeasurement(raw_value="₹50 lakh", role="baseline", metric_name="Starting Portfolio"),
        ],
    )

    candidate = build_candidate_composition_data("metric_hero", intent)
    assert candidate["value"] == "₹50 lakh"

    llm_data_with_drift = {
        "value": "₹999 lakh",  # LLM drifted / hallucinated
        "label": "Climax Portfolio Size",  # Valid presentation label
        "emphasis": "hero",
    }

    merged = merge_factual_and_presentation_data("metric_hero", candidate, llm_data_with_drift, intent)

    assert merged["value"] == "₹50 lakh"  # Factual integrity enforced!
    assert merged["label"] == "Climax Portfolio Size"  # LLM presentation refinement preserved!
    assert merged["emphasis"] == "hero"


def test_llm_presentation_fields_are_preserved() -> None:
    """
    Proves LLM-generated presentation labels (input_label, result_label, note)
    are preserved alongside deterministic facts.
    """
    intent = VisualIntent(
        intent_id="intent_01",
        narration_excerpt="4% withdrawal yields ₹2 lakh.",
        what_viewer_must_understand="4% yields ₹2 lakh.",
        relationship_type="calculation",
        measurements=[
            QuantitativeMeasurement(raw_value="₹50 lakh", role="input"),
            QuantitativeMeasurement(raw_value="4%", role="rate"),
            QuantitativeMeasurement(raw_value="₹2 lakh", role="result"),
        ],
    )

    candidate = build_candidate_composition_data("calculation_story", intent)

    llm_presentation = {
        "input_label": "Nest Egg Corpus",
        "result_label": "Annual Spendable Cash",
        "operation_label": "multiplied by",
        "note": "Standard 4% Safe Withdrawal Rule",
    }

    merged = merge_factual_and_presentation_data("calculation_story", candidate, llm_presentation, intent)

    # Factual values:
    assert merged["input_value"] == "₹50 lakh"
    assert merged["rate_label"] == "4%"
    assert merged["result_value"] == "₹2 lakh"

    # Presentation refinements:
    assert merged["input_label"] == "Nest Egg Corpus"
    assert merged["result_label"] == "Annual Spendable Cash"
    assert merged["operation_label"] == "multiplied by"
    assert merged["note"] == "Standard 4% Safe Withdrawal Rule"


# ============================================================================
# 6. Complete End-to-End Planner Engine Run (Narration Independence)
# ============================================================================

def test_planner_engine_run_with_rich_intent_and_dummy_narration() -> None:
    """
    End-to-end test of CompositionPlannerEngine.run():
    Passes completely unrelated narration text, but rich comparison intent.
    Proves the engine selects comparison_split and populates verified data without re-parsing text.
    """
    intent = VisualIntent(
        intent_id="intent_01",
        narration_excerpt="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        what_viewer_must_understand="Equity outperforms Fixed Deposit by 6%.",
        relationship_type="comparison",
        comparison=ComparisonStructure(
            subject_a="Fixed Deposit",
            value_a="6%",
            subject_b="Equity Fund",
            value_b="12%",
            comparison_dimension="Annual Return",
            delta="+6% spread",
            winner="Equity Fund",
        ),
    )

    llm_payload = {
        "status": "ok",
        "composition_id": "comparison_split",
        "composition_data": {
            "comparison_label": "LONG TERM ANNUAL RETURN",
            "tone": "positive_negative",
        },
        "visual_goal": "Contrast returns",
    }

    engine = CompositionPlannerEngine(MockLLMProvider(llm_payload))
    result = engine._run_legacy_llm(intent=intent, beat_id="beat_01")

    assert result.used_fallback is False
    assert result.beat.composition_id == "comparison_split"
    data = result.beat.composition_data
    assert data["left_role"] == "Fixed Deposit"
    assert data["left_value"] == "6%"
    assert data["right_role"] == "Equity Fund"
    assert data["right_value"] == "12%"
    assert data["delta"] == "+6% spread"
    assert data["winner"] == "right"
    assert data["comparison_label"] == "LONG TERM ANNUAL RETURN"
    assert data["tone"] == "positive_negative"
