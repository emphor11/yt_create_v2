from __future__ import annotations

import pytest
from pydantic import ValidationError

from domain.continuous_story_plan import ContinuousStoryDraft
from domain.research_packet import ResearchPacket
from domain.script_visual_strategy import ScriptVisualStrategy, VideoIdea
from domain.voice_track import VoiceTrack, WordTimestamp
from engines.continuous_story_engine import (
    ContinuousStoryEngine,
    ContinuousStoryEngineError,
    _normalize_zone,
    _safe_contract_repair,
    _safe_temporal_repair,
)
from providers.llm_provider import (
    LLMJsonRequest,
    LLMJsonResponse,
    LLMMessage,
    LLMProvider,
    LLMProviderMetadata,
)


@pytest.fixture
def sample_voice_track():
    return VoiceTrack(
        voice_id="Matthew",
        audio_file_name="narration.mp3",
        storage_key="test/narration.mp3",
        duration_seconds=5.0,
        full_script_text="A 50 lakh rupee home loan starts at 8.5 percent interest.",
        word_timestamps=[
            WordTimestamp(word="A", start_ms=0, end_ms=300),
            WordTimestamp(word="50", start_ms=300, end_ms=600),
            WordTimestamp(word="lakh", start_ms=600, end_ms=1000),
            WordTimestamp(word="rupee", start_ms=1000, end_ms=1400),
            WordTimestamp(word="home", start_ms=1400, end_ms=1800),
            WordTimestamp(word="loan", start_ms=1800, end_ms=2200),
            WordTimestamp(word="starts", start_ms=2200, end_ms=2600),
            WordTimestamp(word="at", start_ms=2600, end_ms=3000),
            WordTimestamp(word="8.5", start_ms=3000, end_ms=3500),
            WordTimestamp(word="percent", start_ms=3500, end_ms=4000),
            WordTimestamp(word="interest", start_ms=4000, end_ms=4500),
        ],
    )


@pytest.fixture
def sample_research_packet():
    return ResearchPacket(
        topic="Home Loan Rate Hike",
        audience="borrowers",
        channel="Finance",
        verified_facts=["₹50 lakhs loan at 8.5% interest rate with 100 bps hike"],
        approved_facts={
            "research_money_1": {
                "value": 5000000,
                "format": "currency_inr",
                "display": "₹50,00,000",
                "meaning": "home loan principal amount",
            },
            "research_percent_2": {
                "value": 8.5,
                "format": "percentage",
                "display": "8.5%",
                "meaning": "annual interest rate",
            },
            "research_bps_3": {
                "value": 100,
                "format": "basis_points",
                "display": "100 bps",
                "meaning": "rate shift",
            },
        },
    )


@pytest.fixture
def sample_strategy():
    return ScriptVisualStrategy(
        thesis="Rate hikes increase interest burdens.",
        ideas=[
            VideoIdea(
                idea_id="idea_01",
                title="Loan overview",
                focus_concept="Principal",
                core_teaching_point="Starting loan amount",
                narration="A 50 lakh rupee home loan starts at 8.5 percent interest.",
            )
        ],
    )


def test_structured_facts_are_loaded_from_the_research_packet(sample_research_packet):
    assert sample_research_packet.approved_facts["research_money_1"]["value"] == 5000000
    assert sample_research_packet.approved_facts["research_percent_2"]["display"] == "8.5%"
    assert sample_research_packet.approved_facts["research_bps_3"]["format"] == "basis_points"


def test_direct_authoring_prompt_does_not_inject_fact_registry(sample_research_packet):
    from engines.continuous_story_engine import build_continuous_story_prompt
    facts = sample_research_packet.approved_facts
    _, user_prompt = build_continuous_story_prompt("story_test", "Test narration", facts)
    assert "SEMANTIC FACT REGISTRY" not in user_prompt
    assert "APPROVED FACT IDS" not in user_prompt
    assert "Test narration" in user_prompt


def test_zone_normalization():
    # 5 allowed layouts return themselves
    for z in ("center", "split_left", "split_right", "full_screen", "full_bottom"):
        assert _normalize_zone(z) == z

    # Removed layouts fail loudly with INVALID_LAYOUT_ZONE
    removed = [
        "top_left", "top_center", "top_right",
        "center_left", "center_right",
        "bottom_left", "bottom_center", "bottom_right",
        "full_top", "left", "right", "top", "bottom", "invalid_zone"
    ]
    for r in removed:
        with pytest.raises(ValueError, match="INVALID_LAYOUT_ZONE"):
            _normalize_zone(r)

    # Relative layout dictionary fails loudly
    with pytest.raises(ValueError, match="INVALID_LAYOUT_ZONE"):
        _normalize_zone({"right_of": "card_a"})


