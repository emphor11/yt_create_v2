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
5. 5-Layout Spatial Preservation: preserves clean zone layout names for Remotion layout engine.
"""
import html
import re
from typing import Any

from domain.continuous_story_plan import ContinuousStoryDraft, StoryObjectDraft, StoryEventDraft, VALID_ZONES


def resolve_anchor_ms(
    word_timestamps: list[dict[str, Any]],
    anchor_phrase: str,
    min_start_ms: int = 0,
) -> int:
    """
    Resolves a spoken anchor phrase to its exact start time in milliseconds using audio word timestamps.
    Enforces exact contiguous phrase matching while normalizing Polly speech mark words:
      - HTML-decodes entities (e.g. fund&#x27;s -> fund's)
      - Removes SSML tags (e.g. <break time="..."/>)
      - Ignores non-spoken pause tokens
    Fails loudly with ValueError if the exact phrase is not found.
    """
    if not anchor_phrase or not anchor_phrase.strip():
        raise ValueError("Anchor phrase cannot be empty.")

    anchor_decoded = html.unescape(anchor_phrase)
    anchor_clean = re.sub(r"<[^>]+>", " ", anchor_decoded).replace("-", " ")
    clean_tokens = [
        re.sub(r"[^\w\.]", "", t.lower()).strip(".")
        for t in anchor_clean.split()
        if re.sub(r"[^\w\.]", "", t.lower()).strip(".")
    ]
    if not clean_tokens:
        raise ValueError(f"Anchor phrase '{anchor_phrase}' contains no searchable speech tokens.")

    token_entries: list[tuple[str, int, int]] = []
    for w in word_timestamps:
        start_ms = w.get("start_ms", 0)
        end_ms = w.get("end_ms", 0)
        w_raw = str(w.get("word", ""))
        w_decoded = html.unescape(w_raw)
        w_stripped = re.sub(r"<[^>]+>", " ", w_decoded)
        w_clean = w_stripped.replace("-", " ")
        for tok in w_clean.split():
            c_tok = re.sub(r"[^\w\.]", "", tok.lower()).strip(".")
            if c_tok and not w_raw.strip().startswith("<break") and not w_raw.strip().startswith("<pause"):
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
        # 1. Resolve Object Lifespans to Enable Context-Aware Promotion
        # ----------------------------------------------------
        object_intervals: dict[str, tuple[int, int]] = {}
        for event in draft.events:
            tgt = event.target_id
            if event.action in ("enter", "connect"):
                try:
                    start_ms = resolve_anchor_ms(word_timestamps, event.anchor)
                    s_frame = round((start_ms / 1000.0) * fps)
                except Exception:
                    s_frame = 0
                cur_end = object_intervals.get(tgt, (s_frame, duration_in_frames))[1]
                object_intervals[tgt] = (s_frame, cur_end)
            elif event.action == "exit":
                try:
                    exit_ms = resolve_anchor_ms(word_timestamps, event.anchor)
                    e_frame = round((exit_ms / 1000.0) * fps)
                except Exception:
                    e_frame = duration_in_frames
                cur_start = object_intervals.get(tgt, (0, duration_in_frames))[0]
                object_intervals[tgt] = (cur_start, e_frame)

        # ----------------------------------------------------
        # 2. Compile Atomic Elements Directly
        # ----------------------------------------------------
        compiled_objects: list[dict[str, Any]] = []

        for obj in draft.objects:
            if obj.type != "connector" and obj.layout not in VALID_ZONES:
                raise ValueError(
                    f"INVALID_LAYOUT_ZONE: Object '{obj.id}' specifies invalid layout zone '{obj.layout}'. Valid zones: {sorted(VALID_ZONES)}"
                )

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
                if obj.layout == "full_bottom":
                    chart_start, chart_end = object_intervals.get(obj.id, (0, duration_in_frames))
                    has_concurrent = False
                    for other in draft.objects:
                        if other.id != obj.id and other.type in ("card", "number", "image", "text", "character"):
                            o_start, o_end = object_intervals.get(other.id, (0, duration_in_frames))
                            if max(chart_start, o_start) < min(chart_end, o_end):
                                has_concurrent = True
                                break
                    if not has_concurrent:
                        chart_dict["layout"] = "center"
                        chart_dict["width"] = 1440
                        chart_dict["height"] = 560
                compiled_objects.append(chart_dict)

            elif obj.type == "image":
                img_dict = self._compile_image(obj, fixture=fixture)
                compiled_objects.append(img_dict)

            elif obj.type == "stock_video":
                sv_dict = self._compile_stock_video(obj, fixture=fixture)
                compiled_objects.append(sv_dict)

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
            target_obj = next((o for o in draft.objects if o.id == event.target_id), None)
            if event.action != "enter":
                min_start = enter_times_ms.get(event.target_id, 0)
                if event.action == "connect":
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
                target_obj=target_obj,
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

        # Dynamic responsive dimensions based on layout zone
        if card_obj.layout == "center":
            width = 720
            height = 360
        elif card_obj.layout in ("split_left", "split_right"):
            width = 560
            height = 300
        else:
            width = 420
            height = 240

        return {
            "id": card_obj.id,
            "type": "card",
            "layout": card_obj.layout,
            "width": width,
            "height": height,
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

        width = 680 if obj.layout == "center" else 360
        height = 220 if obj.layout == "center" else 180

        return {
            "id": obj.id,
            "type": "number",
            "layout": obj.layout,
            "width": width,
            "height": height,
            "numberProps": number_props,
        }

    def _compile_text(self, obj: StoryObjectDraft) -> dict[str, Any]:
        """Compiles a standalone text element."""
        return {
            "id": obj.id,
            "type": "text",
            "layout": obj.layout,
            "width": 800,
            "height": 160,
            "textProps": {
                "text": obj.text or obj.purpose or "",
                "variant": "title",
                "color": "#202522",
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

        # If layout is full_bottom, full_screen, or center, width/height adjust accordingly
        is_full_bottom = obj.layout == "full_bottom"
        is_full_screen = obj.layout == "full_screen"
        is_center = obj.layout == "center"
        if is_full_bottom:
            width = 1760
            height = 260
        elif is_full_screen:
            width = 1760
            height = 920
        elif is_center:
            width = 1440
            height = 560
        else:
            width = 640
            height = 280

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
        if not obj.asset_id:
            raise ValueError(
                f"IMAGE_ASSET_REQUEST_MISSING: Image '{obj.id}' has unresolved asset_request before compilation."
            )

        if fixture and "available_assets" in fixture:
            avail = fixture.get("available_assets")
            if not avail:
                raise ValueError(
                    f"UNKNOWN_ASSET_ID: Image '{obj.id}' is used, but available_assets list is empty or not provided."
                )
            if obj.asset_id not in avail:
                raise ValueError(
                    f"UNKNOWN_ASSET_ID: Image '{obj.id}' references unknown asset_id '{obj.asset_id}'. Available assets: {sorted(avail)}"
                )

        image_props: dict[str, Any] = {
            "assetId": obj.asset_id,
        }
        if obj.alt:
            image_props["alt"] = obj.alt
        if obj.caption:
            image_props["caption"] = obj.caption
        if obj.badge:
            image_props["badge"] = obj.badge
        if obj.fit:
            image_props["fit"] = obj.fit
        if obj.border_color:
            image_props["borderColor"] = obj.border_color
        if obj.border_radius is not None:
            image_props["borderRadius"] = obj.border_radius

        return {
            "id": obj.id,
            "type": "image",
            "layout": obj.layout,
            "width": 1920 if obj.layout == "full_screen" else 640,
            "height": 1080 if obj.layout == "full_screen" else 360,
            "imageProps": image_props,
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

    def _compile_stock_video(
        self,
        obj: StoryObjectDraft,
        fixture: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Compiles a full-screen stock video visual element with asset verification."""
        if obj.layout != "full_screen":
            raise ValueError(
                f"STOCK_VIDEO_INVALID_LAYOUT: stock_video '{obj.id}' layout must be 'full_screen', got '{obj.layout}'."
            )

        if not obj.asset_id:
            raise ValueError(
                f"VIDEO_ASSET_REQUEST_MISSING: stock_video '{obj.id}' has unresolved asset_request before compilation."
            )

        if fixture and "available_assets" in fixture:
            avail = fixture.get("available_assets")
            if not avail:
                raise ValueError(
                    f"UNKNOWN_ASSET_ID: stock_video '{obj.id}' is used, but available_assets list is empty or not provided."
                )
            if obj.asset_id not in avail:
                raise ValueError(
                    f"UNKNOWN_ASSET_ID: stock_video '{obj.id}' references unknown asset_id '{obj.asset_id}'. Available assets: {sorted(avail)}"
                )

        stock_video_props: dict[str, Any] = {
            "assetId": obj.asset_id,
            "fit": obj.fit or "cover",
        }
        if fixture and "asset_durations" in fixture:
            dur = fixture.get("asset_durations", {}).get(obj.asset_id)
            if dur:
                stock_video_props["durationSeconds"] = float(dur)
        if obj.alt:
            stock_video_props["alt"] = obj.alt
        if obj.caption:
            stock_video_props["caption"] = obj.caption
        if obj.overlay_tint:
            stock_video_props["overlayTint"] = obj.overlay_tint

        return {
            "id": obj.id,
            "type": "stock_video",
            "layout": "full_screen",
            "width": 1920,
            "height": 1080,
            "stockVideoProps": stock_video_props,
        }

    def _compile_event(
        self,
        event: StoryEventDraft,
        word_timestamps: list[dict[str, Any]],
        fps: int,
        min_start_ms: int = 0,
        approved_facts: dict[str, Any] | None = None,
        target_obj: StoryObjectDraft | None = None,
    ) -> dict[str, Any]:
        """Compiles a choreography action, resolving speech anchors to exact frames."""
        start_frame = resolve_anchor_frame(
            word_timestamps=word_timestamps,
            anchor_phrase=event.anchor,
            fps=fps,
            min_start_ms=min_start_ms,
        )

        is_stock_video = target_obj is not None and target_obj.type == "stock_video"
        is_cut_enter = event.action == "enter" and (event.style == "cut" or is_stock_video)
        is_cut_exit = event.action == "exit" and (event.direction == "cut" or is_stock_video)

        duration_frames = 25
        if is_cut_enter or is_cut_exit:
            duration_frames = 0

        event_dict: dict[str, Any] = {
            "action": event.action,
            "targetId": event.target_id,
            "startFrame": start_frame,
            "durationFrames": duration_frames,
            "anchor": event.anchor,
        }

        if event.action == "enter":
            event_dict["style"] = "cut" if is_cut_enter else (event.style or "fade_slide_up")

        elif event.action == "move":
            if not event.to or event.to not in VALID_ZONES:
                raise ValueError(
                    f"INVALID_MOVE_ZONE: Action 'move' on '{event.target_id}' specifies invalid destination zone '{event.to}'. Valid zones: {sorted(VALID_ZONES)}"
                )
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
            if is_cut_exit:
                event_dict["direction"] = "cut"
                event_dict["durationFrames"] = 0
            else:
                event_dict["direction"] = event.direction or "fade"
                event_dict["durationFrames"] = 24  # Match EXIT_DURATION

        return event_dict


def compile_story_draft(draft: ContinuousStoryDraft, fixture: dict[str, Any]) -> dict[str, Any]:
    """Convenience functional wrapper for ContinuousStoryCompiler."""
    return ContinuousStoryCompiler().compile(draft, fixture)
