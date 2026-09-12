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
import re
from app.assets import load_prompt


# Common English grammatical stopwords disallowed as trigger words.
TRIGGER_WORD_STOPWORDS: frozenset[str] = frozenset({
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "of", "in", "on", "at", "and", "or", "but", "to", "for", "with", "by",
    "it", "this", "that", "these", "those", "so", "as", "if",
})


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
                    "entities": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "role": {"type": "string", "nullable": True},
                                "category": {"type": "string", "nullable": True},
                            },
                            "required": ["name"],
                        },
                    },
                    "measurements": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "raw_value": {"type": "string"},
                                "entity_name": {"type": "string", "nullable": True},
                                "metric_name": {"type": "string", "nullable": True},
                                "unit": {"type": "string", "nullable": True},
                                "numeric_value": {"type": "number", "nullable": True},
                                "direction": {
                                    "type": "string",
                                    "enum": ["up", "down", "flat", "neutral"],
                                    "nullable": True,
                                },
                                "polarity": {
                                    "type": "string",
                                    "enum": ["positive", "negative", "neutral", "warning"],
                                    "nullable": True,
                                },
                                "role": {
                                    "type": "string",
                                    "enum": ["input", "rate", "result", "baseline", "delta", "benchmark", "context"],
                                    "nullable": True,
                                },
                            },
                            "required": ["raw_value"],
                        },
                    },
                    "temporal": {
                        "type": "object",
                        "properties": {
                            "horizon": {"type": "string", "nullable": True},
                            "frequency": {"type": "string", "nullable": True},
                            "is_decay_over_time": {"type": "boolean"},
                        },
                        "nullable": True,
                    },
                    "causal": {
                        "type": "object",
                        "properties": {
                            "causes": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                            "mechanism": {"type": "string", "nullable": True},
                            "outcome": {"type": "string", "nullable": True},
                            "outcome_severity": {
                                "type": "string",
                                "enum": ["critical", "high", "medium", "low", "positive", "neutral"],
                                "nullable": True,
                            },
                        },
                        "nullable": True,
                    },
                    "comparison": {
                        "type": "object",
                        "properties": {
                            "subject_a": {"type": "string"},
                            "value_a": {"type": "string"},
                            "subject_b": {"type": "string"},
                            "value_b": {"type": "string"},
                            "comparison_dimension": {"type": "string"},
                            "delta": {"type": "string", "nullable": True},
                            "winner": {"type": "string", "nullable": True},
                        },
                        "required": ["subject_a", "value_a", "subject_b", "value_b", "comparison_dimension"],
                        "nullable": True,
                    },
                    "visual_dynamics": {
                        "type": "object",
                        "properties": {
                            "focal_point": {"type": "string", "nullable": True},
                            "desired_visual_outcome": {"type": "string", "nullable": True},
                            "motion_intent": {"type": "string", "nullable": True},
                            "visual_priority": {"type": "string", "nullable": True},
                        },
                        "nullable": True,
                    },
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

        # Validate trigger_words according to strict semantic rules:
        # 1. First intent must have trigger_word=null (starts immediately)
        # 2. Subsequent intents must have a non-empty trigger_word
        # 3. trigger_word must appear verbatim in narration_excerpt
        # 4. trigger_word must appear verbatim in narration
        # 5. No duplicate trigger_word within the same idea
        # 6. Single lexical word (no whitespace)
        # 7. Must not be punctuation-only
        # 8. Must not be a common English stopword
        intents_raw = raw.get("intents", [])
        seen_trigger_words: set[str] = set()
        for i, intent_item in enumerate(intents_raw):
            tw = intent_item.get("trigger_word")
            intent_label = intent_item.get("intent_id", f"intent_{i+1:02d}")
            if i == 0:
                if tw is not None and str(tw).strip() != "":
                    raise VisualIntentEngineError(
                        "The first VisualIntent must have trigger_word=null (it starts immediately).",
                        raw_payload=raw,
                        provider_metadata=response.metadata,
                    )
                intent_item["trigger_word"] = None
            else:
                if tw is None or str(tw).strip() == "":
                    raise VisualIntentEngineError(
                        f"VisualIntent at index {i} ('{intent_label}') must have a non-empty trigger_word.",
                        raw_payload=raw,
                        provider_metadata=response.metadata,
                    )
                tw_raw = str(tw).strip()
                if re.search(r"\s", tw_raw):
                    raise VisualIntentEngineError(
                        f"VisualIntent trigger_word '{tw_raw}' must be a single word without spaces.",
                        raw_payload=raw,
                        provider_metadata=response.metadata,
                    )
                clean_tw = tw_raw.strip(".,;:!?\"'()")
                if not clean_tw or not re.search(r"[a-zA-Z0-9\u0900-\u097F]", clean_tw):
                    raise VisualIntentEngineError(
                        f"VisualIntent trigger_word '{tw_raw}' must not be punctuation-only.",
                        raw_payload=raw,
                        provider_metadata=response.metadata,
                    )
                tw_lower = clean_tw.lower()
                if tw_lower in TRIGGER_WORD_STOPWORDS:
                    raise VisualIntentEngineError(
                        f"VisualIntent trigger_word '{tw_raw}' cannot be a common stopword ('{tw_lower}').",
                        raw_payload=raw,
                        provider_metadata=response.metadata,
                    )
                if tw_lower in seen_trigger_words:
                    raise VisualIntentEngineError(
                        f"Duplicate trigger_word '{clean_tw}' in idea '{idea_id}'. Each trigger word within an idea must be unique.",
                        raw_payload=raw,
                        provider_metadata=response.metadata,
                    )
                seen_trigger_words.add(tw_lower)

                excerpt = intent_item.get("narration_excerpt", "")
                if tw_lower not in excerpt.lower():
                    raise VisualIntentEngineError(
                        f"VisualIntent trigger_word '{clean_tw}' does not appear in narration_excerpt: '{excerpt}'.",
                        raw_payload=raw,
                        provider_metadata=response.metadata,
                    )

                if tw_lower not in narration.lower():
                    raise VisualIntentEngineError(
                        f"VisualIntent trigger_word '{clean_tw}' does not appear in narration: '{narration}'.",
                        raw_payload=raw,
                        provider_metadata=response.metadata,
                    )
                intent_item["trigger_word"] = clean_tw

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
