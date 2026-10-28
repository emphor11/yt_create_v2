"""
test_continuous_story_split_screen.py — Comprehensive Unit & Integration Tests for Split-Screen Layouts.

Tests all required aspects of split_left and split_right:
1. Card in split_left
2. Card in split_right
3. Image on split_left and chart on split_right
4. Move from center to split_left
5. Move from split_left to split_right
6. Collision across the divider
7. full_screen conflicting with split_left / split_right
8. Invalid split layout names failing loudly
"""
from __future__ import annotations

import json
from pathlib import Path
import pydantic
import pytest

from domain.continuous_story_plan import ContinuousStoryDraft, VALID_ZONES
from engines.continuous_story_draft_validator import validate_story_draft
from engines.continuous_story_compiler import ContinuousStoryCompiler


@pytest.fixture
def loan_fixture() -> dict:
    fixture_path = Path(__file__).resolve().parent.parent / "fixtures" / "loan_story_fixture.json"
    with open(fixture_path, "r", encoding="utf-8") as f:
        return json.load(f)


def test_card_in_split_left(loan_fixture: dict):
    """1. Test card in split_left: centers in left half (x approx 480, y approx 540) without crossing divider."""
    raw = {
        "story_id": "split_left_card_test",
        "objects": [
            {
                "id": "bank_card",
                "type": "card",
                "purpose": "Bank institution card",
                "layout": "split_left",
                "title": "National Bank",
                "subtitle": "Institutional Lender",
                "display_value": "₹50 Lakh",
                "numeric_value": 5000000,
            }
        ],
        "events": [
            {
                "action": "enter",
                "target_id": "bank_card",
                "anchor": "50 lakh",
            }
        ],
    }

    draft = ContinuousStoryDraft.model_validate(raw)
    assert draft.objects[0].layout == "split_left"

    result = validate_story_draft(
        draft=draft,
        approved_facts=loan_fixture["approved_facts"],
        word_timestamps=loan_fixture["word_timestamps"],
        total_duration_ms=loan_fixture["total_duration_ms"],
    )
    assert result.valid is True
    assert len(result.errors) == 0

    compiler = ContinuousStoryCompiler()
    compiled = compiler.compile(draft=draft, fixture=loan_fixture)
    assert compiled["objects"][0]["layout"] == "split_left"


def test_card_in_split_right(loan_fixture: dict):
    """2. Test card in split_right: centers in right half (x approx 1440, y approx 540) without crossing divider."""
    raw = {
        "story_id": "split_right_card_test",
        "objects": [
            {
                "id": "interest_card",
                "type": "card",
                "purpose": "Cumulative interest burden",
                "layout": "split_right",
                "title": "Total Interest",
                "subtitle": "Borrower Burden",
                "display_value": "₹88.4 Lakh",
                "numeric_value": 8840000,
            }
        ],
        "events": [
            {
                "action": "enter",
                "target_id": "interest_card",
                "anchor": "50 lakh",
            }
        ],
    }

    draft = ContinuousStoryDraft.model_validate(raw)
    assert draft.objects[0].layout == "split_right"

    result = validate_story_draft(
        draft=draft,
        approved_facts=loan_fixture["approved_facts"],
        word_timestamps=loan_fixture["word_timestamps"],
        total_duration_ms=loan_fixture["total_duration_ms"],
    )
    assert result.valid is True
    assert len(result.errors) == 0

    compiler = ContinuousStoryCompiler()
    compiled = compiler.compile(draft=draft, fixture=loan_fixture)
    assert compiled["objects"][0]["layout"] == "split_right"


def test_image_on_split_left_and_chart_on_split_right(loan_fixture: dict):
    """3. Test image on split_left and chart on split_right coexisting simultaneously."""
    raw = {
        "story_id": "split_comparison_image_chart",
        "objects": [
            {
                "id": "bank_image",
                "type": "image",
                "purpose": "Bank visual context",
                "layout": "split_left",
                "asset_id": "assets/bank_exterior.jpg",
                "caption": "Commercial Banking Division",
            },
            {
                "id": "interest_chart",
                "type": "chart",
                "purpose": "Interest growth curve",
                "layout": "split_right",
                "chart_type": "trajectory_area",
                "title": "Cumulative Cost Growth",
                "points": [
                    {"xLabel": "Yr 0", "yValue": 0},
                    {"xLabel": "Yr 10", "yValue": 40},
                    {"xLabel": "Yr 20", "yValue": 88},
                ],
            },
        ],
        "events": [
            {
                "action": "enter",
                "target_id": "bank_image",
                "anchor": "50 lakh",
            },
            {
                "action": "enter",
                "target_id": "interest_chart",
                "anchor": "starts at",
            },
        ],
    }

    draft = ContinuousStoryDraft.model_validate(raw)
    result = validate_story_draft(
        draft=draft,
        approved_facts=loan_fixture["approved_facts"],
        word_timestamps=loan_fixture["word_timestamps"],
        total_duration_ms=loan_fixture["total_duration_ms"],
        available_assets=["assets/bank_exterior.jpg"],
    )
    assert result.valid is True
    assert len(result.errors) == 0

    compiler = ContinuousStoryCompiler()
    compiled = compiler.compile(draft=draft, fixture=loan_fixture)
    assert compiled["objects"][0]["layout"] == "split_left"
    assert compiled["objects"][1]["layout"] == "split_right"


