from pydantic import BaseModel, Field


class VideoIdea(BaseModel):
    idea_id: str
    title: str
    focus_concept: str
    core_teaching_point: str
    narration: str


class ScriptVisualStrategy(BaseModel):
    schema_version: str = "1"
    thesis: str
    ideas: list[VideoIdea] = Field(default_factory=list)
