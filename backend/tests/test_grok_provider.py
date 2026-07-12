import pytest

from providers.grok_provider import GrokProvider
from providers.llm_provider import LLMJsonRequest, LLMMessage, LLMProviderError


def make_request() -> LLMJsonRequest:
    return LLMJsonRequest(
        schema_name="ResearchPacket",
        response_schema={
            "type": "object",
            "properties": {
                "topic": {"type": "string"},
            },
            "required": ["topic"],
        },
        messages=[
            LLMMessage(role="system", content="Return JSON only."),
            LLMMessage(role="user", content="Research topic."),
        ],
        temperature=0.1,
        max_tokens=500,
    )


def test_grok_provider_builds_payload() -> None:
    provider = GrokProvider(api_key="test-grok-key", model="grok-test")
    payload = provider._build_payload(make_request())

    assert payload["model"] == "grok-test"
    assert payload["temperature"] == 0.1
    assert payload["max_tokens"] == 500
    assert payload["response_format"] == {"type": "json_object"}
    assert payload["messages"] == [
        {"role": "system", "content": "Return JSON only."},
        {"role": "user", "content": "Research topic."},
    ]


def test_grok_provider_parses_json_response(monkeypatch) -> None:
    provider = GrokProvider(api_key="test-grok-key", model="grok-test")

    def mock_post_chat_completions(_payload):
        return {
            "choices": [
                {
                    "finish_reason": "stop",
                    "message": {
                        "role": "assistant",
                        "content": '{"topic": "Reframing Prices"}',
                    },
                }
            ],
            "usage": {
                "prompt_tokens": 15,
                "completion_tokens": 10,
            },
        }

    monkeypatch.setattr(provider, "_post_chat_completions", mock_post_chat_completions)

    response = provider.generate_json(make_request())

    assert response.payload == {
        "topic": "Reframing Prices",
    }
    assert response.metadata.provider == "grok"
    assert response.metadata.model == "grok-test"
    assert response.metadata.raw_metadata["finish_reason"] == "stop"
    assert response.metadata.raw_metadata["usage_metadata"] == {
        "prompt_tokens": 15,
        "completion_tokens": 10,
    }


def test_grok_provider_raises_error_on_non_json(monkeypatch) -> None:
    provider = GrokProvider(api_key="test-grok-key", model="grok-test")

    def mock_post_chat_completions(_payload):
        return {
            "choices": [
                {
                    "finish_reason": "stop",
                    "message": {
                        "role": "assistant",
                        "content": "Plain text response",
                    },
                }
            ]
        }

    monkeypatch.setattr(provider, "_post_chat_completions", mock_post_chat_completions)

    with pytest.raises(LLMProviderError, match="Grok returned non-JSON text"):
        provider.generate_json(make_request())
