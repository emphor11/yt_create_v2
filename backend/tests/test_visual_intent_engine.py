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
    result = engine.run(
        idea_id="idea_05",
        narration="Imagine you retire with ₹50 lakh. You withdraw 4% every year.",
    )
    assert result.sequence.idea_id == "idea_05"


def test_engine_rejects_invalid_relationship_type() -> None:
    payload = valid_payload()
    payload["intents"][0]["relationship_type"] = "totally_made_up"
    provider = StaticLLMProvider(payload)
    engine = VisualIntentEngine(provider)
    with pytest.raises(VisualIntentEngineError, match="invalid relationship_type"):
        engine.run(
            idea_id="idea_01",
            narration="Imagine you retire with ₹50 lakh. You withdraw 4% every year.",
        )


def test_engine_rejects_non_null_trigger_word_on_first_intent() -> None:
    payload = valid_payload()
    payload["intents"][0]["trigger_word"] = "retire"  # must be null for first
    provider = StaticLLMProvider(payload)
    engine = VisualIntentEngine(provider)
    with pytest.raises(VisualIntentEngineError, match="first VisualIntent"):
        engine.run(
            idea_id="idea_01",
            narration="Imagine you retire with ₹50 lakh. You withdraw 4% every year.",
        )


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
    engine.run(
        idea_id="idea_01",
        narration="Imagine you retire with ₹50 lakh. You withdraw 4% every year.",
    )
    assert provider.last_request is not None
    assert provider.last_request.schema_name == "VisualIntentSequence"


def test_engine_uses_low_temperature() -> None:
    """Classification task must use low temperature for consistency."""
    provider = StaticLLMProvider(valid_payload())
    engine = VisualIntentEngine(provider)
    engine.run(
        idea_id="idea_01",
        narration="Imagine you retire with ₹50 lakh. You withdraw 4% every year.",
    )
    assert provider.last_request is not None
    assert provider.last_request.temperature <= 0.2


# --- Pacing Budget & Progressive Storytelling Tests ---

from engines.visual_intent_engine import calculate_pacing_budget
from app.assets import load_prompt


def test_calculate_pacing_budget_all_lengths() -> None:
    """Tests pacing budget calculation across standard narration lengths."""
    # 1. Very short: ~15 words
    n15 = " ".join(["word"] * 15)
    b15 = calculate_pacing_budget(n15)
    assert b15["word_count"] == 15
    assert b15["estimated_seconds"] == 5.6
    assert b15["target_beats_min"] == 2
    assert b15["target_beats_max"] == 3

    # 2. Short: ~30 words
    n30 = " ".join(["word"] * 30)
    b30 = calculate_pacing_budget(n30)
    assert b30["word_count"] == 30
    assert b30["estimated_seconds"] == 11.1
    assert b30["target_beats_min"] == 2
    assert b30["target_beats_max"] == 3

    # 3. Medium: ~50 words
    n50 = " ".join(["word"] * 50)
    b50 = calculate_pacing_budget(n50)
    assert b50["word_count"] == 50
    assert b50["estimated_seconds"] == 18.5
    assert b50["target_beats_min"] == 3
    assert b50["target_beats_max"] == 4

    # 4. Long: ~75 words
    n75 = " ".join(["word"] * 75)
    b75 = calculate_pacing_budget(n75)
    assert b75["word_count"] == 75
    assert b75["estimated_seconds"] == 27.8
    assert b75["target_beats_min"] == 4
    assert b75["target_beats_max"] == 6

    # 5. Very long: ~100 words
    n100 = " ".join(["word"] * 100)
    b100 = calculate_pacing_budget(n100)
    assert b100["word_count"] == 100
    assert b100["estimated_seconds"] == 37.0
    assert b100["target_beats_min"] == 5
    assert b100["target_beats_max"] == 8

    # 6. Extra long: ~150 words
    n150 = " ".join(["word"] * 150)
    b150 = calculate_pacing_budget(n150)
    assert b150["word_count"] == 150
    assert b150["estimated_seconds"] == 55.6
    assert b150["target_beats_min"] == 7
    assert b150["target_beats_max"] == 11


def test_engine_injects_pacing_budget_for_body_idea() -> None:
    """Verifies that non-hook ideas receive PACING BUDGET in the user prompt."""
    provider = StaticLLMProvider(valid_payload())
    engine = VisualIntentEngine(provider)
    narration_75 = "Imagine you retire with fifty lakh rupees and you withdraw four percent every year. " + " ".join(["word"] * 60)
    words = len(narration_75.split())

    result = engine.run(
        idea_id="idea_03",
        narration=narration_75,
        topic="Wealth Building",
        audience="corporate employees",
        is_hook=False,
    )

    assert provider.last_request is not None
    prompt_text = provider.last_request.messages[1].content
    assert "PACING BUDGET:" in prompt_text
    assert f"Narration length: {words} words" in prompt_text
    assert "Suggested visual intent range:" in prompt_text
    assert "Use this range as a pacing guide" in prompt_text
    assert "HOOK-SPECIFIC CONSTRAINTS" not in prompt_text
    assert result.pacing_diagnostic is not None
    assert result.pacing_diagnostic["word_count"] == words


def test_engine_preserves_hook_specific_constraints() -> None:
    """Verifies that hook mode receives HOOK-SPECIFIC CONSTRAINTS and NOT body pacing budget."""
    provider = StaticLLMProvider(valid_payload("hook"))
    engine = VisualIntentEngine(provider)
    hook_narration = "Imagine you retire with fifty lakh rupees and you withdraw four percent every year."

    result = engine.run(
        idea_id="hook",
        narration=hook_narration,
        topic="Rent vs Buy",
        audience="corporate employees",
        is_hook=True,
    )

    assert provider.last_request is not None
    prompt_text = provider.last_request.messages[1].content
    assert "HOOK-SPECIFIC CONSTRAINTS:" in prompt_text
    assert "Generate exactly 2 to 3 punchy, high-retention visual intents" in prompt_text
    assert "PACING BUDGET:" not in prompt_text
    assert result.pacing_diagnostic is None


def test_engine_pacing_diagnostic_detects_underproduction() -> None:
    """Verifies pacing_diagnostic flags below_min when generated beats are below target_beats_min."""
    # 75 words expects min 4 beats, but payload only has 2
    provider = StaticLLMProvider(valid_payload())
    engine = VisualIntentEngine(provider)
    narration_75 = "Imagine you retire with fifty lakh and you withdraw four percent. " + " ".join(["word"] * 64)

    result = engine.run(
        idea_id="idea_01",
        narration=narration_75,
    )

    assert result.pacing_diagnostic is not None
    assert result.pacing_diagnostic["target_beats_min"] == 4
    assert result.pacing_diagnostic["generated_beats"] == 2
    assert result.pacing_diagnostic["below_min"] is True


def test_system_prompt_contains_progressive_visual_storytelling() -> None:
    """Verifies system prompt asset contains Progressive Visual Storytelling rule."""
    content = load_prompt("visual_intent_system.txt")
    assert "PROGRESSIVE VISUAL STORYTELLING" in content
    assert "The number of intents must be determined by **semantic progression**" in content
    assert "RULE 1 — GROUP RELATED SENTENCES" not in content


