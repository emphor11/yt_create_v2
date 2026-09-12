"""
CompositionPlannerEngine — selects a composition for one VisualIntent.

This is Stage 2 of the composition visual pipeline:
  VisualIntent → CompositionBeat

For each VisualIntent it:
1. Calls the LLM with the closed composition catalog + the intent
2. Validates the response (composition_id must be registered, data must pass schema)
3. Returns a CompositionBeat, or a BrollCaption fallback beat if no composition fits

The LLM cannot invent composition names — the response_schema enum is built
dynamically from CompositionRegistry.all_ids().
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from domain.composition_plan import CompositionBeat
from domain.visual_intent import VisualIntent
from providers.llm_provider import (
    LLMJsonRequest,
    LLMMessage,
    LLMProvider,
    LLMProviderError,
    LLMProviderMetadata,
)
from registries.composition_registry import CompositionRegistry
from app.assets import load_prompt


@dataclass(frozen=True)
class CompositionPlannerResult:
    beat: CompositionBeat
    provider_metadata: LLMProviderMetadata
    raw_payload: dict[str, Any]
    used_fallback: bool  # True when "no_suitable_composition" was returned or validation failed
    fallback_reason: str | None = None


class CompositionPlannerEngineError(Exception):
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


def _is_declining_intent(intent: VisualIntent) -> bool:
    """Returns True if the intent describes a decline, erosion, or loss over time."""
    if intent.relationship_type == "decline":
        return True

    if intent.emphasis and any(
        w in intent.emphasis.lower()
        for w in ("decline", "erosion", "loss", "decay", "drop", "fall", "purchasing_power_decline", "value_erosion")
    ):
        return True

    decline_indicators = (
        "decline", "declining", "decrease", "decreasing", "erode", "erodes", "erosion",
        "decay", "loss", "loses", "losing", "drop", "drops", "deplete", "depletion",
        "fall", "falling", "shrink", "shrinking", "diminish", "halved", "downward",
        "purchasing power",
    )
    combined_text = f"{intent.what_viewer_must_understand} {intent.narration_excerpt}".lower()
    return any(ind in combined_text for ind in decline_indicators)


def _make_fallback_beat(
    intent: VisualIntent,
    beat_id: str,
    fallback_reason: str = "no_suitable_composition",
) -> CompositionBeat:
    """Creates a safe broll_caption fallback beat for a given intent."""
    return CompositionBeat(
        beat_id=beat_id,
        composition_id="broll_caption",
        variant=None,
        composition_data={
            "caption": intent.what_viewer_must_understand,
            "emphasis_phrase": intent.key_values[0] if intent.key_values else None,
        },
        asset_requirement="optional_broll",
        asset_query=intent.narration_excerpt[:60],
        trigger_word=intent.trigger_word,
        visual_goal=intent.what_viewer_must_understand,
        relationship_type=intent.relationship_type,
        used_fallback=True,
        fallback_reason=fallback_reason,
    )


class CompositionPlannerEngine:
    """
    Selects and validates a composition for one VisualIntent.

    One LLM call per intent. Returns a CompositionBeat ready for assembly.
    """

    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider

    def run(
        self,
        *,
        intent: VisualIntent,
        beat_id: str,
        topic: str = "",
        audience: str = "",
    ) -> CompositionPlannerResult:
        """
        Args:
            intent:   The VisualIntent to find a composition for.
            beat_id:  Identifier for this beat (e.g. "beat_01").
            topic:    Optional — injected for context.
            audience: Optional — injected for context.

        Returns:
            CompositionPlannerResult containing:
              - beat: a CompositionBeat (either selected or broll_caption fallback)
              - used_fallback: True if fallback was triggered
        """
        system_prompt_template = load_prompt("composition_planner_system.txt")
        catalog_section = CompositionRegistry.get_planner_prompt_section()
        system_content = system_prompt_template.replace("{{COMPOSITION_CATALOG}}", catalog_section)

        intent_json = (
            f"relationship_type: {intent.relationship_type}\n"
            f"what_viewer_must_understand: {intent.what_viewer_must_understand}\n"
            f"key_values: {intent.key_values}\n"
            f"emphasis: {intent.emphasis}\n"
            f"trigger_word: {intent.trigger_word!r}\n"
            f"narration_excerpt: {intent.narration_excerpt}\n"
        )

        user_content = (
            f"Topic: {topic}\n"
            f"Audience: {audience}\n\n"
            f"VISUAL INTENT:\n{intent_json}\n\n"
            "Select the best composition from the catalog for this intent, "
            "or return 'no_suitable_composition' if none fits."
        )

        response_schema = CompositionRegistry.build_planner_response_schema()

        llm_request = LLMJsonRequest(
            schema_name="CompositionPlannerResponse",
            response_schema=response_schema,
            messages=[
                LLMMessage(role="system", content=system_content),
                LLMMessage(role="user", content=user_content),
            ],
            temperature=0.1,  # Low temperature — structured selection, not creativity
            max_tokens=1500,
        )

        # --- LLM call ---
        try:
            response = self.llm_provider.generate_json(llm_request)
        except LLMProviderError as error:
            # LLM hard failure → use fallback, don't crash the pipeline
            fallback_reason = f"provider_error: {error}"
            fallback = _make_fallback_beat(intent, beat_id, fallback_reason=fallback_reason)
            return CompositionPlannerResult(
                beat=fallback,
                provider_metadata=LLMProviderMetadata(provider="fallback", model="fallback"),
                raw_payload={"error": str(error)},
                used_fallback=True,
                fallback_reason=fallback_reason,
            )

        raw = response.payload
        status = raw.get("status", "")

        # --- No suitable composition declared by LLM ---
        if status == "no_suitable_composition":
            reason = raw.get("reason", "No suitable composition declared by LLM")
            fallback_reason = f"no_suitable_composition: {reason}"
            fallback = _make_fallback_beat(intent, beat_id, fallback_reason=fallback_reason)
            return CompositionPlannerResult(
                beat=fallback,
                provider_metadata=response.metadata,
                raw_payload=raw,
                used_fallback=True,
                fallback_reason=fallback_reason,
            )

        # --- Validate composition_id ---
        composition_id = raw.get("composition_id", "")
        if not CompositionRegistry.is_registered(composition_id):
            # Unknown composition → fallback (LLM ignored the enum constraint)
            fallback_reason = f"unknown_composition_id: '{composition_id}' is not registered"
            fallback = _make_fallback_beat(intent, beat_id, fallback_reason=fallback_reason)
            return CompositionPlannerResult(
                beat=fallback,
                provider_metadata=response.metadata,
                raw_payload=raw,
                used_fallback=True,
                fallback_reason=fallback_reason,
            )

        defn = CompositionRegistry.get(composition_id)
        assert defn is not None  # guaranteed by is_registered check above

        # --- Validate supported relationship_type ---
        if intent.relationship_type not in defn.supported_relationship_types:
            fallback_reason = (
                f"unsupported_relationship_type: '{composition_id}' does not support '{intent.relationship_type}'"
            )
            fallback = _make_fallback_beat(intent, beat_id, fallback_reason=fallback_reason)
            return CompositionPlannerResult(
                beat=fallback,
                provider_metadata=response.metadata,
                raw_payload=raw,
                used_fallback=True,
                fallback_reason=fallback_reason,
            )

        # --- Semantic guardrail: time_decay must strictly represent decline/erosion ---
        if composition_id == "time_decay" and intent.relationship_type == "trend" and not _is_declining_intent(intent):
            fallback_reason = "time_decay rejected: trend does not indicate decline or erosion"
            fallback = _make_fallback_beat(intent, beat_id, fallback_reason=fallback_reason)
            return CompositionPlannerResult(
                beat=fallback,
                provider_metadata=response.metadata,
                raw_payload=raw,
                used_fallback=True,
                fallback_reason=fallback_reason,
            )

        # --- Validate variant ---
        variant = raw.get("variant")
        if variant is not None and defn.allowed_variants and variant not in defn.allowed_variants:
            variant = None  # silently drop invalid variant

        # --- Validate composition_data ---
        composition_data_raw: dict[str, Any] = raw.get("composition_data", {})
        is_valid, errors, normalized_data = CompositionRegistry.validate_composition_data(
            composition_id, composition_data_raw, visual_goal=raw.get("visual_goal", "")
        )

        if not is_valid:
            # Invalid data → fallback
            fallback_reason = f"validation_error: {'; '.join(errors)}"
            fallback = _make_fallback_beat(intent, beat_id, fallback_reason=fallback_reason)
            return CompositionPlannerResult(
                beat=fallback,
                provider_metadata=response.metadata,
                raw_payload=raw,
                used_fallback=True,
                fallback_reason=fallback_reason,
            )

        # --- Build CompositionBeat ---
        beat = CompositionBeat(
            beat_id=beat_id,
            composition_id=composition_id,
            variant=variant,
            composition_data=normalized_data,
            asset_requirement=raw.get("asset_requirement", "none"),
            asset_query=raw.get("asset_query"),
            trigger_word=raw.get("trigger_word"),
            visual_goal=raw.get("visual_goal", intent.what_viewer_must_understand),
            relationship_type=intent.relationship_type,
            used_fallback=False,
            fallback_reason=None,
        )

        return CompositionPlannerResult(
            beat=beat,
            provider_metadata=response.metadata,
            raw_payload=raw,
            used_fallback=False,
            fallback_reason=None,
        )
