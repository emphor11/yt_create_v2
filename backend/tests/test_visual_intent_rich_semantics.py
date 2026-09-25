"""
Tests for Rich VisualIntent Semantic Layer.

Verifies:
1. Semantic entity binding (measurements bound to specific entities).
2. Comparison structure (subject_a vs subject_b, dimensions, deltas, winners).
3. Causal & multi-factor structures.
4. Temporal context and decay dynamics.
5. All 8 trigger-word validation rules.
6. 100% backward compatibility with legacy intent structures.
7. Semantic sub-structures populated ONLY when supported by narration.
"""
import pytest
from pydantic import ValidationError

from domain.visual_intent import (
    VALID_RELATIONSHIP_TYPES,
    CausalStructure,
    ComparisonStructure,
    QuantitativeMeasurement,
    SemanticEntity,
    TemporalContext,
    VisualDynamics,
    VisualIntent,
    VisualIntentSequence,
)
from engines.visual_intent_engine import (
    TRIGGER_WORD_STOPWORDS,
    VisualIntentEngine,
    VisualIntentEngineError,
)
from providers.llm_provider import (
    LLMJsonRequest,
    LLMJsonResponse,
    LLMProviderMetadata,
)


class MockLLMProvider:
    def __init__(self, payload: dict | Exception):
        self.payload = payload
        self.last_request: LLMJsonRequest | None = None

    def generate_json(self, request: LLMJsonRequest) -> LLMJsonResponse:
        self.last_request = request
        if isinstance(self.payload, Exception):
            raise self.payload
        return LLMJsonResponse(
            payload=self.payload,
            metadata=LLMProviderMetadata(provider="mock-llm", model="mock-test"),
        )


# ============================================================================
# 1. Backward Compatibility Tests
# ============================================================================

def test_backward_compatibility_old_intent_instantiation() -> None:
    """Legacy callers creating VisualIntent without any rich fields must work seamlessly."""
    intent = VisualIntent(
        intent_id="intent_01",
        narration_excerpt="Imagine you retire with ₹50 lakh.",
        what_viewer_must_understand="₹50 lakh is the starting retirement portfolio.",
        key_values=["₹50 lakh"],
        relationship_type="metric",
        emphasis="hero",
        trigger_word=None,
    )
    assert intent.intent_id == "intent_01"
    assert intent.entities == []
    assert intent.measurements == []
    assert intent.temporal is None
    assert intent.causal is None
    assert intent.comparison is None
    assert intent.visual_dynamics is None


def test_backward_compatibility_none_lists_normalized() -> None:
    """Passing None for entities or measurements must safely normalize to empty lists."""
    raw = {
        "intent_id": "intent_01",
        "narration_excerpt": "Text",
        "what_viewer_must_understand": "Goal",
        "relationship_type": "statement",
        "entities": None,
        "measurements": None,
        "temporal": None,
        "causal": None,
        "comparison": None,
        "visual_dynamics": None,
    }
    intent = VisualIntent.model_validate(raw)
    assert intent.entities == []
    assert intent.measurements == []
    assert intent.temporal is None


# ============================================================================
# 2. Rich Semantic Sub-Structure Domain Tests
# ============================================================================

def test_rich_intent_simple_metric() -> None:
    """Metric intent with explicit entity, bound measurement, and visual dynamics."""
    intent = VisualIntent(
        intent_id="intent_01",
        narration_excerpt="Imagine you retire with ₹50 lakh. That is your entire starting portfolio.",
        what_viewer_must_understand="₹50 lakh is the starting retirement portfolio.",
        key_values=["₹50 lakh"],
        relationship_type="metric",
        emphasis="hero",
        trigger_word=None,
        entities=[
            SemanticEntity(name="Starting Portfolio", role="subject", category="asset")
        ],
        measurements=[
            QuantitativeMeasurement(
                raw_value="₹50 lakh",
                entity_name="Starting Portfolio",
                metric_name="Corpus Size",
                unit="₹ lakh",
                numeric_value=50.0,
                direction="neutral",
                polarity="neutral",
            )
        ],
        temporal=None,
        causal=None,
        comparison=None,
        visual_dynamics=VisualDynamics(
            focal_point="₹50 lakh starting corpus",
            desired_visual_outcome="Viewer anchors on the total initial nest egg as the baseline",
            motion_intent="counter_increment",
            visual_priority="high",
        ),
    )
    assert len(intent.entities) == 1
    assert intent.entities[0].name == "Starting Portfolio"
    assert len(intent.measurements) == 1
    assert intent.measurements[0].entity_name == "Starting Portfolio"
    assert intent.measurements[0].numeric_value == 50.0
    assert intent.comparison is None
    assert intent.causal is None
    assert intent.temporal is None


