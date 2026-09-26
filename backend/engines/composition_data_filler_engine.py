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
        "time_horizon", "path_a", "path_b", "divergence_gap",
    ),
    "cash_flow_waterfall": (
        "starting_label", "starting_value", "steps", "final_label", "final_value",
        "header_label",
    ),
    "accumulation_decomposition": (
        "total_value", "total_label", "time_horizon", "streams", "annotation", "header_label",
    ),
    "debt_amortization_schedule": (
        "loan_amount", "loan_label", "interest_rate", "tenure", "payment_amount",
        "total_interest", "periods", "annotation", "header_label",
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

# These fields describe presentation or structural treatment rather than a
# source fact. They are intentionally excluded from grounding checks because
# their defaults/enums are owned by the selected composition schema.
_NON_FACTUAL_FIELDS = {
    "connector", "icon", "outcome_severity", "combined_severity", "severity",
    "polarity", "variant", "emphasis", "show_chart", "decay_type", "growth_type",
    "operation_label", "operation_type", "direction", "tone", "winner", "header_label",
    "footer_label", "final_label", "baseline_label", "rank", "numeric_value", "badge",
    "type", "layout", "show_bars", "color_token", "principal_numeric", "interest_numeric",
    "asset_queries",
}

_COLLECTION_CONSTRAINTS: dict[str, dict[str, tuple[int, int | None]]] = {
    "cause_effect": {"causes": (1, 3)},
    "multi_factor_pressure": {"factors": (2, 4)},
    "cash_flow_waterfall": {"steps": (1, 6)},
    "accumulation_decomposition": {"streams": (2, 4)},
    "debt_amortization_schedule": {"periods": (0, 4)},
    "ranked_list": {"items": (2, 5)},
    "process_flow": {"steps": (2, 5)},
}


def _normal(value: Any) -> str:
    return str(value).strip().casefold()


def _iter_factual_values(data: dict[str, Any], composition_id: str) -> list[Any]:
    paths = _FACTUAL_PATHS.get(composition_id, ())
    values: list[Any] = []

    def collect(value: Any, field_name: str | None = None) -> None:
        if field_name in _NON_FACTUAL_FIELDS:
            return
        if isinstance(value, dict):
            for key, nested in value.items():
                if key in _NON_FACTUAL_FIELDS:
                    continue
                collect(nested, key)
        elif isinstance(value, list):
            for nested in value:
                collect(nested, field_name)
        else:
            values.append(value)

    for path in paths:
        if path in _NON_FACTUAL_FIELDS:
            continue
        if path in data:
            collect(data[path], path)
    return values


def _with_filler_constraints(schema: dict[str, Any], composition_id: str) -> dict[str, Any]:
    """Add composition collection limits to the schema used by the filler."""
    constrained = json.loads(json.dumps(schema))
    properties = constrained.get("properties", {})
    for field_name, (minimum, maximum) in _COLLECTION_CONSTRAINTS.get(composition_id, {}).items():
        field_schema = properties.get(field_name)
        if isinstance(field_schema, dict):
            field_schema["minItems"] = minimum
            if maximum is not None:
                field_schema["maxItems"] = maximum
    return constrained


def _validate_collection_constraints(composition_id: str, data: dict[str, Any]) -> None:
    for field_name, (minimum, maximum) in _COLLECTION_CONSTRAINTS.get(composition_id, {}).items():
        value = data.get(field_name)
        if not isinstance(value, list):
            continue
        if len(value) < minimum:
            raise CompositionDataFillerError(
                f"{composition_id}.{field_name} requires at least {minimum} item(s)."
            )
        if maximum is not None and len(value) > maximum:
            raise CompositionDataFillerError(
                f"{composition_id}.{field_name} allows at most {maximum} item(s)."
            )


def _validate_grounding(
    *,
    intent: VisualIntent,
    composition_id: str,
    data: dict[str, Any],
) -> None:
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
        filler_schema = _with_filler_constraints(composition.get_data_schema(), composition.composition_id)
        user_content = (
            f"{source_context}SELECTED COMPOSITION: {composition.composition_id}\n"
            f"DESCRIPTION: {composition.description}\n"
            f"SELECTED DATA SCHEMA:\n{json.dumps(filler_schema, ensure_ascii=False, indent=2)}\n\n"
            f"VISUAL INTENT:\n{intent_json}\n\n"
            "Return exactly one JSON object matching the selected data schema."
        )
        request = LLMJsonRequest(
            schema_name=f"CompositionData:{composition.composition_id}",
            response_schema=filler_schema,
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
        _validate_collection_constraints(composition.composition_id, validated)
        _validate_grounding(intent=intent, composition_id=composition.composition_id, data=validated)
        return CompositionDataFillerResult(
            composition_data=validated,
            provider_metadata=response.metadata,
            raw_payload=payload,
        )
