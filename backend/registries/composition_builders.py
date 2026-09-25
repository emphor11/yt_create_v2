"""
Authoritative Deterministic Composition Builders and Eligibility Guards.

This module provides the single source of truth for constructing composition_data
directly and deterministically from structured VisualIntent domain models.

Principles:
- Pure Python, zero LLM calls.
- Fail-fast: raises CompositionDataError whenever required data is missing or invalid.
- Strict factual locking: no invented financial numbers, balances, rates, or placeholder labels.
- Never slices narration or what_viewer_must_understand to fabricate missing labels or causes.
- Never copies start_value to end_value in growth trajectories.
- Derived values (e.g., waterfall balance) are computed mathematically only when
  all necessary input numbers exist in the source intent.
- Variants are selected based on semantic intent signals.
"""
from __future__ import annotations

import re
from typing import Any

from domain.visual_intent import VisualIntent


class CompositionDataError(Exception):
    """Raised when structured VisualIntent lacks required data for deterministic composition building."""

    def __init__(
        self,
        composition_id: str,
        missing_field: str,
        expected_source: str,
        details: str = "",
    ):
        msg = (
            f"Cannot build data for composition '{composition_id}': "
            f"missing required field '{missing_field}'. Expected source: {expected_source}."
        )
        if details:
            msg += f" Details: {details}"
        super().__init__(msg)
        self.composition_id = composition_id
        self.missing_field = missing_field
        self.expected_source = expected_source
        self.details = details


# ---------------------------------------------------------------------------
# Metric Hero
# ---------------------------------------------------------------------------

def is_eligible_metric_hero(intent: VisualIntent) -> bool:
    """
    metric_hero requires exactly one authoritative quantitative measurement
    with raw_value and metric_name or entity_name.
    Ambiguous multiple measurements without explicit primary/metric role fail.
    """
    if not intent.measurements:
        return False
    if len(intent.measurements) == 1:
        m = intent.measurements[0]
        return bool(m.raw_value and (m.metric_name or m.entity_name))
    # Multiple measurements: exactly one with an authoritative primary role (input preferred over baseline).
    # Roles rate/delta/context are supporting, never the hero.
    primary_candidates = [m for m in intent.measurements if m.role == "input"]
    if len(primary_candidates) == 1:
        m = primary_candidates[0]
        return bool(m.raw_value and (m.metric_name or m.entity_name))
    baseline_candidates = [m for m in intent.measurements if m.role == "baseline"]
    if len(baseline_candidates) == 1:
        m = baseline_candidates[0]
        return bool(m.raw_value and (m.metric_name or m.entity_name))
    return False


def build_metric_hero_data(intent: VisualIntent) -> dict[str, Any]:
    if not intent.measurements:
        raise CompositionDataError(
            "metric_hero",
            "measurements",
            "intent.measurements",
            "At least one authoritative measurement is required.",
        )

    if len(intent.measurements) == 1:
        m = intent.measurements[0]
    else:
        primary_candidates = [mm for mm in intent.measurements if mm.role == "input"]
        if len(primary_candidates) == 1:
            m = primary_candidates[0]
        else:
            baseline_candidates = [mm for mm in intent.measurements if mm.role == "baseline"]
            if len(baseline_candidates) == 1:
                m = baseline_candidates[0]
            else:
                raise CompositionDataError(
                    "metric_hero",
                    "measurement",
                    "single authoritative measurement with role='input' or role='baseline'",
                    f"Multiple measurements ({len(intent.measurements)}) present without a single authoritative primary role.",
                )

    if not m.raw_value:
        raise CompositionDataError(
            "metric_hero",
            "value",
            "authoritative measurement.raw_value",
        )

    label = m.metric_name or m.entity_name
    if not label:
        raise CompositionDataError(
            "metric_hero",
            "label",
            "measurement.metric_name or measurement.entity_name",
            "No placeholder or entity list fallback allowed.",
        )

    candidate: dict[str, Any] = {
        "value": m.raw_value,
        "label": label,
    }

    if m.polarity:
        candidate["polarity"] = m.polarity
    if m.direction:
        candidate["direction"] = m.direction

    baseline_m = next((bm for bm in intent.measurements if bm.role == "baseline" and bm != m), None)
    if baseline_m and baseline_m.raw_value:
        candidate["baseline_value"] = baseline_m.raw_value

    delta_m = next((dm for dm in intent.measurements if dm.role == "delta" and dm != m), None)
    if delta_m and delta_m.raw_value:
        candidate["delta"] = delta_m.raw_value

    if intent.temporal:
        if intent.temporal.frequency:
            candidate["context"] = intent.temporal.frequency
        elif intent.temporal.horizon:
            candidate["context"] = intent.temporal.horizon

    if intent.emphasis:
        candidate["emphasis"] = intent.emphasis

    # Variant resolution
    if candidate.get("baseline_value"):
        candidate["variant"] = "before_after_metric"
    elif candidate.get("polarity") == "warning":
        candidate["variant"] = "warning_metric"
    elif intent.emphasis in ("hero", "climax"):
        candidate["variant"] = "hero_milestone"
    else:
        candidate["variant"] = "supporting_metric"

    return candidate


