from pydantic import BaseModel, ConfigDict, Field


class DraftScene(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scene_id: str
    scene_function_label: str
    narration: str


class ScriptDraft(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: str = "1"
    topic: str
    angle: str
    thesis: str
    hook: str
    scenes: list[DraftScene] = Field(default_factory=list)
    outro: str
