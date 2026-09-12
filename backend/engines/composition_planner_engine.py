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

import json
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


def build_candidate_composition_data(
    composition_id: str,
    intent: VisualIntent,
) -> dict[str, Any]:
    """
    Deterministically extracts verified factual data from structured VisualIntent fields.
    Rule: Structured meaning can be transformed; it cannot be invented.
    No operations, severities, or extraneous values are guessed.
    """
    candidate: dict[str, Any] = {}

    if composition_id == "metric_hero":
        if intent.measurements:
            candidate["value"] = intent.measurements[0].raw_value
            if intent.measurements[0].metric_name:
                candidate["label"] = intent.measurements[0].metric_name
            elif intent.measurements[0].entity_name:
                candidate["label"] = intent.measurements[0].entity_name
        elif intent.entities:
            candidate["label"] = intent.entities[0].name

        if intent.temporal:
            if intent.temporal.frequency:
                candidate["context"] = intent.temporal.frequency
            elif intent.temporal.horizon:
                candidate["context"] = intent.temporal.horizon

        if intent.emphasis:
            candidate["emphasis"] = intent.emphasis

    elif composition_id == "calculation_story":
        # Extract by semantic role (never by list order)
        input_m = next((m for m in intent.measurements if m.role in ("input", "baseline")), None)
        rate_m = next((m for m in intent.measurements if m.role == "rate"), None)
        result_m = next((m for m in intent.measurements if m.role == "result"), None)

        if input_m:
            candidate["input_value"] = input_m.raw_value
            if input_m.metric_name:
                candidate["input_label"] = input_m.metric_name
            elif input_m.entity_name:
                candidate["input_label"] = input_m.entity_name

        if rate_m:
            candidate["rate_label"] = rate_m.raw_value

        if result_m:
            candidate["result_value"] = result_m.raw_value
            if result_m.metric_name:
                candidate["result_label"] = result_m.metric_name
            elif result_m.entity_name:
                candidate["result_label"] = result_m.entity_name

        # Note: operation_label is NOT invented here. LLM provides it during refinement.
        if intent.visual_dynamics and intent.visual_dynamics.focal_point:
            candidate["note"] = intent.visual_dynamics.focal_point

    elif composition_id == "comparison_split":
        if intent.comparison:
            candidate["left_role"] = intent.comparison.subject_a
            candidate["left_value"] = intent.comparison.value_a
            candidate["right_role"] = intent.comparison.subject_b
            candidate["right_value"] = intent.comparison.value_b
            if intent.comparison.comparison_dimension:
                candidate["comparison_label"] = intent.comparison.comparison_dimension
            if intent.comparison.delta:
                candidate["delta"] = intent.comparison.delta
            if intent.comparison.winner:
                w = intent.comparison.winner.strip().lower()
                sa = intent.comparison.subject_a.strip().lower()
                sb = intent.comparison.subject_b.strip().lower()
                if w == "left" or w == sa:
                    candidate["winner"] = "left"
                elif w == "right" or w == sb:
                    candidate["winner"] = "right"
        elif len(intent.entities) >= 2:
            candidate["left_role"] = intent.entities[0].name
            candidate["right_role"] = intent.entities[1].name

        # Units from measurements if matching entity
        for m in intent.measurements:
            if m.unit and m.entity_name:
                if candidate.get("left_role") and m.entity_name.lower() in candidate["left_role"].lower():
                    candidate["left_unit"] = m.unit
                elif candidate.get("right_role") and m.entity_name.lower() in candidate["right_role"].lower():
                    candidate["right_unit"] = m.unit

    elif composition_id == "cause_effect":
        if intent.causal and intent.causal.causes:
            candidate["causes"] = [{"label": c} for c in intent.causal.causes[:3]]
        elif intent.entities:
            risk_entities = [e for e in intent.entities if e.role == "risk_factor"]
            if risk_entities:
                candidate["causes"] = [{"label": e.name} for e in risk_entities[:3]]

        if intent.causal and intent.causal.outcome:
            candidate["outcome_label"] = intent.causal.outcome

        # Severity mapped without inventing: only if intent.causal.outcome_severity is explicitly set
        if intent.causal and intent.causal.outcome_severity:
            sev = intent.causal.outcome_severity.lower()
            if sev in ("critical", "high", "medium"):
                candidate["outcome_severity"] = "negative"
            elif sev == "positive":
                candidate["outcome_severity"] = "positive"
            elif sev == "neutral":
                candidate["outcome_severity"] = "neutral"

    elif composition_id == "multi_factor_pressure":
        if intent.causal and intent.causal.causes:
            factors: list[dict[str, Any]] = []
            for c in intent.causal.causes[:4]:
                item: dict[str, Any] = {"label": c}
                if intent.causal.outcome_severity in ("critical", "high", "medium"):
                    item["severity"] = intent.causal.outcome_severity
                factors.append(item)
            if factors:
                candidate["factors"] = factors
        elif intent.entities:
            risk_entities = [e for e in intent.entities if e.role == "risk_factor"]
            if risk_entities:
                candidate["factors"] = [{"label": e.name} for e in risk_entities[:4]]

        if intent.causal and intent.causal.outcome:
            candidate["combined_label"] = intent.causal.outcome

        if intent.causal and intent.causal.outcome_severity:
            sev = intent.causal.outcome_severity.lower()
            if sev in ("critical", "high", "medium"):
                candidate["combined_severity"] = sev

        if intent.causal and intent.causal.mechanism:
            candidate["outcome_note"] = intent.causal.mechanism

    elif composition_id == "time_decay":
        # Meaning-based: baseline role vs result role
        baseline_m = next((m for m in intent.measurements if m.role in ("baseline", "input")), None)
        result_m = next((m for m in intent.measurements if m.role in ("result", "delta")), None)

        if baseline_m:
            candidate["fixed_amount"] = baseline_m.raw_value
            if baseline_m.entity_name:
                candidate["amount_label"] = baseline_m.entity_name
            elif baseline_m.metric_name:
                candidate["amount_label"] = baseline_m.metric_name
        elif intent.entities:
            subj_entity = next((e for e in intent.entities if e.role == "subject"), intent.entities[0])
            candidate["amount_label"] = subj_entity.name

        if intent.temporal and intent.temporal.horizon:
            candidate["time_period"] = intent.temporal.horizon

        if intent.temporal and intent.temporal.is_decay_over_time:
            candidate["emphasis"] = "purchasing_power_decline"

        if result_m:
            candidate["annotation"] = f"Erodes to {result_m.raw_value}"
        elif intent.visual_dynamics and intent.visual_dynamics.focal_point:
            candidate["annotation"] = intent.visual_dynamics.focal_point

    elif composition_id == "ranked_list":
        if intent.entities:
            items: list[dict[str, Any]] = []
            for idx, e in enumerate(intent.entities[:5]):
                matching_m = next((m for m in intent.measurements if m.entity_name == e.name), None)
                val = matching_m.raw_value if matching_m else None
                num_val = matching_m.numeric_value if matching_m else None
                items.append({
                    "title": e.name,
                    "rank": idx + 1,
                    "value": val,
                    "numeric_value": num_val,
                })
            if items:
                candidate["items"] = items

        if intent.visual_dynamics and intent.visual_dynamics.focal_point:
            candidate["header_label"] = intent.visual_dynamics.focal_point

    elif composition_id == "process_flow":
        if intent.entities:
            steps: list[dict[str, Any]] = []
            for e in intent.entities[:5]:
                steps.append({
                    "title": e.name,
                    "subtitle": e.role if e.role and not e.role.startswith("step_") else None,
                    "type": "step",
                })
            if steps:
                candidate["steps"] = steps

        if intent.visual_dynamics and intent.visual_dynamics.focal_point:
            candidate["header_label"] = intent.visual_dynamics.focal_point

    elif composition_id == "broll_caption":
        candidate["caption"] = intent.what_viewer_must_understand
        if intent.visual_dynamics and intent.visual_dynamics.focal_point:
            candidate["emphasis_phrase"] = intent.visual_dynamics.focal_point
        elif intent.key_values:
            candidate["emphasis_phrase"] = intent.key_values[0]

        author_entity = next((e for e in intent.entities if e.role == "author" or e.category == "person"), None)
        if author_entity:
            candidate["author"] = author_entity.name

    return candidate


