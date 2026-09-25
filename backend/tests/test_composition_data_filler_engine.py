"""Regression tests for schema-scoped, fact-locked composition filling."""
from typing import Any

import pytest

from domain.visual_intent import QuantitativeMeasurement, VisualIntent
from engines.composition_data_filler_engine import (
    CompositionDataFillerEngine,
    CompositionDataFillerError,
)
from engines.composition_planner_engine import CompositionPlannerEngine
from providers.llm_provider import LLMJsonRequest, LLMJsonResponse, LLMProviderMetadata
from registries.composition_registry import CompositionRegistry


class StaticFiller:
    def __init__(self, payload: dict[str, Any]):
        self.payload = payload
        self.requests: list[LLMJsonRequest] = []

    def generate_json(self, request: LLMJsonRequest) -> LLMJsonResponse:
        self.requests.append(request)
        return LLMJsonResponse(
            payload=self.payload,
            metadata=LLMProviderMetadata(provider="test", model="fixture"),
        )


def metric_intent() -> VisualIntent:
    return VisualIntent(
        intent_id="intent_01",
        narration_excerpt="Start with ₹50 lakh.",
        what_viewer_must_understand="The starting portfolio is ₹50 lakh.",
        relationship_type="metric",
        measurements=[
            QuantitativeMeasurement(
                raw_value="₹50 lakh",
                metric_name="Starting Portfolio",
                role="input",
            )
        ],
    )


def test_filler_sends_only_selected_schema_and_preserves_fact() -> None:
    provider = StaticFiller({"value": "₹50 lakh", "label": "Starting Portfolio"})
    definition = CompositionRegistry.get("metric_hero")
    assert definition is not None

    result = CompositionDataFillerEngine(provider).fill(
        intent=metric_intent(),
        composition=definition,
        source_artifact_id="artifact_visual_intent",
        source_idea_id="idea_01",
    )

    assert result.composition_data["value"] == "₹50 lakh"
    request = provider.requests[0]
    assert request.schema_name == "CompositionData:metric_hero"
    assert "composition_data" not in request.response_schema.get("properties", {})
    assert "CompositionPlannerResponse" not in request.messages[1].content


def test_planner_beat_identifies_exact_source_intent() -> None:
    provider = StaticFiller({"value": "₹50 lakh", "label": "Starting Portfolio"})
    result = CompositionPlannerEngine(llm_provider=provider).run(
        intent=metric_intent(),
        beat_id="beat_01",
        source_idea_id="idea_01",
        source_visual_intent_artifact_id="artifact_visual_intent",
    )

    assert result.beat.source_intent_id == "intent_01"
    assert result.beat.source_idea_id == "idea_01"
    assert result.beat.source_visual_intent_artifact_id == "artifact_visual_intent"
    assert result.beat.composition_data["value"] == "₹50 lakh"


def test_changed_factual_value_is_rejected() -> None:
    definition = CompositionRegistry.get("metric_hero")
    assert definition is not None
    provider = StaticFiller({"value": "₹5,000", "label": "Starting Portfolio"})

    with pytest.raises(CompositionDataFillerError, match="not present"):
        CompositionDataFillerEngine(provider).fill(intent=metric_intent(), composition=definition)


def test_missing_required_fact_is_rejected_without_placeholder() -> None:
    definition = CompositionRegistry.get("metric_hero")
    assert definition is not None
    provider = StaticFiller({"value": "₹50 lakh", "label": "Original Value"})

    with pytest.raises(CompositionDataFillerError, match="placeholder|unsupported"):
        CompositionDataFillerEngine(provider).fill(intent=metric_intent(), composition=definition)


def test_extra_wrapper_or_unknown_field_is_rejected() -> None:
    definition = CompositionRegistry.get("metric_hero")
    assert definition is not None
    provider = StaticFiller({
        "value": "₹50 lakh",
        "label": "Starting Portfolio",
        "composition_id": "calculation_story",
    })

    with pytest.raises(CompositionDataFillerError, match="extra|composition_id"):
        CompositionDataFillerEngine(provider).fill(intent=metric_intent(), composition=definition)