def test_continuous_story_engine_isolated_run(
    sample_voice_track,
    sample_strategy,
    sample_research_packet,
):
    engine = ContinuousStoryEngine()
    approved_facts = {
        "loan_principal": {
            "label": "Loan Principal",
            "value": 5000000,
            "format": "currency_inr",
        }
    }
    mock_draft = {
        "story_id": "test_loan_story",
        "objects": [
            {
                "id": "loan_card",
                "type": "card",
                "layout": "center",
                "purpose": "Hero card",
                "value_fact_id": "loan_principal",
                "title": "Home Loan Principal",
            },
        ],
        "events": [
            {
                "action": "enter",
                "target_id": "loan_card",
                "anchor": "50 lakh",
            }
        ],
    }

    result = engine.run(
        project_id="proj_123",
        voice_track=sample_voice_track,
        strategy=sample_strategy,
        research_packet=sample_research_packet,
        approved_facts=approved_facts,
        mock_draft=mock_draft,
    )

    assert result.artifact.story_id == "test_loan_story"
    assert result.artifact.width == 1920
    assert result.artifact.height == 1080
    assert len(result.draft.objects) == 1
    assert result.draft.objects[0].id == "loan_card"
    assert result.artifact.plan["durationInFrames"] >= 150


class MockLLMProvider(LLMProvider):
    def __init__(self, responses: list[dict]):
        self.responses = responses
        self.call_count = 0

    def generate_json(self, request: LLMJsonRequest) -> LLMJsonResponse:
        payload = self.responses[self.call_count]
        self.call_count += 1
        return LLMJsonResponse(
            payload=payload,
            metadata=LLMProviderMetadata(provider="google", model="mock-gemini"),
        )

    def generate_text(self, request: Any) -> Any:
        raise NotImplementedError


def test_continuous_story_engine_with_llm_provider(
    sample_voice_track,
    sample_strategy,
    sample_research_packet,
):
    valid_ai_response = {
        "story_id": "ai_loan_story",
        "objects": [
            {
                "id": "loan_card",
                "type": "card",
                "layout": "center",
                "purpose": "Principal card",
                "value_fact_id": "research_money_1",
                "display_value": "₹50 Lakhs",
                "numeric_value": 5000000,
                "subtitle": "Starting principal",
                "title": "Home Loan Principal",
            },
        ],
        "events": [
            {
                "action": "enter",
                "target_id": "loan_card",
                "anchor": "50 lakh",
            }
        ],
    }
    mock_llm = MockLLMProvider([valid_ai_response])
    engine = ContinuousStoryEngine(llm_provider=mock_llm)

    result = engine.run(
        project_id="proj_ai",
        voice_track=sample_voice_track,
        strategy=sample_strategy,
        research_packet=sample_research_packet,
    )

    assert mock_llm.call_count == 1
    assert result.draft.story_id == "ai_loan_story"
    assert result.artifact.story_id == "ai_loan_story"
    assert result.provider_metadata.model == "mock-gemini"


def test_connector_missing_from_id_fails(
    sample_voice_track,
    sample_strategy,
    sample_research_packet,
):
    engine = ContinuousStoryEngine()
    invalid_draft = {
        "story_id": "test_missing_from_id",
        "objects": [
            {
                "id": "card_a",
                "type": "card",
                "layout": "split_left",
                "purpose": "Source card",
                "value_fact_id": "research_money_1",
                "title": "Principal",
            },
            {
                "id": "card_b",
                "type": "card",
                "layout": "split_right",
                "purpose": "Target card",
                "value_fact_id": "research_money_1",
                "title": "Repayment",
            },
            {
                "id": "causality_connector",
                "type": "connector",
                "layout": "center",
                "purpose": "Link",
                "to_id": "card_b",
                "label": "Drives repayment",
                # missing from_id!
            },
        ],
        "events": [
            {"action": "enter", "target_id": "card_a", "anchor": "50 lakh"},
            {"action": "enter", "target_id": "card_b", "anchor": "starts at"},
            {"action": "connect", "target_id": "causality_connector", "anchor": "interest"},
        ],
    }

    with pytest.raises(ContinuousStoryEngineError) as exc_info:
        engine.run(
            project_id="proj_fail_1",
            voice_track=sample_voice_track,
            strategy=sample_strategy,
            research_packet=sample_research_packet,
            mock_draft=invalid_draft,
        )

    err_msg = str(exc_info.value)
    assert "Stage 7 failed: invalid visual choreography contract" in err_msg
    assert "CONTINUOUS_STORY_CONTRACT_ERROR: Connector 'causality_connector' requires valid from_id and to_id." in err_msg
    assert exc_info.value.raw_payload == invalid_draft


