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
                "layout": "split_right",
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
                "to": "split_left",
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
                "to_display_value": "10.5%",
                "to_numeric_value": 10.5,
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
        "anchor": "surges to",
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


def test_exit_missing_direction_defaults_to_fade(valid_draft: ContinuousStoryDraft):
    raw = valid_draft.model_dump()
    raw["events"].append({
        "action": "exit",
        "target_id": "loan_card",
        "anchor": "surges to 49,919",
    })
    draft = ContinuousStoryDraft.model_validate(raw)
    assert draft.events[-1].direction == "fade"


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
    exit_err = next(e for e in result.errors if e.code == "EXIT_BEFORE_OBJECT_ENTER")
    assert "original enter anchor '8.5'" in exit_err.message
    assert exit_err.details["enter_anchor"] == "8.5"
    assert exit_err.details["enter_time_ms"] > exit_err.details["exit_time_ms"]
    assert "An exit anchor must occur strictly after the target object's enter anchor." in exit_err.message


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
        "points": [
            {"xLabel": "Year 0", "yValue": 0},
            {"xLabel": "Year 5", "yValue": 15},
            {"xLabel": "Year 10", "yValue": 35},
            {"xLabel": "Year 15", "yValue": 65},
            {"xLabel": "Year 20", "yValue": 100},
        ],
    })
    raw["events"].append({
        "action": "exit",
        "target_id": "loan_card",
        "anchor": "surges to",
        "direction": "left",
    })
    raw["events"].append({
        "action": "exit",
        "target_id": "rate_card",
        "anchor": "surges to",
        "direction": "fade",
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


def test_reject_chart_missing_data_fails(valid_draft: ContinuousStoryDraft):
    raw = valid_draft.model_dump()
    raw["objects"].append({
        "id": "bad_chart",
        "type": "chart",
        "purpose": "Bad chart missing both series and points",
        "layout": "full_bottom",
        "chart_type": "trajectory_area",
    })
    raw["events"].append({
        "action": "enter",
        "target_id": "bad_chart",
        "anchor": "heavy burden",
    })
    with pytest.raises(pydantic.ValidationError, match="requires directly authored 'series' or 'points'"):
        ContinuousStoryDraft.model_validate(raw)


# ----------------------------------------------------
# 12-Zone Spatial Occupancy & Collision Tests
# ----------------------------------------------------

def test_reject_zone_occupancy_collision(valid_draft: ContinuousStoryDraft, loan_fixture: dict):
    """Zone capacity allows up to 4 simultaneous elements (vertical stack); 5+ triggers collision."""
    raw = valid_draft.model_dump()
    # Add a 2nd card in split_right: allowed by multi-element auto-layout
    raw["objects"].append({
        "id": "conflicting_card",
        "type": "card",
        "purpose": "Second card in split_right",
        "layout": "split_right",
        "value_fact_id": "rate_high",
        "title": "High Rate",
    })
    raw["events"].append({
        "action": "enter",
        "target_id": "conflicting_card",
        "anchor": "8.5",
    })
    draft_two = ContinuousStoryDraft.model_validate(raw)
    result_two = validate_story_draft(
        draft=draft_two,
        approved_facts=loan_fixture["approved_facts"],
        word_timestamps=loan_fixture["word_timestamps"],
        total_duration_ms=loan_fixture["total_duration_ms"],
    )
    assert result_two.valid is True

    # Add 3rd and 4th cards in split_right: allowed up to 4 simultaneous elements
    raw["objects"].extend([
        {
            "id": "third_card",
            "type": "card",
            "purpose": "Third card in split_right",
            "layout": "split_right",
            "value_fact_id": "rate_high",
            "title": "Third Rate",
        },
        {
            "id": "fourth_card",
            "type": "card",
            "purpose": "Fourth card in split_right",
            "layout": "split_right",
            "value_fact_id": "rate_high",
            "title": "Fourth Rate",
        },
    ])
    raw["events"].extend([
        {"action": "enter", "target_id": "third_card", "anchor": "8.5"},
        {"action": "enter", "target_id": "fourth_card", "anchor": "8.5"},
    ])
    draft_four = ContinuousStoryDraft.model_validate(raw)
    result_four = validate_story_draft(
        draft=draft_four,
        approved_facts=loan_fixture["approved_facts"],
        word_timestamps=loan_fixture["word_timestamps"],
        total_duration_ms=loan_fixture["total_duration_ms"],
    )
    assert result_four.valid is True

    # Add a 5th card in split_right: exceeds capacity (max 4)
    raw["objects"].append({
        "id": "fifth_card",
        "type": "card",
        "purpose": "Fifth card in split_right",
        "layout": "split_right",
        "value_fact_id": "rate_high",
        "title": "Fifth Rate",
    })
    raw["events"].append({
        "action": "enter",
        "target_id": "fifth_card",
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


def test_validator_searches_anchor_after_card_enter_for_repeating_words():
    """Verifies that an event anchor searches after the card has entered when words repeat."""
    word_timestamps = [
        {"word": "equity", "start_ms": 1000, "end_ms": 1300},
        {"word": "catch", "start_ms": 5000, "end_ms": 5500},
        {"word": "equity", "start_ms": 8000, "end_ms": 8300},
    ]
    raw_draft = {
        "story_id": "repeat_anchor_validator_test",
        "objects": [
            {
                "id": "card_test",
                "type": "card",
                "layout": "center",
                "title": "Test Card",
                "display_value": "100",
                "numeric_value": 100,
            }
        ],
        "events": [
            {"action": "enter", "target_id": "card_test", "anchor": "catch"},
            {"action": "exit", "target_id": "card_test", "anchor": "equity"},
        ],
    }
    draft = ContinuousStoryDraft.model_validate(raw_draft)
    result = validate_story_draft(
        draft=draft,
        word_timestamps=word_timestamps,
        total_duration_ms=10000,
    )
    assert result.valid is True


def test_validator_fails_when_object_missing_explicit_enter():
    """Requirement: Every object must have an explicit enter event. Missing enter must fail validation."""
    word_timestamps = [
        {"word": "fixed", "start_ms": 100, "end_ms": 300},
        {"word": "return", "start_ms": 300, "end_ms": 600},
    ]
    raw_draft = {
        "story_id": "missing_enter_test",
        "objects": [
            {
                "id": "card_entered",
                "type": "card",
                "layout": "split_left",
                "title": "Entered Card",
                "display_value": "₹5 Lakh",
                "numeric_value": 500000,
            },
            {
                "id": "card_without_enter",
                "type": "card",
                "layout": "split_right",
                "title": "Forgotten Card",
                "display_value": "₹10 Lakh",
                "numeric_value": 1000000,
            },
        ],
        "events": [
            {"action": "enter", "target_id": "card_entered", "anchor": "fixed"},
        ],
    }
    draft = ContinuousStoryDraft.model_validate(raw_draft)
    result = validate_story_draft(
        draft=draft,
        word_timestamps=word_timestamps,
        total_duration_ms=5000,
    )
    assert result.valid is False
    assert any(e.code == "MISSING_ENTER_EVENT" and e.target_id == "card_without_enter" for e in result.errors)


def test_validator_rejects_non_contiguous_or_substring_phrase():
    """Requirement: Exact contiguous phrase matching only; substring or non-contiguous fails."""
    word_timestamps = [
        {"word": "fixed", "start_ms": 100, "end_ms": 300},
        {"word": "deposit", "start_ms": 300, "end_ms": 500},
        {"word": "scheme", "start_ms": 500, "end_ms": 800},
    ]
    raw_draft = {
        "story_id": "non_contiguous_anchor_test",
        "objects": [
            {
                "id": "test_card",
                "type": "card",
                "layout": "center",
                "title": "Deposit",
                "display_value": "100",
                "numeric_value": 100,
            }
        ],
        "events": [
            # "fixed scheme" skips "deposit" -> non-contiguous!
            {"action": "enter", "target_id": "test_card", "anchor": "fixed scheme"},
        ],
    }
    draft = ContinuousStoryDraft.model_validate(raw_draft)
    result = validate_story_draft(
        draft=draft,
        word_timestamps=word_timestamps,
        total_duration_ms=5000,
    )
    assert result.valid is False
    assert any(e.code == "ANCHOR_NOT_FOUND" for e in result.errors)


def test_anchor_word_count_allows_multi_word_verbatim_phrases(valid_draft: ContinuousStoryDraft, loan_fixture: dict):
    # 1. Multi-word anchor (4 words) -> ACCEPTED (no ANCHOR_TOO_LONG)
    raw_4_words = valid_draft.model_dump()
    raw_4_words["events"][0]["anchor"] = "starts at eight point"  # 4 words
    draft_4 = ContinuousStoryDraft.model_validate(raw_4_words)
    res_4 = validate_story_draft(
        draft=draft_4,
        approved_facts=loan_fixture["approved_facts"],
        word_timestamps=loan_fixture["word_timestamps"],
        total_duration_ms=loan_fixture["total_duration_ms"],
    )
    assert not any(e.code == "ANCHOR_TOO_LONG" for e in res_4.errors)

    # 2. Multi-word anchor (5 words) -> ACCEPTED
    raw_5_words = valid_draft.model_dump()
    raw_5_words["events"][0]["anchor"] = "home loan starts at eight"  # 5 words
    draft_5 = ContinuousStoryDraft.model_validate(raw_5_words)
    res_5 = validate_story_draft(
        draft=draft_5,
        approved_facts=loan_fixture["approved_facts"],
        word_timestamps=loan_fixture["word_timestamps"],
        total_duration_ms=loan_fixture["total_duration_ms"],
    )
    assert not any(e.code == "ANCHOR_TOO_LONG" for e in res_5.errors)

    # 3. Empty anchor -> REJECTED at schema validation
    raw_empty = valid_draft.model_dump()
    raw_empty["events"][0]["anchor"] = "   "
    with pytest.raises(pydantic.ValidationError, match="requires a non-empty spoken 'anchor'"):
        ContinuousStoryDraft.model_validate(raw_empty)


def test_mandatory_exit_rules_before_fullscreen(loan_fixture: dict):
    """Test that foreground visuals before full_screen canvas image MUST have explicit exit events."""
    raw = {
        "story_id": "missing_exit_fullscreen_test",
        "objects": [
            {
                "id": "unexited_hero",
                "type": "card",
                "layout": "center",
                "title": "Unexited Hero",
                "subtitle": "No exit before video",
                "display_value": "₹50 Lakh",
                "numeric_value": 5000000,
            },
            {
                "id": "fullscreen_img",
                "type": "image",
                "layout": "full_screen",
                "asset_id": "assets/test.png",
            },
        ],
        "events": [
            {"action": "enter", "target_id": "unexited_hero", "anchor": "50 lakh"},
            {"action": "enter", "target_id": "fullscreen_img", "anchor": "rate rises", "style": "cut"},
            {"action": "exit", "target_id": "fullscreen_img", "anchor": "heavy burden", "direction": "cut"},
        ],
    }
    draft = ContinuousStoryDraft.model_validate(raw)
    res = validate_story_draft(
        draft=draft,
        approved_facts=loan_fixture["approved_facts"],
        word_timestamps=loan_fixture["word_timestamps"],
        total_duration_ms=loan_fixture["total_duration_ms"],
        available_assets=["assets/test.png"],
    )
    assert res.valid is False
    assert any(e.code == "MISSING_EXIT_BEFORE_FULLSCREEN" for e in res.errors)

    # Adding explicit exit fixes it
    raw["events"].insert(1, {
        "action": "exit",
        "target_id": "unexited_hero",
        "anchor": "rate rises",
        "direction": "cut",
    })
    draft_fixed = ContinuousStoryDraft.model_validate(raw)
    res_fixed = validate_story_draft(
        draft=draft_fixed,
        approved_facts=loan_fixture["approved_facts"],
        word_timestamps=loan_fixture["word_timestamps"],
        total_duration_ms=loan_fixture["total_duration_ms"],
        available_assets=["assets/test.png"],
    )
    assert not any(e.code == "MISSING_EXIT_BEFORE_FULLSCREEN" for e in res_fixed.errors)


def test_stock_video_cutaway_does_not_require_exit_before_enter(loan_fixture: dict):
    """Test that stock_video is a Cutaway B-Roll Layer and does NOT require preceding canvas visuals to exit."""
    raw = {
        "story_id": "stock_video_cutaway_continuity_test",
        "objects": [
            {
                "id": "hero_character",
                "type": "character",
                "layout": "split_left",
                "role": "investigator",
                "character_style": "futuristic_stick",
                "pose": "idle",
                "facing": "right",
            },
            {
                "id": "broll_video",
                "type": "stock_video",
                "layout": "full_screen",
                "asset_id": "assets/test.mp4",
            },
        ],
        "events": [
            # Character stays alive across the stock video cutaway!
            {"action": "enter", "target_id": "hero_character", "anchor": "50 lakh"},
            {"action": "exit", "target_id": "hero_character", "anchor": "20 years", "direction": "fade"},
            {"action": "enter", "target_id": "broll_video", "anchor": "rate rises", "style": "cut"},
            {"action": "exit", "target_id": "broll_video", "anchor": "heavy burden", "direction": "cut"},
        ],
    }
    draft = ContinuousStoryDraft.model_validate(raw)
    res = validate_story_draft(
        draft=draft,
        approved_facts=loan_fixture["approved_facts"],
        word_timestamps=loan_fixture["word_timestamps"],
        total_duration_ms=loan_fixture["total_duration_ms"],
        available_assets=["assets/test.mp4"],
    )
    assert res.valid is True
    assert len(res.errors) == 0


def test_low_visual_density_enforcement(loan_fixture: dict):
    """Test that videos >= 45s enforce minimum event cadence (at least 1 event every 3 seconds)."""
    # 5 events for a 60-second video (requires floor(60/3) = 20 events)
    raw = {
        "story_id": "low_density_test",
        "objects": [
            {
                "id": "card_test",
                "type": "card",
                "layout": "center",
                "title": "Test Card",
                "subtitle": "Testing density",
                "display_value": "₹50 Lakh",
                "numeric_value": 5000000,
            }
        ],
        "events": [
            {"action": "enter", "target_id": "card_test", "anchor": "50 lakh"},
        ],
    }
    draft = ContinuousStoryDraft.model_validate(raw)

    # 1. total_duration_ms = 60,000ms (60s) -> requires 20 events -> fails with LOW_VISUAL_DENSITY
    res = validate_story_draft(
        draft=draft,
        approved_facts=loan_fixture["approved_facts"],
        word_timestamps=loan_fixture["word_timestamps"],
        total_duration_ms=60000,
    )
    assert res.valid is False
    assert any(e.code == "LOW_VISUAL_DENSITY" for e in res.errors)
    density_err = next(e for e in res.errors if e.code == "LOW_VISUAL_DENSITY")
    assert density_err.details["required_events"] == 20
    assert density_err.details["actual_events"] == 1

    # 2. total_duration_ms = 20,000ms (<45s micro-fixture) -> check is not triggered
    res_short = validate_story_draft(
        draft=draft,
        approved_facts=loan_fixture["approved_facts"],
        word_timestamps=loan_fixture["word_timestamps"],
        total_duration_ms=20000,
    )
    assert not any(e.code == "LOW_VISUAL_DENSITY" for e in res_short.errors)


def test_sequential_zone_handoff_clamping():
    """Test that a short transition overlap (<=2000ms) between an exiting and entering element in full_bottom is clamped cleanly."""
    word_timestamps = [
        {"word": "first", "start_ms": 0, "end_ms": 500},
        {"word": "handoff", "start_ms": 5000, "end_ms": 5500},
        {"word": "exit_word", "start_ms": 6200, "end_ms": 6700},
        {"word": "end", "start_ms": 10000, "end_ms": 10500},
    ]

    # Chart 1 enters at 0ms, exits at 6200ms (clearance to 6800ms)
    # Chart 2 enters at 5500ms (overlap is 6800 - 5500 = 1300ms <= 2000ms)
    raw = {
        "story_id": "handoff_clamping_test",
        "objects": [
            {
                "id": "chart_first",
                "type": "chart",
                "chart_type": "trajectory_area",
                "layout": "full_bottom",
                "title": "First Chart",
                "series": [{"label": "Data", "points": [{"x": 1, "y": 10}]}],
            },
            {
                "id": "chart_second",
                "type": "chart",
                "chart_type": "trajectory_area",
                "layout": "full_bottom",
                "title": "Second Chart",
                "series": [{"label": "Data", "points": [{"x": 1, "y": 20}]}],
            },
        ],
        "events": [
            {"action": "enter", "target_id": "chart_first", "anchor": "first"},
            {"action": "enter", "target_id": "chart_second", "anchor": "handoff"},
            {"action": "exit", "target_id": "chart_first", "anchor": "exit_word"},
            {"action": "exit", "target_id": "chart_second", "anchor": "end"},
        ],
    }
    draft = ContinuousStoryDraft.model_validate(raw)

    res = validate_story_draft(
        draft=draft,
        approved_facts={},
        word_timestamps=word_timestamps,
        total_duration_ms=12000,
    )
    # Clamping resolves the 1.3s handoff, so NO ZONE_OCCUPANCY_COLLISION
    assert not any(e.code == "ZONE_OCCUPANCY_COLLISION" for e in res.errors)


def test_chronological_anchor_resolution_avoids_backward_jump():
    """
    When narration contains repeated phrases (e.g. 'late 2024' at 2s and 60s),
    an event authored late in the draft should resolve to the late occurrence,
    avoiding false zone collisions or exit-before-enter errors.
    """
    word_timestamps = [
        {"word": "intro", "start_ms": 1000, "end_ms": 1500},
        {"word": "late", "start_ms": 2000, "end_ms": 2500},
        {"word": "2024", "start_ms": 2500, "end_ms": 3000},
        {"word": "first", "start_ms": 4000, "end_ms": 4500},
        {"word": "middle", "start_ms": 50000, "end_ms": 50500},
        {"word": "late", "start_ms": 60000, "end_ms": 60500},
        {"word": "2024", "start_ms": 60500, "end_ms": 61000},
        {"word": "conclusion", "start_ms": 70000, "end_ms": 70500},
    ]

    raw = {
        "story_id": "test_chronological",
        "objects": [
            {
                "id": "card_intro",
                "type": "card",
                "layout": "split_left",
                "title": "Intro Card",
            },
            {
                "id": "card_late",
                "type": "card",
                "layout": "split_left",
                "title": "Late Card",
            },
        ],
        "events": [
            {"action": "enter", "target_id": "card_intro", "anchor": "intro"},
            {"action": "exit", "target_id": "card_intro", "anchor": "first"},
            {"action": "enter", "target_id": "card_late", "anchor": "late 2024"},
            {"action": "exit", "target_id": "card_late", "anchor": "conclusion"},
        ],
    }
    draft = ContinuousStoryDraft.model_validate(raw)
    res = validate_story_draft(
        draft=draft,
        approved_facts={},
        word_timestamps=word_timestamps,
        total_duration_ms=75000,
    )
    # card_late must resolve to 60,000ms, not 2,000ms.
    # Therefore it does not overlap with card_intro (1000ms - 4000ms), and no collisions occur.
    assert not any(e.code == "ZONE_OCCUPANCY_COLLISION" for e in res.errors)
    assert not any(e.code == "EXIT_BEFORE_OBJECT_ENTER" for e in res.errors)








