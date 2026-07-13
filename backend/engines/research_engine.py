from dataclasses import dataclass
from typing import Any

from pydantic import ValidationError

from domain.generate_video_request import GenerateVideoRequest
from domain.research_packet import ResearchPacket
from providers.llm_provider import (
    LLMJsonRequest,
    LLMMessage,
    LLMProvider,
    LLMProviderError,
    LLMProviderMetadata,
)

RESEARCH_RESPONSE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "topic": {"type": "string"},
        "audience": {"type": "string"},
        "channel": {"type": "string"},
        "verified_facts": {
            "type": "array",
            "items": {"type": "string"},
        },
        "statistics": {
            "type": "array",
            "items": {"type": "string"},
        },
        "concepts": {
            "type": "array",
            "items": {"type": "string"},
        },
        "misconceptions": {
            "type": "array",
            "items": {"type": "string"},
        },
        "examples": {
            "type": "array",
            "items": {"type": "string"},
        },
        "trusted_sources": {
            "type": "array",
            "items": {"type": "string"},
        },
    },
    "required": [
        "topic",
        "audience",
        "channel",
        "verified_facts",
        "statistics",
        "concepts",
        "misconceptions",
        "examples",
        "trusted_sources",
    ],
    "additionalProperties": False,
}


@dataclass(frozen=True)
class ResearchResult:
    research_packet: ResearchPacket
    provider_metadata: LLMProviderMetadata
    raw_payload: dict[str, Any]


class ResearchEngineError(Exception):
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


class ResearchEngine:
    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider

    def run(self, request: GenerateVideoRequest) -> ResearchResult:
        system_content = load_prompt("research_system.txt")
        llm_request = LLMJsonRequest(
            schema_name="ResearchPacket",
            response_schema=RESEARCH_RESPONSE_SCHEMA,
            messages=[
                LLMMessage(
                    role="system",
                    content=system_content,
                ),
                LLMMessage(
                    role="user",
                    content=(
                        f"Topic: {request.topic}\n"
                        f"Audience: {request.audience}\n"
                        f"Channel: {request.channel}\n"
                        "Generate a highly detailed research packet."
                    ),
                ),
            ],
            temperature=0.2,
            max_tokens=4000,
        )

        try:
            response = self.llm_provider.generate_json(llm_request)
        except LLMProviderError as error:
            raise ResearchEngineError(str(error)) from error

        try:
            research_packet = ResearchPacket.model_validate(response.payload)
        except ValidationError as error:
            raise ResearchEngineError(
                "LLM returned invalid ResearchPacket JSON.",
                raw_payload=response.payload,
                provider_metadata=response.metadata,
            ) from error

        return ResearchResult(
            research_packet=research_packet,
            provider_metadata=response.metadata,
            raw_payload=response.payload,
        )
