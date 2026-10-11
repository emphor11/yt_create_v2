from enum import Enum
from pydantic import BaseModel, Field


class DurationProfile(str, Enum):
    SHORT_2MIN = "short_2min"
    LONG_5MIN = "long_5min"


class VisualMode(str, Enum):
    WORLD = "world"              # Universal Visual World: 2-Pass Storyboarder + Compiler (Current/Recommended)
    COMPOSITION = "composition"  # Intent-driven Composition Pipeline
    LEGACY = "legacy"            # Legacy component-selection pipeline


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
        default=VisualMode.WORLD,
        description="Controls which visual pipeline runs. 'world' = Universal Visual World (Storyboarder + Compiler), 'composition' = composition system, 'legacy' = component-selection.",
    )