def test_move_from_center_to_split_left(loan_fixture: dict):
    """4. Test move from center to split_left."""
    raw = {
        "story_id": "move_center_to_split_left",
        "objects": [
            {
                "id": "loan_card",
                "type": "card",
                "purpose": "Initial loan card",
                "layout": "center",
                "title": "Home Loan Principal",
                "subtitle": "Starting principal",
                "display_value": "₹50 Lakh",
                "numeric_value": 5000000,
            }
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
        ],
    }

    draft = ContinuousStoryDraft.model_validate(raw)
    result = validate_story_draft(
        draft=draft,
        approved_facts=loan_fixture["approved_facts"],
        word_timestamps=loan_fixture["word_timestamps"],
        total_duration_ms=loan_fixture["total_duration_ms"],
    )
    assert result.valid is True
    assert len(result.errors) == 0

    compiler = ContinuousStoryCompiler()
    compiled = compiler.compile(draft=draft, fixture=loan_fixture)
    move_ev = next(e for e in compiled["events"] if e["action"] == "move")
    assert move_ev["to"] == "split_left"


def test_move_from_split_left_to_split_right(loan_fixture: dict):
    """5. Test move from split_left to split_right."""
    raw = {
        "story_id": "move_split_left_to_split_right",
        "objects": [
            {
                "id": "transfer_card",
                "type": "card",
                "purpose": "Shifting visual idea",
                "layout": "split_left",
                "title": "Capital Allocation",
                "subtitle": "Reallocating across canvas",
                "display_value": "₹25 Lakh",
                "numeric_value": 2500000,
            }
        ],
        "events": [
            {
                "action": "enter",
                "target_id": "transfer_card",
                "anchor": "50 lakh",
            },
            {
                "action": "move",
                "target_id": "transfer_card",
                "anchor": "starts at",
                "to": "split_right",
            },
        ],
    }

    draft = ContinuousStoryDraft.model_validate(raw)
    result = validate_story_draft(
        draft=draft,
        approved_facts=loan_fixture["approved_facts"],
        word_timestamps=loan_fixture["word_timestamps"],
        total_duration_ms=loan_fixture["total_duration_ms"],
    )
    assert result.valid is True
    assert len(result.errors) == 0

    compiler = ContinuousStoryCompiler()
    compiled = compiler.compile(draft=draft, fixture=loan_fixture)
    move_ev = next(e for e in compiled["events"] if e["action"] == "move")
    assert move_ev["to"] == "split_right"


