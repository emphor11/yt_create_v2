from artifact_store.models import ArtifactRecord
from artifact_store.sqlite_store import ArtifactStore
from app.stage_logger import StageLogger
from domain.generate_video_request import GenerateVideoRequest
from domain.hook import Hook
from domain.research_packet import ResearchPacket
from domain.thumbnail import Thumbnail
from domain.validators.thumbnail_validator import ThumbnailValidator
from domain.youtube_metadata import YoutubeMetadata
from engines.thumbnail_engine import ThumbnailEngine


class ThumbnailHandler:
    def __init__(
        self,
        *,
        store: ArtifactStore,
        thumbnail_engine: ThumbnailEngine,
        thumbnail_validator: ThumbnailValidator,
        stage_logger: StageLogger,
    ) -> None:
        self.store = store
        self.thumbnail_engine = thumbnail_engine
        self.thumbnail_validator = thumbnail_validator
        self.stage_logger = stage_logger

    def run(self, project_id: str, run_id: str) -> ArtifactRecord:
        existing = self.store.find_artifact_by_type(project_id, run_id, "thumbnail")
        if existing is not None:
            return existing

        start = self.stage_logger.log_start(project_id, run_id, "thumbnail")
        try:
            metadata_artifact = self.store.require_artifact(
                project_id, run_id, "youtube_metadata", for_stage="thumbnail"
            )
            metadata = YoutubeMetadata.model_validate(metadata_artifact.payload_json)

            hook_artifact = self.store.find_artifact_by_type(project_id, run_id, "hook")
            hook_line = ""
            if hook_artifact:
                hook = Hook.model_validate(hook_artifact.payload_json)
                hook_line = hook.script_text[:120] if hook.script_text else hook.conceptual_hook

            request_artifact = (
                self.store.find_artifact_by_type(project_id, run_id, "generate_video_request")
                or self.store.find_artifact_by_type(project_id, run_id, "topic_request")
            )
            topic = ""
            if request_artifact:
                req = GenerateVideoRequest.model_validate(request_artifact.payload_json)
                topic = req.topic
            elif hook_artifact:
                research_artifact = self.store.find_artifact_by_type(project_id, run_id, "research_packet")
                if research_artifact:
                    res = ResearchPacket.model_validate(research_artifact.payload_json)
                    topic = res.topic

            strategy_artifact = self.store.find_artifact_by_type(project_id, run_id, "script_visual_strategy")
            thesis = ""
            if strategy_artifact:
                thesis = strategy_artifact.payload_json.get("thesis", "")

            thumbnail = self.thumbnail_engine.run(
                metadata=metadata,
                hook_line=hook_line,
                topic=topic,
                thesis=thesis,
                project_id=project_id,
                run_id=run_id,
            )

            validation = self.thumbnail_validator.validate(thumbnail)

            parent_roles = {"youtube_metadata": metadata_artifact.id}
            if hook_artifact:
                parent_roles["hook"] = hook_artifact.id
            if strategy_artifact:
                parent_roles["script_visual_strategy"] = strategy_artifact.id

            artifact = self.store.save_artifact(
                project_id=project_id,
                run_id=run_id,
                artifact_type="thumbnail",
                schema_version=thumbnail.schema_version,
                payload_json=thumbnail.model_dump(),
                parent_artifact_roles_json=parent_roles,
                validation_json=validation,
            )
        except Exception as exc:
            self.stage_logger.log_error(project_id, run_id, "thumbnail", error=exc, start_time=start)
            raise

        self.stage_logger.log_finish(project_id, run_id, "thumbnail", start_time=start)
        return artifact
