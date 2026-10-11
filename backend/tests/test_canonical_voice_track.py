"""Focused unit tests for the Canonical VoiceTrack and timing contract.

Verifies:
A. SSML break tags (<break time="300ms"/>) are excluded from spoken content.
B. HTML entities (doesn&#x27;t) decode and match authoritative narration.
C. Multi-word timestamps ("nine point five to ten percent") preserved as single timed spans.
D. Mixed spans ([single word] + [multi-word phrase] + [single word]) resolve seamlessly.
E. Trigger word inside a multi-word span resolves to span start timing without false precision.
F. Ambiguous repeated narration fails deterministically with NarrationSpanAmbiguousError.
G. Punctuation and casing variations resolve deterministically.
H. Real project VoiceTrack timing resolution succeeds across all beats and speech triggers.
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
import pytest

from domain.timing_contract import (
    CanonicalVoiceTrack,
    MalformedCanonicalTimingSpanError,
    NarrationSpanAmbiguousError,
    NarrationSpanNotFoundError,
    TimedSpokenSpan,
    TimingResolutionError,
    TriggerWordAmbiguousError,
    TriggerWordNotFoundError,
    clean_spoken_token,
    is_ssml_token,
    normalize_for_search,
)
from domain.voice_track import VoiceTrack, WordTimestamp


# ==============================================================================
# Helper Factories
# ==============================================================================

def _make_voice_track(
    *,
    script: str,
    timestamps: list[tuple[str, int, int]],
    voice_id: str = "test-voice",
    duration_seconds: float = 10.0,
) -> VoiceTrack:
    return VoiceTrack(
        voice_id=voice_id,
        audio_file_name="test.mp3",
        storage_key="voice/test.mp3",
        duration_seconds=duration_seconds,
        full_script_text=script,
        word_timestamps=[
            WordTimestamp(word=w, start_ms=s, end_ms=e)
            for w, s, e in timestamps
        ],
    )


# ==============================================================================
# Test A: SSML Break Tags
# ==============================================================================

def test_ssml_break_tags_are_excluded_from_spoken_content() -> None:
    script = "You get a ten percent raise. That math doesn't add up."
    raw_timestamps = [
        ("You", 0, 200),
        ("get", 200, 400),
        ("a", 400, 500),
        ("ten", 500, 800),
        ("percent", 800, 1200),
        ("raise", 1200, 1600),
        ('<break time="300ms"/>', 1600, 1900),  # SSML tag
        ("That", 1900, 2200),
        ("math", 2200, 2500),
        ("doesn't", 2500, 2900),
        ("add", 2900, 3100),
        ("up", 3100, 3300),
    ]
    vt = _make_voice_track(script=script, timestamps=raw_timestamps)
    canonical = CanonicalVoiceTrack.from_voice_track(vt)

    # 1. SSML tag must not be present in spoken spans
    words = [s.word for s in canonical.spans]
    assert '<break time="300ms"/>' not in words
    assert all(not is_ssml_token(s.word) for s in canonical.spans)
    assert len(canonical.spans) == 11

    # 2. Narration across the break tag resolves continuously
    span = canonical.resolve_narration_span(
        beat_id="beat_01",
        narration=script,
    )
    assert span.start_ms == 0
    assert span.end_ms == 3300


# ==============================================================================
# Test B: HTML Entities
# ==============================================================================

def test_html_entities_decode_and_match_authoritative_narration() -> None:
    script = "That math doesn't add up."
    raw_timestamps = [
        ("That", 0, 200),
        ("math", 200, 500),
        ("doesn&#x27;t", 500, 900),  # Encoded apostrophe from Polly
        ("add", 900, 1100),
        ("up", 1100, 1300),
    ]
    vt = _make_voice_track(script=script, timestamps=raw_timestamps)
    canonical = CanonicalVoiceTrack.from_voice_track(vt)

    # Decoded word should be "doesn't"
    span_words = [s.word for s in canonical.spans]
    assert "doesn't" in span_words
    assert "doesn&#x27;t" not in span_words

    # Search representation should be normalized
    search_norm = [s.normalized_text for s in canonical.spans]
    assert "doesnt" in search_norm

    # Resolves cleanly against authoritative script
    span = canonical.resolve_narration_span(beat_id="beat_01", narration="That math doesn't add up.")
    assert span.start_ms == 0
    assert span.end_ms == 1300


# ==============================================================================
# Test C: Multi-Word Timestamps
# ==============================================================================

def test_multi_word_timestamps_preserved_as_single_honest_span() -> None:
    script = "Corporate increments are projected right around nine point five to ten percent on paper."
    raw_timestamps = [
        ("Corporate", 0, 400),
        ("increments", 400, 800),
        ("are", 800, 950),
        ("projected", 950, 1400),
        ("right", 1400, 1600),
        ("around", 1600, 1900),
        ("nine point five to ten percent", 1900, 3200),  # Single grouped timestamp
        ("on", 3200, 3350),
        ("paper", 3350, 3800),
    ]
    vt = _make_voice_track(script=script, timestamps=raw_timestamps)
    canonical = CanonicalVoiceTrack.from_voice_track(vt)

    # Must preserve one honest span, not invent 6 fake single-word timestamps
    grouped_span = next(s for s in canonical.spans if "nine point five" in s.word)
    assert grouped_span.word == "nine point five to ten percent"
    assert grouped_span.start_ms == 1900
    assert grouped_span.end_ms == 3200
    assert len(canonical.spans) == 9

    # Narration resolution across the multi-word span
    span = canonical.resolve_narration_span(beat_id="beat_02", narration=script)
    assert span.start_ms == 0
    assert span.end_ms == 3800


# ==============================================================================
# Test D: Mixed Spans
# ==============================================================================

def test_mixed_single_and_multi_word_spans_resolve_continuously() -> None:
    script = "The raise is instantly wiped out by inflation."
    raw_timestamps = [
        ("The", 0, 150),
        ("raise", 150, 450),
        ("is", 450, 600),
        ("instantly wiped out", 600, 1400),  # Multi-word phrase
        ("by", 1400, 1550),
        ("inflation", 1550, 2100),
    ]
    vt = _make_voice_track(script=script, timestamps=raw_timestamps)
    canonical = CanonicalVoiceTrack.from_voice_track(vt)

    span = canonical.resolve_narration_span(beat_id="beat_mixed", narration=script)
    assert span.start_ms == 0
    assert span.end_ms == 2100
    assert span.first_span_index == 0
    assert span.last_span_index == 5


# ==============================================================================
# Test E: Trigger Inside Multi-Word Span
# ==============================================================================

def test_trigger_word_inside_multi_word_span_returns_honest_span_timing() -> None:
    script = "The extra raise is instantly wiped out today."
    raw_timestamps = [
        ("The", 0, 200),
        ("extra", 200, 500),
        ("raise", 500, 800),
        ("is", 800, 950),
        ("instantly wiped out", 950, 1850),  # Contains "wiped"
        ("today", 1850, 2200),
    ]
    vt = _make_voice_track(script=script, timestamps=raw_timestamps)
    canonical = CanonicalVoiceTrack.from_voice_track(vt)

    beat_span = canonical.resolve_narration_span(beat_id="beat_03", narration=script)

    # Trigger word "wiped" inside "instantly wiped out"
    anchor = canonical.resolve_trigger_anchor(
        action_id="act_wiped",
        beat_id="beat_03",
        trigger_word="wiped",
        beat_span=beat_span,
    )
    assert anchor.start_ms == 950
    assert anchor.end_ms == 1850
    assert anchor.span_word == "instantly wiped out"


# ==============================================================================
# Test F: Ambiguous Repeated Narration
# ==============================================================================

def test_ambiguous_repeated_narration_fails_deterministically() -> None:
    script = "That math doesn't add up. Every year you check. That math doesn't add up."
    raw_timestamps = [
        ("That", 0, 200),
        ("math", 200, 400),
        ("doesn't", 400, 700),
        ("add", 700, 900),
        ("up", 900, 1100),
        ("Every", 1100, 1400),
        ("year", 1400, 1600),
        ("you", 1600, 1800),
        ("check", 1800, 2100),
        ("That", 2100, 2300),
        ("math", 2300, 2500),
        ("doesn't", 2500, 2800),
        ("add", 2800, 3000),
        ("up", 3000, 3200),
    ]
    vt = _make_voice_track(script=script, timestamps=raw_timestamps)
    canonical = CanonicalVoiceTrack.from_voice_track(vt)

    # Searching from 0 with repeated identical text without boundary fails with AmbiguousError
    with pytest.raises(NarrationSpanAmbiguousError) as exc_info:
        canonical.resolve_narration_span(
            beat_id="beat_dup",
            narration="That math doesn't add up.",
            search_start_char=0,
        )
    assert exc_info.value.match_count == 2
    assert "ambiguous" in str(exc_info.value).lower()


# ==============================================================================
# Test G: Punctuation and Casing Variation
# ==============================================================================

def test_punctuation_and_casing_variations_resolve_cleanly() -> None:
    script = "Taxation takes its share, and rent remains fixed!"
    raw_timestamps = [
        ("taxation", 0, 400),       # Lowercase
        ("takes", 400, 700),
        ("its", 700, 900),
        ("share", 900, 1200),
        ("and", 1200, 1350),
        ("rent", 1350, 1650),
        ("remains", 1650, 2000),
        ("fixed", 2000, 2400),
    ]
    vt = _make_voice_track(script=script, timestamps=raw_timestamps)
    canonical = CanonicalVoiceTrack.from_voice_track(vt)

    beat_span = canonical.resolve_narration_span(
        beat_id="beat_tax",
        narration="Taxation takes its share, and rent remains fixed!",
    )
    assert beat_span.start_ms == 0
    assert beat_span.end_ms == 2400

    # Trigger with uppercase "Taxation" against lowercase span
    anchor_tax = canonical.resolve_trigger_anchor(
        action_id="act_tax",
        beat_id="beat_tax",
        trigger_word="Taxation",
        beat_span=beat_span,
    )
    assert anchor_tax.start_ms == 0
    assert anchor_tax.span_word == "taxation"

    # Trigger with "Rent"
    anchor_rent = canonical.resolve_trigger_anchor(
        action_id="act_rent",
        beat_id="beat_tax",
        trigger_word="Rent",
        beat_span=beat_span,
    )
    assert anchor_rent.start_ms == 1350


# ==============================================================================
# Test Missing Trigger and Invalid Occurrence
# ==============================================================================

def test_missing_trigger_word_fails_loudly() -> None:
    script = "You get a ten percent raise on paper."
    raw_timestamps = [
        ("You", 0, 200),
        ("get", 200, 400),
        ("a", 400, 500),
        ("ten", 500, 800),
        ("percent", 800, 1200),
        ("raise", 1200, 1600),
        ("on", 1600, 1800),
        ("paper", 1800, 2200),
    ]
    vt = _make_voice_track(script=script, timestamps=raw_timestamps)
    canonical = CanonicalVoiceTrack.from_voice_track(vt)
    beat_span = canonical.resolve_narration_span(beat_id="b1", narration=script)

    with pytest.raises(TriggerWordNotFoundError) as exc_info:
        canonical.resolve_trigger_anchor(
            action_id="act_ghost",
            beat_id="b1",
            trigger_word="bonus",
            beat_span=beat_span,
        )
    assert "was not found" in str(exc_info.value)


def test_invalid_trigger_occurrence_fails_with_ambiguous_error() -> None:
    script = "You get a ten percent raise on paper."
    raw_timestamps = [
        ("You", 0, 200),
        ("get", 200, 400),
        ("a", 400, 500),
        ("ten", 500, 800),
        ("percent", 800, 1200),
        ("raise", 1200, 1600),
        ("on", 1600, 1800),
        ("paper", 1800, 2200),
    ]
    vt = _make_voice_track(script=script, timestamps=raw_timestamps)
    canonical = CanonicalVoiceTrack.from_voice_track(vt)
    beat_span = canonical.resolve_narration_span(beat_id="b1", narration=script)

    # "percent" occurs only once; occurrence=2 must fail
    with pytest.raises(TriggerWordAmbiguousError) as exc_info:
        canonical.resolve_trigger_anchor(
            action_id="act_pct2",
            beat_id="b1",
            trigger_word="percent",
            occurrence=2,
            beat_span=beat_span,
        )
    assert exc_info.value.occurrence == 2
    assert exc_info.value.match_count == 1


# ==============================================================================
# Test H: Real Project VoiceTrack Acceptance Test
# ==============================================================================

def test_real_project_voicetrack_resolves_all_beats_and_actions() -> None:
    db_path = Path("/Users/dakshyadav/Documents/YTcreate_V2/backend/.data/ytcreate_v2.db")
    if not db_path.exists():
        pytest.skip("SQLite database not found.")

    conn = sqlite3.connect(str(db_path))
    c = conn.cursor()
    c.execute(
        "SELECT payload_json FROM artifacts WHERE project_id = ? AND artifact_type = ?",
        ("project_3b357ab4412f4946b898960afacd6716", "voice_track"),
    )
    row = c.fetchone()
    conn.close()
    if not row:
        pytest.skip("Real VoiceTrack not found in database.")

    vt_dict = json.loads(row[0])
    voice_track = VoiceTrack.model_validate(vt_dict)

    artifact_path = Path("/Users/dakshyadav/.gemini/antigravity/brain/4d3bebca-deaf-4d89-b531-1f38803605d1/project_3b35_hardened_storyboard_result.json")
    if not artifact_path.exists():
        pytest.skip("Real VisualWorldSpec artifact not found.")

    with open(artifact_path) as f:
        world_data = json.load(f)

    # 1. Canonical conversion
    canonical = CanonicalVoiceTrack.from_voice_track(voice_track)
    assert len(canonical.spans) == 684  # All 5 SSML tags filtered out
    assert all(not is_ssml_token(s.word) for s in canonical.spans)

    # 2. Sequential beat resolution
    search_start_char = 0
    resolved_beats = {}
    for beat in world_data["beats"]:
        span = canonical.resolve_narration_span(
            beat_id=beat["beat_id"],
            narration=beat["narration"],
            search_start_char=search_start_char,
        )
        assert span.start_ms < span.end_ms
        assert len(span.matched_spans) > 0
        resolved_beats[beat["beat_id"]] = span
        search_start_char = span.end_char

    assert len(resolved_beats) == 8

    # 3. Action trigger words resolution
    for beat in world_data["beats"]:
        bid = beat["beat_id"]
        beat_span = resolved_beats[bid]
        for act in beat.get("actions", []):
            anchor = canonical.resolve_trigger_anchor(
                action_id=act["action_id"],
                beat_id=bid,
                trigger_word=act["trigger_word"],
                occurrence=act.get("trigger_occurrence", 1),
                beat_span=beat_span,
            )
            assert anchor.start_ms >= beat_span.start_ms
            assert anchor.end_ms <= beat_span.end_ms
            assert anchor.start_ms < anchor.end_ms
