from domain.script_visual_strategy import ScriptVisualStrategy
from domain.validation import ValidationResult
from registries.component_registry import ComponentRegistry


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
                canonical = ComponentRegistry.canonical_name(comp)
                if not comp:
                    errors.append(f"Visual beat '{beat.beat_id}' in idea '{idea.idea_id}' requires preferred_component.")
                elif not ComponentRegistry.is_supported(comp):
                    errors.append(
                        f"Visual beat '{beat.beat_id}' in idea '{idea.idea_id}' uses unsupported component '{comp}'. "
                        f"Must choose only from: {', '.join(sorted(ComponentRegistry.CANONICAL_COMPONENTS.keys()))}."
                    )
                else:
                    # In-place normalize component data
                    _, _, normalized_data = ComponentRegistry.validate_component_data(
                        comp, beat.component_data, visual_goal=beat.visual_goal, narration_text=idea.narration
                    )
                    beat.component_data = normalized_data

                    # ─── Per-component data type checks ───────────────────────
                    # COMMENTED OUT: These manual type checks are redundant with
                    # the Pydantic model validation that already runs above on
                    # line 43 via ComponentRegistry.validate_component_data().
                    # They were also inconsistent with the Pydantic models
                    # (e.g. demanding left_label when prompts output left_role,
                    # requiring left_unit as non-empty when it's optional,
                    # rejecting string left_value when Pydantic accepts it).
                    # Pydantic is the single source of truth for field types.
                    # Re-enable individual checks here only if a specific
                    # validation rule is needed BEYOND what Pydantic enforces.
                    # ──────────────────────────────────────────────────────────
                    # data = beat.component_data or {}
                    # if canonical == "SplitComparison":
                    #     for field in ["left_label", "right_label", "left_unit", "right_unit"]:
                    #         val = data.get(field, "")
                    #         if val is not None and (not isinstance(val, str) or not str(val).strip()):
                    #             errors.append(f"SplitComparison beat '{beat.beat_id}' requires non-empty string '{field}'.")
                    #     for field in ["left_value", "right_value"]:
                    #         val = data.get(field)
                    #         if not isinstance(val, (int, float)) or val <= 0:
                    #             errors.append(f"SplitComparison beat '{beat.beat_id}' requires '{field}' to be greater than 0.")
                    # elif canonical == "NumberCounter":
                    #     for field in ["label", "unit"]:
                    #         val = data.get(field, "")
                    #         if val is not None and not isinstance(val, str):
                    #             errors.append(f"NumberCounter beat '{beat.beat_id}' requires string '{field}'.")
                    #     for field in ["start_value", "end_value"]:
                    #         val = data.get(field)
                    #         if not isinstance(val, (int, float)):
                    #             errors.append(f"NumberCounter beat '{beat.beat_id}' requires numeric '{field}'.")
                    # elif canonical == "Charts":
                    #     chart_type = data.get("chart_type", "")
                    #     if not isinstance(chart_type, str) or chart_type not in ["bar", "pie", "line", "donut", "horizontal_bar"]:
                    #         errors.append(f"Charts beat '{beat.beat_id}' requires chart_type to be 'bar', 'pie', or 'line'.")
                    #     labels = data.get("labels")
                    #     if not isinstance(labels, list) or not all(isinstance(l, str) for l in labels):
                    #         errors.append(f"Charts beat '{beat.beat_id}' requires labels to be a list of strings.")
                    #     values = data.get("values")
                    #     if not isinstance(values, list) or not all(isinstance(v, (int, float)) for v in values):
                    #         errors.append(f"Charts beat '{beat.beat_id}' requires values to be a list of numbers.")
                    # elif canonical == "Timeline":
                    #     events = data.get("events")
                    #     steps = data.get("steps")
                    #     if events is not None:
                    #         if not isinstance(events, list) or not all(isinstance(e, (dict, str)) for e in events):
                    #             errors.append(f"Timeline beat '{beat.beat_id}' requires events to be a list.")
                    #     elif steps is not None:
                    #         if not isinstance(steps, list) or not all(isinstance(s, str) for s in steps):
                    #             errors.append(f"Timeline beat '{beat.beat_id}' requires steps to be a list of strings.")

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

        if errors:
            return ValidationResult(status="blocked", errors=errors)

        return ValidationResult(status="valid")