def test_rich_intent_comparison_entity_binding() -> None:
    """
    CRITICAL SUCCESS TEST:
    Verifies that in a comparison, values are explicitly bound to specific entities
    (6% -> Fixed Deposit, 12% -> Equity Fund) and comparison structure captures delta and winner.
    """
    intent = VisualIntent(
        intent_id="intent_01",
        narration_excerpt="A Fixed Deposit gives you around 6% return, while an Equity Fund delivers closer to 12%. That 6% difference compounds massively over 15 years.",
        what_viewer_must_understand="Equity Fund return (12%) outperforms Fixed Deposit (6%) by 6% spread over 15 years.",
        key_values=["6%", "12%", "6%", "15 years"],
        relationship_type="comparison",
        emphasis="highlight_spread",
        trigger_word=None,
        entities=[
            SemanticEntity(name="Fixed Deposit", role="baseline", category="investment"),
            SemanticEntity(name="Equity Fund", role="alternative", category="investment"),
        ],
        measurements=[
            QuantitativeMeasurement(
                raw_value="6%",
                entity_name="Fixed Deposit",
                metric_name="Annual Return",
                unit="%",
                numeric_value=6.0,
                direction="flat",
                polarity="neutral",
            ),
            QuantitativeMeasurement(
                raw_value="12%",
                entity_name="Equity Fund",
                metric_name="Annual Return",
                unit="%",
                numeric_value=12.0,
                direction="up",
                polarity="positive",
            ),
        ],
        temporal=TemporalContext(
            horizon="15 years",
            frequency="annual",
            is_decay_over_time=False,
        ),
        causal=None,
        comparison=ComparisonStructure(
            subject_a="Fixed Deposit",
            value_a="6%",
            subject_b="Equity Fund",
            value_b="12%",
            comparison_dimension="Annual Return",
            delta="+6% spread",
            winner="Equity Fund",
        ),
        visual_dynamics=VisualDynamics(
            focal_point="6% return advantage of Equity Fund over Fixed Deposit",
            desired_visual_outcome="Immediate visual contrast showing Equity Fund outperforming Fixed Deposit over 15 years",
            motion_intent="side_by_side_reveal",
            visual_priority="high",
        ),
    )

    # 1. Check entity-to-measurement binding
    fd_measurement = next(m for m in intent.measurements if m.entity_name == "Fixed Deposit")
    equity_measurement = next(m for m in intent.measurements if m.entity_name == "Equity Fund")
    assert fd_measurement.numeric_value == 6.0
    assert equity_measurement.numeric_value == 12.0

    # 2. Check structured comparison
    assert intent.comparison is not None
    assert intent.comparison.subject_a == "Fixed Deposit"
    assert intent.comparison.value_a == "6%"
    assert intent.comparison.subject_b == "Equity Fund"
    assert intent.comparison.value_b == "12%"
    assert intent.comparison.delta == "+6% spread"
    assert intent.comparison.winner == "Equity Fund"

    # 3. Check temporal horizon
    assert intent.temporal is not None
    assert intent.temporal.horizon == "15 years"
    assert intent.causal is None


