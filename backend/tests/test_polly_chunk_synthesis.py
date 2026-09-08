import json
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

from domain.tts_chunk import TTSChunk
from providers.voice_provider import PollyVoiceProvider, PollyChunkSynthesisError


def _make_mock_stream(content: bytes):
    mock = MagicMock()
    mock.read.return_value = content
    return mock


import base64

VALID_24KHZ_MP3_BYTES = base64.b64decode(
    'SUQzBAAAAAAAI1RTU0UAAAAPAAADTGF2ZjYyLjEyLjEwMAAAAAAAAAAAAAAA//OEwAAAAAAAAAAAAEluZm8AAAAPAAAACwAABOAAOzs7Ozs7Ozs7Tk5OTk5OTk5OYmJiYmJiYmJidnZ2dnZ2dnZ2iYmJiYmJiYmJnZ2dnZ2dnZ2dsbGxsbGxsbGxxMTExMTExMTE2NjY2NjY2NjY7Ozs7Ozs7Ozs////////////AAAAAExhdmM2Mi4yOAAAAAAAAAAAAAAAACQDwAAAAAAAAATgJ4dPNwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA//NExAAAAANIAAAAAExBTUUzLjEwMFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVTEFNRTMu//NExFMAAANIAAAAADEwMFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVTEFNRTMu//NExKYAAANIAAAAADEwMFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVTEFNRTMu//NExKwAAANIAAAAADEwMFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVTEFNRTMu//NExKwAAANIAAAAADEwMFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVTEFNRTMu//NExKwAAANIAAAAADEwMFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVTEFNRTMu//NExKwAAANIAAAAADEwMFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVTEFNRTMu//NExKwAAANIAAAAADEwMFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVTEFNRTMu//NExKwAAANIAAAAADEwMFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV//NExKwAAANIAAAAAFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV//NExKwAAANIAAAAAFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV'
)


def _mock_polly_client(recorded_calls: list[dict] | None = None):
    """Creates a mock boto3 Polly client returning valid audio bytes and json speech marks."""
    client = MagicMock()

    def mock_synthesize_speech(*args, **kwargs):
        if recorded_calls is not None:
            recorded_calls.append(kwargs)
        fmt = kwargs.get("OutputFormat")
        text = kwargs.get("Text", "")
        if fmt == "mp3":
            return {"AudioStream": _make_mock_stream(VALID_24KHZ_MP3_BYTES)}
        elif fmt == "json":
            words = text.split()
            lines = []
            cur_ms = 100
            cur_char = 0
            for w in words:
                w_clean = w.strip()
                lines.append(
                    json.dumps({
                        "time": cur_ms,
                        "type": "word",
                        "start": cur_char,
                        "end": cur_char + len(w_clean),
                        "value": w_clean,
                    })
                )
                cur_ms += 150
                cur_char += len(w) + 1
            return {"AudioStream": _make_mock_stream("\n".join(lines).encode("utf-8"))}
        return {}

    client.synthesize_speech.side_effect = mock_synthesize_speech
    return client


def test_single_chunk_synthesis(tmp_path: Path):
    recorded_calls = []
    mock_client = _mock_polly_client(recorded_calls)
    provider = PollyVoiceProvider(voice_id="Matthew", engine="neural")

    chunk = TTSChunk(
        chunk_id="chunk_001",
        source_id="hook",
        sequence=1,
        text="The market rose 3.2% in January.",
        char_count=len("The market rose 3.2% in January."),
    )

    result = provider.synthesize_chunk(chunk, tmp_path, client=mock_client)

    # 1. Structure assertions
    assert result.chunk_id == "chunk_001"
    assert result.sequence == 1
    assert result.source_id == "hook"
    assert result.text == "The market rose 3.2% in January."
    assert result.duration_ms > 0
    assert result.duration_seconds > 0.0

    # 2. Files generated on disk
    assert Path(result.audio_path).exists()
    assert Path(result.audio_path).name == "chunk_001.mp3"
    assert Path(result.speech_marks_path).exists()
    assert Path(result.speech_marks_path).name == "chunk_001.marks.json"

    # 3. Timestamps extracted
    assert len(result.word_timestamps) > 0
    words = [ts["word"] for ts in result.word_timestamps]
    assert "The" in words
    assert "market" in words

    # 4. Exact text passed to Polly without mutation
    assert len(recorded_calls) == 2
    for call in recorded_calls:
        assert call["Text"] == "The market rose 3.2% in January."
        assert call["VoiceId"] == "Matthew"
        assert call["Engine"] == "neural"