# ---------------------------------------------------------------------------
# Calculation Story
# ---------------------------------------------------------------------------

def is_eligible_calculation_story(intent: VisualIntent) -> bool:
    """
    calculation_story requires explicit input/baseline and result measurements
    with raw_value and metric_name or entity_name.
    """
    input_m = next((m for m in intent.measurements if m.role in ("input", "baseline")), None)
    result_m = next((m for m in intent.measurements if m.role in ("result", "outcome", "target", "impact") and m != input_m), None)
    if not input_m or not result_m:
        return False
    if not (input_m.raw_value and result_m.raw_value):
        return False
    has_input_label = bool(input_m.metric_name or input_m.entity_name)
    has_result_label = bool(result_m.metric_name or result_m.entity_name)
    return has_input_label and has_result_label


def build_calculation_story_data(intent: VisualIntent) -> dict[str, Any]:
    input_m = next((m for m in intent.measurements if m.role in ("input", "baseline")), None)
    if not input_m or not input_m.raw_value:
        raise CompositionDataError(
            "calculation_story",
            "input_value",
            "measurement with role in ('input', 'baseline')",
            "Positional measurements[0] or key_values fallback is prohibited.",
        )

    input_label = input_m.metric_name or input_m.entity_name
    if not input_label:
        raise CompositionDataError(
            "calculation_story",
            "input_label",
            "input measurement.metric_name or input measurement.entity_name",
            "No placeholder 'Initial Value' or entity list fallback allowed.",
        )

    result_m = next((m for m in intent.measurements if m.role in ("result", "outcome", "target", "impact") and m != input_m), None)
    if not result_m or not result_m.raw_value:
        raise CompositionDataError(
            "calculation_story",
            "result_value",
            "measurement with role in ('result', 'outcome', 'target', 'impact')",
            "Positional measurements[-1] or key_values fallback is prohibited.",
        )

    result_label = result_m.metric_name or result_m.entity_name
    if not result_label:
        raise CompositionDataError(
            "calculation_story",
            "result_label",
            "result measurement.metric_name or result measurement.entity_name",
            "No placeholder 'Result' or entity list fallback allowed.",
        )

    candidate: dict[str, Any] = {
        "input_value": input_m.raw_value,
        "input_label": input_label,
        "result_value": result_m.raw_value,
        "result_label": result_label,
    }

    if result_m.polarity:
        candidate["polarity"] = result_m.polarity

    rate_m = next((m for m in intent.measurements if m.role == "rate" and m not in (input_m, result_m)), None)
    if rate_m and rate_m.raw_value:
        candidate["rate_label"] = rate_m.raw_value
        if "%" not in rate_m.raw_value:
            candidate["secondary_value"] = rate_m.raw_value
            candidate["secondary_label"] = rate_m.metric_name or rate_m.entity_name

    if intent.temporal and intent.temporal.horizon:
        candidate["timeframe"] = intent.temporal.horizon

    # Contextual operation type derivation: strictly from structured temporal or rate
    if candidate.get("timeframe"):
        candidate["operation_type"] = "growth"
        candidate["variant"] = "growth"
    elif candidate.get("rate_label") and "%" in candidate["rate_label"]:
        candidate["operation_type"] = "multiplication"
        candidate["variant"] = "multiplication"
    else:
        candidate["operation_type"] = "neutral"
        candidate["variant"] = "neutral"

    if intent.visual_dynamics and intent.visual_dynamics.focal_point:
        candidate["note"] = intent.visual_dynamics.focal_point

    return candidate


# ---------------------------------------------------------------------------
# Cause Effect
# ---------------------------------------------------------------------------

def is_eligible_cause_effect(intent: VisualIntent) -> bool:
    """cause_effect requires structured intent.causal with at least one cause and an explicit outcome."""
    return bool(intent.causal and intent.causal.causes and len(intent.causal.causes) >= 1 and intent.causal.outcome)


