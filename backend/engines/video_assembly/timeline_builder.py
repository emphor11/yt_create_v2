import re
from typing import Any, NamedTuple, Literal, TYPE_CHECKING
from domain.hook import Hook
from domain.script_visual_strategy import ScriptVisualStrategy
from domain.voice_track import VoiceTrack, WordTimestamp

if TYPE_CHECKING:
    from domain.composition_plan import FullCompositionPlan

# Constant for minimum beat duration in frames (30fps: 15 frames = 0.5s)
MIN_BEAT_DURATION_FRAMES = 15


def _is_word_match(polly_raw: str, trigger_raw: str) -> bool:
    p_clean = re.sub(r"[^\w]", "", polly_raw.lower())
    t_clean = re.sub(r"[^\w]", "", trigger_raw.lower())
    if not p_clean or not t_clean:
        return False
    if p_clean == t_clean:
        return True

    # 1. Check token-based exact matching first
    p_tokens = [re.sub(r"[^\w]", "", pt) for pt in re.split(r"[^a-zA-Z0-9]", polly_raw.lower()) if re.sub(r"[^\w]", "", pt)]
    t_tokens = [re.sub(r"[^\w]", "", tt) for tt in re.split(r"[^a-zA-Z0-9]", trigger_raw.lower()) if re.sub(r"[^\w]", "", tt)]
    if p_tokens and t_tokens:
        for pt in p_tokens:
            for tt in t_tokens:
                if pt == tt:
                    return True

    # 2. Check safe substring matching:
    if t_clean in p_clean:
        if len(t_clean) >= 3 or (t_clean.isdigit() and len(t_clean) >= 2):
            return True

    if p_clean in t_clean:
        if len(p_clean) >= 3 or (p_clean.isdigit() and len(p_clean) >= 2):
            return True

    return False


def _find_trigger_index(
    timestamps: list[Any],
    trigger_raw: str,
    section_text: str,
    prev_start_idx: int,
) -> int:
    """
    Finds the index in timestamps corresponding to trigger_raw.
    Dual-Strategy:
    1. Primary: Character-Offset Span Matching (Exact ground truth for numbers, currencies, compounds).
    2. Secondary: Token & Phonetic Substring Matching (Legacy / Mock fallback).
    Returns -1 if not found.
    """
    if not timestamps or not trigger_raw or not trigger_raw.strip():
        return -1

    if prev_start_idx >= len(timestamps):
        return -1

    t_clean = re.sub(r"[^\w]", "", trigger_raw.lower())

    # 1. Primary Strategy: Character-Offset Span Matching
    has_char_offsets = any(getattr(ts, "start_char", None) is not None for ts in timestamps)
    if has_char_offsets and section_text:
        prev_char_threshold = 0
        if prev_start_idx < len(timestamps) and getattr(timestamps[prev_start_idx], "start_char", None) is not None:
            prev_char_threshold = getattr(timestamps[prev_start_idx], "start_char") or 0

        char_pos = section_text.lower().find(trigger_raw.lower(), prev_char_threshold)
        if char_pos == -1 and t_clean:
            char_pos = section_text.lower().find(t_clean, prev_char_threshold)

        if char_pos != -1:
            for idx in range(prev_start_idx, len(timestamps)):
                sc = getattr(timestamps[idx], "start_char", None)
                ec = getattr(timestamps[idx], "end_char", None)
                if sc is not None and ec is not None:
                    word = getattr(timestamps[idx], "word", "")
                    if (sc <= char_pos <= ec or sc >= char_pos) and _is_word_match(word, trigger_raw):
                        return idx

    # 2. Secondary Strategy: Token & Substring Matching
    for idx in range(prev_start_idx, len(timestamps)):
        word = getattr(timestamps[idx], "word", "")
        if _is_word_match(word, trigger_raw):
            return idx

    return -1


class TimelineBuilderError(Exception):
    """Raised when timeline generation fails."""


class TimedBeatInterval(NamedTuple):
    beat_id: str
    start_frame: int
    end_frame: int
    duration_frames: int
    section_type: Literal["hook", "body"]
    section_index: int
    beat_index: int


