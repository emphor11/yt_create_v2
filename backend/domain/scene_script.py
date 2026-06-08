from pydantic import BaseModel, ConfigDict, Field


class SceneStoryState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    recurring_example: str


class SceneScript(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: str = "1"
    scene_id: str
    topic: str
    angle: str
    thesis: str
    mechanism: str
    scene_function_label: str
    arc_phases: list[str] = Field(default_factory=list)
    narrative_purpose: str
    narration: str
    story_state: SceneStoryState
