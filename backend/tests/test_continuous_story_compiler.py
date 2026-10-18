"""
test_continuous_story_compiler.py — Unit Tests for Deterministic Continuous Story Compiler.
"""
from __future__ import annotations

import json
from pathlib import Path
import pytest

from domain.continuous_story_plan import ContinuousStoryDraft
from engines.continuous_story_compiler import ContinuousStoryCompiler, compile_story_draft, resolve_anchor_frame


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
                "value_fact_id": "loan_principal",
                "title": "Home Loan Principal",
            },
            {
                "id": "card_rate",
                "type": "card",
                "purpose": "interest rate card",
                "layout": "center_right",
                "value_fact_id": "rate_baseline",
                "title": "Interest Rate",
            },
            {
                "id": "card_emi",
                "type": "card",
                "purpose": "monthly payment burden",
                "layout": "bottom_center",
                "value_fact_id": "emi_baseline",
                "title": "Monthly EMI",
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
    assert card_loan["cardProps"]["format"] == "currency_inr"
    assert card_loan["cardProps"]["accentColor"] == "#3B82F6"

    # Card Rate
    card_rate = plan["objects"][1]
    assert card_rate["id"] == "card_rate"
    assert card_rate["layout"] == "center_right"
    assert card_rate["cardProps"]["value"] == 8.5
    assert card_rate["cardProps"]["format"] == "percentage"

    # Card EMI has provenance
    card_emi = plan["objects"][2]
    assert card_emi["cardProps"]["value"] == 43391
    assert "provenance" in card_emi["cardProps"]
    assert card_emi["cardProps"]["provenance"]["formula"] == "loan_emi"
    assert card_emi["cardProps"]["provenance"]["inputs"]["principal"] == 5000000

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
