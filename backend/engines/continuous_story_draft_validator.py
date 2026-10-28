"""
continuous_story_draft_validator.py — Pre-Compilation AI Draft Validator.

Validates a parsed ContinuousStoryDraft produced by an AI (or fake provider)
BEFORE deterministic compilation into Remotion plans.

CRITICAL ARCHITECTURAL PIPELINE FLOW:
  1. Raw Gemini JSON
  2. ContinuousStoryDraft.model_validate(...)   [Enforces Pydantic schema, extra="forbid", ZoneName]
  3. validate_story_draft(...)                  [Enforces semantic graph integrity, approved facts, temporal causality, and spatial non-collision]
  4. ContinuousStoryCompiler                    [Compiles to Remotion StoryPlan]

NEVER call validate_story_draft() on an unparsed dictionary.

Enforces 16 strict pre-compilation rules:
1. Every layout is one of the 5 allowed layouts: center, split_left, split_right, full_screen, full_bottom.
2. Every object has a unique ID.
3. Every fact ID (fact_id, value_fact_id) exists in approved_facts.
4. 'number' and card metrics reference numeric facts.
5. 'chart' objects reference valid chart facts with series or segments.
6. Every event target exists in declared objects.
7. Every connector's from_id and to_id exist and target valid surface elements.
8. Connectors strictly connect visual surface elements (card, chart, image).
9. Every speech anchor can be found in narration timestamp words.
10. Word timestamps have valid ranges (non-negative, monotonic, end >= start).
11. Every event happens after its target has entered.
12. 'transform_number' strictly targets 'card' or 'number' and uses an approved numeric fact.
13. 'change_visual_state' strictly targets 'card' elements.
14. 'exit' actions require a valid direction ('left', 'right', 'up', 'down', 'fade').
15. TEMPORAL SPATIAL OCCUPANCY: Two surface elements cannot occupy the same zone simultaneously.
16. MACRO & BOUNDARY EXCLUSIVITY: full_screen requires exclusive canvas; full_bottom cannot conflict with subtitle clearance or active surfaces.
"""
from __future__ import annotations

import html
import math
import re
from dataclasses import dataclass, field
from typing import Any

from domain.continuous_story_plan import ContinuousStoryDraft


VALID_ZONES = {
    "center",
    "split_left",
    "split_right",
    "full_screen",
    "full_bottom",
}

SURFACE_TYPES = {
    "card",
    "number",
    "text",
    "chart",
    "image",
    "character",
    "scale",
    "money_stack",
    "document",
    "waterfall",
    "capital_flow",
}
EXIT_DURATION_MS = 0  # Zone releases immediately upon exit start, enabling seamless cross-fades and handoffs without black screen gaps

MACRO_ZONE_CONFLICTS: dict[str, set[str]] = {
    "full_screen": {
        "center",
        "split_left",
        "split_right",
        "full_bottom",
        "full_screen",
    },
}

DEFAULT_PRIMITIVE_DIMENSIONS: dict[str, tuple[int, int]] = {
    "chart": (560, 320),
    "document": (580, 360),
    "image": (420, 240),
    "number": (340, 160),
    "text": (800, 160),
    "character": (240, 360),
    "card": (420, 240),
    "stock_video": (1920, 1080),
    "scale": (640, 360),
    "money_stack": (640, 360),
    "waterfall": (640, 360),
    "capital_flow": (680, 320),
}

ZONE_CENTERS: dict[str, tuple[int, int]] = {
    "center": (960, 540),
    "split_left": (480, 540),
    "split_right": (1440, 540),
}


def _resolve_obj_geometry(
    obj_type: str,
    zone: str,
    width: int | None = None,
    height: int | None = None,
) -> tuple[int, int, int, int]:
    if zone not in VALID_ZONES:
        raise ValueError(
            f"INVALID_LAYOUT_ZONE: Invalid zone '{zone}'. Valid zones: {sorted(VALID_ZONES)}"
        )
    default_w, default_h = DEFAULT_PRIMITIVE_DIMENSIONS.get(obj_type, (420, 240))
    w = width if width is not None else default_w
    h = height if height is not None else default_h

    # Ensure localized images strictly stay under the zone's safe dimensions
    if obj_type == "image" and zone in ZONE_CENTERS:
        max_w = 740 if zone in ("split_left", "split_right") else 1080
        max_h = 440 if zone in ("split_left", "split_right") else 640
        w = min(w, max_w)
        h = min(h, max_h)

    if zone in ZONE_CENTERS:
        cx, cy = ZONE_CENTERS[zone]
        x = round(cx - w / 2)
        y = round(cy - h / 2)
    elif zone == "full_screen":
        if obj_type in ("image", "stock_video"):
            x, y, w, h = 0, 0, 1920, 1080
        else:
            x, y, w, h = 80, 80, 1920 - 160, 1080 - 160
    elif zone == "full_bottom":
        if height is None:
            h = 260
        x, w, h = 80, 1920 - 160, h
        y = 1080 - 80 - h - 40
    else:
        x = round((1920 - w) / 2)
        y = round((1080 - h) / 2)

    return x, y, w, h


@dataclass(frozen=True)
class DraftValidationError:
    code: str
    message: str
    target_id: str | None = None
    details: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DraftValidationResult:
    valid: bool
    errors: list[DraftValidationError]

    def raise_if_invalid(self) -> None:
        if not self.valid:
            error_lines = [f"[{e.code}] {e.message}" for e in self.errors]
            raise ValueError("Draft validation failed:\n" + "\n".join(error_lines))


def _clean_token(text: str) -> str:
    """Normalize word token for speech anchor matching."""
    return re.sub(r"[^\w\.]", "", text.lower()).strip(".")


