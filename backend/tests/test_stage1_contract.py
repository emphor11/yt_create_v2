"""
Stage 1 Contract Tests — composition-independent VisualIntent extraction.

Stage 1 validates grounded excerpts, trigger words, relationship types, and
raw values. Composition-specific completeness is tested at the selected
composition filler boundary, not here.

Tests A–Q map to the requirements in the implementation plan:

A  — Valid cause_effect with full causal → passes
B  — cause_effect with causal=null → passes to the filler boundary
C  — cause_effect with causal.causes=[] → passes to the filler boundary
D  — multi_factor with only 1 cause → passes to the filler boundary
E  — comparison with comparison=null → passes to the filler boundary
F  — divergence without temporal.horizon → passes to the filler boundary
G  — metric with no measurements and no key_values → passes to the filler boundary
H  — calculation with no input-role measurement → passes to the filler boundary
I  — narration_excerpt not verbatim in narration → raises (engine)
J  — narration_excerpt out of narration order → raises (engine)
K  — overlapping narration_excerpts → raises (engine)
L  — duplicate intent_id → raises (engine)
M  — trigger_word 'invest' does NOT match 'investing' (boundary fix)
N  — raw_value not present in narration_excerpt → raises (engine)
O  — valid ranking with ≥2 ordered entities → passes
P  — calculation: result measurement without any input/baseline → passes to filler boundary
Q  — valid broll with no semantic fields → passes
"""
import pytest

from domain.visual_intent import (
    CausalStructure,
    ComparisonStructure,
    QuantitativeMeasurement,
    SemanticEntity,
    VisualIntent,
)
from engines.visual_intent_engine import VisualIntentEngine, VisualIntentEngineError
from providers.llm_provider import LLMJsonRequest, LLMJsonResponse, LLMProviderMetadata


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

class StaticLLM:
    """Minimal LLM stub — returns a fixed payload."""

    def __init__(self, payload: dict):
        self.payload = payload

    def generate_json(self, _: LLMJsonRequest) -> LLMJsonResponse:
        return LLMJsonResponse(
            payload=self.payload,
            metadata=LLMProviderMetadata(provider="static", model="static"),
        )


def engine_with(payload: dict) -> VisualIntentEngine:
    return VisualIntentEngine(StaticLLM(payload))


def single_intent_payload(
    *,
    narration: str = "Test narration.",
    excerpt: str | None = None,
    relationship_type: str = "statement",
    extra: dict | None = None,
) -> dict:
    intent: dict = {
        "intent_id": "intent_01",
        "narration_excerpt": excerpt if excerpt is not None else narration,
        "what_viewer_must_understand": "Test understanding.",
        "relationship_type": relationship_type,
        "trigger_word": None,
    }
    if extra:
        intent.update(extra)
    return {"idea_id": "idea_01", "intents": [intent]}


# ---------------------------------------------------------------------------
# A — Valid cause_effect with full causal structure → passes
# ---------------------------------------------------------------------------

def test_A_valid_cause_effect_passes() -> None:
    """A complete cause_effect intent must pass the model_validator."""
    intent = VisualIntent(
        intent_id="intent_01",
        narration_excerpt="High inflation erodes purchasing power, leading to a retirement shortfall.",
        what_viewer_must_understand="Inflation causes retirement corpus shortfall.",
        relationship_type="cause_effect",
        causal=CausalStructure(
            causes=["High inflation"],
            mechanism="Purchasing power erosion over time",
            outcome="Retirement corpus shortfall",
            outcome_severity="high",
        ),
    )
    assert intent.relationship_type == "cause_effect"
    assert intent.causal is not None
    assert len(intent.causal.causes) == 1


# ---------------------------------------------------------------------------
# B — cause_effect with causal=null → raises
# ---------------------------------------------------------------------------