def _compute_section_byte_spans(
    section_texts: list[str],
    full_text: str,
) -> list[tuple[int, int]]:
    """
    Computes [start_byte, end_byte) spans for each section within full_text encoded as UTF-8.
    Polly's speech marks report start and end as UTF-8 byte offsets.
    """
    full_bytes = full_text.encode("utf-8")
    spans: list[tuple[int, int]] = []
    curr_byte_pos = 0

    for text in section_texts:
        clean = text.strip()
        if not clean:
            spans.append((curr_byte_pos, curr_byte_pos))
            continue

        sec_bytes = clean.encode("utf-8")
        found_idx = full_bytes.find(sec_bytes, curr_byte_pos)
        if found_idx != -1:
            start_byte = found_idx
            end_byte = found_idx + len(sec_bytes)
            spans.append((start_byte, end_byte))
            curr_byte_pos = end_byte
        else:
            # Fallback if raw unstripped text matches
            raw_bytes = text.encode("utf-8")
            raw_idx = full_bytes.find(raw_bytes, curr_byte_pos)
            if raw_idx != -1:
                start_byte = raw_idx
                end_byte = raw_idx + len(raw_bytes)
                spans.append((start_byte, end_byte))
                curr_byte_pos = end_byte
            else:
                spans.append((curr_byte_pos, curr_byte_pos + len(sec_bytes)))
                curr_byte_pos += len(sec_bytes)

    return spans


def _find_section_for_byte_offset(
    b_start: int,
    spans: list[tuple[int, int]],
) -> int:
    """
    Determines which section index owns the given UTF-8 byte offset.
    Respects Polly byte-offset semantics and handles boundary gaps gracefully.
    Skips empty sections (start_byte == end_byte).
    """
    non_empty = [i for i, (s, e) in enumerate(spans) if s < e]
    if not non_empty:
        return 0

    # Before the first non-empty section -> first non-empty section
    if b_start < spans[non_empty[0]][0]:
        return non_empty[0]

    # At or after the start of the last non-empty section -> last non-empty section
    if b_start >= spans[non_empty[-1]][0]:
        return non_empty[-1]

    for pos, idx in enumerate(non_empty):
        if pos + 1 < len(non_empty):
            next_idx = non_empty[pos + 1]
            if spans[idx][0] <= b_start < spans[next_idx][0]:
                return idx

    return non_empty[-1]


