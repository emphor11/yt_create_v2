from domain.script_visual_strategy import ScriptVisualStrategy
from domain.validation import ValidationResult


class ScriptVisualStrategyValidator:
    def validate(self, strategy: ScriptVisualStrategy) -> ValidationResult:
        errors: list[str] = []

        if not strategy.thesis.strip():
            errors.append("Script strategy core thesis is required.")
        if not strategy.ideas:
            errors.append("Script strategy must contain at least 1 video idea.")

        for idea_idx, idea in enumerate(strategy.ideas):
            if not idea.idea_id.strip():
                errors.append(f"Video idea at index {idea_idx} requires an idea_id.")
            if not idea.title.strip():
                errors.append(f"Video idea '{idea.idea_id}' requires a title.")
            if not idea.focus_concept.strip():
                errors.append(f"Video idea '{idea.idea_id}' requires a focus concept.")
            if not idea.core_teaching_point.strip():
                errors.append(f"Video idea '{idea.idea_id}' requires a core teaching point.")
            if not idea.narration.strip():
                errors.append(f"Video idea '{idea.idea_id}' requires narration text.")

        if errors:
            return ValidationResult(status="blocked", errors=errors)

        return ValidationResult(status="valid")
