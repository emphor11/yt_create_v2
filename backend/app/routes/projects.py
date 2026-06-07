from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.dependencies import get_artifact_store
from artifact_store.models import PipelineRunRecord, ProjectRecord
from artifact_store.sqlite_store import ArtifactStore, RecordNotFoundError


router = APIRouter()


class CreateProjectRequest(BaseModel):
    title: str = Field(min_length=1)


class CreateProjectResponse(BaseModel):
    project: ProjectRecord
    run: PipelineRunRecord


@router.post("/projects", response_model=CreateProjectResponse)
def create_project(
    request: CreateProjectRequest,
    store: ArtifactStore = Depends(get_artifact_store),
) -> CreateProjectResponse:
    try:
        project = store.create_project(request.title)
        run = store.create_run(project.id, mode="deterministic")
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    return CreateProjectResponse(project=project, run=run)


@router.get("/projects", response_model=list[ProjectRecord])
def list_projects(store: ArtifactStore = Depends(get_artifact_store)) -> list[ProjectRecord]:
    return store.list_projects()


@router.get("/projects/{project_id}", response_model=ProjectRecord)
def get_project(
    project_id: str,
    store: ArtifactStore = Depends(get_artifact_store),
) -> ProjectRecord:
    try:
        return store.get_project(project_id)
    except RecordNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.get("/projects/{project_id}/runs", response_model=list[PipelineRunRecord])
def list_runs(
    project_id: str,
    store: ArtifactStore = Depends(get_artifact_store),
) -> list[PipelineRunRecord]:
    try:
        return store.list_runs(project_id)
    except RecordNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.get("/projects/{project_id}/runs/{run_id}", response_model=PipelineRunRecord)
def get_run(
    project_id: str,
    run_id: str,
    store: ArtifactStore = Depends(get_artifact_store),
) -> PipelineRunRecord:
    try:
        return store.get_run(project_id, run_id)
    except RecordNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error

