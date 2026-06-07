from domain.narrative_arc import NarrativeArc
from domain.script_brief import ScriptBrief
from domain.script_draft import ScriptDraft
from domain.validation import ValidationResult


FORBIDDEN_LATER_STAGE_KEYS = {
    "semantic_entities",
    "entities",
    "relationships",
    "visual_events",
    "component",
    "props",
    "timed_spans",
    "render_spec",
    "frames",
}


class ScriptDraftValidator:
    def validate(
        self,
        script_draft: ScriptDraft,
        *,
        script_brief: ScriptBrief,
        narrative_arc: NarrativeArc,
    ) -> ValidationResult:
        errors: list[str] = []

        if script_draft.topic != script_brief.topic:
            errors.append("ScriptDraft topic must match ScriptBrief topic.")
        if script_draft.angle != script_brief.angle:
            errors.append("ScriptDraft angle must match ScriptBrief angle.")
        if script_draft.thesis != script_brief.thesis:
            errors.append("ScriptDraft thesis must match ScriptBrief thesis.")
        if narrative_arc.topic != script_brief.topic:
            errors.append("NarrativeArc topic must match ScriptBrief topic.")
        if narrative_arc.thesis != script_brief.thesis:
            errors.append("NarrativeArc thesis must match ScriptBrief thesis.")

        if not script_draft.hook.strip():
            errors.append("ScriptDraft hook is required.")
        if not script_draft.outro.strip():
            errors.append("ScriptDraft outro is required.")
        if not script_draft.scenes:
            errors.append("At least one draft scene is required.")

        brief_scene_ids = [scene_function.scene_id for scene_function in script_brief.scene_functions]
        arc_scene_ids = [scene_step.scene_id for scene_step in narrative_arc.scene_arc_steps]
        draft_scene_ids = [draft_scene.scene_id for draft_scene in script_draft.scenes]

        if draft_scene_ids != brief_scene_ids:
            errors.append("ScriptDraft scene order must match ScriptBrief scene functions.")
        if draft_scene_ids != arc_scene_ids:
            errors.append("ScriptDraft scene order must match NarrativeArc scene steps.")

        brief_labels = {
            scene_function.scene_id: scene_function.label
            for scene_function in script_brief.scene_functions
        }
        arc_labels = {
            scene_step.scene_id: scene_step.scene_function_label
            for scene_step in narrative_arc.scene_arc_steps
        }

        for draft_scene in script_draft.scenes:
            if not draft_scene.scene_id.strip():
                errors.append("Draft scene scene_id is required.")
            if not draft_scene.scene_function_label.strip():
                errors.append(f"Draft scene {draft_scene.scene_id} scene_function_label is required.")
            if not draft_scene.narration.strip():
                errors.append(f"Draft scene {draft_scene.scene_id} narration is required.")

            if draft_scene.scene_id in brief_labels:
                expected_label = brief_labels[draft_scene.scene_id]
                if draft_scene.scene_function_label != expected_label:
                    errors.append(
                        f"Draft scene label for {draft_scene.scene_id} must match ScriptBrief scene function label."
                    )
            if draft_scene.scene_id in arc_labels:
                expected_label = arc_labels[draft_scene.scene_id]
                if draft_scene.scene_function_label != expected_label:
                    errors.append(
                        f"Draft scene label for {draft_scene.scene_id} must match NarrativeArc scene function label."
                    )

        combined_narration = " ".join(
            [script_draft.hook, *[scene.narration for scene in script_draft.scenes], script_draft.outro]
        )
        if "₹80,000" not in combined_narration or "phone" not in combined_narration.lower():
            errors.append("ScriptDraft must keep the recurring example: ₹80,000 phone.")
        if "EMI" not in combined_narration and "monthly" not in combined_narration.lower():
            errors.append("ScriptDraft must stay focused on monthly payment framing.")

        leaked_keys = FORBIDDEN_LATER_STAGE_KEYS.intersection(script_draft.model_dump().keys())
        if leaked_keys:
            errors.append(
                "ScriptDraft must not contain later-stage fields: "
                + ", ".join(sorted(leaked_keys))
                + "."
            )

        if errors:
            return ValidationResult(status="blocked", errors=errors)

        return ValidationResult(status="valid")
