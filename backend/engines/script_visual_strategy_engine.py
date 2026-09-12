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
from registries.component_registry import ComponentRegistry
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
                            "anyOf": ComponentRegistry.get_polymorphic_beat_schema(is_hook=False),
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
        duration_profile: DurationProfile = DurationProfile.SHORT_2MIN,
    ) -> ScriptVisualStrategyResult:
        system_content = load_prompt("script_visual_strategy_system.txt")
        is_long_5min = (
            str(duration_profile) == str(DurationProfile.LONG_5MIN)
            or duration_profile == "long_5min"
        )
        if is_long_5min:
            budget_instructions = (
                "5. 5-MINUTE BUDGET: Target roughly 85 to 95 words of natural spoken narration per idea, "
                "prioritizing natural spoken delivery and an overall total of roughly 700-800 narration words across all ideas and the hook.\n"
                "6. VISUAL PACING: Plan approximately 5 to 7 visual beats per idea (aiming for roughly 40 to 55 visual beats total across the video).\n"
                "7. NARRATIVE FLOW: Maintain coherent story progression across all ideas without repeating facts or statistics.\n"
                "8. Generate a highly detailed body script and visual strategy conforming exactly to the response schema and these requirements."
            )
        else:
            budget_instructions = (
                "5. Keep each idea's narration to roughly 40-70 words.\n"
                "6. Generate a highly detailed body script and visual strategy conforming exactly to the response schema and these requirements."
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
                        f"2. Any numbers or statistics you mention in the narration text or SplitComparison values MUST be strictly verified and present in 'Verified Facts' or 'Verified Statistics'. Do NOT invent or use any other numbers (except common small numbers/indexes like 1, 2, 3, etc.).\n"
                        f"3. You MUST generate exactly one output 'idea' in the 'ideas' array for every 'scene_beat' provided in the Narrative Plan. Maintain their exact chronological order, titles, focus concepts, and core teaching points, while filling in the 'narration' and 'visual_sequence' fields.\n"
                        f"4. For every visual beat (except the first beat of a sequence which should have trigger_word set to null), you MUST choose a 'trigger_word' present in the narration text. This word defines the exact moment the visual changes on screen.\n"
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

        # Clean and snap any inflected/stemmed trigger words to the exact narration token
        import re
        for idea in strategy.ideas:
            cleaned_narration_words = [
                re.sub(r"[^\w]", "", w.lower())
                for w in idea.narration.split()
                if re.sub(r"[^\w]", "", w)
            ]
            for idx, beat in enumerate(idea.visual_sequence):
                if idx == 0:
                    beat.trigger_word = None
                    continue
                if not beat.trigger_word or not beat.trigger_word.strip():
                    continue
                cw = re.sub(r"[^\w]", "", beat.trigger_word.lower())
                if cw in cleaned_narration_words:
                    beat.trigger_word = cw
                else:
                    matched = None
                    if cw.endswith("s") and cw[:-1] in cleaned_narration_words:
                        matched = cw[:-1]
                    elif cw.endswith("es") and cw[:-2] in cleaned_narration_words:
                        matched = cw[:-2]
                    elif cw.endswith("ed") and cw[:-2] in cleaned_narration_words:
                        matched = cw[:-2]
                    elif cw.endswith("ing") and cw[:-3] in cleaned_narration_words:
                        matched = cw[:-3]
                    elif cw + "s" in cleaned_narration_words:
                        matched = cw + "s"
                    elif cw + "es" in cleaned_narration_words:
                        matched = cw + "es"
                    else:
                        for nw in cleaned_narration_words:
                            if len(nw) >= 4 and len(cw) >= 4 and (nw.startswith(cw) or cw.startswith(nw)):
                                matched = nw
                                break
                    if matched:
                        beat.trigger_word = matched

        return ScriptVisualStrategyResult(
            strategy=strategy,
            provider_metadata=response.metadata,
            raw_payload=response.payload,
        )
