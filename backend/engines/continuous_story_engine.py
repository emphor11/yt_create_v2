from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any

from app.assets import load_prompt
from domain.continuous_story_plan import (
    ContinuousStoryDraft,
    ContinuousStoryPlanArtifact,
    VALID_CHART_TYPES,
    VALID_VISUAL_STATES,
    VALID_ZONES,
    build_continuous_story_contract_schema,
)
from domain.research_packet import ResearchPacket
from domain.script_visual_strategy import ScriptVisualStrategy
from domain.voice_track import VoiceTrack
from engines.continuous_story_asset_resolver import (
    ContinuousStoryAssetResolver,
    ContinuousStoryAssetResolverError,
    ResolvedImageAsset,
)
from engines.continuous_story_compiler import ContinuousStoryCompiler, resolve_anchor_frame
from engines.continuous_story_draft_validator import validate_story_draft
from pydantic import ValidationError
from providers.llm_provider import (
    LLMJsonRequest,
    LLMMessage,
    LLMProvider,
    LLMProviderMetadata,
)

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


def _normalize_zone(val: Any) -> str:
    """Validates zone name against the 5 allowed layouts.
    Never silently converts removed or unknown layouts to center.
    Fails loudly with ValueError('INVALID_LAYOUT_ZONE: ...') if invalid or unknown.
    """
    if isinstance(val, str) and val in VALID_ZONES:
        return val
    raise ValueError(f"INVALID_LAYOUT_ZONE: Layout zone '{val}' is invalid. Allowed layouts: {sorted(VALID_ZONES)}")


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
    object_types: dict[str, int] = {}
    for obj in raw_payload.get("objects", []):
        obj_type = str(obj.get("type", "unknown")) if isinstance(obj, dict) else "unknown"
        object_types[obj_type] = object_types.get(obj_type, 0) + 1
    print("\n--- CONTINUOUS STORY PREFLIGHT REPORT ---")
    print(f"Objects: {num_objects}")
    print(f"Events:  {num_events}")
    if object_types:
        composition = ", ".join(f"{key}={value}" for key, value in sorted(object_types.items()))
        print(f"Composition: {composition}")

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


EXACT_REPAIR_INSTRUCTION = (
    "Every anchor must be copied character-for-character from the verbatim narration.\n"
    "Do not paraphrase.\n"
    "Do not summarize.\n"
    "Do not invent anchor text.\n"
    "Use a unique phrase of at least 3 meaningful words.\n\n"
    "An exit anchor must occur strictly after the target object's enter anchor.\n"
    "Never use the same anchor for enter and exit.\n"
    "If there is no later spoken phrase, omit the exit event instead of inventing one."
)


