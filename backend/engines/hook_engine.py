from dataclasses import dataclass
from typing import Any

from pydantic import ValidationError

from domain.generate_video_request import GenerateVideoRequest
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
        "conceptual_hook": {
            "type": "string",
            "description": "Refined conceptual hook idea or analogy connecting the opening to the narrative thesis.",
        },
        "script_text": {
            "type": "string",
            "description": "The exact spoken opening hook script for narration.",
        },
    },
    "required": [
        "conceptual_hook",
        "script_text",
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

    def run(self, request: GenerateVideoRequest, narrative_plan: NarrativePlan) -> HookResult:
        system_content = load_prompt("hook_system.txt")
        first_scene = narrative_plan.scene_beats[0] if narrative_plan.scene_beats else None
        user_lines = [
            f"Topic: {request.topic}",
            f"Angle: {request.angle}",
            f"Audience: {request.audience}",
            f"Channel: {request.channel}",
            f"Thesis: {narrative_plan.thesis}",
            f"Target Pain Point: {narrative_plan.target_pain_point}",
        ]
        if narrative_plan.central_tension:
            user_lines.append(f"Central Tension: {narrative_plan.central_tension}")
        if narrative_plan.starting_belief:
            user_lines.append(f"Starting Belief: {narrative_plan.starting_belief}")
        if narrative_plan.ending_understanding:
            user_lines.append(f"Ending Understanding: {narrative_plan.ending_understanding}")
        if narrative_plan.conceptual_hook:
            user_lines.append(f"Conceptual Hook: {narrative_plan.conceptual_hook}")
        if narrative_plan.narrative_arc_type:
            user_lines.append(f"Narrative Arc Type: {narrative_plan.narrative_arc_type}")

        if first_scene:
            user_lines.append(f"Scene 01 Title: {first_scene.title}")
            if first_scene.scene_role:
                user_lines.append(f"Scene 01 Role: {first_scene.scene_role}")
            if first_scene.viewer_question:
                user_lines.append(f"Scene 01 Viewer Question: {first_scene.viewer_question}")
            user_lines.append(f"Scene 01 Core Teaching Point: {first_scene.core_teaching_point}")
            if first_scene.key_evidence:
                user_lines.append(f"Scene 01 Key Evidence: {', '.join(first_scene.key_evidence)}")

        user_lines.append("Generate a highly engaging opening hook script matching the narrative plan's conceptual hook and tension.")

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
                    content="\n".join(user_lines),
                ),
            ],
            temperature=0.5,
            max_tokens=4096,
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
