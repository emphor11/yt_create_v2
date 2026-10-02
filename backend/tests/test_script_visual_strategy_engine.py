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
                "narration": "Let's compare the actual unrecoverable costs between renting and buying.",
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
    assert result.strategy.ideas[0].narration == "Let's compare the actual unrecoverable costs between renting and buying."
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


def test_strategy_engine_preserves_narrative_lineage_and_hook_context() -> None:
    provider = StaticTestLLMProvider(valid_strategy_payload())
    engine = ScriptVisualStrategyEngine(provider)

    packet = ResearchPacket(
        topic="Gold Investment Risks",
        audience="salaried professionals",
        channel="MindshiftFinance",
        verified_facts=["Gold hit ₹1.5 lakh per 10g", "Gold-ETF inflows surged 67%"],
        statistics=["Domestic CAGR 10.2%"],
        concepts=["Opportunity Cost", "Safe-Haven Asset"],
    )
    plan = NarrativePlan(
        thesis="Gold preserves capital but lags equities in the long run",
        target_pain_point="FOMO buying at peak prices",
        central_tension="Investors rush into gold at all-time highs when safety margin is lowest",
        starting_belief="Gold is guaranteed to make you rich quickly",
        ending_understanding="Gold is portfolio insurance, not a wealth multiplier",
        conceptual_hook="The Golden Anchor",
        narrative_arc_type="paradox_resolution",
        scene_beats=[
            SceneBeat(
                scene_id="scene_01",
                title="The Record Price Shock",
                scene_role="problem",
                viewer_question="Why are retail investors pouring billions into gold right now?",
                focus_concept="Safe-Haven Asset",
                core_teaching_point="Explain the milestone price and surge in ETF inflows",
                key_evidence=["Gold hit ₹1.5 lakh per 10g", "Gold-ETF inflows surged 67%"],
            )
        ],
    )
    hook = Hook(
        conceptual_hook="The Golden Anchor",
        script_text="When gold crosses one-and-a-half lakh rupees, panic sets in.",
    )

    result = engine.run(packet, plan, hook)

    # 1. Assert prompt formatting
    assert provider.last_request is not None
    prompt = provider.last_request.messages[1].content
    assert "Central Tension: Investors rush into gold at all-time highs" in prompt
    assert 'Spoken Hook Script: "When gold crosses one-and-a-half lakh rupees, panic sets in."' in prompt
    assert "DO NOT REPEAT" in prompt
    assert 'Role: problem' in prompt
    assert 'Viewer Question: "Why are retail investors pouring billions into gold right now?"' in prompt
    assert 'Key Evidence: [\'Gold hit ₹1.5 lakh per 10g\', \'Gold-ETF inflows surged 67%\']' in prompt

    # 2. Assert lineage backfilled onto VideoIdea
    idea = result.strategy.ideas[0]
    assert idea.scene_role == "problem"
    assert idea.viewer_question == "Why are retail investors pouring billions into gold right now?"
    assert idea.key_evidence == ["Gold hit ₹1.5 lakh per 10g", "Gold-ETF inflows surged 67%"]


def test_strategy_engine_supports_voice_cues() -> None:
    payload = {
        "thesis": "Compounding requires time over contribution",
        "ideas": [
            {
                "idea_id": "idea_01",
                "title": "The Time Advantage",
                "focus_concept": "Compound Interest",
                "core_teaching_point": "Starting five years earlier beats doubling monthly investment later",
                "narration": "On paper, investing more feels like the safest route. Until you calculate the lost time.",
                "voice_cues": [
                    {
                        "anchor": "safest route.",
                        "pause_after_ms": 400,
                    },
                    {
                        "anchor": "lost time.",
                        "rate": 94,
                        "volume_db": 2,
                    },
                    {
                        "anchor": "₹5,000",
                        "pronunciation": "five thousand rupees",
                    },
                ],
            }
        ],
    }

    provider = StaticTestLLMProvider(payload)
    engine = ScriptVisualStrategyEngine(provider)

    packet = ResearchPacket(
        topic="Compounding",
        audience="retail investors",
        channel="WealthUnpacked",
        concepts=["Compound Interest"],
    )
    plan = NarrativePlan(
        thesis="Compounding requires time",
        target_pain_point="Delayed start",
        conceptual_hook="Time vs Capital",
        narrative_arc_type="Mechanism",
        scene_beats=[
            SceneBeat(
                scene_id="scene_01",
                title="The Time Advantage",
                focus_concept="Compound Interest",
                core_teaching_point="Starting five years earlier beats doubling monthly investment later",
            )
        ],
    )
    hook = Hook(
        conceptual_hook="Time vs Capital",
        script_text="What happens when you delay your SIP by five years?",
    )

    result = engine.run(packet, plan, hook)

    idea = result.strategy.ideas[0]
    assert len(idea.voice_cues) == 3
    assert idea.voice_cues[0].anchor == "safest route."
    assert idea.voice_cues[0].pause_after_ms == 400
    assert idea.voice_cues[1].anchor == "lost time."
    assert idea.voice_cues[1].rate == 94
    assert idea.voice_cues[1].volume_db == 2
    assert idea.voice_cues[2].anchor == "₹5,000"
    assert idea.voice_cues[2].pronunciation == "five thousand rupees"