def _assign_words_to_sections(
    section_texts: list[str],
    section_ids: list[str],
    voice_track: VoiceTrack,
) -> list[list[WordTimestamp]]:
    """
    Assigns Polly word timestamps to hook and idea sections.

    Order of preference:
    1. Chunk-Source Mapping: Only used when voice_track.chunks is present, each chunk
       has a valid source_id matching a known section in section_ids, and total word counts
       match voice_track.word_timestamps. Otherwise falls through to byte-range mapping.
    2. Source-Text Byte Range Mapping: Used when word_timestamps have UTF-8 byte offsets (start_char).
       Determines section ownership from source-text byte spans in full_script_text.
       Completely immune to Polly token expansions (currencies, decimals, symbols, abbreviations).
    3. Sequential Word Count Mapping: Fallback for legacy mock unit tests where neither chunks nor
       byte offsets are present.
    """
    word_timestamps = voice_track.word_timestamps or []
    section_timestamps: list[list[WordTimestamp]] = [[] for _ in section_texts]

    if not word_timestamps or not section_texts:
        return section_timestamps

    # --- Strategy 1: Multi-Chunk Source Mapping ---
    chunks = getattr(voice_track, "chunks", None) or []
    if chunks:
        chunk_source_ids = [c.get("source_id") for c in chunks if isinstance(c, dict)]
        section_id_set = set(section_ids)
        total_chunk_words = sum(len(c.get("word_timestamps", [])) for c in chunks if isinstance(c, dict))

        # Only use chunk-source mapping when source_id is valid and matches a known section
        all_valid_and_known = (
            len(chunk_source_ids) == len(chunks)
            and all(isinstance(sid, str) and sid in section_id_set for sid in chunk_source_ids)
            and total_chunk_words == len(word_timestamps)
        )

        if all_valid_and_known:
            sorted_chunks = sorted(chunks, key=lambda c: c.get("sequence", 0))
            word_idx = 0
            for chunk in sorted_chunks:
                c_source_id = chunk.get("source_id")
                c_words = chunk.get("word_timestamps", [])
                c_count = len(c_words)
                s_idx = section_ids.index(c_source_id)

                for local_ts in c_words:
                    if word_idx < len(word_timestamps):
                        global_ts = word_timestamps[word_idx]
                        if isinstance(local_ts, dict) and local_ts.get("start_char") is not None:
                            word_item = WordTimestamp(
                                word=global_ts.word,
                                start_ms=global_ts.start_ms,
                                end_ms=global_ts.end_ms,
                                start_char=local_ts.get("start_char"),
                                end_char=local_ts.get("end_char"),
                            )
                        else:
                            word_item = global_ts
                        section_timestamps[s_idx].append(word_item)
                        word_idx += 1
            return section_timestamps

    # --- Strategy 2: Source-Text Byte Range Mapping ---
    has_byte_offsets = any(getattr(ts, "start_char", None) is not None for ts in word_timestamps)
    if has_byte_offsets:
        full_text = voice_track.full_script_text
        if not full_text:
            full_text = "\n\n".join(t.strip() for t in section_texts if t.strip())

        spans = _compute_section_byte_spans(section_texts, full_text)
        last_s_idx = 0

        for ts in word_timestamps:
            b_start = getattr(ts, "start_char", None)
            if b_start is not None:
                s_idx = _find_section_for_byte_offset(b_start, spans)
                last_s_idx = s_idx
            else:
                s_idx = last_s_idx

            # Normalize start_char and end_char to section-local offset for trigger matching
            if b_start is not None:
                sec_start_byte = spans[s_idx][0]
                local_sc = max(0, ts.start_char - sec_start_byte)
                local_ec = max(0, ts.end_char - sec_start_byte) if ts.end_char is not None else None
                section_word = WordTimestamp(
                    word=ts.word,
                    start_ms=ts.start_ms,
                    end_ms=ts.end_ms,
                    start_char=local_sc,
                    end_char=local_ec,
                )
            else:
                section_word = ts

            section_timestamps[s_idx].append(section_word)

        return section_timestamps

    # --- Strategy 3: Sequential Count Mapping (Legacy / Mock Fallback) ---
    all_section_word_mappings = []
    for s_idx, text in enumerate(section_texts):
        words = [re.sub(r"[^\w]", "", w.lower()) for w in text.split() if re.sub(r"[^\w]", "", w)]
        for _ in words:
            all_section_word_mappings.append(s_idx)

    polly_len = len(word_timestamps)
    sect_len = len(all_section_word_mappings)

    if sect_len > 0 and polly_len > 0:
        polly_idx = 0
        for sect_idx in range(sect_len):
            if polly_idx >= polly_len:
                break
            s_idx = all_section_word_mappings[sect_idx]
            section_timestamps[s_idx].append(word_timestamps[polly_idx])
            polly_idx += 1

        # Clamp remaining Polly words to the last section
        while polly_idx < polly_len:
            section_timestamps[-1].append(word_timestamps[polly_idx])
            polly_idx += 1

    return section_timestamps


