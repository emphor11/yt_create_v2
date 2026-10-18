"""
test_continuous_story_draft_validator.py — Automated Unit Tests for AI Draft Validator.
"""
from __future__ import annotations

import json
from pathlib import Path
import pydantic
import pytest

from domain.continuous_story_plan import ContinuousStoryDraft
from engines.continuous_story_draft_validator import validate_story_draft


@pytest.fixture
def loan_fixture() -> dict:
    fixture_path = Path(__file__).resolve().parent.parent / "fixtures" / "loan_story_fixture.json"
    with open(fixture_path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def valid_draft() -> ContinuousStoryDraft:
    raw = {
        "story_id": "loan_rate_hike",
        "objects": [
            {
                "id": "loan_card",
                "type": "card",
                "purpose": "show the original loan",
                "layout": "center",
                "value_fact_id": "loan_principal",
                "title": "Home Loan Principal",
            },
            {
                "id": "rate_card",
                "type": "card",
                "purpose": "show interest rate container",
                "layout": "center_right",
                "value_fact_id": "rate_baseline",
                "title": "Interest Rate",
            },
            {
                "id": "flow_conn",
                "type": "connector",
                "purpose": "connect loan card to rate card",
                "from_id": "loan_card",
                "to_id": "rate_card",
                "label": "Drives payment",
            },
        ],
        "events": [
            {
                "action": "enter",
                "target_id": "loan_card",
                "anchor": "50 lakh",
            },
            {
                "action": "move",
                "target_id": "loan_card",
                "anchor": "starts at",
                "to": "center_left",
            },
            {
                "action": "enter",
                "target_id": "rate_card",
                "anchor": "8.5",
            },
            {
                "action": "connect",
                "target_id": "flow_conn",
                "anchor": "percent",
            },
            {
                "action": "transform_number",
                "target_id": "rate_card",
                "anchor": "rises to 10.5",
                "to_fact_id": "rate_high",
            },
        ],
    }
    return ContinuousStoryDraft.model_validate(raw)


def test_valid_draft_passes(valid_draft: ContinuousStoryDraft, loan_fixture: dict):
    result = validate_story_draft(
        draft=valid_draft,
        approved_facts=loan_fixture["approved_facts"],
        word_timestamps=loan_fixture["word_timestamps"],
        total_duration_ms=loan_fixture["total_duration_ms"],
    )
    assert result.valid is True
    assert len(result.errors) == 0


def test_reject_parent_id_forbidden():
    raw = {
        "story_id": "bad",
        "objects": [
            {
                "id": "c",
                "type": "card",
                "layout": "center",
                "parent_id": "something",
            }
        ],
        "events": [],
    }
    with pytest.raises(pydantic.ValidationError, match="extra_forbidden"):
        ContinuousStoryDraft.model_validate(raw)


def test_reject_unexpected_to_fact_id_on_non_transform(valid_draft: ContinuousStoryDraft, loan_fixture: dict):
    raw = valid_draft.model_dump()
    raw["events"][0]["to_fact_id"] = "emi_high"  # action is "enter"
    draft = ContinuousStoryDraft.model_validate(raw)

    result = validate_story_draft(
        draft=draft,
        approved_facts=loan_fixture["approved_facts"],
        word_timestamps=loan_fixture["word_timestamps"],
        total_duration_ms=loan_fixture["total_duration_ms"],
    )
    assert result.valid is False
    codes = [e.code for e in result.errors]
    assert "UNEXPECTED_TO_FACT_ID" in codes


def test_reject_transform_number_non_numeric_fact(valid_draft: ContinuousStoryDraft, loan_fixture: dict):
    facts = dict(loan_fixture["approved_facts"])
    facts["bad_str_fact"] = {"value": "ten_percent"}

    raw = valid_draft.model_dump()
    raw["events"][4]["to_fact_id"] = "bad_str_fact"
    draft = ContinuousStoryDraft.model_validate(raw)

    result = validate_story_draft(
        draft=draft,
        approved_facts=facts,
        word_timestamps=loan_fixture["word_timestamps"],
        total_duration_ms=loan_fixture["total_duration_ms"],
    )
    assert result.valid is False
    codes = [e.code for e in result.errors]
    assert "NON_NUMERIC_TRANSFORM_FACT" in codes


def test_timestamp_range_negative_start(valid_draft: ContinuousStoryDraft, loan_fixture: dict):
    words = [{"word": "A", "start_ms": -50, "end_ms": 100}]
    result = validate_story_draft(
        draft=valid_draft,
        approved_facts=loan_fixture["approved_facts"],
        word_timestamps=words,
        total_duration_ms=1000,
    )
    codes = [e.code for e in result.errors]
    assert "NEGATIVE_TIMESTAMP" in codes


def test_timestamp_range_end_before_start(valid_draft: ContinuousStoryDraft, loan_fixture: dict):
    words = [{"word": "A", "start_ms": 200, "end_ms": 100}]
    result = validate_story_draft(
        draft=valid_draft,
        approved_facts=loan_fixture["approved_facts"],
        word_timestamps=words,
        total_duration_ms=1000,
    )
    codes = [e.code for e in result.errors]
    assert "INVALID_TIMESTAMP_RANGE" in codes


def test_timestamp_exceeds_audio_duration(valid_draft: ContinuousStoryDraft, loan_fixture: dict):
    words = [{"word": "A", "start_ms": 0, "end_ms": 12600}]
    result = validate_story_draft(
        draft=valid_draft,
        approved_facts=loan_fixture["approved_facts"],
        word_timestamps=words,
        total_duration_ms=12543,
    )
    codes = [e.code for e in result.errors]
    assert "TIMESTAMP_EXCEEDS_AUDIO_DURATION" in codes


def test_timestamp_monotonicity(valid_draft: ContinuousStoryDraft, loan_fixture: dict):
    words = [
        {"word": "A", "start_ms": 100, "end_ms": 200},
        {"word": "loan", "start_ms": 80, "end_ms": 250},
    ]
    result = validate_story_draft(
        draft=valid_draft,
        approved_facts=loan_fixture["approved_facts"],
        word_timestamps=words,
        total_duration_ms=1000,
    )
    codes = [e.code for e in result.errors]
    assert "NON_MONOTONIC_WORD_TIMESTAMPS" in codes


def test_trailing_silence_is_allowed(valid_draft: ContinuousStoryDraft, loan_fixture: dict):
    result = validate_story_draft(
        draft=valid_draft,
        approved_facts=loan_fixture["approved_facts"],
        word_timestamps=loan_fixture["word_timestamps"],
        total_duration_ms=loan_fixture["total_duration_ms"],
    )
    timestamp_errors = [e for e in result.errors if "TIMESTAMP" in e.code]
    assert len(timestamp_errors) == 0


def test_reject_connect_before_cards_enter(valid_draft: ContinuousStoryDraft, loan_fixture: dict):
    raw = valid_draft.model_dump()
    # rate_card enters at '8.5' (2680ms). Try connecting at '50 lakh' (335ms) before rate_card enters:
    raw["events"][3]["anchor"] = "50 lakh"  # 'connect' event
    draft = ContinuousStoryDraft.model_validate(raw)

    result = validate_story_draft(
        draft=draft,
        approved_facts=loan_fixture["approved_facts"],
        word_timestamps=loan_fixture["word_timestamps"],
        total_duration_ms=loan_fixture["total_duration_ms"],
    )
    assert result.valid is False
    codes = [e.code for e in result.errors]
    assert "CONNECT_BEFORE_CARDS_ENTER" in codes


def test_reject_transform_before_card_enters(valid_draft: ContinuousStoryDraft, loan_fixture: dict):
    raw = valid_draft.model_dump()
    # rate_card enters at '8.5' (2680ms). Try transforming at '50 lakh' (335ms):
    raw["events"][4]["anchor"] = "50 lakh"  # 'transform_number' on rate_card
    draft = ContinuousStoryDraft.model_validate(raw)

    result = validate_story_draft(
        draft=draft,
        approved_facts=loan_fixture["approved_facts"],
        word_timestamps=loan_fixture["word_timestamps"],
        total_duration_ms=loan_fixture["total_duration_ms"],
    )
    assert result.valid is False
    codes = [e.code for e in result.errors]
    assert "ACTION_BEFORE_OBJECT_ENTER" in codes


def test_reject_move_before_enter(valid_draft: ContinuousStoryDraft, loan_fixture: dict):
    raw = valid_draft.model_dump()
    # loan_card enters at 'starts at' (2010ms), but tries to move at '50 lakh' (335ms):
    raw["events"][0]["anchor"] = "starts at"  # enter loan_card
    raw["events"][1]["anchor"] = "50 lakh"    # move loan_card BEFORE entering!
    draft = ContinuousStoryDraft.model_validate(raw)

    result = validate_story_draft(
        draft=draft,
        approved_facts=loan_fixture["approved_facts"],
        word_timestamps=loan_fixture["word_timestamps"],
        total_duration_ms=loan_fixture["total_duration_ms"],
    )
    assert result.valid is False
    codes = [e.code for e in result.errors]
    assert "ACTION_BEFORE_OBJECT_ENTER" in codes


def test_valid_change_visual_state(valid_draft: ContinuousStoryDraft, loan_fixture: dict):
    raw = valid_draft.model_dump()
    raw["events"].append({
        "action": "change_visual_state",
        "target_id": "rate_card",
        "anchor": "rises to 10.5",
        "state": "warning",
        "badge": "+2.0% HIKE",
    })
    draft = ContinuousStoryDraft.model_validate(raw)

    result = validate_story_draft(
        draft=draft,
        approved_facts=loan_fixture["approved_facts"],
        word_timestamps=loan_fixture["word_timestamps"],
        total_duration_ms=loan_fixture["total_duration_ms"],
    )
    assert result.valid is True


def test_reject_change_visual_state_before_card_enters(valid_draft: ContinuousStoryDraft, loan_fixture: dict):
    raw = valid_draft.model_dump()
    raw["events"].append({
        "action": "change_visual_state",
        "target_id": "rate_card",
        "anchor": "50 lakh",  # Before rate_card enters!
        "state": "warning",
    })
    draft = ContinuousStoryDraft.model_validate(raw)

    result = validate_story_draft(
        draft=draft,
        approved_facts=loan_fixture["approved_facts"],
        word_timestamps=loan_fixture["word_timestamps"],
        total_duration_ms=loan_fixture["total_duration_ms"],
    )
    assert result.valid is False
    codes = [e.code for e in result.errors]
    assert "ACTION_BEFORE_OBJECT_ENTER" in codes


def test_reject_invalid_badge(valid_draft: ContinuousStoryDraft, loan_fixture: dict):
    # Empty badge
    raw_empty = valid_draft.model_dump()
    raw_empty["events"].append({
        "action": "change_visual_state",
        "target_id": "rate_card",
        "anchor": "rises to 10.5",
        "state": "warning",
        "badge": "   ",
    })
    draft_empty = ContinuousStoryDraft.model_validate(raw_empty)
    res_empty = validate_story_draft(
        draft=draft_empty,
        approved_facts=loan_fixture["approved_facts"],
        word_timestamps=loan_fixture["word_timestamps"],
    )
    assert res_empty.valid is False
    assert "EMPTY_BADGE" in [e.code for e in res_empty.errors]


def test_valid_exit_action(valid_draft: ContinuousStoryDraft, loan_fixture: dict):
    raw = valid_draft.model_dump()
    raw["events"].append({
        "action": "exit",
        "target_id": "loan_card",
        "anchor": "surges to 49,919",
        "direction": "left",
    })
    draft = ContinuousStoryDraft.model_validate(raw)

    result = validate_story_draft(
        draft=draft,
        approved_facts=loan_fixture["approved_facts"],
        word_timestamps=loan_fixture["word_timestamps"],
        total_duration_ms=loan_fixture["total_duration_ms"],
    )
    assert result.valid is True


def test_reject_exit_missing_direction(valid_draft: ContinuousStoryDraft):
    raw = valid_draft.model_dump()
    raw["events"].append({
        "action": "exit",
        "target_id": "loan_card",
        "anchor": "surges to 49,919",
    })
    with pytest.raises(pydantic.ValidationError, match="requires 'direction'"):
        ContinuousStoryDraft.model_validate(raw)


def test_reject_exit_before_object_enters(valid_draft: ContinuousStoryDraft, loan_fixture: dict):
    raw = valid_draft.model_dump()
    raw["events"].append({
        "action": "exit",
        "target_id": "rate_card",
        "anchor": "50 lakh",  # exits before entering!
        "direction": "left",
    })
    draft = ContinuousStoryDraft.model_validate(raw)

    result = validate_story_draft(
        draft=draft,
        approved_facts=loan_fixture["approved_facts"],
        word_timestamps=loan_fixture["word_timestamps"],
        total_duration_ms=loan_fixture["total_duration_ms"],
    )
    assert result.valid is False
    codes = [e.code for e in result.errors]
    assert "EXIT_BEFORE_OBJECT_ENTER" in codes


def test_valid_chart_draft(valid_draft: ContinuousStoryDraft, loan_fixture: dict):
    raw = valid_draft.model_dump()
    raw["objects"].append({
        "id": "chart_trajectory",
        "type": "chart",
        "purpose": "20-year extra interest trajectory",
        "layout": "full_bottom",
        "fact_id": "loan_interest_trajectory",
        "chart_type": "trajectory_area",
        "title": "20-Year Extra Interest Trajectory",
    })
    raw["events"].append({
        "action": "enter",
        "target_id": "chart_trajectory",
        "anchor": "heavy burden",
    })
    draft = ContinuousStoryDraft.model_validate(raw)
    result = validate_story_draft(
        draft=draft,
        approved_facts=loan_fixture["approved_facts"],
        word_timestamps=loan_fixture["word_timestamps"],
        total_duration_ms=loan_fixture["total_duration_ms"],
    )
    assert result.valid is True
    assert len(result.errors) == 0


def test_reject_chart_invalid_fact(valid_draft: ContinuousStoryDraft, loan_fixture: dict):
    raw = valid_draft.model_dump()
    raw["objects"].append({
        "id": "bad_chart",
        "type": "chart",
        "purpose": "Bad chart pointing to numeric scalar fact",
        "layout": "full_bottom",
        "fact_id": "rate_baseline",
        "chart_type": "trajectory_area",
    })
    raw["events"].append({
        "action": "enter",
        "target_id": "bad_chart",
        "anchor": "heavy burden",
    })
    draft = ContinuousStoryDraft.model_validate(raw)
    result = validate_story_draft(
        draft=draft,
        approved_facts=loan_fixture["approved_facts"],
        word_timestamps=loan_fixture["word_timestamps"],
        total_duration_ms=loan_fixture["total_duration_ms"],
    )
    assert result.valid is False
    codes = [e.code for e in result.errors]
    assert "INVALID_CHART_FACT" in codes


# ----------------------------------------------------
# 12-Zone Spatial Occupancy & Collision Tests
# ----------------------------------------------------

def test_reject_zone_occupancy_collision(valid_draft: ContinuousStoryDraft, loan_fixture: dict):
    """Cannot place two active surfaces into the exact same zone simultaneously."""
    raw = valid_draft.model_dump()
    # Add another card also in 'center_right' entering at '8.5' without rate_card exiting
    raw["objects"].append({
        "id": "conflicting_card",
        "type": "card",
        "purpose": "Colliding card",
        "layout": "center_right",  # Already occupied by rate_card!
        "value_fact_id": "rate_high",
        "title": "High Rate",
    })
    raw["events"].append({
        "action": "enter",
        "target_id": "conflicting_card",
        "anchor": "8.5",
    })
    draft = ContinuousStoryDraft.model_validate(raw)
    result = validate_story_draft(
        draft=draft,
        approved_facts=loan_fixture["approved_facts"],
        word_timestamps=loan_fixture["word_timestamps"],
        total_duration_ms=loan_fixture["total_duration_ms"],
    )
    assert result.valid is False
    codes = [e.code for e in result.errors]
    assert "ZONE_OCCUPANCY_COLLISION" in codes


def test_zone_occupancy_allowed_after_exit(valid_draft: ContinuousStoryDraft, loan_fixture: dict):
    """A zone CAN be reused after the previous occupant has fully completed its exit."""
    raw = valid_draft.model_dump()
    # loan_card exits at 'starts at'
    raw["events"].append({
        "action": "exit",
        "target_id": "loan_card",
        "anchor": "starts at",
        "direction": "left",
    })
    # New card enters into freed 'center' zone at 'benchmark rate' (well after exit clears)
    raw["objects"].append({
        "id": "new_hero_card",
        "type": "card",
        "purpose": "New Hero",
        "layout": "center",
        "value_fact_id": "total_extra_interest",
        "title": "Extra Cost",
    })
    raw["events"].append({
        "action": "enter",
        "target_id": "new_hero_card",
        "anchor": "benchmark rate",
    })
    draft = ContinuousStoryDraft.model_validate(raw)
    result = validate_story_draft(
        draft=draft,
        approved_facts=loan_fixture["approved_facts"],
        word_timestamps=loan_fixture["word_timestamps"],
        total_duration_ms=loan_fixture["total_duration_ms"],
    )
    assert result.valid is True