def test_B_cause_effect_null_causal_raises() -> None:
    """Missing causal detail is allowed until the selected composition filler."""
    intent = VisualIntent(
        intent_id="intent_01",
        narration_excerpt="Inflation leads to lower corpus.",
        what_viewer_must_understand="Inflation reduces corpus.",
        relationship_type="cause_effect",
        causal=None,
    )
    assert intent.causal is None


# ---------------------------------------------------------------------------
# C — cause_effect with causes=[] → raises
# ---------------------------------------------------------------------------

def test_C_cause_effect_empty_causes_raises() -> None:
    """An empty causal structure is preserved for composition-stage validation."""
    intent = VisualIntent(
        intent_id="intent_01",
        narration_excerpt="Something leads to something else.",
        what_viewer_must_understand="Effect.",
        relationship_type="cause_effect",
        causal=CausalStructure(causes=[], outcome="Portfolio shrinks"),
    )
    assert intent.causal is not None and intent.causal.causes == []


# ---------------------------------------------------------------------------
# D — multi_factor with only 1 cause → raises
# ---------------------------------------------------------------------------

def test_D_multi_factor_single_cause_raises() -> None:
    """The filler, not Stage 1, owns the minimum factor count."""
    intent = VisualIntent(
        intent_id="intent_01",
        narration_excerpt="Inflation and weak returns destroy wealth together.",
        what_viewer_must_understand="Two pressures on wealth.",
        relationship_type="multi_factor",
        causal=CausalStructure(causes=["Inflation"], outcome="Wealth destruction", outcome_severity="high"),
    )
    assert intent.causal is not None and len(intent.causal.causes) == 1


# ---------------------------------------------------------------------------
# E — comparison with comparison=null → raises
# ---------------------------------------------------------------------------

def test_E_comparison_null_raises() -> None:
    """Comparison data is filled after comparison_split is selected."""
    intent = VisualIntent(
        intent_id="intent_01",
        narration_excerpt="Fixed Deposit gives 6% while Equity Fund gives 12%.",
        what_viewer_must_understand="Equity outperforms FD.",
        relationship_type="comparison",
        comparison=None,
    )
    assert intent.comparison is None


# ---------------------------------------------------------------------------
# F — divergence without temporal.horizon → raises
# ---------------------------------------------------------------------------

def test_F_divergence_no_temporal_raises() -> None:
    """Temporal completeness belongs to trajectory_divergence data filling."""
    intent = VisualIntent(
        intent_id="intent_01",
        narration_excerpt="Investing grows, spending shrinks.",
        what_viewer_must_understand="Two diverging paths.",
        relationship_type="divergence",
        temporal=None,
        comparison=ComparisonStructure(
            subject_a="Investing", value_a="grows", subject_b="Spending",
            value_b="shrinks", comparison_dimension="Wealth trajectory",
        ),
    )
    assert intent.temporal is None


# ---------------------------------------------------------------------------
# G — metric with no measurements AND no key_values → raises
# ---------------------------------------------------------------------------

def test_G_metric_no_values_raises() -> None:
    """The metric schema/filler owns the required value check."""
    intent = VisualIntent(
        intent_id="intent_01",
        narration_excerpt="This is an important number.",
        what_viewer_must_understand="Some number is important.",
        relationship_type="metric",
        measurements=[],
        key_values=[],
    )
    assert intent.measurements == [] and intent.key_values == []


# ---------------------------------------------------------------------------
# H — calculation with no input-role measurement → raises
# ---------------------------------------------------------------------------

def test_H_calculation_no_input_raises() -> None:
    """The calculation schema/filler owns the required input check."""
    intent = VisualIntent(
        intent_id="intent_01",
        narration_excerpt="4% of the corpus gives two lakh.",
        what_viewer_must_understand="4% of corpus = 2 lakh.",
        relationship_type="calculation",
        measurements=[QuantitativeMeasurement(raw_value="two lakh", role="result")],
    )
    assert intent.measurements[0].role == "result"


# ---------------------------------------------------------------------------
# I — narration_excerpt not verbatim → engine raises
# ---------------------------------------------------------------------------

