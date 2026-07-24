import re
from typing import Any, NamedTuple, Literal
from domain.hook import Hook
from domain.script_visual_strategy import ScriptVisualStrategy
from domain.voice_track import VoiceTrack

# Constant for minimum beat duration in frames (30fps: 15 frames = 0.5s)
MIN_BEAT_DURATION_FRAMES = 15

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
            words = [w.lower() for w in re.findall(r"\w+", text)]
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
        hook_beats_count = len(hook.visual_directives)
        if hook_beats_count > 0:
            # Since hook has no trigger_word fields, split timestamps proportionally
            hook_subgroups = self._split_timestamps_proportionally(
                timestamps=hook_timestamps,
                text=hook.script_text,
                num_beats=hook_beats_count,
            )
            for b_idx in range(hook_beats_count):
                sub = hook_subgroups[b_idx]
                if sub:
                    beat_time_bounds.append((float(sub[0].start_ms), float(sub[-1].end_ms)))
                else:
                    last_end = beat_time_bounds[-1][1] if beat_time_bounds else 0.0
                    beat_time_bounds.append((last_end, last_end))

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
                    cleaned_polly_word = re.sub(r"[^\w]", "", timestamps[idx].word.lower())
                    if cleaned_polly_word == cleaned_trigger:
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
                    last_end = beat_time_bounds[-1][1] if beat_time_bounds else 0.0
                    beat_time_bounds.append((last_end, last_end))

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

    @staticmethod
    def _split_timestamps_proportionally(
        timestamps: list[Any],
        text: str,
        num_beats: int,
    ) -> list[list[Any]]:
        # Split text into sentences
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
        if not sentences:
            sentences = [text]

        N = len(sentences)
        M = num_beats
        if N >= M:
            k, m = divmod(N, M)
            sentence_groups = [
                sentences[i * k + min(i, m) : (i + 1) * k + min(i + 1, m)]
                for i in range(M)
            ]
        else:
            sentence_groups = [[sentences[i]] if i < N else [] for i in range(M)]

        word_counts = []
        for group in sentence_groups:
            if group:
                combined_text = " ".join(group)
                word_counts.append(max(1, len(re.findall(r"\w+", combined_text))))
            else:
                word_counts.append(1)

        total_words_in_beats = sum(word_counts)
        total_timestamps = len(timestamps)

        subgroups = []
        curr_time_idx = 0
        for i, count in enumerate(word_counts):
            if total_words_in_beats > 0:
                share = int(round((count / total_words_in_beats) * total_timestamps))
            else:
                share = total_timestamps // M

            if share <= 0 and curr_time_idx < total_timestamps:
                share = 1

            if i == M - 1:
                end_time_idx = total_timestamps
            else:
                end_time_idx = min(curr_time_idx + share, total_timestamps)

            subgroups.append(timestamps[curr_time_idx:end_time_idx])
            curr_time_idx = end_time_idx

        return subgroups
