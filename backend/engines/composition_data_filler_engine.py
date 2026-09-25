"""Schema-scoped, fact-locked composition data filling.

This is deliberately separate from composition selection.  Selection is a
deterministic Python decision; this engine only fills the already selected
composition's schema from one persisted VisualIntent.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

from app.assets import load_prompt
from domain.visual_intent import VisualIntent
from providers.llm_provider import (
    LLMJsonRequest,
    LLMMessage,
    LLMProvider,
    LLMProviderError,
    LLMProviderMetadata,
)
from registries.composition_registry import CompositionDefinition, CompositionRegistry


class CompositionDataFillerError(Exception):
    """Raised when composition data cannot be filled without inventing facts."""


@dataclass(frozen=True)
class CompositionDataFillerResult:
    composition_data: dict[str, Any]
    provider_metadata: LLMProviderMetadata
    raw_payload: dict[str, Any]


_FACTUAL_PATHS: dict[str, tuple[str, ...]] = {
    "metric_hero": ("value", "label", "context", "baseline_value", "delta"),
    "calculation_story": (
        "input_label", "input_value", "rate_label", "result_label", "result_value",
        "timeframe", "secondary_label", "secondary_value",
    ),
    "cause_effect": ("causes", "outcome_label", "outcome_value", "outcome_note"),
    "multi_factor_pressure": ("factors", "combined_label", "outcome_value", "outcome_note"),
    "time_decay": (
        "fixed_amount", "amount_label", "time_period", "annotation", "end_value",
        "end_label", "drop_rate", "rate_label",
    ),
    "growth_trajectory": (
        "start_value", "start_label", "end_value", "end_label", "time_horizon",
        "growth_rate", "milestone_value", "milestone_label", "annotation",
    ),
    "trajectory_divergence": (
        "time_horizon", "baseline_label", "path_a", "path_b", "divergence_gap",
        "header_label",
    ),
    "cash_flow_waterfall": (
        "starting_label", "starting_value", "steps", "final_label", "final_value",
        "header_label",
    ),
    "comparison_split": (
        "left_role", "left_value", "left_label", "left_unit", "right_role", "right_value",
        "right_label", "right_unit", "comparison_label", "delta",
    ),
    "ranked_list": ("items", "header_label", "footer_label"),
    "process_flow": ("steps", "header_label", "footer_label"),
    "broll_caption": ("caption", "emphasis_phrase", "author", "header_label", "source_context"),
}

_PLACEHOLDERS = {
    "unknown", "n/a", "na", "null", "none", "not provided", "not available",
    "original value", "starting value", "initial value", "target corpus",
    "common starting point", "option a", "option b", "result",
}


def _normal(value: Any) -> str:
    return str(value).strip().casefold()


def _walk_strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value] if value.strip() else []
    if isinstance(value, dict):
        result: list[str] = []
        for item in value.values():
            result.extend(_walk_strings(item))
        return result
    if isinstance(value, list):
        result = []
        for item in value:
            result.extend(_walk_strings(item))
        return result
    return []


def _source_facts(intent: VisualIntent) -> set[str]:
    """Return verbatim semantic values that may be copied into composition data."""
    facts: list[str] = list(intent.key_values)
    for entity in intent.entities:
        facts.extend(value for value in (entity.name, entity.role, entity.category) if value)
    for measurement in intent.measurements:
        facts.extend(
            value for value in (
                measurement.raw_value, measurement.entity_name, measurement.metric_name,
                measurement.unit,
            ) if value
        )
    if intent.temporal:
        facts.extend(value for value in (intent.temporal.horizon, intent.temporal.frequency) if value)
    if intent.causal:
        facts.extend(intent.causal.causes)
        facts.extend(value for value in (intent.causal.mechanism, intent.causal.outcome, intent.causal.outcome_severity) if value)
    if intent.comparison:
        facts.extend(
            value for value in (
                intent.comparison.subject_a, intent.comparison.value_a,
                intent.comparison.subject_b, intent.comparison.value_b,
                intent.comparison.comparison_dimension, intent.comparison.delta,
                intent.comparison.winner,
            ) if value
        )
    # Narration and the viewer-understanding sentence are valid source text for
    # labels/captions, but do not make up new numeric values.
    facts.extend((intent.narration_excerpt, intent.what_viewer_must_understand))
    return {_normal(value) for value in facts if value}


def _source_numbers(intent: VisualIntent) -> set[str]:
    source_text = " ".join(_walk_strings(intent.model_dump()))
    return set(re.findall(r"\d+(?:[.,]\d+)*", source_text))


def _iter_factual_values(data: dict[str, Any], composition_id: str) -> list[Any]:
    paths = _FACTUAL_PATHS.get(composition_id, ())
    values: list[Any] = []

    def collect(value: Any) -> None:
        if isinstance(value, dict):
            for nested in value.values():
                collect(nested)
        elif isinstance(value, list):
            for nested in value:
                collect(nested)
        else:
            values.append(value)

    for path in paths:
        if path in data:
            collect(data[path])
    return values


def _validate_grounding(
    *,
    intent: VisualIntent,
    composition_id: str,
    data: dict[str, Any],
) -> None:
    facts = _source_facts(intent)
    source_numbers = _source_numbers(intent)
    for value in _iter_factual_values(data, composition_id):
        if value is None or isinstance(value, bool):
            continue
        text = str(value).strip()
        if not text:
            continue
        if _normal(text) in _PLACEHOLDERS:
            raise CompositionDataFillerError(
                f"{composition_id} contains placeholder factual value '{text}'."
            )
        output_numbers = set(re.findall(r"\d+(?:[.,]\d+)*", text))
        if output_numbers and not output_numbers.issubset(source_numbers):
            raise CompositionDataFillerError(
                f"{composition_id} contains numeric value '{text}' not present in VisualIntent."
            )
        # Exact semantic values are required for fields that carry facts.  A
        # prose caption may contain source text, so accept it when it is a
        # substring of the verbatim excerpt.
        if _normal(text) not in facts and _normal(text) not in _normal(intent.narration_excerpt):
            raise CompositionDataFillerError(
                f"{composition_id} contains unsupported factual value '{text}'."
            )


class CompositionDataFillerEngine:
    """Fill only the selected composition schema using one VisualIntent."""

    def __init__(self, llm_provider: LLMProvider | None):
        self.llm_provider = llm_provider

    def fill(
        self,
        *,
        intent: VisualIntent,
        composition: CompositionDefinition,
        source_artifact_id: str | None = None,
        source_idea_id: str | None = None,
    ) -> CompositionDataFillerResult:
        if self.llm_provider is None:
            raise CompositionDataFillerError(
                "Composition data filling requires an LLM provider; no fallback data is permitted."
            )

        intent_json = json.dumps(intent.model_dump(exclude_none=True), ensure_ascii=False, indent=2)
        source_context = (
            f"Source visual_intent artifact: {source_artifact_id}\n"
            f"Source idea: {source_idea_id}\n"
            if source_artifact_id or source_idea_id else ""
        )
        user_content = (
            f"{source_context}SELECTED COMPOSITION: {composition.composition_id}\n"
            f"DESCRIPTION: {composition.description}\n"
            f"SELECTED DATA SCHEMA:\n{json.dumps(composition.get_data_schema(), ensure_ascii=False, indent=2)}\n\n"
            f"VISUAL INTENT:\n{intent_json}\n\n"
            "Return exactly one JSON object matching the selected data schema."
        )
        request = LLMJsonRequest(
            schema_name=f"CompositionData:{composition.composition_id}",
            response_schema=composition.get_data_schema(),
            messages=[
                LLMMessage(role="system", content=load_prompt("composition_data_filler_system.txt")),
                LLMMessage(role="user", content=user_content),
            ],
            temperature=0.1,
            max_tokens=1200,
        )
        try:
            response = self.llm_provider.generate_json(request)
        except LLMProviderError as exc:
            raise CompositionDataFillerError(str(exc)) from exc
        except Exception as exc:
            raise CompositionDataFillerError(f"Composition data provider failed: {exc}") from exc

        payload = response.payload
        if not isinstance(payload, dict):
            raise CompositionDataFillerError("Composition data response must be a JSON object.")
        valid, errors, validated = CompositionRegistry.validate_composition_data(
            composition.composition_id,
            payload,
            visual_goal=intent.what_viewer_must_understand,
        )
        if not valid:
            raise CompositionDataFillerError(
                f"Invalid {composition.composition_id} data: {'; '.join(errors)}"
            )
        _validate_grounding(intent=intent, composition_id=composition.composition_id, data=validated)
        return CompositionDataFillerResult(
            composition_data=validated,
            provider_metadata=response.metadata,
            raw_payload=payload,
        )
