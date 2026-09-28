from domain.narrative_plan import NarrativePlan
from domain.validation import ValidationResult


class NarrativePlanValidator:
    def validate(self, plan: NarrativePlan) -> ValidationResult:
        errors: list[str] = []

        if not plan.thesis.strip():
            errors.append("Thesis is required and cannot be empty.")
        if not plan.target_pain_point.strip():
            errors.append("Target pain point is required.")
        if not plan.conceptual_hook.strip():
            errors.append("Conceptual hook is required.")
        if not plan.narrative_arc_type.strip():
            errors.append("Narrative arc type is required.")

        if plan.central_tension and not plan.central_tension.strip():
            errors.append("Central tension cannot be empty whitespace.")
        if plan.starting_belief and not plan.starting_belief.strip():
            errors.append("Starting belief cannot be empty whitespace.")
        if plan.ending_understanding and not plan.ending_understanding.strip():
            errors.append("Ending understanding cannot be empty whitespace.")

        if len(plan.scene_beats) < 3:
            errors.append("Narrative plan must contain at least 3 scene beats (e.g. Hook, Body, Conclusion).")

        for idx, beat in enumerate(plan.scene_beats):
            if not beat.scene_id.strip():
                errors.append(f"Scene beat at index {idx} requires a valid scene_id.")
            if not beat.title.strip():
                errors.append(f"Scene beat '{beat.scene_id}' requires a title.")
            if not beat.focus_concept.strip():
                errors.append(f"Scene beat '{beat.scene_id}' requires a focus concept.")
            if not beat.core_teaching_point.strip():
                errors.append(f"Scene beat '{beat.scene_id}' requires a core teaching point.")
            if beat.scene_role and not beat.scene_role.strip():
                errors.append(f"Scene beat '{beat.scene_id}' requires a non-empty scene_role.")
            if beat.viewer_question and not beat.viewer_question.strip():
                errors.append(f"Scene beat '{beat.scene_id}' requires a non-empty viewer_question.")

        if errors:
            return ValidationResult(status="blocked", errors=errors)

        return ValidationResult(status="valid")