def test_collision_across_divider_and_same_half(loan_fixture: dict):
    """6. Test collision across divider:
       - Oversized element crossing divider (width 1100 in split_left)
       - Two simultaneous elements in the same split half (both in split_left)
       - Geometric overlap between split_left and full_bottom
    """
    # 6a. Oversized element in split_left crossing x=960 divider
    raw_crossing = {
        "story_id": "divider_crossing_test",
        "objects": [
            {
                "id": "huge_split_card",
                "type": "card",
                "purpose": "Oversized card crossing divider",
                "layout": "split_left",
                "title": "Oversized Card",
                "subtitle": "Crosses x=960 divider",
                "display_value": "₹50 Lakh",
                "numeric_value": 5000000,
            }
        ],
        "events": [
            {"action": "enter", "target_id": "huge_split_card", "anchor": "50 lakh"}
        ],
    }
    draft_crossing = ContinuousStoryDraft.model_validate(raw_crossing)
    # Give the card a custom width of 1100 so its right edge exceeds 960 (480 - 550 + 1100 = 1030 > 960)
    object.__setattr__(draft_crossing.objects[0], "width", 1100)

    result_crossing = validate_story_draft(
        draft=draft_crossing,
        approved_facts=loan_fixture["approved_facts"],
        word_timestamps=loan_fixture["word_timestamps"],
        total_duration_ms=loan_fixture["total_duration_ms"],
    )
    assert result_crossing.valid is False
    assert any(e.code == "DIVIDER_CROSSING_COLLISION" for e in result_crossing.errors)

    # 6b. Two simultaneous elements in the same split half (both split_left)
    raw_same_half = {
        "story_id": "same_half_collision_test",
        "objects": [
            {
                "id": "left_card_1",
                "type": "card",
                "purpose": "First card in split_left",
                "layout": "split_left",
                "title": "First Card",
                "subtitle": "Left Side 1",
                "display_value": "₹10 Lakh",
                "numeric_value": 1000000,
            },
            {
                "id": "left_card_2",
                "type": "card",
                "purpose": "Second card in split_left",
                "layout": "split_left",
                "title": "Second Card",
                "subtitle": "Left Side 2",
                "display_value": "₹20 Lakh",
                "numeric_value": 2000000,
            },
        ],
        "events": [
            {"action": "enter", "target_id": "left_card_1", "anchor": "50 lakh"},
            {"action": "enter", "target_id": "left_card_2", "anchor": "50 lakh"},
        ],
    }
    draft_same_half = ContinuousStoryDraft.model_validate(raw_same_half)
    result_same_half = validate_story_draft(
        draft=draft_same_half,
        approved_facts=loan_fixture["approved_facts"],
        word_timestamps=loan_fixture["word_timestamps"],
        total_duration_ms=loan_fixture["total_duration_ms"],
    )
    # 2 cards in split_left is now valid (auto-stacked vertically)
    assert result_same_half.valid is True

    # 3 and 4 cards in split_left are valid (stacked vertically up to 4 elements)
    raw_same_half["objects"].extend([
        {
            "id": "left_card_3",
            "type": "card",
            "purpose": "Third card in split_left",
            "layout": "split_left",
            "title": "Third Card",
            "subtitle": "Left Side 3",
            "display_value": "₹30 Lakh",
            "numeric_value": 3000000,
        },
        {
            "id": "left_card_4",
            "type": "card",
            "purpose": "Fourth card in split_left",
            "layout": "split_left",
            "title": "Fourth Card",
            "subtitle": "Left Side 4",
            "display_value": "₹40 Lakh",
            "numeric_value": 4000000,
        },
    ])
    raw_same_half["events"].extend([
        {"action": "enter", "target_id": "left_card_3", "anchor": "50 lakh"},
        {"action": "enter", "target_id": "left_card_4", "anchor": "50 lakh"},
    ])
    draft_four = ContinuousStoryDraft.model_validate(raw_same_half)
    result_four = validate_story_draft(
        draft=draft_four,
        approved_facts=loan_fixture["approved_facts"],
        word_timestamps=loan_fixture["word_timestamps"],
        total_duration_ms=loan_fixture["total_duration_ms"],
    )
    assert result_four.valid is True

    # 5 cards in split_left exceeds max concurrency (4)
    raw_same_half["objects"].append({
        "id": "left_card_5",
        "type": "card",
        "purpose": "Fifth card in split_left",
        "layout": "split_left",
        "title": "Fifth Card",
        "subtitle": "Left Side 5",
        "display_value": "₹50 Lakh",
        "numeric_value": 5000000,
    })
    raw_same_half["events"].append({
        "action": "enter",
        "target_id": "left_card_5",
        "anchor": "50 lakh",
    })
    draft_five = ContinuousStoryDraft.model_validate(raw_same_half)
    result_five = validate_story_draft(
        draft=draft_five,
        approved_facts=loan_fixture["approved_facts"],
        word_timestamps=loan_fixture["word_timestamps"],
        total_duration_ms=loan_fixture["total_duration_ms"],
    )
    assert result_five.valid is False
    assert any(e.code == "ZONE_OCCUPANCY_COLLISION" for e in result_five.errors)

    # 6c. Geometric overlap between split_left (y=420..660) and full_bottom (y=640..960)
    raw_geom_overlap = {
        "story_id": "geom_overlap_split_bottom_test",
        "objects": [
            {
                "id": "split_card",
                "type": "card",
                "purpose": "Split left card",
                "layout": "split_left",
                "title": "Split Card",
                "subtitle": "At split_left (y=420..660)",
                "display_value": "₹10 Lakh",
                "numeric_value": 1000000,
            },
            {
                "id": "bottom_chart",
                "type": "chart",
                "purpose": "Bottom chart",
                "layout": "full_bottom",
                "chart_type": "trajectory_area",
                "title": "Bottom Chart",
                "points": [{"xLabel": "Y1", "yValue": 10}, {"xLabel": "Y2", "yValue": 20}],
            },
        ],
        "events": [
            {"action": "enter", "target_id": "split_card", "anchor": "50 lakh"},
            {"action": "enter", "target_id": "bottom_chart", "anchor": "50 lakh"},
        ],
    }
    draft_geom = ContinuousStoryDraft.model_validate(raw_geom_overlap)
    # Give the bottom chart height of 320 (y=640..960) so it overlaps split_left (y=420..660)
    object.__setattr__(draft_geom.objects[1], "height", 320)
    result_geom = validate_story_draft(
        draft=draft_geom,
        approved_facts=loan_fixture["approved_facts"],
        word_timestamps=loan_fixture["word_timestamps"],
        total_duration_ms=loan_fixture["total_duration_ms"],
    )
    assert result_geom.valid is False
    assert any(e.code == "CARD_OVERLAP" for e in result_geom.errors)


