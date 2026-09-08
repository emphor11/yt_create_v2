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


def test_validator_duration_profile_defaults_and_options() -> None:
    from domain.generate_video_request import DurationProfile

    # Default is short_2min
    req_default = GenerateVideoRequest(
        topic="EMIs vs Full Payment",
        audience="retail investors",
        language="English",
        style="edutainment",
        channel="FinanceChannel",
    )
    assert req_default.duration_profile == DurationProfile.SHORT_2MIN
    assert GenerateVideoRequestValidator().validate(req_default).status == "valid"

    # Explicit long_5min enum
    req_long = GenerateVideoRequest(
        topic="EMIs vs Full Payment",
        audience="retail investors",
        language="English",
        style="edutainment",
        channel="FinanceChannel",
        duration_profile=DurationProfile.LONG_5MIN,
    )
    assert req_long.duration_profile == DurationProfile.LONG_5MIN
    assert GenerateVideoRequestValidator().validate(req_long).status == "valid"

    # String coercion "long_5min"
    req_str = GenerateVideoRequest(
        topic="EMIs vs Full Payment",
        audience="retail investors",
        language="English",
        style="edutainment",
        channel="FinanceChannel",
        duration_profile="long_5min",  # type: ignore[arg-type]
    )
    assert req_str.duration_profile == DurationProfile.LONG_5MIN
    assert GenerateVideoRequestValidator().validate(req_str).status == "valid"