def build_cause_effect_data(intent: VisualIntent) -> dict[str, Any]:
    if not (intent.causal and intent.causal.causes):
        raise CompositionDataError(
            "cause_effect",
            "causes",
            "intent.causal.causes",
            "Reconstructing causes from entities, key_values, or narration is prohibited.",
        )

    if not (intent.causal and intent.causal.outcome):
        raise CompositionDataError(
            "cause_effect",
            "outcome_label",
            "intent.causal.outcome",
            "Slicing what_viewer_must_understand is prohibited.",
        )

    candidate: dict[str, Any] = {
        "causes": [{"label": c} for c in intent.causal.causes[:3]],
        "outcome_label": intent.causal.outcome,
        "connector": intent.trigger_word or "leads to",
    }

    if intent.causal.outcome_severity:
        sev = intent.causal.outcome_severity.lower()
        if sev in ("critical", "high", "medium"):
            candidate["outcome_severity"] = "negative"
        elif sev == "positive":
            candidate["outcome_severity"] = "positive"
        elif sev == "neutral":
            candidate["outcome_severity"] = "neutral"

    if intent.causal.mechanism:
        candidate["outcome_note"] = intent.causal.mechanism

    if intent.measurements:
        for m in intent.measurements:
            if m.role in ("result", "delta", "impact") or (
                m.entity_name
                and m.entity_name.lower() in candidate["outcome_label"].lower()
            ):
                candidate["outcome_value"] = m.raw_value
                break

    causes_count = len(candidate["causes"])
    if causes_count == 1:
        candidate["variant"] = "single_cause"
    elif causes_count == 2:
        candidate["variant"] = "dual_cause"
    else:
        candidate["variant"] = "multi_cause"

    if candidate.get("outcome_severity"):
        candidate["polarity"] = candidate["outcome_severity"]

    return candidate


# ---------------------------------------------------------------------------
# Comparison Split
# ---------------------------------------------------------------------------

def is_eligible_comparison_split(intent: VisualIntent) -> bool:
    """comparison_split requires structured ComparisonStructure with subjects, values, and comparison dimension."""
    return bool(
        intent.comparison
        and intent.comparison.subject_a
        and intent.comparison.subject_b
        and intent.comparison.value_a
        and intent.comparison.value_b
        and intent.comparison.comparison_dimension
    )


def build_comparison_split_data(intent: VisualIntent) -> dict[str, Any]:
    if not intent.comparison:
        raise CompositionDataError(
            "comparison_split",
            "comparison",
            "intent.comparison",
            "Constructing comparison from entities or positional measurements is prohibited.",
        )

    cmp = intent.comparison
    if not cmp.subject_a:
        raise CompositionDataError(
            "comparison_split",
            "left_role",
            "intent.comparison.subject_a",
            "No placeholder 'Option A' allowed.",
        )
    if not cmp.value_a:
        raise CompositionDataError(
            "comparison_split",
            "left_value",
            "intent.comparison.value_a",
            "No placeholder '-' allowed.",
        )
    if not cmp.subject_b:
        raise CompositionDataError(
            "comparison_split",
            "right_role",
            "intent.comparison.subject_b",
            "No placeholder 'Option B' allowed.",
        )
    if not cmp.value_b:
        raise CompositionDataError(
            "comparison_split",
            "right_value",
            "intent.comparison.value_b",
            "No placeholder '-' allowed.",
        )
    if not cmp.comparison_dimension:
        raise CompositionDataError(
            "comparison_split",
            "comparison_label",
            "intent.comparison.comparison_dimension",
        )

    candidate: dict[str, Any] = {
        "left_role": cmp.subject_a,
        "left_value": cmp.value_a,
        "right_role": cmp.subject_b,
        "right_value": cmp.value_b,
        "comparison_label": cmp.comparison_dimension,
    }

    if cmp.delta:
        candidate["delta"] = cmp.delta

    if cmp.winner:
        w = cmp.winner.strip().lower()
        sa = (cmp.subject_a or "").strip().lower()
        sb = (cmp.subject_b or "").strip().lower()
        if w in ("left", sa):
            candidate["winner"] = "left"
        elif w in ("right", sb):
            candidate["winner"] = "right"

    # Units from measurements if matching entity
    if intent.measurements:
        for m in intent.measurements:
            if m.unit and m.entity_name:
                if candidate.get("left_role") and m.entity_name.lower() in candidate["left_role"].lower():
                    candidate["left_unit"] = m.unit
                elif candidate.get("right_role") and m.entity_name.lower() in candidate["right_role"].lower():
                    candidate["right_unit"] = m.unit

    candidate["variant"] = "versus" if candidate.get("delta") else "cards"
    return candidate


# ---------------------------------------------------------------------------
# Ranked List
# ---------------------------------------------------------------------------

def is_eligible_ranked_list(intent: VisualIntent) -> bool:
    """ranked_list requires at least 2 structured entities with names."""
    return bool(intent.entities and len(intent.entities) >= 2 and all(e.name for e in intent.entities))


