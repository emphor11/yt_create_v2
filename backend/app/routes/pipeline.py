from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.dependencies import get_pipeline_service
from app.pipeline_service import PipelineService, PipelineServiceError
from artifact_store.models import ArtifactRecord
from artifact_store.sqlite_store import RecordNotFoundError
from domain.validation import ValidationResult


router = APIRouter()


class RunStageResponse(BaseModel):
    artifact_id: str
    artifact: ArtifactRecord
    validation: ValidationResult


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
    if stage != "script_brief":
        raise HTTPException(status_code=404, detail=f"Stage {stage} is not implemented.")

    try:
        artifact = pipeline_service.run_script_brief(project_id, run_id)
    except RecordNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except PipelineServiceError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error

    return RunStageResponse(
        artifact_id=artifact.id,
        artifact=artifact,
        validation=artifact.validation_json,
    )

