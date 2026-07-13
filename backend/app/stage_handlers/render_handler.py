from artifact_store.models import ArtifactRecord
from artifact_store.sqlite_store import ArtifactStore
from app.stage_logger import StageLogger
from domain.render_spec import RenderSpec
from domain.validators.video_validator import VideoValidator
from engines.render_engine import RenderEngine


class RenderHandler:
    def __init__(
        self,
        *,
        store: ArtifactStore,
        render_engine: RenderEngine,
        video_validator: VideoValidator,
        stage_logger: StageLogger,
    ) -> None:
        self.store = store
        self.render_engine = render_engine
        self.video_validator = video_validator
        self.stage_logger = stage_logger

    def run(self, project_id: str, run_id: str) -> ArtifactRecord:
        from app.pipeline_service import PipelineServiceError

        existing = self.store.find_artifact_by_type(project_id, run_id, "video")
        if existing is not None:
            return existing

        # Retrieve run details

        start = self.stage_logger.log_start(project_id, run_id, "render")
        try:
            render_spec_artifact = self.store.require_artifact(
                project_id, run_id, "render_spec", for_stage="render"
            )
            render_spec = RenderSpec.model_validate(render_spec_artifact.payload_json)
            video = self.render_engine.run(
                render_spec=render_spec,
                project_id=project_id,
                run_id=run_id,
            )
            validation = self.video_validator.validate(video, render_spec=render_spec)
            artifact = self.store.save_artifact(
                project_id=project_id,
                run_id=run_id,
                artifact_type="video",
                schema_version=video.schema_version,
                payload_json=video.model_dump(),
                parent_artifact_roles_json={"render_spec": render_spec_artifact.id},
                validation_json=validation,
            )
        except Exception as exc:
            self.stage_logger.log_error(project_id, run_id, "render", error=exc, start_time=start)
            raise
        self.stage_logger.log_finish(project_id, run_id, "render", start_time=start)
        return artifact