def build_ranked_list_data(intent: VisualIntent) -> dict[str, Any]:
    if not (intent.entities and len(intent.entities) >= 2):
        raise CompositionDataError(
            "ranked_list",
            "items",
            "intent.entities (>= 2 with name)",
            "key_values or arbitrary guessing is prohibited. VisualIntent entities list is authoritative.",
        )

    items: list[dict[str, Any]] = []
    for idx, e in enumerate(intent.entities[:5]):
        if not e.name:
            raise CompositionDataError(
                "ranked_list",
                "entity.name",
                f"intent.entities[{idx}].name",
            )
        matching_m = next((m for m in intent.measurements if m.entity_name == e.name), None)
        val = matching_m.raw_value if matching_m else None
        num_val = matching_m.numeric_value if matching_m else None
        items.append({
            "title": e.name,
            "rank": idx + 1,
            "value": val,
            "numeric_value": num_val,
        })

    candidate: dict[str, Any] = {
        "items": items,
        "header_label": intent.visual_dynamics.focal_point if intent.visual_dynamics and intent.visual_dynamics.focal_point else None,
        "variant": "standard",
    }
    return candidate


# ---------------------------------------------------------------------------
# Process Flow
# ---------------------------------------------------------------------------

def is_eligible_process_flow(intent: VisualIntent) -> bool:
    """process_flow requires at least 2 structured entities representing chronological steps."""
    return bool(intent.entities and len(intent.entities) >= 2 and all(e.name for e in intent.entities))


def build_process_flow_data(intent: VisualIntent) -> dict[str, Any]:
    if not (intent.entities and len(intent.entities) >= 2):
        raise CompositionDataError(
            "process_flow",
            "steps",
            "intent.entities (>= 2 with name)",
            "key_values or arbitrary guessing is prohibited. VisualIntent entities list is authoritative.",
        )

    steps: list[dict[str, Any]] = []
    for idx, e in enumerate(intent.entities[:5]):
        if not e.name:
            raise CompositionDataError(
                "process_flow",
                "entity.name",
                f"intent.entities[{idx}].name",
            )
        steps.append({
            "title": e.name,
            "subtitle": e.role if e.role and not e.role.startswith("step_") else None,
            "type": "step",
        })

    candidate: dict[str, Any] = {
        "steps": steps,
        "variant": "horizontal" if len(steps) <= 3 else "vertical",
    }
    if intent.visual_dynamics and intent.visual_dynamics.focal_point:
        candidate["header_label"] = intent.visual_dynamics.focal_point

    return candidate


# ---------------------------------------------------------------------------
# Time Decay
# ---------------------------------------------------------------------------

def is_eligible_time_decay(intent: VisualIntent) -> bool:
    """
    time_decay requires decline/trend intent with:
    1. Explicit temporal.horizon
    2. Explicit baseline/input measurement with raw_value and label
    3. Explicit decline measurement (rate with %, delta with downward direction or minus, or negative result)
    """
    if intent.relationship_type not in ("decline", "trend"):
        return False
    if not (intent.temporal and intent.temporal.horizon):
        return False

    baseline_m = next((m for m in intent.measurements if m.role in ("baseline", "input")), None)
    if not baseline_m or not baseline_m.raw_value:
        return False
    if not (baseline_m.entity_name or baseline_m.metric_name):
        return False

    rate_m = next((m for m in intent.measurements if m.role == "rate" and "%" in m.raw_value), None)
    delta_m = next(
        (m for m in intent.measurements if m.role == "delta" and (m.direction == "down" or m.raw_value.startswith("-"))),
        None,
    )
    result_m = next(
        (m for m in intent.measurements if m.role == "result" and (m.direction == "down" or m.polarity == "negative")),
        None,
    )
    pct_m = next((m for m in intent.measurements if "%" in m.raw_value and m.direction == "down"), None)

    return bool(rate_m or delta_m or result_m or pct_m)


