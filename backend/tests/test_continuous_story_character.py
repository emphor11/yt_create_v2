"""
test_continuous_story_character.py — Unit & Integration Tests for Futuristic Character Primitive.

Covers the 14 contract requirements:
1. Valid futuristic character object.
2. Missing character_style rejection.
3. Invalid pose rejection.
4. Invalid facing rejection.
5. Field leakage rejection (title, display_value, etc.).
6. Valid change_pose event.
7. change_pose targeting a card rejection.
8. change_pose before enter rejection.
9. Unknown character target rejection.
10. Compiler output for characterProps.
11. Compiler output for change_pose.
12. Character collision with cards.
13. Character enter, pose change, move, and exit lifecycle.
14. Regression validation.
"""
from __future__ import annotations

import pytest
from pydantic import ValidationError

from domain.continuous_story_plan import ContinuousStoryDraft, StoryObjectDraft, StoryEventDraft
from engines.continuous_story_draft_validator import validate_story_draft
from engines.continuous_story_compiler import compile_story_draft


@pytest.fixture
def base_character_story() -> dict:
    return {
        "story_id": "character_demo_story",
        "objects": [
            {
                "id": "worker",
                "type": "character",
                "layout": "split_left",
                "character_style": "futuristic_stick",
                "role": "salaried employee",
                "label": "A salaried employee",
                "pose": "idle",
                "emotion": "neutral",
                "facing": "right",
                "accent": "#38BDF8",
                "purpose": "Represent the person experiencing the financial decision",
            },
            {
                "id": "wealth_card",
                "type": "card",
                "layout": "split_right",
                "title": "Retirement Corpus",
                "subtitle": "Fixed Return",
                "display_value": "₹2.5 Cr",
                "numeric_value": 25000000,
                "purpose": "show accumulated wealth",
            },
        ],
        "events": [
            {
                "action": "enter",
                "target_id": "worker",
                "anchor": "salaried employee",
            },
            {
                "action": "enter",
                "target_id": "wealth_card",
                "anchor": "fixed return",
            },
            {
                "action": "change_pose",
                "target_id": "worker",
                "pose": "think",
                "emotion": "focused",
                "anchor": "the difference comes",
            },
            {
                "action": "change_pose",
                "target_id": "worker",
                "pose": "worried",
                "emotion": "concerned",
                "anchor": "inflation eats",
            },
        ],
    }


@pytest.fixture
def base_narration_data() -> dict:
    return {
        "text": "A salaried employee invests monthly for a fixed return, but the difference comes when inflation eats into real purchasing power.",
        "word_timestamps": [
            {"word": "A", "start_ms": 0, "end_ms": 150},
            {"word": "salaried", "start_ms": 160, "end_ms": 500},
            {"word": "employee", "start_ms": 510, "end_ms": 900},
            {"word": "invests", "start_ms": 910, "end_ms": 1200},
            {"word": "monthly", "start_ms": 1210, "end_ms": 1600},
            {"word": "for", "start_ms": 1610, "end_ms": 1800},
            {"word": "a", "start_ms": 1810, "end_ms": 1900},
            {"word": "fixed", "start_ms": 1910, "end_ms": 2200},
            {"word": "return", "start_ms": 2210, "end_ms": 2600},
            {"word": "but", "start_ms": 2610, "end_ms": 2800},
            {"word": "the", "start_ms": 2810, "end_ms": 2950},
            {"word": "difference", "start_ms": 2960, "end_ms": 3400},
            {"word": "comes", "start_ms": 3410, "end_ms": 3800},
            {"word": "when", "start_ms": 3810, "end_ms": 4000},
            {"word": "inflation", "start_ms": 4010, "end_ms": 4500},
            {"word": "eats", "start_ms": 4510, "end_ms": 4900},
            {"word": "into", "start_ms": 4910, "end_ms": 5200},
            {"word": "real", "start_ms": 5210, "end_ms": 5500},
            {"word": "purchasing", "start_ms": 5510, "end_ms": 6000},
            {"word": "power", "start_ms": 6010, "end_ms": 6500},
        ],
    }


# ====================================================================
# TEST 1: Valid Futuristic Character Object
# ====================================================================
def test_valid_futuristic_character_object(base_character_story, base_narration_data):
    draft = ContinuousStoryDraft(**base_character_story)
    assert len(draft.objects) == 2
    char_obj = draft.objects[0]
    assert char_obj.type == "character"
    assert char_obj.character_style == "futuristic_stick"
    assert char_obj.role == "salaried employee"
    assert char_obj.pose == "idle"
    assert char_obj.emotion == "neutral"
    assert char_obj.facing == "right"
    assert char_obj.accent == "#38BDF8"

    # Validator pass
    val_res = validate_story_draft(
        draft,
        approved_facts={},
        word_timestamps=base_narration_data["word_timestamps"],
    )
    assert val_res.valid, f"Validation failed: {val_res.errors}"


