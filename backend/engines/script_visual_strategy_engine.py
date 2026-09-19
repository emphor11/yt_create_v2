from dataclasses import dataclass
from typing import Any

from pydantic import ValidationError

from domain.generate_video_request import DurationProfile
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
                },
                "required": [
                    "idea_id",
                    "title",
                    "focus_concept",
                    "core_teaching_point",
                    "narration",
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
        duration_profile: DurationProfile = DurationProfile.SHORT_2MIN,
    ) -> ScriptVisualStrategyResult:
        system_content = load_prompt("script_visual_strategy_system.txt")
        is_long_5min = (
            str(duration_profile) == str(DurationProfile.LONG_5MIN)
            or duration_profile == "long_5min"
        )
        if is_long_5min:
            budget_instructions = (
                "4. 5-MINUTE BUDGET: Target roughly 85 to 95 words of natural spoken narration per idea, "
                "prioritizing natural spoken delivery and an overall total of roughly 700-800 narration words across all ideas and the hook.\n"
                "5. NARRATIVE FLOW: Maintain coherent story progression across all ideas without repeating facts or statistics.\n"
                "6. Generate a highly detailed body script conforming exactly to the response schema and these requirements."
            )
        else:
            budget_instructions = (
                "4. Keep each idea's narration to roughly 40-70 words.\n"
                "5. Generate a highly detailed body script conforming exactly to the response schema and these requirements."
            )

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
                        f"Hook: {hook.model_dump()}\n\n"
                        f"--- STRICT RESEARCH CONTEXT & FACTS ---\n"
                        f"Verified Concepts: {research_packet.concepts}\n"
                        f"Verified Facts: {research_packet.verified_facts}\n"
                        f"Verified Statistics: {research_packet.statistics}\n\n"
                        f"CRITICAL INSTRUCTIONS:\n"
                        f"1. For each idea's 'focus_concept', you MUST choose exactly one concept from the 'Verified Concepts' list above. Do NOT make up new concepts or use phrasing not present in that list.\n"
                        f"2. Any numbers or statistics you mention in the narration text MUST be strictly verified and present in 'Verified Facts' or 'Verified Statistics'. Do NOT invent or use any other numbers (except common small numbers/indexes like 1, 2, 3, etc.).\n"
                        f"3. You MUST generate exactly one output 'idea' in the 'ideas' array for every 'scene_beat' provided in the Narrative Plan. Maintain their exact chronological order, titles, focus concepts, and core teaching points, while filling in the 'narration' field.\n"
                        f"{budget_instructions}"
                    ),
                ),
            ],
            temperature=0.5,
            max_tokens=8192,
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
