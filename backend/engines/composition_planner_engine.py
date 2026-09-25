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
import re
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
from engines.composition_selector import select_composition_for_intent, CompositionSelectionError
from engines.composition_data_filler_engine import (
    CompositionDataFillerEngine,
    CompositionDataFillerError,
)
from registries.composition_builders import CompositionDataError
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
        beat_id: str | None = None,
        relationship_type: str | None = None,
        composition_id: str | None = None,
        cause: Exception | None = None,
        raw_payload: dict[str, Any] | None = None,
        provider_metadata: LLMProviderMetadata | None = None,
    ):
        super().__init__(message)
        self.beat_id = beat_id
        self.relationship_type = relationship_type
        self.composition_id = composition_id
        self.cause = cause
        self.raw_payload = raw_payload or {}
        self.provider_metadata = provider_metadata


def _is_declining_intent(intent: VisualIntent) -> bool:
    """Returns True if the intent describes a decline, erosion, or loss over time."""
    if intent.relationship_type == "decline":
        return True

    if intent.emphasis and any(
        w in intent.emphasis.lower()
        for w in ("decline", "erosion", "loss", "decay", "drop", "fall", "purchasing_power_decline", "value_erosion", "single_period_drop")
    ):
        return True

    decline_indicators = (
        "decline", "declining", "decrease", "decreasing", "erode", "erodes", "erosion",
        "decay", "loss", "loses", "losing", "drop", "drops", "deplete", "depletion",
        "fall", "falling", "shrink", "shrinking", "diminish", "halved", "downward",
        "purchasing power", "depreciation", "depreciate", "depreciates",
    )
    combined_text = f"{intent.what_viewer_must_understand} {intent.narration_excerpt}".lower()
    return any(ind in combined_text for ind in decline_indicators)


def is_valid_asset_query(query: str | None) -> bool:
    """
    Validates whether an asset query is a concrete, usable stock-search query.
    Rejects:
    - None or whitespace-only
    - Sentences / clauses containing 'viewer', 'understands', 'realizes', 'grasps', 'feels', etc.
    - Queries longer than 8 words
    - Narration sentence fragments or punctuation typical of full sentences
    """
    if not query or not isinstance(query, str):
        return False

    q = query.strip()
    if len(q) < 3:
        return False

    words = q.split()
    if len(words) > 8:
        # Full sentence or paragraph, not a search query
        return False

    q_lower = q.lower()
    # Check for conceptual/educational framing phrases
    invalid_patterns = (
        "viewer ", "viewer's", "viewers",
        "understand", "realize", "grasp", "recognize",
        "concept of", "principle of", "theory of",
        "the monthly installment", "while you are paying",
    )
    if any(pat in q_lower for pat in invalid_patterns):
        return False

    # Reject strings with punctuation typical of sentences (periods, semicolons, questions)
    if re.search(r"[.;?!]", q):
        return False

    return True


def build_fallback_asset_query(intent: VisualIntent, topic: str = "") -> str:
    """
    Deterministically builds a concrete, search-friendly stock media query (2-5 words).
    Priority:
    1. Concrete physical entities from intent.entities
    2. Contextual physical action/object matching from narration and visual intent
    3. Domain-specific grounded physical fallback

    NEVER returns narration excerpts, truncated strings, or 'viewer understands...' phrases.
    """
    # 1. Check intent.entities for concrete physical objects / roles
    concrete_entity_map: list[tuple[str, str]] = [
        ("mechanic", "mechanic repairing car"),
        ("tire", "mechanic replacing tire"),
        ("dealership", "car dealership showroom"),
        ("showroom", "car dealership showroom"),
        ("insurance", "car insurance paperwork"),
        ("loan", "car loan paperwork"),
        ("bank", "bank loan paperwork"),
        ("fuel", "driver filling fuel"),
        ("gas", "driver filling fuel"),
        ("calculator", "person calculating expenses"),
        ("budget", "person calculating expenses"),
        ("bills", "person reviewing bills"),
        ("investment", "person reviewing investments"),
        ("portfolio", "person reviewing investments"),
        ("index fund", "person reviewing investments"),
        ("driver", "driver in car"),
        ("car", "car driving on road"),
        ("vehicle", "car driving on road"),
    ]

    entity_names = [e.name.lower() for e in (intent.entities or []) if e.name]
    for ent_text in entity_names:
        for keyword, mapped_query in concrete_entity_map:
            if keyword in ent_text:
                return mapped_query

    # 2. Text keyword scanning across narration_excerpt + what_viewer_must_understand
    combined_text = f"{intent.narration_excerpt or ''} {intent.what_viewer_must_understand or ''}".lower()

    text_match_rules: list[tuple[tuple[str, ...], str]] = [
        # Repairs / Maintenance
        (("tire", "tires", "mechanic", "servicing", "service", "maintenance", "detailing", "repairs"), "mechanic changing car tire"),
        # Dealership / Showroom
        (("dealership", "showroom", "salesperson", "sales pitch", "salesman"), "car dealership showroom"),
        # Used / Pre-owned
        (("pre-owned", "used car", "second hand"), "used car showroom"),
        # Insurance / Totaled / Accidents
        (("insurance", "totaled", "accident", "stolen", "write-off"), "car insurance paperwork"),
        # Fuel / Gas / Commute
        (("fuel", "gas station", "petrol", "filling"), "driver filling car fuel"),
        # Luxury / Lifestyle creep
        (("luxury", "valet", "lifestyle creep", "premium vehicle", "sports car"), "luxury car interior"),
        # Loans / Financing / EMI / Banking
        (("loan", "emi", "bank", "interest rate", "finance manager", "financing", "installment", "down payment", "negative equity", "underwater"), "car loan paperwork"),
        # Investments / Opportunity Cost / Compounding
        (("index fund", "invest", "investment", "portfolio", "compound", "mutual fund", "stock market"), "person reviewing investments"),
        # Budget / Savings / Expenses / Cash flow
        (("budget", "expenses", "cash flow", "cannibalize", "savings", "spending", "bills"), "person calculating expenses"),
        # Commute / Driving / Highway
        (("drive to work", "drive", "driving", "traffic", "highway", "commute", "road"), "car driving on road"),
    ]

    for keywords, mapped_query in text_match_rules:
        if any(kw in combined_text for kw in keywords):
            return mapped_query

    # 3. Domain Fallback
    topic_lower = (topic or "").lower()
    if any(k in topic_lower for k in ("car", "auto", "vehicle")):
        return "car finance paperwork"
    elif any(k in topic_lower for k in ("invest", "retire", "wealth", "money", "salary", "loan")):
        return "person reviewing loan documents"

    return "person reviewing financial documents"