def test_multi_chunk_synthesis_ordering_and_association(tmp_path: Path):
    recorded_calls = []
    mock_client = _mock_polly_client(recorded_calls)
    provider = PollyVoiceProvider(voice_id="Matthew", engine="neural")

    chunks = [
        TTSChunk(chunk_id="chunk_001", source_id="hook", sequence=1, text="First opening sentence.", char_count=23),
        TTSChunk(chunk_id="chunk_002", source_id="idea_01", sequence=2, text="Second teaching point.", char_count=22),
        TTSChunk(chunk_id="chunk_003", source_id="idea_02", sequence=3, text="Third concluding thought.", char_count=25),
    ]

    results = provider.synthesize_chunks(chunks, tmp_path, client=mock_client)

    # 1. Chunk ordering preserved
    assert len(results) == 3
    assert [r.sequence for r in results] == [1, 2, 3]
    assert [r.chunk_id for r in results] == ["chunk_001", "chunk_002", "chunk_003"]
    assert [r.source_id for r in results] == ["hook", "idea_01", "idea_02"]

    # 2. Each result is correctly associated with its individual files
    for r in results:
        assert Path(r.audio_path).exists()
        assert Path(r.audio_path).name == f"{r.chunk_id}.mp3"
        assert Path(r.speech_marks_path).exists()
        assert Path(r.speech_marks_path).name == f"{r.chunk_id}.marks.json"
        assert len(r.word_timestamps) > 0

    # 3. Calls were made chronologically with exact text
    texts_sent_to_polly = [call["Text"] for call in recorded_calls if call.get("OutputFormat") == "mp3"]
    assert texts_sent_to_polly == [
        "First opening sentence.",
        "Second teaching point.",
        "Third concluding thought.",
    ]


def test_polly_audio_failure_identifies_failing_chunk(tmp_path: Path):
    provider = PollyVoiceProvider()
    base_client = _mock_polly_client()

    # Fail on chunk 2 when OutputFormat is mp3
    def mock_synthesize(**kwargs):
        if kwargs.get("Text") == "Second teaching point." and kwargs.get("OutputFormat") == "mp3":
            raise RuntimeError("Polly internal 500 server error")
        return base_client.synthesize_speech.side_effect(**kwargs)

    mock_client = MagicMock()
    mock_client.synthesize_speech.side_effect = mock_synthesize

    chunks = [
        TTSChunk(chunk_id="chunk_001", source_id="hook", sequence=1, text="First opening sentence.", char_count=23),
        TTSChunk(chunk_id="chunk_002", source_id="idea_01", sequence=2, text="Second teaching point.", char_count=22),
        TTSChunk(chunk_id="chunk_003", source_id="idea_02", sequence=3, text="Third concluding thought.", char_count=25),
    ]

    with pytest.raises(PollyChunkSynthesisError) as exc_info:
        provider.synthesize_chunks(chunks, tmp_path, client=mock_client)

    err = exc_info.value
    assert err.chunk_id == "chunk_002"
    assert err.stage == "audio"
    assert "Polly internal 500 server error" in str(err)


