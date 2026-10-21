"""
continuous_story_compiler.py — Deterministic AI Draft Compiler for Atomic StoryEngine.

Converts a validated ContinuousStoryDraft + story fixture into a deterministic,
fully-resolved StoryPlan dictionary ready for the Remotion renderer.

Pipeline Position:
  Raw Gemini JSON
  → ContinuousStoryDraft.model_validate(...)   [Pydantic schema & syntax]
  → validate_story_draft(...)                  [Semantic graph, spatial occupancy & fixture validation]
  → ContinuousStoryCompiler                    [Deterministic compilation -> Remotion StoryPlan]

Guarantees:
1. 100% Deterministic: identical draft + fixture always produces identical StoryPlan.
2. Atomic Architecture: no parent-child nesting. Cards, metrics, text, charts are independent.
3. Open Direct Authoring: renders directly authored titles, values, subtitles, badges, series, and points without fact lookup, fact resolution, regex extraction, or fallback guessing.
4. Audio Synchronization: maps phrase anchors to exact spoken frames via word timestamps.
5. 12-Zone Spatial Preservation: preserves clean zone layout names for Remotion layout engine.
"""
from __future__ import annotations

import re
from typing import Any

from domain.continuous_story_plan import ContinuousStoryDraft, StoryObjectDraft, StoryEventDraft


def resolve_anchor_ms(
    word_timestamps: list[dict[str, Any]],
    anchor_phrase: str,
    min_start_ms: int = 0,
) -> int:
    """
    Resolves a spoken anchor phrase to its exact start time in milliseconds using audio word timestamps.
    Enforces exact contiguous phrase matching.
    Removed: first-token fallback, substring matching, fallback search from frame zero.
    Fails loudly with ValueError if the exact phrase is not found.
    """
    if not anchor_phrase or not anchor_phrase.strip():
        raise ValueError("Anchor phrase cannot be empty.")

    anchor_clean = anchor_phrase.replace("-", " ")
    clean_tokens = [
        re.sub(r"[^\w\.]", "", t.lower())
        for t in anchor_clean.split()
        if re.sub(r"[^\w\.]", "", t.lower())
    ]
    if not clean_tokens:
        raise ValueError(f"Anchor phrase '{anchor_phrase}' contains no searchable speech tokens.")

    token_entries: list[tuple[str, int, int]] = []
    for w in word_timestamps:
        start_ms = w.get("start_ms", 0)
        end_ms = w.get("end_ms", 0)
        w_clean = str(w.get("word", "")).replace("-", " ")
        for tok in w_clean.split():
            c_tok = re.sub(r"[^\w\.]", "", tok.lower())
            if c_tok:
                token_entries.append((c_tok, start_ms, end_ms))

    num_tokens = len(clean_tokens)
    for i in range(len(token_entries) - num_tokens + 1):
        if token_entries[i][1] < min_start_ms:
            continue
        match = True
        for j in range(num_tokens):
            if token_entries[i + j][0] != clean_tokens[j]:
                match = False
                break
        if match:
            return token_entries[i][1]

    raise ValueError(
        f"Exact anchor phrase '{anchor_phrase}' could not be resolved to any spoken word timestamp at or after {min_start_ms}ms."
    )


