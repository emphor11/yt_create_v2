from pydantic import BaseModel, ConfigDict


class Thumbnail(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: str = "1"
    storage_key: str
    file_name: str = "thumbnail.png"
    content_type: str = "image/png"
    width: int = 1280
    height: int = 720
    size_bytes: int
    headline: str | None = None
    image_prompt: str | None = None
    visual_concept: str | None = None
    provider_used: str | None = None
