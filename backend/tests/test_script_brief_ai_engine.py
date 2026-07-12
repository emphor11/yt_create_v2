import pytest

from domain.topic_request import TopicRequest
from engines.script_brief_ai_engine import ScriptBriefAIEngine, ScriptBriefAIEngineError
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


def valid_ai_script_brief_payload() -> dict:
    return {
        "schema_version": "1",
        "topic": "Why Monthly Payments Feel Cheap",
        "angle": "How EMIs hide total cost",
        "thesis": (
            "Monthly payments make an expensive phone feel cheaper by shrinking "
            "the moment of payment pain."
        ),
        "primary_mechanisms": [
            "payment_pain_reduction",
            "affordability_illusion",
        ],
        "recurring_example": "₹80,000 phone",
        "scene_functions": [
            {
                "scene_id": "scene_01",
                "label": "full_price_vs_monthly_payment",
                "mechanism": "payment_pain_reduction",
                "purpose": (
                    "Show the full phone price beside the EMI so the viewer can see "
                    "how the smaller monthly number changes perception."
                ),
            }
        ],
    }


def test_script_brief_ai_engine_returns_script_brief_from_json_response() -> None:
    provider = StaticTestLLMProvider(valid_ai_script_brief_payload())
    engine = ScriptBriefAIEngine(provider)

    result = engine.run(
        TopicRequest(
            topic="Why Monthly Payments Feel Cheap",
            angle="How EMIs hide total cost",
        )
    )

    assert result.script_brief.recurring_example == "₹80,000 phone"
    assert result.provider_metadata.provider == "static-test"
    assert result.raw_payload["topic"] == "Why Monthly Payments Feel Cheap"
    assert provider.last_request is not None
    assert provider.last_request.schema_name == "ScriptBrief"
    assert provider.last_request.messages[0].role == "system"
    assert provider.last_request.messages[1].content == (
        "Topic: Why Monthly Payments Feel Cheap\n"
        "Angle: How EMIs hide total cost\n"
        "Create one scene function for scene_01."
    )


def test_script_brief_ai_engine_raises_for_invalid_script_brief_shape() -> None:
    provider = StaticTestLLMProvider(
        {
            "topic": "Why Monthly Payments Feel Cheap",
            "angle": "How EMIs hide total cost",
        }
    )
    engine = ScriptBriefAIEngine(provider)

    with pytest.raises(ScriptBriefAIEngineError, match="invalid ScriptBrief JSON") as error:
        engine.run(
            TopicRequest(
                topic="Why Monthly Payments Feel Cheap",
                angle="How EMIs hide total cost",
            )
        )

    assert error.value.raw_payload == {
        "topic": "Why Monthly Payments Feel Cheap",
        "angle": "How EMIs hide total cost",
    }
    assert error.value.provider_metadata is not None
