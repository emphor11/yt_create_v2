"""Tests for CompositionPlannerEngine."""
import pytest

from domain.visual_intent import VisualIntent
from engines.composition_planner_engine import CompositionPlannerEngine, CompositionPlannerResult
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


def make_metric_intent(trigger_word: str | None = None) -> VisualIntent:
    return VisualIntent(
        intent_id="intent_01",
        narration_excerpt="Imagine you retire with ₹50 lakh.",
        what_viewer_must_understand="₹50 lakh is the starting retirement portfolio.",
        key_values=["₹50 lakh"],
        relationship_type="metric",
        emphasis="hero",
        trigger_word=trigger_word,
    )


def make_statement_intent() -> VisualIntent:
    return VisualIntent(
        intent_id="intent_02",
        narration_excerpt="That sounds safe at first.",
        what_viewer_must_understand="The rule initially appears safe.",
        key_values=[],
        relationship_type="statement",
        trigger_word="sounds",
    )


def valid_metric_hero_response() -> dict:
    return {
        "status": "ok",
        "composition_id": "metric_hero",
        "variant": "hero",
        "composition_data": {
            "value": "₹50 lakh",
            "label": "Starting Retirement Portfolio",
        },
        "asset_requirement": "none",
        "asset_query": None,
        "trigger_word": None,
        "visual_goal": "Show ₹50 lakh as the hero opening metric.",
    }


# --- Happy path ---

def test_planner_returns_valid_beat_for_metric_intent() -> None:
    provider = StaticLLMProvider(valid_metric_hero_response())
    engine = CompositionPlannerEngine(provider)
    result = engine.run(intent=make_metric_intent(), beat_id="beat_01")
    assert result.used_fallback is False
    assert result.beat.composition_id == "metric_hero"
    assert result.beat.beat_id == "beat_01"
    assert result.beat.composition_data["value"] == "₹50 lakh"
    assert result.beat.trigger_word is None


def test_planner_preserves_trigger_word_from_llm_response() -> None:
    response = valid_metric_hero_response()
    response["trigger_word"] = "retire"
    provider = StaticLLMProvider(response)
    engine = CompositionPlannerEngine(provider)
    result = engine.run(intent=make_metric_intent(trigger_word="retire"), beat_id="beat_02")
    assert result.beat.trigger_word == "retire"


def test_planner_preserves_visual_goal() -> None:
    provider = StaticLLMProvider(valid_metric_hero_response())
    engine = CompositionPlannerEngine(provider)
    result = engine.run(intent=make_metric_intent(), beat_id="beat_01")
    assert "₹50 lakh" in result.beat.visual_goal or "metric" in result.beat.visual_goal.lower()


# --- Fallback triggers ---

def test_planner_returns_fallback_on_no_suitable_composition() -> None:
    response = {"status": "no_suitable_composition", "reason": "No infographic fits this."}
    provider = StaticLLMProvider(response)
    engine = CompositionPlannerEngine(provider)
    result = engine.run(intent=make_statement_intent(), beat_id="beat_03")
    assert result.used_fallback is True
    assert result.beat.composition_id == "broll_caption"
    assert result.beat.beat_id == "beat_03"


def test_planner_returns_fallback_on_unknown_composition_id() -> None:
    response = {
        "status": "ok",
        "composition_id": "invented_composition_xyz",
        "composition_data": {"value": "₹50 lakh"},
        "visual_goal": "Some goal",
    }
    provider = StaticLLMProvider(response)
    engine = CompositionPlannerEngine(provider)
    result = engine.run(intent=make_metric_intent(), beat_id="beat_04")
    assert result.used_fallback is True
    assert result.beat.composition_id == "broll_caption"


def test_planner_returns_fallback_on_missing_required_composition_data() -> None:
    response = {
        "status": "ok",
        "composition_id": "metric_hero",
        "composition_data": {"value": "₹50 lakh"},  # missing required "label"
        "visual_goal": "Some goal",
    }
    provider = StaticLLMProvider(response)
    engine = CompositionPlannerEngine(provider)
    result = engine.run(intent=make_metric_intent(), beat_id="beat_05")
    assert result.used_fallback is True
    assert result.beat.composition_id == "broll_caption"


def test_planner_returns_fallback_on_llm_provider_error() -> None:
    provider = StaticLLMProvider(LLMProviderError("LLM unreachable"))
    engine = CompositionPlannerEngine(provider)
    result = engine.run(intent=make_metric_intent(), beat_id="beat_06")
    assert result.used_fallback is True
    assert result.beat.composition_id == "broll_caption"


def test_planner_fallback_uses_intent_data_for_caption() -> None:
    response = {"status": "no_suitable_composition", "reason": "Nothing fits."}
    provider = StaticLLMProvider(response)
    engine = CompositionPlannerEngine(provider)
    intent = make_statement_intent()
    result = engine.run(intent=intent, beat_id="beat_07")
    assert result.beat.composition_data["caption"] == intent.what_viewer_must_understand


# --- Invalid variant handling ---

def test_planner_drops_invalid_variant_silently() -> None:
    response = valid_metric_hero_response()
    response["variant"] = "nonexistent_variant"
    provider = StaticLLMProvider(response)
    engine = CompositionPlannerEngine(provider)
    result = engine.run(intent=make_metric_intent(), beat_id="beat_08")
    # Should still succeed (not fallback), but variant should be null
    assert result.used_fallback is False
    assert result.beat.variant is None


