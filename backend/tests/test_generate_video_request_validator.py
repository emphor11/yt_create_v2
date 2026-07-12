from domain.generate_video_request import GenerateVideoRequest
from domain.validators.generate_video_request_validator import GenerateVideoRequestValidator


def test_validator_accepts_valid_request() -> None:
    req = GenerateVideoRequest(
        topic="EMIs vs Full Payment",
        audience="retail investors",
        language="English",
        style="edutainment",
        channel="FinanceChannel",
    )
    result = GenerateVideoRequestValidator().validate(req)
    assert result.status == "valid"
    assert not result.errors


def test_validator_blocks_empty_fields() -> None:
    req = GenerateVideoRequest(
        topic="EMIs vs Full Payment",
        audience="",
        language="English",
        style="edutainment",
        channel="",
    )
    result = GenerateVideoRequestValidator().validate(req)
    assert result.status == "blocked"
    assert "Audience is required." in result.errors
    assert "Channel is required." in result.errors
