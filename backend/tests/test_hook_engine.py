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
        "visual_directives": [
            {
                "beat_id": "beat_01",
                "visual_instruction": "Show anchor sliding down",
                "trigger_word": None,
            },
            {
                "beat_id": "beat_02",
                "visual_instruction": "Show engine blasting off",
                "trigger_word": "rent",
            },
        ],
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
    assert len(result.hook.visual_directives) == 2
    assert result.provider_metadata.provider == "static-test"
    assert provider.last_request is not None
    assert provider.last_request.schema_name == "Hook"
    assert provider.last_request.messages[0].role == "system"


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