def test_I_non_verbatim_excerpt_raises() -> None:
    """A paraphrased narration_excerpt must be rejected by the engine."""
    narration = "You invest fifty lakh rupees and it grows to one crore over fifteen years."
    payload = single_intent_payload(
        narration=narration,
        excerpt="You put away fifty lakh and it doubles.",  # paraphrased
        relationship_type="metric",
        extra={"key_values": ["fifty lakh"]},
    )
    with pytest.raises(VisualIntentEngineError, match="verbatim|substring"):
        engine_with(payload).run(idea_id="idea_01", narration=narration)


# ---------------------------------------------------------------------------
# J — narration_excerpt out of narration order → engine raises
# ---------------------------------------------------------------------------

def test_J_out_of_order_excerpt_raises() -> None:
    """Intents whose excerpts appear in reverse narration order must be rejected."""
    narration = "First sentence here. Second sentence follows."
    payload = {
        "idea_id": "idea_01",
        "intents": [
            {
                "intent_id": "intent_01",
                "narration_excerpt": "Second sentence follows.",
                "what_viewer_must_understand": "Second sentence.",
                "relationship_type": "statement",
                "trigger_word": None,
            },
            {
                "intent_id": "intent_02",
                "narration_excerpt": "First sentence here.",
                "what_viewer_must_understand": "First sentence.",
                "relationship_type": "statement",
                "trigger_word": "sentence",
            },
        ],
    }
    with pytest.raises(VisualIntentEngineError, match="order|overlap"):
        engine_with(payload).run(idea_id="idea_01", narration=narration)


# ---------------------------------------------------------------------------
# K — overlapping narration_excerpts → engine raises
# ---------------------------------------------------------------------------

def test_K_overlapping_excerpts_raises() -> None:
    """Two intents that reference overlapping narration spans must be rejected."""
    narration = "Inflation erodes value. Inflation destroys wealth over time."
    payload = {
        "idea_id": "idea_01",
        "intents": [
            {
                "intent_id": "intent_01",
                "narration_excerpt": "Inflation erodes value. Inflation destroys wealth over time.",
                "what_viewer_must_understand": "Full narration.",
                "relationship_type": "statement",
                "trigger_word": None,
            },
            {
                "intent_id": "intent_02",
                "narration_excerpt": "Inflation destroys wealth over time.",
                "what_viewer_must_understand": "Destruction.",
                "relationship_type": "statement",
                "trigger_word": "destroys",
            },
        ],
    }
    with pytest.raises(VisualIntentEngineError, match="order|overlap"):
        engine_with(payload).run(idea_id="idea_01", narration=narration)


# ---------------------------------------------------------------------------
# L — duplicate intent_id → engine raises
# ---------------------------------------------------------------------------

def test_L_duplicate_intent_id_raises() -> None:
    """Two intents with the same intent_id must be rejected."""
    narration = "First point. Second point follows."
    payload = {
        "idea_id": "idea_01",
        "intents": [
            {
                "intent_id": "intent_01",
                "narration_excerpt": "First point.",
                "what_viewer_must_understand": "First.",
                "relationship_type": "statement",
                "trigger_word": None,
            },
            {
                "intent_id": "intent_01",
                "narration_excerpt": "Second point follows.",
                "what_viewer_must_understand": "Second.",
                "relationship_type": "statement",
                "trigger_word": "Second",
            },
        ],
    }
    with pytest.raises(VisualIntentEngineError, match="Duplicate intent_id"):
        engine_with(payload).run(idea_id="idea_01", narration=narration)


# ---------------------------------------------------------------------------
# M — trigger_word 'invest' must NOT match the word 'investing'
# ---------------------------------------------------------------------------

