"""Canonical voice timing contract and resolution architecture.

Defines the normalized, provider-agnostic representation of spoken audio timing,
decoupling compiler logic from raw TTS provider quirks (SSML markup, HTML entities,
compound multi-word timestamps, and provider-specific token grouping).
"""
from __future__ import annotations

import html
import re
from typing import Any
from pydantic import BaseModel, Field


# ==============================================================================
# Helper Normalizers
# ==============================================================================

def is_ssml_token(token: str) -> bool:
    """Check if token is an XML / SSML markup fragment (e.g. <break time="300ms"/>)."""
    t = token.strip()
    return t.startswith("<") and t.endswith(">")


def clean_spoken_token(token: str) -> str:
    """Decode HTML entities (e.g. doesn&#x27;t -> doesn't) and normalize whitespace."""
    if not token:
        return ""
    unescaped = html.unescape(token).strip()
    return " ".join(unescaped.split())


def normalize_for_search(text: str) -> str:
    """Deterministic normalization for search: lowercase alphanumeric + currency symbols."""
    cleaned = clean_spoken_token(text).lower()
    return re.sub(r"[^\w₹$%]", "", cleaned)


# ==============================================================================
# Canonical Timing Models
# ==============================================================================

class TimedSpokenSpan(BaseModel):
    """Canonical timed spoken span representing one or more spoken words."""
    word: str
    start_ms: int
    end_ms: int
    start_char: int | None = None
    end_char: int | None = None
    normalized_text: str | None = None


# Backward-compatible alias
WordTimestamp = TimedSpokenSpan


class ResolvedNarrationSpan(BaseModel):
    """Result of resolving a beat's narration against the canonical timeline."""
    beat_id: str
    start_ms: int
    end_ms: int
    start_char: int
    end_char: int
    first_span_index: int
    last_span_index: int
    matched_spans: list[TimedSpokenSpan] = Field(default_factory=list)


class ResolvedTriggerAnchor(BaseModel):
    """Result of resolving a speech trigger word against the canonical timeline."""
    action_id: str
    beat_id: str
    trigger_word: str
    occurrence: int
    start_ms: int
    end_ms: int
    span_word: str
    span_index: int


# ==============================================================================
# Deterministic Error Model
# ==============================================================================

class TimingResolutionError(Exception):
    """Base exception for all canonical voice timing resolution failures."""
    pass


class NarrationSpanNotFoundError(TimingResolutionError):
    """Raised when a beat narration substring cannot be located in the canonical script."""
    def __init__(
        self,
        *,
        requested_text: str,
        canonical_search_text: str,
        beat_id: str | None = None,
        world_id: str | None = None,
        source_span: str | None = None,
        message: str | None = None,
    ):
        self.requested_text = requested_text
        self.canonical_search_text = canonical_search_text
        self.beat_id = beat_id
        self.world_id = world_id
        self.source_span = source_span
        msg = message or (
            f"Narration span was not found for beat '{beat_id or 'unknown'}' "
            f"in world '{world_id or 'unknown'}'. "
            f"Requested: {requested_text!r}, search text: {canonical_search_text!r}, source span: {source_span}"
        )
        super().__init__(msg)


class NarrationSpanAmbiguousError(TimingResolutionError):
    """Raised when a beat narration substring matches multiple locations ambiguously."""
    def __init__(
        self,
        *,
        requested_text: str,
        canonical_search_text: str,
        match_count: int,
        beat_id: str | None = None,
        world_id: str | None = None,
        source_span: str | None = None,
        message: str | None = None,
    ):
        self.requested_text = requested_text
        self.canonical_search_text = canonical_search_text
        self.match_count = match_count
        self.beat_id = beat_id
        self.world_id = world_id
        self.source_span = source_span
        msg = message or (
            f"Narration span is ambiguous ({match_count} matches) for beat '{beat_id or 'unknown'}' "
            f"in world '{world_id or 'unknown'}'. "
            f"Requested: {requested_text!r}, search text: {canonical_search_text!r}, source span: {source_span}"
        )
        super().__init__(msg)


class TriggerWordNotFoundError(TimingResolutionError):
    """Raised when an action trigger word cannot be located within its beat's narration span."""
    def __init__(
        self,
        *,
        trigger_word: str,
        canonical_search_text: str,
        action_id: str | None = None,
        beat_id: str | None = None,
        world_id: str | None = None,
        source_span: str | None = None,
        message: str | None = None,
    ):
        self.trigger_word = trigger_word
        self.canonical_search_text = canonical_search_text
        self.action_id = action_id
        self.beat_id = beat_id
        self.world_id = world_id
        self.source_span = source_span
        msg = message or (
            f"Trigger word {trigger_word!r} was not found for action '{action_id or 'unknown'}' "
            f"in beat '{beat_id or 'unknown'}' (world '{world_id or 'unknown'}'). "
            f"Search text: {canonical_search_text!r}, source span: {source_span}"
        )
        super().__init__(msg)