def _get_anchor_start_ms(anchor: str, word_timestamps: list[dict[str, Any]], min_start_ms: int = 0) -> int | None:
    """Returns the start_ms of the exact contiguous anchor phrase in word timestamps at or after min_start_ms, or None if not found."""
    if not anchor or not word_timestamps:
        return None

    anchor_decoded = html.unescape(anchor)
    anchor_clean = re.sub(r"<[^>]+>", " ", anchor_decoded).replace("-", " ")
    anchor_clean = re.sub(r"([a-zA-Z]+)(\d+)", r"\1 \2", anchor_clean)
    anchor_clean = re.sub(r"(\d+)([a-zA-Z]+)", r"\1 \2", anchor_clean)
    clean_anchor_tokens = [_clean_token(t) for t in anchor_clean.split() if _clean_token(t)]
    if not clean_anchor_tokens:
        return None

    token_entries: list[tuple[str, int, int]] = []
    for w in word_timestamps:
        start_ms = w.get("start_ms", 0)
        end_ms = w.get("end_ms", 0)
        w_raw = str(w.get("word", ""))
        w_decoded = html.unescape(w_raw)
        w_stripped = re.sub(r"<[^>]+>", " ", w_decoded)
        w_clean = w_stripped.replace("-", " ")
        w_clean = re.sub(r"([a-zA-Z]+)(\d+)", r"\1 \2", w_clean)
        w_clean = re.sub(r"(\d+)([a-zA-Z]+)", r"\1 \2", w_clean)
        for tok in w_clean.split():
            c_tok = _clean_token(tok)
            if c_tok and not w_raw.strip().startswith("<break") and not w_raw.strip().startswith("<pause"):
                token_entries.append((c_tok, start_ms, end_ms))

    num_tokens = len(clean_anchor_tokens)
    for i in range(len(token_entries) - num_tokens + 1):
        if token_entries[i][1] < min_start_ms:
            continue
        match = True
        for j in range(num_tokens):
            if token_entries[i + j][0] != clean_anchor_tokens[j]:
                match = False
                break
        if match:
            return token_entries[i][1]

    # No first-token fallback, no substring matching, no fallback search from frame zero
    return None


def _find_anchor_in_words(anchor: str, word_timestamps: list[dict[str, Any]], min_start_ms: int = 0) -> bool:
    """Checks if exact anchor phrase tokens exist in narration word timestamps as an exact contiguous sub-sequence."""
    return _get_anchor_start_ms(anchor, word_timestamps, min_start_ms=min_start_ms) is not None