def test_polly_speech_mark_failure_identifies_failing_chunk(tmp_path: Path):
    provider = PollyVoiceProvider()
    base_client = _mock_polly_client()

    # Fail on chunk 3 when OutputFormat is json
    def mock_synthesize(**kwargs):
        if kwargs.get("Text") == "Third concluding thought." and kwargs.get("OutputFormat") == "json":
            raise RuntimeError("Speech marks stream corrupted")
        return base_client.synthesize_speech.side_effect(**kwargs)

    mock_client = MagicMock()
    mock_client.synthesize_speech.side_effect = mock_synthesize

    chunks = [
        TTSChunk(chunk_id="chunk_001", source_id="hook", sequence=1, text="First opening sentence.", char_count=23),
        TTSChunk(chunk_id="chunk_002", source_id="idea_01", sequence=2, text="Second teaching point.", char_count=22),
        TTSChunk(chunk_id="chunk_003", source_id="idea_02", sequence=3, text="Third concluding thought.", char_count=25),
    ]

    with pytest.raises(PollyChunkSynthesisError) as exc_info:
        provider.synthesize_chunks(chunks, tmp_path, client=mock_client)

    err = exc_info.value
    assert err.chunk_id == "chunk_003"
    assert err.stage == "speech_marks"
    assert "Speech marks stream corrupted" in str(err)


def test_exact_text_passed_to_polly_no_mutation(tmp_path: Path):
    recorded_calls = []
    mock_client = _mock_polly_client(recorded_calls)
    provider = PollyVoiceProvider()

    special_text = "The U.S. Fed held benchmark rates at 5.25%, Dr. Powell announced yesterday."
    chunk = TTSChunk(
        chunk_id="chunk_001",
        source_id="news",
        sequence=1,
        text=special_text,
        char_count=len(special_text),
    )

    result = provider.synthesize_chunk(chunk, tmp_path, client=mock_client)

    assert result.text == special_text
    for call in recorded_calls:
        # Guarantee no case changing, abbreviation expanding, or punctuation stripping
        assert call["Text"] == special_text


def test_backward_compatible_synthesize_produces_valid_output(tmp_path: Path):
    mock_client = _mock_polly_client()
    provider = PollyVoiceProvider()

    output_path = tmp_path / "legacy_narration.mp3"
    with patch("boto3.client", return_value=mock_client):
        dur_sec, timestamps = provider.synthesize("Single sentence for legacy test.", output_path)

    assert dur_sec > 0
    assert len(timestamps) > 0
    assert output_path.exists()
    assert output_path.stat().st_size > 0