def merge_factual_and_presentation_data(
    composition_id: str,
    candidate_facts: dict[str, Any],
    llm_data: dict[str, Any],
    intent: VisualIntent,
) -> dict[str, Any]:
    """
    Merges deterministic factual data with LLM planner presentation refinements.
    
    Factual values from candidate_facts are authoritative and take precedence over LLM drift.
    Presentation fields (labels, operation wording, notes, connectors, tone) from LLM are preserved.
    Rule: Structured meaning can be transformed; it cannot be invented.
    Missing required fields are never fabricated.
    """
    result: dict[str, Any] = dict(llm_data)

    if composition_id == "metric_hero":
        if "value" in candidate_facts:
            result["value"] = candidate_facts["value"]
        if "label" in candidate_facts and not result.get("label"):
            result["label"] = candidate_facts["label"]
        if "context" in candidate_facts and not result.get("context"):
            result["context"] = candidate_facts["context"]
        if "emphasis" in candidate_facts and not result.get("emphasis"):
            result["emphasis"] = candidate_facts["emphasis"]

    elif composition_id == "calculation_story":
        if "input_value" in candidate_facts:
            result["input_value"] = candidate_facts["input_value"]
        if "result_value" in candidate_facts:
            result["result_value"] = candidate_facts["result_value"]

        if "rate_label" in candidate_facts:
            cand_rate = candidate_facts["rate_label"]
            llm_rate = result.get("rate_label", "")
            if cand_rate not in llm_rate:
                result["rate_label"] = cand_rate

        if "input_label" in candidate_facts and not result.get("input_label"):
            result["input_label"] = candidate_facts["input_label"]
        if "result_label" in candidate_facts and not result.get("result_label"):
            result["result_label"] = candidate_facts["result_label"]
        if "note" in candidate_facts and not result.get("note"):
            result["note"] = candidate_facts["note"]

    elif composition_id == "comparison_split":
        for k in ("left_role", "left_value", "right_role", "right_value", "delta", "winner"):
            if k in candidate_facts and candidate_facts[k] is not None:
                result[k] = candidate_facts[k]

        if "comparison_label" in candidate_facts and not result.get("comparison_label"):
            result["comparison_label"] = candidate_facts["comparison_label"]
        if "left_unit" in candidate_facts and not result.get("left_unit"):
            result["left_unit"] = candidate_facts["left_unit"]
        if "right_unit" in candidate_facts and not result.get("right_unit"):
            result["right_unit"] = candidate_facts["right_unit"]

    elif composition_id == "cause_effect":
        if "causes" in candidate_facts and candidate_facts["causes"]:
            cand_causes = candidate_facts["causes"]
            llm_causes = result.get("causes", [])
            merged_causes: list[dict[str, Any]] = []
            for i, cc in enumerate(cand_causes):
                item = dict(cc)
                if i < len(llm_causes) and isinstance(llm_causes[i], dict):
                    if llm_causes[i].get("icon"):
                        item["icon"] = llm_causes[i]["icon"]
                    if llm_causes[i].get("value"):
                        item["value"] = llm_causes[i]["value"]
                merged_causes.append(item)
            result["causes"] = merged_causes

        if "outcome_label" in candidate_facts and not result.get("outcome_label"):
            result["outcome_label"] = candidate_facts["outcome_label"]

        if "outcome_severity" in candidate_facts and not result.get("outcome_severity"):
            result["outcome_severity"] = candidate_facts["outcome_severity"]

    elif composition_id == "multi_factor_pressure":
        if "factors" in candidate_facts and candidate_facts["factors"]:
            cand_factors = candidate_facts["factors"]
            llm_factors = result.get("factors", [])
            merged_factors: list[dict[str, Any]] = []
            for i, cf in enumerate(cand_factors):
                item = dict(cf)
                if i < len(llm_factors) and isinstance(llm_factors[i], dict):
                    if llm_factors[i].get("severity"):
                        item["severity"] = llm_factors[i]["severity"]
                    if llm_factors[i].get("value"):
                        item["value"] = llm_factors[i]["value"]
                merged_factors.append(item)
            result["factors"] = merged_factors

        if "combined_label" in candidate_facts and not result.get("combined_label"):
            result["combined_label"] = candidate_facts["combined_label"]

        if "combined_severity" in candidate_facts and not result.get("combined_severity"):
            result["combined_severity"] = candidate_facts["combined_severity"]

        if "outcome_note" in candidate_facts and not result.get("outcome_note"):
            result["outcome_note"] = candidate_facts["outcome_note"]

    elif composition_id == "time_decay":
        if "fixed_amount" in candidate_facts:
            result["fixed_amount"] = candidate_facts["fixed_amount"]
        if "amount_label" in candidate_facts and not result.get("amount_label"):
            result["amount_label"] = candidate_facts["amount_label"]
        if "time_period" in candidate_facts and not result.get("time_period"):
            result["time_period"] = candidate_facts["time_period"]
        if "emphasis" in candidate_facts and not result.get("emphasis"):
            result["emphasis"] = candidate_facts["emphasis"]
        if "annotation" in candidate_facts and not result.get("annotation"):
            result["annotation"] = candidate_facts["annotation"]

    elif composition_id == "ranked_list":
        if "items" in candidate_facts and candidate_facts["items"]:
            result["items"] = candidate_facts["items"]
        if "header_label" in candidate_facts and not result.get("header_label"):
            result["header_label"] = candidate_facts["header_label"]

    elif composition_id == "process_flow":
        if "steps" in candidate_facts and candidate_facts["steps"]:
            result["steps"] = candidate_facts["steps"]
        if "header_label" in candidate_facts and not result.get("header_label"):
            result["header_label"] = candidate_facts["header_label"]

    elif composition_id == "broll_caption":
        if "caption" in candidate_facts and not result.get("caption"):
            result["caption"] = candidate_facts["caption"]
        if "emphasis_phrase" in candidate_facts and not result.get("emphasis_phrase"):
            result["emphasis_phrase"] = candidate_facts["emphasis_phrase"]
        if "author" in candidate_facts and not result.get("author"):
            result["author"] = candidate_facts["author"]

    return result


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

        intent_dict = intent.model_dump(exclude_none=True)
        intent_json = json.dumps(intent_dict, indent=2, ensure_ascii=False)

        user_content = (
            f"Topic: {topic}\n"
            f"Audience: {audience}\n\n"
            f"VISUAL INTENT:\n{intent_json}\n\n"
            "Select the best composition from the catalog for this intent. "
            "Use the structured semantic fields as the primary source of factual data, "
            "and refine the presentation labels, editorial notes, and operation wording. "
            "Return 'no_suitable_composition' if no registered composition fits."
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

        # --- Merge Factual Candidate Data with LLM Presentation Refinements ---
        candidate_facts = build_candidate_composition_data(composition_id, intent)
        composition_data_raw: dict[str, Any] = raw.get("composition_data", {})
        merged_data = merge_factual_and_presentation_data(
            composition_id=composition_id,
            candidate_facts=candidate_facts,
            llm_data=composition_data_raw,
            intent=intent,
        )

        is_valid, errors, normalized_data = CompositionRegistry.validate_composition_data(
            composition_id, merged_data, visual_goal=raw.get("visual_goal", "")
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
