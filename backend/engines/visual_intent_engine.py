"""
VisualIntentEngine — converts narration into semantic VisualIntents.

Takes the narration of one narrative idea and calls the LLM to produce
an ordered list of VisualIntents using the closed relationship_type taxonomy.

This is Stage 1 of the composition visual pipeline:
  narration → VisualIntentSequence → (→ CompositionPlannerEngine → CompositionBeat[])
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pydantic import ValidationError

from domain.visual_intent import VALID_RELATIONSHIP_TYPES, VisualIntent, VisualIntentSequence
from providers.llm_provider import (
    LLMJsonRequest,
    LLMMessage,
    LLMProvider,
    LLMProviderError,
    LLMProviderMetadata,
)
from app.assets import load_prompt


# JSON Schema for LLM structured output.
# relationship_type is a closed enum — LLM cannot invent new values.
VISUAL_INTENT_RESPONSE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "idea_id": {"type": "string"},
        "intents": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "intent_id": {"type": "string"},
                    "narration_excerpt": {"type": "string"},
                    "what_viewer_must_understand": {"type": "string"},
                    "key_values": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "relationship_type": {
                        "type": "string",
                        "enum": VALID_RELATIONSHIP_TYPES,
                    },
                    "emphasis": {"type": "string", "nullable": True},
                    "trigger_word": {"type": "string", "nullable": True},
                },
                "required": [
                    "intent_id",
                    "narration_excerpt",
                    "what_viewer_must_understand",
                    "relationship_type",
                ],
            },
        },
    },
    "required": ["idea_id", "intents"],
}


@dataclass(frozen=True)
class VisualIntentResult:
    sequence: VisualIntentSequence
    provider_metadata: LLMProviderMetadata
    raw_payload: dict[str, Any]


class VisualIntentEngineError(Exception):
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


class VisualIntentEngine:
    """
    Converts the narration of one narrative idea into an ordered list of VisualIntents.

    One LLM call per idea. The output feeds into CompositionPlannerEngine.
    """

    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider

    def run(
        self,
        *,
        idea_id: str,
        narration: str,
        topic: str = "",
        audience: str = "",
    ) -> VisualIntentResult:
        """
        Args:
            idea_id:   The idea_id from the ScriptVisualStrategy (e.g. "idea_01").
            narration: The full narration text for this idea.
            topic:     Optional — injected into the prompt for context.
            audience:  Optional — injected into the prompt for context.

        Returns:
            VisualIntentResult containing the validated VisualIntentSequence.

        Raises:
            VisualIntentEngineError: on LLM failure or validation failure.
        """
        system_content = load_prompt("visual_intent_system.txt")

        user_content = (
            f"Topic: {topic}\n"
            f"Audience: {audience}\n"
            f"Idea ID: {idea_id}\n\n"
            f"NARRATION:\n{narration}\n\n"
            "Analyze this narration and produce the list of VisualIntents."
        )

        llm_request = LLMJsonRequest(
            schema_name="VisualIntentSequence",
            response_schema=VISUAL_INTENT_RESPONSE_SCHEMA,
            messages=[
                LLMMessage(role="system", content=system_content),
                LLMMessage(role="user", content=user_content),
            ],
            temperature=0.1,  # Low temperature — this is classification, not creativity
            max_tokens=2000,
        )

        try:
            response = self.llm_provider.generate_json(llm_request)
        except LLMProviderError as error:
            raise VisualIntentEngineError(str(error)) from error

        raw = response.payload

        # Validate relationship_type values before Pydantic — gives clearer errors
        bad_types: list[str] = []
        for item in raw.get("intents", []):
            rt = item.get("relationship_type", "")
            if rt not in VALID_RELATIONSHIP_TYPES:
                bad_types.append(rt)

        if bad_types:
            raise VisualIntentEngineError(
                f"LLM returned invalid relationship_type values: {bad_types}. "
                f"Allowed: {VALID_RELATIONSHIP_TYPES}",
                raw_payload=raw,
                provider_metadata=response.metadata,
            )

        # Validate trigger_word: first intent must have trigger_word=None
        intents_raw = raw.get("intents", [])
        if intents_raw and intents_raw[0].get("trigger_word") is not None:
            raise VisualIntentEngineError(
                "The first VisualIntent must have trigger_word=null (it starts immediately).",
                raw_payload=raw,
                provider_metadata=response.metadata,
            )

        try:
            # Ensure idea_id is set correctly (LLM might echo it back incorrectly)
            raw["idea_id"] = idea_id
            sequence = VisualIntentSequence(
                idea_id=idea_id,
                narration=narration,
                intents=[VisualIntent.model_validate(i) for i in intents_raw],
            )
        except ValidationError as error:
            raise VisualIntentEngineError(
                "LLM returned invalid VisualIntent data.",
                raw_payload=raw,
                provider_metadata=response.metadata,
            ) from error

        return VisualIntentResult(
            sequence=sequence,
            provider_metadata=response.metadata,
            raw_payload=raw,
        )
