from domain.generate_video_request import DurationProfile, GenerateVideoRequest, VisualMode
from domain.validation import ValidationResult


class GenerateVideoRequestValidator:
    def validate(self, request: GenerateVideoRequest) -> ValidationResult:
        errors: list[str] = []
        for field_name in ["topic", "audience", "language", "style", "channel"]:
            val = getattr(request, field_name, "").strip()
            if not val:
                errors.append(f"{field_name.capitalize()} is required.")

        if not isinstance(request.duration_profile, DurationProfile):
            try:
                DurationProfile(str(request.duration_profile))
            except ValueError:
                valid_profiles = ", ".join(p.value for p in DurationProfile)
                errors.append(
                    f"Invalid duration profile '{request.duration_profile}'. Must be one of: {valid_profiles}."
                )

        if not isinstance(request.visual_mode, VisualMode):
            try:
                VisualMode(str(request.visual_mode))
            except ValueError:
                valid_modes = ", ".join(m.value for m in VisualMode)
                errors.append(
                    f"Invalid visual mode '{request.visual_mode}'. Must be one of: {valid_modes}."
                )

        if errors:
            return ValidationResult(status="blocked", errors=errors)
        return ValidationResult(status="valid")

