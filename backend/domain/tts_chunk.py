from pydantic import BaseModel, Field


class TTSChunk(BaseModel):
    chunk_id: str = Field(description="Unique identifier for the chunk, e.g. chunk_001")
    source_id: str = Field(description="Originating scene or idea identifier, e.g. hook or idea_02")
    sequence: int = Field(description="1-indexed sequential position in the overall narration")
    text: str = Field(description="Exact, unmutated script text for this chunk")
    char_count: int = Field(description="Exact character length of the text")
