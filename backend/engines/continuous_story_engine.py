from __future__ import annotations

from dataclasses import dataclass
import json
import re
from typing import Any

from app.assets import load_prompt
from domain.continuous_story_plan import (
    ContinuousStoryDraft,
    ContinuousStoryPlanArtifact,
    VALID_CHART_TYPES,
    VALID_VISUAL_STATES,
    VALID_ZONES,
)
from domain.research_packet import ResearchPacket
from domain.script_visual_strategy import ScriptVisualStrategy
from domain.voice_track import VoiceTrack
from engines.continuous_story_compiler import ContinuousStoryCompiler, resolve_anchor_frame
from engines.continuous_story_draft_validator import validate_story_draft
from pydantic import ValidationError
from providers.llm_provider import (
    LLMJsonRequest,
    LLMMessage,
    LLMProvider,
    LLMProviderMetadata,
)

_MONEY_RE = re.compile(
    r"(?<![A-Za-z])(?:₹|rs(?:\.)?|inr)\s*(\d[\d,]*(?:\.\d+)?)\s*(lakh|lakhs|crore|crores)?",
    re.IGNORECASE,
)
_PERCENT_RE = re.compile(r"([\d]+(?:\.\d+)?)\s*%")
_BPS_RE = re.compile(r"([\d]+(?:\.\d+)?)\s*(?:basis\s*points?|bps\b)", re.IGNORECASE)


@dataclass(frozen=True)
class ContinuousStoryEngineResult:
    artifact: ContinuousStoryPlanArtifact
    draft: ContinuousStoryDraft
    raw_payload: dict[str, Any]
    provider_metadata: LLMProviderMetadata | None = None


class ContinuousStoryEngineError(Exception):
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


def _format_inr(val: float | int) -> str:
    """Formats a numeric value as an Indian Rupee string (e.g. ₹50,00,000)."""
    val_int = int(round(val))
    s = str(val_int)
    if len(s) <= 3:
        return f"₹{s}"
    last3 = s[-3:]
    rest = s[:-3]
    parts = []
    while len(rest) > 2:
        parts.insert(0, rest[-2:])
        rest = rest[:-2]
    if rest:
        parts.insert(0, rest)
    return "₹" + ",".join(parts) + "," + last3


def _get_clause_for_match(source: str, start: int, end: int) -> str:
    """Isolates the phrase or clause around a regex match to prevent context bleed."""
    delims = [",", ";", ".", " - ", "—", "\n"]
    clause_start = 0
    for d in delims:
        idx = source[:start].rfind(d)
        if idx != -1 and idx + len(d) > clause_start:
            clause_start = idx + len(d)
    clause_end = len(source)
    for d in delims:
        idx = source[end:].find(d)
        if idx != -1 and (end + idx) < clause_end:
            clause_end = end + idx
    clause = source[clause_start:clause_end].strip()
    if len(clause) < 20:
        clause = source[max(0, start - 50):min(len(source), end + 50)]
    return clause


def _infer_semantic_meaning(clause: str, val: float, kind: str) -> tuple[str, list[str]]:
    """Infers factual meaning and allowed narrative roles from surrounding clause text."""
    c = clause.lower()
    if kind == "money":
        if any(w in c for w in ["pure interest", "interest alone", "in interest", "interest outgo", "interest payment", "interest payments"]):
            return "total lifetime interest outgo", ["card_value", "final_consequence", "transform_target"]
        if any(w in c for w in ["total amount paid", "total payment", "total payments", "total paid", "entire tenure", "lifetime outgo"]):
            return "total loan repayment over 30 years", ["card_value", "final_consequence", "transform_target"]
        if any(w in c for w in ["saving", "savings", "saves", "slashes"]):
            return "lifetime interest savings via prepayment", ["card_value", "solution_payoff"]
        if any(w in c for w in ["loan", "principal", "borrower"]) or (val >= 500000 and "loan" in c):
            return "home loan principal amount", ["card_value", "comparison_baseline", "baseline_hero"]
        if any(w in c for w in ["emi", "monthly"]):
            return "standard monthly EMI payment", ["card_value", "operational_metric"]
        return f"monetary fact ({_format_inr(val)})", ["card_value"]
    elif kind == "percent":
        if any(w in c for w in ["interest rate", "rate of", "loan at"]):
            return "annual interest rate", ["card_value", "context_metric"]
        if any(w in c for w in ["bank interest", "toward interest", "servicing the interest", "initial emi", "early"]):
            return "share of initial EMI going toward interest", ["card_value", "mechanism_warning"]
        return f"percentage metric ({val}%)", ["card_value"]
    elif kind == "bps":
        return f"{val} bps rate shift", ["card_value", "context_metric"]
    return "numeric fact", ["card_value"]


