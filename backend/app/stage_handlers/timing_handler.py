from artifact_store.models import ArtifactRecord
from artifact_store.sqlite_store import ArtifactStore
from app.stage_logger import StageLogger
from domain.visual_event_sequence import VisualEventSequence
from domain.visual_plan import VisualPlan
from domain.validators.timed_scene_plan_validator import TimedScenePlanValidator
from engines.timing_engine import TimingEngine


class TimingHandler:
    def __init__(
        self,
        *,
        store: ArtifactStore,
        timing_engine: TimingEngine,
        timed_scene_plan_validator: TimedScenePlanValidator,
        stage_logger: StageLogger,
    ) -> None:
        self.store = store
        self.timing_engine = timing_engine
        self.timed_scene_plan_validator = timed_scene_plan_validator
        self.stage_logger = stage_logger

    def run(self, project_id: str, run_id: str) -> ArtifactRecord:
        from app.pipeline_service import PipelineServiceError

        existing = self.store.find_artifact_by_type(project_id, run_id, "timed_scene_plan")
        if existing is not None:
            return existing

        run = self.store.get_run(project_id, run_id)
        if run.mode == "ai":
            raise PipelineServiceError("AI mode is not implemented for timing yet.")

        start = self.stage_logger.log_start(project_id, run_id, "timing")
        try:
            visual_plan_artifact = self.store.require_artifact(
                project_id, run_id, "visual_plan", for_stage="timing"
            )
            visual_event_sequence_artifact = self.store.require_artifact(
                project_id, run_id, "visual_event_sequence", for_stage="timing"
            )
            visual_plan = VisualPlan.model_validate(visual_plan_artifact.payload_json)
            visual_event_sequence = VisualEventSequence.model_validate(
                visual_event_sequence_artifact.payload_json
            )
            timed_scene_plan = self.timing_engine.run(
                visual_plan=visual_plan,
                visual_event_sequence=visual_event_sequence,
            )
            validation = self.timed_scene_plan_validator.validate(
                timed_scene_plan,
                visual_plan=visual_plan,
                visual_event_sequence=visual_event_sequence,
            )
            artifact = self.store.save_artifact(
                project_id=project_id,
                run_id=run_id,
                artifact_type="timed_scene_plan",
                schema_version=timed_scene_plan.schema_version,
                payload_json=timed_scene_plan.model_dump(),
                parent_artifact_roles_json={
                    "visual_plan": visual_plan_artifact.id,
                    "visual_event_sequence": visual_event_sequence_artifact.id,
                },
                validation_json=validation,
            )
        except Exception as exc:
            self.stage_logger.log_error(project_id, run_id, "timing", error=exc, start_time=start)
            raise
        self.stage_logger.log_finish(project_id, run_id, "timing", start_time=start)
        return artifact
