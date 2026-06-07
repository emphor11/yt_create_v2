from domain.topic_request import TopicRequest
from domain.validation import ValidationResult


class TopicRequestValidator:
    def validate(self, topic_request: TopicRequest) -> ValidationResult:
        errors: list[str] = []

        if not topic_request.topic.strip():
            errors.append("Topic is required.")
        if not topic_request.angle.strip():
            errors.append("Angle is required.")

        if errors:
            return ValidationResult(status="blocked", errors=errors)

        return ValidationResult(status="valid")

