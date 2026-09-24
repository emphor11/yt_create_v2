from __future__ import annotations

import json
import logging
import os
import re
import socket
import time
from typing import Any
from urllib import error, request

logger = logging.getLogger(__name__)

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
        model: str | None = None,
        api_base_url: str = "https://generativelanguage.googleapis.com/v1beta",
        timeout_seconds: int = 120,
        max_retries: int = 5,
    ):
        normalized_api_key = api_key.strip()
        if not normalized_api_key:
            raise ValueError("Gemini API key is required.")
        
        target_model = (model or os.getenv("GEMINI_MODEL", "")).strip()
        if not target_model:
            target_model = os.getenv("GEMINI_MODEL", "gemini-3.6-flash").strip()
            
        self.api_key = normalized_api_key
        self.model = target_model
        self.api_base_url = api_base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries

    def generate_json(self, llm_request: LLMJsonRequest) -> LLMJsonResponse:
        payload = self._build_payload(llm_request)
        raw_response = self._post_generate_content(payload)
        finish_reason = self._finish_reason(raw_response)
        text = self._extract_text(raw_response).strip()
        
        # Clean markdown code block wrapping if present
        if text.startswith("```json"):
            text = text.removeprefix("```json").removesuffix("```").strip()
        elif text.startswith("```"):
            text = text.removeprefix("```").removesuffix("```").strip()

        # Pre-process text to collapse repeating phrase loops if an LLM hallucination loop occurred
        text = self._collapse_phrase_loops(text)

        try:
            parsed_payload = json.loads(text)
        except json.JSONDecodeError as error:
            # Attempt JSON truncation repair by collapsing unclosed runaway strings
            repaired_text = self._attempt_json_repair(text)
            if repaired_text:
                try:
                    parsed_payload = json.loads(repaired_text)
                except json.JSONDecodeError:
                    if finish_reason == "MAX_TOKENS":
                        raise LLMProviderError(
                            f"Gemini output was truncated due to MAX_TOKENS limit ({llm_request.max_tokens} tokens). "
                            f"Raw truncated text ends with: ...{text[-150:]}"
                        ) from error
                    raise LLMProviderError(f"Gemini returned non-JSON text. Raw content: {text}") from error
            else:
                if finish_reason == "MAX_TOKENS":
                    raise LLMProviderError(
                        f"Gemini output was truncated due to MAX_TOKENS limit ({llm_request.max_tokens} tokens). "
                        f"Raw truncated text ends with: ...{text[-150:]}"
                    ) from error
                raise LLMProviderError(f"Gemini returned non-JSON text. Raw content: {text}") from error

        return LLMJsonResponse(
            payload=parsed_payload,
            metadata=LLMProviderMetadata(
                provider="gemini",
                model=self.model,
                raw_metadata={
                    "finish_reason": finish_reason,
                    "usage_metadata": raw_response.get("usageMetadata", {}),
                    "schema_name": llm_request.schema_name,
                },
            ),
        )

    @staticmethod
    def _collapse_phrase_loops(text: str) -> str:
        """Collapse repeating phrase loops (e.g. 'and legacy and impact and influence') caused by LLM output hallucinations."""
        import re
        if not text:
            return text

        def _sub_loop(t: str) -> str:
            # Matches any phrase of 1 to 8 words repeating 2 or more times
            res = re.sub(
                r'(\b[\w\-]+(?:\s+[\w\-]+){0,7}\b)(?:(?:\s*,\s*|\s+)\1){2,}',
                r'\1',
                t,
                flags=re.IGNORECASE,
            )
            # Matches repeating sentence blocks (e.g. 4 sentences repeating 60 times)
            res = re.sub(
                r'([^"\\]{10,250}\.)(?:\s*\1){2,}',
                r'\1',
                res,
                flags=re.IGNORECASE,
            )
            return res

        prev = text
        for _ in range(4):
            curr = _sub_loop(prev)
            if curr == prev:
                break
            prev = curr
        return prev

    @staticmethod
    def _attempt_json_repair(text: str) -> str | None:
        """Attempt simple repair for JSON cut off mid-string or mid-array."""
        import re
        cleaned = text.strip()
        if not cleaned:
            return None

        # 1. Try closing open string quote and open array/object brackets directly
        for suffix in ['"]}]}', '"]}', '"}]}', '"}', ']}', '}']:
            candidate = cleaned + suffix
            try:
                json.loads(candidate)
                return candidate
            except json.JSONDecodeError:
                continue

        # 2. If a runaway string quote was cut off mid-sentence, truncate the runaway string to last complete word and close JSON
        quote_pos = cleaned.rfind('"')
        if quote_pos != -1:
            truncated = cleaned[:quote_pos]
            for suffix in ['"]}]}', '"]}', '"}]}', '"}', ']}', '}']:
                candidate = truncated + suffix
                try:
                    json.loads(candidate)
                    return candidate
                except json.JSONDecodeError:
                    continue

        return None

    def _build_payload(self, llm_request: LLMJsonRequest) -> dict[str, Any]:
        system_instruction = self._system_instruction(llm_request.messages)
        contents = self._contents(llm_request.messages)
        if not contents:
            raise LLMProviderError("Gemini request requires at least one non-system message.")

        generation_config: dict[str, Any] = {
            "temperature": llm_request.temperature,
            "maxOutputTokens": llm_request.max_tokens,
            "responseMimeType": "application/json",
        }
        if llm_request.response_schema:
            generation_config["responseSchema"] = self._clean_schema_for_gemini(
                llm_request.response_schema
            )

        payload: dict[str, Any] = {
            "contents": contents,
            "generationConfig": generation_config,
        }
        if system_instruction is not None:
            payload["system_instruction"] = system_instruction
        return payload

    @staticmethod
    def _clean_schema_for_gemini(schema: dict[str, Any]) -> dict[str, Any]:
        """Recursively dereference '$ref' pointers, remove '$defs'/'definitions',
        and remove 'additionalProperties' since Gemini API v1beta does not support them.
        """
        def _collect_defs(node: Any, defs_map: dict[str, dict[str, Any]]) -> None:
            if isinstance(node, dict):
                for def_key in ("$defs", "definitions"):
                    if def_key in node and isinstance(node[def_key], dict):
                        for k, v in node[def_key].items():
                            if isinstance(v, dict):
                                defs_map[k] = v
                for v in node.values():
                    _collect_defs(v, defs_map)
            elif isinstance(node, list):
                for item in node:
                    _collect_defs(item, defs_map)

        defs_map: dict[str, dict[str, Any]] = {}
        _collect_defs(schema, defs_map)

        def _resolve_and_clean(node: Any, visited_refs: set[str] | None = None) -> Any:
            if visited_refs is None:
                visited_refs = set()

            if not isinstance(node, dict):
                if isinstance(node, list):
                    return [_resolve_and_clean(item, set(visited_refs)) for item in node]
                return node

            if "$ref" in node and isinstance(node["$ref"], str):
                ref_str = node["$ref"]
                ref_name = ref_str.split("/")[-1]
                if ref_name in defs_map and ref_name not in visited_refs:
                    target_def = defs_map[ref_name]
                    merged_node = {k: v for k, v in node.items() if k != "$ref"}
                    for k, v in target_def.items():
                        if k not in merged_node:
                            merged_node[k] = v
                    return _resolve_and_clean(merged_node, visited_refs | {ref_name})

            cleaned: dict[str, Any] = {}
            for k, v in node.items():
                if k in ("additionalProperties", "$defs", "definitions"):
                    continue
                cleaned[k] = _resolve_and_clean(v, set(visited_refs))

            return cleaned

        res = _resolve_and_clean(schema)
        return res if isinstance(res, dict) else {}

    @staticmethod
    def _extract_retry_delay(response_body: str, attempt: int) -> float:
        default_delay = min(30.0, (2.0 ** attempt) + 1.0)
        try:
            data = json.loads(response_body)
            # Check RetryInfo details
            details = data.get("error", {}).get("details", [])
            for item in details:
                if isinstance(item, dict) and "retryDelay" in item:
                    delay_str = str(item["retryDelay"]).rstrip("s")
                    return max(1.0, float(delay_str) + 1.0)
            # Check error message regex e.g. "Please retry in 4.063931228s"
            msg = data.get("error", {}).get("message", "")
            match = re.search(r"retry in ([\d\.]+)s", msg, re.IGNORECASE)
            if match:
                return max(1.0, float(match.group(1)) + 1.0)
        except Exception:
            pass
        return default_delay

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

        response_body: str = ""
        for attempt in range(1, self.max_retries + 1):
            try:
                with request.urlopen(http_request, timeout=self.timeout_seconds) as response:
                    response_body = response.read().decode("utf-8")
                break
            except (TimeoutError, socket.timeout) as timeout_err:
                if attempt >= self.max_retries:
                    raise LLMProviderError(
                        f"Gemini API request timed out after {self.timeout_seconds} seconds."
                    ) from timeout_err
                time.sleep(2.0 * attempt)
            except error.HTTPError as http_error:
                response_body = http_error.read().decode("utf-8", errors="replace")
                if http_error.code in (429, 500, 502, 503, 504) and attempt < self.max_retries:
                    retry_seconds = self._extract_retry_delay(response_body, attempt)
                    if http_error.code != 429:
                        retry_seconds = max(retry_seconds, 3.0 * attempt)
                    logger.warning(
                        f"Gemini API transient error {http_error.code} hit. Waiting {retry_seconds:.1f}s before retry (attempt {attempt}/{self.max_retries})..."
                    )
                    time.sleep(retry_seconds)
                    continue

                raise LLMProviderError(
                    f"Gemini API request failed with status {http_error.code}: {response_body}"
                ) from http_error
            except error.URLError as url_error:
                if attempt >= self.max_retries:
                    raise LLMProviderError(f"Gemini API request failed: {url_error.reason}") from url_error
                time.sleep(2.0 * attempt)

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
