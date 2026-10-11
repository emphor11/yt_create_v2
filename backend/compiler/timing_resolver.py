"""Deterministic Voice Timing and Frame Resolver.

Resolves Storyboarder spoken trigger words against the authoritative VoiceTrack into exact frames.
Formula: trigger_frame = round(start_ms / 1000 * fps).
Strictly fails compilation if any required trigger word cannot be resolved.
"""
from __future__ import annotations

import re
from typing import NamedTuple
from compiler.models import VisualCompilerError
from domain.voice_track import VoiceTrack, WordTimestamp


def clean_word(token: str) -> str:
    """Normalizes a spoken token by stripping punctuation and lowercasing."""
    return re.sub(r"[^\w₹$%]", "", token.strip()).lower()


class ResolvedTrigger(NamedTuple):
    word: str
    occurrence: int
    start_ms: int
    end_ms: int
    trigger_frame: int
    global_trigger_frame: int


class TimingResolver:
    """Resolves spoken trigger words and scene durations against an authoritative VoiceTrack."""

    def __init__(self, voice_track: VoiceTrack, fps: int = 30):
        self.voice_track = voice_track
        self.fps = fps
        self.cleaned_timestamps = [
            (i, wt, clean_word(wt.word))
            for i, wt in enumerate(voice_track.word_timestamps)
        ]

    def resolve_scene_time_span(
        self,
        scene_id: str,
        scene_narration: str,
        start_search_index: int = 0,
    ) -> tuple[int, int, int]:
        """Finds the (start_ms, end_ms, next_search_index) span for a scene's narration."""
        narration_words = [clean_word(w) for w in scene_narration.split() if clean_word(w)]
        if not narration_words:
            # Fallback for empty narration
            return 0, int(self.voice_track.duration_seconds * 1000), len(self.voice_track.word_timestamps)

        # Match the first and last words of the scene within the voice track
        first_target = narration_words[0]
        last_target = narration_words[-1]

        # Find first matching word from start_search_index
        first_idx = None
        for i in range(start_search_index, len(self.cleaned_timestamps)):
            if self.cleaned_timestamps[i][2] == first_target:
                first_idx = i
                break

        if first_idx is None:
            # Wrap around or search from 0
            for i in range(len(self.cleaned_timestamps)):
                if self.cleaned_timestamps[i][2] == first_target:
                    first_idx = i
                    break

        if first_idx is None:
            first_idx = max(0, start_search_index)

        # Find last matching word after first_idx
        expected_span = len(narration_words)
        search_end = min(len(self.cleaned_timestamps), first_idx + expected_span + 5)
        last_idx = first_idx
        for i in range(first_idx, search_end):
            if self.cleaned_timestamps[i][2] == last_target:
                last_idx = i

        start_ms = self.voice_track.word_timestamps[first_idx].start_ms if self.voice_track.word_timestamps else 0
        end_ms = self.voice_track.word_timestamps[last_idx].end_ms if self.voice_track.word_timestamps else int(self.voice_track.duration_seconds * 1000)

        # Add modest padding (e.g. 400ms) after speech ends for pacing
        end_ms = min(int(self.voice_track.duration_seconds * 1000), end_ms + 400)
        return start_ms, end_ms, last_idx + 1

    def resolve_trigger(
        self,
        scene_id: str,
        scene_narration: str,
        trigger_word: str,
        trigger_occurrence: int = 1,
        scene_start_ms: int = 0,
    ) -> ResolvedTrigger:
        """Deterministically resolves a trigger word and occurrence into exact milliseconds and frame.

        Fails with VisualCompilerError if the trigger word cannot be resolved.
        """
        clean_target = clean_word(trigger_word)
        if not clean_target:
            raise VisualCompilerError(
                f"Invalid empty trigger word '{trigger_word}' in scene '{scene_id}'."
            )

        if trigger_occurrence < 1:
            raise VisualCompilerError(
                f"Invalid trigger occurrence {trigger_occurrence} for word '{trigger_word}' in scene '{scene_id}'."
            )

        # 1. Verify that the trigger word exists in the scene narration
        scene_words = [clean_word(w) for w in scene_narration.split() if clean_word(w)]
        narration_matches = [i for i, w in enumerate(scene_words) if w == clean_target]
        if not narration_matches:
            raise VisualCompilerError(
                f"Unresolved required trigger word '{trigger_word}' was not found in scene '{scene_id}' narration: '{scene_narration}'."
            )

        if trigger_occurrence > len(narration_matches):
            raise VisualCompilerError(
                f"Trigger word '{trigger_word}' in scene '{scene_id}' requests occurrence {trigger_occurrence}, "
                f"but only appears {len(narration_matches)} time(s) in narration."
            )

        # 2. Find matching words in VoiceTrack
        # Look for matches within or near the scene window
        matching_timestamps: list[WordTimestamp] = []
        for _, wt, w in self.cleaned_timestamps:
            if w == clean_target:
                matching_timestamps.append(wt)

        if not matching_timestamps:
            raise VisualCompilerError(
                f"Trigger word '{trigger_word}' exists in scene narration but was not found in VoiceTrack word timestamps."
            )

        # Find the occurrence relevant to this scene window
        scene_candidates = [
            wt for wt in matching_timestamps if wt.start_ms >= max(0, scene_start_ms - 200)
        ]

        target_timestamp: WordTimestamp
        if len(scene_candidates) >= trigger_occurrence:
            target_timestamp = scene_candidates[trigger_occurrence - 1]
        elif len(matching_timestamps) >= trigger_occurrence:
            target_timestamp = matching_timestamps[trigger_occurrence - 1]
        else:
            raise VisualCompilerError(
                f"Cannot resolve occurrence {trigger_occurrence} for trigger word '{trigger_word}' in VoiceTrack."
            )

        start_ms = target_timestamp.start_ms
        end_ms = target_timestamp.end_ms

        # Scene-relative frame (for scene composition starting at frame 0)
        rel_ms = max(0, start_ms - scene_start_ms)
        trigger_frame = round(rel_ms / 1000.0 * self.fps)
        global_trigger_frame = round(start_ms / 1000.0 * self.fps)

        return ResolvedTrigger(
            word=trigger_word,
            occurrence=trigger_occurrence,
            start_ms=start_ms,
            end_ms=end_ms,
            trigger_frame=trigger_frame,
            global_trigger_frame=global_trigger_frame,
        )
