"""Tests proving removal of fabricated storyboard content fallbacks and proper retry handling."""
from __future__ import annotations

import pytest
from pydantic import ValidationError

from domain.narrative_plan import NarrativePlan, SceneBeat
from domain.research_packet import ResearchPacket
from domain.storyboard import StoryboardInputContext
from domain.storyboard_foundation import WorldFoundationSpec
from domain.visual_intent import VisualIntent, VisualIntentSequence
from domain.visual_intent_artifact import VisualIntentArtifact, build_visual_intent_provenance
from engines.scene_storyboarder_engine import (
    SceneStoryboarderEngine,
    SceneStoryboarderEngineError,
    _sanitize_and_repair_foundation_payload,
)
from providers.llm_provider import LLMJsonRequest, LLMJsonResponse, LLMProvider, LLMProviderMetadata


class SequenceMockLLMProvider(LLMProvider):
    """Mock LLM provider that yields pre-configured payloads across retry attempts."""

    def __init__(self, payloads: list[dict]):
        self.payloads = payloads
        self.call_count = 0
        self.recorded_requests: list[LLMJsonRequest] = []

    def generate_json(self, request: LLMJsonRequest) -> LLMJsonResponse:
        self.recorded_requests.append(request)
        if self.call_count < len(self.payloads):
            payload = self.payloads[self.call_count]
            self.call_count += 1
        else:
            payload = self.payloads[-1]
        return LLMJsonResponse(
            payload=payload,
            metadata=LLMProviderMetadata(provider="mock", model="mock"),
        )


def _build_test_context() -> StoryboardInputContext:
    full_script = "When the central bank nudges rates up, floating mortgage costs climb."
    seq = VisualIntentSequence(
        idea_id="idea_01",
        narration=full_script,
        intents=[
            VisualIntent(
                intent_id="intent_01",
                narration_excerpt=full_script,
                what_viewer_must_understand="Rate hikes inflate mortgage costs.",
            )
        ],
    )
    return StoryboardInputContext(
        full_script=full_script,
        narrative_plan=NarrativePlan(
            thesis="Rates drive mortgages.",
            target_pain_point="Cost inflation",
            conceptual_hook="The rate hike",
            narrative_arc_type="expository",
            beats=[SceneBeat(beat_id="beat_01", scene_id="scene_01", title="Intro", focus_concept="Hike", core_teaching_point="Impact")],
        ),
        visual_intent_artifact=VisualIntentArtifact(
            sequences=[seq],
            provenance=build_visual_intent_provenance(seq, source_kind="idea"),
        ),
        verified_facts=["Rates increased by 25 bps."],
    )


# -----------------------------------------------------------------------------
# 1. No Fabricated Defaults in _sanitize_and_repair_foundation_payload
# -----------------------------------------------------------------------------

def test_no_fabricated_defaults_for_herostat_or_metriccard():
    raw_payload = {
        "world_id": "test_world",
        "beats": [
            {
                "beat_id": "beat_01",
                "narration": "When the central bank nudges rates up, floating mortgage costs climb.",
                "visual_goal": "Show rate",
                "visual_strategy": "Hero stat",
                "elements": [
                    {
                        "object_id": "rate_stat",
                        "component_type": "HeroStat",
                        "semantic_content": {},  # Missing label and display_value
                    },
                    {
                        "object_id": "metric_card_test",
                        "component_type": "MetricCard",
                        "semantic_content": {},  # Missing label and display_value
                    },
                ],
            }
        ],
    }

    sanitized = _sanitize_and_repair_foundation_payload(raw_payload)
    el1_sem = sanitized["beats"][0]["elements"][0]["semantic_content"]
    el2_sem = sanitized["beats"][0]["elements"][1]["semantic_content"]

    # Must NOT have fabricated '0%', '100%', or invented labels
    assert "display_value" not in el1_sem
    assert "label" not in el1_sem
    assert "display_value" not in el2_sem
    assert "label" not in el2_sem

    # When validated by WorldFoundationSpec, must fail component validation clearly
    with pytest.raises(ValidationError) as exc_info:
        WorldFoundationSpec.model_validate(sanitized)
    errors = str(exc_info.value)
    assert "display_value" in errors
    assert "label" in errors


