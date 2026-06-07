from pydantic import BaseModel, Field


class SceneArcStep(BaseModel):
    scene_id: str
    scene_function_label: str
    arc_phases: list[str] = Field(default_factory=list)
    narrative_purpose: str
    is_payoff_scene: bool = False


class NarrativeArc(BaseModel):
    schema_version: str = "1"
    topic: str
    thesis: str
    viewer_question: str
    arc: list[str] = Field(default_factory=list)
    scene_arc_steps: list[SceneArcStep] = Field(default_factory=list)

