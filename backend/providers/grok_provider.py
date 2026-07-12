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


class GrokProvider:
    def __init__(
        self,
        *,
        api_key: str,
        model: str = "grok-2-1212",
        api_base_url: str = "https://api.xai.ai/v1",
        timeout_seconds: int = 60,
    ):
        normalized_api_key = api_key.strip()
        if not normalized_api_key:
            raise ValueError("Grok API key is required.")
        self.api_key = normalized_api_key
        self.model = model
        self.api_base_url = api_base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def generate_json(self, llm_request: LLMJsonRequest) -> LLMJsonResponse:
        payload = self._build_payload(llm_request)
        raw_response = self._post_chat_completions(payload)
        text = self._extract_text(raw_response)
        try:
            parsed_payload = json.loads(text)
        except json.JSONDecodeError as error:
            raise LLMProviderError("Grok returned non-JSON text.") from error

        return LLMJsonResponse(
            payload=parsed_payload,
            metadata=LLMProviderMetadata(
                provider="grok",
                model=self.model,
                raw_metadata={
                    "finish_reason": self._finish_reason(raw_response),
                    "usage_metadata": raw_response.get("usage", {}),
                    "schema_name": llm_request.schema_name,
                },
            ),
        )

    def _build_payload(self, llm_request: LLMJsonRequest) -> dict[str, Any]:
        messages_payload = []
        for msg in llm_request.messages:
            # Map roles: system, user, assistant
            messages_payload.append({
                "role": msg.role,
                "content": msg.content,
            })

        if not messages_payload:
            raise LLMProviderError("Grok request requires at least one message.")

        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages_payload,
            "temperature": llm_request.temperature,
            "max_tokens": llm_request.max_tokens,
            "response_format": {
                "type": "json_object"
            }
        }
        return payload

    def _post_chat_completions(self, payload: dict[str, Any]) -> dict[str, Any]:
        url = f"{self.api_base_url}/chat/completions"
        http_request = request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST",
        )
        try:
            with request.urlopen(http_request, timeout=self.timeout_seconds) as response:
                response_body = response.read().decode("utf-8")
        except error.HTTPError as http_error:
            response_body = http_error.read().decode("utf-8", errors="replace")
            raise LLMProviderError(
                f"Grok API request failed with status {http_error.code}: {response_body}"
            ) from http_error
        except error.URLError as url_error:
            raise LLMProviderError(f"Grok API request failed: {url_error.reason}") from url_error

        try:
            return json.loads(response_body)
        except json.JSONDecodeError as decode_error:
            raise LLMProviderError("Grok API returned invalid JSON response.") from decode_error

    @staticmethod
    def _extract_text(response_body: dict[str, Any]) -> str:
        try:
            return response_body["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as error:
            raise LLMProviderError("Grok API response did not contain message content.") from error

    @staticmethod
    def _finish_reason(response_body: dict[str, Any]) -> str | None:
        try:
            return response_body["choices"][0].get("finish_reason")
        except (KeyError, IndexError, TypeError):
            return None
