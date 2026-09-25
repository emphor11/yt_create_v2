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


def test_numeric_value_accepted_without_grounding_rejection() -> None:
    definition = CompositionRegistry.get("metric_hero")
    assert definition is not None
    provider = StaticFiller({"value": "0", "label": "Starting Portfolio"})
    result = CompositionDataFillerEngine(provider).fill(intent=metric_intent(), composition=definition)
    assert result.composition_data["value"] == "0"


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


def test_cause_effect_structure_is_filled_after_intent_stage() -> None:
    intent = VisualIntent(
        intent_id="intent_cause_01",
        narration_excerpt="Lifestyle inflation swallowed every rupee before saving.",
        what_viewer_must_understand="Lifestyle inflation prevents saving.",
        relationship_type="cause_effect",
    )
    definition = CompositionRegistry.get("cause_effect")
    assert definition is not None
    provider = StaticFiller({
        "causes": [{"label": "Lifestyle inflation"}],
        "connector": "causes",
        "outcome_label": "every rupee before saving",
    })

    result = CompositionPlannerEngine(llm_provider=provider).run(
        intent=intent,
        beat_id="beat_cause_01",
        source_idea_id="idea_01",
        source_visual_intent_artifact_id="artifact_visual_intent",
    )

    assert result.beat.composition_id == "cause_effect"
    assert result.beat.composition_data["causes"][0]["label"] == "Lifestyle inflation"


def test_semantic_label_can_be_grounded_in_persisted_intent_text() -> None:
    intent = VisualIntent(
        intent_id="intent_semantic_label_01",
        narration_excerpt="Lifestyle inflation quietly swallowed every rupee before you could save.",
        what_viewer_must_understand="Lifestyle inflation silently consumes savings before accumulation can happen.",
        relationship_type="cause_effect",
    )
    definition = CompositionRegistry.get("cause_effect")
    assert definition is not None
    provider = StaticFiller({
        "causes": [{"label": "Savings"}],
        "connector": "causes",
        "outcome_label": "Lifestyle inflation",
    })

    result = CompositionDataFillerEngine(provider).fill(
        intent=intent,
        composition=definition,
    )

    assert result.composition_data["causes"][0]["label"] == "Savings"


def test_selected_schema_rejects_missing_required_calculation_data() -> None:
    intent = VisualIntent(
        intent_id="intent_calc_01",
        narration_excerpt="The annual withdrawal is two lakh rupees.",
        what_viewer_must_understand="Two lakh is the annual withdrawal.",
        relationship_type="calculation",
        measurements=[QuantitativeMeasurement(raw_value="two lakh rupees", role="result")],
    )
    definition = CompositionRegistry.get("calculation_story")
    assert definition is not None
    provider = StaticFiller({"result_label": "Annual Withdrawal", "result_value": "two lakh rupees"})

    with pytest.raises(CompositionDataFillerError, match="input_label|input_value"):
        CompositionDataFillerEngine(provider).fill(intent=intent, composition=definition)


def test_filler_allows_synthesized_phrasing_without_strict_substring_failure() -> None:
    intent = VisualIntent(
        intent_id="intent_02",
        narration_excerpt="You planned to save, but lifestyle inflation quietly swallowed every rupee before you even noticed.",
        what_viewer_must_understand="Lifestyle inflation silently consumes savings before any accumulation can happen.",
        relationship_type="cause_effect",
    )
    definition = CompositionRegistry.get("cause_effect")
    assert definition is not None
    provider = StaticFiller({
        "causes": [{"label": "Lifestyle inflation"}],
        "connector": "causes",
        "outcome_label": "Savings loss",
        "outcome_note": "Every rupee consumed before noticed",
    })

    result = CompositionDataFillerEngine(provider).fill(
        intent=intent,
        composition=definition,
    )

    assert result.composition_data["outcome_note"] == "Every rupee consumed before noticed"