def build_time_decay_data(intent: VisualIntent) -> dict[str, Any]:
    if not (intent.temporal and intent.temporal.horizon):
        raise CompositionDataError(
            "time_decay",
            "time_period",
            "intent.temporal.horizon",
            "No placeholder 'Over Time' or narration keyword detection allowed.",
        )

    baseline_m = next((m for m in intent.measurements if m.role in ("baseline", "input")), None)
    if not baseline_m or not baseline_m.raw_value:
        raise CompositionDataError(
            "time_decay",
            "fixed_amount",
            "measurement with role in ('baseline', 'input')",
            "Positional measurements[0], key_values, or entities fallback is prohibited.",
        )

    amount_label = baseline_m.entity_name or baseline_m.metric_name
    if not amount_label:
        raise CompositionDataError(
            "time_decay",
            "amount_label",
            "baseline measurement.entity_name or baseline measurement.metric_name",
            "No placeholder 'Asset Value' or 'Original Value' allowed.",
        )

    candidate: dict[str, Any] = {
        "time_period": intent.temporal.horizon,
        "fixed_amount": baseline_m.raw_value,
        "amount_label": amount_label,
    }

    rate_m = next((m for m in intent.measurements if m.role == "rate" and "%" in m.raw_value), None)
    delta_m = next(
        (m for m in intent.measurements if m.role == "delta" and (m.direction == "down" or m.raw_value.startswith("-"))),
        None,
    )
    result_m = next(
        (m for m in intent.measurements if m.role == "result" and (m.direction == "down" or m.polarity == "negative")),
        None,
    )
    pct_m = next((m for m in intent.measurements if "%" in m.raw_value and m.direction == "down"), None)

    if not (rate_m or delta_m or result_m or pct_m):
        raise CompositionDataError(
            "time_decay",
            "drop_rate or end_value",
            "measurements with rate, decline delta, or negative result",
            "A decay curve requires an explicit drop rate or end value. Focal point alone is not sufficient.",
        )

    if rate_m:
        candidate["drop_rate"] = rate_m.raw_value
        candidate["rate_label"] = rate_m.raw_value
    elif delta_m:
        candidate["drop_rate"] = delta_m.raw_value
        candidate["rate_label"] = delta_m.raw_value
    elif pct_m:
        candidate["drop_rate"] = pct_m.raw_value
        candidate["rate_label"] = pct_m.raw_value

    if result_m:
        candidate["end_value"] = result_m.raw_value
        candidate["end_label"] = result_m.entity_name or result_m.metric_name or "Remaining Value"
        candidate["annotation"] = f"Erodes to {result_m.raw_value}"
    elif intent.visual_dynamics and intent.visual_dynamics.focal_point:
        candidate["annotation"] = intent.visual_dynamics.focal_point

    if intent.temporal and intent.temporal.is_decay_over_time:
        candidate["decay_type"] = "purchasing_power"
        candidate["emphasis"] = "purchasing_power_decline"
        candidate["variant"] = "inflation_erosion"
    else:
        candidate["decay_type"] = "standard"
        candidate["emphasis"] = "value_erosion"
        candidate["variant"] = "standard"

    # Severity resolution
    if intent.visual_dynamics:
        if intent.visual_dynamics.visual_priority in ("high", "primary"):
            candidate["severity"] = "severe"
        elif intent.visual_dynamics.visual_priority in ("secondary", "context"):
            candidate["severity"] = "mild"

    if not candidate.get("severity") and candidate.get("drop_rate"):
        m = re.search(r"(\d+(?:\.\d+)?)\s*%", candidate["drop_rate"])
        if m:
            pct = float(m.group(1))
            if pct <= 20:
                candidate["severity"] = "mild"
            elif pct >= 50:
                candidate["severity"] = "severe"
            else:
                candidate["severity"] = "moderate"

    return candidate


# ---------------------------------------------------------------------------
# Growth Trajectory
# ---------------------------------------------------------------------------

def is_eligible_growth_trajectory(intent: VisualIntent) -> bool:
    """growth_trajectory requires distinct start and end measurements with authoritative labels."""
    if intent.relationship_type not in ("growth", "trend"):
        return False

    start_m = next((m for m in intent.measurements if m.role in ("input", "baseline", "initial")), None)
    end_m = next((m for m in intent.measurements if m.role in ("result", "final", "outcome", "target") and m != start_m), None)

    if not start_m or not end_m:
        return False

    if not (start_m.raw_value and end_m.raw_value):
        return False

    if start_m.raw_value == end_m.raw_value:
        return False

    has_start_lbl = bool(start_m.metric_name or start_m.entity_name)
    has_end_lbl = bool(end_m.metric_name or end_m.entity_name)
    return has_start_lbl and has_end_lbl


