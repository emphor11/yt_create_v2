from pydantic import BaseModel, Field


class SceneBeat(BaseModel):
    scene_id: str
    title: str
    focus_concept: str
    core_teaching_point: str


class NarrativePlan(BaseModel):
    schema_version: str = "1"
    thesis: str
    target_pain_point: str
    conceptual_hook: str
    narrative_arc_type: str
    scene_beats: list[SceneBeat] = Field(default_factory=list)