def test_rich_intent_calculation() -> None:
    """Verifies math story with inputs, withdrawal rate, and result."""
    intent = VisualIntent(
        intent_id="intent_01",
        narration_excerpt="You withdraw 4% every year. On ₹50 lakh, that is ₹2 lakh annually.",
        what_viewer_must_understand="4% of ₹50 lakh equals ₹2 lakh per year.",
        key_values=["4%", "₹50 lakh", "₹2 lakh"],
        relationship_type="calculation",
        emphasis="show_result",
        trigger_word=None,
        entities=[
            SemanticEntity(name="Retirement Portfolio", role="baseline", category="asset"),
            SemanticEntity(name="Annual Withdrawal", role="subject", category="metric"),
        ],
        measurements=[
            QuantitativeMeasurement(
                raw_value="4%",
                entity_name="Annual Withdrawal",
                metric_name="Withdrawal Rate",
                role="rate",
                numeric_value=4.0,
                unit="%",
            ),
            QuantitativeMeasurement(
                raw_value="₹50 lakh",
                entity_name="Retirement Portfolio",
                metric_name="Corpus Base",
                role="input",
                numeric_value=50.0,
                unit="₹ lakh",
            ),
            QuantitativeMeasurement(
                raw_value="₹2 lakh",
                entity_name="Annual Withdrawal",
                metric_name="Annual Cash Flow",
                role="result",
                numeric_value=2.0,
                unit="₹ lakh",
            ),
        ],
        temporal=TemporalContext(horizon="1 year", frequency="yearly", is_decay_over_time=False),
        causal=None,
        comparison=None,
        visual_dynamics=VisualDynamics(
            focal_point="Resulting ₹2 lakh annual income",
            desired_visual_outcome="Clear arithmetic link showing 4% rate yields ₹2 lakh cash flow",
            motion_intent="equation_reveal",
            visual_priority="high",
        ),
    )
    assert len(intent.measurements) == 3
    assert intent.temporal is not None
    assert intent.temporal.frequency == "yearly"
    assert intent.comparison is None
    assert intent.causal is None


def test_rich_intent_multi_factor_causality() -> None:
    """Verifies multi-factor convergence with causes, mechanism, and critical outcome."""
    intent = VisualIntent(
        intent_id="intent_01",
        narration_excerpt="High inflation erodes the value of money. Weak investment returns reduce your corpus growth. Together, these two forces put your retirement at serious risk.",
        what_viewer_must_understand="Inflation and weak returns combine to create severe retirement shortfall risk.",
        key_values=["inflation", "investment returns", "risk"],
        relationship_type="multi_factor",
        emphasis="highlight_risk",
        trigger_word=None,
        entities=[
            SemanticEntity(name="Inflation", role="risk_factor", category="concept"),
            SemanticEntity(name="Weak Returns", role="risk_factor", category="concept"),
            SemanticEntity(name="Retirement Corpus", role="subject", category="asset"),
        ],
        measurements=[],
        temporal=None,
        causal=CausalStructure(
            causes=["High inflation", "Weak investment returns"],
            mechanism="Dual pressure: purchasing power loss combined with stagnant growth",
            outcome="Severe retirement corpus shortfall",
            outcome_severity="critical",
        ),
        comparison=None,
        visual_dynamics=VisualDynamics(
            focal_point="Converging pressure on retirement corpus",
            desired_visual_outcome="Viewer feels the compounding danger of two independent negative forces acting together",
            motion_intent="convergence_inward",
            visual_priority="high",
        ),
    )
    assert intent.causal is not None
    assert len(intent.causal.causes) == 2
    assert intent.causal.outcome_severity == "critical"
    assert intent.comparison is None


