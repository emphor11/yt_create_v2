from artifact_store.models import ArtifactRecord
from artifact_store.sqlite_store import ArtifactStore
from app.stage_logger import StageLogger
from domain.generate_video_request import GenerateVideoRequest
from domain.hook import Hook
from domain.render_spec import RenderSpec
from domain.research_packet import ResearchPacket
from domain.validators.youtube_metadata_validator import YoutubeMetadataValidator
from engines.youtube_metadata_engine import YoutubeMetadataEngine


class YoutubeMetadataHandler:
    def __init__(
        self,
        *,
        store: ArtifactStore,
        metadata_engine: YoutubeMetadataEngine,
        metadata_validator: YoutubeMetadataValidator,
        stage_logger: StageLogger,
    ) -> None:
        self.store = store
        self.metadata_engine = metadata_engine
        self.metadata_validator = metadata_validator
        self.stage_logger = stage_logger

    def run(self, project_id: str, run_id: str) -> ArtifactRecord:
        existing = self.store.find_artifact_by_type(project_id, run_id, "youtube_metadata")
        if existing is not None:
            return existing

        start = self.stage_logger.log_start(project_id, run_id, "youtube_metadata")
        try:
            # Require finished video and render spec
            video_artifact = self.store.require_artifact(
                project_id, run_id, "video", for_stage="youtube_metadata"
            )
            render_spec_artifact = self.store.require_artifact(
                project_id, run_id, "render_spec", for_stage="youtube_metadata"
            )
            render_spec = RenderSpec.model_validate(render_spec_artifact.payload_json)

            # Optional/additional context artifacts
            hook_artifact = self.store.find_artifact_by_type(project_id, run_id, "hook")
            hook = Hook.model_validate(hook_artifact.payload_json) if hook_artifact else None

            research_artifact = self.store.find_artifact_by_type(project_id, run_id, "research_packet")
            research = ResearchPacket.model_validate(research_artifact.payload_json) if research_artifact else None

            request_artifact = (
                self.store.find_artifact_by_type(project_id, run_id, "generate_video_request")
                or self.store.find_artifact_by_type(project_id, run_id, "topic_request")
            )
            topic = ""
            angle = ""
            if request_artifact:
                req = GenerateVideoRequest.model_validate(request_artifact.payload_json)
                topic = req.topic
                angle = req.angle

            result = self.metadata_engine.run(
                render_spec=render_spec,
                hook=hook,
                research=research,
                topic=topic,
                angle=angle,
            )

            validation = self.metadata_validator.validate(result.metadata)

            parent_roles = {
                "video": video_artifact.id,
                "render_spec": render_spec_artifact.id,
            }
            if hook_artifact:
                parent_roles["hook"] = hook_artifact.id

            artifact = self.store.save_artifact(
                project_id=project_id,
                run_id=run_id,
                artifact_type="youtube_metadata",
                schema_version=result.metadata.schema_version,
                payload_json=result.metadata.model_dump(),
                parent_artifact_roles_json=parent_roles,
                validation_json=validation,
            )
        except Exception as exc:
            self.stage_logger.log_error(project_id, run_id, "youtube_metadata", error=exc, start_time=start)
            raise

        self.stage_logger.log_finish(project_id, run_id, "youtube_metadata", start_time=start)
        return artifact