def test_connector_missing_to_id_fails(
    sample_voice_track,
    sample_strategy,
    sample_research_packet,
):
    engine = ContinuousStoryEngine()
    invalid_draft = {
        "story_id": "test_missing_to_id",
        "objects": [
            {
                "id": "card_a",
                "type": "card",
                "layout": "split_left",
                "purpose": "Source card",
                "value_fact_id": "research_money_1",
                "title": "Principal",
            },
            {
                "id": "card_b",
                "type": "card",
                "layout": "split_right",
                "purpose": "Target card",
                "value_fact_id": "research_money_1",
                "title": "Repayment",
            },
            {
                "id": "causality_connector",
                "type": "connector",
                "layout": "center",
                "purpose": "Link",
                "from_id": "card_a",
                "label": "Drives repayment",
                # missing to_id!
            },
        ],
        "events": [
            {"action": "enter", "target_id": "card_a", "anchor": "50 lakh"},
            {"action": "enter", "target_id": "card_b", "anchor": "starts at"},
            {"action": "connect", "target_id": "causality_connector", "anchor": "interest"},
        ],
    }

    with pytest.raises(ContinuousStoryEngineError) as exc_info:
        engine.run(
            project_id="proj_fail_2",
            voice_track=sample_voice_track,
            strategy=sample_strategy,
            research_packet=sample_research_packet,
            mock_draft=invalid_draft,
        )

    err_msg = str(exc_info.value)
    assert "Stage 7 failed: invalid visual choreography contract" in err_msg
    assert "CONTINUOUS_STORY_CONTRACT_ERROR: Connector 'causality_connector' requires valid from_id and to_id." in err_msg
    assert exc_info.value.raw_payload == invalid_draft


def test_connector_unknown_endpoint_fails(
    sample_voice_track,
    sample_strategy,
    sample_research_packet,
):
    engine = ContinuousStoryEngine()
    invalid_draft = {
        "story_id": "test_unknown_endpoint",
        "objects": [
            {
                "id": "card_a",
                "type": "card",
                "layout": "split_left",
                "purpose": "Source card",
                "value_fact_id": "research_money_1",
                "title": "Principal",
            },
            {
                "id": "causality_connector",
                "type": "connector",
                "layout": "center",
                "purpose": "Link",
                "from_id": "card_a",
                "to_id": "ghost_card",  # Non-existent target ID!
                "label": "Drives repayment",
            },
        ],
        "events": [
            {"action": "enter", "target_id": "card_a", "anchor": "50 lakh"},
            {"action": "connect", "target_id": "causality_connector", "anchor": "interest"},
        ],
    }

    with pytest.raises(ContinuousStoryEngineError) as exc_info:
        engine.run(
            project_id="proj_fail_3",
            voice_track=sample_voice_track,
            strategy=sample_strategy,
            research_packet=sample_research_packet,
            mock_draft=invalid_draft,
        )

    err_msg = str(exc_info.value)
    assert "Stage 7 failed: invalid visual choreography contract" in err_msg
    assert "CONTINUOUS_STORY_CONTRACT_ERROR: Connector 'causality_connector' requires valid to_id that exists in declared objects (found 'ghost_card')." in err_msg


def test_connector_self_referencing_fails(
    sample_voice_track,
    sample_strategy,
    sample_research_packet,
):
    engine = ContinuousStoryEngine()
    invalid_draft = {
        "story_id": "test_self_referencing",
        "objects": [
            {
                "id": "card_a",
                "type": "card",
                "layout": "split_left",
                "purpose": "Source card",
                "value_fact_id": "research_money_1",
                "title": "Principal",
            },
            {
                "id": "causality_connector",
                "type": "connector",
                "layout": "center",
                "purpose": "Link",
                "from_id": "card_a",
                "to_id": "card_a",  # Self reference!
                "label": "Loops to self",
            },
        ],
        "events": [
            {"action": "enter", "target_id": "card_a", "anchor": "50 lakh"},
            {"action": "connect", "target_id": "causality_connector", "anchor": "interest"},
        ],
    }

    with pytest.raises(ContinuousStoryEngineError) as exc_info:
        engine.run(
            project_id="proj_fail_4",
            voice_track=sample_voice_track,
            strategy=sample_strategy,
            research_packet=sample_research_packet,
            mock_draft=invalid_draft,
        )

    err_msg = str(exc_info.value)
    assert "Stage 7 failed: invalid visual choreography contract" in err_msg
    assert "cannot connect element to itself" in err_msg