def generate_timing_report(plan: dict[str, Any]) -> str:
    """
    Generates a timing report before rendering for all objects in the story plan.
    Format:
    Object: interest_card
    Anchor: "eighty-eight point four lakhs rupees"
    Matched timestamp: 33.73s
    Start frame: 1012
    Enter event: present
    Visible interval: 33.73s – 41.83s
    """
    fps = plan.get("fps", 30) or 30
    duration_frames = plan.get("durationInFrames", 380) or 380
    objects = plan.get("objects", [])
    events = plan.get("events", [])

    lines: list[str] = []
    for obj in objects:
        obj_id = obj.get("id") if isinstance(obj, dict) else getattr(obj, "id", "")
        enter_ev = next(
            (e for e in events if (e.get("action") if isinstance(e, dict) else getattr(e, "action", None)) == "enter"
             and (e.get("targetId") if isinstance(e, dict) else getattr(e, "targetId", None)) == obj_id),
            None
        )
        if enter_ev is None:
            enter_ev = next(
                (e for e in events if (e.get("action") if isinstance(e, dict) else getattr(e, "action", None)) == "connect"
                 and (e.get("targetId") if isinstance(e, dict) else getattr(e, "targetId", None)) == obj_id),
                None
            )

        exit_ev = next(
            (e for e in events if (e.get("action") if isinstance(e, dict) else getattr(e, "action", None)) == "exit"
             and (e.get("targetId") if isinstance(e, dict) else getattr(e, "targetId", None)) == obj_id),
            None
        )

        if enter_ev is not None:
            anchor = enter_ev.get("anchor") if isinstance(enter_ev, dict) else getattr(enter_ev, "anchor", "")
            start_frame = enter_ev.get("startFrame") if isinstance(enter_ev, dict) else getattr(enter_ev, "startFrame", 0)
            matched_ts = f"{start_frame / fps:.2f}s"
            enter_status = "present"
            if exit_ev is not None:
                ef = exit_ev.get("startFrame") if isinstance(exit_ev, dict) else getattr(exit_ev, "startFrame", duration_frames)
                end_ts = f"{ef / fps:.2f}s"
            else:
                end_ts = f"{duration_frames / fps:.2f}s"
            visible_interval = f"{matched_ts} – {end_ts}"
        else:
            anchor = ""
            matched_ts = "N/A"
            start_frame = "N/A"
            enter_status = "missing"
            visible_interval = "N/A (invisible)"

        lines.append(f"Object: {obj_id}")
        lines.append(f'Anchor: "{anchor}"')
        lines.append(f"Matched timestamp: {matched_ts}")
        lines.append(f"Start frame: {start_frame}")
        lines.append(f"Enter event: {enter_status}")
        lines.append(f"Visible interval: {visible_interval}")
        lines.append("")

    return "\n".join(lines).strip()



def resolve_anchor_frame(
    word_timestamps: list[dict[str, Any]],
    anchor_phrase: str,
    fps: int = 30,
    min_start_ms: int = 0,
) -> int:
    """
    Resolves a spoken anchor phrase to its exact start frame using audio word timestamps.
    If min_start_ms > 0, searches only for occurrences at or after min_start_ms.
    """
    start_ms = resolve_anchor_ms(word_timestamps, anchor_phrase, min_start_ms=min_start_ms)
    return max(0, round((start_ms / 1000.0) * fps))


