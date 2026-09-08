import pytest

from domain.research_packet import ResearchPacket
from domain.narrative_plan import NarrativePlan, SceneBeat
from domain.hook import Hook, VisualDirective as HookVisualDirective
from engines.script_visual_strategy_engine import ScriptVisualStrategyEngine, ScriptVisualStrategyEngineError
from providers.llm_provider import LLMJsonRequest, LLMJsonResponse, LLMProviderMetadata


class StaticTestLLMProvider:
    def __init__(self, payload: dict):
        self.payload = payload
        self.last_request: LLMJsonRequest | None = None

    def generate_json(self, request: LLMJsonRequest) -> LLMJsonResponse:
        self.last_request = request
        return LLMJsonResponse(
            payload=self.payload,
            metadata=LLMProviderMetadata(
                provider="static-test",
                model="static-test-model",
            ),
        )


def valid_strategy_payload() -> dict:
    return {
        "thesis": "Renting beats buying in urban markets",
        "ideas": [
            {
                "idea_id": "idea_01",
                "title": "Cost Contrast",
                "focus_concept": "Opportunity Cost",
                "core_teaching_point": "Show unrecoverable housing expenses",
                "narration": "Let's compare the actual unrecoverable costs.",
                "visual_sequence": [
                    {
                        "beat_id": "beat_01",
                        "preferred_component": "SplitComparison",
                        "visual_goal": "Compare rent vs buying unrecoverable costs",
                        "component_data": {
                            "left_role": "product_price",
                            "left_label": "Rent cost",
                            "left_value": 30000,
                            "left_unit": "INR",
                            "right_role": "monthly_payment",
                            "right_label": "Buy cost",
                            "right_value": 75000,
                            "right_unit": "INR",
                        },
                    },
                    {
                        "beat_id": "beat_02",
                        "preferred_component": "Typography",
                        "visual_goal": "Show text overlays",
                        "trigger_word": "actual",
                    },
                ],
            }
        ],
    }


def test_strategy_engine_returns_valid_strategy() -> None:
    provider = StaticTestLLMProvider(valid_strategy_payload())
    engine = ScriptVisualStrategyEngine(provider)

    result = engine.run(
        ResearchPacket(
            topic="Renting vs Buying",
            audience="young professionals",
            channel="FinanceShorts",
            verified_facts=["Rent cost is lower in initial years."],
            statistics=["Rental yield is 2-3%"],
            concepts=["Opportunity Cost"],
        ),
        NarrativePlan(
            thesis="Renting is smarter",
            target_pain_point="Anxiety",
            conceptual_hook="Anchor vs Engine",
            narrative_arc_type="PSA",
            scene_beats=[
                SceneBeat(
                    scene_id="scene_01",
                    title="Intro",
                    focus_concept="Opportunity Cost",
                    core_teaching_point="Introduce opportunity cost",
                )
            ],
        ),
        Hook(
            conceptual_hook="Anchor vs Engine",
            script_text="Is renting throwing money away?",
            visual_directives=[
                HookVisualDirective(beat_id="beat_01", visual_instruction="Show anchor sinking"),
                HookVisualDirective(beat_id="beat_02", visual_instruction="Show rocket engine igniting"),
            ],
        ),
    )

    assert result.strategy.thesis == "Renting beats buying in urban markets"
    assert len(result.strategy.ideas) == 1
    assert result.strategy.ideas[0].idea_id == "idea_01"
    assert len(result.strategy.ideas[0].visual_sequence) == 2
    assert result.provider_metadata.provider == "static-test"


def test_strategy_engine_raises_error_for_invalid_shape() -> None:
    provider = StaticTestLLMProvider({"ideas": []})
    engine = ScriptVisualStrategyEngine(provider)

    with pytest.raises(ScriptVisualStrategyEngineError, match="invalid ScriptVisualStrategy JSON") as exc:
        engine.run(
            ResearchPacket(
                topic="Renting vs Buying",
                audience="young professionals",
                channel="FinanceShorts",
                verified_facts=["Rent cost is lower in initial years."],
                statistics=["Rental yield is 2-3%"],
                concepts=["Opportunity Cost"],
            ),
            NarrativePlan(
                thesis="Renting is smarter",
                target_pain_point="Anxiety",
                conceptual_hook="Anchor vs Engine",
                narrative_arc_type="PSA",
                scene_beats=[
                    SceneBeat(
                        scene_id="scene_01",
                        title="Intro",
                        focus_concept="Opportunity Cost",
                        core_teaching_point="Introduce opportunity cost",
                    )
                ],
            ),
            Hook(
                conceptual_hook="Anchor vs Engine",
                script_text="Is renting throwing money away?",
                visual_directives=[
                    HookVisualDirective(beat_id="beat_01", visual_instruction="Show anchor sinking"),
                    HookVisualDirective(beat_id="beat_02", visual_instruction="Show rocket engine igniting"),
                ],
            ),
        )


    assert exc.value.raw_payload == {"ideas": []}
    assert exc.value.provider_metadata is not None


def test_strategy_engine_5min_profile_prompts_budget_and_beats() -> None:
    from domain.generate_video_request import DurationProfile

    provider = StaticTestLLMProvider(valid_strategy_payload())
    engine = ScriptVisualStrategyEngine(provider)

    packet = ResearchPacket(
        topic="Renting vs Buying",
        audience="young professionals",
        channel="FinanceShorts",
        verified_facts=["Rent cost is lower in initial years."],
        statistics=["Rental yield is 2-3%"],
        concepts=["Opportunity Cost"],
    )
    plan = NarrativePlan(
        thesis="Renting is smarter",
        target_pain_point="Anxiety",
        conceptual_hook="Anchor vs Engine",
        narrative_arc_type="PSA",
        scene_beats=[
            SceneBeat(
                scene_id="scene_01",
                title="Intro",
                focus_concept="Opportunity Cost",
                core_teaching_point="Introduce opportunity cost",
            )
        ],
    )
    hook = Hook(
        conceptual_hook="Anchor vs Engine",
        script_text="Is renting throwing money away?",
        visual_directives=[
            HookVisualDirective(beat_id="beat_01", visual_instruction="Show anchor sinking"),
        ],
    )

    # 1. Default (short_2min)
    engine.run(packet, plan, hook)
    assert provider.last_request is not None
    user_msg_short = provider.last_request.messages[1].content
    assert "Keep each idea's narration to roughly 40-70 words." in user_msg_short
    assert "5-MINUTE BUDGET" not in user_msg_short

    # 2. Long 5min profile
    engine.run(packet, plan, hook, duration_profile=DurationProfile.LONG_5MIN)
    assert provider.last_request is not None
    user_msg_long = provider.last_request.messages[1].content
    assert "5-MINUTE BUDGET" in user_msg_long
    assert "85 to 95 words" in user_msg_long
    assert "700-800 narration words" in user_msg_long
    assert "5 to 7 visual beats per idea" in user_msg_long
    assert "40 to 55 visual beats total" in user_msg_long
