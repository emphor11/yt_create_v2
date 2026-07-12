from domain.generate_video_request import GenerateVideoRequest
from domain.validation import ValidationResult


class GenerateVideoRequestValidator:
    def validate(self, request: GenerateVideoRequest) -> ValidationResult:
        errors: list[str] = []
        for field_name in ["topic", "audience", "language", "style", "channel"]:
            val = getattr(request, field_name, "").strip()
            if not val:
                errors.append(f"{field_name.capitalize()} is required.")
        if errors:
            return ValidationResult(status="blocked", errors=errors)
        return ValidationResult(status="valid")
