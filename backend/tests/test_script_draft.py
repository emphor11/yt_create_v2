import pytest
from pydantic import ValidationError

from domain.narrative_arc import NarrativeArc, SceneArcStep
from domain.script_brief import ScriptBrief
from domain.script_draft import ScriptDraft
from domain.topic_request import TopicRequest
from domain.validators.script_draft_validator import ScriptDraftValidator
from engines.narrative_arc_engine import NarrativeArcEngine
from engines.script_brief_engine import ScriptBriefEngine
from engines.script_draft_engine import ScriptDraftEngine


def make_script_brief() -> ScriptBrief:
    return ScriptBriefEngine().run(
        topic_request=TopicRequest(
            topic="Why Monthly Payments Feel Cheap",
            angle="How EMIs hide total cost",
        )
    )


def make_narrative_arc(script_brief: ScriptBrief) -> NarrativeArc:
    return NarrativeArcEngine().run(script_brief)


def make_script_draft() -> tuple[ScriptBrief, NarrativeArc, ScriptDraft]:
    script_brief = make_script_brief()
    narrative_arc = make_narrative_arc(script_brief)
    script_draft = ScriptDraftEngine().run(
        script_brief=script_brief,
        narrative_arc=narrative_arc,
    )
    return script_brief, narrative_arc, script_draft


def test_script_draft_engine_creates_hook_scene_and_outro() -> None:
    script_brief, narrative_arc, script_draft = make_script_draft()

    assert script_draft.topic == script_brief.topic
    assert script_draft.angle == script_brief.angle
    assert script_draft.thesis == script_brief.thesis
    assert "₹80,000 phone" in script_draft.hook
    assert len(script_draft.scenes) == len(narrative_arc.scene_arc_steps)
    assert script_draft.scenes[0].scene_id == "scene_01"
    assert script_draft.scenes[0].scene_function_label == "full_price_vs_monthly_payment"
    assert "₹6,667 per month" in script_draft.scenes[0].narration
    assert script_draft.outro


def test_script_draft_validator_accepts_mvp_draft() -> None:
    script_brief, narrative_arc, script_draft = make_script_draft()

    result = ScriptDraftValidator().validate(
        script_draft,
        script_brief=script_brief,
        narrative_arc=narrative_arc,
    )

    assert result.status == "valid"
    assert result.errors == []


def test_script_draft_validator_blocks_scene_count_drift() -> None:
    script_brief, narrative_arc, script_draft = make_script_draft()
    script_draft.scenes = []

    result = ScriptDraftValidator().validate(
        script_draft,
        script_brief=script_brief,
        narrative_arc=narrative_arc,
    )

    assert result.status == "blocked"
    assert "At least one draft scene is required." in result.errors
    assert "ScriptDraft scene order must match ScriptBrief scene functions." in result.errors


def test_script_draft_validator_blocks_topic_drift() -> None:
    script_brief, narrative_arc, script_draft = make_script_draft()
    script_draft.topic = "A different finance topic"

    result = ScriptDraftValidator().validate(
        script_draft,
        script_brief=script_brief,
        narrative_arc=narrative_arc,
    )

    assert result.status == "blocked"
    assert "ScriptDraft topic must match ScriptBrief topic." in result.errors


def test_script_draft_validator_blocks_missing_recurring_example() -> None:
    script_brief, narrative_arc, script_draft = make_script_draft()
    script_draft.hook = "An expensive purchase can feel smaller when split up."
    script_draft.scenes[0].narration = (
        "The total price stays the same, but a monthly payment changes how the buyer feels."
    )

    result = ScriptDraftValidator().validate(
        script_draft,
        script_brief=script_brief,
        narrative_arc=narrative_arc,
    )

    assert result.status == "blocked"
    assert "ScriptDraft must keep the recurring example: ₹80,000 phone." in result.errors


def test_script_draft_rejects_later_stage_fields() -> None:
    payload = {
        "topic": "Why Monthly Payments Feel Cheap",
        "angle": "How EMIs hide total cost",
        "thesis": "Monthly payments shift attention away from total price.",
        "hook": "An ₹80,000 phone feels different as an EMI.",
        "scenes": [],
        "outro": "Monthly payments change how expensive a purchase feels.",
        "entities": [],
    }

    with pytest.raises(ValidationError):
        ScriptDraft.model_validate(payload)


def test_script_draft_validator_blocks_narrative_arc_parent_mismatch() -> None:
    script_brief, narrative_arc, script_draft = make_script_draft()
    narrative_arc = NarrativeArc(
        topic=script_brief.topic,
        thesis="Different thesis",
        viewer_question="Why does the EMI feel smaller?",
        arc=["curiosity", "comfort", "reversal", "realization"],
        scene_arc_steps=[
            SceneArcStep(
                scene_id="scene_01",
                scene_function_label="full_price_vs_monthly_payment",
                arc_phases=["curiosity", "comfort", "reversal", "realization"],
                narrative_purpose="Move the viewer through the idea.",
                is_payoff_scene=True,
            )
        ],
    )

    result = ScriptDraftValidator().validate(
        script_draft,
        script_brief=script_brief,
        narrative_arc=narrative_arc,
    )

    assert result.status == "blocked"
    assert "NarrativeArc thesis must match ScriptBrief thesis." in result.errors
