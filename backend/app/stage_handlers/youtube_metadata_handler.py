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
        if existing is not None and existing.status not in ("failed", "error"):
            return existing

        start = self.stage_logger.log_start(project_id, run_id, "youtube_metadata")
        try:
            # Require finished video and either compiled_world or render_spec
            video_artifact = self.store.require_artifact(
                project_id, run_id, "video", for_stage="youtube_metadata"
            )
            render_spec_artifact = self.store.find_artifact_by_type(
                project_id, run_id, "render_spec"
            )
            compiled_world_artifact = self.store.find_artifact_by_type(
                project_id, run_id, "compiled_world"
            )

            chapter_cues: list[str] = []
            render_spec = None
            if render_spec_artifact:
                render_spec = RenderSpec.model_validate(render_spec_artifact.payload_json)
            elif compiled_world_artifact:
                cw = compiled_world_artifact.payload_json
                fps = cw.get("canvas_config", {}).get("fps", 30) or 30
                sb_artifact = self.store.find_artifact_by_type(project_id, run_id, "storyboard")
                beat_narrations = {}
                if sb_artifact and sb_artifact.payload_json:
                    for b in sb_artifact.payload_json.get("beats", []):
                        b_id = b.get("beat_id", "")
                        b_narr = b.get("narration") or b.get("semantic_goal") or ""
                        if b_id:
                            beat_narrations[b_id] = b_narr

                for b_int in cw.get("beat_intervals", []):
                    b_id = b_int.get("beat_id", "")
                    narr = beat_narrations.get(b_id, b_id)
                    start_f = b_int.get("start_frame", 0)
                    seconds = int(start_f / fps)
                    mm = seconds // 60
                    ss = seconds % 60
                    ts = f"{mm:02d}:{ss:02d}"
                    chapter_cues.append(f"{ts} - {narr[:80]}")
            else:
                from app.pipeline_service import PipelineServiceError
                raise PipelineServiceError(
                    "Cannot run 'youtube_metadata': neither 'compiled_world' nor 'render_spec' artifact exists."
                )

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
                chapter_cues=chapter_cues if not render_spec else None,
                hook=hook,
                research=research,
                topic=topic,
                angle=angle,
            )

            validation = self.metadata_validator.validate(result.metadata)

            parent_roles = {
                "video": video_artifact.id,
            }
            if render_spec_artifact:
                parent_roles["render_spec"] = render_spec_artifact.id
            elif compiled_world_artifact:
                parent_roles["compiled_world"] = compiled_world_artifact.id
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