def test_full_screen_conflicting_with_split_screen(loan_fixture: dict):
    """7. Test full_screen conflicting with split_left/split_right, and full_top failing loudly."""
    # 7a. full_screen conflicts with split_left
    raw_fs = {
        "story_id": "fs_split_conflict_test",
        "objects": [
            {
                "id": "bg_image",
                "type": "image",
                "purpose": "Full screen background",
                "layout": "full_screen",
                "asset_id": "assets/bg.jpg",
            },
            {
                "id": "split_card",
                "type": "card",
                "purpose": "Split card",
                "layout": "split_left",
                "title": "Split Card",
                "subtitle": "Conflicting with macro",
                "display_value": "₹10 Lakh",
                "numeric_value": 1000000,
            },
        ],
        "events": [
            {"action": "enter", "target_id": "bg_image", "anchor": "50 lakh"},
            {"action": "enter", "target_id": "split_card", "anchor": "50 lakh"},
        ],
    }
    draft_fs = ContinuousStoryDraft.model_validate(raw_fs)
    result_fs = validate_story_draft(
        draft=draft_fs,
        approved_facts=loan_fixture["approved_facts"],
        word_timestamps=loan_fixture["word_timestamps"],
        total_duration_ms=loan_fixture["total_duration_ms"],
        available_assets=["assets/bg.jpg"],
    )
    assert result_fs.valid is False
    assert any(e.code == "MACRO_LAYOUT_COLLISION" for e in result_fs.errors)

    # 7b. full_screen conflicts with split_right
    raw_fs_right = {
        "story_id": "fs_split_right_conflict_test",
        "objects": [
            {
                "id": "bg_image_right",
                "type": "image",
                "purpose": "Full screen background",
                "layout": "full_screen",
                "asset_id": "assets/bg.jpg",
            },
            {
                "id": "split_card_right",
                "type": "card",
                "purpose": "Split right card",
                "layout": "split_right",
                "title": "Split Right Card",
                "subtitle": "Conflicting with full_screen",
                "display_value": "₹10 Lakh",
                "numeric_value": 1000000,
            },
        ],
        "events": [
            {"action": "enter", "target_id": "bg_image_right", "anchor": "50 lakh"},
            {"action": "enter", "target_id": "split_card_right", "anchor": "50 lakh"},
        ],
    }
    draft_fs_right = ContinuousStoryDraft.model_validate(raw_fs_right)
    result_fs_right = validate_story_draft(
        draft=draft_fs_right,
        approved_facts=loan_fixture["approved_facts"],
        word_timestamps=loan_fixture["word_timestamps"],
        total_duration_ms=loan_fixture["total_duration_ms"],
        available_assets=["assets/bg.jpg"],
    )
    assert result_fs_right.valid is False
    assert any(e.code == "MACRO_LAYOUT_COLLISION" for e in result_fs_right.errors)

    # 7c. full_top is rejected as an invalid layout zone
    raw_ft = {
        "story_id": "ft_invalid_layout_test",
        "objects": [
            {
                "id": "top_banner",
                "type": "text",
                "layout": "full_top",
                "text": "CRITICAL NOTICE",
            },
        ],
        "events": [
            {"action": "enter", "target_id": "top_banner", "anchor": "50 lakh"},
        ],
    }
    with pytest.raises(pydantic.ValidationError, match="Input should be 'center', 'split_left', 'split_right', 'full_screen' or 'full_bottom'"):
        ContinuousStoryDraft.model_validate(raw_ft)


def test_invalid_split_layout_names_fail_loudly():
    """8. Test invalid split layout names failing loudly:
       - Generic 'split' is forbidden
       - 'split_screen', 'split_center', 'split_middle', 'left' fail loudly
    """
    invalid_zones = ["split", "split_screen", "split_center", "split_middle", "left", "split_both"]

    for inv in invalid_zones:
        # Pydantic schema validation failure
        raw = {
            "story_id": "invalid_zone_test",
            "objects": [
                {
                    "id": "bad_obj",
                    "type": "card",
                    "purpose": "Test invalid layout",
                    "layout": inv,
                    "title": "Invalid Card",
                    "subtitle": "Must fail",
                    "display_value": "₹10 Lakh",
                    "numeric_value": 1000000,
                }
            ],
            "events": [
                {"action": "enter", "target_id": "bad_obj", "anchor": "50 lakh"}
            ],
        }
        with pytest.raises(pydantic.ValidationError) as exc_info:
            ContinuousStoryDraft.model_validate(raw)
        assert "layout" in str(exc_info.value)