def _numeric_facts_from_research(research_packet: ResearchPacket) -> dict[str, Any]:
    """Promote explicit numeric evidence into typed compiler facts with semantic grounding."""
    facts: dict[str, Any] = {}
    seen_semantic_keys: set[tuple[Any, str, str]] = set()
    counter = 1

    sources = [
        *research_packet.verified_facts,
        *research_packet.statistics,
        *research_packet.examples,
    ]

    for source in sources:
        for match in _MONEY_RE.finditer(source):
            raw_val = float(match.group(1).replace(",", ""))
            unit = (match.group(2) or "").lower()
            if unit.startswith("lakh"):
                raw_val *= 100_000
            elif unit.startswith("crore"):
                raw_val *= 10_000_000
            value = int(raw_val) if raw_val.is_integer() else raw_val

            clause = _get_clause_for_match(source, match.start(), match.end())
            meaning, allowed_use = _infer_semantic_meaning(clause, value, "money")
            sem_key = (value, "currency_inr", meaning)
            if sem_key in seen_semantic_keys:
                continue
            seen_semantic_keys.add(sem_key)

            display = _format_inr(value)
            facts[f"research_money_{counter}"] = {
                "value": value,
                "format": "currency_inr",
                "meaning": meaning,
                "display": display,
                "allowed_use": allowed_use,
                "label": meaning,
                "subtitle": clause[:120],
                "provenance": {"formula": "research_grounded", "source": source},
            }
            counter += 1

        for match in _PERCENT_RE.finditer(source):
            value = float(match.group(1))
            value = int(value) if value.is_integer() else value

            clause = _get_clause_for_match(source, match.start(), match.end())
            meaning, allowed_use = _infer_semantic_meaning(clause, value, "percent")
            sem_key = (value, "percentage", meaning)
            if sem_key in seen_semantic_keys:
                continue
            seen_semantic_keys.add(sem_key)

            display = f"{value}%"
            facts[f"research_percent_{counter}"] = {
                "value": value,
                "format": "percentage",
                "meaning": meaning,
                "display": display,
                "allowed_use": allowed_use,
                "label": meaning,
                "subtitle": clause[:120],
                "provenance": {"formula": "research_grounded", "source": source},
            }
            counter += 1

        for match in _BPS_RE.finditer(source):
            value = float(match.group(1))
            value = int(value) if value.is_integer() else value

            clause = _get_clause_for_match(source, match.start(), match.end())
            meaning, allowed_use = _infer_semantic_meaning(clause, value, "bps")
            sem_key = (value, "basis_points", meaning)
            if sem_key in seen_semantic_keys:
                continue
            seen_semantic_keys.add(sem_key)

            display = f"{value} bps"
            facts[f"research_bps_{counter}"] = {
                "value": value,
                "format": "basis_points",
                "meaning": meaning,
                "display": display,
                "allowed_use": allowed_use,
                "label": meaning,
                "subtitle": clause[:120],
                "provenance": {"formula": "research_grounded", "source": source},
            }
            counter += 1

    if not facts:
        num_re = re.compile(r"\b(\d[\d,]*(?:\.\d+)?)\b")
        for source in sources:
            for match in num_re.finditer(source):
                val_str = match.group(1).replace(",", "")
                try:
                    val = float(val_str)
                    if val <= 0:
                        continue
                    val = int(val) if val.is_integer() else val
                    facts[f"research_num_{counter}"] = {
                        "value": val,
                        "format": "plain",
                        "meaning": f"numeric fact ({val})",
                        "display": str(val),
                        "allowed_use": ["card_value"],
                        "label": f"numeric fact ({val})",
                        "subtitle": source[:120],
                        "provenance": {"formula": "research_grounded", "source": source},
                    }
                    counter += 1
                except ValueError:
                    continue

    return facts


