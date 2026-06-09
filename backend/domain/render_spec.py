from pydantic import BaseModel, ConfigDict

from domain.visual_plan import SplitComparisonProps


class RenderFrameSpan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_id: str
    start_frame: int
    end_frame: int
    duration_frames: int


class RenderSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: str = "1"
    scene_id: str
    composition: str
    fps: int
    duration_frames: int
    props: SplitComparisonProps
    frame_spans: list[RenderFrameSpan]
