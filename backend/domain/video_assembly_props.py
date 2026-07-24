from typing import Any, Literal
from pydantic import BaseModel, ConfigDict

class TimedBeatSegment(BaseModel):
    model_config = ConfigDict(extra="forbid")
    beat_id: str
    start_frame: int
    end_frame: int
    duration_frames: int
    preferred_component: str | None = None
    visual_goal: str
    asset_query: str | None = None
    notes: str | None = None
    component_data: dict[str, Any] = {}
    narration_text: str

class AssetReference(BaseModel):
    model_config = ConfigDict(extra="forbid")
    asset_id: str
    asset_type: Literal["image", "video"]
    source: Literal["pexels", "pixabay", "fallback"]
    query: str
    local_path: str
    url: str | None = None
    asset_status: Literal["found", "cached", "fallback", "failed"]

class ComponentSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")
    component_id: str  # "SplitComparison", "Typography", etc.
    props: dict[str, Any]  # Strict rendering-specific parameters only

class SceneSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")
    scene_id: str
    start_frame: int
    end_frame: int
    duration_frames: int
    component: ComponentSpec
    asset: AssetReference | None = None
    narration_text: str | None = None

class AudioSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")
    audio_file_name: str
    local_path: str
    duration_seconds: float

class VideoAssemblyProps(BaseModel):
    model_config = ConfigDict(extra="forbid")
    scenes: list[SceneSpec]
    audio: AudioSpec