def _normalize_zone(val: Any, default: str = "center") -> str:
    """Safely normalizes arbitrary layout inputs into one of the 12 strict ZoneNames."""
    if isinstance(val, str) and val in VALID_ZONES:
        return val
    if isinstance(val, str):
        aliases = {
            "left": "center_left",
            "right": "center_right",
            "top": "top_center",
            "bottom": "bottom_center",
        }
        if val in aliases:
            return aliases[val]
    if isinstance(val, dict):
        if "right_of" in val:
            return "center_right"
        if "left_of" in val:
            return "center_left"
        if "below" in val:
            return "bottom_center"
        if "above" in val:
            return "top_center"
    return default


def _safe_contract_repair(payload: dict[str, Any]) -> dict[str, Any]:
    """Deprecated fallback: silent deletion or alteration of objects is forbidden by system policy.

    The AI may make a mistake, but the system must never hide or reinterpret that mistake.
    Contract errors must fail loudly, preserving the invalid payload.
    """
    raise ContinuousStoryEngineError(
        "CONTINUOUS_STORY_CONTRACT_ERROR: Silent repair fallback is disabled by policy. Contract errors must fail loudly.",
        raw_payload=payload,
    )


def _safe_temporal_repair(
    draft: ContinuousStoryDraft,
    word_timestamps: list[dict[str, Any]],
) -> ContinuousStoryDraft:
    """Deprecated fallback: silent re-anchoring of events is forbidden by system policy.

    Causality and temporal errors must fail loudly to preserve editorial integrity.
    """
    raise ContinuousStoryEngineError(
        "CONTINUOUS_STORY_VALIDATION_ERROR: Silent temporal repair fallback is disabled by policy. Pacing errors must fail loudly.",
        raw_payload=draft.model_dump() if hasattr(draft, "model_dump") else {},
    )


def print_local_preflight_report(
    raw_payload: dict[str, Any],
    validation_error: Exception | None = None,
    draft_errors: list[Any] | None = None,
) -> None:
    """Prints a clear, localized preflight summary of objects, events, and validation issues."""
    num_objects = len(raw_payload.get("objects", []))
    num_events = len(raw_payload.get("events", []))
    print("\n--- CONTINUOUS STORY PREFLIGHT REPORT ---")
    print(f"Objects: {num_objects}")
    print(f"Events:  {num_events}")

    invalid_items: list[str] = []
    if isinstance(validation_error, ValidationError):
        for err in validation_error.errors():
            loc = err["loc"]
            msg = err["msg"]
            if msg.startswith("Value error, "):
                msg = msg[len("Value error, "):]
            if len(loc) >= 2 and isinstance(loc[1], int):
                loc_name = f"{loc[0]}[{loc[1]}]"
                if len(loc) > 2:
                    loc_name += f".{loc[2]}"
            else:
                loc_name = ".".join(str(x) for x in loc)
            invalid_items.append(f"- {loc_name}: {msg}")
    elif validation_error is not None:
        invalid_items.append(f"- [SCHEMA_ERROR] {validation_error}")

    if draft_errors:
        for err in draft_errors:
            code = getattr(err, "code", "VALIDATION_ERROR")
            msg = getattr(err, "message", str(err))
            target_id = getattr(err, "target_id", None)
            target_str = f" on '{target_id}'" if target_id else ""
            invalid_items.append(f"- [{code}]{target_str} {msg}")

    if invalid_items:
        print("\nInvalid fields / validation issues:")
        for item in invalid_items:
            print(item)
    else:
        print("\nStatus: All fields conform to schema and contract.")
    print("-----------------------------------------\n")


