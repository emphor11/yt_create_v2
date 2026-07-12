from pydantic import BaseModel, Field


class ResearchPacket(BaseModel):
    schema_version: str = "1"
    topic: str
    audience: str
    channel: str
    verified_facts: list[str] = Field(default_factory=list)
    statistics: list[str] = Field(default_factory=list)
    concepts: list[str] = Field(default_factory=list)
    misconceptions: list[str] = Field(default_factory=list)
    examples: list[str] = Field(default_factory=list)
    trusted_sources: list[str] = Field(default_factory=list)