def test_invalid_repaired_response_fails(
    sample_voice_track,
    sample_strategy,
    sample_research_packet,
):
    # LLM produces invalid response on turn 1 (connector missing from_id)
    first_invalid = {
        "story_id": "ai_repair_story",
        "objects": [
            {
                "id": "card_a",
                "type": "card",
                "layout": "split_left",
                "purpose": "Principal card",
                "value_fact_id": "research_money_1",
                "title": "Home Loan Principal",
            },
            {
                "id": "causality_connector",
                "type": "connector",
                "layout": "center",
                "purpose": "Connector",
                "to_id": "card_a",
                # missing from_id!
            },
        ],
        "events": [
            {"action": "enter", "target_id": "card_a", "anchor": "50 lakh"},
        ],
    }
    # LLM repair attempt also returns invalid response (still missing from_id)
    second_invalid = {
        "story_id": "ai_repair_story",
        "objects": [
            {
                "id": "card_a",
                "type": "card",
                "layout": "split_left",
                "purpose": "Principal card",
                "value_fact_id": "research_money_1",
                "title": "Home Loan Principal",
            },
            {
                "id": "causality_connector",
                "type": "connector",
                "layout": "center",
                "purpose": "Connector",
                "to_id": "card_a",
                # STILL missing from_id!
            },
        ],
        "events": [
            {"action": "enter", "target_id": "card_a", "anchor": "50 lakh"},
        ],
    }

    mock_llm = MockLLMProvider([first_invalid, second_invalid])
    engine = ContinuousStoryEngine(llm_provider=mock_llm)

    with pytest.raises(ContinuousStoryEngineError) as exc_info:
        engine.run(
            project_id="proj_repair_fail",
            voice_track=sample_voice_track,
            strategy=sample_strategy,
            research_packet=sample_research_packet,
        )

    # Policy verification:
    # 1. 2 LLM calls made (initial + 1 repair attempt)
    assert mock_llm.call_count == 2
    # 2. Did NOT silently delete the connector!
    # 3. Failed loudly with exact contract error!
    err_msg = str(exc_info.value)
    assert "Stage 7 failed: invalid visual choreography contract" in err_msg
    assert "CONTINUOUS_STORY_CONTRACT_ERROR: Connector 'causality_connector' requires valid from_id and to_id." in err_msg
    # 4. Preserved raw invalid payload for debugging
    assert exc_info.value.raw_payload == second_invalid


def test_silent_fallbacks_disabled_by_policy():
    with pytest.raises(ContinuousStoryEngineError) as exc1:
        _safe_contract_repair({"objects": []})
    assert "Silent repair fallback is disabled by policy" in str(exc1.value)

    mock_draft = ContinuousStoryDraft(
        story_id="s1",
        objects=[
            {"id": "c1", "type": "card", "layout": "center", "title": "C1"}
        ],
        events=[
            {"action": "enter", "target_id": "c1", "anchor": "word"}
        ]
    )
    with pytest.raises(ContinuousStoryEngineError) as exc2:
        _safe_temporal_repair(mock_draft, [])
    assert "Silent temporal repair fallback is disabled by policy" in str(exc2.value)


def test_exit_without_direction_becomes_fade(
    sample_voice_track,
    sample_strategy,
    sample_research_packet,
):
    engine = ContinuousStoryEngine()
    draft = {
        "story_id": "test_exit_default",
        "objects": [
            {
                "id": "card_a",
                "type": "card",
                "layout": "center",
                "purpose": "Hero card",
                "value_fact_id": "research_money_1",
                "title": "Principal",
            },
        ],
        "events": [
            {"action": "enter", "target_id": "card_a", "anchor": "50 lakh"},
            {"action": "exit", "target_id": "card_a", "anchor": "starts at"},  # direction omitted!
        ],
    }

    result = engine.run(
        project_id="proj_exit_def",
        voice_track=sample_voice_track,
        strategy=sample_strategy,
        research_packet=sample_research_packet,
        mock_draft=draft,
    )

    exit_event = result.draft.events[1]
    assert exit_event.action == "exit"
    assert exit_event.direction == "fade"


def test_explicit_exit_direction_preserved(
    sample_voice_track,
    sample_strategy,
    sample_research_packet,
):
    engine = ContinuousStoryEngine()
    draft = {
        "story_id": "test_explicit_exit",
        "objects": [
            {
                "id": "card_a",
                "type": "card",
                "layout": "center",
                "purpose": "Hero card",
                "value_fact_id": "research_money_1",
                "title": "Principal",
            },
        ],
        "events": [
            {"action": "enter", "target_id": "card_a", "anchor": "50 lakh"},
            {"action": "exit", "target_id": "card_a", "direction": "left", "anchor": "starts at"},
        ],
    }

    result = engine.run(
        project_id="proj_explicit_exit",
        voice_track=sample_voice_track,
        strategy=sample_strategy,
        research_packet=sample_research_packet,
        mock_draft=draft,
    )

    exit_event = result.draft.events[1]
    assert exit_event.action == "exit"
    assert exit_event.direction == "left"