def test_voice_generation_handler_preserves_single_chunk_behavior(tmp_path: Path):
    """
    Verifies Requirement 8:
    Preserve existing behavior for scripts that fit into a single chunk.
    A short current video produces a valid single-chunk VoiceTrack path.
    """
    from artifact_store.sqlite_store import ArtifactStore
    from app.stage_handlers.voice_generation_handler import VoiceGenerationHandler
    from app.stage_logger import StageLogger
    from domain.validation import ValidationResult
    from domain.validators.voice_track_validator import VoiceTrackValidator
    from providers.media_storage import LocalMediaStorage

    store = ArtifactStore(tmp_path / "voice_single.db")
    store.initialize()
    media = LocalMediaStorage(tmp_path / "media")
    logger = StageLogger()

    project = store.create_project("Single Chunk Project")
    run = store.create_run(project.id, mode="ai")

    # Prerequisite artifacts
    h_art = store.save_artifact(
        project_id=project.id,
        run_id=run.id,
        artifact_type="hook",
        schema_version="1",
        payload_json={"conceptual_hook": "Hook", "script_text": "Short hook text."},
        parent_artifact_roles_json={},
        validation_json=ValidationResult(status="valid"),
    )
    s_art = store.save_artifact(
        project_id=project.id,
        run_id=run.id,
        artifact_type="script_visual_strategy",
        schema_version="1",
        payload_json={"thesis": "Thesis", "ideas": []},
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

    mock_client = _mock_polly_client()
    provider = PollyVoiceProvider()

    handler = VoiceGenerationHandler(
        store=store,
        media_storage=media,
        voice_provider=provider,
        voice_validator=VoiceTrackValidator(),
        stage_logger=logger,
    )

    with patch("boto3.client", return_value=mock_client):
        artifact = handler.run(project.id, run.id)

    assert artifact.artifact_type == "voice_track"
    assert artifact.status == "valid"
    payload = artifact.payload_json
    assert payload["audio_file_name"] == "narration.mp3"
    assert payload["duration_seconds"] > 0
    assert len(payload["word_timestamps"]) > 0

    # Verify per-chunk result was captured in artifact
    assert len(payload["chunks"]) == 1
    assert payload["chunks"][0]["chunk_id"] == "chunk_001"
    assert payload["chunks"][0]["source_id"] == "hook"

    # Verify master narration.mp3 file exists on disk
    master_path = media.path_for_key(payload["storage_key"])
    assert master_path.exists()
    assert master_path.stat().st_size > 0


def test_voice_generation_handler_multi_chunk_persists_all_chunks(tmp_path: Path):
    """
    Verifies Requirement 2, 6, 7:
    Multi-chunk narration is passed through TTSChunker, each chunk is synthesized,
    and structured per-chunk results are persisted in the VoiceTrack artifact.
    """
    from artifact_store.sqlite_store import ArtifactStore
    from app.stage_handlers.voice_generation_handler import VoiceGenerationHandler
    from app.stage_logger import StageLogger
    from domain.validation import ValidationResult
    from domain.validators.voice_track_validator import VoiceTrackValidator
    from engines.tts_chunker import TTSChunker
    from providers.media_storage import LocalMediaStorage

    store = ArtifactStore(tmp_path / "voice_multi.db")
    store.initialize()
    media = LocalMediaStorage(tmp_path / "media")
    logger = StageLogger()

    project = store.create_project("Multi Chunk Project")
    run = store.create_run(project.id, mode="ai")

    # Prerequisite artifacts with multiple distinct ideas
    h_art = store.save_artifact(
        project_id=project.id,
        run_id=run.id,
        artifact_type="hook",
        schema_version="1",
        payload_json={"conceptual_hook": "Hook", "script_text": "First chapter opening."},
        parent_artifact_roles_json={},
        validation_json=ValidationResult(status="valid"),
    )
    s_art = store.save_artifact(
        project_id=project.id,
        run_id=run.id,
        artifact_type="script_visual_strategy",
        schema_version="1",
        payload_json={
            "thesis": "Thesis",
            "ideas": [
                {"idea_id": "idea_01", "title": "T1", "focus_concept": "C1", "core_teaching_point": "P1", "narration": "Second chapter details.", "visual_sequence": []},
                {"idea_id": "idea_02", "title": "T2", "focus_concept": "C2", "core_teaching_point": "P2", "narration": "Third chapter conclusions.", "visual_sequence": []},
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

    # Use a chunker with safe_max_chars=30 to force 3 chunks
    chunker = TTSChunker(safe_max_chars=30)
    mock_client = _mock_polly_client()
    provider = PollyVoiceProvider()

    handler = VoiceGenerationHandler(
        store=store,
        media_storage=media,
        voice_provider=provider,
        voice_validator=VoiceTrackValidator(),
        stage_logger=logger,
        chunker=chunker,
    )

    with patch("boto3.client", return_value=mock_client):
        artifact = handler.run(project.id, run.id)

    assert artifact.artifact_type == "voice_track"
    assert artifact.status == "valid"
    payload = artifact.payload_json

    # Verify structured per-chunk results are persisted
    assert len(payload["chunks"]) == 3
    chunk_ids = [c["chunk_id"] for c in payload["chunks"]]
    assert chunk_ids == ["chunk_001", "chunk_002", "chunk_003"]
    assert [c["sequence"] for c in payload["chunks"]] == [1, 2, 3]

    # Verify each chunk has audio_path and speech_marks_path on disk
    for chunk_meta in payload["chunks"]:
        assert Path(chunk_meta["audio_path"]).exists()
        assert Path(chunk_meta["speech_marks_path"]).exists()
        assert chunk_meta["duration_ms"] > 0
        assert len(chunk_meta["word_timestamps"]) > 0

