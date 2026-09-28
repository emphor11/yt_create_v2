from pydantic import BaseModel, Field


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


class ScriptVisualStrategy(BaseModel):
    """Domain model representing the complete spoken body script of the video."""
    schema_version: str = "1"
    thesis: str
    ideas: list[VideoIdea] = Field(default_factory=list)
