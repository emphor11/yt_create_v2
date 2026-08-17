from dataclasses import dataclass
from typing import Any

from pydantic import ValidationError

from domain.research_packet import ResearchPacket
from domain.narrative_plan import NarrativePlan
from domain.hook import Hook
from providers.llm_provider import (
    LLMJsonRequest,
    LLMMessage,
    LLMProvider,
    LLMProviderError,
    LLMProviderMetadata,
)
from app.assets import load_prompt

HOOK_RESPONSE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "conceptual_hook": {"type": "string"},
        "script_text": {"type": "string"},
        "visual_directives": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "beat_id": {"type": "string"},
                    "preferred_component": {"type": "string"},
                    "visual_goal": {"type": "string"},
                    "onscreen_text": {"type": "string"},
                    "asset_query": {"type": "string"},
                    "trigger_word": {"type": "string"},
                    "component_data": {
                        "type": "object",
                        "anyOf": [
                            {
                                "type": "object",
                                "properties": {
                                    "left_role": {"type": "string"},
                                    "left_label": {"type": "string"},
                                    "left_value": {"type": "number"},
                                    "left_unit": {"type": "string"},
                                    "right_role": {"type": "string"},
                                    "right_label": {"type": "string"},
                                    "right_value": {"type": "number"},
                                    "right_unit": {"type": "string"}
                                },
                                "required": [
                                    "left_role", "left_label", "left_value", "left_unit",
                                    "right_role", "right_label", "right_value", "right_unit"
                                ]
                            },
                            {
                                "type": "object",
                                "properties": {
                                    "start_value": {"type": "number"},
                                    "end_value": {"type": "number"},
                                    "label": {"type": "string"},
                                    "unit": {"type": "string"}
                                },
                                "required": ["start_value", "end_value", "label", "unit"]
                            },
                            {
                                "type": "object",
                                "properties": {
                                    "chart_type": {"type": "string"},
                                    "labels": {
                                        "type": "array",
                                        "items": {"type": "string"}
                                    },
                                    "values": {
                                        "type": "array",
                                        "items": {"type": "number"}
                                    }
                                },
                                "required": ["chart_type", "labels", "values"]
                            },
                            {
                                "type": "object",
                                "properties": {
                                    "steps": {
                                        "type": "array",
                                        "items": {"type": "string"}
                                    }
                                },
                                "required": ["steps"]
                            },
                            {
                                "type": "object",
                                "properties": {}
                            }
                        ]
                    },
                },
                "required": ["beat_id"],
            },
        },
    },
    "required": [
        "conceptual_hook",
        "script_text",
        "visual_directives",
    ],
}


@dataclass(frozen=True)
class HookResult:
    hook: Hook
    provider_metadata: LLMProviderMetadata
    raw_payload: dict[str, Any]


class HookEngineError(Exception):
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


class HookEngine:
    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider

    def run(self, research_packet: ResearchPacket, narrative_plan: NarrativePlan) -> HookResult:
        system_content = load_prompt("hook_system.txt")
        llm_request = LLMJsonRequest(
            schema_name="Hook",
            response_schema=HOOK_RESPONSE_SCHEMA,
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
                        f"Target Pain Point: {narrative_plan.target_pain_point}\n"
                        f"Conceptual Hook Analogy: {narrative_plan.conceptual_hook}\n"
                        f"First Scene Beat Focus: {narrative_plan.scene_beats[0].core_teaching_point if narrative_plan.scene_beats else ''}\n"
                        "Generate a highly engaging opening hook script and matching visual directives."
                    ),
                ),
            ],
            temperature=0.3,
            max_tokens=4000,
        )

        try:
            response = self.llm_provider.generate_json(llm_request)
        except LLMProviderError as error:
            raise HookEngineError(str(error)) from error

        try:
            hook = Hook.model_validate(response.payload)
        except ValidationError as error:
            raise HookEngineError(
                "LLM returned invalid Hook JSON.",
                raw_payload=response.payload,
                provider_metadata=response.metadata,
            ) from error

        return HookResult(
            hook=hook,
            provider_metadata=response.metadata,
            raw_payload=response.payload,
        )
