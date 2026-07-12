from __future__ import annotations

import json
from typing import Any
from urllib import error, request

from providers.llm_provider import (
    LLMJsonRequest,
    LLMJsonResponse,
    LLMMessage,
    LLMProviderError,
    LLMProviderMetadata,
)


class GeminiProvider:
    def __init__(
        self,
        *,
        api_key: str,
        model: str = "gemini-3.5-flash",
        api_base_url: str = "https://generativelanguage.googleapis.com/v1beta",
        timeout_seconds: int = 60,
    ):
        normalized_api_key = api_key.strip()
        if not normalized_api_key:
            raise ValueError("Gemini API key is required.")
        self.api_key = normalized_api_key
        self.model = model
        self.api_base_url = api_base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def generate_json(self, llm_request: LLMJsonRequest) -> LLMJsonResponse:
        payload = self._build_payload(llm_request)
        raw_response = self._post_generate_content(payload)
        text = self._extract_text(raw_response)
        try:
            parsed_payload = json.loads(text)
        except json.JSONDecodeError as error:
            raise LLMProviderError("Gemini returned non-JSON text.") from error

        return LLMJsonResponse(
            payload=parsed_payload,
            metadata=LLMProviderMetadata(
                provider="gemini",
                model=self.model,
                raw_metadata={
                    "finish_reason": self._finish_reason(raw_response),
                    "usage_metadata": raw_response.get("usageMetadata", {}),
                    "schema_name": llm_request.schema_name,
                },
            ),
        )

    def _build_payload(self, llm_request: LLMJsonRequest) -> dict[str, Any]:
        system_instruction = self._system_instruction(llm_request.messages)
        contents = self._contents(llm_request.messages)
        if not contents:
            raise LLMProviderError("Gemini request requires at least one non-system message.")

        generation_config: dict[str, Any] = {
            "temperature": llm_request.temperature,
            "maxOutputTokens": llm_request.max_tokens,
            "responseFormat": {
                "text": {
                    "mimeType": "application/json",
                    "schema": llm_request.response_schema or {"type": "object"},
                }
            },
        }

        payload: dict[str, Any] = {
            "contents": contents,
            "generationConfig": generation_config,
        }
        if system_instruction is not None:
            payload["system_instruction"] = system_instruction
        return payload

    def _post_generate_content(self, payload: dict[str, Any]) -> dict[str, Any]:
        url = f"{self.api_base_url}/models/{self.model}:generateContent"
        http_request = request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "x-goog-api-key": self.api_key,
            },
            method="POST",
        )
        try:
            with request.urlopen(http_request, timeout=self.timeout_seconds) as response:
                response_body = response.read().decode("utf-8")
        except error.HTTPError as http_error:
            response_body = http_error.read().decode("utf-8", errors="replace")
            raise LLMProviderError(
                f"Gemini API request failed with status {http_error.code}: {response_body}"
            ) from http_error
        except error.URLError as url_error:
            raise LLMProviderError(f"Gemini API request failed: {url_error.reason}") from url_error

        try:
            return json.loads(response_body)
        except json.JSONDecodeError as decode_error:
            raise LLMProviderError("Gemini API returned invalid JSON response.") from decode_error

    @staticmethod
    def _system_instruction(messages: list[LLMMessage]) -> dict[str, Any] | None:
        system_text = "\n\n".join(
            message.content for message in messages if message.role == "system"
        ).strip()
        if not system_text:
            return None
        return {"parts": [{"text": system_text}]}

    @staticmethod
    def _contents(messages: list[LLMMessage]) -> list[dict[str, Any]]:
        contents: list[dict[str, Any]] = []
        for message in messages:
            if message.role == "system":
                continue
            role = "model" if message.role == "assistant" else "user"
            contents.append(
                {
                    "role": role,
                    "parts": [{"text": message.content}],
                }
            )
        return contents

    @staticmethod
    def _extract_text(response_body: dict[str, Any]) -> str:
        try:
            return response_body["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError, TypeError) as error:
            raise LLMProviderError("Gemini API response did not contain text output.") from error

    @staticmethod
    def _finish_reason(response_body: dict[str, Any]) -> str | None:
        try:
            return response_body["candidates"][0].get("finishReason")
        except (KeyError, IndexError, TypeError):
            return None
