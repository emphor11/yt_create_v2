from enum import Enum
from pydantic import BaseModel, Field


class DurationProfile(str, Enum):
    SHORT_2MIN = "short_2min"
    LONG_5MIN = "long_5min"


class VisualMode(str, Enum):
    LEGACY = "legacy"          # current component-selection pipeline (default)
    COMPOSITION = "composition"  # new intent-driven composition pipeline


class GenerateVideoRequest(BaseModel):
    schema_version: str = "1"
    topic: str = Field(default="")
    angle: str = Field(default="")
    audience: str = Field(default="")
    language: str = Field(default="")
    style: str = Field(default="")
    channel: str = Field(default="")
    duration_profile: DurationProfile = Field(default=DurationProfile.SHORT_2MIN)
    visual_mode: VisualMode = Field(
        default=VisualMode.LEGACY,
        description="Controls which visual pipeline runs. 'legacy' = existing component-selection. 'composition' = new intent-driven composition system.",
    )
