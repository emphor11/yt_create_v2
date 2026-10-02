import json
from pathlib import Path
from unittest.mock import MagicMock
import pytest

from domain.tts_chunk import TTSChunk
from domain.script_visual_strategy import VoiceCue
from providers.voice_provider import PollyVoiceProvider, PollyChunkSynthesisError
from tests.test_polly_chunk_synthesis import VALID_24KHZ_MP3_BYTES, _make_mock_stream


def _mock_ssml_polly_client(recorded_calls: list[dict] | None = None, raise_on_ssml: bool = False):
    client = MagicMock()

    def mock_synthesize_speech(*args, **kwargs):
        if recorded_calls is not None:
            recorded_calls.append(kwargs)

        text_type = kwargs.get("TextType")
        if raise_on_ssml and text_type == "ssml":
            raise Exception("InvalidSsmlException: The input text is not valid SSML.")

        fmt = kwargs.get("OutputFormat")
        if fmt == "mp3":
            return {"AudioStream": _make_mock_stream(VALID_24KHZ_MP3_BYTES)}
        elif fmt == "json":
            lines = [
                json.dumps({"time": 0, "type": "ssml", "value": "hook_start", "start": 8, "end": 35}),
                json.dumps({"time": 100, "type": "word", "value": "On", "start": 36, "end": 38}),
                json.dumps({"time": 250, "type": "word", "value": "paper", "start": 39, "end": 44}),
                json.dumps({"time": 750, "type": "word", "value": "relief", "start": 45, "end": 51}),
            ]
            return {"AudioStream": _make_mock_stream("\n".join(lines).encode("utf-8"))}
        return {}

    client.synthesize_speech.side_effect = mock_synthesize_speech
    return client


def test_polly_synthesizes_with_ssml_when_cues_present(tmp_path: Path):
    recorded_calls = []
    mock_client = _mock_ssml_polly_client(recorded_calls)
    provider = PollyVoiceProvider(voice_id="Danielle", engine="neural")

    chunk = TTSChunk(
        chunk_id="chunk_001",
        source_id="hook",
        sequence=1,
        text="On paper, lower EMI looks like relief. Until you calculate the cost.",
        char_count=67,
        voice_cues=[
            VoiceCue(anchor="relief.", pause_after_ms=400).model_dump()
        ],
    )

    result = provider.synthesize_chunk(chunk, tmp_path, client=mock_client)

    # 1. Calls were made with TextType="ssml"
    assert len(recorded_calls) == 2
    audio_call = recorded_calls[0]
    marks_call = recorded_calls[1]

    assert audio_call["OutputFormat"] == "mp3"
    assert audio_call["TextType"] == "ssml"
    assert audio_call["VoiceId"] == "Danielle"
    assert audio_call["Engine"] == "neural"
    assert "<speak>" in audio_call["Text"]
    assert '<break time="400ms"/>' in audio_call["Text"]

    assert marks_call["OutputFormat"] == "json"
    assert marks_call["TextType"] == "ssml"
    assert marks_call["SpeechMarkTypes"] == ["word", "ssml"]
    assert marks_call["Text"] == audio_call["Text"]  # Exact same text used for both

    # 2. Both word timestamps and SSML marks are extracted
    assert len(result.word_timestamps) == 3
    assert result.word_timestamps[0]["word"] == "On"
    assert len(result.speech_marks) == 1
    assert result.speech_marks[0]["mark_type"] == "ssml"
    assert result.speech_marks[0]["value"] == "hook_start"


def test_polly_falls_back_to_plain_text_on_invalid_ssml_exception(tmp_path: Path):
    recorded_calls = []
    # Mock client that rejects SSML with InvalidSsmlException
    mock_client = _mock_ssml_polly_client(recorded_calls, raise_on_ssml=True)
    provider = PollyVoiceProvider(voice_id="Danielle", engine="neural")

    chunk = TTSChunk(
        chunk_id="chunk_001",
        source_id="idea_01",
        sequence=1,
        text="Plain text backup test.",
        char_count=23,
        voice_cues=[
            {"anchor": "test.", "pause_after_ms": 300}
        ],
    )

    result = provider.synthesize_chunk(chunk, tmp_path, client=mock_client)

    # Should have attempted SSML, failed, and retried with TextType="text"
    assert len(recorded_calls) >= 2
    retry_audio_call = recorded_calls[1]
    assert retry_audio_call["OutputFormat"] == "mp3"
    assert retry_audio_call["TextType"] == "text"
    assert retry_audio_call["Text"] == "Plain text backup test."
    assert Path(result.audio_path).exists()


def test_polly_fails_loudly_on_configuration_error(tmp_path: Path):
    client = MagicMock()
    # Configuration error: invalid voice ID
    client.synthesize_speech.side_effect = Exception("ValidationException: Voice 'NonExistentVoice' does not exist.")

    provider = PollyVoiceProvider(voice_id="NonExistentVoice")
    chunk = TTSChunk(
        chunk_id="chunk_001",
        source_id="idea_01",
        sequence=1,
        text="Hello world.",
        char_count=12,
    )

    with pytest.raises(PollyChunkSynthesisError) as exc_info:
        provider.synthesize_chunk(chunk, tmp_path, client=client)

    assert "NonExistentVoice" in str(exc_info.value)
    assert exc_info.value.stage == "audio"


def test_polly_preserves_plain_text_when_no_cues(tmp_path: Path):
    recorded_calls = []
    mock_client = _mock_ssml_polly_client(recorded_calls)
    provider = PollyVoiceProvider(voice_id="Danielle", engine="neural")

    chunk = TTSChunk(
        chunk_id="chunk_001",
        source_id="idea_01",
        sequence=1,
        text="Simple plain sentence without cues.",
        char_count=36,
        voice_cues=[],
    )

    result = provider.synthesize_chunk(chunk, tmp_path, client=mock_client)

    assert len(recorded_calls) == 2
    assert recorded_calls[0]["TextType"] == "text"
    assert recorded_calls[0]["Text"] == "Simple plain sentence without cues."
    assert recorded_calls[1]["TextType"] == "text"
    assert recorded_calls[1]["SpeechMarkTypes"] == ["word"]


def test_polly_uses_ssml_when_global_rate_configured(tmp_path: Path):
    recorded_calls = []
    mock_client = _mock_ssml_polly_client(recorded_calls)
    provider = PollyVoiceProvider(voice_id="Kajal", engine="neural", global_rate=96)

    chunk = TTSChunk(
        chunk_id="chunk_001",
        source_id="idea_01",
        sequence=1,
        text="Simple plain sentence synthesized at global 96% rate.",
        char_count=52,
        voice_cues=[],
    )

    result = provider.synthesize_chunk(chunk, tmp_path, client=mock_client)

    assert len(recorded_calls) == 2
    assert recorded_calls[0]["TextType"] == "ssml"
    assert '<prosody rate="96%">' in recorded_calls[0]["Text"]
    assert recorded_calls[1]["TextType"] == "ssml"
    assert recorded_calls[1]["SpeechMarkTypes"] == ["word", "ssml"]