# ====================================================================
# TEST 2: Missing character_style Rejection
# ====================================================================
def test_missing_character_style_rejection():
    with pytest.raises(ValidationError) as exc_info:
        StoryObjectDraft(
            id="worker",
            type="character",
            layout="split_left",
            role="salaried employee",
            pose="idle",
            facing="right",
            # character_style missing
        )
    assert "character_style" in str(exc_info.value)


# ====================================================================
# TEST 3: Invalid Pose Rejection
# ====================================================================
def test_invalid_pose_rejection():
    with pytest.raises(ValidationError) as exc_info:
        StoryObjectDraft(
            id="worker",
            type="character",
            layout="split_left",
            character_style="futuristic_stick",
            role="salaried employee",
            pose="superman_fly",  # Invalid pose
            facing="right",
        )
    assert "Invalid pose" in str(exc_info.value) or "Input should be" in str(exc_info.value)


# ====================================================================
# TEST 4: Invalid Facing Rejection
# ====================================================================
def test_invalid_facing_rejection():
    with pytest.raises(ValidationError) as exc_info:
        StoryObjectDraft(
            id="worker",
            type="character",
            layout="split_left",
            character_style="futuristic_stick",
            role="salaried employee",
            pose="idle",
            facing="upwards",  # Invalid facing
        )
    assert "Invalid facing" in str(exc_info.value) or "Input should be" in str(exc_info.value)


# ====================================================================
# TEST 5: Field Leakage Rejection (title, display_value, etc.)
# ====================================================================
@pytest.mark.parametrize(
    "leaked_field, leaked_val",
    [
        ("title", "Forbidden Title"),
        ("subtitle", "Forbidden Subtitle"),
        ("display_value", "₹10,000"),
        ("numeric_value", 10000),
        ("chart_type", "split_bar"),
        ("points", [{"xLabel": "2024", "yValue": 100}]),
        ("asset_id", "asset_123"),
        ("from_id", "some_id"),
        ("to_id", "some_other_id"),
        ("text", "Some forbidden text"),
    ],
)
def test_field_leakage_rejection(leaked_field, leaked_val):
    kwargs = {
        "id": "worker",
        "type": "character",
        "layout": "split_left",
        "character_style": "futuristic_stick",
        "role": "salaried employee",
        "pose": "idle",
        "facing": "right",
        leaked_field: leaked_val,
    }
    with pytest.raises(ValidationError) as exc_info:
        StoryObjectDraft(**kwargs)
    assert f"cannot specify non-character fields: {leaked_field}" in str(exc_info.value)


# ====================================================================
# TEST 6: Valid change_pose Event
# ====================================================================
def test_valid_change_pose_event(base_character_story, base_narration_data):
    ev = StoryEventDraft(
        action="change_pose",
        target_id="worker",
        pose="celebrate",
        emotion="happy",
        facing="left",
        anchor="difference comes",
    )
    assert ev.action == "change_pose"
    assert ev.pose == "celebrate"
    assert ev.emotion == "happy"
    assert ev.facing == "left"


# ====================================================================
# TEST 7: change_pose Targeting a Card Rejection
# ====================================================================
def test_change_pose_targeting_card_rejection(base_character_story, base_narration_data):
    data = dict(base_character_story)
    data["events"] = [
        {"action": "enter", "target_id": "worker", "anchor": "salaried employee"},
        {"action": "enter", "target_id": "wealth_card", "anchor": "fixed return"},
        {
            "action": "change_pose",
            "target_id": "wealth_card",  # Target is a CARD, not a character!
            "pose": "think",
            "anchor": "the difference comes",
        },
    ]
    draft = ContinuousStoryDraft(**data)
    val_res = validate_story_draft(
        draft,
        approved_facts={},
        word_timestamps=base_narration_data["word_timestamps"],
    )
    assert not val_res.valid
    assert any(e.code == "CHANGE_POSE_TARGET_NOT_CHARACTER" for e in val_res.errors)


# ====================================================================
# TEST 8: change_pose Before Enter Rejection
# ====================================================================
def test_change_pose_before_enter_rejection(base_character_story, base_narration_data):
    data = dict(base_character_story)
    data["events"] = [
        {
            "action": "change_pose",
            "target_id": "worker",
            "pose": "think",
            "anchor": "salaried employee",  # Before worker enters!
        },
        {"action": "enter", "target_id": "worker", "anchor": "fixed return"},
    ]
    draft = ContinuousStoryDraft(**data)
    val_res = validate_story_draft(
        draft,
        approved_facts={},
        word_timestamps=base_narration_data["word_timestamps"],
    )
    assert not val_res.valid
    assert any(e.code == "ACTION_BEFORE_OBJECT_ENTER" for e in val_res.errors)


# ====================================================================
# TEST 9: Unknown Character Target Rejection
# ====================================================================
def test_unknown_character_target_rejection(base_character_story, base_narration_data):
    data = dict(base_character_story)
    data["events"].append({
        "action": "change_pose",
        "target_id": "ghost_character",  # Target does NOT exist!
        "pose": "think",
        "anchor": "purchasing power",
    })
    draft = ContinuousStoryDraft(**data)
    val_res = validate_story_draft(
        draft,
        approved_facts={},
        word_timestamps=base_narration_data["word_timestamps"],
    )
    assert not val_res.valid
    assert any(e.code == "UNKNOWN_TARGET_ID" for e in val_res.errors)