def format_programmatic_repair_prompt(
    raw_payload: dict[str, Any],
    validation_error: Exception | None = None,
    draft_errors: list[Any] | None = None,
    approved_facts: dict[str, Any] | None = None,
) -> str:
    """Builds a surgical, error-specific repair prompt from Pydantic and draft validator errors."""
    lines: list[str] = [
        "The previous JSON is invalid. Return the complete corrected JSON.\n",
        "Errors:\n",
    ]
    err_idx = 1
    objects = raw_payload.get("objects", [])
    events = raw_payload.get("events", [])
    valid_fact_ids = list((approved_facts or {}).keys())

    if isinstance(validation_error, ValidationError):
        for err in validation_error.errors():
            loc = err["loc"]
            msg = err["msg"]
            if msg.startswith("Value error, "):
                msg = msg[len("Value error, "):]

            loc_str = (
                f"{loc[0]}[{loc[1]}]"
                if len(loc) >= 2 and isinstance(loc[1], int)
                else ".".join(str(x) for x in loc)
            )
            item_info = ""
            specific_guidance = ""

            # Event errors
            if len(loc) >= 2 and loc[0] == "events" and isinstance(loc[1], int):
                ev_idx = loc[1]
                if ev_idx < len(events):
                    ev = events[ev_idx]
                    action = ev.get("action")
                    tgt = ev.get("target_id")
                    item_info = f'   action is "{action}"\n   target_id is "{tgt}"\n'
                    if "requires 'to' destination zone" in msg or "to" in loc:
                        specific_guidance = (
                            '   Missing required field: "to"\n'
                            '   "to" must be one of:\n'
                            "   " + ", ".join(f'"{z}"' for z in VALID_ZONES) + "\n"
                        )
                    elif "requires 'to_fact_id'" in msg or "to_fact_id" in loc:
                        specific_guidance = (
                            '   Missing required field: "to_fact_id"\n'
                            "   Choose one exact approved fact ID from the supplied fact registry.\n"
                            f"   Valid fact IDs: {valid_fact_ids}\n"
                        )
                    elif "requires 'state'" in msg or "state" in loc:
                        specific_guidance = (
                            '   Missing required field: "state"\n'
                            "   Valid values:\n"
                            "   " + ", ".join(f'\"{s}\"' for s in VALID_VISUAL_STATES) + "\n"
                        )

            # Object errors
            elif len(loc) >= 2 and loc[0] == "objects" and isinstance(loc[1], int):
                obj_idx = loc[1]
                if obj_idx < len(objects):
                    obj = objects[obj_idx]
                    obj_type = obj.get("type")
                    obj_id = obj.get("id")
                    item_info = f'   type is "{obj_type}"\n   id is "{obj_id}"\n'
                    if obj_type == "connector":
                        specific_guidance = (
                            '   Missing required fields: "from_id", "to_id"\n'
                            "   Both from_id and to_id must reference declared non-connector objects.\n"
                            "   Remove all card fields (such as title, subtitle, visual_state, badge, value_fact_id) from this connector.\n"
                            "   A connector may contain only: id, type, layout, from_id, to_id, label, purpose.\n"
                        )
                    elif obj_type == "card" and "title" in msg:
                        specific_guidance = (
                            '   Missing required field: "title"\n'
                            "   Every card must have a non-empty header title string.\n"
                        )

            lines.append(f"{err_idx}. {loc_str}:\n{item_info}{specific_guidance}   Detail: {msg}\n")
            err_idx += 1

    elif validation_error is not None:
        lines.append(f"{err_idx}. Schema Validation Error:\n   {validation_error}\n")
        err_idx += 1

    if draft_errors:
        for err in draft_errors:
            code = getattr(err, "code", "DRAFT_VALIDATION_ERROR")
            msg = getattr(err, "message", str(err))
            target_id = getattr(err, "target_id", None)
            target_str = f" on '{target_id}'" if target_id else ""
            lines.append(f"{err_idx}. [{code}]{target_str}:\n   {msg}\n")
            err_idx += 1

    lines.append(f"Previous JSON: {json.dumps(raw_payload, ensure_ascii=False)}\n")
    lines.append("Return the entire corrected ContinuousStoryDraft.")
    lines.append("Do not return a partial patch.")
    lines.append("Do not omit valid objects or events.")
    return "\n".join(lines)



