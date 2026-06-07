from domain.topic_request import TopicRequest
from domain.validators.topic_request_validator import TopicRequestValidator


def test_topic_request_validator_accepts_topic_and_angle() -> None:
    result = TopicRequestValidator().validate(
        TopicRequest(
            topic="Why Monthly Payments Feel Cheap",
            angle="How EMIs hide total cost",
        )
    )

    assert result.status == "valid"
    assert result.errors == []


def test_topic_request_validator_blocks_empty_topic() -> None:
    result = TopicRequestValidator().validate(
        TopicRequest(topic="", angle="How EMIs hide total cost")
    )

    assert result.status == "blocked"
    assert result.errors == ["Topic is required."]


def test_topic_request_validator_blocks_empty_angle() -> None:
    result = TopicRequestValidator().validate(
        TopicRequest(topic="Why Monthly Payments Feel Cheap", angle="")
    )

    assert result.status == "blocked"
    assert result.errors == ["Angle is required."]