def test_move_without_to_fails(
    sample_voice_track,
    sample_strategy,
    sample_research_packet,
):
    engine = ContinuousStoryEngine()
    invalid_draft = {
        "story_id": "test_move_no_to",
        "objects": [
            {
                "id": "card_a",
                "type": "card",
                "layout": "center",
                "purpose": "Hero card",
                "value_fact_id": "research_money_1",
                "title": "Principal",
            },
        ],
        "events": [
            {"action": "enter", "target_id": "card_a", "anchor": "50 lakh"},
            {"action": "move", "target_id": "card_a", "anchor": "starts at"},  # Missing 'to'!
        ],
    }

    with pytest.raises(ContinuousStoryEngineError) as exc_info:
        engine.run(
            project_id="proj_move_fail",
            voice_track=sample_voice_track,
            strategy=sample_strategy,
            research_packet=sample_research_packet,
            mock_draft=invalid_draft,
        )

    err_msg = str(exc_info.value)
    assert "Stage 7 failed: invalid visual choreography contract" in err_msg
    assert "Action 'move' targeting 'card_a' requires 'to' destination zone." in err_msg


def test_malformed_connector_with_card_fields_fails_loudly(
    sample_voice_track,
    sample_strategy,
    sample_research_packet,
):
    engine = ContinuousStoryEngine()
    invalid_draft = {
        "story_id": "test_connector_card_fields",
        "objects": [
            {
                "id": "card_a",
                "type": "card",
                "layout": "split_left",
                "purpose": "Source",
                "value_fact_id": "research_money_1",
                "title": "Principal",
            },
            {
                "id": "card_b",
                "type": "card",
                "layout": "split_right",
                "purpose": "Target",
                "value_fact_id": "research_money_1",
                "title": "Repayment",
            },
            {
                "id": "conn1",
                "type": "connector",
                "layout": "center",
                "from_id": "card_a",
                "to_id": "card_b",
                "visual_state": "normal",  # Illegal card field on connector!
                "badge": "BURDEN",         # Illegal card field on connector!
            },
        ],
        "events": [
            {"action": "enter", "target_id": "card_a", "anchor": "50 lakh"},
            {"action": "enter", "target_id": "card_b", "anchor": "starts at"},
            {"action": "connect", "target_id": "conn1", "anchor": "interest"},
        ],
    }

    with pytest.raises(ContinuousStoryEngineError) as exc_info:
        engine.run(
            project_id="proj_conn_card_fields",
            voice_track=sample_voice_track,
            strategy=sample_strategy,
            research_packet=sample_research_packet,
            mock_draft=invalid_draft,
        )

    err_msg = str(exc_info.value)
    assert "Stage 7 failed: invalid visual choreography contract" in err_msg
    assert "CONTINUOUS_STORY_CONTRACT_ERROR: Connector 'conn1' cannot specify card field 'visual_state'." in err_msg


def test_valid_connectors_pass(
    sample_voice_track,
    sample_strategy,
    sample_research_packet,
):
    engine = ContinuousStoryEngine()
    valid_draft = {
        "story_id": "test_valid_connector",
        "objects": [
            {
                "id": "interest_card",
                "type": "card",
                "layout": "split_left",
                "purpose": "Source",
                "value_fact_id": "research_money_1",
                "title": "Interest",
            },
            {
                "id": "repayment_card",
                "type": "card",
                "layout": "split_right",
                "purpose": "Target",
                "value_fact_id": "research_money_1",
                "title": "Repayment",
            },
            {
                "id": "causality_connector",
                "type": "connector",
                "layout": "center",
                "from_id": "interest_card",
                "to_id": "repayment_card",
                "label": "Interest drives repayment",
            },
        ],
        "events": [
            {"action": "enter", "target_id": "interest_card", "anchor": "50 lakh"},
            {"action": "enter", "target_id": "repayment_card", "anchor": "home loan"},
            {"action": "connect", "target_id": "causality_connector", "anchor": "starts at"},
            {"action": "exit", "target_id": "interest_card", "anchor": "interest"},
        ],
    }

    result = engine.run(
        project_id="proj_valid_conn",
        voice_track=sample_voice_track,
        strategy=sample_strategy,
        research_packet=sample_research_packet,
        mock_draft=valid_draft,
    )

    assert result.draft.story_id == "test_valid_connector"
    assert len(result.draft.objects) == 3
    assert result.draft.events[3].action == "exit"
    assert result.draft.events[3].direction == "fade"  # defaulted
    assert result.artifact.plan["durationInFrames"] >= 150


