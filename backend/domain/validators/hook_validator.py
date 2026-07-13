from domain.hook import Hook
from domain.validation import ValidationResult


class HookValidator:
    def validate(self, hook: Hook) -> ValidationResult:
        errors: list[str] = []

        if not hook.conceptual_hook.strip():
            errors.append("Hook conceptual description is required.")
        if not hook.script_text.strip():
            errors.append("Hook script spoken text is required and cannot be empty.")

        if len(hook.visual_directives) < 2:
            errors.append("Hook must contain at least 2 visual directives matching speech beats.")

        for idx, beat in enumerate(hook.visual_directives):
            if not beat.beat_id.strip():
                errors.append(f"Visual directive at index {idx} requires a valid beat_id.")
            if not beat.visual_instruction.strip():
                errors.append(f"Visual directive '{beat.beat_id}' requires a visual instruction.")

        if errors:
            return ValidationResult(status="blocked", errors=errors)

        return ValidationResult(status="valid")
