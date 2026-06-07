from pydantic import BaseModel, Field


class SceneFunction(BaseModel):
    scene_id: str
    label: str
    mechanism: str
    purpose: str


class ScriptBrief(BaseModel):
    schema_version: str = "1"
    topic: str
    angle: str
    thesis: str
    primary_mechanisms: list[str] = Field(default_factory=list)
    recurring_example: str
    scene_functions: list[SceneFunction] = Field(default_factory=list)