def test_field_aliases_accepted_seamlessly(
    sample_voice_track,
    sample_strategy,
    sample_research_packet,
):
    engine = ContinuousStoryEngine()
    # Uses 'from', 'to' on connector and 'visualState' on change_visual_state
    alias_draft = {
        "story_id": "test_alias_draft",
        "objects": [
            {
                "id": "card_a",
                "type": "card",
                "layout": "split_left",
                "purpose": "Source",
                "value_fact_id": "research_money_1",
                "title": "Principal",
            },
            {
                "id": "card_b",
                "type": "card",
                "layout": "split_right",
                "purpose": "Target",
                "value_fact_id": "research_money_1",
                "title": "Repayment",
            },
            {
                "id": "conn1",
                "type": "connector",
                "layout": "center",
                "from": "card_a",  # alias for from_id!
                "to": "card_b",    # alias for to_id!
                "label": "Drives repayment",
            },
        ],
        "events": [
            {"action": "enter", "target_id": "card_a", "anchor": "50 lakh"},
            {"action": "enter", "target_id": "card_b", "anchor": "home loan"},
            {"action": "connect", "target_id": "conn1", "anchor": "starts at"},
            {
                "action": "change_visual_state",
                "target_id": "card_b",
                "visualState": "danger",  # alias for state!
                "anchor": "interest",
            },
        ],
    }

    result = engine.run(
        project_id="proj_alias_test",
        voice_track=sample_voice_track,
        strategy=sample_strategy,
        research_packet=sample_research_packet,
        mock_draft=alias_draft,
    )

    connector_obj = result.draft.objects[2]
    assert connector_obj.from_id == "card_a"
    assert connector_obj.to_id == "card_b"

    state_event = result.draft.events[3]
    assert state_event.state == "danger"


def test_card_requires_title_and_allows_optional_fact_id():
    # 1. Card with title but no value_fact_id (conceptual/chapter card) passes
    draft = ContinuousStoryDraft(
        story_id="test_conceptual_card",
        objects=[
            {
                "id": "chapter_card",
                "type": "card",
                "layout": "center",
                "title": "The hidden cost",
                "subtitle": "A mortgage can cost much more than expected",
            }
        ],
        events=[
            {"action": "enter", "target_id": "chapter_card", "anchor": "word"}
        ]
    )
    assert draft.objects[0].title == "The hidden cost"
    assert draft.objects[0].value_fact_id is None

    # 2. Card without title fails validation loudly
    with pytest.raises(ValueError) as exc:
        ContinuousStoryDraft(
            story_id="test_missing_title",
            objects=[
                {
                    "id": "bad_card",
                    "type": "card",
                    "layout": "center",
                    "subtitle": "Missing title",
                }
            ],
            events=[
                {"action": "enter", "target_id": "bad_card", "anchor": "word"}
            ]
        )
    assert "Card 'bad_card' requires non-empty 'title'." in str(exc.value)


def test_schema_card_contract_matches_pydantic_policy():
    schema = ContinuousStoryDraft.model_json_schema()
    card_schema = next(
        variant for variant in schema["properties"]["objects"]["items"]["anyOf"]
        if variant["properties"]["type"]["enum"] == ["card"]
    )
    # Title, display_value, and subtitle are required on cards
    assert "title" in card_schema["required"]
    assert "display_value" in card_schema["required"]
    assert "subtitle" in card_schema["required"]
    # value_fact_id is optional on cards
    assert "value_fact_id" not in card_schema["required"]
    assert "value_fact_id" in card_schema["properties"]


def test_format_programmatic_repair_prompt_structure():
    from engines.continuous_story_engine import format_programmatic_repair_prompt
    bad_payload = {
        "story_id": "test_bad",
        "objects": [
            {"id": "bad_card", "type": "card", "layout": "center"},
            {"id": "bad_conn", "type": "connector", "layout": "center", "title": "illegal"},
        ],
        "events": [
            {"action": "move", "target_id": "bad_card", "anchor": "test"},
            {"action": "transform_number", "target_id": "bad_card", "anchor": "test"},
            {"action": "change_visual_state", "target_id": "bad_card", "anchor": "test"},
        ],
    }

    with pytest.raises(ValidationError) as exc:
        ContinuousStoryDraft.model_validate(bad_payload)

    prompt = format_programmatic_repair_prompt(
        raw_payload=bad_payload,
        validation_error=exc.value,
        approved_facts={"research_money_1": 5000000},
    )

    # 1. Error on bad_card title
    assert 'objects[0]' in prompt
    assert "Every card must have non-empty 'title', 'display_value', and 'subtitle'" in prompt

    # 2. Error on bad_conn missing from_id, to_id and card fields
    assert 'objects[1]' in prompt
    assert 'Remove all card fields' in prompt
    assert 'Both from_id and to_id must reference declared non-connector objects' in prompt

    # 3. Error on move missing 'to'
    assert 'events[0]' in prompt
    assert 'Missing required field: "to"' in prompt
    assert '"split_left"' in prompt

    # 4. Error on transform_number missing direct values
    assert 'events[1]' in prompt
    assert 'Missing required fields: "to_display_value" and "to_numeric_value"' in prompt

    # 5. Error on change_visual_state missing 'state'
    assert 'events[2]' in prompt
    # 6. Exact repair instruction in prompt
    assert "Every anchor must be copied character-for-character from the verbatim narration." in prompt
    assert "Do not paraphrase." in prompt
    assert "Do not summarize." in prompt
    assert "Do not invent anchor text." in prompt
    assert "Use a unique phrase of at least 3 meaningful words." in prompt
    assert "An exit anchor must occur strictly after the target object's enter anchor." in prompt
    assert "Never use the same anchor for enter and exit." in prompt
    assert "If there is no later spoken phrase, omit the exit event instead of inventing one." in prompt


