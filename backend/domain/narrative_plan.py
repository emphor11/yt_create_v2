from pydantic import BaseModel, Field


class SceneBeat(BaseModel):
    scene_id: str
    title: str
    focus_concept: str
    core_teaching_point: str
    scene_role: str = ""
    viewer_question: str = ""
    key_evidence: list[str] = Field(default_factory=list)


class NarrativePlan(BaseModel):
    schema_version: str = "1"
    thesis: str
    target_pain_point: str
    conceptual_hook: str
    narrative_arc_type: str
    central_tension: str = ""
    starting_belief: str = ""
    ending_understanding: str = ""
    scene_beats: list[SceneBeat] = Field(default_factory=list)