def build_continuous_story_prompt(
    story_id: str,
    narration_text: str,
    approved_facts: dict[str, Any],
) -> tuple[str, str]:
    """Builds system and user prompts for Gemini visual choreography with semantic fact grounding."""
    system_prompt = load_prompt("continuous_story_system.txt")

    semantic_registry: dict[str, dict[str, Any]] = {}
    for fid, fval in approved_facts.items():
        if isinstance(fval, dict):
            val = fval.get("value")
            fmt = fval.get("format", "plain")
            meaning = fval.get("meaning") or fval.get("label") or fid
            display = fval.get("display")
            if not display:
                if fmt == "currency_inr" and isinstance(val, (int, float)):
                    display = _format_inr(val)
                elif fmt == "percentage" and isinstance(val, (int, float)):
                    display = f"{val}%"
                elif fmt == "basis_points" and isinstance(val, (int, float)):
                    display = f"{val} bps"
                else:
                    display = str(val) if val is not None else "chart_data"
            allowed_use = fval.get("allowed_use", ["card_value", "transform_target"])
            semantic_registry[fid] = {
                "meaning": meaning,
                "display": display,
                "format": fmt,
                "allowed_use": allowed_use,
            }
        else:
            semantic_registry[fid] = {
                "meaning": str(fval),
                "display": str(fval),
                "format": "plain",
                "allowed_use": ["card_value"],
            }

    registry_json_str = json.dumps(semantic_registry, indent=2, ensure_ascii=False)
    fact_ids_str = ", ".join(repr(fid) for fid in approved_facts) or "(none)"

    user_prompt = (
        f"STORY ID: {story_id}\n\n"
        f"NARRATION TEXT (Spoken Audio Track):\n"
        f"\"{narration_text}\"\n\n"
        f"SEMANTIC FACT REGISTRY (Every card value, standalone number, chart, and transform_number MUST reference an approved fact_id from this registry):\n"
        f"```json\n{registry_json_str}\n```\n\n"
        f"APPROVED FACT IDS: {fact_ids_str}\n\n"
        "FACT USE INSTRUCTIONS:\n"
        "- Choose facts by their 'meaning' and 'allowed_use' rather than arbitrary IDs.\n"
        "- Baseline vs. Consequence: Use baseline facts (e.g. loan principal) for initial hero/context cards. Use consequence facts (e.g. total 30-year payout, lifetime interest outgo) for consequence beats or transform_number targets.\n"
        "- Solution: Use savings facts for solution/prepayment beats.\n"
        "- transform_number MUST use a fact representing a genuine consequential change (e.g. principal -> total payout).\n\n"
        "RULES REMINDER:\n"
        "- Every card requires a non-empty 'title'. 'value_fact_id' is optional for conceptual cards, but required when displaying a numeric fact.\n"
        "- Standalone numbers require 'fact_id'. Standalone charts require 'fact_id' and 'chart_type'.\n"
        "- Connectors MUST specify non-empty 'from_id' and 'to_id' referencing declared surface objects, and must NEVER include card fields (such as visual_state, badge, title, subtitle, or value_fact_id).\n"
        "- Use only the 12 spatial layout zone names: top_left, top_center, top_right, center_left, center, center_right, bottom_left, bottom_center, bottom_right, full_screen, full_top, full_bottom.\n"
        "- Prevent stacking: Do not enter a surface into an occupied zone.\n"
        "Output strictly valid ContinuousStoryDraft JSON following all rules."
    )
    return system_prompt, user_prompt


