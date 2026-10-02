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
                    "scene_role": {"type": "string"},
                    "viewer_question": {"type": "string"},
                    "focus_concept": {"type": "string"},
                    "core_teaching_point": {"type": "string"},
                    "key_evidence": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "narration": {"type": "string"},
                    "voice_cues": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "cue_id": {"type": "string"},
                                "anchor": {"type": "string"},
                                "pause_before_ms": {"type": "integer"},
                                "pause_after_ms": {"type": "integer"},
                                "rate_percent": {"type": "integer"},
                                "rate": {"type": "integer"},
                                "volume_db": {"type": "integer"},
                                "pronunciation": {"type": "string"},
                            },
                            "required": ["anchor"],
                        },
                    },
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
                "5-MINUTE BUDGET: Target roughly 85 to 95 words of natural spoken narration per idea, "
                "prioritizing natural spoken delivery and an overall total of roughly 700-800 narration words across all ideas and the hook.\n"
                "NARRATIVE FLOW: Maintain coherent story progression across all ideas without repeating facts or statistics."
            )
        else:
            budget_instructions = (
                "Keep each idea's narration to roughly 40-70 words."
            )

        user_prompt_lines = [
            f"Topic: {research_packet.topic}",
            f"Audience: {research_packet.audience}",
            f"Channel: {research_packet.channel}",
            f"Thesis: {narrative_plan.thesis}",
        ]
        if narrative_plan.central_tension:
            user_prompt_lines.append(f"Central Tension: {narrative_plan.central_tension}")
        if narrative_plan.starting_belief:
            user_prompt_lines.append(f"Starting Belief: {narrative_plan.starting_belief}")
        if narrative_plan.ending_understanding:
            user_prompt_lines.append(f"Ending Understanding: {narrative_plan.ending_understanding}")
        if narrative_plan.narrative_arc_type:
            user_prompt_lines.append(f"Narrative Arc Type: {narrative_plan.narrative_arc_type}")

        user_prompt_lines.append("\n--- SPOKEN OPENING HOOK (ALREADY WRITTEN - DO NOT REPEAT) ---")
        user_prompt_lines.append(f"Conceptual Hook: {hook.conceptual_hook}")
        user_prompt_lines.append(f'Spoken Hook Script: "{hook.script_text}"')

        user_prompt_lines.append("\n--- NARRATIVE PLAN STORY ARCHITECTURE ---")
        user_prompt_lines.append("Planned Scene Beats (Generate exactly one idea per scene beat in exact order):")
        for idx, beat in enumerate(narrative_plan.scene_beats):
            beat_desc = f"- Scene {idx + 1} ({beat.scene_id}): Title: \"{beat.title}\""
            if beat.scene_role:
                beat_desc += f" | Role: {beat.scene_role}"
            if beat.viewer_question:
                beat_desc += f" | Viewer Question: \"{beat.viewer_question}\""
            beat_desc += f" | Focus Concept: \"{beat.focus_concept}\""
            beat_desc += f" | Core Teaching Point: \"{beat.core_teaching_point}\""
            if beat.key_evidence:
                beat_desc += f" | Key Evidence: {beat.key_evidence}"
            user_prompt_lines.append(beat_desc)

        user_prompt_lines.append("\n--- STRICT RESEARCH CONTEXT & FACTS ---")
        user_prompt_lines.append(f"Verified Concepts: {research_packet.concepts}")
        user_prompt_lines.append(f"Verified Facts: {research_packet.verified_facts}")
        user_prompt_lines.append(f"Verified Statistics: {research_packet.statistics}")
        user_prompt_lines.append(f"Examples: {research_packet.examples}")

        user_prompt_lines.append("\n--- BUDGET & PACING ---")
        user_prompt_lines.append(budget_instructions)

        user_prompt_lines.append("\nCRITICAL INSTRUCTIONS:")
        user_prompt_lines.append("1. For each idea's 'focus_concept', you MUST choose exactly one concept from the 'Verified Concepts' list above. Do NOT make up new concepts or use phrasing not present in that list.")
        user_prompt_lines.append("2. Any numbers, statistics, or figures you mention in the narration text MUST be strictly grounded in 'Verified Facts', 'Verified Statistics', or 'Examples'. You are explicitly permitted and encouraged to use the concrete numbers and calculations from 'Examples' (such as salary figures, percentage allocations, and timelines) in your narration. Do NOT invent or use any other numbers (except common small numbers/indexes like 1, 2, 3, etc.).")
        user_prompt_lines.append("3. You MUST generate exactly one output 'idea' in the 'ideas' array for every 'scene_beat' provided in the Narrative Plan. Maintain their exact chronological order, titles, focus concepts, and core teaching points, while filling in the 'narration' field.")
        user_prompt_lines.append(
            "4. For every idea, explicitly evaluate whether the narration contains a genuine "
            "performance moment such as a reveal, contradiction, key realization, important "
            "contrast, payoff, or conclusion. If it does, provide 1 meaningful voice cue in "
            "'voice_cues'. If it contains two clearly distinct performance moments, you may "
            "provide 2 cues. Use [] only when normal delivery is genuinely sufficient. "
            "Do not add cues merely because the narration contains numbers, statistics, "
            "technical terms, or other factual information."
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
                    content="\n".join(user_prompt_lines),
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

        # Backfill lineage metadata from NarrativePlan scene beats if absent
        for idx, idea in enumerate(strategy.ideas):
            if idx < len(narrative_plan.scene_beats):
                beat = narrative_plan.scene_beats[idx]
                if not idea.scene_role and beat.scene_role:
                    idea.scene_role = beat.scene_role
                if not idea.viewer_question and beat.viewer_question:
                    idea.viewer_question = beat.viewer_question
                if not idea.key_evidence and beat.key_evidence:
                    idea.key_evidence = list(beat.key_evidence)

        return ScriptVisualStrategyResult(
            strategy=strategy,
            provider_metadata=response.metadata,
            raw_payload=response.payload,
        )
