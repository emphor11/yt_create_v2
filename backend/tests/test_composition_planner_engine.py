"""Tests for CompositionPlannerEngine."""
import pytest
from pydantic import ValidationError

from domain.visual_intent import VisualIntent, SemanticEntity, QuantitativeMeasurement
from engines.composition_planner_engine import CompositionPlannerEngine, CompositionPlannerResult, CompositionPlannerEngineError
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
        measurements=[
            QuantitativeMeasurement(raw_value="₹50 lakh", metric_name="Starting Retirement Portfolio", role="input")
        ],
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

def test_planner_fallback_uses_intent_data_for_caption() -> None:
    response = {"status": "no_suitable_composition", "reason": "Nothing fits."}
    provider = StaticLLMProvider(response)
    engine = CompositionPlannerEngine(provider)
    intent = make_statement_intent()
    result = engine.run(intent=intent, beat_id="beat_07")
    assert result.beat.composition_data["caption"] == intent.what_viewer_must_understand


def test_planner_rejects_missing_calculation_story_required_fields_and_fails_fast() -> None:
    engine = CompositionPlannerEngine()
    intent = VisualIntent(
        intent_id="intent_calc_err",
        narration_excerpt="A four percent withdrawal.",
        what_viewer_must_understand="Calculate 4%",
        key_values=["4%"],
        relationship_type="calculation",
        measurements=[
            # Missing metric_name and entity_name: passes Stage 1 sufficiency, but fails Stage 2 calculation_story eligibility
            QuantitativeMeasurement(raw_value="50L", role="input"),
            QuantitativeMeasurement(raw_value="2L", role="result"),
        ],
    )
    with pytest.raises(CompositionPlannerEngineError) as exc_info:
        engine.run(intent=intent, beat_id="beat_calc_err")
    assert "not eligible for composition 'calculation_story'" in str(exc_info.value)