def test_no_fabricated_defaults_for_comparison_process_callout_flow():
    raw_payload = {
        "world_id": "test_world",
        "beats": [
            {
                "beat_id": "beat_01",
                "narration": "When the central bank nudges rates up, floating mortgage costs climb.",
                "visual_goal": "Test missing",
                "visual_strategy": "Test",
                "elements": [
                    {
                        "object_id": "comp_1",
                        "component_type": "ComparisonCard",
                        "semantic_content": {},  # Missing left/right labels/values
                    },
                    {
                        "object_id": "proc_1",
                        "component_type": "ProcessCard",
                        "semantic_content": {},  # Missing steps
                    },
                    {
                        "object_id": "callout_1",
                        "component_type": "Callout",
                        "semantic_content": {},  # Missing text
                    },
                    {
                        "object_id": "flow_1",
                        "component_type": "FlowConnector",
                        "semantic_content": {},  # Missing source_id, target_id
                    },
                ],
            }
        ],
    }

    sanitized = _sanitize_and_repair_foundation_payload(raw_payload)
    comp_sem = sanitized["beats"][0]["elements"][0]["semantic_content"]
    proc_sem = sanitized["beats"][0]["elements"][1]["semantic_content"]
    callout_sem = sanitized["beats"][0]["elements"][2]["semantic_content"]
    flow_sem = sanitized["beats"][0]["elements"][3]["semantic_content"]

    # ComparisonCard: no 'Baseline', 'Observed', 'Standard Reality', 'Key Contrast'
    assert "left_label" not in comp_sem
    assert "left_value" not in comp_sem
    assert "right_label" not in comp_sem
    assert "right_value" not in comp_sem

    # ProcessCard: no generic steps inserted
    assert "steps" not in proc_sem

    # Callout: no narration excerpt inserted
    assert "text" not in callout_sem

    # FlowConnector: no inferred endpoints or circular references
    assert "source_id" not in flow_sem
    assert "target_id" not in flow_sem


# -----------------------------------------------------------------------------
# 2. Safe Structural Normalization & Aliases Preserved
# -----------------------------------------------------------------------------

def test_safe_normalization_preserves_root_props_and_aliases():
    raw_payload = {
        "world_id": "test_world",
        "beats": [
            {
                "beat_id": "beat_01",
                "narration": "When the central bank nudges rates up, floating mortgage costs climb.",
                "visual_goal": "Show rates",
                "visual_strategy": "Hero stat",
                "elements": [
                    {
                        "object_id": "hero_stat_1",
                        "component_type": "HeroStat",
                        # Properties placed at root level instead of semantic_content
                        "label": "REPO RATE",
                        "display_value": "6.50%",
                        "badge_text": "BENCHMARK",
                    },
                    {
                        "object_id": "comp_card_1",
                        "component_type": "ComparisonCard",
                        "semantic_content": {
                            "title": "RATE SPREAD",  # title alias for header
                            "left_label": "LOAN",
                            "left_value": "8.5%",
                            "right_label": "DEPOSIT",
                            "right_value": "6.5%",
                        },
                    },
                ],
            }
        ],
    }

    sanitized = _sanitize_and_repair_foundation_payload(raw_payload)

    # HeroStat root properties rescued into semantic_content and badge_text mapped to tag
    hero_sem = sanitized["beats"][0]["elements"][0]["semantic_content"]
    assert hero_sem["label"] == "REPO RATE"
    assert hero_sem["display_value"] == "6.50%"
    assert hero_sem["tag"] == "BENCHMARK"
    assert "badge_text" not in hero_sem
    assert "display_value" not in sanitized["beats"][0]["elements"][0]

    # ComparisonCard title mapped to header
    comp_sem = sanitized["beats"][0]["elements"][1]["semantic_content"]
    assert comp_sem["header"] == "RATE SPREAD"
    assert "title" not in comp_sem

    # Validates cleanly via WorldFoundationSpec
    spec = WorldFoundationSpec.model_validate(sanitized)
    assert spec.beats[0].elements[0].semantic_content["tag"] == "BENCHMARK"
    assert spec.beats[0].elements[1].semantic_content["header"] == "RATE SPREAD"


# -----------------------------------------------------------------------------
# 3. Engine Retry Path Correctly Reports Validation Error
# -----------------------------------------------------------------------------

def test_engine_retry_recovers_when_llm_fixes_missing_property():
    invalid_payload = {
        "world_id": "retry_world",
        "beats": [
            {
                "beat_id": "beat_01",
                "narration": "When the central bank nudges rates up, floating mortgage costs climb.",
                "visual_goal": "Show rate",
                "visual_strategy": "Hero stat",
                "elements": [
                    {
                        "object_id": "rate_stat",
                        "component_type": "HeroStat",
                        "semantic_content": {
                            "label": "REPO RATE",
                            # Missing display_value
                        },
                    }
                ],
            }
        ],
    }

    valid_payload = {
        "world_id": "retry_world",
        "beats": [
            {
                "beat_id": "beat_01",
                "narration": "When the central bank nudges rates up, floating mortgage costs climb.",
                "visual_goal": "Show rate",
                "visual_strategy": "Hero stat",
                "elements": [
                    {
                        "object_id": "rate_stat",
                        "component_type": "HeroStat",
                        "semantic_content": {
                            "label": "REPO RATE",
                            "display_value": "6.50%",
                        },
                    }
                ],
            }
        ],
    }

    provider = SequenceMockLLMProvider([invalid_payload, valid_payload])
    engine = SceneStoryboarderEngine(provider)
    context = _build_test_context()

    result = engine.run(context)
    assert result is not None
    assert result.storyboard.world_id == "retry_world"
    assert provider.call_count == 2

    # Check feedback sent to LLM on attempt 2
    second_request = provider.recorded_requests[1]
    user_prompt = second_request.messages[1].content
    assert "=== PREVIOUS VALIDATION FEEDBACK ===" in user_prompt
    assert "display_value" in user_prompt
    assert "Field required" in user_prompt


