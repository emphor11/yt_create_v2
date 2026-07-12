import pytest

from app import dependencies
from providers.gemini_provider import GeminiProvider
from providers.llm_provider import LLMJsonRequest, LLMMessage, LLMProviderError


def clear_dependency_caches() -> None:
    dependencies.get_llm_provider.cache_clear()
    dependencies._load_backend_dotenv.cache_clear()


def make_request() -> LLMJsonRequest:
    return LLMJsonRequest(
        schema_name="ScriptBrief",
        response_schema={
            "type": "object",
            "properties": {
                "thesis": {"type": "string"},
            },
            "required": ["thesis"],
        },
        messages=[
            LLMMessage(role="system", content="Return JSON only."),
            LLMMessage(role="user", content="Create a script brief."),
            LLMMessage(role="assistant", content='{"draft": true}'),
        ],
        temperature=0.1,
        max_tokens=500,
    )


def test_gemini_provider_builds_structured_output_payload() -> None:
    provider = GeminiProvider(api_key="test-key", model="gemini-test")

    payload = provider._build_payload(make_request())

    assert payload["system_instruction"] == {
        "parts": [{"text": "Return JSON only."}]
    }
    assert payload["contents"] == [
        {
            "role": "user",
            "parts": [{"text": "Create a script brief."}],
        },
        {
            "role": "model",
            "parts": [{"text": '{"draft": true}'}],
        },
    ]
    assert payload["generationConfig"] == {
        "temperature": 0.1,
        "maxOutputTokens": 500,
        "responseFormat": {
            "text": {
                "mimeType": "application/json",
                "schema": {
                    "type": "object",
                    "properties": {
                        "thesis": {"type": "string"},
                    },
                    "required": ["thesis"],
                },
            }
        },
    }


def test_gemini_provider_parses_json_text_response(monkeypatch) -> None:
    provider = GeminiProvider(api_key="test-key", model="gemini-test")

    def post_generate_content(_payload):
        return {
            "candidates": [
                {
                    "finishReason": "STOP",
                    "content": {
                        "parts": [
                            {"text": '{"thesis": "Monthly payments reduce payment pain."}'}
                        ]
                    },
                }
            ],
            "usageMetadata": {
                "promptTokenCount": 20,
                "candidatesTokenCount": 8,
            },
        }

    monkeypatch.setattr(provider, "_post_generate_content", post_generate_content)

    response = provider.generate_json(make_request())

    assert response.payload == {
        "thesis": "Monthly payments reduce payment pain.",
    }
    assert response.metadata.provider == "gemini"
    assert response.metadata.model == "gemini-test"
    assert response.metadata.raw_metadata == {
        "finish_reason": "STOP",
        "usage_metadata": {
            "promptTokenCount": 20,
            "candidatesTokenCount": 8,
        },
        "schema_name": "ScriptBrief",
    }


def test_gemini_provider_rejects_empty_api_key() -> None:
    with pytest.raises(ValueError, match="Gemini API key is required"):
        GeminiProvider(api_key=" ")


def test_gemini_provider_rejects_non_json_text(monkeypatch) -> None:
    provider = GeminiProvider(api_key="test-key")

    def post_generate_content(_payload):
        return {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {"text": "not json"}
                        ]
                    }
                }
            ]
        }

    monkeypatch.setattr(provider, "_post_generate_content", post_generate_content)

    with pytest.raises(LLMProviderError, match="non-JSON"):
        provider.generate_json(make_request())


def test_dependency_uses_gemini_provider_when_api_key_exists(monkeypatch) -> None:
    clear_dependency_caches()
    monkeypatch.setenv("YTCREATE_ENV_FILE", "/tmp/ytcreate-v2-missing-env")
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setenv("GEMINI_MODEL", "gemini-test")

    provider = dependencies.get_llm_provider()

    assert isinstance(provider, GeminiProvider)
    assert provider.model == "gemini-test"
    clear_dependency_caches()


def test_dependency_has_no_provider_without_api_key(monkeypatch) -> None:
    clear_dependency_caches()
    monkeypatch.setenv("YTCREATE_ENV_FILE", "/tmp/ytcreate-v2-missing-env")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)

    provider = dependencies.get_llm_provider()

    assert provider is None
    clear_dependency_caches()


def test_dependency_loads_gemini_provider_from_env_file(tmp_path, monkeypatch) -> None:
    clear_dependency_caches()
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "GEMINI_API_KEY=file-key",
                'GEMINI_MODEL="gemini-file-model"',
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("YTCREATE_ENV_FILE", str(env_file))
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_MODEL", raising=False)

    provider = dependencies.get_llm_provider()

    assert isinstance(provider, GeminiProvider)
    assert provider.api_key == "file-key"
    assert provider.model == "gemini-file-model"
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_MODEL", raising=False)
    clear_dependency_caches()


def test_env_file_does_not_override_exported_values(tmp_path, monkeypatch) -> None:
    clear_dependency_caches()
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "GEMINI_API_KEY=file-key",
                "GEMINI_MODEL=file-model",
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("YTCREATE_ENV_FILE", str(env_file))
    monkeypatch.setenv("GEMINI_API_KEY", "exported-key")
    monkeypatch.setenv("GEMINI_MODEL", "exported-model")

    provider = dependencies.get_llm_provider()

    assert isinstance(provider, GeminiProvider)
    assert provider.api_key == "exported-key"
    assert provider.model == "exported-model"
    clear_dependency_caches()


def test_dependency_accepts_google_api_key_alias(tmp_path, monkeypatch) -> None:
    clear_dependency_caches()
    monkeypatch.setenv("YTCREATE_ENV_FILE", "/tmp/ytcreate-v2-missing-env")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.setenv("GOOGLE_API_KEY", "google-key")

    provider = dependencies.get_llm_provider()

    assert isinstance(provider, GeminiProvider)
    assert provider.api_key == "google-key"
    clear_dependency_caches()