def test_rich_intent_decline_time_erosion() -> None:
    """Verifies purchasing power decay over time."""
    intent = VisualIntent(
        intent_id="intent_01",
        narration_excerpt="Over 20 years, 7% annual inflation slashes the purchasing power of your ₹100 note down to just ₹26.",
        what_viewer_must_understand="Purchasing power of ₹100 drops to ₹26 over 20 years due to 7% inflation.",
        key_values=["20 years", "7%", "₹100", "₹26"],
        relationship_type="decline",
        emphasis="show_decline",
        trigger_word=None,
        entities=[
            SemanticEntity(name="₹100 Note", role="subject", category="asset"),
            SemanticEntity(name="Inflation", role="risk_factor", category="concept"),
        ],
        measurements=[
            QuantitativeMeasurement(
                raw_value="₹100",
                entity_name="₹100 Note",
                numeric_value=100.0,
                direction="flat",
                polarity="neutral",
            ),
            QuantitativeMeasurement(
                raw_value="₹26",
                entity_name="₹100 Note",
                numeric_value=26.0,
                direction="down",
                polarity="negative",
            ),
            QuantitativeMeasurement(
                raw_value="7%",
                entity_name="Inflation",
                numeric_value=7.0,
                direction="up",
                polarity="warning",
            ),
        ],
        temporal=TemporalContext(
            horizon="20 years",
            frequency="annual",
            is_decay_over_time=True,
        ),
        causal=CausalStructure(
            causes=["7% annual inflation"],
            mechanism="Compounding purchasing power erosion",
            outcome="74% loss in real monetary value",
            outcome_severity="high",
        ),
        comparison=None,
    )
    assert intent.temporal is not None
    assert intent.temporal.is_decay_over_time is True
    assert intent.temporal.horizon == "20 years"
    down_measurement = [m for m in intent.measurements if m.direction == "down"][0]
    assert down_measurement.raw_value == "₹26"
    assert down_measurement.polarity == "negative"


def test_rich_intent_unicode_currencies_and_normalization() -> None:
    """Verifies parsing of unicode currency symbols (₹, $, €, £) and numeric coercion."""
    m1 = QuantitativeMeasurement(raw_value="₹1,50,000", numeric_value="₹1,50,000", unit="₹")
    assert m1.numeric_value == 150000.0

    m2 = QuantitativeMeasurement(raw_value="$45.50", numeric_value="$45.50", unit="$")
    assert m2.numeric_value == 45.5

    m3 = QuantitativeMeasurement(raw_value="€10M", numeric_value="10", unit="€")
    assert m3.numeric_value == 10.0

    # Direction and polarity normalizations
    m4 = QuantitativeMeasurement(raw_value="5%", direction="increase", polarity="good")
    assert m4.direction == "up"
    assert m4.polarity == "positive"

    m5 = QuantitativeMeasurement(raw_value="2%", direction="falling", polarity="danger")
    assert m5.direction == "down"
    assert m5.polarity == "negative"


# ============================================================================
# 3. Trigger-Word Validation (All 8 Rules)
# ============================================================================

def make_engine_with_payload(payload: dict) -> VisualIntentEngine:
    return VisualIntentEngine(MockLLMProvider(payload))


def test_trigger_word_rule_1_first_intent_must_be_null() -> None:
    """Rule 1: First intent must have trigger_word=null."""
    payload = {
        "idea_id": "idea_01",
        "intents": [
            {
                "intent_id": "intent_01",
                "narration_excerpt": "Starting portfolio of ₹50 lakh.",
                "what_viewer_must_understand": "₹50 lakh portfolio",
                "relationship_type": "metric",
                "trigger_word": "starting",  # INVALID for first intent!
            }
        ],
    }
    engine = make_engine_with_payload(payload)
    with pytest.raises(VisualIntentEngineError, match="first VisualIntent must have trigger_word=null"):
        engine.run(idea_id="idea_01", narration="Starting portfolio of ₹50 lakh.")


