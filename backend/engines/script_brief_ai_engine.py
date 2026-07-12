from dataclasses import dataclass
from typing import Any

from pydantic import ValidationError

from domain.script_brief import ScriptBrief
from domain.topic_request import TopicRequest
from providers.llm_provider import (
    LLMJsonRequest,
    LLMMessage,
    LLMProvider,
    LLMProviderError,
    LLMProviderMetadata,
)


SCRIPT_BRIEF_RESPONSE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "schema_version": {
            "type": "string",
            "description": "Schema version. Use 1.",
        },
        "topic": {
            "type": "string",
            "description": "Must exactly match the TopicRequest topic.",
        },
        "angle": {
            "type": "string",
            "description": "Must exactly match the TopicRequest angle.",
        },
        "thesis": {
            "type": "string",
            "description": "The central claim the video will prove.",
        },
        "primary_mechanisms": {
            "type": "array",
            "items": {
                "type": "string",
                "enum": [
                    "payment_pain_reduction",
                    "affordability_illusion",
                ],
            },
            "description": "Supported finance mechanisms for the MVP.",
        },
        "recurring_example": {
            "type": "string",
            "description": "Must be exactly ₹80,000 phone for the MVP.",
        },
        "scene_functions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "scene_id": {"type": "string"},
                    "label": {"type": "string"},
                    "mechanism": {
                        "type": "string",
                        "enum": [
                            "payment_pain_reduction",
                            "affordability_illusion",
                        ],
                    },
                    "purpose": {"type": "string"},
                },
                "required": [
                    "scene_id",
                    "label",
                    "mechanism",
                    "purpose",
                ],
            },
            "description": "One scene function for scene_01.",
        },
    },
    "required": [
        "schema_version",
        "topic",
        "angle",
        "thesis",
        "primary_mechanisms",
        "recurring_example",
        "scene_functions",
    ],
    "additionalProperties": False,
}


@dataclass(frozen=True)
class ScriptBriefAIResult:
    script_brief: ScriptBrief
    provider_metadata: LLMProviderMetadata
    raw_payload: dict[str, Any]


class ScriptBriefAIEngineError(Exception):
    def __init__(
        self,
        message: str,
        *,
        raw_payload: dict[str, Any] | None = None,
        provider_metadata: LLMProviderMetadata | None = None,
    ):
        super().__init__(message)
        self.raw_payload = raw_payload or {}
        self.provider_metadata = provider_metadata


from app.assets import load_prompt


class ScriptBriefAIEngine:
    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider

    def run(self, topic_request: TopicRequest) -> ScriptBriefAIResult:
        system_content = load_prompt("script_brief_system.txt")
        request = LLMJsonRequest(
            schema_name="ScriptBrief",
            response_schema=SCRIPT_BRIEF_RESPONSE_SCHEMA,
            messages=[
                LLMMessage(
                    role="system",
                    content=system_content,
                ),
                LLMMessage(
                    role="user",
                    content=(
                        f"Topic: {topic_request.topic}\n"
                        f"Angle: {topic_request.angle}\n"
                        "Create one scene function for scene_01."
                    ),
                ),
            ],
            temperature=0.2,
            max_tokens=1200,
        )
        try:
            response = self.llm_provider.generate_json(request)
        except LLMProviderError as error:
            raise ScriptBriefAIEngineError(str(error)) from error

        try:
            script_brief = ScriptBrief.model_validate(response.payload)
        except ValidationError as error:
            raise ScriptBriefAIEngineError(
                "LLM returned invalid ScriptBrief JSON.",
                raw_payload=response.payload,
                provider_metadata=response.metadata,
            ) from error

        return ScriptBriefAIResult(
            script_brief=script_brief,
            provider_metadata=response.metadata,
            raw_payload=response.payload,
        )
