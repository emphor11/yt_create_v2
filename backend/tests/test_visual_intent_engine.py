"""Tests for VisualIntentEngine."""
import pytest

from domain.visual_intent import VALID_RELATIONSHIP_TYPES, VisualIntent, VisualIntentSequence
from engines.visual_intent_engine import VisualIntentEngine, VisualIntentEngineError
from providers.llm_provider import LLMJsonRequest, LLMJsonResponse, LLMProviderMetadata, LLMProviderError


class StaticLLMProvider:
    def __init__(self, payload: dict | Exception):
        self.payload = payload
        self.last_request: LLMJsonRequest | None = None

    def generate_json(self, request: LLMJsonRequest) -> LLMJsonResponse:
        self.last_request = request
        if isinstance(self.payload, Exception):
            raise self.payload
        return LLMJsonResponse(
            payload=self.payload,
            metadata=LLMProviderMetadata(provider="static-test", model="static-test"),
        )


def valid_payload(idea_id: str = "idea_01") -> dict:
    return {
        "idea_id": idea_id,
        "intents": [
            {
                "intent_id": "intent_01",
                "narration_excerpt": "Imagine you retire with ₹50 lakh.",
                "what_viewer_must_understand": "₹50 lakh is the starting retirement portfolio.",
                "key_values": ["₹50 lakh"],
                "relationship_type": "metric",
                "emphasis": "hero",
                "trigger_word": None,
            },
            {
                "intent_id": "intent_02",
                "narration_excerpt": "You withdraw 4% every year, giving you ₹2 lakh.",
                "what_viewer_must_understand": "4% of ₹50 lakh equals ₹2 lakh annually.",
                "key_values": ["4%", "₹50 lakh", "₹2 lakh"],
                "relationship_type": "calculation",
                "emphasis": "show_result",
                "trigger_word": "withdraw",
            },
        ],
    }


# --- Domain model tests ---

def test_visual_intent_rejects_invalid_relationship_type() -> None:
    with pytest.raises(Exception, match="relationship_type"):
        VisualIntent(
            intent_id="intent_01",
            narration_excerpt="Some text",
            what_viewer_must_understand="Something",
            relationship_type="invented_type",
        )


def test_visual_intent_accepts_all_valid_relationship_types() -> None:
    for rt in VALID_RELATIONSHIP_TYPES:
        intent = VisualIntent(
            intent_id="intent_01",
            narration_excerpt="Some text",
            what_viewer_must_understand="Something",
            relationship_type=rt,
        )
        assert intent.relationship_type == rt


def test_visual_intent_defaults() -> None:
    intent = VisualIntent(
        intent_id="intent_01",
        narration_excerpt="Some text",
        what_viewer_must_understand="Something",
        relationship_type="metric",
    )
    assert intent.key_values == []
    assert intent.emphasis is None
    assert intent.trigger_word is None


def test_visual_intent_sequence_allows_empty_intents() -> None:
    seq = VisualIntentSequence(
        idea_id="idea_01",
        narration="Let's explore this.",
        intents=[],
    )
    assert seq.intents == []


# --- Engine tests ---

def test_engine_returns_valid_sequence() -> None:
    provider = StaticLLMProvider(valid_payload())
    engine = VisualIntentEngine(provider)
    result = engine.run(
        idea_id="idea_01",
        narration="Imagine you retire with ₹50 lakh. You withdraw 4% every year.",
        topic="Retirement Planning",
        audience="retail investors",
    )
    assert result.sequence.idea_id == "idea_01"
    assert len(result.sequence.intents) == 2
    assert result.sequence.intents[0].relationship_type == "metric"
    assert result.sequence.intents[1].trigger_word == "withdraw"


def test_engine_overrides_idea_id_from_llm() -> None:
    """LLM might return wrong idea_id — engine must correct it."""
    payload = valid_payload("wrong_id")
    provider = StaticLLMProvider(payload)
    engine = VisualIntentEngine(provider)
    result = engine.run(idea_id="idea_05", narration="Some narration")
    assert result.sequence.idea_id == "idea_05"


def test_engine_rejects_invalid_relationship_type() -> None:
    payload = valid_payload()
    payload["intents"][0]["relationship_type"] = "totally_made_up"
    provider = StaticLLMProvider(payload)
    engine = VisualIntentEngine(provider)
    with pytest.raises(VisualIntentEngineError, match="invalid relationship_type"):
        engine.run(idea_id="idea_01", narration="Some narration")


def test_engine_rejects_non_null_trigger_word_on_first_intent() -> None:
    payload = valid_payload()
    payload["intents"][0]["trigger_word"] = "retire"  # must be null for first
    provider = StaticLLMProvider(payload)
    engine = VisualIntentEngine(provider)
    with pytest.raises(VisualIntentEngineError, match="first VisualIntent"):
        engine.run(idea_id="idea_01", narration="Some narration")


def test_engine_handles_empty_intents() -> None:
    """Filler narration may produce zero intents — valid."""
    payload = {"idea_id": "idea_01", "intents": []}
    provider = StaticLLMProvider(payload)
    engine = VisualIntentEngine(provider)
    result = engine.run(idea_id="idea_01", narration="Let's explore this further.")
    assert result.sequence.intents == []


def test_engine_raises_on_llm_provider_error() -> None:
    provider = StaticLLMProvider(LLMProviderError("LLM unavailable"))
    engine = VisualIntentEngine(provider)
    with pytest.raises(VisualIntentEngineError):
        engine.run(idea_id="idea_01", narration="Some text")


def test_engine_injects_idea_id_into_schema_name() -> None:
    """The LLM request should include schema_name=VisualIntentSequence."""
    provider = StaticLLMProvider(valid_payload())
    engine = VisualIntentEngine(provider)
    engine.run(idea_id="idea_01", narration="Some text about retirement.")
    assert provider.last_request is not None
    assert provider.last_request.schema_name == "VisualIntentSequence"


def test_engine_uses_low_temperature() -> None:
    """Classification task must use low temperature for consistency."""
    provider = StaticLLMProvider(valid_payload())
    engine = VisualIntentEngine(provider)
    engine.run(idea_id="idea_01", narration="Some text.")
    assert provider.last_request is not None
    assert provider.last_request.temperature <= 0.2
