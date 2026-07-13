from typing import Any
from pydantic import BaseModel, Field


class VisualStrategyBeat(BaseModel):
    beat_id: str
    preferred_component: str
    visual_goal: str
    asset_query: str | None = None
    notes: str | None = None
    component_data: dict[str, Any] = Field(default_factory=dict)


class VideoIdea(BaseModel):
    idea_id: str
    title: str
    focus_concept: str
    core_teaching_point: str
    narration: str
    visual_sequence: list[VisualStrategyBeat] = Field(default_factory=list)


class ScriptVisualStrategy(BaseModel):
    schema_version: str = "1"
    thesis: str
    ideas: list[VideoIdea] = Field(default_factory=list)
