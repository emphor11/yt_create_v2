from domain.narrative_arc import NarrativeArc, SceneArcStep
from domain.script_brief import ScriptBrief
from domain.topic_request import TopicRequest
from domain.validators.narrative_arc_validator import NarrativeArcValidator
from engines.narrative_arc_engine import NarrativeArcEngine
from engines.script_brief_engine import ScriptBriefEngine


def make_script_brief() -> ScriptBrief:
    return ScriptBriefEngine().run(
        topic_request=TopicRequest(
            topic="Why Monthly Payments Feel Cheap",
            angle="How EMIs hide total cost",
        )
    )


def test_narrative_arc_engine_creates_scene_level_arc_map() -> None:
    script_brief = make_script_brief()

    narrative_arc = NarrativeArcEngine().run(script_brief)

    assert narrative_arc.topic == script_brief.topic
    assert narrative_arc.thesis == script_brief.thesis
    assert narrative_arc.viewer_question == (
        "If the phone costs ₹80,000, why does ₹6,667 per month feel easier to accept?"
    )
    assert narrative_arc.arc == ["curiosity", "comfort", "reversal", "realization"]
    assert narrative_arc.scene_arc_steps[0].scene_id == "scene_01"
    assert narrative_arc.scene_arc_steps[0].is_payoff_scene


def test_narrative_arc_validator_accepts_mvp_arc() -> None:
    script_brief = make_script_brief()
    narrative_arc = NarrativeArcEngine().run(script_brief)

    result = NarrativeArcValidator().validate(narrative_arc, script_brief=script_brief)

    assert result.status == "valid"
    assert result.errors == []


def test_narrative_arc_validator_blocks_missing_scene_mapping() -> None:
    script_brief = make_script_brief()
    narrative_arc = NarrativeArcEngine().run(script_brief)
    narrative_arc.scene_arc_steps = []

    result = NarrativeArcValidator().validate(narrative_arc, script_brief=script_brief)

    assert result.status == "blocked"
    assert "Missing arc step for scene function: scene_01." in result.errors


def test_narrative_arc_validator_blocks_missing_payoff_scene() -> None:
    script_brief = make_script_brief()
    narrative_arc = NarrativeArcEngine().run(script_brief)
    narrative_arc.scene_arc_steps[0].is_payoff_scene = False

    result = NarrativeArcValidator().validate(narrative_arc, script_brief=script_brief)

    assert result.status == "blocked"
    assert "At least one payoff scene is required." in result.errors


def test_narrative_arc_validator_blocks_vague_arc_prose() -> None:
    script_brief = make_script_brief()
    narrative_arc = NarrativeArc(
        topic=script_brief.topic,
        thesis=script_brief.thesis,
        viewer_question="Why does the EMI feel easier?",
        arc=["some vague emotional journey"],
        scene_arc_steps=[
            SceneArcStep(
                scene_id="scene_01",
                scene_function_label="full_price_vs_monthly_payment",
                arc_phases=["some vague emotional journey"],
                narrative_purpose="Make the point.",
                is_payoff_scene=True,
            )
        ],
    )

    result = NarrativeArcValidator().validate(narrative_arc, script_brief=script_brief)

    assert result.status == "blocked"
    assert "NarrativeArc arc must be curiosity, comfort, reversal, realization." in result.errors
