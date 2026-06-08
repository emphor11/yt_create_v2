from domain.narrative_arc import NarrativeArc
from domain.scene_script import SceneScript, SceneStoryState
from domain.script_brief import ScriptBrief
from domain.script_draft import ScriptDraft


class SceneScriptEngine:
    def run(
        self,
        *,
        script_brief: ScriptBrief,
        narrative_arc: NarrativeArc,
        script_draft: ScriptDraft,
    ) -> SceneScript:
        draft_scene = script_draft.scenes[0]
        scene_function = next(
            scene_function
            for scene_function in script_brief.scene_functions
            if scene_function.scene_id == draft_scene.scene_id
        )
        scene_arc_step = next(
            scene_step
            for scene_step in narrative_arc.scene_arc_steps
            if scene_step.scene_id == draft_scene.scene_id
        )

        return SceneScript(
            scene_id=draft_scene.scene_id,
            topic=script_brief.topic,
            angle=script_brief.angle,
            thesis=script_brief.thesis,
            mechanism=scene_function.mechanism,
            scene_function_label=scene_function.label,
            arc_phases=scene_arc_step.arc_phases,
            narrative_purpose=scene_arc_step.narrative_purpose,
            narration=draft_scene.narration,
            story_state=SceneStoryState(recurring_example=script_brief.recurring_example),
        )
