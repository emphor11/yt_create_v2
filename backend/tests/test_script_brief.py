from domain.script_brief import SceneFunction, ScriptBrief
from domain.topic_request import TopicRequest
from domain.validators.script_brief_validator import ScriptBriefValidator
from engines.script_brief_engine import ScriptBriefEngine
from registries.finance_domain_registry import FinanceDomainRegistry


def make_validator() -> ScriptBriefValidator:
    return ScriptBriefValidator(FinanceDomainRegistry())


def test_script_brief_engine_creates_deterministic_brief() -> None:
    topic_request = TopicRequest(
        topic="Why Monthly Payments Feel Cheap",
        angle="How EMIs hide total cost",
    )

    brief = ScriptBriefEngine().run(topic_request)

    assert brief.topic == topic_request.topic
    assert brief.angle == topic_request.angle
    assert brief.recurring_example == "₹80,000 phone"
    assert brief.primary_mechanisms == [
        "payment_pain_reduction",
        "affordability_illusion",
    ]
    assert brief.scene_functions[0].scene_id == "scene_01"
    assert brief.scene_functions[0].mechanism == "payment_pain_reduction"


def test_script_brief_validator_accepts_mvp_brief() -> None:
    topic_request = TopicRequest(
        topic="Why Monthly Payments Feel Cheap",
        angle="How EMIs hide total cost",
    )
    brief = ScriptBriefEngine().run(topic_request)

    result = make_validator().validate(brief, topic_request=topic_request)

    assert result.status == "valid"
    assert result.errors == []


def test_script_brief_validator_blocks_unsupported_mechanism() -> None:
    topic_request = TopicRequest(
        topic="Why Monthly Payments Feel Cheap",
        angle="How EMIs hide total cost",
    )
    brief = ScriptBrief(
        topic=topic_request.topic,
        angle=topic_request.angle,
        thesis="A generic money-saving tip.",
        primary_mechanisms=["generic_saving_tip"],
        recurring_example="₹80,000 phone",
        scene_functions=[
            SceneFunction(
                scene_id="scene_01",
                label="generic_tip",
                mechanism="generic_saving_tip",
                purpose="Give a generic tip.",
            )
        ],
    )

    result = make_validator().validate(brief, topic_request=topic_request)

    assert result.status == "blocked"
    assert "Unsupported mechanism: generic_saving_tip." in result.errors


def test_script_brief_validator_blocks_vague_recurring_example() -> None:
    topic_request = TopicRequest(
        topic="Why Monthly Payments Feel Cheap",
        angle="How EMIs hide total cost",
    )
    brief = ScriptBriefEngine().run(topic_request)
    brief.recurring_example = "expensive product"

    result = make_validator().validate(brief, topic_request=topic_request)

    assert result.status == "blocked"
    assert result.errors == [
        "Recurring example must be the concrete MVP example: ₹80,000 phone."
    ]

