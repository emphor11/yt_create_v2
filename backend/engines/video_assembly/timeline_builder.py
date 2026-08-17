import re
from typing import Any, NamedTuple, Literal
from domain.hook import Hook
from domain.script_visual_strategy import ScriptVisualStrategy
from domain.voice_track import VoiceTrack

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
    # Trigger inside Polly word (e.g. trigger "106" inside Polly "106inr")
    if t_clean in p_clean:
        if len(t_clean) >= 3 or (t_clean.isdigit() and len(t_clean) >= 2):
            return True
            
    # Polly word inside Trigger (e.g. Polly "30" inside trigger "30-year")
    if p_clean in t_clean:
        if len(p_clean) >= 3 or (p_clean.isdigit() and len(p_clean) >= 2):
            return True
            
    return False

class TimelineBuilderError(Exception):
    """Raised when timeline generation fails, e.g. when a trigger word is missing."""

class TimedBeatInterval(NamedTuple):
    beat_id: str
    start_frame: int
    end_frame: int
    duration_frames: int
    section_type: Literal["hook", "body"]
    section_index: int
    beat_index: int

class TimelineBuilder:
    def __init__(self, fps: int = 30):
        self.fps = fps

    def build_timeline(
        self,
        *,
        hook: Hook,
        strategy: ScriptVisualStrategy,
        voice_track: VoiceTrack,
    ) -> list[TimedBeatInterval]:
        # 1. Collect narration texts for sections to align them against Polly words
        # Index 0: Hook
        section_texts: list[str] = [hook.script_text]
        # Index 1..N: Body Ideas
        for idea in strategy.ideas:
            section_texts.append(idea.narration)

        # 2. Extract Polly word timestamps sequence
        word_timestamps = voice_track.word_timestamps or []

        # 3. Align Polly words to sections using a sequential needle-pointer approach
        section_timestamps: list[list[Any]] = [[] for _ in section_texts]
        
        # Map word indices of the overall script to sections
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

        # 4. Compute timing bounds for each beat
        beat_time_bounds: list[tuple[float, float]] = []

        # Process Hook section
        hook_timestamps = section_timestamps[0]
        hook_beats = hook.visual_directives
        hook_beats_count = len(hook_beats)
        if hook_beats_count > 0:
            # Align hook beats using trigger words (same as body sections)
            hook_start_indices = [0]
            for b_idx in range(1, hook_beats_count):
                trigger = hook_beats[b_idx].trigger_word
                if not trigger or not trigger.strip():
                    raise TimelineBuilderError(
                        f"Beat '{hook_beats[b_idx].beat_id}' in hook requires trigger_word."
                    )
                
                cleaned_trigger = re.sub(r"[^\w]", "", trigger.lower())
                
                # Find matching word in hook timestamps starting from the last matched word
                match_idx = -1
                prev_start = hook_start_indices[-1]
                for idx in range(prev_start, len(hook_timestamps)):
                    if _is_word_match(hook_timestamps[idx].word, trigger):
                        match_idx = idx
                        break
                
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
        for s_idx, idea in enumerate(strategy.ideas):
            timestamps = section_timestamps[s_idx + 1]
            beats = idea.visual_sequence
            M = len(beats)
            if M == 0:
                continue

            # Build list of transition points (indices in the timestamps list)
            # Start of beat 0 is always start of section (timestamp index 0)
            beat_start_indices = [0]
            
            # Look up trigger words for subsequent beats
            for b_idx in range(1, M):
                trigger = beats[b_idx].trigger_word
                if not trigger or not trigger.strip():
                    raise TimelineBuilderError(
                        f"Beat '{beats[b_idx].beat_id}' in idea '{idea.idea_id}' requires trigger_word."
                    )
                
                cleaned_trigger = re.sub(r"[^\w]", "", trigger.lower())
                
                # Find matching word in section timestamps starting from the last matched word
                match_idx = -1
                prev_start = beat_start_indices[-1]
                for idx in range(prev_start, len(timestamps)):
                    if _is_word_match(timestamps[idx].word, trigger):
                        match_idx = idx
                        break
                
                if match_idx == -1:
                    raise TimelineBuilderError(
                        f"Trigger word '{trigger}' for beat '{beats[b_idx].beat_id}' in idea '{idea.idea_id}' "
                        f"was not found in the voice track words."
                    )
                
                beat_start_indices.append(match_idx)

            # Append total length as the end boundary
            beat_start_indices.append(len(timestamps))

            # Assign bounds to each beat
            for b_idx in range(M):
                start_idx = beat_start_indices[b_idx]
                end_idx = beat_start_indices[b_idx + 1]
                
                if start_idx < end_idx and start_idx < len(timestamps):
                    start_ms = float(timestamps[start_idx].start_ms)
                    # End time is end of the word before next starts, or end of section
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
        last_end_frame = 0

        # Construct flat list of beats metadata for index references
        flat_beat_refs = []
        # Hook index
        for b_idx, directive in enumerate(hook.visual_directives):
            flat_beat_refs.append(("hook", 0, b_idx, directive.beat_id))
        # Body ideas
        for s_idx, idea in enumerate(strategy.ideas):
            for b_idx, beat in enumerate(idea.visual_sequence):
                flat_beat_refs.append(("body", s_idx, b_idx, beat.beat_id))

        for idx, (section_type, s_idx, b_idx, beat_id) in enumerate(flat_beat_refs):
            raw_start_ms, raw_end_ms = beat_time_bounds[idx]

            start_frame = int(round((raw_start_ms / 1000.0) * self.fps))
            end_frame = int(round((raw_end_ms / 1000.0) * self.fps))

            # Maintain strict contiguity
            if idx == 0:
                start_frame = 0
            else:
                start_frame = last_end_frame

            # Enforce minimum duration constant
            end_frame = max(start_frame + MIN_BEAT_DURATION_FRAMES, end_frame)

            # Clamp the last beat to exact total duration
            if idx == len(flat_beat_refs) - 1:
                end_frame = total_duration_frames

            # Clamp if exceeded total duration
            if end_frame > total_duration_frames:
                end_frame = total_duration_frames

            duration_frames = end_frame - start_frame
            last_end_frame = end_frame

            timed_intervals.append(
                TimedBeatInterval(
                    beat_id=beat_id,
                    start_frame=start_frame,
                    end_frame=end_frame,
                    duration_frames=duration_frames,
                    section_type=section_type,
                    section_index=s_idx,
                    beat_index=b_idx
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
                beat_index=last.beat_index
            )

        return timed_intervals
