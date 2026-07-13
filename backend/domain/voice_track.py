from pydantic import BaseModel, Field


class WordTimestamp(BaseModel):
    word: str
    start_ms: int
    end_ms: int


class VoiceTrack(BaseModel):
    schema_version: str = "1"
    voice_id: str
    audio_file_name: str
    storage_key: str
    duration_seconds: float
    full_script_text: str
    word_timestamps: list[WordTimestamp] = Field(default_factory=list)
