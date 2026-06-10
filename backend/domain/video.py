from typing import Literal

from pydantic import BaseModel, ConfigDict


RenderStatus = Literal["succeeded", "failed"]


class Video(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: str = "1"
    scene_id: str
    render_status: RenderStatus
    file_name: str
    content_type: str
    fps: int
    duration_frames: int
    storage_key: str | None = None
    size_bytes: int | None = None
    error_message: str | None = None
