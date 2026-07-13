from dataclasses import dataclass
from typing import Any

from pydantic import ValidationError

from domain.research_packet import ResearchPacket
from domain.narrative_plan import NarrativePlan
from providers.llm_provider import (
    LLMJsonRequest,
    LLMMessage,
    LLMProvider,
    LLMProviderError,
    LLMProviderMetadata,
)
from app.assets import load_prompt

NARRATIVE_PLAN_RESPONSE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "thesis": {"type": "string"},
        "target_pain_point": {"type": "string"},
        "conceptual_hook": {"type": "string"},
        "narrative_arc_type": {"type": "string"},
        "scene_beats": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "scene_id": {"type": "string"},
                    "title": {"type": "string"},
                    "focus_concept": {"type": "string"},
                    "core_teaching_point": {"type": "string"},
                },
                "required": ["scene_id", "title", "focus_concept", "core_teaching_point"],
            },
        },
    },
    "required": [
        "thesis",
        "target_pain_point",
        "conceptual_hook",
        "narrative_arc_type",
        "scene_beats",
    ],
}


@dataclass(frozen=True)
class NarrativePlanResult:
    narrative_plan: NarrativePlan
    provider_metadata: LLMProviderMetadata
    raw_payload: dict[str, Any]


class NarrativePlanEngineError(Exception):
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


class NarrativePlanEngine:
    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider

    def run(self, research_packet: ResearchPacket) -> NarrativePlanResult:
        system_content = load_prompt("narrative_plan_system.txt")
        llm_request = LLMJsonRequest(
            schema_name="NarrativePlan",
            response_schema=NARRATIVE_PLAN_RESPONSE_SCHEMA,
            messages=[
                LLMMessage(
                    role="system",
                    content=system_content,
                ),
                LLMMessage(
                    role="user",
                    content=(
                        f"Topic: {research_packet.topic}\n"
                        f"Audience: {research_packet.audience}\n"
                        f"Channel: {research_packet.channel}\n"
                        f"Verified Facts: {research_packet.verified_facts}\n"
                        f"Statistics: {research_packet.statistics}\n"
                        f"Concepts: {research_packet.concepts}\n"
                        f"Misconceptions: {research_packet.misconceptions}\n"
                        f"Examples: {research_packet.examples}\n"
                        f"Trusted Sources: {research_packet.trusted_sources}\n"
                        "Generate a highly structured narrative plan."
                    ),
                ),
            ],
            temperature=0.2,
            max_tokens=4000,
        )

        try:
            response = self.llm_provider.generate_json(llm_request)
        except LLMProviderError as error:
            raise NarrativePlanEngineError(str(error)) from error

        try:
            narrative_plan = NarrativePlan.model_validate(response.payload)
        except ValidationError as error:
            raise NarrativePlanEngineError(
                "LLM returned invalid NarrativePlan JSON.",
                raw_payload=response.payload,
                provider_metadata=response.metadata,
            ) from error

        return NarrativePlanResult(
            narrative_plan=narrative_plan,
            provider_metadata=response.metadata,
            raw_payload=response.payload,
        )
