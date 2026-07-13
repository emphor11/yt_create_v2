from domain.review_result import ReviewResult
from domain.validation import ValidationResult


class ReviewResultValidator:
    def validate(self, result: ReviewResult) -> ValidationResult:
        errors: list[str] = []

        if result.approved:
            failed_checks = [c.name for c in result.checks if c.status == "failed"]
            if failed_checks:
                errors.append(
                    f"ReviewResult approved is True, but the following critical checks failed: "
                    f"{', '.join(failed_checks)}."
                )

        # Basic score/feedback validations
        for idx, check in enumerate(result.checks):
            if not check.name.strip():
                errors.append(f"Validation check at index {idx} requires a name.")
            if check.status not in ("passed", "failed"):
                errors.append(f"Validation check '{check.name}' has invalid status '{check.status}'.")

        if errors:
            return ValidationResult(status="blocked", errors=errors)

        # If any check has status 'failed' inside the review result, the result status is 'failed'!
        # This allows the orchestrator state machine to transition the ProjectRun state to 'failed'!
        # Wait, if approved is False, we return 'failed' status so the run stops!
        if not result.approved:
            failed_msgs = [f"{c.name}: {c.message}" for c in result.checks if c.status == "failed"]
            return ValidationResult(
                status="failed",
                errors=failed_msgs or ["Quality review failed but did not specify error messages."],
            )

        return ValidationResult(status="valid")