def build_growth_trajectory_data(intent: VisualIntent) -> dict[str, Any]:
    start_m = next((m for m in intent.measurements if m.role in ("input", "baseline", "initial")), None)
    if not start_m or not start_m.raw_value:
        raise CompositionDataError(
            "growth_trajectory",
            "start_value",
            "measurement with role in ('input', 'baseline', 'initial')",
            "Positional measurements[0], key_values, or copied values are prohibited.",
        )

    start_label = start_m.metric_name or start_m.entity_name
    if not start_label:
        raise CompositionDataError(
            "growth_trajectory",
            "start_label",
            "start measurement.metric_name or start measurement.entity_name",
            "No placeholder 'Starting Point' or entities fallback allowed.",
        )

    end_m = next((m for m in intent.measurements if m.role in ("result", "final", "outcome", "target") and m != start_m), None)
    if not end_m or not end_m.raw_value:
        raise CompositionDataError(
            "growth_trajectory",
            "end_value",
            "measurement with role in ('result', 'final', 'outcome', 'target')",
            "Positional measurements[-1], key_values, or copied values are prohibited.",
        )

    end_label = end_m.metric_name or end_m.entity_name
    if not end_label:
        raise CompositionDataError(
            "growth_trajectory",
            "end_label",
            "end measurement.metric_name or end measurement.entity_name",
            "No placeholder 'Target Corpus' or entities fallback allowed.",
        )

    # FAIL-FAST: start_value and end_value must be distinct
    if start_m.raw_value == end_m.raw_value:
        raise CompositionDataError(
            "growth_trajectory",
            "end_value",
            "distinct end_value from start_value",
            f"start_value and end_value are identical: '{start_m.raw_value}'. GrowthTrajectory requires distinct growth endpoints.",
        )

    candidate: dict[str, Any] = {
        "start_value": start_m.raw_value,
        "start_label": start_label,
        "end_value": end_m.raw_value,
        "end_label": end_label,
        "growth_type": "linear",
        "variant": "standard",
    }

    rate_m = next((m for m in intent.measurements if m.role == "rate" and m not in (start_m, end_m)), None)
    if rate_m and rate_m.raw_value:
        candidate["growth_rate"] = rate_m.raw_value

    milestone_m = next((m for m in intent.measurements if m.role in ("milestone", "intermediate", "benchmark") and m not in (start_m, end_m)), None)
    if milestone_m and milestone_m.raw_value:
        candidate["milestone_value"] = milestone_m.raw_value
        if milestone_m.metric_name or milestone_m.entity_name:
            candidate["milestone_label"] = milestone_m.metric_name or milestone_m.entity_name
        candidate["variant"] = "milestone_progression"

    if intent.temporal and intent.temporal.horizon:
        candidate["time_horizon"] = intent.temporal.horizon

    if intent.visual_dynamics and intent.visual_dynamics.focal_point:
        candidate["annotation"] = intent.visual_dynamics.focal_point

    return candidate


# ---------------------------------------------------------------------------
# Multi-Factor Pressure
# ---------------------------------------------------------------------------

def is_eligible_multi_factor_pressure(intent: VisualIntent) -> bool:
    """multi_factor_pressure requires at least 2 causal causes, an explicit outcome, and explicit severity."""
    has_factors = bool(intent.causal and intent.causal.causes and len(intent.causal.causes) >= 2)
    has_outcome = bool(intent.causal and intent.causal.outcome)
    has_severity = bool(
        intent.causal
        and intent.causal.outcome_severity
        and intent.causal.outcome_severity.lower() in ("critical", "high", "medium")
    )
    return has_factors and has_outcome and has_severity


def build_multi_factor_pressure_data(intent: VisualIntent) -> dict[str, Any]:
    if not (intent.causal and intent.causal.causes and len(intent.causal.causes) >= 2):
        raise CompositionDataError(
            "multi_factor_pressure",
            "factors",
            "intent.causal.causes (>= 2)",
            "Using entities, key_values, or narration text to construct factors is prohibited.",
        )

    if not (intent.causal and intent.causal.outcome):
        raise CompositionDataError(
            "multi_factor_pressure",
            "combined_label",
            "intent.causal.outcome",
            "Slicing what_viewer_must_understand is prohibited.",
        )

    if not (
        intent.causal
        and intent.causal.outcome_severity
        and intent.causal.outcome_severity.lower() in ("critical", "high", "medium")
    ):
        raise CompositionDataError(
            "multi_factor_pressure",
            "combined_severity",
            "intent.causal.outcome_severity ('critical', 'high', 'medium')",
            "Cannot default severity to 'high' or invent severity.",
        )

    sev = intent.causal.outcome_severity.lower()
    factors: list[dict[str, Any]] = [
        {"label": c, "severity": sev} for c in intent.causal.causes[:4]
    ]

    candidate: dict[str, Any] = {
        "factors": factors,
        "combined_label": intent.causal.outcome,
        "combined_severity": sev,
        "polarity": sev,
        "outcome_header_label": f"{sev.upper()} THREAT",
    }

    if intent.causal.mechanism:
        candidate["outcome_note"] = intent.causal.mechanism

    if intent.measurements:
        res_m = next((m for m in intent.measurements if m.role in ("result", "delta", "impact")), None)
        if not res_m and candidate.get("combined_label"):
            cl = candidate["combined_label"].lower()
            res_m = next((m for m in intent.measurements if m.entity_name and m.entity_name.lower() in cl), None)
        if res_m:
            candidate["outcome_value"] = res_m.raw_value

    factor_count = len(factors)
    if factor_count == 2:
        candidate["variant"] = "dual_factor"
    elif factor_count == 3:
        candidate["variant"] = "tri_factor"
    elif factor_count >= 4:
        candidate["variant"] = "quad_factor"
    else:
        candidate["variant"] = "standard"

    return candidate


