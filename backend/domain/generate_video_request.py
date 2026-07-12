from pydantic import BaseModel, Field


class GenerateVideoRequest(BaseModel):
    schema_version: str = "1"
    topic: str = Field(default="")
    audience: str = Field(default="")
    language: str = Field(default="")
    style: str = Field(default="")
    channel: str = Field(default="")