def test_repair_prompt_contains_narration_text_and_exit_conflict_details():
    from engines.continuous_story_engine import format_programmatic_repair_prompt
    from engines.continuous_story_draft_validator import DraftValidationError

    sample_narration = "A salaried employee invests monthly for a fixed return over twenty years."
    draft_err = DraftValidationError(
        code="EXIT_BEFORE_OBJECT_ENTER",
        message="Action 'exit' on 'card_x' occurs at 1000ms (exit anchor: 'invests monthly'), which is before or at its original enter anchor 'salaried employee' at 1000ms.",
        target_id="card_x",
        details={
            "target_id": "card_x",
            "exit_anchor": "invests monthly",
            "exit_time_ms": 1000,
            "enter_anchor": "salaried employee",
            "enter_time_ms": 1000,
        },
    )

    prompt = format_programmatic_repair_prompt(
        raw_payload={"objects": [], "events": []},
        draft_errors=[draft_err],
        narration_text=sample_narration,
    )

    # 1. Complete verbatim narration text included
    assert "Complete Verbatim Spoken Narration:" in prompt
    assert sample_narration in prompt

    # 2. Exact repair instructions included
    assert "Every anchor must be copied character-for-character from the verbatim narration." in prompt
    assert "An exit anchor must occur strictly after the target object's enter anchor." in prompt
    assert "Never use the same anchor for enter and exit." in prompt

    # 3. EXIT_BEFORE_OBJECT_ENTER conflict details included
    assert "Original enter anchor: 'salaried employee' (starts at 1000ms)" in prompt
    assert "Attempted exit anchor: 'invests monthly' (starts at 1000ms)" in prompt


def test_print_local_preflight_report_output(capsys):
    from engines.continuous_story_engine import print_local_preflight_report
    bad_payload = {
        "story_id": "test_bad",
        "objects": [{"id": "bad_card", "type": "card", "layout": "center"}],
        "events": [{"action": "move", "target_id": "bad_card", "anchor": "test"}],
    }

    with pytest.raises(ValidationError) as exc:
        ContinuousStoryDraft.model_validate(bad_payload)

    print_local_preflight_report(bad_payload, validation_error=exc.value)
    captured = capsys.readouterr().out

    assert "Objects: 1" in captured
    assert "Events:  1" in captured
    assert "Invalid fields / validation issues:" in captured
    assert "objects[0]" in captured
    assert "events[0]" in captured


