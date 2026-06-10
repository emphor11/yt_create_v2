from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.dependencies import get_pipeline_service
from app.pipeline_service import PipelineService, PipelineServiceError
from artifact_store.models import ArtifactRecord
from artifact_store.sqlite_store import RecordNotFoundError
from domain.validation import ArtifactStatus, ValidationResult


router = APIRouter()


class RunStageResponse(BaseModel):
    artifact_id: str
    artifact: ArtifactRecord
    validation: ValidationResult


class PipelineStageSummary(BaseModel):
    stage: str
    artifact_type: str
    artifact_id: str | None
    status: ArtifactStatus | Literal["missing"]
    error_count: int
    warning_count: int
    errors: list[str]
    warnings: list[str]


class RunStatusResponse(BaseModel):
    project_id: str
    run_id: str
    stages: list[PipelineStageSummary]


class RegenerateDescendantsResponse(BaseModel):
    artifact_id: str
    deleted_artifacts: list[ArtifactRecord]
    next_stage: str | None


@router.post(
    "/projects/{project_id}/runs/{run_id}/run/{stage}",
    response_model=RunStageResponse,
)
def run_stage(
    project_id: str,
    run_id: str,
    stage: str,
    pipeline_service: PipelineService = Depends(get_pipeline_service),
) -> RunStageResponse:
    try:
        if stage == "script_brief":
            artifact = pipeline_service.run_script_brief(project_id, run_id)
        elif stage == "narrative_arc":
            artifact = pipeline_service.run_narrative_arc(project_id, run_id)
        elif stage == "script_draft":
            artifact = pipeline_service.run_script_draft(project_id, run_id)
        elif stage == "scene_script":
            artifact = pipeline_service.run_scene_script(project_id, run_id)
        elif stage == "semantic_scene":
            artifact = pipeline_service.run_semantic_scene(project_id, run_id)
        elif stage == "visual_event_sequence":
            artifact = pipeline_service.run_visual_event_sequence(project_id, run_id)
        elif stage == "visual_plan":
            artifact = pipeline_service.run_visual_plan(project_id, run_id)
        elif stage == "timing":
            artifact = pipeline_service.run_timing(project_id, run_id)
        elif stage == "render_spec":
            artifact = pipeline_service.run_render_spec(project_id, run_id)
        elif stage == "render":
            artifact = pipeline_service.run_render(project_id, run_id)
        else:
            raise HTTPException(status_code=404, detail=f"Stage {stage} is not implemented.")
    except RecordNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except PipelineServiceError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error

    return RunStageResponse(
        artifact_id=artifact.id,
        artifact=artifact,
        validation=artifact.validation_json,
    )


@router.get(
    "/projects/{project_id}/runs/{run_id}/status",
    response_model=RunStatusResponse,
)
def get_run_status(
    project_id: str,
    run_id: str,
    pipeline_service: PipelineService = Depends(get_pipeline_service),
) -> RunStatusResponse:
    try:
        summaries = pipeline_service.get_run_status(project_id, run_id)
    except RecordNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error

    return RunStatusResponse(
        project_id=project_id,
        run_id=run_id,
        stages=[PipelineStageSummary.model_validate(summary) for summary in summaries],
    )


@router.post(
    "/projects/{project_id}/runs/{run_id}/artifacts/{artifact_id}/regenerate-descendants",
    response_model=RegenerateDescendantsResponse,
)
def regenerate_descendants(
    project_id: str,
    run_id: str,
    artifact_id: str,
    pipeline_service: PipelineService = Depends(get_pipeline_service),
) -> RegenerateDescendantsResponse:
    try:
        deleted_artifacts, next_stage = pipeline_service.regenerate_descendants(
            project_id,
            run_id,
            artifact_id,
        )
    except RecordNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except PipelineServiceError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error

    return RegenerateDescendantsResponse(
        artifact_id=artifact_id,
        deleted_artifacts=deleted_artifacts,
        next_stage=next_stage,
    )
