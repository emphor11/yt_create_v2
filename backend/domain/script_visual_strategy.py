from pydantic import BaseModel, Field, model_validator


class VoiceCue(BaseModel):
    """Represents a semantic vocal performance direction anchored to a word or phrase.
    
    The LLM outputs pure semantic intent; downstream SSMLCompiler turns this into valid Polly SSML.
    """
    cue_id: str | None = None
    anchor: str
    pause_before_ms: int | None = None
    pause_after_ms: int | None = None
    rate_percent: int | None = None   # Speed percentage, e.g. 94 to 98 (None = 100% normal)
    rate: int | None = None           # Backward-compatible alias for rate_percent
    volume_db: int | None = None      # Volume lift, e.g. 1, 2, 3 dB
    pronunciation: str | None = None  # Spoken pronunciation override (e.g. for "₹50,000" -> "fifty thousand rupees")

    @model_validator(mode="after")
    def sync_rate_fields(self) -> "VoiceCue":
        # Keep rate and rate_percent in sync for 100% backward/forward compatibility
        if self.rate_percent is not None and self.rate is None:
            self.rate = self.rate_percent
        elif self.rate is not None and self.rate_percent is None:
            self.rate_percent = self.rate
        return self


class VideoIdea(BaseModel):
    """Represents the spoken narration and pedagogical intent for a single scene beat.
    
    Preserves narrative lineage from Stage 2 (Narrative Plan SceneBeat) into Stage 4 (Body Script),
    allowing downstream visual intent and composition planning to understand the scene's exact role.
    """
    idea_id: str
    title: str
    scene_role: str | None = None
    viewer_question: str | None = None
    focus_concept: str
    core_teaching_point: str
    key_evidence: list[str] = Field(default_factory=list)
    narration: str
    voice_cues: list[VoiceCue] = Field(default_factory=list)


class ScriptVisualStrategy(BaseModel):
    """Domain model representing the complete spoken body script of the video."""
    schema_version: str = "1"
    thesis: str
    ideas: list[VideoIdea] = Field(default_factory=list)
