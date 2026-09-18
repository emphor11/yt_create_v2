from artifact_store.models import ArtifactRecord
from artifact_store.sqlite_store import ArtifactStore
from app.stage_logger import StageLogger
from domain.thumbnail import Thumbnail
from domain.validators.youtube_upload_validator import YoutubeUploadValidator
from domain.video import Video
from domain.youtube_metadata import YoutubeMetadata
from engines.youtube_upload_engine import YoutubeUploadEngine


class YoutubeUploadHandler:
    def __init__(
        self,
        *,
        store: ArtifactStore,
        upload_engine: YoutubeUploadEngine,
        upload_validator: YoutubeUploadValidator,
        stage_logger: StageLogger,
    ) -> None:
        self.store = store
        self.upload_engine = upload_engine
        self.upload_validator = upload_validator
        self.stage_logger = stage_logger

    def run(self, project_id: str, run_id: str) -> ArtifactRecord:
        existing = self.store.find_artifact_by_type(project_id, run_id, "youtube_upload")
        if existing is not None:
            return existing

        start = self.stage_logger.log_start(project_id, run_id, "youtube_upload")
        try:
            video_artifact = self.store.require_artifact(
                project_id, run_id, "video", for_stage="youtube_upload"
            )
            video = Video.model_validate(video_artifact.payload_json)
            if video.render_status != "succeeded" or not video.storage_key:
                raise ValueError("Cannot upload to YouTube: Video rendering did not succeed or has no storage key.")

            metadata_artifact = self.store.require_artifact(
                project_id, run_id, "youtube_metadata", for_stage="youtube_upload"
            )
            metadata = YoutubeMetadata.model_validate(metadata_artifact.payload_json)

            thumbnail_artifact = self.store.find_artifact_by_type(project_id, run_id, "thumbnail")
            thumbnail_storage_key = None
            if thumbnail_artifact and thumbnail_artifact.status != "skipped":
                try:
                    thumbnail = Thumbnail.model_validate(thumbnail_artifact.payload_json)
                    thumbnail_storage_key = thumbnail.storage_key
                except Exception:
                    thumbnail_storage_key = None

            upload = self.upload_engine.run(
                video_storage_key=video.storage_key,
                metadata=metadata,
                thumbnail_storage_key=thumbnail_storage_key,
                privacy_status="private",
            )

            validation = self.upload_validator.validate(upload)

            parent_roles = {
                "video": video_artifact.id,
                "youtube_metadata": metadata_artifact.id,
            }
            if thumbnail_artifact and thumbnail_storage_key is not None:
                parent_roles["thumbnail"] = thumbnail_artifact.id

            artifact = self.store.save_artifact(
                project_id=project_id,
                run_id=run_id,
                artifact_type="youtube_upload",
                schema_version=upload.schema_version,
                payload_json=upload.model_dump(),
                parent_artifact_roles_json=parent_roles,
                validation_json=validation,
            )
        except Exception as exc:
            self.stage_logger.log_error(project_id, run_id, "youtube_upload", error=exc, start_time=start)
            raise

        self.stage_logger.log_finish(project_id, run_id, "youtube_upload", start_time=start)
        return artifact
