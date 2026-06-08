import pytest
from pydantic import ValidationError

from domain.narrative_arc import NarrativeArc
from domain.scene_script import SceneScript
from domain.script_brief import ScriptBrief
from domain.script_draft import ScriptDraft
from domain.topic_request import TopicRequest
from domain.validators.scene_script_validator import SceneScriptValidator
from engines.narrative_arc_engine import NarrativeArcEngine
from engines.scene_script_engine import SceneScriptEngine
from engines.script_brief_engine import ScriptBriefEngine
from engines.script_draft_engine import ScriptDraftEngine


def make_parents():
    script_brief = ScriptBriefEngine().run(
        topic_request=TopicRequest(
            topic="Why Monthly Payments Feel Cheap",
            angle="How EMIs hide total cost",
        )
    )
    narrative_arc = NarrativeArcEngine().run(script_brief)
    script_draft = ScriptDraftEngine().run(
        script_brief=script_brief,
        narrative_arc=narrative_arc,
    )
    return script_brief, narrative_arc, script_draft


def make_scene_script() -> tuple[ScriptBrief, NarrativeArc, ScriptDraft, SceneScript]:
    script_brief, narrative_arc, script_draft = make_parents()
    scene_script = SceneScriptEngine().run(
        script_brief=script_brief,
        narrative_arc=narrative_arc,
        script_draft=script_draft,
    )
    return script_brief, narrative_arc, script_draft, scene_script


def test_scene_script_engine_creates_independent_scene_unit() -> None:
    script_brief, narrative_arc, script_draft, scene_script = make_scene_script()

    assert scene_script.scene_id == "scene_01"
    assert scene_script.topic == script_brief.topic
    assert scene_script.angle == script_brief.angle
    assert scene_script.thesis == script_brief.thesis
    assert scene_script.mechanism == script_brief.scene_functions[0].mechanism
    assert scene_script.scene_function_label == script_brief.scene_functions[0].label
    assert scene_script.arc_phases == narrative_arc.scene_arc_steps[0].arc_phases
    assert scene_script.narrative_purpose == narrative_arc.scene_arc_steps[0].narrative_purpose
    assert scene_script.narration == script_draft.scenes[0].narration
    assert scene_script.story_state.recurring_example == "₹80,000 phone"


def test_scene_script_validator_accepts_mvp_scene() -> None:
    script_brief, narrative_arc, script_draft, scene_script = make_scene_script()

    result = SceneScriptValidator().validate(
        scene_script,
        script_brief=script_brief,
        narrative_arc=narrative_arc,
        script_draft=script_draft,
    )

    assert result.status == "valid"
    assert result.errors == []


def test_scene_script_validator_blocks_mechanism_drift() -> None:
    script_brief, narrative_arc, script_draft, scene_script = make_scene_script()
    scene_script.mechanism = "affordability_illusion"

    result = SceneScriptValidator().validate(
        scene_script,
        script_brief=script_brief,
        narrative_arc=narrative_arc,
        script_draft=script_draft,
    )

    assert result.status == "blocked"
    assert (
        "SceneScript mechanism for scene_01 must match ScriptBrief scene function."
        in result.errors
    )


def test_scene_script_validator_blocks_story_state_drift() -> None:
    script_brief, narrative_arc, script_draft, scene_script = make_scene_script()
    scene_script.story_state.recurring_example = "a generic phone"

    result = SceneScriptValidator().validate(
        scene_script,
        script_brief=script_brief,
        narrative_arc=narrative_arc,
        script_draft=script_draft,
    )

    assert result.status == "blocked"
    assert "SceneScript story_state.recurring_example must match ScriptBrief recurring example." in result.errors


def test_scene_script_validator_blocks_narration_drift() -> None:
    script_brief, narrative_arc, script_draft, scene_script = make_scene_script()
    scene_script.narration = "A different narration."

    result = SceneScriptValidator().validate(
        scene_script,
        script_brief=script_brief,
        narrative_arc=narrative_arc,
        script_draft=script_draft,
    )

    assert result.status == "blocked"
    assert "SceneScript narration for scene_01 must match ScriptDraft scene narration." in result.errors


def test_scene_script_rejects_later_stage_fields() -> None:
    payload = {
        "scene_id": "scene_01",
        "topic": "Why Monthly Payments Feel Cheap",
        "angle": "How EMIs hide total cost",
        "thesis": "Monthly payments shift attention away from total price.",
        "mechanism": "payment_pain_reduction",
        "scene_function_label": "full_price_vs_monthly_payment",
        "arc_phases": ["curiosity", "comfort", "reversal", "realization"],
        "narrative_purpose": "Move the viewer through the idea.",
        "narration": "The phone costs ₹80,000.",
        "story_state": {"recurring_example": "₹80,000 phone"},
        "entities": [],
    }

    with pytest.raises(ValidationError):
        SceneScript.model_validate(payload)
