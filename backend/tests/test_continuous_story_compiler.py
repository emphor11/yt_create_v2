"""
test_continuous_story_compiler.py — Unit Tests for Deterministic Continuous Story Compiler.
"""
from __future__ import annotations

import json
from pathlib import Path
import pytest

from domain.continuous_story_plan import ContinuousStoryDraft
from engines.continuous_story_compiler import (
    ContinuousStoryCompiler,
    compile_story_draft,
    resolve_anchor_frame,
    resolve_anchor_ms,
    generate_timing_report,
)


@pytest.fixture
def loan_fixture() -> dict:
    fixture_path = Path(__file__).resolve().parent.parent / "fixtures" / "loan_story_fixture.json"
    with open(fixture_path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def loan_draft() -> ContinuousStoryDraft:
    raw = {
        "story_id": "loan_rate_hike",
        "objects": [
            {
                "id": "card_loan",
                "type": "card",
                "purpose": "show original loan",
                "layout": "center",
                "title": "Home Loan Principal",
                "display_value": "₹50 Lakhs",
                "numeric_value": 5000000,
                "value_fact_id": "loan_principal",
            },
            {
                "id": "card_rate",
                "type": "card",
                "purpose": "interest rate card",
                "layout": "center_right",
                "title": "Interest Rate",
                "display_value": "8.5%",
                "numeric_value": 8.5,
                "value_fact_id": "rate_baseline",
            },
            {
                "id": "card_emi",
                "type": "card",
                "purpose": "monthly payment burden",
                "layout": "bottom_center",
                "title": "Monthly EMI",
                "display_value": "₹43,391",
                "numeric_value": 43391,
                "value_fact_id": "emi_baseline",
            },
            {
                "id": "conn_rate_emi",
                "type": "connector",
                "purpose": "drives payment",
                "from_id": "card_rate",
                "to_id": "card_emi",
                "label": "Drives payment",
            },
        ],
        "events": [
            {
                "action": "enter",
                "target_id": "card_loan",
                "anchor": "50 lakh",
            },
            {
                "action": "move",
                "target_id": "card_loan",
                "anchor": "starts at",
                "to": "center_left",
            },
            {
                "action": "enter",
                "target_id": "card_rate",
                "anchor": "8.5",
            },
            {
                "action": "enter",
                "target_id": "card_emi",
                "anchor": "monthly EMI",
            },
            {
                "action": "connect",
                "target_id": "conn_rate_emi",
                "anchor": "surges to",
            },
            {
                "action": "transform_number",
                "target_id": "card_rate",
                "anchor": "rises to 10.5",
                "to_display_value": "10.5%",
                "to_numeric_value": 10.5,
                "to_fact_id": "rate_high",
            },
        ],
    }
    return ContinuousStoryDraft.model_validate(raw)


def test_anchor_frame_resolution(loan_fixture: dict):
    words = loan_fixture["word_timestamps"]

    # "50 lakh": words at 335ms and 670ms -> frame = round((335 / 1000) * 30) = 10
    frame_50l = resolve_anchor_frame(words, "50 lakh", fps=30)
    assert frame_50l == 10

    # "rises to 10.5": word 'rises' at 5739ms -> frame = round((5739 / 1000) * 30) = 172
    frame_rises = resolve_anchor_frame(words, "rises to 10.5", fps=30)
    assert frame_rises == 172


def test_compiler_determinism(loan_draft: ContinuousStoryDraft, loan_fixture: dict):
    plan1 = compile_story_draft(loan_draft, loan_fixture)
    plan2 = compile_story_draft(loan_draft, loan_fixture)

    json1 = json.dumps(plan1, sort_keys=True)
    json2 = json.dumps(plan2, sort_keys=True)

    assert json1 == json2


def test_compiled_plan_structure_and_defaults(loan_draft: ContinuousStoryDraft, loan_fixture: dict):
    plan = compile_story_draft(loan_draft, loan_fixture)

    assert plan["id"] == "loan_rate_hike"
    assert plan["fps"] == 30
    assert plan["durationInFrames"] >= 380
    assert plan["width"] == 1920
    assert plan["height"] == 1080
    assert plan["safeMargin"] == 80
    assert plan["audioFileName"] == "loan_narration.mp3"
    assert plan["narration"]["text"] == loan_fixture["narration_text"]
    assert len(plan["narration"]["wordTimestamps"]) == len(loan_fixture["word_timestamps"])


def test_compiled_objects_hierarchy_and_properties(loan_draft: ContinuousStoryDraft, loan_fixture: dict):
    plan = compile_story_draft(loan_draft, loan_fixture)

    # Top-level objects are atomic cards and connectors
    top_types = [o["type"] for o in plan["objects"]]
    assert top_types == ["card", "card", "card", "connector"]

    # Card Loan
    card_loan = plan["objects"][0]
    assert card_loan["id"] == "card_loan"
    assert card_loan["layout"] == "center"
    assert card_loan["cardProps"]["title"] == "Home Loan Principal"
    assert card_loan["cardProps"]["value"] == 5000000
    assert card_loan["cardProps"]["displayValue"] == "₹50 Lakhs"
    assert card_loan["cardProps"]["accentColor"] == "#3B82F6"

    # Card Rate
    card_rate = plan["objects"][1]
    assert card_rate["id"] == "card_rate"
    assert card_rate["layout"] == "center_right"
    assert card_rate["cardProps"]["value"] == 8.5
    assert card_rate["cardProps"]["displayValue"] == "8.5%"

    # Card EMI
    card_emi = plan["objects"][2]
    assert card_emi["cardProps"]["value"] == 43391
    assert card_emi["cardProps"]["displayValue"] == "₹43,391"

    # Connector
    conn = plan["objects"][3]
    assert conn["id"] == "conn_rate_emi"
    assert conn["type"] == "connector"
    assert conn["connectorProps"]["fromId"] == "card_rate"
    assert conn["connectorProps"]["toId"] == "card_emi"


def test_compiled_events(loan_draft: ContinuousStoryDraft, loan_fixture: dict):
    plan = compile_story_draft(loan_draft, loan_fixture)

    assert len(plan["events"]) == 6

    # Enter action
    enter_ev = plan["events"][0]
    assert enter_ev["action"] == "enter"
    assert enter_ev["targetId"] == "card_loan"
    assert enter_ev["startFrame"] == 10
    assert enter_ev["durationFrames"] == 25
    assert enter_ev["style"] == "fade_slide_up"

    # Move action
    move_ev = plan["events"][1]
    assert move_ev["action"] == "move"
    assert move_ev["targetId"] == "card_loan"
    assert move_ev["to"] == "center_left"

    # Transform Number action
    trans_ev = plan["events"][5]
    assert trans_ev["action"] == "transform_number"
    assert trans_ev["targetId"] == "card_rate"
    assert trans_ev["toValue"] == 10.5
    assert trans_ev["startFrame"] == 172


def test_resolve_anchor_frame_unknown_raises_error(loan_fixture: dict):
    words = loan_fixture["word_timestamps"]
    with pytest.raises(ValueError, match="could not be resolved to any spoken word"):
        resolve_anchor_frame(words, "completely absent non existent phrase", fps=30)


def test_compiler_rejects_unsupported_object_type(loan_fixture: dict):
    # A draft with an invalid object type
    with pytest.raises(Exception):
        ContinuousStoryDraft.model_validate({
            "story_id": "bad_type",
            "objects": [
                {
                    "id": "bad_obj",
                    "type": "invalid_primitive_kind",
                    "layout": "center",
                }
            ],
            "events": [],
        })


def test_compiled_change_visual_state_event(loan_draft: ContinuousStoryDraft, loan_fixture: dict):
    raw = loan_draft.model_dump()
    raw["events"].append({
        "action": "change_visual_state",
        "target_id": "card_rate",
        "anchor": "rises to 10.5",
        "state": "warning",
        "badge": "+2.0% HIKE",
    })
    draft = ContinuousStoryDraft.model_validate(raw)
    plan = compile_story_draft(draft, loan_fixture)

    state_event = plan["events"][-1]
    assert state_event["action"] == "change_visual_state"
    assert state_event["targetId"] == "card_rate"
    assert state_event["startFrame"] == 172
    assert state_event["state"] == "warning"
    assert state_event["badge"] == "+2.0% HIKE"
    assert state_event["anchor"] == "rises to 10.5"


def test_compiled_exit_event(loan_draft: ContinuousStoryDraft, loan_fixture: dict):
    raw = loan_draft.model_dump()
    raw["events"].append({
        "action": "exit",
        "target_id": "card_loan",
        "anchor": "monthly EMI",
        "direction": "left",
    })
    draft = ContinuousStoryDraft.model_validate(raw)
    plan = compile_story_draft(draft, loan_fixture)

    exit_event = plan["events"][-1]
    assert exit_event["action"] == "exit"
    assert exit_event["targetId"] == "card_loan"
    assert exit_event["startFrame"] > 0
    assert exit_event["durationFrames"] == 24
    assert exit_event["direction"] == "left"
    assert exit_event["anchor"] == "monthly EMI"


def test_two_beat_scene_continuation_compilation(loan_draft: ContinuousStoryDraft, loan_fixture: dict):
    raw = loan_draft.model_dump()
    # Add consequence card for Beat 2
    raw["objects"].append({
        "id": "card_consequence",
        "type": "card",
        "purpose": "Total extra interest penalty",
        "layout": "bottom_left",
        "value_fact_id": "total_extra_interest",
        "title": "Total Extra Interest",
    })
    # Add exit of old card
    raw["events"].append({
        "action": "exit",
        "target_id": "card_loan",
        "anchor": "adding",
        "direction": "left",
    })
    # Add entrance of new consequence card
    raw["events"].append({
        "action": "enter",
        "target_id": "card_consequence",
        "anchor": "burden",
    })

    draft = ContinuousStoryDraft.model_validate(raw)
    plan = compile_story_draft(draft, loan_fixture)

    exit_ev = [e for e in plan["events"] if e["action"] == "exit" and e["targetId"] == "card_loan"][0]
    enter_ev = [e for e in plan["events"] if e["action"] == "enter" and e["targetId"] == "card_consequence"][0]

    assert exit_ev["startFrame"] > 0
    assert enter_ev["startFrame"] > exit_ev["startFrame"]
    assert enter_ev["targetId"] == "card_consequence"


def test_compiled_chart_object(loan_draft: ContinuousStoryDraft, loan_fixture: dict):
    raw = loan_draft.model_dump()
    raw["objects"].append({
        "id": "chart_interest_trajectory",
        "type": "chart",
        "purpose": "20-year extra interest trajectory area curve",
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
        "action": "enter",
        "target_id": "chart_interest_trajectory",
        "anchor": "heavy burden",
    })

    draft = ContinuousStoryDraft.model_validate(raw)
    plan = compile_story_draft(draft, loan_fixture)

    chart_objs = [o for o in plan["objects"] if o["id"] == "chart_interest_trajectory"]
    assert len(chart_objs) == 1
    chart = chart_objs[0]
    assert chart["type"] == "chart"
    assert chart["layout"] == "full_bottom"
    assert chart["width"] == 1760
    assert chart["height"] == 360
    assert chart["chartProps"]["chartType"] == "trajectory_area"
    assert chart["chartProps"]["title"] == "20-Year Extra Interest Trajectory"
    assert len(chart["chartProps"]["series"]) == 1
    assert len(chart["chartProps"]["series"][0]["points"]) == 5


def test_card_direct_authoring_compilation(loan_fixture: dict):
    raw_draft = {
        "story_id": "direct_authoring_test",
        "objects": [
            {
                "id": "card_home_loan",
                "type": "card",
                "purpose": "Directly authored home loan card",
                "layout": "center",
                "title": "Home Loan Principal",
                "display_value": "₹50 Lakhs",
                "numeric_value": 5000000,
                "subtitle": "30-Year Mortgage",
            },
            {
                "id": "num_rate",
                "type": "number",
                "purpose": "Directly authored number",
                "layout": "center_right",
                "display_value": "8.5%",
                "numeric_value": 8.5,
            },
        ],
        "events": [
            {
                "action": "enter",
                "target_id": "card_home_loan",
                "anchor": "50 lakh",
            },
            {
                "action": "transform_number",
                "target_id": "card_home_loan",
                "anchor": "rises to",
                "to_display_value": "₹1.38 Cr",
                "to_numeric_value": 13800000,
            },
        ],
    }

    draft = ContinuousStoryDraft.model_validate(raw_draft)
    plan = compile_story_draft(draft, loan_fixture)

    compiled_card = next(o for o in plan["objects"] if o["id"] == "card_home_loan")
    assert compiled_card["cardProps"]["title"] == "Home Loan Principal"
    assert compiled_card["cardProps"]["displayValue"] == "₹50 Lakhs"
    assert compiled_card["cardProps"]["value"] == 5000000
    assert compiled_card["cardProps"]["subtitle"] == "30-Year Mortgage"

    compiled_num = next(o for o in plan["objects"] if o["id"] == "num_rate")
    assert compiled_num["numberProps"]["displayValue"] == "8.5%"
    assert compiled_num["numberProps"]["value"] == 8.5
    assert compiled_num["numberProps"]["format"] == "plain"

    transform_ev = next(e for e in plan["events"] if e["action"] == "transform_number")
    assert transform_ev["toDisplayValue"] == "₹1.38 Cr"
    assert transform_ev["toValue"] == 13800000


def test_card_conceptual_without_value(loan_fixture: dict):
    raw_draft = {
        "story_id": "conceptual_card_test",
        "objects": [
            {
                "id": "card_concept",
                "type": "card",
                "purpose": "Purely qualitative conceptual card",
                "layout": "center",
                "title": "Compounding Effect",
                "subtitle": "Interest Accumulates Over Time",
            }
        ],
        "events": [
            {
                "action": "enter",
                "target_id": "card_concept",
                "anchor": "starts at",
            }
        ],
    }

    draft = ContinuousStoryDraft.model_validate(raw_draft)
    plan = compile_story_draft(draft, loan_fixture)

    compiled_card = next(o for o in plan["objects"] if o["id"] == "card_concept")
    assert compiled_card["cardProps"]["title"] == "Compounding Effect"
    assert compiled_card["cardProps"]["subtitle"] == "Interest Accumulates Over Time"
    assert compiled_card["cardProps"].get("displayValue") is None
    assert compiled_card["cardProps"].get("value") is None


def test_missing_chart_data_fails():
    # 1. Pydantic validation fails if chart has neither series nor points
    with pytest.raises(Exception, match="requires directly authored 'series' or 'points'"):
        ContinuousStoryDraft.model_validate({
            "story_id": "bad_chart_story",
            "objects": [
                {
                    "id": "chart_empty",
                    "type": "chart",
                    "layout": "full_bottom",
                    "chart_type": "trajectory_area",
                    "title": "Empty Chart",
                }
            ],
            "events": [
                {"action": "enter", "target_id": "chart_empty", "anchor": "test"}
            ],
        })


def test_missing_transform_data_fails():
    # 1. transform_number missing to_display_value fails
    with pytest.raises(Exception, match="requires 'to_display_value'"):
        ContinuousStoryDraft.model_validate({
            "story_id": "bad_transform_story",
            "objects": [
                {
                    "id": "card_test",
                    "type": "card",
                    "layout": "center",
                    "title": "Test Card",
                }
            ],
            "events": [
                {
                    "action": "transform_number",
                    "target_id": "card_test",
                    "anchor": "test",
                    "to_numeric_value": 100,
                }
            ],
        })

    # 2. transform_number missing to_numeric_value fails
    with pytest.raises(Exception, match="requires 'to_numeric_value'"):
        ContinuousStoryDraft.model_validate({
            "story_id": "bad_transform_story",
            "objects": [
                {
                    "id": "card_test",
                    "type": "card",
                    "layout": "center",
                    "title": "Test Card",
                }
            ],
            "events": [
                {
                    "action": "transform_number",
                    "target_id": "card_test",
                    "anchor": "test",
                    "to_display_value": "₹100",
                }
            ],
        })


def test_no_fact_registry_needed(loan_fixture: dict):
    # Completely empty fixture with NO approved_facts
    clean_fixture = {
        "word_timestamps": loan_fixture["word_timestamps"],
        "narration_text": loan_fixture["narration_text"],
        "total_duration_ms": loan_fixture["total_duration_ms"],
    }
    raw_draft = {
        "story_id": "fact_free_story",
        "objects": [
            {
                "id": "card_direct",
                "type": "card",
                "layout": "center",
                "title": "Direct Metric",
                "display_value": "₹1 Crore",
                "numeric_value": 10000000,
            }
        ],
        "events": [
            {"action": "enter", "target_id": "card_direct", "anchor": "50 lakh"}
        ],
    }
    draft = ContinuousStoryDraft.model_validate(raw_draft)
    plan = compile_story_draft(draft, clean_fixture)

    assert plan["id"] == "fact_free_story"
    compiled_card = plan["objects"][0]
    assert compiled_card["cardProps"]["title"] == "Direct Metric"
    assert compiled_card["cardProps"]["displayValue"] == "₹1 Crore"
    assert compiled_card["cardProps"]["value"] == 10000000
    assert compiled_card["cardProps"]["valueFactId"] is None


def test_direct_all_primitives_compile_correctly(loan_fixture: dict):
    # Fixture with no facts and with available_assets
    fixture = {
        "word_timestamps": loan_fixture["word_timestamps"],
        "narration_text": loan_fixture["narration_text"],
        "total_duration_ms": loan_fixture["total_duration_ms"],
        "available_assets": ["shield_icon"],
    }

    raw_draft = {
        "story_id": "all_primitives_story",
        "objects": [
            {
                "id": "card_savings",
                "type": "card",
                "layout": "top_left",
                "title": "Emergency Savings",
                "display_value": "₹10,000",
                "numeric_value": 10000,
                "subtitle": "Safe Cushion",
                "badge": "SECURE",
                "accent": "#10B981",
                "visual_state": "success",
            },
            {
                "id": "num_rate",
                "type": "number",
                "layout": "top_right",
                "display_value": "7.2%",
                "numeric_value": 7.2,
                "purpose": "Inflation Rate",
            },
            {
                "id": "txt_callout",
                "type": "text",
                "layout": "center_left",
                "text": "Inflation silently eats purchasing power.",
                "purpose": "Core insight",
            },
            {
                "id": "chart_inflation",
                "type": "chart",
                "layout": "bottom_center",
                "chart_type": "split_bar",
                "title": "Savings vs Inflation",
                "subtitle": "5-Year Impact",
                "points": [
                    {"xLabel": "Year 1", "yValue": 100},
                    {"xLabel": "Year 5", "yValue": 70},
                ],
            },
            {
                "id": "img_shield",
                "type": "image",
                "layout": "center_right",
                "asset_id": "shield_icon",
            },
            {
                "id": "conn_savings_rate",
                "type": "connector",
                "layout": "center",
                "from_id": "card_savings",
                "to_id": "num_rate",
                "label": "eroded by",
            },
        ],
        "events": [
            {"action": "enter", "target_id": "card_savings", "anchor": "50 lakh"},
            {"action": "enter", "target_id": "num_rate", "anchor": "8.5"},
            {"action": "enter", "target_id": "txt_callout", "anchor": "starts at"},
            {"action": "enter", "target_id": "chart_inflation", "anchor": "monthly EMI"},
            {"action": "enter", "target_id": "img_shield", "anchor": "percent"},
            {"action": "connect", "target_id": "conn_savings_rate", "anchor": "surges to"},
            {
                "action": "transform_number",
                "target_id": "card_savings",
                "anchor": "rises to 10.5",
                "to_display_value": "₹7,000",
                "to_numeric_value": 7000,
            },
        ],
    }

    draft = ContinuousStoryDraft.model_validate(raw_draft)
    plan = compile_story_draft(draft, fixture)

    assert len(plan["objects"]) == 6

    # 1. card
    card = next(o for o in plan["objects"] if o["id"] == "card_savings")
    assert card["type"] == "card"
    assert card["cardProps"]["title"] == "Emergency Savings"
    assert card["cardProps"]["displayValue"] == "₹10,000"
    assert card["cardProps"]["value"] == 10000
    assert card["cardProps"]["subtitle"] == "Safe Cushion"
    assert card["cardProps"]["badge"] == "SECURE"
    assert card["cardProps"]["accentColor"] == "#10B981"
    assert card["cardProps"]["visualState"] == "success"

    # 2. number
    num = next(o for o in plan["objects"] if o["id"] == "num_rate")
    assert num["type"] == "number"
    assert num["numberProps"]["displayValue"] == "7.2%"
    assert num["numberProps"]["value"] == 7.2

    # 3. text
    txt = next(o for o in plan["objects"] if o["id"] == "txt_callout")
    assert txt["type"] == "text"
    assert txt["textProps"]["text"] == "Inflation silently eats purchasing power."

    # 4. chart
    chart = next(o for o in plan["objects"] if o["id"] == "chart_inflation")
    assert chart["type"] == "chart"
    assert chart["chartProps"]["chartType"] == "split_bar"
    assert chart["chartProps"]["title"] == "Savings vs Inflation"
    assert chart["chartProps"]["subtitle"] == "5-Year Impact"
    assert chart["chartProps"]["series"][0]["points"][0] == {"xLabel": "Year 1", "yValue": 100}

    # 5. image
    img = next(o for o in plan["objects"] if o["id"] == "img_shield")
    assert img["type"] == "image"
    assert img["imageProps"]["assetId"] == "shield_icon"

    # 6. connector
    conn = next(o for o in plan["objects"] if o["id"] == "conn_savings_rate")
    assert conn["type"] == "connector"
    assert conn["connectorProps"]["fromId"] == "card_savings"
    assert conn["connectorProps"]["toId"] == "num_rate"
    assert conn["connectorProps"]["label"] == "eroded by"

    # transform event
    trans_ev = next(e for e in plan["events"] if e["action"] == "transform_number")
    assert trans_ev["toDisplayValue"] == "₹7,000"
    assert trans_ev["toValue"] == 7000


def test_image_requires_available_assets_and_rejects_unknown(loan_fixture: dict):
    raw_draft = {
        "story_id": "image_test_story",
        "objects": [
            {
                "id": "img_brand",
                "type": "image",
                "layout": "center",
                "asset_id": "unknown_brand_logo",
            }
        ],
        "events": [
            {"action": "enter", "target_id": "img_brand", "anchor": "50 lakh"}
        ],
    }
    draft = ContinuousStoryDraft.model_validate(raw_draft)

    # 1. Fails when available_assets is empty
    with pytest.raises(ValueError, match="available_assets list is empty"):
        compile_story_draft(draft, {
            "word_timestamps": loan_fixture["word_timestamps"],
            "total_duration_ms": loan_fixture["total_duration_ms"],
            "available_assets": [],
        })

    # 2. Fails when asset_id is not in available_assets
    with pytest.raises(ValueError, match="references unknown asset_id 'unknown_brand_logo'"):
        compile_story_draft(draft, {
            "word_timestamps": loan_fixture["word_timestamps"],
            "total_duration_ms": loan_fixture["total_duration_ms"],
            "available_assets": ["valid_logo_1", "valid_logo_2"],
        })


def test_anchor_searches_after_card_enter_for_repeating_words():
    """Verifies that an event's anchor resolves after the card entered when words repeat."""
    word_timestamps = [
        {"word": "equity", "start_ms": 1000, "end_ms": 1300},
        {"word": "catch", "start_ms": 5000, "end_ms": 5500},
        {"word": "equity", "start_ms": 8000, "end_ms": 8300},
    ]
    raw_draft = {
        "story_id": "repeat_anchor_test",
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
    plan = compile_story_draft(draft, {
        "word_timestamps": word_timestamps,
        "total_duration_ms": 10000,
    })

    enter_event = plan["events"][0]
    exit_event = plan["events"][1]

    # Enter at 'catch' (5000ms = 150 frames @ 30fps)
    assert enter_event["startFrame"] == 150
    # Exit at 'equity' AFTER enter (8000ms = 240 frames @ 30fps), NOT the one at 1000ms (30 frames)
    assert exit_event["startFrame"] == 240


def test_resolve_anchor_ms_strict_contiguous_phrase_matching():
    """
    Requirement:
    Replace fuzzy anchor matching with exact contiguous phrase matching.
    Remove:
      - first-token fallback
      - substring matching
      - fallback search from frame zero
    If the exact phrase is not found, the pipeline should fail loudly.
    """
    words = [
        {"word": "A", "start_ms": 0, "end_ms": 200},
        {"word": "fifty", "start_ms": 200, "end_ms": 500},
        {"word": "lakh", "start_ms": 500, "end_ms": 800},
        {"word": "rupee", "start_ms": 800, "end_ms": 1100},
        {"word": "home", "start_ms": 1100, "end_ms": 1400},
        {"word": "loan", "start_ms": 1400, "end_ms": 1700},
    ]

    # 1. Exact contiguous match works
    assert resolve_anchor_ms(words, "fifty lakh rupee") == 200

    # 2. Non-contiguous tokens must fail loudly (no skipping words)
    with pytest.raises(ValueError, match="could not be resolved to any spoken word"):
        resolve_anchor_ms(words, "fifty rupee")

    # 3. Substring within a word must fail loudly (e.g. 'akh' in 'lakh')
    with pytest.raises(ValueError, match="could not be resolved to any spoken word"):
        resolve_anchor_ms(words, "akh")

    # 4. First-token only fallback removed: if phrase is 'fifty crore', 'fifty' is present but 'fifty crore' is not
    with pytest.raises(ValueError, match="could not be resolved to any spoken word"):
        resolve_anchor_ms(words, "fifty crore")

    # 5. Fallback search from frame zero removed: if searched after min_start_ms=1000,
    # 'fifty lakh' (at 200ms) must NOT fall back to 200ms and must fail loudly!
    with pytest.raises(ValueError, match="could not be resolved to any spoken word"):
        resolve_anchor_ms(words, "fifty lakh", min_start_ms=1000)


def test_generate_timing_report_format():
    """
    Requirement: Add a timing report before rendering:
    Object: interest_card
    Anchor: "eighty-eight point four lakhs rupees"
    Matched timestamp: 33.73s
    Start frame: 1012
    Enter event: present
    Visible interval: 33.73s – 41.83s
    """
    plan = {
        "id": "timing_report_test",
        "fps": 30,
        "durationInFrames": 1500,
        "objects": [
            {
                "id": "interest_card",
                "type": "card",
                "layout": "center",
            }
        ],
        "events": [
            {
                "action": "enter",
                "targetId": "interest_card",
                "startFrame": 1012,
                "durationFrames": 20,
                "anchor": "eighty-eight point four lakhs rupees",
            },
            {
                "action": "exit",
                "targetId": "interest_card",
                "startFrame": 1255,  # 1255 / 30 = 41.83s
                "durationFrames": 20,
                "anchor": "end of interval",
            },
        ],
    }

    report = generate_timing_report(plan)
    assert "Object: interest_card" in report
    assert 'Anchor: "eighty-eight point four lakhs rupees"' in report
    assert "Matched timestamp: 33.73s" in report
    assert "Start frame: 1012" in report
    assert "Enter event: present" in report
    assert "Visible interval: 33.73s – 41.83s" in report


