from domain.narrative_arc import NarrativeArc, SceneArcStep
from domain.script_brief import ScriptBrief


class NarrativeArcEngine:
    def run(self, script_brief: ScriptBrief) -> NarrativeArc:
        return NarrativeArc(
            topic=script_brief.topic,
            thesis=script_brief.thesis,
            viewer_question=(
                "If the phone costs ₹80,000, why does ₹6,667 per month feel easier to accept?"
            ),
            arc=["curiosity", "comfort", "reversal", "realization"],
            scene_arc_steps=[
                SceneArcStep(
                    scene_id=scene_function.scene_id,
                    scene_function_label=scene_function.label,
                    arc_phases=["curiosity", "comfort", "reversal", "realization"],
                    narrative_purpose=(
                        "Move the viewer from noticing the smaller EMI number to realizing "
                        "that monthly framing reduces the pain of the full price."
                    ),
                    is_payoff_scene=True,
                )
                for scene_function in script_brief.scene_functions
            ],
        )