def test_trigger_word_rule_2_subsequent_intent_must_have_trigger() -> None:
    """Rule 2: Subsequent intents must have a non-empty trigger_word."""
    payload = {
        "idea_id": "idea_01",
        "intents": [
            {
                "intent_id": "intent_01",
                "narration_excerpt": "Starting portfolio of ₹50 lakh.",
                "what_viewer_must_understand": "₹50 lakh portfolio",
                "relationship_type": "metric",
                "trigger_word": None,
            },
            {
                "intent_id": "intent_02",
                "narration_excerpt": "Next we invest in equity funds.",
                "what_viewer_must_understand": "Equity allocation",
                "relationship_type": "metric",
                "trigger_word": None,  # INVALID: subsequent intent cannot be None
            },
        ],
    }
    engine = make_engine_with_payload(payload)
    with pytest.raises(VisualIntentEngineError, match="must have a non-empty trigger_word"):
        engine.run(idea_id="idea_01", narration="Starting portfolio of ₹50 lakh. Next we invest in equity funds.")


def test_trigger_word_rule_3_verbatim_in_narration_excerpt() -> None:
    """Rule 3: trigger_word must appear verbatim in narration_excerpt."""
    payload = {
        "idea_id": "idea_01",
        "intents": [
            {
                "intent_id": "intent_01",
                "narration_excerpt": "Starting portfolio of ₹50 lakh.",
                "what_viewer_must_understand": "₹50 lakh portfolio",
                "relationship_type": "metric",
                "trigger_word": None,
            },
            {
                "intent_id": "intent_02",
                "narration_excerpt": "Next we invest in equity funds.",
                "what_viewer_must_understand": "Equity allocation",
                "relationship_type": "metric",
                "trigger_word": "bonds",  # 'bonds' not in narration_excerpt
            },
        ],
    }
    engine = make_engine_with_payload(payload)
    with pytest.raises(VisualIntentEngineError, match="does not appear in narration_excerpt"):
        engine.run(idea_id="idea_01", narration="Starting portfolio of ₹50 lakh. Next we invest in equity funds.")


def test_trigger_word_rule_4_verbatim_in_narration() -> None:
    """Rule 4: trigger_word must appear verbatim in full idea narration."""
    payload = {
        "idea_id": "idea_01",
        "intents": [
            {
                "intent_id": "intent_01",
                "narration_excerpt": "Starting portfolio of ₹50 lakh.",
                "what_viewer_must_understand": "₹50 lakh portfolio",
                "relationship_type": "metric",
                "trigger_word": None,
            },
            {
                "intent_id": "intent_02",
                "narration_excerpt": "We allocate to equities.",
                "what_viewer_must_understand": "Equities",
                "relationship_type": "metric",
                "trigger_word": "allocate",
            },
        ],
    }
    engine = make_engine_with_payload(payload)
    # The narration text passed to run() does NOT contain 'allocate'
    with pytest.raises(VisualIntentEngineError, match="does not appear in narration"):
        engine.run(idea_id="idea_01", narration="Starting portfolio of ₹50 lakh. Completely different text here.")


def test_trigger_word_rule_5_no_duplicate_triggers() -> None:
    """Rule 5: No duplicate trigger words in the same idea."""
    payload = {
        "idea_id": "idea_01",
        "intents": [
            {
                "intent_id": "intent_01",
                "narration_excerpt": "Starting portfolio of ₹50 lakh.",
                "what_viewer_must_understand": "₹50 lakh portfolio",
                "relationship_type": "metric",
                "trigger_word": None,
            },
            {
                "intent_id": "intent_02",
                "narration_excerpt": "Growth stocks multiply rapidly.",
                "what_viewer_must_understand": "Stocks multiply",
                "relationship_type": "metric",
                "trigger_word": "rapidly",
            },
            {
                "intent_id": "intent_03",
                "narration_excerpt": "Compounding acts rapidly over time.",
                "what_viewer_must_understand": "Rapid compounding",
                "relationship_type": "metric",
                "trigger_word": "rapidly",  # DUPLICATE!
            },
        ],
    }
    engine = make_engine_with_payload(payload)
    narration = "Starting portfolio of ₹50 lakh. Growth stocks multiply rapidly. Compounding acts rapidly over time."
    with pytest.raises(VisualIntentEngineError, match="Duplicate trigger_word"):
        engine.run(idea_id="idea_01", narration=narration)