class ContinuousStoryEngine:
    """
    Engine that generates and compiles Continuous Story Choreography.

    Owns:
    1. Extracting and structuring approved facts from Research/Strategy.
    2. Prompt construction using continuous_story_system.txt.
    3. LLM choreography generation via Gemini.
    4. Two-tier self-healing repair loops (schema contract & spatial/temporal simulation).
    5. Deterministic StoryPlan compilation into Remotion frames.
    """

    def __init__(
        self,
        llm_provider: LLMProvider | None = None,
        compiler: ContinuousStoryCompiler | None = None,
    ) -> None:
        self.llm_provider = llm_provider
        self.compiler = compiler or ContinuousStoryCompiler()

    def run(
        self,
        *,
        project_id: str,
        voice_track: VoiceTrack,
        strategy: ScriptVisualStrategy,
        research_packet: ResearchPacket,
        approved_facts: dict[str, Any] | None = None,
        mock_draft: ContinuousStoryDraft | dict[str, Any] | None = None,
    ) -> ContinuousStoryEngineResult:
        # 1. Resolve approved facts from explicit argument or fallback to research
        if approved_facts is None:
            strat_dict = strategy.model_dump() if hasattr(strategy, "model_dump") else {}
            res_dict = research_packet.model_dump() if hasattr(research_packet, "model_dump") else {}
            if isinstance(strat_dict, dict) and strat_dict.get("approved_facts"):
                approved_facts = strat_dict["approved_facts"]
            elif isinstance(res_dict, dict) and res_dict.get("approved_facts"):
                approved_facts = res_dict["approved_facts"]
            else:
                approved_facts = _numeric_facts_from_research(research_packet)

        story_id = f"story_{project_id}"
        word_timestamps_raw = [
            ts if isinstance(ts, dict) else ts.model_dump()
            for ts in voice_track.word_timestamps
        ]
        max_word_end = max((w.get("end_ms", 0) for w in word_timestamps_raw), default=0)
        total_duration_ms = max(int(voice_track.duration_seconds * 1000), max_word_end)

        # 2. Generate visual choreography (Gemini or mock for testing)
        raw_gemini_payload: dict[str, Any] = {}
        provider_metadata: LLMProviderMetadata | None = None

        if mock_draft is not None:
            if isinstance(mock_draft, dict):
                raw_gemini_payload = mock_draft
                try:
                    draft = ContinuousStoryDraft.model_validate(mock_draft)
                except Exception as val_err:
                    print_local_preflight_report(raw_gemini_payload, validation_error=val_err)
                    raise ContinuousStoryEngineError(
                        f"Stage 7 failed: invalid visual choreography contract: {val_err}",
                        raw_payload=raw_gemini_payload,
                    ) from val_err
            else:
                draft = mock_draft
                raw_gemini_payload = mock_draft.model_dump()

            draft_validation = validate_story_draft(
                draft=draft,
                approved_facts=approved_facts,
                word_timestamps=word_timestamps_raw,
                total_duration_ms=total_duration_ms,
            )
            if not draft_validation.valid:
                print_local_preflight_report(raw_gemini_payload, draft_errors=draft_validation.errors)
                error_msgs = [f"[{e.code}] {e.message}" for e in draft_validation.errors]
                raise ContinuousStoryEngineError(
                    f"Stage 7 failed: invalid visual choreography contract: CONTINUOUS_STORY_VALIDATION_ERROR: {'; '.join(error_msgs)}",
                    raw_payload=raw_gemini_payload,
                )
            print_local_preflight_report(raw_gemini_payload)
        else:
            if self.llm_provider is None:
                raise ContinuousStoryEngineError(
                    "LLMProvider is required for ContinuousStoryEngine when mock_draft is not provided."
                )

            system_prompt, user_prompt = build_continuous_story_prompt(
                story_id=story_id,
                narration_text=voice_track.full_script_text,
                approved_facts=approved_facts,
            )
            draft_schema = ContinuousStoryDraft.model_json_schema()
            req = LLMJsonRequest(
                messages=[
                    LLMMessage(role="system", content=system_prompt),
                    LLMMessage(role="user", content=user_prompt),
                ],
                schema_name="ContinuousStoryDraft",
                response_schema=draft_schema,
                temperature=0.0,
                max_tokens=4096,
            )
            response = self.llm_provider.generate_json(req)
            raw_gemini_payload = response.payload
            provider_metadata = response.metadata
            try:
                draft = ContinuousStoryDraft.model_validate(raw_gemini_payload)
            except Exception as first_error:
                print_local_preflight_report(raw_gemini_payload, validation_error=first_error)
                repair_prompt_content = format_programmatic_repair_prompt(
                    raw_payload=raw_gemini_payload,
                    validation_error=first_error,
                    approved_facts=approved_facts,
                )
                repair_req = LLMJsonRequest(
                    messages=[
                        LLMMessage(
                            role="system",
                            content=(
                                system_prompt
                                + "\nReturn only the complete corrected JSON object. Do not explain the repair."
                            ),
                        ),
                        LLMMessage(role="user", content=repair_prompt_content),
                    ],
                    schema_name="ContinuousStoryDraftRepair",
                    response_schema=draft_schema,
                    temperature=0.0,
                    max_tokens=4096,
                )
                repaired = self.llm_provider.generate_json(repair_req)
                raw_gemini_payload = repaired.payload
                provider_metadata = repaired.metadata
                try:
                    draft = ContinuousStoryDraft.model_validate(raw_gemini_payload)
                except Exception as second_error:
                    print_local_preflight_report(raw_gemini_payload, validation_error=second_error)
                    raise ContinuousStoryEngineError(
                        f"Stage 7 failed: invalid visual choreography contract: {second_error}",
                        raw_payload=raw_gemini_payload,
                        provider_metadata=provider_metadata,
                    ) from second_error

            # 3. Run pre-compilation draft validation (occupancy & temporal simulation)
            draft_validation = validate_story_draft(
                draft=draft,
                approved_facts=approved_facts,
                word_timestamps=word_timestamps_raw,
                total_duration_ms=total_duration_ms,
            )
            if not draft_validation.valid:
                print_local_preflight_report(raw_gemini_payload, draft_errors=draft_validation.errors)
                temporal_repair_prompt = format_programmatic_repair_prompt(
                    raw_payload=raw_gemini_payload,
                    draft_errors=draft_validation.errors,
                    approved_facts=approved_facts,
                )
                repair_req = LLMJsonRequest(
                    messages=[
                        LLMMessage(
                            role="system",
                            content=(
                                system_prompt
                                + "\nReturn only the complete corrected JSON object. Do not explain the repair."
                            ),
                        ),
                        LLMMessage(role="user", content=temporal_repair_prompt),
                    ],
                    schema_name="ContinuousStoryDraftTemporalRepair",
                    response_schema=draft_schema,
                    temperature=0.0,
                    max_tokens=4096,
                )
                repaired = self.llm_provider.generate_json(repair_req)
                raw_gemini_payload = repaired.payload
                provider_metadata = repaired.metadata
                try:
                    draft = ContinuousStoryDraft.model_validate(raw_gemini_payload)
                except Exception as schema_err:
                    print_local_preflight_report(raw_gemini_payload, validation_error=schema_err)
                    raise ContinuousStoryEngineError(
                        f"Stage 7 failed: invalid visual choreography contract: {schema_err}",
                        raw_payload=raw_gemini_payload,
                        provider_metadata=provider_metadata,
                    ) from schema_err

                draft_validation = validate_story_draft(
                    draft=draft,
                    approved_facts=approved_facts,
                    word_timestamps=word_timestamps_raw,
                    total_duration_ms=total_duration_ms,
                )
                if not draft_validation.valid:
                    print_local_preflight_report(raw_gemini_payload, draft_errors=draft_validation.errors)
                    error_msgs = [f"[{e.code}] {e.message}" for e in draft_validation.errors]
                    raise ContinuousStoryEngineError(
                        f"Stage 7 failed: invalid visual choreography contract: CONTINUOUS_STORY_VALIDATION_ERROR: {'; '.join(error_msgs)}",
                        raw_payload=raw_gemini_payload,
                        provider_metadata=provider_metadata,
                    )

            # Preflight report on successful candidate
            print_local_preflight_report(raw_gemini_payload)

        # 4. Deterministic compilation
        fixture_context = {
            "story_id": draft.story_id,
            "approved_facts": approved_facts,
            "word_timestamps": word_timestamps_raw,
            "total_duration_ms": total_duration_ms,
            "audio_file": voice_track.audio_file_name,
            "narration_text": voice_track.full_script_text,
        }
        try:
            compiled_plan = self.compiler.compile(draft, fixture_context)
        except Exception as compile_err:
            raise ContinuousStoryEngineError(
                f"Stage 7 failed: invalid visual choreography contract: CONTINUOUS_STORY_COMPILER_ERROR: {compile_err}",
                raw_payload=raw_gemini_payload,
                provider_metadata=provider_metadata,
            ) from compile_err

        # 5. Build artifact envelope
        artifact_model = ContinuousStoryPlanArtifact.from_compiled_plan(
            plan=compiled_plan,
            draft=draft,
            audio_storage_key=voice_track.storage_key,
        )

        return ContinuousStoryEngineResult(
            artifact=artifact_model,
            draft=draft,
            raw_payload=raw_gemini_payload,
            provider_metadata=provider_metadata,
        )