class TimelineBuilder:
    def __init__(self, fps: int = 30):
        self.fps = fps

    def build_timeline(
        self,
        *,
        hook: Hook,
        strategy: ScriptVisualStrategy,
        voice_track: VoiceTrack,
        composition_plan: FullCompositionPlan | None = None,
    ) -> list[TimedBeatInterval]:
        # 1. Collect narration texts for sections to align them against Polly words
        # Index 0: Hook
        section_texts: list[str] = [hook.script_text]
        # Index 1..N: Body Ideas
        if composition_plan is not None:
            for comp_idea in composition_plan.ideas:
                section_texts.append(comp_idea.narration)
            section_ids: list[str] = ["hook"] + [comp_idea.idea_id for comp_idea in composition_plan.ideas]
        else:
            for idea in strategy.ideas:
                section_texts.append(idea.narration)
            section_ids: list[str] = ["hook"] + [idea.idea_id for idea in strategy.ideas]

        # 2. Extract Polly word timestamps sequence
        word_timestamps = voice_track.word_timestamps or []

        # 3. Align Polly words to sections using robust 3-tier hierarchy
        section_timestamps = _assign_words_to_sections(
            section_texts=section_texts,
            section_ids=section_ids,
            voice_track=voice_track,
        )

        # 4. Compute timing bounds for each beat
        beat_time_bounds: list[tuple[float, float]] = []

        # Process Hook section
        hook_timestamps = section_timestamps[0]
        hook_beats = hook.visual_directives
        hook_beats_count = len(hook_beats)
        if hook_beats_count > 0:
            hook_start_indices = [0]
            for b_idx in range(1, hook_beats_count):
                trigger = hook_beats[b_idx].trigger_word
                if not trigger or not trigger.strip():
                    raise TimelineBuilderError(
                        f"Beat '{hook_beats[b_idx].beat_id}' in hook requires trigger_word."
                    )
                match_idx = _find_trigger_index(
                    timestamps=hook_timestamps,
                    trigger_raw=trigger,
                    section_text=hook.script_text,
                    prev_start_idx=hook_start_indices[-1] + 1,
                )
                if match_idx == -1:
                    raise TimelineBuilderError(
                        f"Trigger word '{trigger}' for beat '{hook_beats[b_idx].beat_id}' in hook "
                        f"was not found in the voice track words."
                    )
                hook_start_indices.append(match_idx)

            hook_start_indices.append(len(hook_timestamps))

            # Assign bounds to hook beats
            for b_idx in range(hook_beats_count):
                start_idx = hook_start_indices[b_idx]
                end_idx = hook_start_indices[b_idx + 1]

                if start_idx < end_idx and start_idx < len(hook_timestamps):
                    start_ms = float(hook_timestamps[start_idx].start_ms)
                    actual_end_idx = min(end_idx - 1, len(hook_timestamps) - 1)
                    end_ms = float(hook_timestamps[actual_end_idx].end_ms)
                    beat_time_bounds.append((start_ms, end_ms))
                else:
                    raise TimelineBuilderError(
                        f"Invalid trigger word order or empty range for beat '{hook_beats[b_idx].beat_id}' in hook."
                    )

        # Process Body Sections
        if composition_plan is not None:
            for s_idx, comp_idea in enumerate(composition_plan.ideas):
                timestamps = section_timestamps[s_idx + 1]
                beats = comp_idea.beats
                M = len(beats)
                if M == 0:
                    continue

                if M == 1:
                    # Single composition beat: spans the entire idea interval
                    if len(timestamps) > 0:
                        start_ms = float(timestamps[0].start_ms)
                        end_ms = float(timestamps[-1].end_ms)
                        beat_time_bounds.append((start_ms, end_ms))
                    else:
                        beat_time_bounds.append((0.0, 0.0))
                else:
                    beat_start_indices = [0]
                    for b_idx in range(1, M):
                        trigger = beats[b_idx].trigger_word
                        match_idx = -1
                        if trigger and trigger.strip():
                            match_idx = _find_trigger_index(
                                timestamps=timestamps,
                                trigger_raw=trigger,
                                section_text=comp_idea.narration,
                                prev_start_idx=beat_start_indices[-1] + 1,
                            )
                        if match_idx == -1:
                            # Graceful proportional split if trigger word not matched or missing
                            remaining_words = len(timestamps) - beat_start_indices[-1]
                            remaining_beats = M - b_idx + 1
                            step = max(1, remaining_words // remaining_beats)
                            match_idx = beat_start_indices[-1] + step
                            match_idx = min(match_idx, len(timestamps) - (M - b_idx))
                            match_idx = max(beat_start_indices[-1] + 1, match_idx)

                        beat_start_indices.append(match_idx)

                    beat_start_indices.append(len(timestamps))

                    for b_idx in range(M):
                        start_idx = beat_start_indices[b_idx]
                        end_idx = beat_start_indices[b_idx + 1]

                        if start_idx < end_idx and start_idx < len(timestamps):
                            start_ms = float(timestamps[start_idx].start_ms)
                            actual_end_idx = min(end_idx - 1, len(timestamps) - 1)
                            end_ms = float(timestamps[actual_end_idx].end_ms)
                            beat_time_bounds.append((start_ms, end_ms))
                        else:
                            beat_time_bounds.append((0.0, 0.0))
        else:
            # Legacy mode: derives body beats from strategy.ideas[s_idx].visual_sequence
            for s_idx, idea in enumerate(strategy.ideas):
                timestamps = section_timestamps[s_idx + 1]
                beats = idea.visual_sequence
                M = len(beats)
                if M == 0:
                    continue

                beat_start_indices = [0]
                for b_idx in range(1, M):
                    trigger = beats[b_idx].trigger_word
                    if not trigger or not trigger.strip():
                        raise TimelineBuilderError(
                            f"Beat '{beats[b_idx].beat_id}' in idea '{idea.idea_id}' requires trigger_word."
                        )
                    match_idx = _find_trigger_index(
                        timestamps=timestamps,
                        trigger_raw=trigger,
                        section_text=idea.narration,
                        prev_start_idx=beat_start_indices[-1] + 1,
                    )
                    if match_idx == -1:
                        raise TimelineBuilderError(
                            f"Trigger word '{trigger}' for beat '{beats[b_idx].beat_id}' in idea '{idea.idea_id}' "
                            f"was not found in the voice track words."
                        )
                    beat_start_indices.append(match_idx)

                beat_start_indices.append(len(timestamps))

                for b_idx in range(M):
                    start_idx = beat_start_indices[b_idx]
                    end_idx = beat_start_indices[b_idx + 1]

                    if start_idx < end_idx and start_idx < len(timestamps):
                        start_ms = float(timestamps[start_idx].start_ms)
                        actual_end_idx = min(end_idx - 1, len(timestamps) - 1)
                        end_ms = float(timestamps[actual_end_idx].end_ms)
                        beat_time_bounds.append((start_ms, end_ms))
                    else:
                        raise TimelineBuilderError(
                            f"Invalid trigger word order or empty range for beat '{beats[b_idx].beat_id}' in idea '{idea.idea_id}'."
                        )

        # 5. Build contiguous and non-overlapping intervals
        total_duration_frames = int(round(voice_track.duration_seconds * self.fps))
        timed_intervals: list[TimedBeatInterval] = []

        # Construct flat list of beats metadata for index references
        flat_beat_refs = []
        # Hook index
        for b_idx, directive in enumerate(hook.visual_directives):
            flat_beat_refs.append(("hook", 0, b_idx, directive.beat_id))

        if composition_plan is not None:
            # Body ideas from composition_plan
            for s_idx, comp_idea in enumerate(composition_plan.ideas):
                for b_idx, comp_beat in enumerate(comp_idea.beats):
                    flat_beat_refs.append(("body", s_idx, b_idx, comp_beat.beat_id))
        else:
            # Body ideas from legacy strategy
            for s_idx, idea in enumerate(strategy.ideas):
                for b_idx, beat in enumerate(idea.visual_sequence):
                    flat_beat_refs.append(("body", s_idx, b_idx, beat.beat_id))

        for idx, (section_type, s_idx, b_idx, beat_id) in enumerate(flat_beat_refs):
            raw_start_ms, raw_end_ms = beat_time_bounds[idx]

            exact_trigger_start_frame = int(round((raw_start_ms / 1000.0) * self.fps))
            raw_end_frame = int(round((raw_end_ms / 1000.0) * self.fps))

            if idx == 0:
                start_frame = 0
            else:
                # Align start_frame to exact trigger word start time, enforcing minimum beat duration
                prev_start = timed_intervals[-1].start_frame
                start_frame = max(exact_trigger_start_frame, prev_start + MIN_BEAT_DURATION_FRAMES)

                # Extend previous beat's end_frame through the pause to this beat's start_frame
                prev_beat = timed_intervals[-1]
                timed_intervals[-1] = TimedBeatInterval(
                    beat_id=prev_beat.beat_id,
                    start_frame=prev_beat.start_frame,
                    end_frame=start_frame,
                    duration_frames=start_frame - prev_beat.start_frame,
                    section_type=prev_beat.section_type,
                    section_index=prev_beat.section_index,
                    beat_index=prev_beat.beat_index,
                )

            # End frame defaults to raw_end_frame or start_frame + MIN_BEAT_DURATION_FRAMES
            end_frame = max(start_frame + MIN_BEAT_DURATION_FRAMES, raw_end_frame)

            # Clamp the last beat to exact total duration
            if idx == len(flat_beat_refs) - 1:
                end_frame = total_duration_frames

            # Clamp if exceeded total duration
            if end_frame > total_duration_frames:
                end_frame = total_duration_frames

            duration_frames = end_frame - start_frame

            timed_intervals.append(
                TimedBeatInterval(
                    beat_id=beat_id,
                    start_frame=start_frame,
                    end_frame=end_frame,
                    duration_frames=duration_frames,
                    section_type=section_type,
                    section_index=s_idx,
                    beat_index=b_idx,
                )
            )

        # Final safety adjustment: check if last segment didn't reach total duration due to clamping
        if timed_intervals and timed_intervals[-1].end_frame < total_duration_frames:
            last = timed_intervals[-1]
            timed_intervals[-1] = TimedBeatInterval(
                beat_id=last.beat_id,
                start_frame=last.start_frame,
                end_frame=total_duration_frames,
                duration_frames=total_duration_frames - last.start_frame,
                section_type=last.section_type,
                section_index=last.section_index,
                beat_index=last.beat_index,
            )

        return timed_intervals

