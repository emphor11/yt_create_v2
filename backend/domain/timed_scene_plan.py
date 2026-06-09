from pydantic import BaseModel, ConfigDict


class TimedSpan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_id: str
    start_seconds: float
    end_seconds: float
    duration_seconds: float


class TimedScenePlan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: str = "1"
    scene_id: str
    duration_seconds: float
    fps: int
    spans: list[TimedSpan]
