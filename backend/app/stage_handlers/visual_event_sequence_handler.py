from artifact_store.models import ArtifactRecord
from artifact_store.sqlite_store import ArtifactStore
from app.stage_logger import StageLogger
from domain.semantic_scene import SemanticScene
from domain.validators.visual_event_sequence_validator import VisualEventSequenceValidator
from engines.visual_event_sequence_engine import VisualEventSequenceEngine


class VisualEventSequenceHandler:
    def __init__(
        self,
        *,
        store: ArtifactStore,
        visual_event_sequence_engine: VisualEventSequenceEngine,
        visual_event_sequence_validator: VisualEventSequenceValidator,
        stage_logger: StageLogger,
    ) -> None:
        self.store = store
        self.visual_event_sequence_engine = visual_event_sequence_engine
        self.visual_event_sequence_validator = visual_event_sequence_validator
        self.stage_logger = stage_logger

    def run(self, project_id: str, run_id: str) -> ArtifactRecord:
        from app.pipeline_service import PipelineServiceError

        existing = self.store.find_artifact_by_type(project_id, run_id, "visual_event_sequence")
        if existing is not None:
            return existing

        run = self.store.get_run(project_id, run_id)
        if run.mode == "ai":
            raise PipelineServiceError("AI mode is not implemented for visual_event_sequence yet.")

        start = self.stage_logger.log_start(project_id, run_id, "visual_event_sequence")
        try:
            semantic_scene_artifact = self.store.require_artifact(
                project_id, run_id, "semantic_scene", for_stage="visual_event_sequence"
            )
            semantic_scene = SemanticScene.model_validate(semantic_scene_artifact.payload_json)
            visual_event_sequence = self.visual_event_sequence_engine.run(semantic_scene)
            validation = self.visual_event_sequence_validator.validate(
                visual_event_sequence, semantic_scene=semantic_scene
            )
            artifact = self.store.save_artifact(
                project_id=project_id,
                run_id=run_id,
                artifact_type="visual_event_sequence",
                schema_version=visual_event_sequence.schema_version,
                payload_json=visual_event_sequence.model_dump(),
                parent_artifact_roles_json={"semantic_scene": semantic_scene_artifact.id},
                validation_json=validation,
            )
        except Exception as exc:
            self.stage_logger.log_error(project_id, run_id, "visual_event_sequence", error=exc, start_time=start)
            raise
        self.stage_logger.log_finish(project_id, run_id, "visual_event_sequence", start_time=start)
        return artifact