def test_open_direct_authoring_mode_without_approved_facts(
    sample_voice_track,
    sample_strategy,
):
    packet = ResearchPacket(
        topic="Home Loan Comparison",
        audience="borrowers",
        channel="Finance",
        verified_facts=[
            "Home loan principal is 50 lakh with rate at 8.5 percent.",
            "Total repayment reaches 1.38 crore rupees over 30 years.",
        ],
    )
    # In open direct-authoring mode, empty approved_facts should NOT raise an error
    result = ContinuousStoryEngine().run(
        project_id="open_authoring_story",
        voice_track=sample_voice_track,
        strategy=sample_strategy,
        research_packet=packet,
        approved_facts={},
        available_assets=["chart_icon", "bank_logo"],
        mock_draft={
            "story_id": "open_authoring_story",
            "objects": [
                {
                    "id": "card_hero",
                    "type": "card",
                    "layout": "split_left",
                    "title": "Home Loan",
                    "display_value": "₹50 Lakhs",
                    "numeric_value": 5000000,
                    "subtitle": "30-Year Term",
                },
                {
                    "id": "num_rate",
                    "type": "number",
                    "layout": "split_right",
                    "display_value": "8.5%",
                    "numeric_value": 8.5,
                    "purpose": "Interest rate",
                },
                {
                    "id": "txt_note",
                    "type": "text",
                    "layout": "center",
                    "text": "Fixed rate benchmark",
                },
                {
                    "id": "chart_repay",
                    "type": "chart",
                    "layout": "full_bottom",
                    "chart_type": "split_bar",
                    "title": "Repayment Breakdown",
                    "subtitle": "Principal vs Interest",
                    "points": [
                        {"label": "Principal", "value": 50},
                        {"label": "Interest", "value": 88},
                    ],
                },
                {
                    "id": "img_bank",
                    "type": "image",
                    "layout": "center",
                    "asset_id": "bank_logo",
                },
                {
                    "id": "conn_hero_rate",
                    "type": "connector",
                    "layout": "center",
                    "from_id": "card_hero",
                    "to_id": "num_rate",
                    "label": "governed by",
                },
            ],
            "events": [
                {"action": "enter", "target_id": "img_bank", "anchor": "A"},
                {"action": "exit", "target_id": "img_bank", "anchor": "50"},
                {"action": "enter", "target_id": "card_hero", "anchor": "home"},
                {"action": "enter", "target_id": "num_rate", "anchor": "home"},
                {"action": "connect", "target_id": "conn_hero_rate", "anchor": "loan"},
                {"action": "exit", "target_id": "card_hero", "anchor": "starts"},
                {"action": "exit", "target_id": "num_rate", "anchor": "starts"},
                {"action": "enter", "target_id": "txt_note", "anchor": "8.5 percent"},
                {"action": "enter", "target_id": "chart_repay", "anchor": "interest"},
            ],
        },
    )
    assert result.draft.story_id == "open_authoring_story"
    assert len(result.draft.objects) == 6
    assert result.draft.objects[3].chart_type == "split_bar"
    assert len(result.draft.objects[3].points) == 2
    assert result.draft.objects[4].asset_id == "bank_logo"
    assert result.draft.objects[5].from_id == "card_hero"
    assert result.draft.objects[5].to_id == "num_rate"
    assert result.artifact.plan is not None


def test_direct_authoring_draft_validation():
    payload = {
        "story_id": "direct_draft_validation",
        "objects": [
            {
                "id": "card_hero",
                "type": "card",
                "layout": "center",
                "title": "Principal Loan",
                "display_value": "₹50 Lakhs",
                "numeric_value": 5000000,
                "subtitle": "Initial amount borrowed",
            }
        ],
        "events": [
            {
                "action": "enter",
                "target_id": "card_hero",
                "anchor": "borrowed",
            },
            {
                "action": "transform_number",
                "target_id": "card_hero",
                "anchor": "climbs to",
                "to_display_value": "₹1.38 Cr",
                "to_numeric_value": 13800000,
            },
        ],
    }

    draft = ContinuousStoryDraft.model_validate(payload)
    assert draft.objects[0].display_value == "₹50 Lakhs"
    assert draft.objects[0].numeric_value == 5000000
    assert draft.objects[0].subtitle == "Initial amount borrowed"
    assert draft.events[1].to_display_value == "₹1.38 Cr"
    assert draft.events[1].to_numeric_value == 13800000


def test_direct_authoring_contract_requires_card_display_value_and_subtitle():
    from engines.continuous_story_engine import _validate_direct_authoring_contract

    # Missing display_value
    draft_no_val = ContinuousStoryDraft.model_validate({
        "story_id": "test_missing_val",
        "objects": [{"id": "c1", "type": "card", "layout": "center", "title": "My Card", "subtitle": "Some Subtitle"}],
        "events": [{"action": "enter", "target_id": "c1", "anchor": "test"}]
    })
    with pytest.raises(ContinuousStoryEngineError) as exc_val:
        _validate_direct_authoring_contract(draft_no_val)
    assert "Card 'c1' requires non-empty direct 'display_value'." in str(exc_val.value)

    # Missing subtitle
    draft_no_sub = ContinuousStoryDraft.model_validate({
        "story_id": "test_missing_sub",
        "objects": [{"id": "c2", "type": "card", "layout": "center", "title": "My Card", "display_value": "₹10 Lakhs"}],
        "events": [{"action": "enter", "target_id": "c2", "anchor": "test"}]
    })
    with pytest.raises(ContinuousStoryEngineError) as exc_sub:
        _validate_direct_authoring_contract(draft_no_sub)
    assert "Card 'c2' requires non-empty direct 'subtitle'." in str(exc_sub.value)

    # Valid card with title, display_value, and subtitle passes
    draft_valid = ContinuousStoryDraft.model_validate({
        "story_id": "test_valid",
        "objects": [{"id": "c3", "type": "card", "layout": "center", "title": "My Card", "display_value": "₹10 Lakhs", "subtitle": "Some Subtitle"}],
        "events": [{"action": "enter", "target_id": "c3", "anchor": "test"}]
    })
    _validate_direct_authoring_contract(draft_valid)





