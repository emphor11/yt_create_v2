from domain.narrative_arc import NarrativeArc
from domain.script_brief import ScriptBrief
from domain.validation import ValidationResult


MVP_ARC = ["curiosity", "comfort", "reversal", "realization"]


class NarrativeArcValidator:
    def validate(
        self,
        narrative_arc: NarrativeArc,
        *,
        script_brief: ScriptBrief,
    ) -> ValidationResult:
        errors: list[str] = []

        if narrative_arc.topic != script_brief.topic:
            errors.append("NarrativeArc topic must match ScriptBrief topic.")
        if narrative_arc.thesis != script_brief.thesis:
            errors.append("NarrativeArc thesis must match ScriptBrief thesis.")
        if not narrative_arc.viewer_question.strip():
            errors.append("Viewer question is required.")
        if narrative_arc.arc != MVP_ARC:
            errors.append("NarrativeArc arc must be curiosity, comfort, reversal, realization.")
        if not narrative_arc.scene_arc_steps:
            errors.append("At least one scene arc step is required.")

        expected_scene_ids = {scene_function.scene_id for scene_function in script_brief.scene_functions}
        actual_scene_ids = {scene_step.scene_id for scene_step in narrative_arc.scene_arc_steps}

        missing_scene_ids = expected_scene_ids - actual_scene_ids
        extra_scene_ids = actual_scene_ids - expected_scene_ids

        for scene_id in sorted(missing_scene_ids):
            errors.append(f"Missing arc step for scene function: {scene_id}.")
        for scene_id in sorted(extra_scene_ids):
            errors.append(f"Arc step references unknown scene: {scene_id}.")

        if not any(scene_step.is_payoff_scene for scene_step in narrative_arc.scene_arc_steps):
            errors.append("At least one payoff scene is required.")

        scene_function_labels = {
            scene_function.scene_id: scene_function.label
            for scene_function in script_brief.scene_functions
        }
        for scene_step in narrative_arc.scene_arc_steps:
            if not scene_step.scene_id.strip():
                errors.append("Scene arc step scene_id is required.")
            if not scene_step.scene_function_label.strip():
                errors.append("Scene arc step scene_function_label is required.")
            if scene_step.scene_id in scene_function_labels:
                expected_label = scene_function_labels[scene_step.scene_id]
                if scene_step.scene_function_label != expected_label:
                    errors.append(
                        f"Arc step label for {scene_step.scene_id} must match ScriptBrief scene function label."
                    )
            if scene_step.arc_phases != MVP_ARC:
                errors.append(
                    f"Arc step {scene_step.scene_id} must include curiosity, comfort, reversal, realization."
                )
            if not scene_step.narrative_purpose.strip():
                errors.append(f"Arc step {scene_step.scene_id} narrative purpose is required.")

        if errors:
            return ValidationResult(status="blocked", errors=errors)

        return ValidationResult(status="valid")

