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
            if not beat.get_visual_instruction().strip():
                errors.append(f"Visual directive '{beat.beat_id}' requires a visual instruction or goal.")
            
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
                # First beat can have trigger_word, but if it exists, validate it is in the script text
                if beat.trigger_word and beat.trigger_word.strip() and beat.trigger_word.lower() not in ("null", "none"):
                    import re
                    cleaned_word = re.sub(r"[^\w]", "", beat.trigger_word.lower())
                    cleaned_script_words = [re.sub(r"[^\w]", "", w.lower()) for w in hook.script_text.split() if re.sub(r"[^\w]", "", w)]
                    if cleaned_word not in cleaned_script_words:
                        errors.append(
                            f"Visual directive '{beat.beat_id}' in hook has trigger_word '{beat.trigger_word}' which does not exist in the script text."
                        )

        if errors:
            return ValidationResult(status="blocked", errors=errors)

        return ValidationResult(status="valid")
