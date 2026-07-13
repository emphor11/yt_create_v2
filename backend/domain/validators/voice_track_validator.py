from domain.voice_track import VoiceTrack
from domain.validation import ValidationResult


class VoiceTrackValidator:
    def validate(self, voice_track: VoiceTrack) -> ValidationResult:
        errors: list[str] = []

        if not voice_track.voice_id.strip():
            errors.append("Voice track must specify a voice_id.")
        if not voice_track.audio_file_name.strip():
            errors.append("Voice track must specify an audio_file_name.")
        if not voice_track.storage_key.strip():
            errors.append("Voice track must specify a storage_key.")
        if voice_track.duration_seconds <= 0.0:
            errors.append("Voice track must have a positive, non-zero duration_seconds.")
        if not voice_track.full_script_text.strip():
            errors.append("Voice track must have full_script_text.")
        if not voice_track.word_timestamps:
            errors.append("Voice track must have at least one word timestamp.")

        # Validate timestamp bounds
        for idx, ts in enumerate(voice_track.word_timestamps):
            if not ts.word.strip():
                errors.append(f"Word timestamp at index {idx} has an empty word string.")
            if ts.start_ms < 0 or ts.end_ms < 0:
                errors.append(f"Word '{ts.word}' at index {idx} has negative timestamp boundaries.")
            if ts.start_ms > ts.end_ms:
                errors.append(f"Word '{ts.word}' at index {idx} has start_ms greater than end_ms.")

        if errors:
            return ValidationResult(status="failed", errors=errors)
        return ValidationResult(status="valid")
