from pydantic import BaseModel, ConfigDict

from domain.video_assembly_props import VideoAssemblyProps


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
    props: VideoAssemblyProps
    frame_spans: list[RenderFrameSpan]
