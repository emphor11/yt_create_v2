import pytest

from providers.llm_provider import (
    LLMJsonRequest,
    LLMJsonResponse,
    LLMMessage,
    LLMProvider,
    LLMProviderError,
    LLMProviderMetadata,
)


class ScriptedTestLLMProvider:
    def __init__(self, responses):
        self.requests = []
        self.responses = list(responses)

    def generate_json(self, request: LLMJsonRequest) -> LLMJsonResponse:
        self.requests.append(request)
        if not self.responses:
            raise LLMProviderError("No scripted test response.")
        response = self.responses.pop(0)
        if isinstance(response, LLMProviderError):
            raise response
        if isinstance(response, LLMJsonResponse):
            return response
        return LLMJsonResponse(
            payload=response,
            metadata=LLMProviderMetadata(
                provider="scripted-test",
                model="scripted-test-model",
                raw_metadata={"request_index": len(self.requests) - 1},
            ),
        )


def test_scripted_test_provider_matches_llm_provider_interface() -> None:
    provider = ScriptedTestLLMProvider(
        [
            {
                "schema_name": "ScriptBrief",
                "message_count": 2,
            }
        ]
    )
    request = LLMJsonRequest(
        schema_name="ScriptBrief",
        messages=[
            LLMMessage(role="system", content="Return JSON only."),
            LLMMessage(role="user", content="Create a brief."),
        ],
    )

    response = provider.generate_json(request)

    assert isinstance(provider, LLMProvider)
    assert response.payload == {
        "schema_name": "ScriptBrief",
        "message_count": 2,
    }
    assert response.metadata.provider == "scripted-test"
    assert response.metadata.model == "scripted-test-model"
    assert response.metadata.raw_metadata == {"request_index": 0}
    assert provider.requests == [request]
    assert provider.responses == []


def test_scripted_test_provider_returns_queued_responses_in_order() -> None:
    provider = ScriptedTestLLMProvider(
        [
            {"stage": "script_brief"},
            LLMJsonResponse(
                payload={"stage": "narrative_arc"},
                metadata=LLMProviderMetadata(
                    provider="fixture",
                    model="fixture-model",
                ),
            ),
        ]
    )
    request = LLMJsonRequest(
        schema_name="AnySchema",
        messages=[LLMMessage(role="user", content="Generate JSON.")],
    )

    first_response = provider.generate_json(request)
    second_response = provider.generate_json(request)

    assert first_response.payload == {"stage": "script_brief"}
    assert first_response.metadata.provider == "scripted-test"
    assert second_response.payload == {"stage": "narrative_arc"}
    assert second_response.metadata.provider == "fixture"
    assert provider.requests == [request, request]
    assert provider.responses == []


def test_scripted_test_provider_raises_when_no_response_is_queued() -> None:
    provider = ScriptedTestLLMProvider([])
    request = LLMJsonRequest(
        schema_name="ScriptBrief",
        messages=[LLMMessage(role="user", content="Generate JSON.")],
    )

    with pytest.raises(LLMProviderError, match="No scripted test response"):
        provider.generate_json(request)

    assert provider.requests == [request]


def test_scripted_test_provider_can_simulate_provider_errors() -> None:
    provider = ScriptedTestLLMProvider([LLMProviderError("provider unavailable")])
    request = LLMJsonRequest(
        schema_name="ScriptBrief",
        messages=[LLMMessage(role="user", content="Generate JSON.")],
    )

    with pytest.raises(LLMProviderError, match="provider unavailable"):
        provider.generate_json(request)

    assert provider.requests == [request]