def test_planner_accepts_valid_variant() -> None:
    response = valid_metric_hero_response()
    response["variant"] = "supporting"  # valid for metric_hero
    provider = StaticLLMProvider(response)
    engine = CompositionPlannerEngine(provider)
    result = engine.run(intent=make_metric_intent(), beat_id="beat_09")
    assert result.used_fallback is False
    assert result.beat.variant == "supporting"


# --- LLM request properties ---

def test_planner_uses_low_temperature() -> None:
    provider = StaticLLMProvider(valid_metric_hero_response())
    engine = CompositionPlannerEngine(provider)
    engine.run(intent=make_metric_intent(), beat_id="beat_01")
    assert provider.last_request is not None
    assert provider.last_request.temperature <= 0.2


def test_planner_schema_contains_all_registered_ids() -> None:
    from registries.composition_registry import CompositionRegistry
    provider = StaticLLMProvider(valid_metric_hero_response())
    engine = CompositionPlannerEngine(provider)
    engine.run(intent=make_metric_intent(), beat_id="beat_01")
    assert provider.last_request is not None
    schema = provider.last_request.response_schema
    found_ids = set()
    for branch in schema["anyOf"]:
        if branch.get("properties", {}).get("status", {}).get("enum") == ["ok"]:
            found_ids.update(branch["properties"]["composition_id"]["enum"])
    for cid in CompositionRegistry.all_ids():
        assert cid in found_ids


def test_planner_prompt_contains_catalog() -> None:
    provider = StaticLLMProvider(valid_metric_hero_response())
    engine = CompositionPlannerEngine(provider)
    engine.run(intent=make_metric_intent(), beat_id="beat_01", topic="Retirement")
    assert provider.last_request is not None
    system_msg = provider.last_request.messages[0].content
    assert "metric_hero" in system_msg
    assert "calculation_story" in system_msg


# --- Targeted composition data population tests ---

def test_planner_returns_valid_beat_for_calculation_story() -> None:
    response = {
        "status": "ok",
        "composition_id": "calculation_story",
        "variant": None,
        "composition_data": {
            "input_label": "Portfolio",
            "input_value": "₹50 lakh",
            "operation_label": "×",
            "rate_label": "4% withdrawal rate",
            "result_label": "Annual Income",
            "result_value": "₹2 lakh",
            "note": "Safe Withdrawal Rate",
        },
        "asset_requirement": "none",
        "asset_query": None,
        "trigger_word": "withdrawal",
        "visual_goal": "Show 4% of ₹50 lakh equals ₹2 lakh.",
    }
    provider = StaticLLMProvider(response)
    engine = CompositionPlannerEngine(provider)
    intent = VisualIntent(
        intent_id="intent_calc",
        narration_excerpt="A four percent withdrawal on fifty lakh gives two lakh a year.",
        what_viewer_must_understand="4% of 50L is 2L annually.",
        key_values=["₹50 lakh", "4%", "₹2 lakh"],
        relationship_type="calculation",
        trigger_word="withdrawal",
    )
    result = engine.run(intent=intent, beat_id="beat_calc_01")
    assert result.used_fallback is False
    assert result.beat.composition_id == "calculation_story"
    assert result.beat.composition_data["input_label"] == "Portfolio"
    assert result.beat.composition_data["input_value"] == "₹50 lakh"
    assert result.beat.composition_data["operation_label"] == "×"
    assert result.beat.composition_data["rate_label"] == "4% withdrawal rate"
    assert result.beat.composition_data["result_label"] == "Annual Income"
    assert result.beat.composition_data["result_value"] == "₹2 lakh"
    assert result.beat.composition_data["note"] == "Safe Withdrawal Rate"


def test_planner_rejects_missing_calculation_story_required_fields_and_falls_back() -> None:
    response = {
        "status": "ok",
        "composition_id": "calculation_story",
        "composition_data": {
            "input_label": "Portfolio",
            "input_value": "₹50 lakh",
            # Missing operation_label, rate_label, result_label, result_value
        },
        "visual_goal": "Calculate income",
    }
    provider = StaticLLMProvider(response)
    engine = CompositionPlannerEngine(provider)
    intent = VisualIntent(
        intent_id="intent_calc_err",
        narration_excerpt="A four percent withdrawal.",
        what_viewer_must_understand="Calculate 4%",
        key_values=["4%"],
        relationship_type="calculation",
    )
    result = engine.run(intent=intent, beat_id="beat_calc_err")
    assert result.used_fallback is True
    assert result.beat.composition_id == "broll_caption"


def test_planner_returns_valid_beat_for_broll_caption() -> None:
    response = {
        "status": "ok",
        "composition_id": "broll_caption",
        "variant": None,
        "composition_data": {
            "caption": "The journey is not as simple as it looks.",
            "emphasis_phrase": "not as simple",
            "author": None,
        },
        "asset_requirement": "optional_broll",
        "asset_query": "winding mountain road",
        "trigger_word": "journey",
        "visual_goal": "Show a difficult path representing the journey.",
    }
    provider = StaticLLMProvider(response)
    engine = CompositionPlannerEngine(provider)
    intent = make_statement_intent()
    result = engine.run(intent=intent, beat_id="beat_broll_01")
    assert result.used_fallback is False
    assert result.beat.composition_id == "broll_caption"
    assert result.beat.composition_data["caption"] == "The journey is not as simple as it looks."
    assert result.beat.composition_data["emphasis_phrase"] == "not as simple"
    assert result.beat.asset_requirement == "optional_broll"
    assert result.beat.asset_query == "winding mountain road"
