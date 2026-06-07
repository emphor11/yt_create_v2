from typing import Literal

from pydantic import BaseModel, Field


ArtifactStatus = Literal["valid", "warning", "blocked", "failed"]


class ValidationResult(BaseModel):
    status: ArtifactStatus
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