def format_programmatic_repair_prompt(
    raw_payload: dict[str, Any],
    validation_error: Exception | None = None,
    draft_errors: list[Any] | None = None,
    approved_facts: dict[str, Any] | None = None,
    narration_text: str | None = None,
) -> str:
    """Builds a surgical, error-specific repair prompt from Pydantic and draft validator errors."""
    lines: list[str] = [
        "The previous JSON is invalid. Return the complete corrected JSON.\n",
        f"Repair Instructions:\n{EXACT_REPAIR_INSTRUCTION}\n",
    ]
    if narration_text and narration_text.strip():
        lines.append(f"Complete Verbatim Spoken Narration:\n\"\"\"\n{narration_text.strip()}\n\"\"\"\n")
    lines.append("Errors:\n")
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
                    elif "transform_number" in msg or "to_fact_id" in msg or "to_display_value" in msg or "to_numeric_value" in msg:
                        specific_guidance = (
                            '   Missing required fields: "to_display_value" and "to_numeric_value"\n'
                            '   Directly author both "to_display_value" (e.g. "₹1.38 Cr") and "to_numeric_value" (e.g. 13800000).\n'
                        )
                    elif "requires 'state'" in msg or "state" in loc:
                        specific_guidance = (
                            '   Missing required field: "state"\n'
                            "   Valid values:\n"
                            "   " + ", ".join(f'\"{s}\"' for s in VALID_VISUAL_STATES) + "\n"
                        )
                    elif action == "change_pose" or "pose" in loc or "change_pose" in msg:
                        specific_guidance = (
                            '   Action "change_pose" requires: "target_id" (referencing a character), "pose", "anchor".\n'
                            '   Valid poses: "idle", "walk", "point", "think", "worried", "celebrate".\n'
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
                    elif obj_type == "card" and ("title" in msg or "display_value" in msg or "subtitle" in msg):
                        specific_guidance = (
                            '   Missing required field: "title", "display_value", or "subtitle"\n'
                            "   Every card must have non-empty 'title', 'display_value', and 'subtitle'.\n"
                        )
                    elif obj_type == "chart" and ("series" in msg or "points" in msg):
                        specific_guidance = (
                            '   Missing required field: "series" or "points"\n'
                            "   Directly author chart series or points data without relying on fact lookup.\n"
                        )
                    elif obj_type == "character":
                        specific_guidance = (
                            '   Character requires: "character_style" ("futuristic_stick"), "role", "pose", "facing".\n'
                            '   Valid poses: "idle", "walk", "point", "think", "worried", "celebrate".\n'
                            '   Valid facing: "left", "right".\n'
                            "   Do not specify card, chart, number, or image fields on character.\n"
                        )
                    elif obj_type == "image":
                        specific_guidance = (
                            '   Image requires: "type": "image", "layout" ("split_left", "split_right", or "center"), "asset_request": {"query": "cinematic search phrase"}.\n'
                            '   Optional on image: "caption", "badge", "fit".\n'
                            "   Do not specify title, subtitle, display_value, or numeric_value on image.\n"
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
            details = getattr(err, "details", {}) or {}

            guidance = ""
            if code == "EXIT_BEFORE_OBJECT_ENTER":
                enter_anchor = details.get("enter_anchor", "")
                enter_time = details.get("enter_time_ms", "")
                exit_anchor = details.get("exit_anchor", "")
                exit_time = details.get("exit_time_ms", "")
                guidance = (
                    f"   Conflict details:\n"
                    f"     - Original enter anchor: '{enter_anchor}' (starts at {enter_time}ms)\n"
                    f"     - Attempted exit anchor: '{exit_anchor}' (starts at {exit_time}ms)\n"
                    f"   Required fix:\n"
                    f"     An exit anchor must occur strictly after the target object's enter anchor.\n"
                    f"     Never use the same anchor for enter and exit.\n"
                    f"     If there is no later spoken phrase, omit the exit event instead of inventing one.\n"
                )
            elif code == "ANCHOR_NOT_FOUND":
                anchor_val = details.get("anchor", "")
                guidance = (
                    f"   Invalid anchor: '{anchor_val}'\n"
                    f"   Required fix: Every anchor must be copied character-for-character from the verbatim narration above. Do not paraphrase or invent text.\n"
                )
            elif code == "CONNECT_BEFORE_CARDS_ENTER":
                ep_role = details.get("endpoint_role", "endpoint")
                ep_id = details.get("endpoint_id", "")
                ep_enter_t = details.get("endpoint_enter_time_ms", "")
                ep_anchor = details.get("endpoint_enter_anchor", "")
                conn_t = details.get("connect_time_ms", "")
                conn_anchor = details.get("connect_anchor", "")
                guidance = (
                    f"   Conflict details:\n"
                    f"     - Connector connects at {conn_t}ms (anchor: '{conn_anchor}')\n"
                    f"     - But {ep_role} card '{ep_id}' enters at {ep_enter_t}ms (enter anchor: '{ep_anchor}')\n"
                    f"   Required fix:\n"
                    f"     A connector can only connect strictly AFTER BOTH source ('from_id') and target ('to_id') cards have entered.\n"
                    f"     Change the connector's anchor to a spoken phrase occurring AFTER both endpoint cards are already on screen.\n"
                )
            elif code == "ZONE_OCCUPANCY_COLLISION":
                zone = details.get("zone", "")
                other_id = details.get("colliding_with", "")
                s_ms = details.get("start_ms", "")
                e_ms = details.get("end_ms", "")
                s_sec = f"{s_ms/1000:.1f}s" if isinstance(s_ms, (int, float)) else str(s_ms)
                e_sec = f"{e_ms/1000:.1f}s" if isinstance(e_ms, (int, float)) else str(e_ms)
                guidance = (
                    f"   Spatial collision details:\n"
                    f"     - Zone '{zone}' is occupied by '{other_id}' during {s_sec} to {e_sec} ({s_ms}ms–{e_ms}ms).\n"
                    f"   Required fix:\n"
                    f"     Two elements cannot occupy the same zone at the same time.\n"
                    f"     Option A: Place '{target_id}' into a different, free zone (e.g. split_left, split_right, center, full_bottom).\n"
                    f"     Option B: Add an explicit 'exit' event to remove '{other_id}' before '{target_id}' enters zone '{zone}'.\n"
                )
            elif code == "MACRO_LAYOUT_COLLISION":
                macro_zone = details.get("macro_zone", "")
                conflict_zone = details.get("conflicting_zone", "")
                other_id = details.get("colliding_with", "")
                s_ms = details.get("start_ms", "")
                e_ms = details.get("end_ms", "")
                s_sec = f"{s_ms/1000:.1f}s" if isinstance(s_ms, (int, float)) else str(s_ms)
                e_sec = f"{e_ms/1000:.1f}s" if isinstance(e_ms, (int, float)) else str(e_ms)
                guidance = (
                    f"   Macro layout collision details:\n"
                    f"     - Macro zone '{macro_zone}' conflicts with '{conflict_zone}' (occupied by '{other_id}') during {s_sec} to {e_sec} ({s_ms}ms–{e_ms}ms).\n"
                    f"   Required fix:\n"
                    f"     Macro/split zones cannot overlap in time with child/conflicting zones.\n"
                    f"     Assign '{target_id}' or '{other_id}' to non-conflicting zones, or exit one before the other enters.\n"
                )
            elif code == "CARD_OVERLAP":
                id1 = details.get("id1", "")
                id2 = details.get("id2", target_id or "")
                z1 = details.get("zone1", "")
                z2 = details.get("zone2", "")
                s_ms = details.get("start_ms", "")
                e_ms = details.get("end_ms", "")
                s_sec = f"{s_ms/1000:.1f}s" if isinstance(s_ms, (int, float)) else str(s_ms)
                e_sec = f"{e_ms/1000:.1f}s" if isinstance(e_ms, (int, float)) else str(e_ms)
                zone_desc = f" in '{z1}' and '{z2}'" if z1 and z2 else ""
                guidance = (
                    f"   Spatial bounding box overlap details:\n"
                    f"     - '{id1}' and '{id2}'{zone_desc} physically collide on screen during {s_sec} to {e_sec} ({s_ms}ms–{e_ms}ms).\n"
                    f"     - Elements in 'center' (especially wide text primitives) physically cross into and overlap with 'split_left' and 'split_right'.\n"
                    f"   Required fix:\n"
                    f"     Option A: Add an explicit 'exit' event to remove '{id1}' before '{id2}' enters.\n"
                    f"     Option B: Place both elements in non-overlapping layout zones (e.g., split_left and split_right).\n"
                )
            elif code == "MISSING_ENTER_EVENT":
                guidance = (
                    f"   Missing enter event for '{target_id}'.\n"
                    f"   Required fix: Every object in 'objects' must have an explicit 'enter' (or 'connect' for connector) event in 'events'.\n"
                    f"   Add an enter event for '{target_id}' with an exact anchor phrase from the narration.\n"
                )
            elif code == "ACTION_BEFORE_OBJECT_ENTER":
                enter_anchor = details.get("enter_anchor", "")
                enter_time = details.get("enter_time_ms", "")
                ev_anchor = details.get("event_anchor", "")
                ev_time = details.get("event_time_ms", "")
                act = details.get("action", "action")
                guidance = (
                    f"   Action before enter details:\n"
                    f"     - '{target_id}' enters at {enter_time}ms (enter anchor: '{enter_anchor}')\n"
                    f"     - But '{act}' action occurs at {ev_time}ms (anchor: '{ev_anchor}')\n"
                    f"   Required fix:\n"
                    f"     All actions on '{target_id}' must occur strictly after it enters the canvas.\n"
                )

            lines.append(f"{err_idx}. [{code}]{target_str}:\n   {msg}\n{guidance}")
            err_idx += 1

    lines.append(f"Previous JSON: {json.dumps(raw_payload, ensure_ascii=False)}\n")
    lines.append("Return the entire corrected ContinuousStoryDraft.")
    lines.append("Do not return a partial patch.")
    lines.append("Do not omit valid objects or events.")
    return "\n".join(lines)



def build_continuous_story_prompt(
    story_id: str,
    narration_text: str,
    approved_facts: dict[str, Any] | None = None,
    visual_strategy: Any | None = None,
    available_assets: list[str] | None = None,
) -> tuple[str, str]:
    """Builds system and user prompts for Gemini visual choreography in open direct-authoring mode."""
    system_prompt = load_prompt("continuous_story_system.txt")

    approved_facts = approved_facts or {}
    available_assets = available_assets or []
    assets_str = (
        ", ".join(repr(a) for a in available_assets)
        if available_assets
        else "(None pre-loaded — request real-world images dynamically using 'asset_request')"
    )

    strategy_str = ""
    if visual_strategy:
        if hasattr(visual_strategy, "model_dump"):
            strat_json = json.dumps(visual_strategy.model_dump(), indent=2, ensure_ascii=False)
        elif isinstance(visual_strategy, dict):
            strat_json = json.dumps(visual_strategy, indent=2, ensure_ascii=False)
        else:
            strat_json = str(visual_strategy)
        strategy_str = f"VISUAL STRATEGY:\n{strat_json}\n\n"

    user_prompt = (
        f"STORY ID: {story_id}\n\n"
        f"NARRATION TEXT (Spoken Audio Track):\n"
        f"\"{narration_text}\"\n\n"
        f"{strategy_str}"
        f"AVAILABLE IMAGE ASSETS:\n{assets_str}\n\n"
        "The system prompt above is the single authoritative contract. Follow the mandatory 3-second visual refresh rate and the explicit budget (35–50 declared objects, 60–80 events, and 3–6 real-world 'image' objects with descriptive 'asset_request' for 120–180s narration). Localized images conform to 420x240 dimensions. Use direct-authoring mode, exact spoken anchors, and return the complete ContinuousStoryDraft JSON only."
    )
    return system_prompt, user_prompt


def _validate_direct_authoring_contract(
    draft: ContinuousStoryDraft,
    available_assets: list[str] | set[str] | None = None,
) -> None:
    """Validates that Gemini provides all required direct-authored fields for each primitive."""
    errors: list[str] = []
    if available_assets is not None and not isinstance(available_assets, set):
        available_assets = set(available_assets)

    for obj in draft.objects:
        if obj.type == "card":
            if not obj.title or not obj.title.strip():
                errors.append(f"Card '{obj.id}' requires non-empty direct 'title'.")
            if not obj.display_value or not str(obj.display_value).strip():
                errors.append(f"Card '{obj.id}' requires non-empty direct 'display_value'.")
            if not obj.subtitle or not obj.subtitle.strip():
                errors.append(f"Card '{obj.id}' requires non-empty direct 'subtitle'.")
        elif obj.type == "number":
            if not obj.display_value and obj.numeric_value is None:
                errors.append(f"Standalone number '{obj.id}' requires direct 'display_value' or 'numeric_value'.")
        elif obj.type == "text":
            if not obj.text or not obj.text.strip():
                errors.append(f"Text element '{obj.id}' requires non-empty direct 'text'.")
        elif obj.type == "chart":
            if not obj.chart_type:
                errors.append(f"Chart '{obj.id}' requires 'chart_type'.")
            if not obj.series and not obj.points:
                errors.append(f"Chart '{obj.id}' requires directly authored 'series' or 'points'.")
        elif obj.type == "image":
            if not obj.asset_request and (not obj.asset_id or not obj.asset_id.strip()):
                errors.append(f"Image '{obj.id}' requires 'asset_request' or 'asset_id'.")
            elif obj.asset_id and available_assets and obj.asset_id not in available_assets:
                errors.append(f"Image '{obj.id}' references unknown asset_id '{obj.asset_id}'. Available assets: {sorted(available_assets)}")
            elif obj.asset_id and not available_assets:
                errors.append(f"Image '{obj.id}' references asset_id '{obj.asset_id}', but available_assets list is empty.")
        elif obj.type == "connector":
            if not obj.from_id or not obj.to_id:
                errors.append(f"Connector '{obj.id}' requires 'from_id' and 'to_id'.")
            if obj.visual_state or obj.badge or obj.title or obj.subtitle or obj.display_value or obj.numeric_value:
                errors.append(f"Connector '{obj.id}' must not contain card, number, or visual-state fields.")
        elif obj.type == "character":
            if not obj.character_style or obj.character_style != "futuristic_stick":
                errors.append(f"Character '{obj.id}' requires 'character_style' to be 'futuristic_stick'.")
            if not obj.role or not obj.role.strip():
                errors.append(f"Character '{obj.id}' requires non-empty 'role'.")
            if not obj.pose or obj.pose not in ("idle", "walk", "point", "think", "worried", "celebrate"):
                errors.append(f"Character '{obj.id}' requires valid 'pose'.")
            if not obj.facing or obj.facing not in ("left", "right"):
                errors.append(f"Character '{obj.id}' requires valid 'facing' ('left' or 'right').")

    obj_map = {o.id: o for o in draft.objects}
    for event in draft.events:
        if event.action == "transform_number":
            if not event.to_display_value or not event.to_display_value.strip():
                errors.append(f"transform_number on '{event.target_id}' requires 'to_display_value'.")
            if event.to_numeric_value is None:
                errors.append(f"transform_number on '{event.target_id}' requires 'to_numeric_value'.")
        elif event.action == "change_pose":
            target_obj = obj_map.get(event.target_id)
            if not target_obj:
                errors.append(f"change_pose references non-existent target_id '{event.target_id}'.")
            elif target_obj.type != "character":
                errors.append(f"change_pose on '{event.target_id}' must target a 'character', but is '{target_obj.type}'.")
            if not event.pose or event.pose not in ("idle", "walk", "point", "think", "worried", "celebrate"):
                errors.append(f"change_pose on '{event.target_id}' requires valid 'pose'.")

    if errors:
        raise ContinuousStoryEngineError(
            "Stage 7 failed: direct-authoring contract violation: " + " ".join(errors)
        )


def _validate_editorial_composition(
    draft: ContinuousStoryDraft,
    narration_text: str,
) -> None:
    """Rejects visually impoverished drafts before compilation.

    This is an editorial quality gate, not a value/fact validator. The renderer
    already supports every primitive; this gate prevents Gemini from taking the
    safest but least expressive path of emitting only metric cards.
    """
    object_types = {obj.type for obj in draft.objects}
    card_count = sum(1 for obj in draft.objects if obj.type == "card")
    errors: list[str] = []
    narration = narration_text.lower()

    if card_count >= 2 and not (object_types - {"card"}):
        errors.append(
            "CARD_ONLY_COMPOSITION: two or more cards were declared without any supporting primitive. "
            "Use a standalone number, connector, chart, character, text, or image where the narration warrants it."
        )

    human_cues = (
        "person", "people", "employee", "worker", "borrower", "investor", "customer",
        "family", "household", "salary", "professional", "retiree", "saver", "their life",
        "your money", "your salary", "someone",
    )
    if any(cue in narration for cue in human_cues) and "character" not in object_types:
        errors.append(
            "MISSING_CHARACTER_FOR_HUMAN_NARRATIVE: the narration describes a person or lived financial experience, "
            "but no character primitive was declared."
        )

    trend_cues = (
        "over time", "over the years", "over decades", "year by year", "compounds", "compound",
        "growth", "grows", "trajectory", "declines", "decline", "falls", "rises", "trend",
        "difference", "gap", "compare", "comparison", "from ", " to ",
    )
    if any(cue in narration for cue in trend_cues) and "chart" not in object_types:
        errors.append(
            "MISSING_CHART_FOR_TREND_NARRATIVE: the narration describes a trend, comparison, gap, or time progression, "
            "but no chart primitive was declared."
        )

    causal_cues = (
        "because", "leads to", "leads", "causes", "caused", "results in", "drives", "turns into",
        "erodes", "eats away", "converts into", "becomes", "as a result", "which means",
    )
    if any(cue in narration for cue in causal_cues) and card_count >= 2 and "connector" not in object_types:
        errors.append(
            "MISSING_CONNECTOR_FOR_CAUSAL_NARRATIVE: the narration expresses a cause-and-effect relationship, "
            "but no connector object was declared."
        )

    numeric_cues = (
        "₹", "rupee", "rupees", "lakh", "crore", "%", "percent", "per cent", "years", "months",
    )
    if any(cue in narration for cue in numeric_cues) and card_count >= 2 and "number" not in object_types:
        errors.append(
            "MISSING_STANDALONE_NUMBER: the finance narration contains major numeric information, "
            "but no standalone number primitive was declared for the primary reveal."
        )

    institution_or_physical_cues = (
        "bank", "lender", "insurer", "insurance", "company", "office", "branch",
        "home", "house", "property", "car", "vehicle", "gold",
        "document", "contract", "policy", "agreement", "paperwork", "form",
    )
    image_count = sum(1 for obj in draft.objects if obj.type == "image")
    if any(cue in narration for cue in institution_or_physical_cues) and card_count >= 2 and image_count < 1:
        errors.append(
            "MISSING_IMAGE_FOR_PHYSICAL_GROUNDING: the narration references institutions, documents, or physical assets, "
            "but no 'image' primitive was declared. Declare at least 2–3 images with 'asset_request' to ground these entities."
        )

    if errors:
        raise ContinuousStoryEngineError(
            "Stage 7 failed: editorial composition quality gate: " + " ".join(errors)
        )


class ContinuousStoryEngine:
    """
    Engine that generates and compiles Continuous Story Choreography.

    Owns:
    1. Managing open direct authoring across all 6 visual primitives.
    2. Prompt construction using continuous_story_system.txt.
    3. LLM choreography generation via Gemini.
    4. Two-tier self-healing repair loops (schema contract & spatial/temporal simulation).
    5. Deterministic StoryPlan compilation into Remotion frames.
    """

    def __init__(
        self,
        llm_provider: LLMProvider | None = None,
        compiler: ContinuousStoryCompiler | None = None,
        asset_resolver: ContinuousStoryAssetResolver | None = None,
    ) -> None:
        self.llm_provider = llm_provider
        self.compiler = compiler or ContinuousStoryCompiler()
        self.asset_resolver = asset_resolver or ContinuousStoryAssetResolver()

    def _resolve_image_assets(
        self,
        draft: ContinuousStoryDraft,
        project_id: str,
        available_assets: list[str],
        word_timestamps: list[dict[str, Any]] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Resolves ImageAssetRequests on image objects and VideoAssetRequests on stock_video objects in the draft.
        Attaches resolved asset_id to each image/video and populates available_assets.
        """
        resolved_records: list[dict[str, Any]] = []
        for obj in draft.objects:
            if obj.type == "image":
                if obj.asset_request is not None:
                    try:
                        resolved = self.asset_resolver.resolve_image_asset(
                            obj.asset_request,
                            object_id=obj.id,
                            project_id=project_id,
                        )
                    except ContinuousStoryAssetResolverError as res_err:
                        raise ContinuousStoryEngineError(
                            f"Stage 7 failed: {res_err}",
                        ) from res_err
                    except Exception as err:
                        raise ContinuousStoryEngineError(
                            f"Stage 7 failed: IMAGE_DOWNLOAD_FAILED: {err}",
                        ) from err

                    obj.asset_id = resolved.asset_id
                    resolved_records.append(resolved.to_dict())
                    if resolved.asset_id not in available_assets:
                        available_assets.append(resolved.asset_id)
                elif obj.asset_id and obj.asset_id.strip():
                    if available_assets and obj.asset_id not in available_assets:
                        raise ContinuousStoryEngineError(
                            f"Stage 7 failed: UNKNOWN_ASSET_ID: Image '{obj.id}' references unknown asset_id '{obj.asset_id}'. Available: {sorted(available_assets)}"
                        )
                    elif not available_assets:
                        raise ContinuousStoryEngineError(
                            f"Stage 7 failed: UNKNOWN_ASSET_ID: Image '{obj.id}' references asset_id '{obj.asset_id}', but available_assets is empty."
                        )
                else:
                    raise ContinuousStoryEngineError(
                        f"Stage 7 failed: IMAGE_ASSET_REQUEST_MISSING: Image '{obj.id}' has neither asset_request nor asset_id."
                    )

            elif obj.type == "stock_video":
                # Compute required duration if word_timestamps available
                required_duration = None
                if word_timestamps:
                    enter_ev = next((e for e in draft.events if e.action == "enter" and e.target_id == obj.id), None)
                    exit_ev = next((e for e in draft.events if e.action == "exit" and e.target_id == obj.id), None)
                    if enter_ev and exit_ev:
                        try:
                            from engines.continuous_story_compiler import resolve_anchor_ms
                            s_ms = resolve_anchor_ms(word_timestamps, enter_ev.anchor)
                            e_ms = resolve_anchor_ms(word_timestamps, exit_ev.anchor)
                            if e_ms > s_ms:
                                required_duration = (e_ms - s_ms) / 1000.0
                        except Exception:
                            pass

                if obj.asset_request is not None:
                    try:
                        resolved = self.asset_resolver.resolve_video_asset(
                            obj.asset_request,
                            object_id=obj.id,
                            project_id=project_id,
                            required_duration_seconds=required_duration,
                        )
                    except ContinuousStoryAssetResolverError as res_err:
                        raise ContinuousStoryEngineError(
                            f"Stage 7 failed: {res_err}",
                        ) from res_err
                    except Exception as err:
                        raise ContinuousStoryEngineError(
                            f"Stage 7 failed: VIDEO_DOWNLOAD_FAILED: {err}",
                        ) from err

                    obj.asset_id = resolved.asset_id
                    resolved_records.append(resolved.to_dict())
                    if resolved.asset_id not in available_assets:
                        available_assets.append(resolved.asset_id)
                elif obj.asset_id and obj.asset_id.strip():
                    if available_assets and obj.asset_id not in available_assets:
                        raise ContinuousStoryEngineError(
                            f"Stage 7 failed: UNKNOWN_ASSET_ID: stock_video '{obj.id}' references unknown asset_id '{obj.asset_id}'. Available: {sorted(available_assets)}"
                        )
                    elif not available_assets:
                        raise ContinuousStoryEngineError(
                            f"Stage 7 failed: UNKNOWN_ASSET_ID: stock_video '{obj.id}' references asset_id '{obj.asset_id}', but available_assets is empty."
                        )
                else:
                    raise ContinuousStoryEngineError(
                        f"Stage 7 failed: VIDEO_ASSET_REQUEST_MISSING: stock_video '{obj.id}' has neither asset_request nor asset_id."
                    )
        return resolved_records

    def run(
        self,
        *,
        project_id: str,
        voice_track: VoiceTrack,
        strategy: ScriptVisualStrategy,
        research_packet: ResearchPacket,
        approved_facts: dict[str, Any] | None = None,
        available_assets: list[str] | None = None,
        mock_draft: ContinuousStoryDraft | dict[str, Any] | None = None,
    ) -> ContinuousStoryEngineResult:
        # Resolve approved facts if provided (optional in open direct authoring mode)
        if approved_facts is None:
            strat_dict = strategy.model_dump() if hasattr(strategy, "model_dump") else {}
            res_dict = research_packet.model_dump() if hasattr(research_packet, "model_dump") else {}
            if isinstance(strat_dict, dict) and strat_dict.get("approved_facts"):
                approved_facts = strat_dict["approved_facts"]
            elif isinstance(res_dict, dict) and res_dict.get("approved_facts"):
                approved_facts = res_dict["approved_facts"]
            else:
                approved_facts = {}

        story_id = f"story_{project_id}"
        word_timestamps_raw = [
            ts if isinstance(ts, dict) else ts.model_dump()
            for ts in voice_track.word_timestamps
        ]
        max_word_end = max((w.get("end_ms", 0) for w in word_timestamps_raw), default=0)
        total_duration_ms = max(int(voice_track.duration_seconds * 1000), max_word_end)
        available_assets_list: list[str] = list(available_assets) if available_assets is not None else []
        resolved_assets_records: list[dict[str, Any]] = []

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

            resolved_assets_records = self._resolve_image_assets(
                draft=draft,
                project_id=project_id,
                available_assets=available_assets_list,
                word_timestamps=word_timestamps_raw,
            )

            draft_validation = validate_story_draft(
                draft=draft,
                approved_facts=approved_facts,
                word_timestamps=word_timestamps_raw,
                total_duration_ms=total_duration_ms,
                available_assets=available_assets_list,
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
                visual_strategy=strategy,
                available_assets=available_assets_list,
            )
            draft_schema = build_continuous_story_contract_schema()
            req = LLMJsonRequest(
                messages=[
                    LLMMessage(role="system", content=system_prompt),
                    LLMMessage(role="user", content=user_prompt),
                ],
                schema_name="ContinuousStoryDraft",
                response_schema=draft_schema,
                temperature=0.0,
                max_tokens=32768,
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
                    narration_text=voice_track.full_script_text,
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
                    max_tokens=32768,
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

            # 3. Resolve every image asset_request
            resolved_assets_records = self._resolve_image_assets(
                draft=draft,
                project_id=project_id,
                available_assets=available_assets_list,
                word_timestamps=word_timestamps_raw,
            )

            # 4. Run pre-compilation draft validation (occupancy & temporal simulation) with iterative repair
            max_validation_attempts = 4
            for attempt in range(max_validation_attempts):
                draft_validation = validate_story_draft(
                    draft=draft,
                    approved_facts=approved_facts,
                    word_timestamps=word_timestamps_raw,
                    total_duration_ms=total_duration_ms,
                    available_assets=available_assets_list,
                )
                if draft_validation.valid:
                    break

                print_local_preflight_report(raw_gemini_payload, draft_errors=draft_validation.errors)
                if attempt == max_validation_attempts - 1:
                    error_msgs = [f"[{e.code}] {e.message}" for e in draft_validation.errors]
                    raise ContinuousStoryEngineError(
                        f"Stage 7 failed: invalid visual choreography contract: CONTINUOUS_STORY_VALIDATION_ERROR: {'; '.join(error_msgs)}",
                        raw_payload=raw_gemini_payload,
                        provider_metadata=provider_metadata,
                    )

                temporal_repair_prompt = format_programmatic_repair_prompt(
                    raw_payload=raw_gemini_payload,
                    draft_errors=draft_validation.errors,
                    approved_facts=approved_facts,
                    narration_text=voice_track.full_script_text,
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
                    schema_name=f"ContinuousStoryDraftTemporalRepair_{attempt + 1}",
                    response_schema=draft_schema,
                    temperature=0.0,
                    max_tokens=32768,
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

                resolved_assets_records = self._resolve_image_assets(
                    draft=draft,
                    project_id=project_id,
                    available_assets=available_assets_list,
                    word_timestamps=word_timestamps_raw,
                )

            # Preflight report on successful candidate
            print_local_preflight_report(raw_gemini_payload)

        # Real Gemini drafts must use direct authored values.
        if mock_draft is None:
            _validate_direct_authoring_contract(draft, available_assets_list)

        # 4. Deterministic compilation
        asset_durations = {
            rec["asset_id"]: rec.get("duration")
            for rec in resolved_assets_records
            if isinstance(rec, dict) and "duration" in rec and rec.get("duration")
        }
        fixture_context = {
            "story_id": draft.story_id,
            "approved_facts": approved_facts,
            "word_timestamps": word_timestamps_raw,
            "total_duration_ms": total_duration_ms,
            "audio_file": voice_track.audio_file_name,
            "narration_text": voice_track.full_script_text,
            "available_assets": available_assets_list,
            "asset_durations": asset_durations,
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
            resolved_assets=resolved_assets_records,
        )

        return ContinuousStoryEngineResult(
            artifact=artifact_model,
            draft=draft,
            raw_payload=raw_gemini_payload,
            provider_metadata=provider_metadata,
        )
