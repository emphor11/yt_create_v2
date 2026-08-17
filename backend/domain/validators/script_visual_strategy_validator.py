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

                # Validate trigger word existence and presence in narration
                if beat_idx > 0:
                    if not beat.trigger_word or not beat.trigger_word.strip():
                        errors.append(
                            f"Visual beat '{beat.beat_id}' in idea '{idea.idea_id}' is a subsequent beat and requires trigger_word."
                        )
                    else:
                        import re
                        cleaned_word = re.sub(r"[^\w]", "", beat.trigger_word.lower())
                        cleaned_narration_words = [re.sub(r"[^\w]", "", w.lower()) for w in idea.narration.split() if re.sub(r"[^\w]", "", w)]
                        if cleaned_word not in cleaned_narration_words:
                            errors.append(
                                f"Visual beat '{beat.beat_id}' in idea '{idea.idea_id}' has trigger_word '{beat.trigger_word}' which does not exist in the narration text."
                            )
                else:
                    # First beat can have trigger_word, but if it exists, validate it is in the narration text
                    if beat.trigger_word and beat.trigger_word.strip() and beat.trigger_word.lower() not in ("null", "none"):
                        import re
                        cleaned_word = re.sub(r"[^\w]", "", beat.trigger_word.lower())
                        cleaned_narration_words = [re.sub(r"[^\w]", "", w.lower()) for w in idea.narration.split() if re.sub(r"[^\w]", "", w)]
                        if cleaned_word not in cleaned_narration_words:
                            errors.append(
                                f"Visual beat '{beat.beat_id}' in idea '{idea.idea_id}' has trigger_word '{beat.trigger_word}' which does not exist in the narration text."
                            )

                # Conditional validations based on selected component type
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
                elif comp == "NumberCounter":
                    data = beat.component_data
                    for field in ["label", "unit"]:
                        val = data.get(field, "")
                        if val is not None and not isinstance(val, str):
                            errors.append(f"NumberCounter beat '{beat.beat_id}' requires string '{field}'.")
                    for field in ["start_value", "end_value"]:
                        val = data.get(field)
                        if not isinstance(val, (int, float)):
                            errors.append(f"NumberCounter beat '{beat.beat_id}' requires numeric '{field}'.")
                elif comp == "Charts":
                    data = beat.component_data
                    chart_type = data.get("chart_type", "")
                    if not isinstance(chart_type, str) or chart_type not in ["bar", "pie", "line"]:
                        errors.append(f"Charts beat '{beat.beat_id}' requires chart_type to be 'bar', 'pie', or 'line'.")
                    labels = data.get("labels")
                    if not isinstance(labels, list) or not all(isinstance(l, str) for l in labels):
                        errors.append(f"Charts beat '{beat.beat_id}' requires labels to be a list of strings.")
                    values = data.get("values")
                    if not isinstance(values, list) or not all(isinstance(v, (int, float)) for v in values):
                        errors.append(f"Charts beat '{beat.beat_id}' requires values to be a list of numbers.")
                elif comp == "Timeline":
                    data = beat.component_data
                    steps = data.get("steps")
                    if not isinstance(steps, list) or not all(isinstance(s, str) for s in steps):
                        errors.append(f"Timeline beat '{beat.beat_id}' requires steps to be a list of strings.")

        if errors:
            return ValidationResult(status="blocked", errors=errors)

        return ValidationResult(status="valid")