def validate_story_draft(
    draft: ContinuousStoryDraft,
    approved_facts: dict[str, Any] | None = None,
    word_timestamps: list[dict[str, Any]] | None = None,
    total_duration_ms: int | None = None,
    available_assets: list[str] | set[str] | None = None,
) -> DraftValidationResult:
    """
    Validates a parsed ContinuousStoryDraft against speech timestamps,
    causality, asset availability, and spatial zone occupancy.
    """
    errors: list[DraftValidationError] = []
    approved_facts = approved_facts or {}
    word_timestamps = word_timestamps or []
    if available_assets is not None and not isinstance(available_assets, set):
        available_assets = set(available_assets)

    # ----------------------------------------------------
    # Check: Minimum Visual Density & Event Cadence (Fixed Budget Rule 1)
    # ----------------------------------------------------
    if total_duration_ms is not None and total_duration_ms >= 45000:
        duration_seconds = total_duration_ms / 1000.0
        # Under Rule 1, fixed budget targets 50-60 objects and 90-100 visual refresh events.
        # Required floor caps at 70 regardless of audio length, ensuring long videos aren't over-burdened.
        min_required_events = min(70, math.floor(duration_seconds / 3.0))
        actual_events = len(draft.events)
        if actual_events < min_required_events:
            errors.append(
                DraftValidationError(
                    code="LOW_VISUAL_DENSITY",
                    message=(
                        f"Visual choreography is under-populated: draft contains {actual_events} events for {round(duration_seconds)}s narration, "
                        f"falling below the mandatory minimum of {min_required_events} events (Rule 1 target: 90–100 visual refresh events across 50–60 objects). "
                        f"Author additional choreography across sentences (secondary cards, documentary photos, charts, badges/visual states, number transforms, character pose changes, causal connectors) to maintain high visual pacing."
                    ),
                    details={
                        "actual_events": actual_events,
                        "required_events": min_required_events,
                        "duration_seconds": round(duration_seconds),
                    },
                )
            )

    # ----------------------------------------------------
    # Check: Word Timestamps Integrity
    # ----------------------------------------------------
    prev_start_ms = -1
    for i, ts in enumerate(word_timestamps):
        start = ts.get("start_ms", 0)
        end = ts.get("end_ms", 0)
        word = ts.get("word", "")

        if start < 0:
            errors.append(
                DraftValidationError(
                    code="NEGATIVE_TIMESTAMP",
                    message=f"Word '{word}' at index {i} has negative start_ms ({start}ms).",
                    details={"index": i, "word": word, "start_ms": start},
                )
            )

        if end < start:
            errors.append(
                DraftValidationError(
                    code="INVALID_TIMESTAMP_RANGE",
                    message=f"Word '{word}' at index {i} has end_ms ({end}ms) before start_ms ({start}ms).",
                    details={"index": i, "word": word, "start_ms": start, "end_ms": end},
                )
            )

        if start < prev_start_ms:
            errors.append(
                DraftValidationError(
                    code="NON_MONOTONIC_WORD_TIMESTAMPS",
                    message=f"Word '{word}' at index {i} begins at {start}ms, which precedes previous word start ({prev_start_ms}ms).",
                    details={"index": i, "word": word, "start_ms": start, "prev_start_ms": prev_start_ms},
                )
            )
        prev_start_ms = start

        if total_duration_ms is not None and end > total_duration_ms:
            # Skip non-word SSML tags like <break time="400ms"/> from speech timestamp duration errors
            if not (word.startswith("<") and word.endswith(">")):
                errors.append(
                    DraftValidationError(
                        code="TIMESTAMP_EXCEEDS_AUDIO_DURATION",
                        message=f"Word '{word}' at index {i} ends at {end}ms, exceeding audio total_duration_ms ({total_duration_ms}ms).",
                        details={"index": i, "word": word, "end_ms": end, "total_duration_ms": total_duration_ms},
                    )
                )

    # ----------------------------------------------------
    # Check: Duplicate Object IDs & Object Registry
    # ----------------------------------------------------
    seen_ids: set[str] = set()
    object_map: dict[str, Any] = {}

    for obj in draft.objects:
        if obj.id in seen_ids:
            errors.append(
                DraftValidationError(
                    code="DUPLICATE_OBJECT_ID",
                    message=f"Duplicate object ID '{obj.id}' declared in story draft.",
                    target_id=obj.id,
                )
            )
        seen_ids.add(obj.id)
        object_map[obj.id] = obj

    # ----------------------------------------------------
    # Check: Explicit Enter Event for Every Object
    # ----------------------------------------------------
    entered_object_ids = {e.target_id for e in draft.events if e.action == "enter"}
    connected_object_ids = {e.target_id for e in draft.events if e.action == "connect"}

    for obj in draft.objects:
        if obj.type == "connector":
            if obj.id not in entered_object_ids and obj.id not in connected_object_ids:
                errors.append(
                    DraftValidationError(
                        code="MISSING_ENTER_EVENT",
                        message=f"Connector '{obj.id}' declared in draft has no explicit 'connect' or 'enter' event.",
                        target_id=obj.id,
                    )
                )
        else:
            if obj.id not in entered_object_ids:
                errors.append(
                    DraftValidationError(
                        code="MISSING_ENTER_EVENT",
                        message=f"Object '{obj.id}' declared in draft has no explicit 'enter' event. Every object must have an explicit enter event.",
                        target_id=obj.id,
                    )
                )

    # ----------------------------------------------------
    # Check: Object-Level Validation
    # ----------------------------------------------------
    for obj in draft.objects:
        # Check layout is a valid zone
        if obj.layout not in VALID_ZONES:
            errors.append(
                DraftValidationError(
                    code="INVALID_LAYOUT_ZONE",
                    message=f"Object '{obj.id}' specifies invalid layout zone '{obj.layout}'. Valid zones: {sorted(VALID_ZONES)}",
                    target_id=obj.id,
                )
            )

        # Check fact_id exists in approved_facts if approved_facts is non-empty
        if approved_facts and obj.fact_id is not None:
            if obj.fact_id not in approved_facts:
                errors.append(
                    DraftValidationError(
                        code="UNKNOWN_FACT_ID",
                        message=f"Object '{obj.id}' references unknown fact_id '{obj.fact_id}'. Approved facts: {sorted(approved_facts.keys())}",
                        target_id=obj.id,
                        details={"fact_id": obj.fact_id},
                    )
                )
            else:
                if obj.type == "number":
                    fact_val = approved_facts[obj.fact_id].get("value")
                    if not isinstance(fact_val, (int, float)):
                        errors.append(
                            DraftValidationError(
                                code="NON_NUMERIC_FACT",
                                message=f"Standalone number '{obj.id}' references fact '{obj.fact_id}' with non-numeric value: {fact_val}",
                                target_id=obj.id,
                                details={"fact_id": obj.fact_id, "value": fact_val},
                            )
                        )
                elif obj.type == "chart":
                    fact_data = approved_facts[obj.fact_id]
                    has_series = "series" in fact_data and isinstance(fact_data["series"], list) and len(fact_data["series"]) > 0
                    has_segments = "segments" in fact_data and isinstance(fact_data["segments"], list) and len(fact_data["segments"]) > 0
                    if not (has_series or has_segments or obj.series or obj.points):
                        errors.append(
                            DraftValidationError(
                                code="INVALID_CHART_FACT",
                                message=f"Chart '{obj.id}' references fact '{obj.fact_id}' which lacks 'series' or 'segments' data.",
                                target_id=obj.id,
                                details={"fact_id": obj.fact_id},
                            )
                        )

        # Check value_fact_id on cards if approved_facts is non-empty
        if approved_facts and obj.type == "card" and obj.value_fact_id is not None:
            if obj.value_fact_id not in approved_facts:
                errors.append(
                    DraftValidationError(
                        code="UNKNOWN_FACT_ID",
                        message=f"Card '{obj.id}' references unknown value_fact_id '{obj.value_fact_id}'. Approved facts: {sorted(approved_facts.keys())}",
                        target_id=obj.id,
                        details={"value_fact_id": obj.value_fact_id},
                    )
                )
            else:
                fact_val = approved_facts[obj.value_fact_id].get("value")
                if not isinstance(fact_val, (int, float)):
                    errors.append(
                        DraftValidationError(
                            code="NON_NUMERIC_FACT",
                            message=f"Card '{obj.id}' value_fact_id '{obj.value_fact_id}' references non-numeric value: {fact_val}",
                            target_id=obj.id,
                            details={"value_fact_id": obj.value_fact_id, "value": fact_val},
                        )
                    )

        # Check image asset_id against available asset library
        if obj.type == "image":
            if not obj.asset_id or not obj.asset_id.strip():
                if not getattr(obj, "asset_request", None):
                    errors.append(
                        DraftValidationError(
                            code="IMAGE_ASSET_REQUEST_MISSING",
                            message=f"Image '{obj.id}' requires 'asset_request' or 'asset_id'.",
                            target_id=obj.id,
                        )
                    )
                else:
                    errors.append(
                        DraftValidationError(
                            code="IMAGE_ASSET_UNRESOLVED",
                            message=f"Image '{obj.id}' has unresolved asset_request before compilation.",
                            target_id=obj.id,
                        )
                    )
            elif not available_assets:
                errors.append(
                    DraftValidationError(
                        code="EMPTY_AVAILABLE_ASSETS",
                        message=f"Image '{obj.id}' is used, but available_assets list is empty or not provided.",
                        target_id=obj.id,
                    )
                )
            elif obj.asset_id not in available_assets:
                errors.append(
                    DraftValidationError(
                        code="UNKNOWN_ASSET_ID",
                        message=f"Image '{obj.id}' references unknown asset_id '{obj.asset_id}'. Available assets: {sorted(available_assets)}",
                        target_id=obj.id,
                        details={"asset_id": obj.asset_id},
                    )
                )

        # Check stock_video asset_id, layout, and event requirements
        if obj.type == "stock_video":
            if obj.layout != "full_screen":
                errors.append(
                    DraftValidationError(
                        code="STOCK_VIDEO_INVALID_LAYOUT",
                        message=f"stock_video '{obj.id}' layout must be 'full_screen', got '{obj.layout}'.",
                        target_id=obj.id,
                        details={"layout": obj.layout},
                    )
                )

            if not obj.asset_id or not obj.asset_id.strip():
                if not getattr(obj, "asset_request", None):
                    errors.append(
                        DraftValidationError(
                            code="VIDEO_ASSET_REQUEST_MISSING",
                            message=f"stock_video '{obj.id}' requires 'asset_request' or 'asset_id'.",
                            target_id=obj.id,
                        )
                    )
                else:
                    errors.append(
                        DraftValidationError(
                            code="VIDEO_ASSET_UNRESOLVED",
                            message=f"stock_video '{obj.id}' has unresolved asset_request before compilation.",
                            target_id=obj.id,
                        )
                    )
            elif not available_assets:
                errors.append(
                    DraftValidationError(
                        code="EMPTY_AVAILABLE_ASSETS",
                        message=f"stock_video '{obj.id}' is used, but available_assets list is empty or not provided.",
                        target_id=obj.id,
                    )
                )
            elif obj.asset_id not in available_assets:
                errors.append(
                    DraftValidationError(
                        code="UNKNOWN_ASSET_ID",
                        message=f"stock_video '{obj.id}' references unknown asset_id '{obj.asset_id}'. Available assets: {sorted(available_assets)}",
                        target_id=obj.id,
                        details={"asset_id": obj.asset_id},
                    )
                )

            # Check enter and exit events count and transitions
            sv_enters = [e for e in draft.events if e.target_id == obj.id and e.action == "enter"]
            sv_exits = [e for e in draft.events if e.target_id == obj.id and e.action == "exit"]

            if len(sv_enters) != 1:
                errors.append(
                    DraftValidationError(
                        code="STOCK_VIDEO_EVENT_COUNT",
                        message=f"stock_video '{obj.id}' must have exactly one enter event, found {len(sv_enters)}.",
                        target_id=obj.id,
                    )
                )
            elif sv_enters[0].style and sv_enters[0].style != "cut":
                errors.append(
                    DraftValidationError(
                        code="STOCK_VIDEO_INVALID_TRANSITION",
                        message=f"stock_video '{obj.id}' enter event style must be 'cut', got '{sv_enters[0].style}'.",
                        target_id=obj.id,
                    )
                )

            if len(sv_exits) != 1:
                errors.append(
                    DraftValidationError(
                        code="STOCK_VIDEO_EVENT_COUNT",
                        message=f"stock_video '{obj.id}' must have exactly one exit event, found {len(sv_exits)}.",
                        target_id=obj.id,
                    )
                )
            elif sv_exits[0].direction and sv_exits[0].direction != "cut":
                errors.append(
                    DraftValidationError(
                        code="STOCK_VIDEO_INVALID_TRANSITION",
                        message=f"stock_video '{obj.id}' exit event direction must be 'cut', got '{sv_exits[0].direction}'.",
                        target_id=obj.id,
                    )
                )

        # Connector endpoint validation (must target surface elements)
        if obj.type == "connector":
            if obj.from_id not in object_map:
                errors.append(
                    DraftValidationError(
                        code="CONNECTOR_ENDPOINT_NOT_FOUND",
                        message=f"Connector '{obj.id}' references non-existent source 'from_id': '{obj.from_id}'.",
                        target_id=obj.id,
                        details={"from_id": obj.from_id},
                    )
                )
            elif object_map[obj.from_id].type not in SURFACE_TYPES:
                errors.append(
                    DraftValidationError(
                        code="CONNECTOR_ENDPOINT_NOT_SURFACE",
                        message=f"Connector '{obj.id}' source 'from_id' ('{obj.from_id}') must target a surface element, but is '{object_map[obj.from_id].type}'.",
                        target_id=obj.id,
                    )
                )

            if obj.to_id not in object_map:
                errors.append(
                    DraftValidationError(
                        code="CONNECTOR_ENDPOINT_NOT_FOUND",
                        message=f"Connector '{obj.id}' references non-existent target 'to_id': '{obj.to_id}'.",
                        target_id=obj.id,
                        details={"to_id": obj.to_id},
                    )
                )
            elif object_map[obj.to_id].type not in SURFACE_TYPES:
                errors.append(
                    DraftValidationError(
                        code="CONNECTOR_ENDPOINT_NOT_SURFACE",
                        message=f"Connector '{obj.id}' target 'to_id' ('{obj.to_id}') must target a surface element, but is '{object_map[obj.to_id].type}'.",
                        target_id=obj.id,
                    )
                )

    # ----------------------------------------------------
    # Check: Event-Level Validation
    # ----------------------------------------------------
    for event in draft.events:
        if event.target_id not in object_map:
            if event.action == "stamp" and event.target_id == "canvas":
                target_obj = None
            else:
                errors.append(
                    DraftValidationError(
                        code="UNKNOWN_TARGET_ID",
                        message=f"Action '{event.action}' references non-existent target_id '{event.target_id}'.",
                        target_id=event.target_id,
                    )
                )
                continue
        else:
            target_obj = object_map[event.target_id]

        # Check: move destination zone
        if event.action == "move" and event.to not in VALID_ZONES:
            errors.append(
                DraftValidationError(
                    code="INVALID_MOVE_ZONE",
                    message=f"Action 'move' on '{event.target_id}' specifies invalid destination zone '{event.to}'.",
                    target_id=event.target_id,
                )
            )

        # Check: to_fact_id exists in approved_facts if approved_facts is non-empty
        if approved_facts and event.to_fact_id is not None:
            if event.action != "transform_number":
                errors.append(
                    DraftValidationError(
                        code="UNEXPECTED_TO_FACT_ID",
                        message=f"Action '{event.action}' on '{event.target_id}' specifies 'to_fact_id', which is only allowed for 'transform_number'.",
                        target_id=event.target_id,
                    )
                )
            elif event.to_fact_id not in approved_facts:
                errors.append(
                    DraftValidationError(
                        code="UNKNOWN_TO_FACT_ID",
                        message=f"Action '{event.action}' references unknown to_fact_id '{event.to_fact_id}'. Approved facts: {sorted(approved_facts.keys())}",
                        target_id=event.target_id,
                    )
                )
            else:
                target_fact_val = approved_facts[event.to_fact_id].get("value")
                if not isinstance(target_fact_val, (int, float)):
                    errors.append(
                        DraftValidationError(
                            code="NON_NUMERIC_TRANSFORM_FACT",
                            message=f"Action 'transform_number' targets fact '{event.to_fact_id}' with non-numeric value: {target_fact_val}",
                            target_id=event.target_id,
                        )
                    )

        # Check: anchor exists in spoken words
        if not _find_anchor_in_words(event.anchor, word_timestamps):
            errors.append(
                DraftValidationError(
                    code="ANCHOR_NOT_FOUND",
                    message=f"Action '{event.action}' on '{event.target_id}' has anchor '{event.anchor}' which does not match narration words.",
                    target_id=event.target_id,
                    details={"anchor": event.anchor},
                )
            )

        # Check: transform_number targets a card, number, scale, money_stack, or waterfall
        if event.action == "transform_number" and target_obj.type not in ("card", "number", "scale", "money_stack", "waterfall"):
            errors.append(
                DraftValidationError(
                    code="TRANSFORM_TARGET_INVALID",
                    message=f"Action 'transform_number' can only target a 'card', 'number', 'scale', 'money_stack', or 'waterfall' element, but '{target_obj.id}' is a '{target_obj.type}'.",
                    target_id=target_obj.id,
                )
            )

        # Check: connect action targets connector object
        if event.action == "connect" and target_obj.type != "connector":
            errors.append(
                DraftValidationError(
                    code="CONNECT_TARGET_NOT_CONNECTOR",
                    message=f"Action 'connect' can only target a 'connector' primitive, but '{target_obj.id}' is a '{target_obj.type}'.",
                    target_id=target_obj.id,
                )
            )

        # Check: change_visual_state targets a card, character, scale, money_stack, document, waterfall, or capital_flow
        if event.action == "change_visual_state":
            if target_obj.type not in ("card", "character", "scale", "money_stack", "document", "waterfall", "capital_flow"):
                errors.append(
                    DraftValidationError(
                        code="VISUAL_STATE_TARGET_NOT_CARD",
                        message=f"Action 'change_visual_state' can only target a 'card', 'character', 'scale', 'money_stack', 'document', 'waterfall', or 'capital_flow' element, but '{target_obj.id}' is '{target_obj.type}'.",
                        target_id=target_obj.id,
                    )
                )
            if event.badge is not None:
                cleaned_badge = event.badge.strip()
                if not cleaned_badge:
                    errors.append(
                        DraftValidationError(
                            code="EMPTY_BADGE",
                            message=f"Action 'change_visual_state' on '{event.target_id}' specifies an empty badge string.",
                            target_id=event.target_id,
                        )
                    )
                elif len(cleaned_badge) > 30:
                    errors.append(
                        DraftValidationError(
                            code="BADGE_TOO_LONG",
                            message=f"Action 'change_visual_state' on '{event.target_id}' badge '{event.badge}' exceeds 30 characters.",
                            target_id=event.target_id,
                        )
                    )

        # Check: change_pose targets a character and specifies valid pose
        if event.action == "change_pose":
            if target_obj.type != "character":
                errors.append(
                    DraftValidationError(
                        code="CHANGE_POSE_TARGET_NOT_CHARACTER",
                        message=f"Action 'change_pose' can only target a 'character' primitive, but '{target_obj.id}' is a '{target_obj.type}'.",
                        target_id=target_obj.id,
                    )
                )
            if not event.pose or event.pose not in ("idle", "walk", "point", "think", "worried", "celebrate"):
                errors.append(
                    DraftValidationError(
                        code="INVALID_CHARACTER_POSE",
                        message=f"Action 'change_pose' on '{event.target_id}' has invalid pose '{event.pose}'.",
                        target_id=event.target_id,
                    )
                )

        # Check: exit action validates direction if present
        if event.action == "exit" and event.direction and event.direction not in {"left", "right", "up", "down", "fade", "cut"}:
            errors.append(
                DraftValidationError(
                    code="INVALID_EXIT_DIRECTION",
                    message=f"Action 'exit' on '{event.target_id}' has invalid 'direction' ('{event.direction}'). Allowed: ('left', 'right', 'up', 'down', 'fade', 'cut').",
                    target_id=event.target_id,
                )
            )

        # Check: anchor must not be empty
        anchor_tokens = [t for t in re.sub(r"[^\w\.]", " ", event.anchor or "").split() if t]
        if len(anchor_tokens) < 1:
            errors.append(
                DraftValidationError(
                    code="ANCHOR_EMPTY",
                    message=f"Action '{event.action}' on '{event.target_id}' has an empty anchor. Every anchor MUST be at least 1 word.",
                    target_id=event.target_id,
                )
            )

    # ----------------------------------------------------
    # Check: Temporal Causality (Actions After Enter)
    # ----------------------------------------------------
    enter_times_ms: dict[str, int] = {}
    enter_anchors: dict[str, str] = {}
    exit_times_ms: dict[str, int] = {}
    event_resolved_times_ms: list[int | None] = []

    timeline_cursor_ms = 0
    for event in draft.events:
        # Forward-progressing timeline cursor with a 4s grace window for near-simultaneous split events
        search_min = max(0, timeline_cursor_ms - 4000)
        if event.action == "exit" and event.target_id in enter_times_ms:
            search_min = max(search_min, enter_times_ms[event.target_id])
        elif event.action == "connect":
            target_obj_conn = object_map.get(event.target_id)
            if target_obj_conn and target_obj_conn.type == "connector":
                search_min = max(
                    search_min,
                    enter_times_ms.get(target_obj_conn.from_id, 0),
                    enter_times_ms.get(target_obj_conn.to_id, 0),
                )

        t_ms = _get_anchor_start_ms(event.anchor, word_timestamps, min_start_ms=search_min)
        if t_ms is None:
            t_ms = _get_anchor_start_ms(event.anchor, word_timestamps, min_start_ms=0)

        event_resolved_times_ms.append(t_ms)
        if t_ms is not None:
            timeline_cursor_ms = max(timeline_cursor_ms, t_ms)
            if event.action in ("enter", "connect"):
                if event.target_id not in enter_times_ms:
                    enter_times_ms[event.target_id] = t_ms
                    enter_anchors[event.target_id] = event.anchor
            elif event.action == "exit":
                exit_times_ms[event.target_id] = t_ms

    current_exited: set[str] = set()

    for idx, event in enumerate(draft.events):
        event_time_ms = event_resolved_times_ms[idx]
        if event_time_ms is None or event.target_id not in object_map:
            continue

        target_obj = object_map[event.target_id]
        enter_t = enter_times_ms.get(event.target_id)

        if event.action == "enter":
            current_exited.discard(event.target_id)

        elif event.action in ("move", "highlight", "change_visual_state", "transform_number", "transform_text", "change_pose", "stamp"):
            if enter_t is None:
                errors.append(
                    DraftValidationError(
                        code="ACTION_BEFORE_OBJECT_ENTER",
                        message=f"Action '{event.action}' on '{event.target_id}' occurs at {event_time_ms}ms ('{event.anchor}'), but '{event.target_id}' never enters.",
                        target_id=event.target_id,
                    )
                )
            elif event_time_ms < enter_t:
                orig_enter_anchor = enter_anchors.get(event.target_id, "")
                errors.append(
                    DraftValidationError(
                        code="ACTION_BEFORE_OBJECT_ENTER",
                        message=f"Action '{event.action}' on '{event.target_id}' occurs at {event_time_ms}ms, before its enter time ({enter_t}ms, enter anchor: '{orig_enter_anchor}').",
                        target_id=event.target_id,
                        details={
                            "action": event.action,
                            "target_id": event.target_id,
                            "event_anchor": event.anchor,
                            "event_time_ms": event_time_ms,
                            "enter_anchor": orig_enter_anchor,
                            "enter_time_ms": enter_t,
                        },
                    )
                )

            # Rule 8: If character (or object) exits, cannot receive actions after exit unless re-entered
            exit_t = exit_times_ms.get(event.target_id)
            if event.target_id in current_exited or (exit_t is not None and event_time_ms > exit_t):
                errors.append(
                    DraftValidationError(
                        code="ACTION_AFTER_OBJECT_EXIT",
                        message=f"Action '{event.action}' on '{event.target_id}' occurs at {event_time_ms}ms, after the object has exited at {exit_t or event_time_ms}ms.",
                        target_id=event.target_id,
                        details={"event_time_ms": event_time_ms, "exit_time_ms": exit_t or event_time_ms},
                    )
                )

        elif event.action == "exit":
            current_exited.add(event.target_id)
            if enter_t is None:
                errors.append(
                    DraftValidationError(
                        code="ACTION_BEFORE_OBJECT_ENTER",
                        message=f"Action 'exit' on '{event.target_id}' occurs at {event_time_ms}ms, but '{event.target_id}' never enters.",
                        target_id=event.target_id,
                    )
                )
            elif event_time_ms <= enter_t:
                orig_enter_anchor = enter_anchors.get(event.target_id, "")
                errors.append(
                    DraftValidationError(
                        code="EXIT_BEFORE_OBJECT_ENTER",
                        message=(
                            f"Action 'exit' on '{event.target_id}' occurs at {event_time_ms}ms (exit anchor: '{event.anchor}'), "
                            f"which is before or at its original enter anchor '{orig_enter_anchor}' at {enter_t}ms. "
                            f"An exit anchor must occur strictly after the target object's enter anchor."
                        ),
                        target_id=event.target_id,
                        details={
                            "target_id": event.target_id,
                            "exit_anchor": event.anchor,
                            "exit_time_ms": event_time_ms,
                            "enter_anchor": orig_enter_anchor,
                            "enter_time_ms": enter_t,
                        },
                    )
                )

        elif event.action == "connect" or (event.action == "enter" and target_obj.type == "connector"):
            from_card = target_obj.from_id
            to_card = target_obj.to_id
            from_enter_t = enter_times_ms.get(from_card)
            to_enter_t = enter_times_ms.get(to_card)

            if from_enter_t is None or event_time_ms < from_enter_t:
                orig_enter = enter_anchors.get(from_card, "")
                errors.append(
                    DraftValidationError(
                        code="CONNECT_BEFORE_CARDS_ENTER",
                        message=(
                            f"Connector '{event.target_id}' connects at {event_time_ms}ms (anchor: '{event.anchor}'), "
                            f"but source '{from_card}' enters at {from_enter_t}ms (enter anchor: '{orig_enter}')."
                        ),
                        target_id=event.target_id,
                        details={
                            "endpoint_role": "source",
                            "endpoint_id": from_card,
                            "endpoint_enter_time_ms": from_enter_t,
                            "endpoint_enter_anchor": orig_enter,
                            "connect_time_ms": event_time_ms,
                            "connect_anchor": event.anchor,
                        },
                    )
                )
            if to_enter_t is None or event_time_ms < to_enter_t:
                orig_enter = enter_anchors.get(to_card, "")
                errors.append(
                    DraftValidationError(
                        code="CONNECT_BEFORE_CARDS_ENTER",
                        message=(
                            f"Connector '{event.target_id}' connects at {event_time_ms}ms (anchor: '{event.anchor}'), "
                            f"but target '{to_card}' enters at {to_enter_t}ms (enter anchor: '{orig_enter}')."
                        ),
                        target_id=event.target_id,
                        details={
                            "endpoint_role": "target",
                            "endpoint_id": to_card,
                            "endpoint_enter_time_ms": to_enter_t,
                            "endpoint_enter_anchor": orig_enter,
                            "connect_time_ms": event_time_ms,
                            "connect_anchor": event.anchor,
                        },
                    )
                )

    # ----------------------------------------------------
    # Check: Mandatory Exit Events for Surface Objects
    # ----------------------------------------------------
    exited_target_ids = {e.target_id for e in draft.events if e.action == "exit"}

    for obj in draft.objects:
        if obj.type not in SURFACE_TYPES:
            continue
        if obj.type == "stock_video":
            continue  # stock_video exit is checked in STOCK_VIDEO_EVENT_COUNT

        obj_enter_ms = enter_times_ms.get(obj.id)
        if obj_enter_ms is None:
            continue

        has_exit = obj.id in exited_target_ids

        # Check A: Preceding full_screen canvas elements (e.g. backdrop image) must have explicit exit
        # Note: stock_video is a Cutaway B-Roll Layer outside the canvas and does NOT require canvas elements to exit.
        for fs_obj in draft.objects:
            if fs_obj.id != obj.id and fs_obj.layout == "full_screen" and fs_obj.type != "stock_video":
                fs_enter_ms = enter_times_ms.get(fs_obj.id)
                if fs_enter_ms is not None and fs_enter_ms > obj_enter_ms:
                    if not has_exit:
                        errors.append(
                            DraftValidationError(
                                code="MISSING_EXIT_BEFORE_FULLSCREEN",
                                message=(
                                    f"Surface '{obj.id}' enters at {obj_enter_ms}ms but has no explicit 'exit' event "
                                    f"before full_screen '{fs_obj.id}' enters at {fs_enter_ms}ms. "
                                    f"Every foreground visual preceding a full-screen cutaway MUST have an explicit exit event."
                                ),
                                target_id=obj.id,
                                details={
                                    "target_id": obj.id,
                                    "enter_time_ms": obj_enter_ms,
                                    "fullscreen_id": fs_obj.id,
                                    "fullscreen_enter_ms": fs_enter_ms,
                                },
                            )
                        )
                        break
                    else:
                        obj_exit_ms = exit_times_ms.get(obj.id)
                        if obj_exit_ms is not None and obj_exit_ms > fs_enter_ms:
                            errors.append(
                                DraftValidationError(
                                    code="EXIT_AFTER_FULLSCREEN_ENTER",
                                    message=(
                                        f"Surface '{obj.id}' exits at {obj_exit_ms}ms, which is after full_screen "
                                        f"'{fs_obj.id}' enters at {fs_enter_ms}ms. "
                                        f"Preceding foreground visuals must exit on or before the full-screen cutaway."
                                    ),
                                    target_id=obj.id,
                                    details={
                                        "target_id": obj.id,
                                        "exit_time_ms": obj_exit_ms,
                                        "fullscreen_id": fs_obj.id,
                                        "fullscreen_enter_ms": fs_enter_ms,
                                    },
                                )
                            )
                            break

    # ----------------------------------------------------
    # Check: Temporal Spatial Zone Occupancy (Collision Prevention)
    # ----------------------------------------------------
    # Build lifecycle intervals for each surface element
    # Interval: (start_ms, end_ms, zone)
    element_intervals: dict[str, list[tuple[int, int, str]]] = {}

    for obj in draft.objects:
        if obj.type not in SURFACE_TYPES:
            continue  # Connectors do not occupy zones

        enter_t = enter_times_ms.get(obj.id)
        if enter_t is None:
            continue

        exit_t = exit_times_ms.get(obj.id)
        exit_ev = next((e for e in draft.events if e.target_id == obj.id and e.action == "exit"), None)
        is_cut_exit = obj.type == "stock_video" or (exit_ev and exit_ev.direction == "cut")
        exit_clearance_ms = 0 if is_cut_exit else EXIT_DURATION_MS
        full_end_t = (exit_t + exit_clearance_ms) if exit_t is not None else (total_duration_ms or 999999)

        # Sequential zone handoff: if incumbent element in an exclusive zone (full_screen, full_bottom)
        # has an explicit exit that overlaps the next element entering that zone by <= 2000ms,
        # clamp incumbent's end time to the incoming element's enter time to achieve a clean cut transition.
        if exit_t is not None and obj.layout in ("full_screen", "full_bottom"):
            for other_obj in draft.objects:
                if other_obj.id != obj.id and other_obj.layout == obj.layout:
                    other_enter_t = enter_times_ms.get(other_obj.id)
                    if other_enter_t is not None and other_enter_t > enter_t:
                        if full_end_t > other_enter_t and (full_end_t - other_enter_t) <= 2000:
                            full_end_t = other_enter_t

        # If an unexited foreground surface element entered before a full_screen canvas element (e.g. backdrop image),
        # the full_screen element naturally terminates/eclipses the preceding foreground element.
        if exit_t is None and obj.layout != "full_screen" and obj.type != "stock_video":
            earliest_fs_ms = None
            for other_obj in draft.objects:
                if other_obj.id != obj.id and other_obj.layout == "full_screen" and other_obj.type != "stock_video":
                    other_enter_t = enter_times_ms.get(other_obj.id)
                    if other_enter_t is not None and other_enter_t > enter_t:
                        if earliest_fs_ms is None or other_enter_t < earliest_fs_ms:
                            earliest_fs_ms = other_enter_t
            if earliest_fs_ms is not None:
                full_end_t = min(full_end_t, earliest_fs_ms)

        # Check for moves to track zone transitions over time
        moves_for_obj: list[tuple[int, str]] = []
        for idx, event in enumerate(draft.events):
            if event.action == "move" and event.target_id == obj.id and event.to:
                m_t = event_resolved_times_ms[idx]
                if m_t is not None:
                    moves_for_obj.append((m_t, event.to))
        moves_for_obj.sort(key=lambda m: m[0])

        # Interval: (start_ms, end_ms, zone, geom)
        obj_width = getattr(obj, "width", None) if not isinstance(obj, dict) else obj.get("width")
        obj_height = getattr(obj, "height", None) if not isinstance(obj, dict) else obj.get("height")

        current_zone = obj.layout
        current_start = enter_t

        for move_t, next_zone in moves_for_obj:
            if move_t > current_start and move_t < full_end_t:
                if current_zone in VALID_ZONES:
                    geom = _resolve_obj_geometry(obj.type, current_zone, obj_width, obj_height)
                    element_intervals.setdefault(obj.id, []).append((current_start, move_t, current_zone, geom))
                current_zone = next_zone
                current_start = move_t

        if current_zone in VALID_ZONES:
            geom = _resolve_obj_geometry(obj.type, current_zone, obj_width, obj_height)
            element_intervals.setdefault(obj.id, []).append((current_start, full_end_t, current_zone, geom))

    # Check center divider crossing and subtitle clearance (Requirement 8 & D)
    for obj_id, intervals in element_intervals.items():
        for s, e, z, (x, y, w, h) in intervals:
            if z == "split_left" and (x + w > 960 or x < 0):
                errors.append(
                    DraftValidationError(
                        code="DIVIDER_CROSSING_COLLISION",
                        message=(
                            f"Surface element '{obj_id}' in 'split_left' has bounding box crossing the center divider at x=960 "
                            f"(x={x}, width={w}, right={x + w})."
                        ),
                        target_id=obj_id,
                        details={"zone": "split_left", "x": x, "width": w, "right": x + w, "divider": 960},
                    )
                )
            elif z == "split_right" and (x < 960 or x + w > 1920):
                errors.append(
                    DraftValidationError(
                        code="DIVIDER_CROSSING_COLLISION",
                        message=(
                            f"Surface element '{obj_id}' in 'split_right' has bounding box crossing the center divider at x=960 "
                            f"(x={x}, left={x})."
                        ),
                        target_id=obj_id,
                        details={"zone": "split_right", "x": x, "divider": 960},
                    )
                )

            # Subtitle clearance check
            if z == "full_bottom" and h > 280:
                errors.append(
                    DraftValidationError(
                        code="SUBTITLE_OVERLAP",
                        message=(
                            f"Surface element '{obj_id}' in 'full_bottom' has height {h}px exceeding maximum 280px, "
                            f"encroaching into subtitle space."
                        ),
                        target_id=obj_id,
                        details={"height": h, "max_height": 280},
                    )
                )
            if z != "full_screen" and y + h > 960:
                errors.append(
                    DraftValidationError(
                        code="SUBTITLE_OVERLAP",
                        message=(
                            f"Surface element '{obj_id}' bottom edge at y={y + h} encroaches on the subtitle display area "
                            f"(must remain at or above 960px)."
                        ),
                        target_id=obj_id,
                        details={"bottom_y": y + h, "max_allowed_y": 960},
                    )
                )

    # Compare pairwise intervals for spatial collisions
    object_ids = list(element_intervals.keys())
    for idx1 in range(len(object_ids)):
        for idx2 in range(idx1 + 1, len(object_ids)):
            id1 = object_ids[idx1]
            id2 = object_ids[idx2]

            for s1, e1, z1, g1 in element_intervals[id1]:
                for s2, e2, z2, g2 in element_intervals[id2]:
                    # Check temporal overlap
                    overlap_start = max(s1, s2)
                    overlap_end = min(e1, e2)
                    if overlap_start < overlap_end:
                        # 1. Direct zone match
                        if z1 == z2:
                            if z1 in ("full_screen", "full_bottom"):
                                errors.append(
                                    DraftValidationError(
                                        code="ZONE_OCCUPANCY_COLLISION",
                                        message=(
                                            f"Spatial collision in zone '{z1}': element '{id2}' overlaps with '{id1}' "
                                            f"between {overlap_start}ms and {overlap_end}ms. Exclusive zone '{z1}' only allows 1 element."
                                        ),
                                        target_id=id2,
                                        details={
                                            "zone": z1,
                                            "colliding_with": id1,
                                            "start_ms": overlap_start,
                                            "end_ms": overlap_end,
                                            "element_1": id1,
                                            "element_2": id2,
                                        },
                                    )
                                )
                            else:
                                # For split_left, split_right, and center: Remotion Dynamic AutoLayout supports up to 4 concurrent elements (vertical stack with progressive size reduction)
                                concurrent_in_zone = set()
                                for check_id, check_intervals in element_intervals.items():
                                    for cs, ce, cz, _ in check_intervals:
                                        if cz == z1 and max(cs, overlap_start) < min(ce, overlap_end):
                                            concurrent_in_zone.add(check_id)
                                if len(concurrent_in_zone) > 4:
                                    errors.append(
                                        DraftValidationError(
                                            code="ZONE_OCCUPANCY_COLLISION",
                                            message=(
                                                f"Spatial collision in zone '{z1}': {len(concurrent_in_zone)} elements "
                                                f"({sorted(concurrent_in_zone)}) occupy zone '{z1}' simultaneously between "
                                                f"{overlap_start}ms and {overlap_end}ms. Zone '{z1}' supports at most 4 simultaneous elements."
                                            ),
                                            target_id=id2,
                                            details={
                                                "zone": z1,
                                                "concurrent_elements": sorted(concurrent_in_zone),
                                                "start_ms": overlap_start,
                                                "end_ms": overlap_end,
                                                "element_1": id1,
                                                "element_2": id2,
                                            },
                                        )
                                    )
                        # 2. Macro layout conflicts
                        elif z1 in MACRO_ZONE_CONFLICTS and z2 in MACRO_ZONE_CONFLICTS[z1]:
                            errors.append(
                                DraftValidationError(
                                    code="MACRO_LAYOUT_COLLISION",
                                    message=(
                                        f"Macro layout collision: '{id1}' in macro '{z1}' overlaps with '{id2}' in '{z2}' "
                                        f"between {overlap_start}ms and {overlap_end}ms."
                                    ),
                                    target_id=id1,
                                    details={
                                        "macro_zone": z1,
                                        "conflicting_zone": z2,
                                        "colliding_with": id2,
                                        "start_ms": overlap_start,
                                        "end_ms": overlap_end,
                                        "element_1": id1,
                                        "element_2": id2,
                                    },
                                )
                            )
                        elif z2 in MACRO_ZONE_CONFLICTS and z1 in MACRO_ZONE_CONFLICTS[z2]:
                            errors.append(
                                DraftValidationError(
                                    code="MACRO_LAYOUT_COLLISION",
                                    message=(
                                        f"Macro layout collision: '{id2}' in macro '{z2}' overlaps with '{id1}' in '{z1}' "
                                        f"between {overlap_start}ms and {overlap_end}ms."
                                    ),
                                    target_id=id2,
                                    details={
                                        "macro_zone": z2,
                                        "conflicting_zone": z1,
                                        "colliding_with": id1,
                                        "start_ms": overlap_start,
                                        "end_ms": overlap_end,
                                        "element_1": id2,
                                        "element_2": id1,
                                    },
                                )
                            )

                        # 3. Geometric AABB Collision between distinct non-fullscreen surfaces
                        if z1 != z2 and z1 != "full_screen" and z2 != "full_screen":
                            # Dynamic Auto-Layout Living Canvas accommodates complementary zone pairings
                            fb_is_valid = True
                            fb_h = 0
                            if "full_bottom" in (z1, z2):
                                fb_h = g1[3] if z1 == "full_bottom" else g2[3]
                                fb_is_valid = fb_h <= 280

                            is_complementary = (
                                {z1, z2} in (
                                    {"center", "split_left"},
                                    {"center", "split_right"},
                                    {"split_left", "split_right"},
                                )
                                or (
                                    ("full_bottom" in (z1, z2))
                                    and bool({z1, z2} & {"center", "split_left", "split_right"})
                                    and fb_is_valid
                                )
                            )
                            if not is_complementary:
                                if "full_bottom" in (z1, z2) and not fb_is_valid:
                                    errors.append(
                                        DraftValidationError(
                                            code="CARD_OVERLAP",
                                            message=(
                                                f"Element in 'full_bottom' exceeds vertical budget (height {round(fb_h)}px > 280px) "
                                                f"between {overlap_start}ms and {overlap_end}ms."
                                            ),
                                            target_id=id2,
                                            details={
                                                "id1": id1,
                                                "id2": id2,
                                                "zone1": z1,
                                                "zone2": z2,
                                                "start_ms": overlap_start,
                                                "end_ms": overlap_end,
                                            },
                                        )
                                    )
                                else:
                                    x1, y1, w1, h1 = g1
                                    x2, y2, w2, h2 = g2
                                    x_overlap = max(0, min(x1 + w1, x2 + w2) - max(x1, x2))
                                    y_overlap = max(0, min(y1 + h1, y2 + h2) - max(y1, y2))
                                    if x_overlap > 0 and y_overlap > 0:
                                        errors.append(
                                            DraftValidationError(
                                                code="CARD_OVERLAP",
                                                message=(
                                                    f"Spatial bounding box overlap between '{id1}' and '{id2}' ({round(x_overlap)}x{round(y_overlap)}px) "
                                                    f"in zones '{z1}' and '{z2}' between {overlap_start}ms and {overlap_end}ms."
                                                ),
                                                target_id=id2,
                                                details={
                                                    "id1": id1,
                                                    "id2": id2,
                                                    "zone1": z1,
                                                    "zone2": z2,
                                                    "x_overlap": x_overlap,
                                                    "y_overlap": y_overlap,
                                                    "start_ms": overlap_start,
                                                    "end_ms": overlap_end,
                                                },
                                            )
                                        )

    # Check: Stock video cutaways cannot overlap with each other (Cutaway Layer mutual exclusivity)
    stock_videos = [o for o in draft.objects if o.type == "stock_video"]
    for i in range(len(stock_videos)):
        for j in range(i + 1, len(stock_videos)):
            sv1 = stock_videos[i]
            sv2 = stock_videos[j]
            s1, e1 = enter_times_ms.get(sv1.id), exit_times_ms.get(sv1.id)
            s2, e2 = enter_times_ms.get(sv2.id), exit_times_ms.get(sv2.id)
            if s1 is not None and e1 is not None and s2 is not None and e2 is not None:
                overlap_start = max(s1, s2)
                overlap_end = min(e1, e2)
                if overlap_start < overlap_end:
                    errors.append(
                        DraftValidationError(
                            code="STOCK_VIDEO_OVERLAP_COLLISION",
                            message=(
                                f"Stock video cutaway '{sv1.id}' overlaps with '{sv2.id}' between "
                                f"{overlap_start}ms and {overlap_end}ms. Only one cutaway video can play at a time."
                            ),
                            target_id=sv2.id,
                            details={
                                "sv1": sv1.id,
                                "sv2": sv2.id,
                                "overlap_start_ms": overlap_start,
                                "overlap_end_ms": overlap_end,
                            },
                        )
                    )

    return DraftValidationResult(valid=len(errors) == 0, errors=errors)
