from domain.voice_track import VoiceTrack, WordTimestamp
from domain.validators.voice_track_validator import VoiceTrackValidator


def test_validator_accepts_valid_voice_track() -> None:
    track = VoiceTrack(
        voice_id="Matthew",
        audio_file_name="narration.mp3",
        storage_key="path/narration.mp3",
        duration_seconds=1.2,
        full_script_text="Is salary a drug?",
        word_timestamps=[
            WordTimestamp(word="Is", start_ms=0, end_ms=200),
            WordTimestamp(word="salary", start_ms=240, end_ms=500),
            WordTimestamp(word="a", start_ms=540, end_ms=600),
            WordTimestamp(word="drug?", start_ms=640, end_ms=1000),
        ],
    )
    val_res = VoiceTrackValidator().validate(track)
    assert val_res.status == "valid"
    assert not val_res.errors


def test_validator_fails_on_empty_fields() -> None:
    track = VoiceTrack(
        voice_id="",
        audio_file_name="",
        storage_key="",
        duration_seconds=-0.5,
        full_script_text="",
        word_timestamps=[],
    )
    val_res = VoiceTrackValidator().validate(track)
    assert val_res.status == "failed"
    assert len(val_res.errors) >= 6


def test_validator_fails_on_invalid_timestamps() -> None:
    track = VoiceTrack(
        voice_id="Matthew",
        audio_file_name="narration.mp3",
        storage_key="path/narration.mp3",
        duration_seconds=1.2,
        full_script_text="Test",
        word_timestamps=[
            WordTimestamp(word="Bad", start_ms=500, end_ms=200),  # start > end
        ],
    )
    val_res = VoiceTrackValidator().validate(track)
    assert val_res.status == "failed"
    assert "has start_ms greater than end_ms" in val_res.errors[0]
