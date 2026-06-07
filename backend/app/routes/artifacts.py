from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.dependencies import get_artifact_store
from artifact_store.lineage import get_artifact_lineage
from artifact_store.models import ArtifactRecord
from artifact_store.sqlite_store import ArtifactStore, RecordNotFoundError


router = APIRouter()


class ArtifactParentsResponse(BaseModel):
    artifact_id: str
    parents: dict[str, ArtifactRecord]


class ArtifactChildrenResponse(BaseModel):
    artifact_id: str
    children: list[ArtifactRecord]


@router.get(
    "/projects/{project_id}/runs/{run_id}/artifacts",
    response_model=list[ArtifactRecord],
)
def list_run_artifacts(
    project_id: str,
    run_id: str,
    store: ArtifactStore = Depends(get_artifact_store),
) -> list[ArtifactRecord]:
    try:
        return store.list_project_artifacts(project_id, run_id)
    except RecordNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.get("/projects/{project_id}/artifacts", response_model=list[ArtifactRecord])
def list_project_artifacts(
    project_id: str,
    store: ArtifactStore = Depends(get_artifact_store),
) -> list[ArtifactRecord]:
    try:
        return store.list_project_artifacts(project_id)
    except RecordNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.get("/artifacts/{artifact_id}", response_model=ArtifactRecord)
def get_artifact(
    artifact_id: str,
    store: ArtifactStore = Depends(get_artifact_store),
) -> ArtifactRecord:
    try:
        return store.get_artifact(artifact_id)
    except RecordNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.get("/artifacts/{artifact_id}/parents", response_model=ArtifactParentsResponse)
def get_artifact_parents(
    artifact_id: str,
    store: ArtifactStore = Depends(get_artifact_store),
) -> ArtifactParentsResponse:
    try:
        lineage = get_artifact_lineage(store, artifact_id)
    except RecordNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return ArtifactParentsResponse(artifact_id=artifact_id, parents=lineage.parents)


@router.get("/artifacts/{artifact_id}/children", response_model=ArtifactChildrenResponse)
def get_artifact_children(
    artifact_id: str,
    store: ArtifactStore = Depends(get_artifact_store),
) -> ArtifactChildrenResponse:
    try:
        lineage = get_artifact_lineage(store, artifact_id)
    except RecordNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return ArtifactChildrenResponse(artifact_id=artifact_id, children=lineage.children)

