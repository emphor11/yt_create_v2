from domain.script_brief import SceneFunction, ScriptBrief
from domain.topic_request import TopicRequest


class ScriptBriefEngine:
    def run(self, topic_request: TopicRequest) -> ScriptBrief:
        return ScriptBrief(
            topic=topic_request.topic,
            angle=topic_request.angle,
            thesis=(
                "Monthly payments can make an expensive purchase feel cheaper by reducing "
                "payment pain and shifting attention away from the total price."
            ),
            primary_mechanisms=[
                "payment_pain_reduction",
                "affordability_illusion",
            ],
            recurring_example="₹80,000 phone",
            scene_functions=[
                SceneFunction(
                    scene_id="scene_01",
                    label="full_price_vs_monthly_payment",
                    mechanism="payment_pain_reduction",
                    purpose=(
                        "Contrast the full phone price with a monthly EMI framing so the "
                        "viewer sees how affordability can be made to feel smaller."
                    ),
                )
            ],
        )

