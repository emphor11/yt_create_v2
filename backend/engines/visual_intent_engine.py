"""
VisualIntentEngine — converts narration into semantic VisualIntents.

Takes the narration of one narrative idea and calls the LLM to produce
an ordered list of VisualIntents using the closed relationship_type taxonomy.

This is Stage 1 of the composition visual pipeline:
  narration → VisualIntentSequence → (→ CompositionPlannerEngine → CompositionBeat[])
"""
from __future__ import annotations

from dataclasses import dataclass
import logging
import math
import re
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

logger = logging.getLogger(__name__)


# Trigger word stopwords blocklist removed
TRIGGER_WORD_STOPWORDS: frozenset[str] = frozenset()


def calculate_pacing_budget(narration: str) -> dict[str, Any]:
    """
    Computes a pacing budget guideline for a narration segment.

    Formula:
        word_count = number of spoken words
        estimated_seconds = word_count / 2.7
        target_beats_min = max(2, ceil(word_count / 22))
        target_beats_max = max(3, ceil(word_count / 14))
    """
    words = [w for w in re.split(r"\s+", narration.strip()) if w]
    word_count = len(words)
    estimated_seconds = word_count / 2.7
    target_beats_min = max(2, math.ceil(word_count / 22))
    target_beats_max = max(3, math.ceil(word_count / 14))
    return {
        "word_count": word_count,
        "estimated_seconds": round(estimated_seconds, 1),
        "target_beats_min": target_beats_min,
        "target_beats_max": target_beats_max,
    }


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
    pacing_diagnostic: dict[str, Any] | None = None


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
        is_hook: bool = False,
    ) -> VisualIntentResult:
        """
        Args:
            idea_id:   The idea_id from the ScriptVisualStrategy (e.g. "idea_01") or "hook".
            narration: The full narration text for this idea or hook.
            topic:     Optional — injected into the prompt for context.
            audience:  Optional — injected into the prompt for context.
            is_hook:   Optional — if True, applies hook-specific pacing (2-3 beats max, immediate engagement).

        Returns:
            VisualIntentResult containing the validated VisualIntentSequence.

        Raises:
            VisualIntentEngineError: on LLM failure or validation failure.
        """
        system_content = load_prompt("visual_intent_system.txt")

        hook_instructions = ""
        pacing_instructions = ""
        pacing_budget = None

        if is_hook:
            hook_instructions = (
                "\nHOOK-SPECIFIC CONSTRAINTS:\n"
                "- This is the opening HOOK of the video (15-25 seconds total).\n"
                "- Generate exactly 2 to 3 punchy, high-retention visual intents (never more than 3).\n"
                "- The first intent MUST have immediate first-frame engagement (starts immediately at frame 0).\n"
                "- Focus on high visual contrast: bold metric, startling comparison, multi-factor convergence, or key claim.\n"
            )
        else:
            pacing_budget = calculate_pacing_budget(narration)
            pacing_instructions = (
                f"\nPACING BUDGET:\n"
                f"- Narration length: {pacing_budget['word_count']} words\n"
                f"- Estimated spoken duration: {pacing_budget['estimated_seconds']:.1f} seconds\n"
                f"- Suggested visual intent range: {pacing_budget['target_beats_min']}–{pacing_budget['target_beats_max']}\n"
                f"- Instruction: Use this range as a pacing guide, not a mechanical segmentation rule. "
                f"Prioritize meaningful semantic transitions. Do not create filler intents just to reach the target count.\n"
            )

        user_content = (
            f"Topic: {topic}\n"
            f"Audience: {audience}\n"
            f"Idea ID: {idea_id}\n"
            f"{hook_instructions}"
            f"{pacing_instructions}\n"
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
            max_tokens=8192,
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
                if tw_lower in seen_trigger_words:
                    raise VisualIntentEngineError(
                        f"Duplicate trigger_word '{clean_tw}' in idea '{idea_id}'. Each trigger word within an idea must be unique.",
                        raw_payload=raw,
                        provider_metadata=response.metadata,
                    )
                seen_trigger_words.add(tw_lower)

                tw_pattern = re.compile(r"\b" + re.escape(tw_lower) + r"\b", re.IGNORECASE)
                excerpt = intent_item.get("narration_excerpt", "")
                if not tw_pattern.search(excerpt):
                    raise VisualIntentEngineError(
                        f"VisualIntent trigger_word '{clean_tw}' does not appear in narration_excerpt: '{excerpt}' (must match as a complete word).",
                        raw_payload=raw,
                        provider_metadata=response.metadata,
                    )

                if not tw_pattern.search(narration):
                    raise VisualIntentEngineError(
                        f"VisualIntent trigger_word '{clean_tw}' does not appear in narration: '{narration}' (must match as a complete word).",
                        raw_payload=raw,
                        provider_metadata=response.metadata,
                    )
                intent_item["trigger_word"] = clean_tw

        # ── Validate intent_id uniqueness ────────────────────────────────────
        seen_intent_ids: set[str] = set()
        for intent_item in intents_raw:
            iid = intent_item.get("intent_id", "")
            if iid in seen_intent_ids:
                raise VisualIntentEngineError(
                    f"Duplicate intent_id '{iid}' in idea '{idea_id}'. "
                    "Each intent_id must be unique within the same idea.",
                    raw_payload=raw,
                    provider_metadata=response.metadata,
                )
            seen_intent_ids.add(iid)

        # ── Validate narration_excerpt verbatim + ordering ───────────────────
        # Each excerpt must:
        #   1. Be a verbatim contiguous substring of the full narration.
        #   2. Not overlap the preceding excerpt.
        #   3. Appear at or after the position where the previous excerpt ended.
        narration_lower = narration.lower()
        prev_end: int = 0
        for intent_item in intents_raw:
            excerpt: str = intent_item.get("narration_excerpt", "")
            if not excerpt:
                continue  # empty excerpts are allowed (engine will reject later via Pydantic)
            excerpt_lower = excerpt.lower()
            pos = narration_lower.find(excerpt_lower, prev_end)
            if pos == -1:
                # Try from beginning — may be an ordering violation
                pos_from_start = narration_lower.find(excerpt_lower)
                if pos_from_start == -1:
                    raise VisualIntentEngineError(
                        f"narration_excerpt is not a verbatim substring of the narration. "
                        f"Excerpt: '{excerpt[:120]}'. "
                        "narration_excerpt must be copied verbatim from the narration text — do not paraphrase.",
                        raw_payload=raw,
                        provider_metadata=response.metadata,
                    )
                raise VisualIntentEngineError(
                    f"narration_excerpt appears out of order in the narration. "
                    f"Excerpt '{excerpt[:80]}' starts before the end of the previous excerpt. "
                    "Excerpts must be non-overlapping and ordered as they appear in the narration.",
                    raw_payload=raw,
                    provider_metadata=response.metadata,
                )
            prev_end = pos + len(excerpt)

        # ── Validate raw_value grounding in narration_excerpt ────────────────
        # Each measurement.raw_value must appear (case-insensitive substring) in
        # the narration_excerpt of its intent. This prevents invented factual values.
        for intent_item in intents_raw:
            excerpt = intent_item.get("narration_excerpt", "")
            excerpt_lower = excerpt.lower()
            for meas in intent_item.get("measurements", []) or []:
                rv: str = meas.get("raw_value", "") if isinstance(meas, dict) else getattr(meas, "raw_value", "")
                if not rv:
                    continue
                # Normalize: strip currency symbols and commas for a looser token match
                # so '₹50 lakh' finds '50 lakh' and '₹50' finds '50'
                rv_lower = rv.lower()
                # Try exact substring first (most values will match this)
                if rv_lower not in excerpt_lower:
                    # Strip leading currency/symbol characters and retry
                    rv_stripped = re.sub(r"^[₹$€£¥\s]+", "", rv_lower).strip()
                    if rv_stripped and rv_stripped not in excerpt_lower:
                        raise VisualIntentEngineError(
                            f"measurement.raw_value '{rv}' does not appear in its narration_excerpt: '{excerpt[:120]}'. "
                            "raw_value must be the exact token from the narration — do not invent values.",
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
            # Surface the model_validator messages directly — they are already
            # human-readable and contain actionable grounding instructions.
            messages = "; ".join(
                str(e["msg"]) for e in error.errors()
            )
            raise VisualIntentEngineError(
                f"VisualIntent semantic contract violation: {messages}",
                raw_payload=raw,
                provider_metadata=response.metadata,
            ) from error

        pacing_diagnostic = None
        if pacing_budget is not None:
            generated_beats = len(sequence.intents)
            pacing_diagnostic = {
                "word_count": pacing_budget["word_count"],
                "estimated_seconds": pacing_budget["estimated_seconds"],
                "target_beats_min": pacing_budget["target_beats_min"],
                "target_beats_max": pacing_budget["target_beats_max"],
                "generated_beats": generated_beats,
                "below_min": generated_beats < pacing_budget["target_beats_min"],
            }
            if pacing_diagnostic["below_min"]:
                logger.warning(
                    "VisualIntentEngine: idea '%s' (%d words, ~%.1fs) produced %d intents, "
                    "below suggested minimum of %d",
                    idea_id,
                    pacing_budget["word_count"],
                    pacing_budget["estimated_seconds"],
                    generated_beats,
                    pacing_budget["target_beats_min"],
                )

        return VisualIntentResult(
            sequence=sequence,
            provider_metadata=response.metadata,
            raw_payload=raw,
            pacing_diagnostic=pacing_diagnostic,
        )
