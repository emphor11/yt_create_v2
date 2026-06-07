from domain.narrative_arc import NarrativeArc
from domain.script_brief import ScriptBrief
from domain.script_draft import DraftScene, ScriptDraft


class ScriptDraftEngine:
    def run(
        self,
        *,
        script_brief: ScriptBrief,
        narrative_arc: NarrativeArc,
    ) -> ScriptDraft:
        return ScriptDraft(
            topic=script_brief.topic,
            angle=script_brief.angle,
            thesis=script_brief.thesis,
            hook=(
                "An ₹80,000 phone sounds expensive. But when the same phone is shown as "
                "₹6,667 per month, it suddenly feels easier to say yes."
            ),
            scenes=[
                DraftScene(
                    scene_id=scene_step.scene_id,
                    scene_function_label=scene_step.scene_function_label,
                    narration=(
                        "The phone costs ₹80,000. But the EMI is shown as ₹6,667 per month. "
                        "The total price did not become smaller; the pain of paying just got "
                        "split into a number your brain can accept more easily."
                    ),
                )
                for scene_step in narrative_arc.scene_arc_steps
            ],
            outro=(
                "That is the trick of monthly payments: they do not only change when you pay, "
                "they change how expensive the purchase feels."
            ),
        )
