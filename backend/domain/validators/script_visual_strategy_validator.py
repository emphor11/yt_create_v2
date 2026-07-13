from domain.script_visual_strategy import ScriptVisualStrategy
from domain.validation import ValidationResult

SUPPORTED_COMPONENTS = {
    "SplitComparison",
    "Timeline",
    "NumberCounter",
    "Charts",
    "Stock Image",
    "Stock Video",
    "Typography",
    "Icon Animation",
}


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
            if not idea.narration.strip():
                errors.append(f"Video idea '{idea.idea_id}' requires narration text.")

            if not idea.visual_sequence:
                errors.append(f"Video idea '{idea.idea_id}' requires at least 1 visual beat.")

            for beat_idx, beat in enumerate(idea.visual_sequence):
                if not beat.beat_id.strip():
                    errors.append(f"Visual beat at index {beat_idx} in idea '{idea.idea_id}' requires beat_id.")
                
                comp = beat.preferred_component.strip()
                if not comp:
                    errors.append(f"Visual beat '{beat.beat_id}' in idea '{idea.idea_id}' requires preferred_component.")
                elif comp not in SUPPORTED_COMPONENTS:
                    errors.append(
                        f"Visual beat '{beat.beat_id}' in idea '{idea.idea_id}' uses unsupported component '{comp}'. "
                        f"Must choose only from: {', '.join(sorted(SUPPORTED_COMPONENTS))}."
                    )

                if not beat.visual_goal.strip():
                    errors.append(f"Visual beat '{beat.beat_id}' in idea '{idea.idea_id}' requires a visual_goal.")

                # If SplitComparison, ensure the structured data is present for rendering
                if comp == "SplitComparison":
                    data = beat.component_data
                    for field in ["left_label", "right_label", "left_unit", "right_unit"]:
                        val = data.get(field, "")
                        if not isinstance(val, str) or not val.strip():
                            errors.append(f"SplitComparison beat '{beat.beat_id}' requires non-empty string '{field}'.")
                    for field in ["left_value", "right_value"]:
                        val = data.get(field)
                        if not isinstance(val, (int, float)) or val <= 0:
                            errors.append(f"SplitComparison beat '{beat.beat_id}' requires '{field}' to be greater than 0.")

        if errors:
            return ValidationResult(status="blocked", errors=errors)

        return ValidationResult(status="valid")
