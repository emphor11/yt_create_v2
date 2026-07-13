from domain.review_result import ReviewResult, ValidationCheck
from domain.validators.review_result_validator import ReviewResultValidator


def test_validator_accepts_valid_approved_result() -> None:
    result = ReviewResult(
        approved=True,
        checks=[
            ValidationCheck(name="Concept Alignment", status="passed", message="Passed"),
            ValidationCheck(name="Statistic Verification", status="passed", message="Passed"),
        ],
        feedback="All clear",
    )
    val_res = ReviewResultValidator().validate(result)
    assert val_res.status == "valid"
    assert not val_res.errors


def test_validator_blocks_if_approved_but_checks_failed() -> None:
    result = ReviewResult(
        approved=True,
        checks=[
            ValidationCheck(name="Concept Alignment", status="failed", message="Concept not found"),
        ],
    )
    val_res = ReviewResultValidator().validate(result)
    assert val_res.status == "blocked"
    assert "approved is True, but the following critical checks failed" in val_res.errors[0]


def test_validator_returns_failed_if_not_approved() -> None:
    result = ReviewResult(
        approved=False,
        checks=[
            ValidationCheck(name="Concept Alignment", status="failed", message="Concept not found"),
            ValidationCheck(name="Statistic Verification", status="passed", message="Passed"),
        ],
    )
    val_res = ReviewResultValidator().validate(result)
    assert val_res.status == "failed"
    assert "Concept Alignment: Concept not found" in val_res.errors
