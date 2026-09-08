from pydantic import BaseModel, Field


class TTSChunk(BaseModel):
    chunk_id: str = Field(description="Unique identifier for the chunk, e.g. chunk_001")
    source_id: str = Field(description="Originating scene or idea identifier, e.g. hook or idea_02")
    sequence: int = Field(description="1-indexed sequential position in the overall narration")
    text: str = Field(description="Exact, unmutated script text for this chunk")
    char_count: int = Field(description="Exact character length of the text")


class TTSChunkResult(BaseModel):
    chunk_id: str = Field(description="Chunk identifier matching input TTSChunk")
    sequence: int = Field(description="1-indexed sequence position")
    source_id: str = Field(description="Originating scene or idea identifier")
    text: str = Field(description="Verbatim script text synthesized for this chunk")
    audio_path: str = Field(description="Local filesystem path to the synthesized MP3 audio chunk")
    speech_marks_path: str | None = Field(default=None, description="Local filesystem path to the raw speech marks JSON file")
    word_timestamps: list[dict] = Field(default_factory=list, description="Extracted word timestamps for this chunk")
    duration_ms: int = Field(default=0, description="Actual audio duration of this chunk in milliseconds")
    duration_seconds: float = Field(default=0.0, description="Actual audio duration of this chunk in seconds")