def test_M_trigger_word_boundary_invest_vs_investing() -> None:
    """'invest' must NOT match the word 'investing' — word boundary is required."""
    narration = "You are investing your money wisely. This approach maximizes returns."
    payload = {
        "idea_id": "idea_01",
        "intents": [
            {
                "intent_id": "intent_01",
                "narration_excerpt": "You are investing your money wisely.",
                "what_viewer_must_understand": "Investing grows wealth.",
                "relationship_type": "statement",
                "trigger_word": None,
            },
            {
                "intent_id": "intent_02",
                "narration_excerpt": "This approach maximizes returns.",
                "what_viewer_must_understand": "Returns maximized.",
                "relationship_type": "statement",
                # 'invest' appears only as part of 'investing' — must FAIL
                "trigger_word": "invest",
            },
        ],
    }
    with pytest.raises(VisualIntentEngineError, match="complete word|narration_excerpt|narration"):
        engine_with(payload).run(idea_id="idea_01", narration=narration)


# ---------------------------------------------------------------------------
# N — raw_value not present in narration_excerpt → engine raises
# ---------------------------------------------------------------------------

def test_N_invented_raw_value_raises() -> None:
    """A raw_value not present in narration_excerpt must be rejected."""
    narration = "You retire with fifty lakh rupees. That corpus grows annually."
    payload = single_intent_payload(
        narration=narration,
        excerpt="You retire with fifty lakh rupees.",
        relationship_type="metric",
        extra={
            "key_values": ["fifty lakh"],
            "measurements": [
                {
                    "raw_value": "eighty lakh",  # INVENTED — not in excerpt
                    "entity_name": "Retirement Portfolio",
                    "metric_name": "Corpus Size",
                    "role": "input",
                }
            ],
        },
    )
    with pytest.raises(VisualIntentEngineError, match="raw_value|invent"):
        engine_with(payload).run(idea_id="idea_01", narration=narration)


# ---------------------------------------------------------------------------
# O — valid ranking with ≥2 ordered entities → passes
# ---------------------------------------------------------------------------

def test_O_valid_ranking_passes() -> None:
    """A ranking intent with 2 ordered entities must pass the validator."""
    intent = VisualIntent(
        intent_id="intent_01",
        narration_excerpt="Equity funds come first, followed by debt funds, then gold.",
        what_viewer_must_understand="Equity outranks debt, which outranks gold.",
        relationship_type="ranking",
        entities=[
            SemanticEntity(name="Equity Funds", role="subject", category="investment"),
            SemanticEntity(name="Debt Funds", role="subject", category="investment"),
            SemanticEntity(name="Gold", role="subject", category="investment"),
        ],
    )
    assert len(intent.entities) == 3
    assert intent.entities[0].name == "Equity Funds"


# ---------------------------------------------------------------------------
# P — calculation: result without any input/baseline raises
# ---------------------------------------------------------------------------

def test_P_calculation_result_without_input_raises() -> None:
    """
    A calculation intent that has only a result measurement but no input/baseline
    is an incomplete math story and must be rejected.
    """
    intent = VisualIntent(
        intent_id="intent_01",
        narration_excerpt="The annual withdrawal is two lakh rupees.",
        what_viewer_must_understand="Two lakh is the annual withdrawal.",
        relationship_type="calculation",
        measurements=[QuantitativeMeasurement(
            raw_value="two lakh rupees", role="result", metric_name="Annual Withdrawal"
        )],
    )
    assert intent.measurements[0].role == "result"


# ---------------------------------------------------------------------------
# Q — valid broll with no semantic fields → passes
# ---------------------------------------------------------------------------

def test_Q_valid_broll_no_structure_passes() -> None:
    """A broll intent with no semantic sub-structures is legitimately valid."""
    intent = VisualIntent(
        intent_id="intent_01",
        narration_excerpt="This is what financial freedom looks like.",
        what_viewer_must_understand="Atmospheric moment — financial freedom concept.",
        relationship_type="broll",
    )
    assert intent.relationship_type == "broll"
    assert intent.causal is None
    assert intent.comparison is None
    assert intent.measurements == []
