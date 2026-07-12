from typing import Any, Literal

from pydantic import BaseModel, Field

from domain.validation import ArtifactStatus, ValidationResult


RunMode = Literal["deterministic", "ai"]
VALID_RUN_MODES: set[RunMode] = {"deterministic", "ai"}

RunState = Literal["pending", "running", "failed", "completed"]
VALID_RUN_STATES: set[RunState] = {"pending", "running", "failed", "completed"}

ADVANCEABLE_STATUSES: set[ArtifactStatus] = {"valid", "warning"}


def is_advanceable_status(status: ArtifactStatus) -> bool:
    return status in ADVANCEABLE_STATUSES


class ProjectRecord(BaseModel):
    id: str
    title: str
    created_at: str


class PipelineRunRecord(BaseModel):
    id: str
    project_id: str
    created_at: str
    mode: RunMode
    state: RunState = "pending"
    current_stage: str | None = None
    started_at: str | None = None
    completed_at: str | None = None
    error_message: str | None = None


class ArtifactRecord(BaseModel):
    id: str
    project_id: str
    run_id: str
    artifact_type: str
    schema_version: str
    payload_json: dict[str, Any] = Field(default_factory=dict)
    parent_artifact_roles_json: dict[str, str] = Field(default_factory=dict)
    validation_json: ValidationResult
    status: ArtifactStatus
    created_at: str


class ArtifactLineage(BaseModel):
    artifact_id: str
    parents: dict[str, ArtifactRecord]
    children: list[ArtifactRecord]


class ArtifactTraceNode(BaseModel):
    artifact_id: str
    artifact_type: str
    status: ArtifactStatus
    role_path: str
    depth: int


class ArtifactTrace(BaseModel):
    artifact_id: str
    ancestors: list[ArtifactTraceNode]
    descendants: list[ArtifactTraceNode]
