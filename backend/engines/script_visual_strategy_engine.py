from dataclasses import dataclass
from typing import Any

from pydantic import ValidationError

from domain.research_packet import ResearchPacket
from domain.narrative_plan import NarrativePlan
from domain.hook import Hook
from domain.script_visual_strategy import ScriptVisualStrategy
from providers.llm_provider import (
    LLMJsonRequest,
    LLMMessage,
    LLMProvider,
    LLMProviderError,
    LLMProviderMetadata,
)
from app.assets import load_prompt

SCRIPT_VISUAL_STRATEGY_RESPONSE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "thesis": {"type": "string"},
        "ideas": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "idea_id": {"type": "string"},
                    "title": {"type": "string"},
                    "focus_concept": {"type": "string"},
                    "core_teaching_point": {"type": "string"},
                    "narration": {"type": "string"},
                    "visual_sequence": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "beat_id": {"type": "string"},
                                "preferred_component": {"type": "string"},
                                "visual_goal": {"type": "string"},
                                "asset_query": {"type": "string"},
                                "notes": {"type": "string"},
                                "component_data": {"type": "object"},
                            },
                            "required": ["beat_id", "preferred_component", "visual_goal"],
                        },
                    },
                },
                "required": [
                    "idea_id",
                    "title",
                    "focus_concept",
                    "core_teaching_point",
                    "narration",
                    "visual_sequence",
                ],
            },
        },
    },
    "required": ["thesis", "ideas"],
}


@dataclass(frozen=True)
class ScriptVisualStrategyResult:
    strategy: ScriptVisualStrategy
    provider_metadata: LLMProviderMetadata
    raw_payload: dict[str, Any]


class ScriptVisualStrategyEngineError(Exception):
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


class ScriptVisualStrategyEngine:
    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider

    def run(
        self,
        research_packet: ResearchPacket,
        narrative_plan: NarrativePlan,
        hook: Hook,
    ) -> ScriptVisualStrategyResult:
        system_content = load_prompt("script_visual_strategy_system.txt")
        llm_request = LLMJsonRequest(
            schema_name="ScriptVisualStrategy",
            response_schema=SCRIPT_VISUAL_STRATEGY_RESPONSE_SCHEMA,
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
                        f"Thesis: {narrative_plan.thesis}\n"
                        f"Narrative Plan: {narrative_plan.model_dump()}\n"
                        f"Hook: {hook.model_dump()}\n"
                        "Generate a highly detailed body script and visual strategy."
                    ),
                ),
            ],
            temperature=0.2,
            max_tokens=4000,
        )

        try:
            response = self.llm_provider.generate_json(llm_request)
        except LLMProviderError as error:
            raise ScriptVisualStrategyEngineError(str(error)) from error

        try:
            strategy = ScriptVisualStrategy.model_validate(response.payload)
        except ValidationError as error:
            raise ScriptVisualStrategyEngineError(
                "LLM returned invalid ScriptVisualStrategy JSON.",
                raw_payload=response.payload,
                provider_metadata=response.metadata,
            ) from error

        return ScriptVisualStrategyResult(
            strategy=strategy,
            provider_metadata=response.metadata,
            raw_payload=response.payload,
        )