# ---------------------------------------------------------------------------
# Trajectory Divergence
# ---------------------------------------------------------------------------

def is_eligible_trajectory_divergence(intent: VisualIntent) -> bool:
    """
    trajectory_divergence requires explicit divergence relationship, temporal horizon,
    and ComparisonStructure with dual paths.
    """
    has_horizon = bool(intent.temporal and intent.temporal.horizon)
    has_dual_paths = bool(
        intent.comparison
        and intent.comparison.subject_a
        and intent.comparison.subject_b
        and intent.comparison.value_a
        and intent.comparison.value_b
    )
    return has_horizon and has_dual_paths


def build_trajectory_divergence_data(intent: VisualIntent) -> dict[str, Any]:
    if not (intent.temporal and intent.temporal.horizon):
        raise CompositionDataError(
            "trajectory_divergence",
            "time_horizon",
            "intent.temporal.horizon",
            "No placeholder 'Over Time' allowed.",
        )

    if not intent.comparison:
        raise CompositionDataError(
            "trajectory_divergence",
            "comparison",
            "intent.comparison",
            "Constructing divergent paths from entities or measurements is prohibited.",
        )

    cmp = intent.comparison
    if not cmp.subject_a:
        raise CompositionDataError(
            "trajectory_divergence",
            "path_a.label",
            "intent.comparison.subject_a",
            "No placeholder 'Path A' allowed.",
        )
    if not cmp.subject_b:
        raise CompositionDataError(
            "trajectory_divergence",
            "path_b.label",
            "intent.comparison.subject_b",
            "No placeholder 'Path B' allowed.",
        )
    if not cmp.value_a:
        raise CompositionDataError(
            "trajectory_divergence",
            "path_a.end_value",
            "intent.comparison.value_a",
            "No fabricated trajectory value allowed.",
        )
    if not cmp.value_b:
        raise CompositionDataError(
            "trajectory_divergence",
            "path_b.end_value",
            "intent.comparison.value_b",
            "No fabricated trajectory value allowed.",
        )

    path_a: dict[str, Any] = {
        "label": cmp.subject_a,
        "end_value": cmp.value_a,
    }
    path_b: dict[str, Any] = {
        "label": cmp.subject_b,
        "end_value": cmp.value_b,
    }

    # Rate from authoritative role=rate measurements (not by label keyword)
    rate_ms = [m for m in intent.measurements if m.role == "rate" and m.raw_value]
    if len(rate_ms) >= 1:
        path_a["rate"] = rate_ms[0].raw_value
    if len(rate_ms) >= 2:
        path_b["rate"] = rate_ms[1].raw_value

    candidate: dict[str, Any] = {
        "time_horizon": intent.temporal.horizon,
        "path_a": path_a,
        "path_b": path_b,
    }

    if cmp.comparison_dimension:
        candidate["baseline_label"] = cmp.comparison_dimension

    if cmp.delta:
        candidate["divergence_gap"] = cmp.delta

    if intent.visual_dynamics and intent.visual_dynamics.focal_point:
        candidate["header_label"] = intent.visual_dynamics.focal_point

    candidate["variant"] = "divergence"

    return candidate


# ---------------------------------------------------------------------------
# Cash Flow Waterfall
# ---------------------------------------------------------------------------

def is_eligible_cash_flow_waterfall(intent: VisualIntent) -> bool:
    """
    cash_flow_waterfall requires:
    - Exactly one measurement with role == "baseline" (with a label).
    - At least one measurement with role == "delta" (with a label and explicit direction).
    """
    has_baseline = any(
        m.role == "baseline" and (m.metric_name or m.entity_name)
        for m in intent.measurements
    )
    has_delta = any(
        m.role == "delta" and (m.metric_name or m.entity_name)
        for m in intent.measurements
    )
    return has_baseline and has_delta