def test_trigger_word_rule_6_single_word_no_spaces() -> None:
    """Rule 6: trigger_word must be a single word without spaces."""
    payload = {
        "idea_id": "idea_01",
        "intents": [
            {
                "intent_id": "intent_01",
                "narration_excerpt": "Starting portfolio of ₹50 lakh.",
                "what_viewer_must_understand": "₹50 lakh portfolio",
                "relationship_type": "metric",
                "trigger_word": None,
            },
            {
                "intent_id": "intent_02",
                "narration_excerpt": "Next phase begins immediately.",
                "what_viewer_must_understand": "Next phase",
                "relationship_type": "metric",
                "trigger_word": "Next phase",  # INVALID: multiple words
            },
        ],
    }
    engine = make_engine_with_payload(payload)
    with pytest.raises(VisualIntentEngineError, match="single word without spaces"):
        engine.run(idea_id="idea_01", narration="Starting portfolio of ₹50 lakh. Next phase begins immediately.")


def test_trigger_word_rule_7_no_punctuation_only() -> None:
    """Rule 7: trigger_word must not be punctuation-only."""
    payload = {
        "idea_id": "idea_01",
        "intents": [
            {
                "intent_id": "intent_01",
                "narration_excerpt": "Starting portfolio of ₹50 lakh.",
                "what_viewer_must_understand": "₹50 lakh portfolio",
                "relationship_type": "metric",
                "trigger_word": None,
            },
            {
                "intent_id": "intent_02",
                "narration_excerpt": "Wait... look here.",
                "what_viewer_must_understand": "Look here",
                "relationship_type": "metric",
                "trigger_word": "...",  # INVALID: punctuation only
            },
        ],
    }
    engine = make_engine_with_payload(payload)
    with pytest.raises(VisualIntentEngineError, match="must not be punctuation-only"):
        engine.run(idea_id="idea_01", narration="Starting portfolio of ₹50 lakh. Wait... look here.")


def test_trigger_word_rule_8_no_stopwords() -> None:
    """Rule 8: trigger_word must not be a common English stopword."""
    payload = {
        "idea_id": "idea_01",
        "intents": [
            {
                "intent_id": "intent_01",
                "narration_excerpt": "Starting portfolio of ₹50 lakh.",
                "what_viewer_must_understand": "₹50 lakh portfolio",
                "relationship_type": "metric",
                "trigger_word": None,
            },
            {
                "intent_id": "intent_02",
                "narration_excerpt": "And the returns accelerate.",
                "what_viewer_must_understand": "Accelerating returns",
                "relationship_type": "metric",
                "trigger_word": "the",  # INVALID: stopword
            },
        ],
    }
    engine = make_engine_with_payload(payload)
    with pytest.raises(VisualIntentEngineError, match="cannot be a common stopword"):
        engine.run(idea_id="idea_01", narration="Starting portfolio of ₹50 lakh. And the returns accelerate.")


def test_trigger_word_trailing_punctuation_sanitized_successfully() -> None:
    """Trailing punctuation like 'withdraw.' must be automatically stripped and accepted."""
    payload = {
        "idea_id": "idea_01",
        "intents": [
            {
                "intent_id": "intent_01",
                "narration_excerpt": "Starting portfolio of ₹50 lakh.",
                "what_viewer_must_understand": "₹50 lakh portfolio",
                "key_values": ["₹50 lakh"],
                "relationship_type": "metric",
                "trigger_word": None,
            },
            {
                "intent_id": "intent_02",
                "narration_excerpt": "You withdraw every year.",
                "what_viewer_must_understand": "Withdrawal",
                "relationship_type": "statement",
                "trigger_word": "withdraw.",  # Has trailing period from text
            },
        ],
    }
    engine = make_engine_with_payload(payload)
    result = engine.run(
        idea_id="idea_01",
        narration="Starting portfolio of ₹50 lakh. You withdraw every year.",
    )
    assert result.sequence.intents[1].trigger_word == "withdraw"