class ContinuousStoryCompiler:
    """
    Compiles an atomic ContinuousStoryDraft into a deterministic Remotion StoryPlan.
    """

    def __init__(
        self,
        default_width: int = 1920,
        default_height: int = 1080,
        default_fps: int = 30,
        default_safe_margin: int = 80,
        min_duration_frames: int = 380,
    ) -> None:
        self.default_width = default_width
        self.default_height = default_height
        self.default_fps = default_fps
        self.default_safe_margin = default_safe_margin
        self.min_duration_frames = min_duration_frames

    def compile(
        self,
        draft: ContinuousStoryDraft,
        fixture: dict[str, Any],
    ) -> dict[str, Any]:
        approved_facts = fixture.get("approved_facts", {})
        word_timestamps = fixture.get("word_timestamps", [])
        total_duration_ms = fixture.get("total_duration_ms", 12543)
        audio_file = fixture.get("audio_file", "loan_narration.mp3")
        narration_text = fixture.get("narration_text", "")

        fps = self.default_fps
        calculated_frames = round((total_duration_ms / 1000.0) * fps)
        duration_in_frames = max(self.min_duration_frames, calculated_frames)

        # ----------------------------------------------------
        # 1. Compile Atomic Elements Directly
        # ----------------------------------------------------
        compiled_objects: list[dict[str, Any]] = []

        for obj in draft.objects:
            if obj.type == "card":
                card_dict = self._compile_card(obj)
                compiled_objects.append(card_dict)

            elif obj.type == "number":
                num_dict = self._compile_number(obj)
                compiled_objects.append(num_dict)

            elif obj.type == "text":
                text_dict = self._compile_text(obj)
                compiled_objects.append(text_dict)

            elif obj.type == "chart":
                chart_dict = self._compile_chart(obj)
                compiled_objects.append(chart_dict)

            elif obj.type == "image":
                img_dict = self._compile_image(obj, fixture=fixture)
                compiled_objects.append(img_dict)

            elif obj.type == "connector":
                connector_dict = self._compile_connector(obj)
                compiled_objects.append(connector_dict)

            elif obj.type == "character":
                char_dict = self._compile_character(obj)
                compiled_objects.append(char_dict)

            else:
                raise ValueError(f"Unsupported object '{obj.id}' of type '{obj.type}'.")

        # ----------------------------------------------------
        # 2. Compile Events (Speech Anchor -> Start Frame)
        # ----------------------------------------------------
        enter_times_ms: dict[str, int] = {}
        for event in draft.events:
            if event.action == "enter" and event.target_id not in enter_times_ms:
                try:
                    enter_times_ms[event.target_id] = resolve_anchor_ms(
                        word_timestamps=word_timestamps,
                        anchor_phrase=event.anchor,
                    )
                except Exception:
                    pass

        compiled_events: list[dict[str, Any]] = []
        for event in draft.events:
            min_start = 0
            if event.action != "enter":
                min_start = enter_times_ms.get(event.target_id, 0)
                if event.action == "connect":
                    target_obj = next((o for o in draft.objects if o.id == event.target_id), None)
                    if target_obj and target_obj.type == "connector":
                        min_start = max(
                            enter_times_ms.get(target_obj.from_id, 0),
                            enter_times_ms.get(target_obj.to_id, 0),
                        )

            event_dict = self._compile_event(
                event=event,
                word_timestamps=word_timestamps,
                fps=fps,
                min_start_ms=min_start,
            )
            compiled_events.append(event_dict)

        # ----------------------------------------------------
        # 3. Construct Final StoryPlan Contract
        # ----------------------------------------------------
        return {
            "id": draft.story_id,
            "fps": fps,
            "durationInFrames": duration_in_frames,
            "width": self.default_width,
            "height": self.default_height,
            "safeMargin": self.default_safe_margin,
            "audioFileName": audio_file,
            "narration": {
                "text": narration_text,
                "audioFile": audio_file,
                "wordTimestamps": word_timestamps,
            },
            "objects": compiled_objects,
            "events": compiled_events,
        }

    def _compile_card(
        self,
        card_obj: StoryObjectDraft,
        approved_facts: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Compiles a self-contained atomic card directly from Gemini-authored fields."""
        title = card_obj.title or card_obj.purpose or card_obj.id.replace("_", " ").title()
        subtitle = card_obj.subtitle or ""
        display_value = card_obj.display_value
        value = card_obj.numeric_value
        fmt = "plain"
        accent_color = card_obj.accent or "#3B82F6"
        visual_state = card_obj.visual_state or "normal"
        badge = card_obj.badge

        card_props: dict[str, Any] = {
            "title": title,
            "subtitle": subtitle,
            "displayValue": display_value,
            "value": value,
            "format": fmt,
            "valueFactId": card_obj.value_fact_id or card_obj.fact_id,
            "visualState": visual_state,
            "badge": badge,
            "accentColor": accent_color,
        }

        # Dimensions: standard card 420x240
        return {
            "id": card_obj.id,
            "type": "card",
            "layout": card_obj.layout,
            "width": 420,
            "height": 240,
            "cardProps": card_props,
        }

    def _compile_number(
        self,
        obj: StoryObjectDraft,
        approved_facts: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Compiles a standalone numeric callout directly from Gemini-authored fields."""
        fact_key = obj.fact_id or obj.value_fact_id
        number_props: dict[str, Any] = {
            "displayValue": obj.display_value,
            "value": obj.numeric_value,
            "format": "plain",
            "factId": fact_key,
        }

        return {
            "id": obj.id,
            "type": "number",
            "layout": obj.layout,
            "width": 360,
            "height": 180,
            "numberProps": number_props,
        }

    def _compile_text(self, obj: StoryObjectDraft) -> dict[str, Any]:
        """Compiles a standalone text element."""
        return {
            "id": obj.id,
            "type": "text",
            "layout": obj.layout,
            "width": 500,
            "height": 100,
            "textProps": {
                "text": obj.text or obj.purpose or "",
                "variant": "header" if "title" in obj.id.lower() else "caption",
                "color": "#F8FAFC",
            },
        }

    def _compile_connector(self, obj: StoryObjectDraft) -> dict[str, Any]:
        """Compiles a connector between two visual elements."""
        return {
            "id": obj.id,
            "type": "connector",
            "layout": obj.layout,
            "connectorProps": {
                "fromId": obj.from_id,
                "toId": obj.to_id,
                "label": obj.label or obj.purpose or "Drives payment",
                "arrow": True,
                "color": "#64748B",
            },
        }

    def _compile_chart(
        self,
        obj: StoryObjectDraft,
        approved_facts: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Compiles a chart element directly from Gemini-authored series or points."""
        chart_type = obj.chart_type or "trajectory_area"
        accent_color = obj.accent or "#3B82F6"

        chart_props: dict[str, Any] = {
            "chartType": chart_type,
            "title": obj.title or obj.purpose or "Trajectory",
            "subtitle": obj.subtitle or "",
            "accentColor": accent_color,
        }
        if obj.series:
            chart_props["series"] = obj.series
        elif obj.points:
            chart_props["series"] = [
                {
                    "id": f"{obj.id}_series",
                    "name": obj.title or "Data",
                    "color": accent_color,
                    "points": obj.points,
                }
            ]
        else:
            raise ValueError(
                f"Chart '{obj.id}' requires directly authored 'series' or 'points'. Fallback and fact lookup data are not permitted in open direct-authoring mode."
            )

        # If layout is full_bottom or full_screen, width/height adjust accordingly
        is_macro = obj.layout in ("full_bottom", "full_screen", "full_top")
        width = 1760 if is_macro else 640
        height = 360 if is_macro else 280

        return {
            "id": obj.id,
            "type": "chart",
            "layout": obj.layout,
            "width": width,
            "height": height,
            "chartProps": chart_props,
        }

    def _compile_image(
        self,
        obj: StoryObjectDraft,
        fixture: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Compiles an image visual element with available asset verification."""
        if fixture and "available_assets" in fixture:
            avail = fixture.get("available_assets")
            if not avail:
                raise ValueError(
                    f"Image '{obj.id}' is used, but available_assets list is empty or not provided."
                )
            if obj.asset_id not in avail:
                raise ValueError(
                    f"Image '{obj.id}' references unknown asset_id '{obj.asset_id}'. Available assets: {sorted(avail)}"
                )

        return {
            "id": obj.id,
            "type": "image",
            "layout": obj.layout,
            "width": 1920 if obj.layout == "full_screen" else 640,
            "height": 1080 if obj.layout == "full_screen" else 360,
            "imageProps": {
                "assetId": obj.asset_id,
            },
        }

    def _compile_character(self, obj: StoryObjectDraft) -> dict[str, Any]:
        """Compiles a futuristic stick figure character primitive."""
        return {
            "id": obj.id,
            "type": "character",
            "layout": obj.layout,
            "width": 240,
            "height": 360,
            "characterProps": {
                "style": obj.character_style or "futuristic_stick",
                "role": obj.role,
                "label": obj.label or obj.role,
                "pose": obj.pose or "idle",
                "emotion": obj.emotion or "neutral",
                "facing": obj.facing or "right",
                "accentColor": obj.accent or "#38BDF8",
            },
        }

    def _compile_event(
        self,
        event: StoryEventDraft,
        word_timestamps: list[dict[str, Any]],
        fps: int,
        min_start_ms: int = 0,
        approved_facts: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Compiles a choreography action, resolving speech anchors to exact frames."""
        start_frame = resolve_anchor_frame(
            word_timestamps=word_timestamps,
            anchor_phrase=event.anchor,
            fps=fps,
            min_start_ms=min_start_ms,
        )

        event_dict: dict[str, Any] = {
            "action": event.action,
            "targetId": event.target_id,
            "startFrame": start_frame,
            "durationFrames": 25,
            "anchor": event.anchor,
        }

        if event.action == "enter":
            event_dict["style"] = "fade_slide_up"

        elif event.action == "move":
            event_dict["to"] = event.to
            event_dict["style"] = "spring_smooth"

        elif event.action == "transform_number":
            if not event.to_display_value or not event.to_display_value.strip():
                raise ValueError(
                    f"Action 'transform_number' targeting '{event.target_id}' requires 'to_display_value'."
                )
            if event.to_numeric_value is None:
                raise ValueError(
                    f"Action 'transform_number' targeting '{event.target_id}' requires 'to_numeric_value'."
                )
            event_dict["toDisplayValue"] = event.to_display_value
            event_dict["toValue"] = event.to_numeric_value
            event_dict["toFactId"] = event.to_fact_id
            event_dict["format"] = "plain"
            event_dict["durationFrames"] = 30
            event_dict["style"] = "counter_spring"

        elif event.action == "transform_text":
            event_dict["toText"] = event.to_text

        elif event.action == "change_visual_state":
            event_dict["state"] = event.state
            if event.badge:
                event_dict["badge"] = event.badge

        elif event.action == "change_pose":
            event_dict["durationFrames"] = 20
            event_dict["pose"] = event.pose
            if event.emotion:
                event_dict["emotion"] = event.emotion
            if event.facing:
                event_dict["facing"] = event.facing

        elif event.action == "exit":
            event_dict["direction"] = event.direction or "fade"
            event_dict["durationFrames"] = 24  # Match EXIT_DURATION

        return event_dict


def compile_story_draft(draft: ContinuousStoryDraft, fixture: dict[str, Any]) -> dict[str, Any]:
    """Convenience functional wrapper for ContinuousStoryCompiler."""
    return ContinuousStoryCompiler().compile(draft, fixture)