class TriggerWordAmbiguousError(TimingResolutionError):
    """Raised when an action trigger word occurrence cannot be disambiguated."""
    def __init__(
        self,
        *,
        trigger_word: str,
        canonical_search_text: str,
        occurrence: int,
        match_count: int,
        action_id: str | None = None,
        beat_id: str | None = None,
        world_id: str | None = None,
        source_span: str | None = None,
        message: str | None = None,
    ):
        self.trigger_word = trigger_word
        self.canonical_search_text = canonical_search_text
        self.occurrence = occurrence
        self.match_count = match_count
        self.action_id = action_id
        self.beat_id = beat_id
        self.world_id = world_id
        self.source_span = source_span
        msg = message or (
            f"Trigger word {trigger_word!r} occurrence {occurrence} was not found or is ambiguous "
            f"({match_count} matches available) for action '{action_id or 'unknown'}' "
            f"in beat '{beat_id or 'unknown'}' (world '{world_id or 'unknown'}'). "
            f"Search text: {canonical_search_text!r}, source span: {source_span}"
        )
        super().__init__(msg)


class MalformedCanonicalTimingSpanError(TimingResolutionError):
    """Raised when a timing span in canonical voice track is malformed or inverted."""
    def __init__(
        self,
        *,
        span_info: str,
        details: str,
        world_id: str | None = None,
    ):
        self.span_info = span_info
        self.details = details
        self.world_id = world_id
        msg = f"Malformed canonical timing span in world '{world_id or 'unknown'}': {span_info}. Details: {details}"
        super().__init__(msg)


# ==============================================================================
# Canonical VoiceTrack Representation & Resolver
# ==============================================================================

