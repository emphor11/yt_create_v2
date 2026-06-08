from domain.narrative_arc import NarrativeArc
from domain.scene_script import SceneScript
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


class SceneScriptValidator:
    def validate(
        self,
        scene_script: SceneScript,
        *,
        script_brief: ScriptBrief,
        narrative_arc: NarrativeArc,
        script_draft: ScriptDraft,
    ) -> ValidationResult:
        errors: list[str] = []

        if scene_script.topic != script_brief.topic:
            errors.append("SceneScript topic must match ScriptBrief topic.")
        if scene_script.angle != script_brief.angle:
            errors.append("SceneScript angle must match ScriptBrief angle.")
        if scene_script.thesis != script_brief.thesis:
            errors.append("SceneScript thesis must match ScriptBrief thesis.")
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

        if not scene_script.scene_id.strip():
            errors.append("SceneScript scene_id is required.")
        if not scene_script.mechanism.strip():
            errors.append("SceneScript mechanism is required.")
        if not scene_script.scene_function_label.strip():
            errors.append("SceneScript scene_function_label is required.")
        if not scene_script.narrative_purpose.strip():
            errors.append("SceneScript narrative_purpose is required.")
        if not scene_script.narration.strip():
            errors.append("SceneScript narration is required.")
        if not scene_script.story_state.recurring_example.strip():
            errors.append("SceneScript story_state.recurring_example is required.")

        scene_function = next(
            (
                candidate
                for candidate in script_brief.scene_functions
                if candidate.scene_id == scene_script.scene_id
            ),
            None,
        )
        scene_arc_step = next(
            (
                candidate
                for candidate in narrative_arc.scene_arc_steps
                if candidate.scene_id == scene_script.scene_id
            ),
            None,
        )
        draft_scene = next(
            (
                candidate
                for candidate in script_draft.scenes
                if candidate.scene_id == scene_script.scene_id
            ),
            None,
        )

        if scene_function is None:
            errors.append(f"SceneScript references unknown ScriptBrief scene: {scene_script.scene_id}.")
        else:
            if scene_script.mechanism != scene_function.mechanism:
                errors.append(
                    f"SceneScript mechanism for {scene_script.scene_id} must match ScriptBrief scene function."
                )
            if scene_script.scene_function_label != scene_function.label:
                errors.append(
                    f"SceneScript label for {scene_script.scene_id} must match ScriptBrief scene function label."
                )

        if scene_arc_step is None:
            errors.append(f"SceneScript references unknown NarrativeArc scene: {scene_script.scene_id}.")
        else:
            if scene_script.scene_function_label != scene_arc_step.scene_function_label:
                errors.append(
                    f"SceneScript label for {scene_script.scene_id} must match NarrativeArc scene function label."
                )
            if scene_script.arc_phases != scene_arc_step.arc_phases:
                errors.append(
                    f"SceneScript arc phases for {scene_script.scene_id} must match NarrativeArc arc phases."
                )
            if scene_script.narrative_purpose != scene_arc_step.narrative_purpose:
                errors.append(
                    f"SceneScript narrative purpose for {scene_script.scene_id} must match NarrativeArc."
                )

        if draft_scene is None:
            errors.append(f"SceneScript references unknown ScriptDraft scene: {scene_script.scene_id}.")
        else:
            if scene_script.scene_function_label != draft_scene.scene_function_label:
                errors.append(
                    f"SceneScript label for {scene_script.scene_id} must match ScriptDraft scene function label."
                )
            if scene_script.narration != draft_scene.narration:
                errors.append(
                    f"SceneScript narration for {scene_script.scene_id} must match ScriptDraft scene narration."
                )

        if scene_script.story_state.recurring_example != script_brief.recurring_example:
            errors.append("SceneScript story_state.recurring_example must match ScriptBrief recurring example.")

        leaked_keys = FORBIDDEN_LATER_STAGE_KEYS.intersection(scene_script.model_dump().keys())
        if leaked_keys:
            errors.append(
                "SceneScript must not contain later-stage fields: "
                + ", ".join(sorted(leaked_keys))
                + "."
            )

        if errors:
            return ValidationResult(status="blocked", errors=errors)

        return ValidationResult(status="valid")
