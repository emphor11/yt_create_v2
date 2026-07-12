from artifact_store.models import ArtifactRecord
from artifact_store.sqlite_store import ArtifactStore
from app.stage_logger import StageLogger
from domain.semantic_scene import SemanticScene
from domain.visual_event_sequence import VisualEventSequence
from domain.validators.visual_plan_validator import VisualPlanValidator
from engines.visual_plan_engine import VisualPlanEngine


class VisualPlanHandler:
    def __init__(
        self,
        *,
        store: ArtifactStore,
        visual_plan_engine: VisualPlanEngine,
        visual_plan_validator: VisualPlanValidator,
        stage_logger: StageLogger,
    ) -> None:
        self.store = store
        self.visual_plan_engine = visual_plan_engine
        self.visual_plan_validator = visual_plan_validator
        self.stage_logger = stage_logger

    def run(self, project_id: str, run_id: str) -> ArtifactRecord:
        from app.pipeline_service import PipelineServiceError

        existing = self.store.find_artifact_by_type(project_id, run_id, "visual_plan")
        if existing is not None:
            return existing

        run = self.store.get_run(project_id, run_id)
        if run.mode == "ai":
            raise PipelineServiceError("AI mode is not implemented for visual_plan yet.")

        start = self.stage_logger.log_start(project_id, run_id, "visual_plan")
        try:
            semantic_scene_artifact = self.store.require_artifact(
                project_id, run_id, "semantic_scene", for_stage="visual_plan"
            )
            visual_event_sequence_artifact = self.store.require_artifact(
                project_id, run_id, "visual_event_sequence", for_stage="visual_plan"
            )
            semantic_scene = SemanticScene.model_validate(semantic_scene_artifact.payload_json)
            visual_event_sequence = VisualEventSequence.model_validate(
                visual_event_sequence_artifact.payload_json
            )
            visual_plan = self.visual_plan_engine.run(
                semantic_scene=semantic_scene,
                visual_event_sequence=visual_event_sequence,
            )
            validation = self.visual_plan_validator.validate(
                visual_plan,
                semantic_scene=semantic_scene,
                visual_event_sequence=visual_event_sequence,
            )
            artifact = self.store.save_artifact(
                project_id=project_id,
                run_id=run_id,
                artifact_type="visual_plan",
                schema_version=visual_plan.schema_version,
                payload_json=visual_plan.model_dump(),
                parent_artifact_roles_json={
                    "semantic_scene": semantic_scene_artifact.id,
                    "visual_event_sequence": visual_event_sequence_artifact.id,
                },
                validation_json=validation,
            )
        except Exception as exc:
            self.stage_logger.log_error(project_id, run_id, "visual_plan", error=exc, start_time=start)
            raise
        self.stage_logger.log_finish(project_id, run_id, "visual_plan", start_time=start)
        return artifact