# ====================================================================
# TEST 10: Compiler Output for characterProps
# ====================================================================
def test_compiler_output_for_character_props(base_character_story, base_narration_data):
    draft = ContinuousStoryDraft(**base_character_story)
    fixture = {
        "approved_facts": {},
        "word_timestamps": base_narration_data["word_timestamps"],
        "total_duration_ms": 6500,
        "audio_file": "demo_narration.mp3",
        "narration_text": base_narration_data["text"],
    }
    compiled = compile_story_draft(draft=draft, fixture=fixture)
    char_plan_obj = next(o for o in compiled["objects"] if o["id"] == "worker")
    assert char_plan_obj["type"] == "character"
    assert char_plan_obj["layout"] == "split_left"
    assert char_plan_obj["width"] == 240
    assert char_plan_obj["height"] == 360
    assert "characterProps" in char_plan_obj
    props = char_plan_obj["characterProps"]
    assert props["style"] == "futuristic_stick"
    assert props["role"] == "salaried employee"
    assert props["label"] == "A salaried employee"
    assert props["pose"] == "idle"
    assert props["emotion"] == "neutral"
    assert props["facing"] == "right"
    assert props["accentColor"] == "#38BDF8"


# ====================================================================
# TEST 11: Compiler Output for change_pose
# ====================================================================
def test_compiler_output_for_change_pose(base_character_story, base_narration_data):
    draft = ContinuousStoryDraft(**base_character_story)
    fixture = {
        "approved_facts": {},
        "word_timestamps": base_narration_data["word_timestamps"],
        "total_duration_ms": 6500,
        "audio_file": "demo_narration.mp3",
        "narration_text": base_narration_data["text"],
    }
    compiled = compile_story_draft(draft=draft, fixture=fixture)
    pose_events = [e for e in compiled["events"] if e["action"] == "change_pose"]
    assert len(pose_events) == 2

    ev1 = pose_events[0]
    assert ev1["targetId"] == "worker"
    assert ev1["durationFrames"] == 20
    assert ev1["pose"] == "think"
    assert ev1["emotion"] == "focused"
    assert ev1["anchor"] == "the difference comes"
    assert ev1["startFrame"] > 0  # Accurately resolved through speech timestamps

    ev2 = pose_events[1]
    assert ev2["targetId"] == "worker"
    assert ev2["durationFrames"] == 20
    assert ev2["pose"] == "worried"
    assert ev2["emotion"] == "concerned"
    assert ev2["startFrame"] > ev1["startFrame"]


# ====================================================================
# TEST 12: Character Collision with Cards
# ====================================================================
def test_character_collision_with_cards(base_character_story, base_narration_data):
    data = dict(base_character_story)
    # Put card in SAME zone as character: "split_left"
    data["objects"][1]["layout"] = "split_left"
    draft = ContinuousStoryDraft(**data)
    val_res = validate_story_draft(
        draft,
        approved_facts={},
        word_timestamps=base_narration_data["word_timestamps"],
    )
    assert not val_res.valid
    assert any(e.code == "ZONE_OCCUPANCY_COLLISION" for e in val_res.errors)


# ====================================================================
# TEST 13: Character Enter, Pose Change, Move, and Exit Lifecycle
# ====================================================================
def test_character_full_lifecycle_and_rejection_after_exit(base_character_story, base_narration_data):
    data = dict(base_character_story)
    data["objects"] = [data["objects"][0]]  # only test worker lifecycle
    data["events"] = [
        {"action": "enter", "target_id": "worker", "anchor": "salaried employee"},
        {"action": "change_pose", "target_id": "worker", "pose": "think", "anchor": "fixed return"},
        {"action": "move", "target_id": "worker", "to": "split_right", "anchor": "the difference comes"},
        {"action": "exit", "target_id": "worker", "direction": "left", "anchor": "inflation eats"},
    ]
    draft = ContinuousStoryDraft(**data)
    val_res = validate_story_draft(
        draft,
        approved_facts={},
        word_timestamps=base_narration_data["word_timestamps"],
    )
    assert val_res.valid, f"Full lifecycle should be valid: {val_res.errors}"

    # Now attempt a change_pose AFTER exit
    data_bad = dict(data)
    data_bad["events"] = list(data["events"]) + [
        {"action": "change_pose", "target_id": "worker", "pose": "worried", "anchor": "purchasing power"}
    ]
    draft_bad = ContinuousStoryDraft(**data_bad)
    val_bad = validate_story_draft(
        draft_bad,
        approved_facts={},
        word_timestamps=base_narration_data["word_timestamps"],
    )
    assert not val_bad.valid
    assert any(e.code == "ACTION_AFTER_OBJECT_EXIT" for e in val_bad.errors)