class CanonicalVoiceTrack:
    """Canonical searchable narration and timing container.

    Decouples compiler beat and trigger resolution from provider-specific tokenization.
    """

    def __init__(
        self,
        *,
        voice_id: str,
        audio_file_name: str,
        storage_key: str,
        duration_seconds: float,
        full_script_text: str,
        spans: list[TimedSpokenSpan],
    ) -> None:
        self.voice_id = voice_id
        self.audio_file_name = audio_file_name
        self.storage_key = storage_key
        self.duration_seconds = duration_seconds
        self.full_script_text = full_script_text
        self.spans = spans
        self._validate_spans()

    def _validate_spans(self) -> None:
        for idx, span in enumerate(self.spans):
            if span.start_ms < 0 or span.end_ms < 0:
                raise MalformedCanonicalTimingSpanError(
                    span_info=f"span[{idx}]='{span.word}' ({span.start_ms}-{span.end_ms})",
                    details="Negative start or end milliseconds.",
                )
            if span.start_ms > span.end_ms:
                raise MalformedCanonicalTimingSpanError(
                    span_info=f"span[{idx}]='{span.word}' ({span.start_ms}-{span.end_ms})",
                    details="start_ms is greater than end_ms (inverted timing span).",
                )

    @classmethod
    def from_voice_track(cls, voice_track: Any) -> CanonicalVoiceTrack:
        """Constructs a normalized CanonicalVoiceTrack from any raw or existing VoiceTrack."""
        raw_words = getattr(voice_track, "word_timestamps", []) or []
        script = getattr(voice_track, "full_script_text", "") or ""

        # 1. Filter out SSML markup and decode HTML entities
        cleaned_spans: list[TimedSpokenSpan] = []
        for raw in raw_words:
            w = getattr(raw, "word", "")
            if not isinstance(w, str) or is_ssml_token(w):
                continue
            cleaned = clean_spoken_token(w)
            if not cleaned:
                continue

            cleaned_spans.append(
                TimedSpokenSpan(
                    word=cleaned,
                    start_ms=raw.start_ms,
                    end_ms=raw.end_ms,
                    start_char=raw.start_char,
                    end_char=raw.end_char,
                    normalized_text=normalize_for_search(cleaned),
                )
            )

        # 2. Align characters to full_script_text if missing or invalid
        if script:
            cls._align_spans_to_script(script, cleaned_spans)

        return cls(
            voice_id=voice_track.voice_id,
            audio_file_name=voice_track.audio_file_name,
            storage_key=voice_track.storage_key,
            duration_seconds=voice_track.duration_seconds,
            full_script_text=script,
            spans=cleaned_spans,
        )

    @staticmethod
    def _align_spans_to_script(script: str, spans: list[TimedSpokenSpan]) -> None:
        """Deterministically assigns start_char and end_char offsets into full_script_text."""
        current_pos = 0
        script_lower = script.lower()

        for span in spans:
            if span.start_char is not None and span.end_char is not None and span.end_char <= len(script):
                current_pos = span.end_char
                continue

            token_words = span.word.split()
            first_clean = re.sub(r"^[^\w₹$%]+|[^\w₹$%]+$", "", token_words[0]).lower()
            last_clean = re.sub(r"^[^\w₹$%]+|[^\w₹$%]+$", "", token_words[-1]).lower()

            target_first = first_clean if first_clean else token_words[0].lower()
            m_start = script_lower.find(target_first, current_pos)
            if m_start == -1 and current_pos > 0:
                # Wrap-around search if minor misalignment occurred
                m_start = script_lower.find(target_first, max(0, current_pos - 30))

            if m_start != -1:
                if len(token_words) == 1:
                    m_end = m_start + len(first_clean if first_clean else token_words[0])
                else:
                    target_last = last_clean if last_clean else token_words[-1].lower()
                    m_last = script_lower.find(target_last, m_start)
                    if m_last != -1:
                        m_end = m_last + len(last_clean if last_clean else token_words[-1])
                    else:
                        m_end = m_start + len(first_clean if first_clean else token_words[0])
                span.start_char = m_start
                span.end_char = m_end
                current_pos = m_end
            else:
                span.start_char = current_pos
                span.end_char = current_pos

    def resolve_narration_span(
        self,
        *,
        beat_id: str,
        narration: str,
        search_start_char: int = 0,
        world_id: str | None = None,
    ) -> ResolvedNarrationSpan:
        """Deterministically locates a beat's narration span in the canonical voice timeline."""
        clean_narr = narration.strip()
        if not clean_narr:
            raise NarrationSpanNotFoundError(
                requested_text=narration,
                canonical_search_text="",
                beat_id=beat_id,
                world_id=world_id,
                message=f"Beat '{beat_id}' has empty narration text.",
            )

        script = self.full_script_text
        norm_narr_search = normalize_for_search(clean_narr)

        # 1. Exact substring match in full_script_text
        match_start = script.find(clean_narr, search_start_char)

        if match_start == -1:
            # 2. Whitespace-flexible regex match
            escaped_words = [re.escape(w) for w in clean_narr.split()]
            pattern = re.compile(r"\s+".join(escaped_words), re.IGNORECASE)
            regex_matches = list(pattern.finditer(script, search_start_char))
            if len(regex_matches) == 1:
                match_start = regex_matches[0].start()
                match_end = regex_matches[0].end()
            elif len(regex_matches) > 1:
                raise NarrationSpanAmbiguousError(
                    requested_text=clean_narr,
                    canonical_search_text=norm_narr_search,
                    match_count=len(regex_matches),
                    beat_id=beat_id,
                    world_id=world_id,
                    source_span=f"search_from_char={search_start_char}",
                )
            else:
                # 3. Global search check for ambiguity or total absence
                global_matches = list(pattern.finditer(script))
                if len(global_matches) > 1:
                    raise NarrationSpanAmbiguousError(
                        requested_text=clean_narr,
                        canonical_search_text=norm_narr_search,
                        match_count=len(global_matches),
                        beat_id=beat_id,
                        world_id=world_id,
                        source_span="global_script_search",
                    )
                raise NarrationSpanNotFoundError(
                    requested_text=clean_narr,
                    canonical_search_text=norm_narr_search,
                    beat_id=beat_id,
                    world_id=world_id,
                    source_span=f"search_from_char={search_start_char}",
                )
        else:
            match_end = match_start + len(clean_narr)
            # Check for ambiguity if search_start_char is 0 or multiple identical occurrences exist
            if search_start_char == 0:
                second_match = script.find(clean_narr, match_end)
                if second_match != -1:
                    # Multiple identical matches without distinct search boundaries
                    count = script.count(clean_narr)
                    raise NarrationSpanAmbiguousError(
                        requested_text=clean_narr,
                        canonical_search_text=norm_narr_search,
                        match_count=count,
                        beat_id=beat_id,
                        world_id=world_id,
                        source_span="script_global",
                    )

        # 4. Find all overlapping spans
        matched_spans: list[TimedSpokenSpan] = []
        first_idx: int | None = None
        last_idx: int | None = None

        for idx, span in enumerate(self.spans):
            s_start = span.start_char if span.start_char is not None else 0
            s_end = span.end_char if span.end_char is not None else s_start
            if s_start < match_end and s_end > match_start:
                matched_spans.append(span)
                if first_idx is None:
                    first_idx = idx
                last_idx = idx

        if not matched_spans or first_idx is None or last_idx is None:
            raise NarrationSpanNotFoundError(
                requested_text=clean_narr,
                canonical_search_text=norm_narr_search,
                beat_id=beat_id,
                world_id=world_id,
                source_span=f"chars [{match_start}:{match_end}]",
                message=f"No timed spoken spans cover beat '{beat_id}' char span [{match_start}:{match_end}].",
            )

        return ResolvedNarrationSpan(
            beat_id=beat_id,
            start_ms=matched_spans[0].start_ms,
            end_ms=matched_spans[-1].end_ms,
            start_char=match_start,
            end_char=match_end,
            first_span_index=first_idx,
            last_span_index=last_idx,
            matched_spans=matched_spans,
        )

    def resolve_trigger_anchor(
        self,
        *,
        action_id: str,
        beat_id: str,
        trigger_word: str,
        occurrence: int = 1,
        beat_span: ResolvedNarrationSpan,
        world_id: str | None = None,
    ) -> ResolvedTriggerAnchor:
        """Deterministically resolves a trigger word and occurrence to a canonical span timestamp."""
        clean_trig = trigger_word.strip()
        norm_trig_search = normalize_for_search(clean_trig)
        if not clean_trig or not norm_trig_search:
            raise TriggerWordNotFoundError(
                trigger_word=trigger_word,
                canonical_search_text="",
                action_id=action_id,
                beat_id=beat_id,
                world_id=world_id,
                message=f"Action '{action_id}' in beat '{beat_id}' has empty trigger word.",
            )

        script = self.full_script_text
        beat_text = script[beat_span.start_char:beat_span.end_char]

        # 1. Search trigger word in beat text (word boundary first, then whole token)
        pattern = re.compile(r"\b" + re.escape(clean_trig) + r"\b", re.IGNORECASE)
        matches = list(pattern.finditer(beat_text))
        if not matches:
            # Fallback substring in beat text
            pattern_sub = re.compile(re.escape(clean_trig), re.IGNORECASE)
            matches = list(pattern_sub.finditer(beat_text))

        if not matches:
            # Also check across span normalized texts
            span_matches = [
                (idx, s) for idx, s in enumerate(beat_span.matched_spans)
                if norm_trig_search in (s.normalized_text or "")
            ]
            if span_matches:
                if occurrence < 1 or occurrence > len(span_matches):
                    raise TriggerWordAmbiguousError(
                        trigger_word=clean_trig,
                        canonical_search_text=norm_trig_search,
                        occurrence=occurrence,
                        match_count=len(span_matches),
                        action_id=action_id,
                        beat_id=beat_id,
                        world_id=world_id,
                    )
                target_idx, target_span = span_matches[occurrence - 1]
                return ResolvedTriggerAnchor(
                    action_id=action_id,
                    beat_id=beat_id,
                    trigger_word=clean_trig,
                    occurrence=occurrence,
                    start_ms=target_span.start_ms,
                    end_ms=target_span.end_ms,
                    span_word=target_span.word,
                    span_index=beat_span.first_span_index + target_idx,
                )

            raise TriggerWordNotFoundError(
                trigger_word=clean_trig,
                canonical_search_text=norm_trig_search,
                action_id=action_id,
                beat_id=beat_id,
                world_id=world_id,
                source_span=f"beat [{beat_span.start_char}:{beat_span.end_char}]",
            )

        if occurrence < 1 or occurrence > len(matches):
            raise TriggerWordAmbiguousError(
                trigger_word=clean_trig,
                canonical_search_text=norm_trig_search,
                occurrence=occurrence,
                match_count=len(matches),
                action_id=action_id,
                beat_id=beat_id,
                world_id=world_id,
                source_span=f"beat [{beat_span.start_char}:{beat_span.end_char}]",
            )

        match = matches[occurrence - 1]
        tw_char_pos = beat_span.start_char + match.start()

        # 2. Find which span covers tw_char_pos
        selected_span: TimedSpokenSpan | None = None
        selected_span_idx = beat_span.first_span_index

        for idx, span in enumerate(beat_span.matched_spans):
            s_start = span.start_char if span.start_char is not None else 0
            s_end = span.end_char if span.end_char is not None else s_start
            if s_start <= tw_char_pos <= s_end or norm_trig_search in (span.normalized_text or ""):
                selected_span = span
                selected_span_idx = beat_span.first_span_index + idx
                break

        if selected_span is None:
            # Fallback to nearest span in beat
            selected_span = beat_span.matched_spans[0]
            selected_span_idx = beat_span.first_span_index

        return ResolvedTriggerAnchor(
            action_id=action_id,
            beat_id=beat_id,
            trigger_word=clean_trig,
            occurrence=occurrence,
            start_ms=selected_span.start_ms,
            end_ms=selected_span.end_ms,
            span_word=selected_span.word,
            span_index=selected_span_idx,
        )
