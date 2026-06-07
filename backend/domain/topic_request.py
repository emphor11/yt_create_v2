from pydantic import BaseModel, Field


class TopicRequest(BaseModel):
    schema_version: str = "1"
    topic: str = Field(default="")
    angle: str = Field(default="")