def test_engine_raises_clear_error_when_retries_exhausted():
    invalid_payload = {
        "world_id": "fail_world",
        "beats": [
            {
                "beat_id": "beat_01",
                "narration": "When the central bank nudges rates up, floating mortgage costs climb.",
                "visual_goal": "Show rate",
                "visual_strategy": "Hero stat",
                "elements": [
                    {
                        "object_id": "rate_stat",
                        "component_type": "HeroStat",
                        "semantic_content": {
                            # Missing label and display_value
                        },
                    }
                ],
            }
        ],
    }

    provider = SequenceMockLLMProvider([invalid_payload, invalid_payload, invalid_payload])
    engine = SceneStoryboarderEngine(provider)
    context = _build_test_context()

    with pytest.raises(SceneStoryboarderEngineError) as exc_info:
        engine.run(context)

    err = str(exc_info.value)
    assert "WorldFoundationSpec validation failed" in err
    assert "display_value" in err
    assert provider.call_count == 3


def test_sanitizer_merges_split_element_and_cleans_primitives():
    payload = {
        "world_id": "test_merge_world",
        "beats": [
            {
                "beat_id": "beat_01",
                "narration": "When the central bank nudges rates up, floating mortgage costs climb.",
                "visual_goal": "Show rate",
                "visual_strategy": "Hero stat",
                "elements": [
                    {
                        "object_id": "rate_stat",
                        "component_type": "HeroStat",
                        "role": "primary",
                        "macro_zone": "center",
                    },
                    {
                        "object_id": "rate_stat",
                        "semantic_content": {
                            "label": "BENCHMARK RATE",
                            "display_value": "6.50%",
                            "precision": 0,
                            "value": 6.5,
                        },
                    },
                    {
                        "object_id": "takeaway_callout",
                        "component_type": "Callout",
                        "semantic_content": {
                            "text": "Rates impact mortgages.",
                            "precision": 0,
                            "value": 0,
                        },
                    },
                ],
            }
        ],
    }

    sanitized = _sanitize_and_repair_foundation_payload(payload)
    beat_elements = sanitized["beats"][0]["elements"]
    assert len(beat_elements) == 2

    stat = beat_elements[0]
    assert stat["object_id"] == "rate_stat"
    assert stat["component_type"] == "HeroStat"
    assert stat["role"] == "primary"
    assert stat["semantic_content"]["label"] == "BENCHMARK RATE"
    assert stat["semantic_content"]["display_value"] == "6.50%"
    assert stat["semantic_content"]["raw_value"] == 6.5
    assert "precision" not in stat["semantic_content"]
    assert "value" not in stat["semantic_content"]

    callout = beat_elements[1]
    assert callout["object_id"] == "takeaway_callout"
    assert callout["semantic_content"]["text"] == "Rates impact mortgages."
    assert "precision" not in callout["semantic_content"]
    assert "value" not in callout["semantic_content"]


def test_cross_beat_inheritance_in_sanitizer():
    payload = {
        "world_id": "test_world",
        "beats": [
            {
                "beat_id": "beat_01",
                "narration": "First beat script.",
                "visual_goal": "Goal 1",
                "visual_strategy": "Strategy 1",
                "elements": [
                    {
                        "object_id": "crude_metric",
                        "component_type": "MetricCard",
                        "semantic_content": {
                            "label": "CRUDE OIL IMPORT DEPENDENCY",
                            "display_value": "85%",
                            "raw_value": 85,
                        },
                    }
                ],
            },
            {
                "beat_id": "beat_02",
                "narration": "Second beat script.",
                "visual_goal": "Goal 2",
                "visual_strategy": "Strategy 2",
                "elements": [
                    {
                        "object_id": "crude_metric",
                        # component_type and display_value/label omitted on reuse
                        "semantic_content": {
                            "variant": "elevated",
                        },
                    }
                ],
            },
        ],
    }

    sanitized = _sanitize_and_repair_foundation_payload(payload)
    b2_elem = sanitized["beats"][1]["elements"][0]

    assert b2_elem["component_type"] == "MetricCard"
    assert b2_elem["semantic_content"]["label"] == "CRUDE OIL IMPORT DEPENDENCY"
    assert b2_elem["semantic_content"]["display_value"] == "85%"
    assert b2_elem["semantic_content"]["variant"] == "elevated"

