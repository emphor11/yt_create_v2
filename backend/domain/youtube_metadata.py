from pydantic import BaseModel, ConfigDict, Field


class YoutubeMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: str = "1"
    title: str
    description: str
    tags: list[str] = Field(default_factory=list)
    category_id: str = "27"
    thumbnail_concept: str
