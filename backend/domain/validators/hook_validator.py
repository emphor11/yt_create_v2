from domain.hook import Hook
from domain.validation import ValidationResult
from registries.component_registry import ComponentRegistry


class HookValidator:
    def validate(self, hook: Hook) -> ValidationResult:
        errors: list[str] = []

        if not hook.conceptual_hook or not hook.conceptual_hook.strip():
            errors.append("Hook conceptual description is required.")
        if not hook.script_text or not hook.script_text.strip():
            errors.append("Hook script spoken text is required and cannot be empty.")

        if len(hook.visual_directives) < 2:
            errors.append("Hook must contain at least 2 visual directives matching speech beats.")

        for idx, beat in enumerate(hook.visual_directives):
            if not beat.beat_id.strip():
                errors.append(f"Visual directive at index {idx} requires a valid beat_id.")

            goal_or_inst = beat.get_visual_instruction()
            if not goal_or_inst.strip():
                errors.append(f"Visual directive '{beat.beat_id}' requires a visual instruction or goal.")

            comp = beat.preferred_component.strip() if beat.preferred_component else ""
            if comp and not ComponentRegistry.is_supported(comp):
                supported = sorted(ComponentRegistry.CANONICAL_COMPONENTS.keys())
                errors.append(
                    f"Visual directive '{beat.beat_id}' uses unsupported component '{comp}'. "
                    f"Must choose only from: {', '.join(supported)}."
                )

            # Validate trigger word existence and presence in hook script text
            if idx > 0:
                if not beat.trigger_word or not beat.trigger_word.strip():
                    errors.append(
                        f"Visual directive '{beat.beat_id}' in hook is a subsequent beat and requires trigger_word."
                    )
                else:
                    import re
                    cleaned_word = re.sub(r"[^\w]", "", beat.trigger_word.lower())
                    cleaned_script_words = [re.sub(r"[^\w]", "", w.lower()) for w in hook.script_text.split() if re.sub(r"[^\w]", "", w)]
                    if cleaned_word not in cleaned_script_words:
                        errors.append(
                            f"Visual directive '{beat.beat_id}' in hook has trigger_word '{beat.trigger_word}' which does not exist in the script text."
                        )
                    else:
                        beat.trigger_word = cleaned_word
            else:
                # First beat starts automatically at frame 0; always normalize to None
                beat.trigger_word = None

            # Polymorphic Component Data Validation & Normalization
            if comp and ComponentRegistry.is_supported(comp):
                is_valid, comp_errors, normalized_data = ComponentRegistry.validate_component_data(
                    preferred_component=comp,
                    raw_data=beat.component_data,
                    visual_goal=goal_or_inst,
                    narration_text=hook.script_text,
                )
                if not is_valid:
                    errors.extend(comp_errors)
                else:
                    beat.component_data = normalized_data

        if errors:
            return ValidationResult(status="blocked", errors=errors)

        return ValidationResult(status="valid")
