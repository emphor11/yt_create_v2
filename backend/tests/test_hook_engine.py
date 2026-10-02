import pytest

from domain.generate_video_request import GenerateVideoRequest
from domain.narrative_plan import NarrativePlan, SceneBeat
from engines.hook_engine import HookEngine, HookEngineError
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


def valid_hook_payload() -> dict:
    return {
        "conceptual_hook": "Anchor vs Engine comparison",
        "script_text": "What if rent isn't thrown away?",
    }


def test_hook_engine_returns_valid_hook() -> None:
    provider = StaticTestLLMProvider(valid_hook_payload())
    engine = HookEngine(provider)

    result = engine.run(
        GenerateVideoRequest(
            topic="Why Renting a Home is Often Smarter Than Buying",
            angle="Rent as growth capital",
            audience="retail investors",
            channel="FinanceChannel",
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
    )

    assert result.hook.conceptual_hook == "Anchor vs Engine comparison"
    assert result.hook.script_text == "What if rent isn't thrown away?"
    assert result.hook.visual_directives == []
    assert result.provider_metadata.provider == "static-test"
    assert provider.last_request is not None
    assert provider.last_request.schema_name == "Hook"
    assert provider.last_request.messages[0].role == "system"


def test_hook_engine_schema_has_no_visual_directives() -> None:
    from engines.hook_engine import HOOK_RESPONSE_SCHEMA
    assert "visual_directives" not in HOOK_RESPONSE_SCHEMA["properties"]
    assert HOOK_RESPONSE_SCHEMA["required"] == ["conceptual_hook", "script_text"]


def test_hook_engine_passes_rich_narrative_context() -> None:
    provider = StaticTestLLMProvider(valid_hook_payload())
    engine = HookEngine(provider)

    result = engine.run(
        GenerateVideoRequest(
            topic="Gold Just Hit ₹1.5 Lakh",
            angle="Safe Haven or Panic Trap",
            audience="working professionals",
            channel="MindshiftFinance",
        ),
        NarrativePlan(
            thesis="Gold is an insurance policy, not an explosive growth asset",
            target_pain_point="FOMO buying at peak prices",
            central_tension="Investors rush into gold at all-time highs when the margin of safety is lowest",
            starting_belief="Gold is always safe and guaranteed to make you rich",
            ending_understanding="Gold preserves capital but has high opportunity cost against equities",
            conceptual_hook="The Golden Anchor: safety that holds you in place",
            narrative_arc_type="paradox_resolution",
            scene_beats=[
                SceneBeat(
                    scene_id="scene_01",
                    title="The Record Price Shock",
                    scene_role="problem",
                    viewer_question="Why are retail investors pouring billions into gold right now?",
                    focus_concept="Safe-haven rush",
                    core_teaching_point="Explain the milestone price and surge in ETF inflows",
                    key_evidence=["Domestic gold reached ₹1.5 lakh per 10 grams", "Gold-ETF inflows jumped 67%"],
                )
            ],
        ),
    )

    prompt = provider.last_request.messages[1].content
    assert "Central Tension: Investors rush into gold at all-time highs" in prompt
    assert "Starting Belief: Gold is always safe and guaranteed" in prompt
    assert "Ending Understanding: Gold preserves capital" in prompt
    assert "Conceptual Hook: The Golden Anchor" in prompt
    assert "Scene 01 Role: problem" in prompt
    assert "Scene 01 Viewer Question: Why are retail investors pouring billions into gold right now?" in prompt
    assert "Scene 01 Key Evidence: Domestic gold reached ₹1.5 lakh per 10 grams, Gold-ETF inflows jumped 67%" in prompt


def test_hook_engine_raises_error_for_invalid_shape() -> None:
    provider = StaticTestLLMProvider({"script_text": "Only a script text"})
    engine = HookEngine(provider)

    with pytest.raises(HookEngineError, match="invalid Hook JSON") as exc:
        engine.run(
            GenerateVideoRequest(
                topic="Why Renting a Home is Often Smarter Than Buying",
                angle="Rent as growth capital",
                audience="retail investors",
                channel="FinanceChannel",
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
        )

    assert exc.value.raw_payload == {"script_text": "Only a script text"}
    assert exc.value.provider_metadata is not None


def test_hook_engine_supports_voice_cues() -> None:
    payload = {
        "conceptual_hook": "The Rent Myth",
        "script_text": "What if your monthly EMI is secretly doubling your costs?",
        "voice_cues": [
            {
                "anchor": "secretly doubling",
                "pause_after_ms": 350,
                "volume_db": 2,
            }
        ],
    }

    provider = StaticTestLLMProvider(payload)
    engine = HookEngine(provider)

    result = engine.run(
        GenerateVideoRequest(
            topic="Why Renting is Smarter",
            angle="Cash flow",
            audience="working professionals",
            channel="WealthUnpacked",
        ),
        NarrativePlan(
            thesis="Renting preserves capital",
            target_pain_point="Hidden EMI cost",
            conceptual_hook="The Rent Myth",
            narrative_arc_type="PSA",
            scene_beats=[
                SceneBeat(
                    scene_id="scene_01",
                    title="Intro",
                    focus_concept="Opportunity Cost",
                    core_teaching_point="Show EMI cost",
                )
            ],
        ),
    )

    assert len(result.hook.voice_cues) == 1
    assert result.hook.voice_cues[0].anchor == "secretly doubling"
    assert result.hook.voice_cues[0].pause_after_ms == 350
    assert result.hook.voice_cues[0].volume_db == 2