def _make_fallback_beat(
    intent: VisualIntent,
    beat_id: str,
    fallback_reason: str = "no_suitable_composition",
    topic: str = "",
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
        asset_query=build_fallback_asset_query(intent, topic=topic),
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
            m0 = intent.measurements[0]
            candidate["value"] = m0.raw_value
            if m0.metric_name:
                candidate["label"] = m0.metric_name
            elif m0.entity_name:
                candidate["label"] = m0.entity_name
            if m0.polarity:
                candidate["polarity"] = m0.polarity
            if m0.direction:
                candidate["direction"] = m0.direction
            baseline_m = next((m for m in intent.measurements if m.role == "baseline" and m != m0), None)
            if baseline_m:
                candidate["baseline_value"] = baseline_m.raw_value
            delta_m = next((m for m in intent.measurements if m.role == "delta"), None)
            if delta_m:
                candidate["delta"] = delta_m.raw_value
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
        # Extract by semantic role (with safe fallback across measurements)
        input_m = next((m for m in intent.measurements if m.role in ("input", "baseline")), None)
        result_m = next((m for m in intent.measurements if m.role == "result"), None)
        rate_m = next((m for m in intent.measurements if m.role in ("rate", "delta") and m != result_m), None)

        if not result_m:
            result_m = next((m for m in intent.measurements if m.role in ("impact", "delta") and m != input_m and m != rate_m), None)

        if not input_m and intent.measurements:
            input_m = intent.measurements[0]
        if not result_m and len(intent.measurements) >= 2:
            result_m = intent.measurements[-1]

        if input_m:
            candidate["input_value"] = input_m.raw_value
            if input_m.metric_name:
                candidate["input_label"] = input_m.metric_name
            elif input_m.entity_name:
                candidate["input_label"] = input_m.entity_name
        elif intent.entities:
            candidate["input_label"] = intent.entities[0].name
            candidate["input_value"] = "Starting Value"

        if not candidate.get("input_label"):
            candidate["input_label"] = "Initial Value"

        if rate_m and rate_m != input_m and rate_m != result_m:
            candidate["rate_label"] = rate_m.raw_value
            if "%" not in rate_m.raw_value:
                candidate["secondary_value"] = rate_m.raw_value
                candidate["secondary_label"] = rate_m.metric_name or rate_m.entity_name
        elif len(intent.measurements) >= 3:
            mid_m = intent.measurements[1]
            if mid_m not in (input_m, result_m):
                candidate["rate_label"] = mid_m.raw_value
                if "%" not in mid_m.raw_value:
                    candidate["secondary_value"] = mid_m.raw_value
                    candidate["secondary_label"] = mid_m.metric_name or mid_m.entity_name

        if result_m and result_m != input_m:
            candidate["result_value"] = result_m.raw_value
            if result_m.metric_name:
                candidate["result_label"] = result_m.metric_name
            elif result_m.entity_name:
                candidate["result_label"] = result_m.entity_name
            if result_m.polarity:
                candidate["polarity"] = result_m.polarity
        elif len(intent.measurements) == 1 and intent.key_values and len(intent.key_values) >= 2:
            candidate["result_value"] = intent.key_values[-1]
            candidate["result_label"] = "Result"

        if not candidate.get("result_label"):
            candidate["result_label"] = "Result"

        if intent.temporal and intent.temporal.horizon:
            candidate["timeframe"] = intent.temporal.horizon

        # Contextual operation type derivation
        combined_text = f"{intent.narration_excerpt or ''} {intent.what_viewer_must_understand or ''}".lower()
        if candidate.get("timeframe") or any(kw in combined_text for kw in ("grows to", "becomes", "growth", "compounding", "accumulated", "over time")):
            candidate["operation_type"] = "growth"
            candidate["variant"] = "growth"
        elif any(kw in combined_text for kw in ("minus", "subtract", "less", "deduction", "tax", "fee", "drag", "cut")):
            candidate["operation_type"] = "subtraction"
            candidate["variant"] = "subtraction"
        elif any(kw in combined_text for kw in ("plus", "add", "addition", "bonus", "extra", "combined")):
            candidate["operation_type"] = "addition"
            candidate["variant"] = "addition"
        elif candidate.get("rate_label") and "%" in candidate["rate_label"]:
            candidate["operation_type"] = "multiplication"
            candidate["variant"] = "multiplication"
        else:
            candidate["operation_type"] = "neutral"
            candidate["variant"] = "neutral"

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

        if intent.causal and intent.causal.mechanism:
            candidate["outcome_note"] = intent.causal.mechanism

        # Match outcome_value if available in measurements
        if intent.measurements:
            for m in intent.measurements:
                if m.role in ("result", "delta", "impact") or (candidate.get("outcome_label") and m.entity_name and m.entity_name.lower() in candidate["outcome_label"].lower()):
                    candidate["outcome_value"] = m.raw_value
                    break

        # Map variant based on number of causes
        causes_count = len(candidate.get("causes", []))
        if causes_count == 1:
            candidate["variant"] = "single_cause"
        elif causes_count == 2:
            candidate["variant"] = "dual_cause"
        elif causes_count >= 3:
            candidate["variant"] = "multi_cause"

        if candidate.get("outcome_severity"):
            candidate["polarity"] = candidate["outcome_severity"]

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

        # Match factor values from measurements if entity name matches factor label
        if candidate.get("factors") and intent.measurements:
            for item in candidate["factors"]:
                f_label = item.get("label", "").lower()
                m_match = next(
                    (
                        m
                        for m in intent.measurements
                        if (m.entity_name and m.entity_name.lower() in f_label)
                        or (m.metric_name and m.metric_name.lower() in f_label)
                    ),
                    None,
                )
                if m_match and not item.get("value"):
                    item["value"] = m_match.raw_value

        if intent.causal and intent.causal.outcome:
            candidate["combined_label"] = intent.causal.outcome

        if intent.causal and intent.causal.outcome_severity:
            sev = intent.causal.outcome_severity.lower()
            if sev in ("critical", "high", "medium"):
                candidate["combined_severity"] = sev

        if intent.causal and intent.causal.mechanism:
            candidate["outcome_note"] = intent.causal.mechanism

        # Match outcome_value from measurements with role result/delta/impact or matching combined_label
        if intent.measurements:
            res_m = next((m for m in intent.measurements if m.role in ("result", "delta", "impact")), None)
            if not res_m and candidate.get("combined_label"):
                cl = candidate["combined_label"].lower()
                res_m = next((m for m in intent.measurements if m.entity_name and m.entity_name.lower() in cl), None)
            if res_m:
                candidate["outcome_value"] = res_m.raw_value

        # Determine variant by factor count
        factor_count = len(candidate.get("factors", []))
        if factor_count == 2:
            candidate["variant"] = "dual_factor"
        elif factor_count == 3:
            candidate["variant"] = "tri_factor"
        elif factor_count >= 4:
            candidate["variant"] = "quad_factor"

        # Polarity and header label if severity exists (do NOT invent severity!)
        if candidate.get("combined_severity"):
            candidate["polarity"] = candidate["combined_severity"]
            candidate["outcome_header_label"] = f"{candidate['combined_severity'].upper()} THREAT"

    elif composition_id == "time_decay":
        # Meaning-based: baseline role vs result role
        baseline_m = next((m for m in intent.measurements if m.role in ("baseline", "input")), None)
        result_m = next((m for m in intent.measurements if m.role in ("result", "delta")), None)
        rate_m = next((m for m in intent.measurements if m.role == "rate"), None)

        if baseline_m:
            candidate["fixed_amount"] = baseline_m.raw_value
            if baseline_m.entity_name:
                candidate["amount_label"] = baseline_m.entity_name
            elif baseline_m.metric_name:
                candidate["amount_label"] = baseline_m.metric_name
        elif intent.entities:
            subj_entity = next((e for e in intent.entities if e.role == "subject"), intent.entities[0])
            candidate["amount_label"] = subj_entity.name
            candidate["fixed_amount"] = "Original Value"
        else:
            candidate["amount_label"] = "Asset Value"
            candidate["fixed_amount"] = "Original Value"

        if not candidate.get("amount_label") and intent.entities:
            candidate["amount_label"] = intent.entities[0].name

        # Temporal horizon and single-period vs recurring detection
        combined_text = f"{intent.narration_excerpt or ''} {intent.temporal.horizon if intent.temporal and intent.temporal.horizon else ''} {intent.what_viewer_must_understand or ''}".lower()
        is_single_period = any(
            kw in combined_text
            for kw in ("first year", "year 1", "year one", "initial year", "immediate", "day 1", "single year", "first-year")
        )

        if intent.temporal and intent.temporal.horizon:
            candidate["time_period"] = intent.temporal.horizon
        elif is_single_period:
            candidate["time_period"] = "First Year"
        else:
            candidate["time_period"] = "Over Time"

        if is_single_period:
            candidate["decay_type"] = "single_period"
            candidate["variant"] = "single_period_drop"
            candidate["emphasis"] = "single_period_drop"
        elif intent.temporal and intent.temporal.is_decay_over_time:
            candidate["decay_type"] = "purchasing_power"
            candidate["emphasis"] = "purchasing_power_decline"
        else:
            candidate["decay_type"] = "standard"
            candidate["emphasis"] = "value_erosion"

        if result_m:
            candidate["annotation"] = f"Erodes to {result_m.raw_value}"
            candidate["end_value"] = result_m.raw_value
            if result_m.entity_name:
                candidate["end_label"] = result_m.entity_name
            elif result_m.metric_name:
                candidate["end_label"] = result_m.metric_name
        elif intent.visual_dynamics and intent.visual_dynamics.focal_point:
            candidate["annotation"] = intent.visual_dynamics.focal_point

        if rate_m:
            candidate["rate_label"] = rate_m.raw_value
            candidate["drop_rate"] = rate_m.raw_value
        elif result_m and ("%" in result_m.raw_value):
            candidate["drop_rate"] = result_m.raw_value
            candidate["rate_label"] = result_m.raw_value
        elif any("%" in m.raw_value for m in intent.measurements):
            pct_m = next(m for m in intent.measurements if "%" in m.raw_value)
            candidate["drop_rate"] = pct_m.raw_value
            candidate["rate_label"] = pct_m.raw_value

        # Severity resolution
        if intent.visual_dynamics:
            if intent.visual_dynamics.visual_priority in ("high", "primary"):
                candidate["severity"] = "severe"
            elif intent.visual_dynamics.visual_priority in ("secondary", "context"):
                candidate["severity"] = "mild"
            elif intent.visual_dynamics.desired_visual_outcome and any(
                w in intent.visual_dynamics.desired_visual_outcome.lower()
                for w in ("rapid", "severe", "dramatic", "cliff", "catastrophic", "heavy")
            ):
                candidate["severity"] = "severe"

        if not candidate.get("severity") and candidate.get("drop_rate"):
            import re
            m = re.search(r"(\d+(?:\.\d+)?)\s*%", candidate["drop_rate"])
            if m:
                pct = float(m.group(1))
                if pct <= 20:
                    candidate["severity"] = "mild"
                elif pct >= 50:
                    candidate["severity"] = "severe"
                else:
                    candidate["severity"] = "moderate"

    elif composition_id == "growth_trajectory":
        start_m = next((m for m in intent.measurements if m.role in ("input", "baseline", "initial")), None)
        end_m = next((m for m in intent.measurements if m.role in ("result", "final", "outcome", "target")), None)
        rate_m = next((m for m in intent.measurements if m.role == "rate"), None)
        milestone_m = next((m for m in intent.measurements if m.role in ("milestone", "intermediate", "benchmark")), None)

        # Fallback between measurements if explicit roles are not annotated
        if not start_m and not end_m and not milestone_m:
            if len(intent.measurements) >= 2:
                start_m = intent.measurements[0]
                end_m = intent.measurements[-1]
            elif intent.measurements:
                m0 = intent.measurements[0]
                if m0.role == "rate":
                    rate_m = m0
                elif any(kw in (intent.narration_excerpt or "").lower() for kw in ("grows to", "reaches", "hits", "builds to", "snowball into")):
                    end_m = m0
                else:
                    start_m = m0

        if start_m:
            candidate["start_value"] = start_m.raw_value
            if start_m.metric_name:
                candidate["start_label"] = start_m.metric_name
            elif start_m.entity_name:
                candidate["start_label"] = start_m.entity_name
        elif intent.entities:
            candidate["start_label"] = intent.entities[0].name
        if "start_label" not in candidate:
            candidate["start_label"] = "Starting Point"

        if end_m and end_m != start_m:
            candidate["end_value"] = end_m.raw_value
            if end_m.metric_name:
                candidate["end_label"] = end_m.metric_name
            elif end_m.entity_name:
                candidate["end_label"] = end_m.entity_name

        if "end_label" not in candidate:
            candidate["end_label"] = "Target Corpus"

        if rate_m:
            candidate["growth_rate"] = rate_m.raw_value

        if milestone_m and milestone_m != start_m:
            candidate["milestone_value"] = milestone_m.raw_value
            if milestone_m.metric_name or milestone_m.entity_name:
                candidate["milestone_label"] = milestone_m.metric_name or milestone_m.entity_name

        if intent.temporal and intent.temporal.horizon:
            candidate["time_horizon"] = intent.temporal.horizon

        # Growth type & regime detection from narration / understanding
        combined_text = f"{intent.narration_excerpt or ''} {intent.what_viewer_must_understand or ''}".lower()
        if milestone_m or any(kw in combined_text for kw in ("milestone", "first ₹10 lakh", "first 10 lakh", "tipping point", "stepping stone")):
            candidate["growth_type"] = "accelerating" if any(kw in combined_text for kw in ("accelerat", "compound", "snowball")) else "linear"
            candidate["variant"] = "milestone_progression"
        elif any(kw in combined_text for kw in ("snowball", "exponential", "compounding", "compound", "returns generate", "reinvest")):
            candidate["growth_type"] = "compound"
            candidate["variant"] = "compounding_snowball"
        elif any(kw in combined_text for kw in ("accelerat", "speed up", "faster", "builds faster", "pace pick")):
            candidate["growth_type"] = "accelerating"
            candidate["variant"] = "accelerating_growth"
        elif any(kw in combined_text for kw in ("linear", "steady", "incremental", "monthly savings", "predictable amount")):
            candidate["growth_type"] = "linear"
            candidate["variant"] = "linear_accumulation"
        else:
            candidate["growth_type"] = "unspecified"
            candidate["variant"] = "standard"

        if intent.visual_dynamics and intent.visual_dynamics.focal_point:
            candidate["annotation"] = intent.visual_dynamics.focal_point
        elif any(kw in combined_text for kw in ("inflection", "snowball", "accelerat", "transition")):
            candidate["annotation"] = intent.what_viewer_must_understand

    elif composition_id == "trajectory_divergence":
        # Extract time horizon from temporal context
        if intent.temporal and intent.temporal.horizon:
            candidate["time_horizon"] = intent.temporal.horizon
        elif intent.temporal and intent.temporal.start_point and intent.temporal.end_point:
            candidate["time_horizon"] = f"{intent.temporal.start_point} → {intent.temporal.end_point}"
        else:
            candidate["time_horizon"] = "Over Time"

        # Baseline: use comparison dimension if available, else narration-derived
        if intent.comparison and intent.comparison.comparison_dimension:
            candidate["baseline_label"] = intent.comparison.comparison_dimension
        elif intent.entities:
            candidate["baseline_label"] = intent.entities[0].name
        else:
            candidate["baseline_label"] = "Common Starting Point"

        # Path A: from comparison.subject_a + value_a
        path_a: dict[str, Any] = {}
        if intent.comparison and intent.comparison.subject_a:
            path_a["label"] = intent.comparison.subject_a
        elif intent.entities and len(intent.entities) >= 1:
            path_a["label"] = intent.entities[0].name
        else:
            path_a["label"] = "Path A"

        if intent.comparison and intent.comparison.value_a:
            path_a["end_value"] = intent.comparison.value_a

        # Direction/tone inference
        path_a_text = (path_a.get("label") or "").lower()
        if any(kw in path_a_text for kw in ("invest", "sip", "equity", "mutual", "fund", "portfolio", "wealth")):
            path_a["direction"] = "up"
            path_a["tone"] = "positive"

        # Rate from measurements (first rate measurement assigned to path_a if not declining)
        rate_ms = [m for m in intent.measurements if m.role == "rate"]
        if rate_ms:
            path_a["rate"] = rate_ms[0].raw_value

        candidate["path_a"] = path_a

        # Path B: from comparison.subject_b + value_b
        path_b: dict[str, Any] = {}
        if intent.comparison and intent.comparison.subject_b:
            path_b["label"] = intent.comparison.subject_b
        elif intent.entities and len(intent.entities) >= 2:
            path_b["label"] = intent.entities[1].name
        else:
            path_b["label"] = "Path B"

        if intent.comparison and intent.comparison.value_b:
            path_b["end_value"] = intent.comparison.value_b

        path_b_text = (path_b.get("label") or "").lower()
        if any(kw in path_b_text for kw in ("emi", "debt", "loan", "depreciat", "spend", "car", "expense")):
            path_b["direction"] = "down"
            path_b["tone"] = "negative"

        candidate["path_b"] = path_b

        # Divergence gap: from comparison.delta or delta measurement
        if intent.comparison and intent.comparison.delta:
            candidate["divergence_gap"] = intent.comparison.delta
        else:
            delta_m = next((m for m in intent.measurements if m.role == "delta"), None)
            if delta_m:
                candidate["divergence_gap"] = delta_m.raw_value

        # Header from visual_dynamics focal_point
        if intent.visual_dynamics and intent.visual_dynamics.focal_point:
            candidate["header_label"] = intent.visual_dynamics.focal_point

        # Variant selection
        narration_lower = (intent.narration_excerpt or "").lower() + " " + (intent.what_viewer_must_understand or "").lower()
        if any(kw in narration_lower for kw in ("wealth gap", "wealth accumulation gap", "₹ gap")):
            candidate["variant"] = "wealth_gap"
        elif any(kw in narration_lower for kw in ("opportunity cost", "cost of", "foregone")):
            candidate["variant"] = "cost_opportunity"
        else:
            candidate["variant"] = "divergence"

    elif composition_id == "cash_flow_waterfall":
        # Starting value: baseline measurement
        baseline_m = next((m for m in intent.measurements if m.role == "baseline"), None)
        if baseline_m:
            candidate["starting_value"] = baseline_m.raw_value
            if baseline_m.metric_name:
                candidate["starting_label"] = baseline_m.metric_name
            elif baseline_m.entity_name:
                candidate["starting_label"] = baseline_m.entity_name
            else:
                candidate["starting_label"] = "Starting Total"
        elif intent.measurements:
            candidate["starting_value"] = intent.measurements[0].raw_value
            candidate["starting_label"] = intent.measurements[0].metric_name or "Starting Total"

        # Steps: from delta measurements (deductions)
        delta_ms = [m for m in intent.measurements if m.role == "delta"]
        steps: list[dict[str, Any]] = []
        for dm in delta_ms:
            step: dict[str, Any] = {
                "label": dm.metric_name or dm.entity_name or "Deduction",
                "value": f"-{dm.raw_value}" if not dm.raw_value.startswith("-") else dm.raw_value,
                "direction": "subtract",
            }
            if dm.numeric_value is not None:
                step["numeric_amount"] = dm.numeric_value
            steps.append(step)
        if steps:
            candidate["steps"] = steps

        # Deterministic final value: only if all numeric amounts are present
        baseline_numeric = baseline_m.numeric_value if baseline_m and baseline_m.numeric_value is not None else None
        all_numeric = (
            baseline_numeric is not None
            and all(s.get("numeric_amount") is not None for s in steps)
        )
        if all_numeric and steps:
            total_deductions = sum(s["numeric_amount"] for s in steps)
            final_numeric = baseline_numeric - total_deductions
            # Format with commas (Indian numbering style approximation)
            if final_numeric >= 0:
                candidate["final_value"] = f"₹{int(final_numeric):,}"
            # Don't set final_value for negative result (would be meaningless)

        # Always set default final_label
        candidate["final_label"] = "Remaining Balance"

        # Header from visual_dynamics
        if intent.visual_dynamics and intent.visual_dynamics.focal_point:
            candidate["header_label"] = intent.visual_dynamics.focal_point


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

        # Variant selection based on relationship type and signals
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

        # Check for citation/source entity for quote/statement context
        source_entity = next((e for e in intent.entities if e.role in ("source", "citation", "publication")), None)
        if source_entity:
            candidate["source_context"] = source_entity.name

        # Polarity from causal severity
        if intent.causal and intent.causal.outcome_severity:
            candidate["polarity"] = intent.causal.outcome_severity.lower()

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
        for k in ("polarity", "direction", "baseline_value", "delta"):
            if k in candidate_facts and candidate_facts[k] is not None:
                result[k] = candidate_facts[k]

    elif composition_id == "calculation_story":
        if "input_value" in candidate_facts:
            result["input_value"] = candidate_facts["input_value"]
        if "result_value" in candidate_facts:
            result["result_value"] = candidate_facts["result_value"]

        if "rate_label" in candidate_facts and candidate_facts["rate_label"]:
            cand_rate = candidate_facts["rate_label"]
            llm_rate = result.get("rate_label", "")
            if not llm_rate or cand_rate not in llm_rate:
                result["rate_label"] = cand_rate

        if "input_label" in candidate_facts and not result.get("input_label"):
            result["input_label"] = candidate_facts["input_label"]
        if "result_label" in candidate_facts and not result.get("result_label"):
            result["result_label"] = candidate_facts["result_label"]
        if "note" in candidate_facts and not result.get("note"):
            result["note"] = candidate_facts["note"]
        if "operation_label" in candidate_facts and not result.get("operation_label"):
            result["operation_label"] = candidate_facts["operation_label"]
        if "operation_type" in candidate_facts and not result.get("operation_type"):
            result["operation_type"] = candidate_facts["operation_type"]
        if "variant" in candidate_facts and not result.get("variant"):
            result["variant"] = candidate_facts["variant"]
        for k in ("polarity", "timeframe", "secondary_label", "secondary_value"):
            if k in candidate_facts and candidate_facts[k] is not None and not result.get(k):
                result[k] = candidate_facts[k]

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
        for key in ("header_label", "variant", "tone"):
            if key in candidate_facts and not result.get(key):
                result[key] = candidate_facts[key]

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

        if "outcome_value" in candidate_facts and not result.get("outcome_value"):
            result["outcome_value"] = candidate_facts["outcome_value"]

        if "outcome_header_label" in candidate_facts and not result.get("outcome_header_label"):
            result["outcome_header_label"] = candidate_facts["outcome_header_label"]

        if "outcome_note" in candidate_facts and not result.get("outcome_note"):
            result["outcome_note"] = candidate_facts["outcome_note"]

        if "variant" in candidate_facts and not result.get("variant"):
            result["variant"] = candidate_facts["variant"]

        if "polarity" in candidate_facts and not result.get("polarity"):
            result["polarity"] = candidate_facts["polarity"]

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
                    if llm_factors[i].get("icon"):
                        item["icon"] = llm_factors[i]["icon"]
                merged_factors.append(item)
            result["factors"] = merged_factors

        if "combined_label" in candidate_facts and not result.get("combined_label"):
            result["combined_label"] = candidate_facts["combined_label"]

        if "combined_severity" in candidate_facts and not result.get("combined_severity"):
            result["combined_severity"] = candidate_facts["combined_severity"]

        if "outcome_note" in candidate_facts and not result.get("outcome_note"):
            result["outcome_note"] = candidate_facts["outcome_note"]

        for key in ("outcome_value", "outcome_header_label", "variant", "polarity"):
            if key in candidate_facts and not result.get(key):
                result[key] = candidate_facts[key]

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
        for key in ("end_value", "end_label", "drop_rate", "severity", "rate_label", "variant", "decay_type"):
            if key in candidate_facts and not result.get(key):
                result[key] = candidate_facts[key]

    elif composition_id == "growth_trajectory":
        for key in ("start_value", "end_value", "growth_rate", "milestone_value"):
            if key in candidate_facts and candidate_facts[key] is not None:
                result[key] = candidate_facts[key]
        for key in ("start_label", "end_label", "time_horizon", "growth_type", "milestone_label", "annotation", "header_label", "variant"):
            if key in candidate_facts and candidate_facts[key] is not None and not result.get(key):
                result[key] = candidate_facts[key]

    elif composition_id == "trajectory_divergence":
        # Lock factual horizon and gap — these are numerical/factual
        for key in ("time_horizon", "divergence_gap", "baseline_label"):
            if key in candidate_facts and candidate_facts[key] is not None:
                result[key] = candidate_facts[key]

        # Path A: lock numeric end_value/start_value/rate; allow label/direction/tone to be refined
        if "path_a" in candidate_facts and candidate_facts["path_a"]:
            merged_path_a = dict(result.get("path_a") or {})
            fact_path_a = candidate_facts["path_a"]
            llm_path_a = (llm_data.get("path_a") or {})
            for locked in ("end_value", "start_value", "rate"):
                if fact_path_a.get(locked) is not None:
                    merged_path_a[locked] = fact_path_a[locked]
            for presentation in ("label", "direction", "tone"):
                if not merged_path_a.get(presentation):
                    merged_path_a[presentation] = llm_path_a.get(presentation) or fact_path_a.get(presentation)
                elif llm_path_a.get(presentation):
                    merged_path_a[presentation] = llm_path_a[presentation]
            result["path_a"] = merged_path_a

        # Path B: same merge logic
        if "path_b" in candidate_facts and candidate_facts["path_b"]:
            merged_path_b = dict(result.get("path_b") or {})
            fact_path_b = candidate_facts["path_b"]
            llm_path_b = (llm_data.get("path_b") or {})
            for locked in ("end_value", "start_value", "rate"):
                if fact_path_b.get(locked) is not None:
                    merged_path_b[locked] = fact_path_b[locked]
            for presentation in ("label", "direction", "tone"):
                if not merged_path_b.get(presentation):
                    merged_path_b[presentation] = llm_path_b.get(presentation) or fact_path_b.get(presentation)
                elif llm_path_b.get(presentation):
                    merged_path_b[presentation] = llm_path_b[presentation]
            result["path_b"] = merged_path_b

        # Presentation-only fields
        for key in ("header_label", "variant"):
            if key in candidate_facts and candidate_facts[key] is not None and not result.get(key):
                result[key] = candidate_facts[key]

    elif composition_id == "cash_flow_waterfall":
        # Lock factual numeric values — LLM must not overwrite these
        for key in ("starting_value", "final_value"):
            if key in candidate_facts and candidate_facts[key] is not None:
                result[key] = candidate_facts[key]

        # Starting label: use candidate but allow LLM refinement
        if "starting_label" in candidate_facts and candidate_facts["starting_label"]:
            result.setdefault("starting_label", candidate_facts["starting_label"])

        # Steps: lock value/direction from candidate; allow LLM to add subtext only
        if "steps" in candidate_facts and candidate_facts["steps"]:
            llm_steps = llm_data.get("steps") or []
            merged_steps = []
            for i, fact_step in enumerate(candidate_facts["steps"]):
                merged_step = dict(fact_step)  # start with factual data
                if i < len(llm_steps):
                    llm_step = llm_steps[i] if isinstance(llm_steps[i], dict) else {}
                    if llm_step.get("subtext"):
                        merged_step["subtext"] = llm_step["subtext"]
                merged_steps.append(merged_step)
            result["steps"] = merged_steps

        # Presentation-only: final_label can be refined by LLM; header/variant are supplementary
        for key in ("final_label", "header_label", "variant"):
            if key in candidate_facts and candidate_facts[key] is not None and not result.get(key):
                result[key] = candidate_facts[key]

    elif composition_id == "ranked_list":
        if "items" in candidate_facts and candidate_facts["items"]:
            result["items"] = candidate_facts["items"]
        if "header_label" in candidate_facts and not result.get("header_label"):
            result["header_label"] = candidate_facts["header_label"]
        for key in ("variant", "footer_label"):
            if key in candidate_facts and not result.get(key):
                result[key] = candidate_facts[key]

    elif composition_id == "process_flow":
        if "steps" in candidate_facts and candidate_facts["steps"]:
            result["steps"] = candidate_facts["steps"]
        if "header_label" in candidate_facts and not result.get("header_label"):
            result["header_label"] = candidate_facts["header_label"]
        for key in ("variant", "layout", "footer_label"):
            if key in candidate_facts and not result.get(key):
                result[key] = candidate_facts[key]

    elif composition_id == "broll_caption":
        if "caption" in candidate_facts and not result.get("caption"):
            result["caption"] = candidate_facts["caption"]
        if "emphasis_phrase" in candidate_facts and not result.get("emphasis_phrase"):
            result["emphasis_phrase"] = candidate_facts["emphasis_phrase"]
        if "author" in candidate_facts and not result.get("author"):
            result["author"] = candidate_facts["author"]
        for key in ("header_label", "variant", "source_context", "polarity"):
            if key in candidate_facts and not result.get(key):
                result[key] = candidate_facts[key]

    return result


class CompositionPlannerEngine:
    """
    Selects and validates a composition for one VisualIntent.

    Deterministic selector plus schema-scoped composition data filler.

    Selection remains pure Python. The filler receives only the selected
    composition schema and the persisted VisualIntent; missing or ungrounded
    data fails the stage instead of falling back.
    """

    def __init__(
        self,
        llm_provider: LLMProvider | None = None,
        filler_engine: CompositionDataFillerEngine | None = None,
    ):
        self.llm_provider = llm_provider
        self.filler_engine = filler_engine or CompositionDataFillerEngine(llm_provider)

    def run(
        self,
        *,
        intent: VisualIntent,
        beat_id: str,
        topic: str = "",
        audience: str = "",
        source_idea_id: str | None = None,
        source_visual_intent_artifact_id: str | None = None,
    ) -> CompositionPlannerResult:
        """
        Selects a composition deterministically, then fills its exact schema
        from the source VisualIntent. Unlinked calls retain the old
        deterministic builder for compatibility with legacy callers; persisted
        composition plans always pass source IDs and therefore require the
        schema-scoped filler.
        Fail-fast: raises CompositionPlannerEngineError on any ambiguity, missing data, or validation failure.
        """
        # 1. Deterministic Selection
        try:
            selected_id = select_composition_for_intent(intent)
        except CompositionSelectionError as exc:
            raise CompositionPlannerEngineError(
                f"Failed selecting composition: {exc}",
                beat_id=beat_id,
                relationship_type=intent.relationship_type,
                cause=exc,
            ) from exc

        # 2. Registry Lookup
        defn = CompositionRegistry.get(selected_id)
        if defn is None:
            raise CompositionPlannerEngineError(
                f"No definition registered for composition '{selected_id}'.",
                beat_id=beat_id,
                relationship_type=intent.relationship_type,
                composition_id=selected_id,
            )

        # 3. Eligibility Guard Check
        if defn.is_eligible is not None and not defn.is_eligible(intent):
            raise CompositionPlannerEngineError(
                f"VisualIntent is not eligible for composition '{selected_id}'.",
                beat_id=beat_id,
                relationship_type=intent.relationship_type,
                composition_id=selected_id,
            )

        # 4. New persisted path: the exact source IDs opt into LLM #2. The
        # old builder remains only for callers that have not yet adopted the
        # persisted VisualIntent contract.
        if source_idea_id is not None or source_visual_intent_artifact_id is not None:
            if source_idea_id is None or source_visual_intent_artifact_id is None:
                raise CompositionPlannerEngineError(
                    "Persisted composition planning requires both source_idea_id and "
                    "source_visual_intent_artifact_id.",
                    beat_id=beat_id,
                    relationship_type=intent.relationship_type,
                    composition_id=selected_id,
                )
            try:
                filled = self.filler_engine.fill(
                    intent=intent,
                    composition=defn,
                    source_artifact_id=source_visual_intent_artifact_id,
                    source_idea_id=source_idea_id,
                )
            except CompositionDataFillerError as exc:
                raise CompositionPlannerEngineError(
                    f"Failed filling data for composition '{selected_id}': {exc}",
                    beat_id=beat_id,
                    relationship_type=intent.relationship_type,
                    composition_id=selected_id,
                    cause=exc,
                ) from exc
            validated_data = filled.composition_data
            provider_metadata = filled.provider_metadata
            raw_payload = filled.raw_payload
        else:
            if defn.builder is None:
                raise CompositionPlannerEngineError(
                    f"No filler or legacy builder registered for composition '{selected_id}'.",
                    beat_id=beat_id,
                    relationship_type=intent.relationship_type,
                    composition_id=selected_id,
                )
            try:
                candidate_data = defn.builder(intent)
            except CompositionDataError as exc:
                raise CompositionPlannerEngineError(
                    f"Failed building data for composition '{selected_id}': {exc}",
                    beat_id=beat_id,
                    relationship_type=intent.relationship_type,
                    composition_id=selected_id,
                    cause=exc,
                ) from exc
            except Exception as exc:
                raise CompositionPlannerEngineError(
                    f"Unexpected builder error for composition '{selected_id}': {exc}",
                    beat_id=beat_id,
                    relationship_type=intent.relationship_type,
                    composition_id=selected_id,
                    cause=exc,
                ) from exc
            is_valid, errors, validated_data = CompositionRegistry.validate_composition_data(
                selected_id, candidate_data, visual_goal=intent.what_viewer_must_understand
            )
            if not is_valid:
                raise CompositionPlannerEngineError(
                    f"Validation failed for composition '{selected_id}': {'; '.join(errors)}",
                    beat_id=beat_id,
                    relationship_type=intent.relationship_type,
                    composition_id=selected_id,
                    raw_payload=candidate_data,
                )
            provider_metadata = LLMProviderMetadata(provider="deterministic_python", model="legacy_builder_v1")
            raw_payload = validated_data

        # 6. Variant Verification
        variant = validated_data.get("variant")
        if variant is not None and defn.allowed_variants and variant not in defn.allowed_variants:
            variant = None

        # 7. Asset Query & Asset Requirement
        if selected_id == "broll_caption":
            asset_requirement = "optional_broll"
            asset_query = build_fallback_asset_query(intent, topic=topic)
        else:
            asset_requirement = defn.asset_requirement.value
            asset_query = None

        # 8. Construct Beat (Fail-fast deterministic path never uses fallback)
        beat = CompositionBeat(
            beat_id=beat_id,
            source_intent_id=intent.intent_id if source_idea_id is not None else None,
            source_idea_id=source_idea_id,
            source_visual_intent_artifact_id=source_visual_intent_artifact_id,
            source_narration_excerpt=intent.narration_excerpt,
            composition_id=selected_id,
            variant=variant,
            composition_data=validated_data,
            asset_requirement=asset_requirement,
            asset_query=asset_query,
            trigger_word=intent.trigger_word,
            visual_goal=intent.what_viewer_must_understand,
            relationship_type=intent.relationship_type,
            used_fallback=False,
            fallback_reason=None,
        )

        return CompositionPlannerResult(
            beat=beat,
            provider_metadata=provider_metadata,
            raw_payload=raw_payload,
            used_fallback=False,
            fallback_reason=None,
        )

    def _run_legacy_llm(
        self,
        *,
        intent: VisualIntent,
        beat_id: str,
        topic: str = "",
        audience: str = "",
    ) -> CompositionPlannerResult:
        """
        [DEPRECATED / TEMPORARY]
        Preserved legacy LLM execution path solely for transitional test verification.
        Will be removed in Phase 11.
        """
        if self.llm_provider is None:
            fallback = _make_fallback_beat(intent, beat_id, fallback_reason="no_llm_provider", topic=topic)
            return CompositionPlannerResult(
                beat=fallback,
                provider_metadata=LLMProviderMetadata(provider="fallback", model="fallback"),
                raw_payload={"error": "no_llm_provider"},
                used_fallback=True,
                fallback_reason="no_llm_provider",
            )

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
            temperature=0.1,
            max_tokens=1500,
        )

        try:
            response = self.llm_provider.generate_json(llm_request)
        except LLMProviderError as error:
            fallback_reason = f"provider_error: {error}"
            fallback = _make_fallback_beat(intent, beat_id, fallback_reason=fallback_reason, topic=topic)
            return CompositionPlannerResult(
                beat=fallback,
                provider_metadata=LLMProviderMetadata(provider="fallback", model="fallback"),
                raw_payload={"error": str(error)},
                used_fallback=True,
                fallback_reason=fallback_reason,
            )

        raw = response.payload
        status = raw.get("status", "")

        if status == "no_suitable_composition":
            reason = raw.get("reason", "No suitable composition declared by LLM")
            fallback_reason = f"no_suitable_composition: {reason}"
            fallback = _make_fallback_beat(intent, beat_id, fallback_reason=fallback_reason, topic=topic)
            return CompositionPlannerResult(
                beat=fallback,
                provider_metadata=response.metadata,
                raw_payload=raw,
                used_fallback=True,
                fallback_reason=fallback_reason,
            )

        composition_id = raw.get("composition_id", "")
        if not CompositionRegistry.is_registered(composition_id):
            fallback_reason = f"unknown_composition_id: '{composition_id}' is not registered"
            fallback = _make_fallback_beat(intent, beat_id, fallback_reason=fallback_reason, topic=topic)
            return CompositionPlannerResult(
                beat=fallback,
                provider_metadata=response.metadata,
                raw_payload=raw,
                used_fallback=True,
                fallback_reason=fallback_reason,
            )

        defn = CompositionRegistry.get(composition_id)
        assert defn is not None

        if intent.relationship_type not in defn.supported_relationship_types:
            fallback_reason = (
                f"unsupported_relationship_type: '{composition_id}' does not support '{intent.relationship_type}'"
            )
            fallback = _make_fallback_beat(intent, beat_id, fallback_reason=fallback_reason, topic=topic)
            return CompositionPlannerResult(
                beat=fallback,
                provider_metadata=response.metadata,
                raw_payload=raw,
                used_fallback=True,
                fallback_reason=fallback_reason,
            )

        if composition_id == "time_decay" and intent.relationship_type == "trend" and not _is_declining_intent(intent):
            fallback_reason = "time_decay rejected: trend does not indicate decline or erosion"
            fallback = _make_fallback_beat(intent, beat_id, fallback_reason=fallback_reason, topic=topic)
            return CompositionPlannerResult(
                beat=fallback,
                provider_metadata=response.metadata,
                raw_payload=raw,
                used_fallback=True,
                fallback_reason=fallback_reason,
            )

        variant = raw.get("variant")
        if variant is not None and defn.allowed_variants and variant not in defn.allowed_variants:
            variant = None

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
            fallback_reason = f"validation_error: {'; '.join(errors)}"
            fallback = _make_fallback_beat(intent, beat_id, fallback_reason=fallback_reason, topic=topic)
            return CompositionPlannerResult(
                beat=fallback,
                provider_metadata=response.metadata,
                raw_payload=raw,
                used_fallback=True,
                fallback_reason=fallback_reason,
            )

        raw_asset_query = raw.get("asset_query")
        if composition_id == "broll_caption":
            if is_valid_asset_query(raw_asset_query):
                asset_query = raw_asset_query.strip()
            else:
                asset_query = build_fallback_asset_query(intent, topic=topic)
            asset_requirement = "optional_broll"
        else:
            asset_query = None
            asset_requirement = "none"

        beat = CompositionBeat(
            beat_id=beat_id,
            composition_id=composition_id,
            variant=variant,
            composition_data=normalized_data,
            asset_requirement=asset_requirement,
            asset_query=asset_query,
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
