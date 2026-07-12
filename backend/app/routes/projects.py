from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.dependencies import get_artifact_store
from artifact_store.models import ArtifactRecord, PipelineRunRecord, ProjectRecord, RunMode
from artifact_store.sqlite_store import ArtifactStore, RecordNotFoundError
from domain.topic_request import TopicRequest
from domain.validators.topic_request_validator import TopicRequestValidator
from domain.generate_video_request import GenerateVideoRequest
from domain.validators.generate_video_request_validator import GenerateVideoRequestValidator


router = APIRouter()


class CreateProjectRequest(BaseModel):
    topic: str = ""
    angle: str = ""
    title: str | None = None
    mode: RunMode = "deterministic"
    audience: str = ""
    language: str = ""
    style: str = ""
    channel: str = ""


class CreateProjectResponse(BaseModel):
    project: ProjectRecord
    run: PipelineRunRecord
    topic_request_artifact: ArtifactRecord | None = None
    generate_video_request_artifact: ArtifactRecord | None = None


@router.post("/projects", response_model=CreateProjectResponse)
def create_project(
    request: CreateProjectRequest,
    store: ArtifactStore = Depends(get_artifact_store),
) -> CreateProjectResponse:
    try:
        topic = request.topic.strip()
        angle = request.angle.strip()
        project_title = (request.title or "").strip() or topic or "Untitled Project"
        project = store.create_project(project_title)
        run = store.create_run(project.id, mode=request.mode)

        topic_request_artifact = None
        generate_video_request_artifact = None

        new_mvp_fields = {"audience", "language", "style", "channel"}
        is_new_ai_mvp = request.mode == "ai" and bool(request.model_fields_set & new_mvp_fields)

        if is_new_ai_mvp:
            gen_req = GenerateVideoRequest(
                topic=topic,
                audience=request.audience.strip(),
                language=request.language.strip(),
                style=request.style.strip(),
                channel=request.channel.strip(),
            )
            validation = GenerateVideoRequestValidator().validate(gen_req)
            generate_video_request_artifact = store.save_artifact(
                project_id=project.id,
                run_id=run.id,
                artifact_type="generate_video_request",
                schema_version=gen_req.schema_version,
                payload_json=gen_req.model_dump(),
                parent_artifact_roles_json={},
                validation_json=validation,
            )
        else:
            topic_request = TopicRequest(topic=topic, angle=angle)
            validation = TopicRequestValidator().validate(topic_request)
            topic_request_artifact = store.save_artifact(
                project_id=project.id,
                run_id=run.id,
                artifact_type="topic_request",
                schema_version=topic_request.schema_version,
                payload_json=topic_request.model_dump(),
                parent_artifact_roles_json={},
                validation_json=validation,
            )
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    return CreateProjectResponse(
        project=project,
        run=run,
        topic_request_artifact=topic_request_artifact,
        generate_video_request_artifact=generate_video_request_artifact,
    )


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
