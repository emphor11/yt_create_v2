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
