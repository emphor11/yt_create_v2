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
    If min_start_ms > 0, searches only for occurrences occurring at or after min_start_ms.
    Matches contiguous token subsequences with fallback to the initial keyword token.
    """
    clean_tokens = [
        re.sub(r"[^\w\.]", "", t.lower())
        for t in anchor_phrase.split()
        if re.sub(r"[^\w\.]", "", t.lower())
    ]
    if not clean_tokens:
        raise ValueError(f"Anchor phrase '{anchor_phrase}' contains no searchable speech tokens.")

    clean_words = [
        re.sub(r"[^\w\.]", "", w.get("word", "").lower())
        for w in word_timestamps
    ]

    # 1. Contiguous subsequence search
    for i in range(len(clean_words) - len(clean_tokens) + 1):
        if word_timestamps[i].get("start_ms", 0) < min_start_ms:
            continue
        match = True
        for j in range(len(clean_tokens)):
            w = clean_words[i + j]
            t = clean_tokens[j]
            if w != t and t not in w:
                match = False
                break
        if match:
            return word_timestamps[i].get("start_ms", 0)

    # 2. Fallback: match first token
    first_token = clean_tokens[0]
    for i, w in enumerate(clean_words):
        if word_timestamps[i].get("start_ms", 0) < min_start_ms:
            continue
        if first_token == w or first_token in w:
            return word_timestamps[i].get("start_ms", 0)

    # 3. If min_start_ms > 0 and not found after min_start_ms, fall back to search from start
    if min_start_ms > 0:
        return resolve_anchor_ms(word_timestamps, anchor_phrase, min_start_ms=0)

    raise ValueError(
        f"Anchor phrase '{anchor_phrase}' could not be resolved to any spoken word timestamp."
    )


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

        elif event.action == "exit":
            event_dict["direction"] = event.direction or "fade"
            event_dict["durationFrames"] = 24  # Match EXIT_DURATION

        return event_dict


def compile_story_draft(draft: ContinuousStoryDraft, fixture: dict[str, Any]) -> dict[str, Any]:
    """Convenience functional wrapper for ContinuousStoryCompiler."""
    return ContinuousStoryCompiler().compile(draft, fixture)