def build_cash_flow_waterfall_data(intent: VisualIntent) -> dict[str, Any]:
    candidate: dict[str, Any] = {}

    baseline_m = next(
        (m for m in intent.measurements if m.role == "baseline"), None
    )
    if not baseline_m:
        raise CompositionDataError(
            "cash_flow_waterfall",
            "starting_value",
            "measurement with role='baseline'",
            "Positional fallback measurements[0] is prohibited.",
        )

    candidate["starting_value"] = baseline_m.raw_value
    starting_label = baseline_m.metric_name or baseline_m.entity_name
    if not starting_label:
        raise CompositionDataError(
            "cash_flow_waterfall",
            "starting_label",
            "baseline measurement metric_name or entity_name",
            "No placeholder 'Starting Total' allowed.",
        )
    candidate["starting_label"] = starting_label

    # Only authoritative role=delta measurements are deduction steps
    delta_ms = [m for m in intent.measurements if m.role == "delta"]
    if not delta_ms:
        raise CompositionDataError(
            "cash_flow_waterfall",
            "steps",
            "measurements with role='delta'",
            "Positional fallback measurements[1:] is prohibited.",
        )

    steps: list[dict[str, Any]] = []
    for dm in delta_ms:
        label = dm.metric_name or dm.entity_name
        if not label:
            raise CompositionDataError(
                "cash_flow_waterfall",
                "step.label",
                "deduction measurement metric_name or entity_name",
                "Every deduction step must have an explicit label.",
            )
        step: dict[str, Any] = {
            "label": label,
            "value": f"-{dm.raw_value}" if not dm.raw_value.startswith("-") else dm.raw_value,
        }
        # direction must be explicit on the measurement, not inferred
        if dm.direction in ("down", "subtract"):
            step["direction"] = "subtract"
        elif dm.direction in ("up", "add"):
            step["direction"] = "add"
        else:
            raise CompositionDataError(
                "cash_flow_waterfall",
                "step.direction",
                f"delta measurement '{label}' must have direction='down'/'subtract' or direction='up'/'add'",
                "Assuming subtract direction from position is prohibited.",
            )
        if dm.numeric_value is not None:
            step["numeric_amount"] = dm.numeric_value
        steps.append(step)

    if not steps:
        raise CompositionDataError(
            "cash_flow_waterfall",
            "steps",
            "measurements with role='delta'",
            "Cash flow waterfall requires at least one deduction step.",
        )

    candidate["steps"] = steps

    # Derive final_value only when all numeric values are authoritative
    baseline_numeric = baseline_m.numeric_value if baseline_m.numeric_value is not None else None

    all_numeric = (
        baseline_numeric is not None
        and all(s.get("numeric_amount") is not None for s in steps)
    )
    if all_numeric and steps:
        total_deductions = sum(s["numeric_amount"] for s in steps)
        final_numeric = baseline_numeric - total_deductions
        if final_numeric >= 0:
            candidate["final_value"] = f"₹{int(final_numeric):,}"

    candidate["final_label"] = "Remaining Balance"

    if intent.visual_dynamics and intent.visual_dynamics.focal_point:
        candidate["header_label"] = intent.visual_dynamics.focal_point

    candidate["variant"] = "standard"
    return candidate


# ---------------------------------------------------------------------------
# Broll Caption (Terminal Safe Fallback)
# ---------------------------------------------------------------------------

_BROLL_CAPTION_RELATIONSHIP_TYPES = frozenset({"statement", "quote", "definition", "broll"})


def is_eligible_broll_caption(intent: VisualIntent) -> bool:
    """
    broll_caption is ONLY a legitimate composition for:
    statement, quote, definition, broll.
    It is NOT a fallback for other relationship types.
    """
    return (
        intent.relationship_type in _BROLL_CAPTION_RELATIONSHIP_TYPES
        and bool(intent.what_viewer_must_understand or intent.narration_excerpt)
    )


def build_broll_caption_data(intent: VisualIntent) -> dict[str, Any]:
    caption = intent.what_viewer_must_understand or intent.narration_excerpt
    if not caption:
        raise CompositionDataError(
            "broll_caption",
            "caption",
            "intent.what_viewer_must_understand or intent.narration_excerpt",
        )

    candidate: dict[str, Any] = {
        "caption": caption,
    }

    if intent.visual_dynamics and intent.visual_dynamics.focal_point:
        candidate["emphasis_phrase"] = intent.visual_dynamics.focal_point
    elif intent.key_values:
        candidate["emphasis_phrase"] = intent.key_values[0]

    author_entity = next((e for e in intent.entities if e.role == "author" or e.category == "person"), None)
    if author_entity:
        candidate["author"] = author_entity.name

    if intent.relationship_type == "quote" or candidate.get("author"):
        candidate["variant"] = "quote"
        candidate["header_label"] = "NOTABLE PERSPECTIVE"
    elif intent.relationship_type == "statement":
        candidate["variant"] = "statement"
        candidate["header_label"] = "CORE PRINCIPLE"
    elif intent.relationship_type in ("broll", "definition"):
        candidate["variant"] = "ambient_broll"
        candidate["header_label"] = "CONTEXTUAL OVERVIEW"
    else:
        candidate["variant"] = "statement"

    source_entity = next((e for e in intent.entities if e.role in ("source", "citation", "publication")), None)
    if source_entity:
        candidate["source_context"] = source_entity.name

    if intent.causal and intent.causal.outcome_severity:
        candidate["polarity"] = intent.causal.outcome_severity.lower()

    return candidate
