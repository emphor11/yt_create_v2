import base64
import json
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

from domain.tts_chunk import TTSChunk, TTSChunkResult
from domain.voice_track import VoiceTrack, WordTimestamp
from domain.validation import ValidationResult
from domain.validators.voice_track_validator import VoiceTrackValidator
from engines.audio_merger import (
    AudioConcatCompatibilityError,
    AudioDurationMismatchError,
    AudioMergeError,
    AudioMerger,
    AudioStreamInfo,
    polly_byte_to_char_offset,
)
from tests.test_polly_chunk_synthesis import VALID_24KHZ_MP3_BYTES, _mock_polly_client


def _write_mp3(path: Path, data: bytes = VALID_24KHZ_MP3_BYTES) -> Path:
    """Helper to write MP3 bytes to a file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)
    return path


# =========================================================================
# Test A: One chunk (offset zero, timestamps unchanged, valid master audio)
# =========================================================================
def test_a_single_chunk_merge(tmp_path: Path):
    audio_file = _write_mp3(tmp_path / "chunk_001.mp3")
    chunk = TTSChunkResult(
        chunk_id="chunk_001",
        sequence=1,
        source_id="hook",
        text="Single chunk narration text.",
        audio_path=str(audio_file),
        word_timestamps=[
            {"word": "Single", "start_ms": 100, "end_ms": 300, "start_char": 0, "end_char": 6},
            {"word": "chunk", "start_ms": 350, "end_ms": 600, "start_char": 7, "end_char": 12},
        ],
        duration_ms=800,
        duration_seconds=0.8,
    )

    merger = AudioMerger()
    output_path = tmp_path / "master" / "narration.mp3"
    duration_sec, global_ts = merger.merge_chunks([chunk], output_path)

    # 1. Valid master audio is produced
    assert output_path.exists()
    assert output_path.stat().st_size > 0
    assert duration_sec == 0.8

    # 2. Offset is zero; timestamps match local timestamps exactly
    assert len(global_ts) == 2
    assert global_ts[0].word == "Single"
    assert global_ts[0].start_ms == 100
    assert global_ts[0].end_ms == 300
    assert global_ts[0].start_char == 0
    assert global_ts[0].end_char == 6

    assert global_ts[1].word == "chunk"
    assert global_ts[1].start_ms == 350
    assert global_ts[1].end_ms == 600


# =========================================================================
# Test B: Two chunks (chunk 2 timestamps shifted by chunk 1 actual duration)
# =========================================================================
def test_b_two_chunks_timestamp_shift(tmp_path: Path):
    c1_audio = _write_mp3(tmp_path / "c1.mp3")
    c2_audio = _write_mp3(tmp_path / "c2.mp3")

    chunk_1 = TTSChunkResult(
        chunk_id="chunk_001",
        sequence=1,
        source_id="hook",
        text="Welcome back.",
        audio_path=str(c1_audio),
        word_timestamps=[
            {"word": "Welcome", "start_ms": 50, "end_ms": 350},
            {"word": "back", "start_ms": 400, "end_ms": 700},
        ],
        duration_ms=1000,
        duration_seconds=1.0,
    )
    chunk_2 = TTSChunkResult(
        chunk_id="chunk_002",
        sequence=2,
        source_id="idea_01",
        text="Today we learn.",
        audio_path=str(c2_audio),
        word_timestamps=[
            {"word": "Today", "start_ms": 100, "end_ms": 400},
            {"word": "we", "start_ms": 450, "end_ms": 600},
            {"word": "learn", "start_ms": 650, "end_ms": 900},
        ],
        duration_ms=1200,
        duration_seconds=1.2,
    )

    merger = AudioMerger()
    global_ts = merger.compute_global_word_timestamps([chunk_1, chunk_2])

    assert len(global_ts) == 5

    # Chunk 1 (offset = 0)
    assert global_ts[0].word == "Welcome"
    assert global_ts[0].start_ms == 50
    assert global_ts[0].end_ms == 350
    assert global_ts[1].word == "back"
    assert global_ts[1].start_ms == 400
    assert global_ts[1].end_ms == 700

    # Chunk 2 (offset = chunk_1.duration_ms = 1000)
    assert global_ts[2].word == "Today"
    assert global_ts[2].start_ms == 1000 + 100  # 1100
    assert global_ts[2].end_ms == 1000 + 400    # 1400

    assert global_ts[3].word == "we"
    assert global_ts[3].start_ms == 1000 + 450  # 1450
    assert global_ts[3].end_ms == 1000 + 600    # 1600

    assert global_ts[4].word == "learn"
    assert global_ts[4].start_ms == 1000 + 650  # 1650
    assert global_ts[4].end_ms == 1000 + 900    # 1900


# =========================================================================
# Test C: Three chunks (chunk 3 shifted by duration(1) + duration(2))
# =========================================================================
def test_c_three_chunks_cumulative_offsets(tmp_path: Path):
    chunks = [
        TTSChunkResult(
            chunk_id="chunk_001",
            sequence=1,
            source_id="hook",
            text="First chunk.",
            audio_path=str(tmp_path / "c1.mp3"),
            word_timestamps=[{"word": "First", "start_ms": 100, "end_ms": 400}],
            duration_ms=1500,
            duration_seconds=1.5,
        ),
        TTSChunkResult(
            chunk_id="chunk_002",
            sequence=2,
            source_id="idea_01",
            text="Second chunk.",
            audio_path=str(tmp_path / "c2.mp3"),
            word_timestamps=[{"word": "Second", "start_ms": 200, "end_ms": 500}],
            duration_ms=2500,
            duration_seconds=2.5,
        ),
        TTSChunkResult(
            chunk_id="chunk_003",
            sequence=3,
            source_id="idea_02",
            text="Third chunk.",
            audio_path=str(tmp_path / "c3.mp3"),
            word_timestamps=[{"word": "Third", "start_ms": 150, "end_ms": 450}],
            duration_ms=2000,
            duration_seconds=2.0,
        ),
    ]

    merger = AudioMerger()
    global_ts = merger.compute_global_word_timestamps(chunks)

    # Chunk 1: offset = 0
    assert global_ts[0].start_ms == 100
    assert global_ts[0].end_ms == 400

    # Chunk 2: offset = 1500
    assert global_ts[1].start_ms == 1500 + 200  # 1700
    assert global_ts[1].end_ms == 1500 + 500    # 2000

    # Chunk 3: offset = 1500 + 2500 = 4000
    assert global_ts[2].word == "Third"
    assert global_ts[2].start_ms == 4000 + 150  # 4150
    assert global_ts[2].end_ms == 4000 + 450    # 4450


# =========================================================================
# Test D: Last speech mark earlier than actual chunk duration
# =========================================================================
def test_d_offset_uses_actual_audio_duration_not_last_speech_mark(tmp_path: Path):
    """
    CRITICAL DRIFT TEST:
    Polly speech marks end at 1800ms, but physical audio has trailing silence ending at 2400ms.
    The next chunk MUST offset by 2400ms, NOT 1800ms.
    """
    chunk_1 = TTSChunkResult(
        chunk_id="chunk_001",
        sequence=1,
        source_id="hook",
        text="Last word ends early.",
        audio_path=str(tmp_path / "c1.mp3"),
        word_timestamps=[
            {"word": "Last", "start_ms": 100, "end_ms": 400},
            {"word": "early", "start_ms": 1400, "end_ms": 1800},  # Last mark ends at 1800ms
        ],
        duration_ms=2400,  # Actual audio duration is 2400ms (600ms trailing pause)
        duration_seconds=2.4,
    )
    chunk_2 = TTSChunkResult(
        chunk_id="chunk_002",
        sequence=2,
        source_id="idea_01",
        text="Next begins here.",
        audio_path=str(tmp_path / "c2.mp3"),
        word_timestamps=[
            {"word": "Next", "start_ms": 50, "end_ms": 300},
        ],
        duration_ms=1000,
        duration_seconds=1.0,
    )

    merger = AudioMerger()
    global_ts = merger.compute_global_word_timestamps([chunk_1, chunk_2])

    # Next chunk's "Next" must be at 2400 + 50 = 2450ms, NOT 1800 + 50 = 1850ms!
    next_word = global_ts[2]
    assert next_word.word == "Next"
    assert next_word.start_ms == 2450
    assert next_word.start_ms != 1850


# =========================================================================
# Test E: Chunk ordering (master order identical to chunk sequence)
# =========================================================================
def test_e_chunk_ordering_preserves_sequence_regardless_of_input_order(tmp_path: Path):
    # Pass chunks in scrambled input order
    scrambled = [
        TTSChunkResult(
            chunk_id="chunk_003",
            sequence=3,
            source_id="idea_02",
            text="Conclusion.",
            audio_path=str(tmp_path / "c3.mp3"),
            word_timestamps=[{"word": "Conclusion", "start_ms": 100, "end_ms": 400}],
            duration_ms=1000,
            duration_seconds=1.0,
        ),
        TTSChunkResult(
            chunk_id="chunk_001",
            sequence=1,
            source_id="hook",
            text="Intro.",
            audio_path=str(tmp_path / "c1.mp3"),
            word_timestamps=[{"word": "Intro", "start_ms": 100, "end_ms": 300}],
            duration_ms=1000,
            duration_seconds=1.0,
        ),
        TTSChunkResult(
            chunk_id="chunk_002",
            sequence=2,
            source_id="idea_01",
            text="Body.",
            audio_path=str(tmp_path / "c2.mp3"),
            word_timestamps=[{"word": "Body", "start_ms": 100, "end_ms": 350}],
            duration_ms=1000,
            duration_seconds=1.0,
        ),
    ]

    merger = AudioMerger()
    global_ts = merger.compute_global_word_timestamps(scrambled)

    words = [t.word for t in global_ts]
    assert words == ["Intro", "Body", "Conclusion"]
    assert global_ts[0].start_ms == 100
    assert global_ts[1].start_ms == 1100
    assert global_ts[2].start_ms == 2100


# =========================================================================
# Test F: Global timestamp monotonicity
# =========================================================================
def test_f_global_timestamp_monotonicity(tmp_path: Path):
    chunk_1 = TTSChunkResult(
        chunk_id="chunk_001",
        sequence=1,
        source_id="hook",
        text="Chunk one words.",
        audio_path=str(tmp_path / "c1.mp3"),
        word_timestamps=[
            {"word": "Chunk", "start_ms": 0, "end_ms": 200},
            {"word": "one", "start_ms": 200, "end_ms": 400},
            {"word": "words", "start_ms": 400, "end_ms": 600},
        ],
        duration_ms=600,
        duration_seconds=0.6,
    )
    # Chunk 2 starts immediately with zero delay
    chunk_2 = TTSChunkResult(
        chunk_id="chunk_002",
        sequence=2,
        source_id="idea_01",
        text="Chunk two words.",
        audio_path=str(tmp_path / "c2.mp3"),
        word_timestamps=[
            {"word": "Chunk", "start_ms": 0, "end_ms": 200},
            {"word": "two", "start_ms": 200, "end_ms": 400},
            {"word": "words", "start_ms": 400, "end_ms": 600},
        ],
        duration_ms=600,
        duration_seconds=0.6,
    )

    merger = AudioMerger()
    global_ts = merger.compute_global_word_timestamps([chunk_1, chunk_2])

    for i in range(len(global_ts) - 1):
        # Monotonically non-decreasing start times
        assert global_ts[i].start_ms <= global_ts[i + 1].start_ms
        # Monotonically non-overlapping or boundary-aligned
        assert global_ts[i].end_ms <= global_ts[i + 1].start_ms


# =========================================================================
# Test G: Audio duration consistency
# =========================================================================
def test_g_audio_duration_consistency_validates_within_tolerance(tmp_path: Path):
    c1 = _write_mp3(tmp_path / "c1.mp3")
    c2 = _write_mp3(tmp_path / "c2.mp3")

    chunk_1 = TTSChunkResult(
        chunk_id="chunk_001",
        sequence=1,
        source_id="hook",
        text="One",
        audio_path=str(c1),
        duration_ms=200,
        duration_seconds=0.2,
    )
    chunk_2 = TTSChunkResult(
        chunk_id="chunk_002",
        sequence=2,
        source_id="idea_01",
        text="Two",
        audio_path=str(c2),
        duration_ms=200,
        duration_seconds=0.2,
    )

    merger = AudioMerger(default_tolerance_ms=200)
    output_path = tmp_path / "master.mp3"
    master_sec, _ = merger.merge_chunks([chunk_1, chunk_2], output_path)

    assert output_path.exists()
    assert master_sec > 0.35  # ~0.4s combined

    # Now verify failure when duration deviates beyond tolerance
    with patch.object(merger, "_measure_duration", return_value=(5.0, 5000)):
        with pytest.raises(AudioDurationMismatchError) as exc_info:
            merger.merge_chunks([chunk_1, chunk_2], output_path, tolerance_ms=100)

        err = exc_info.value
        assert err.master_duration_ms == 5000
        assert err.expected_duration_ms == 400
        assert err.tolerance_ms == 100


# =========================================================================
# Test H: Incompatible audio stream parameters
# =========================================================================
def test_h_incompatible_audio_streams_fail_with_structured_error(tmp_path: Path):
    c1 = _write_mp3(tmp_path / "c1.mp3")
    c2 = _write_mp3(tmp_path / "c2.mp3")

    chunk_1 = TTSChunkResult(
        chunk_id="chunk_001",
        sequence=1,
        source_id="hook",
        text="Part 1",
        audio_path=str(c1),
        duration_ms=500,
    )
    chunk_2 = TTSChunkResult(
        chunk_id="chunk_002",
        sequence=2,
        source_id="idea_01",
        text="Part 2",
        audio_path=str(c2),
        duration_ms=500,
    )

    merger = AudioMerger()

    # 1. Sample rate mismatch
    with patch.object(
        merger,
        "probe_audio",
        side_effect=[
            AudioStreamInfo(codec_name="mp3", sample_rate=24000, channels=1, format_name="mp3"),
            AudioStreamInfo(codec_name="mp3", sample_rate=44100, channels=1, format_name="mp3"),
        ],
    ):
        with pytest.raises(AudioConcatCompatibilityError) as exc_info:
            merger.verify_stream_compatibility([chunk_1, chunk_2])
        err = exc_info.value
        assert err.incompatible_property == "sample_rate"
        assert err.chunk_1_value == 24000
        assert err.chunk_2_value == 44100

    # 2. Channels mismatch
    with patch.object(
        merger,
        "probe_audio",
        side_effect=[
            AudioStreamInfo(codec_name="mp3", sample_rate=24000, channels=1, format_name="mp3"),
            AudioStreamInfo(codec_name="mp3", sample_rate=24000, channels=2, format_name="mp3"),
        ],
    ):
        with pytest.raises(AudioConcatCompatibilityError) as exc_info:
            merger.verify_stream_compatibility([chunk_1, chunk_2])
        err = exc_info.value
        assert err.incompatible_property == "channels"
        assert err.chunk_1_value == 1
        assert err.chunk_2_value == 2

    # 3. Codec mismatch
    with patch.object(
        merger,
        "probe_audio",
        side_effect=[
            AudioStreamInfo(codec_name="mp3", sample_rate=24000, channels=1, format_name="mp3"),
            AudioStreamInfo(codec_name="aac", sample_rate=24000, channels=1, format_name="aac"),
        ],
    ):
        with pytest.raises(AudioConcatCompatibilityError) as exc_info:
            merger.verify_stream_compatibility([chunk_1, chunk_2])
        err = exc_info.value
        assert err.incompatible_property == "codec_name"
        assert err.chunk_1_value == "mp3"
        assert err.chunk_2_value == "aac"


# =========================================================================
# Test I: Exact narration preservation
# =========================================================================
def test_i_exact_narration_preservation_in_voice_generation_handler(tmp_path: Path):
    from artifact_store.sqlite_store import ArtifactStore
    from app.stage_handlers.voice_generation_handler import VoiceGenerationHandler
    from app.stage_logger import StageLogger
    from engines.tts_chunker import TTSChunker
    from providers.media_storage import LocalMediaStorage
    from providers.voice_provider import PollyVoiceProvider

    store = ArtifactStore(tmp_path / "voice_exact.db")
    store.initialize()
    media = LocalMediaStorage(tmp_path / "media")
    logger = StageLogger()

    project = store.create_project("Exact Text Project")
    run = store.create_run(project.id, mode="ai")

    source_hook = "The market rose 3.2% in January. Investors became optimistic."
    source_idea_1 = "Dr. Powell stated, 'Rates may remain steady at 5.25%.' But uncertainty persists."
    source_idea_2 = "By Q3 2026, tech valuations shifted by $450B."

    store.save_artifact(
        project_id=project.id,
        run_id=run.id,
        artifact_type="hook",
        schema_version="1",
        payload_json={"conceptual_hook": "Hook", "script_text": source_hook},
        parent_artifact_roles_json={},
        validation_json=ValidationResult(status="valid"),
    )
    store.save_artifact(
        project_id=project.id,
        run_id=run.id,
        artifact_type="script_visual_strategy",
        schema_version="1",
        payload_json={
            "thesis": "Thesis",
            "ideas": [
                {"idea_id": "idea_01", "title": "T1", "focus_concept": "C1", "core_teaching_point": "P1", "narration": source_idea_1, "visual_sequence": []},
                {"idea_id": "idea_02", "title": "T2", "focus_concept": "C2", "core_teaching_point": "P2", "narration": source_idea_2, "visual_sequence": []},
            ],
        },
        parent_artifact_roles_json={},
        validation_json=ValidationResult(status="valid"),
    )
    store.save_artifact(
        project_id=project.id,
        run_id=run.id,
        artifact_type="review_result",
        schema_version="1",
        payload_json={"approved": True, "checks": []},
        parent_artifact_roles_json={},
        validation_json=ValidationResult(status="valid"),
    )

    expected_full_script = f"{source_hook}\n\n{source_idea_1}\n\n{source_idea_2}"

    mock_client = _mock_polly_client()
    provider = PollyVoiceProvider()
    handler = VoiceGenerationHandler(
        store=store,
        media_storage=media,
        voice_provider=provider,
        voice_validator=VoiceTrackValidator(),
        stage_logger=logger,
        chunker=TTSChunker(safe_max_chars=60),
    )

    with patch("boto3.client", return_value=mock_client):
        artifact = handler.run(project.id, run.id)

    payload = artifact.payload_json
    # Exact narration preservation check
    assert payload["full_script_text"] == expected_full_script
    # Individual chunks preserved
    assert len(payload["chunks"]) >= 3
    # Master audio path exists
    assert Path(media.path_for_key(payload["storage_key"])).exists()
    # Word timestamps are global
    assert len(payload["word_timestamps"]) > 0


# =========================================================================
# Test J: Unicode and byte-offset behavior
# =========================================================================
def test_j_unicode_byte_offset_semantics_not_treated_as_character_indexes():
    """
    Verifies that AWS Polly's UTF-8 byte offsets ('start' and 'end') are never
    incorrectly treated as Python character offsets when multibyte characters exist.
    """
    # Emojis (4 bytes each) and em-dashes (3 bytes each)
    text = "🚀 Market—Crash: 100% loss."
    text_bytes = text.encode("utf-8")

    # In bytes:
    # 🚀 is 4 bytes (0, 1, 2, 3)
    # space is 1 byte (4)
    # 'Market' is bytes 5 to 11
    market_byte_start = text_bytes.find(b"Market")
    market_byte_end = market_byte_start + len(b"Market")
    assert market_byte_start == 5
    assert market_byte_end == 11

    # In Python character index:
    # '🚀' is index 0 (length 1)
    # ' ' is index 1
    # 'Market' starts at char index 2, ends at char index 8!
    assert text[2:8] == "Market"

    # If incorrectly sliced with byte offsets:
    bad_slice = text[market_byte_start:market_byte_end]
    assert bad_slice != "Market"
    assert bad_slice == "ket\u2014Cr"  # Corrupted substring when bytes treated as chars!

    # Using polly_byte_to_char_offset:
    char_start = polly_byte_to_char_offset(text, market_byte_start)
    char_end = polly_byte_to_char_offset(text, market_byte_end)
    assert char_start == 2
    assert char_end == 8
    assert text[char_start:char_end] == "Market"

    # Test with em-dash:
    # 'Crash' comes after '—' (\xe2\x80\x94, 3 bytes)
    crash_byte_start = text_bytes.find(b"Crash")
    crash_char_start = polly_byte_to_char_offset(text, crash_byte_start)
    assert text[crash_char_start:crash_char_start + 5] == "Crash"


# =========================================================================
# Test K: Backward compatibility
# =========================================================================
def test_k_voice_track_model_backward_compatibility():
    """Verifies that existing VoiceTrack schema accepts both single and multi-chunk structures."""
    vt = VoiceTrack(
        voice_id="Matthew",
        audio_file_name="narration.mp3",
        storage_key="runs/run_1/narration.mp3",
        duration_seconds=5.0,
        full_script_text="Legacy script.",
        word_timestamps=[WordTimestamp(word="Legacy", start_ms=0, end_ms=500)],
        chunks=[],
    )
    result = VoiceTrackValidator().validate(vt)
    assert result.status == "valid"
