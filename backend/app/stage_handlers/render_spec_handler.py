from artifact_store.models import ArtifactRecord
from artifact_store.sqlite_store import ArtifactStore
from app.stage_logger import StageLogger
from domain.timed_scene_plan import TimedScenePlan
from domain.visual_plan import VisualPlan
from domain.validators.render_spec_validator import RenderSpecValidator
from engines.render_spec_engine import RenderSpecEngine


class RenderSpecHandler:
    def __init__(
        self,
        *,
        store: ArtifactStore,
        render_spec_engine: RenderSpecEngine,
        render_spec_validator: RenderSpecValidator,
        stage_logger: StageLogger,
    ) -> None:
        self.store = store
        self.render_spec_engine = render_spec_engine
        self.render_spec_validator = render_spec_validator
        self.stage_logger = stage_logger

    def run(self, project_id: str, run_id: str) -> ArtifactRecord:
        from app.pipeline_service import PipelineServiceError

        existing = self.store.find_artifact_by_type(project_id, run_id, "render_spec")
        if existing is not None:
            return existing

        # Retrieve run details

        start = self.stage_logger.log_start(project_id, run_id, "render_spec")
        try:
            visual_plan_artifact = self.store.require_artifact(
                project_id, run_id, "visual_plan", for_stage="render_spec"
            )
            timed_scene_plan_artifact = self.store.require_artifact(
                project_id, run_id, "timed_scene_plan", for_stage="render_spec"
            )
            visual_plan = VisualPlan.model_validate(visual_plan_artifact.payload_json)
            timed_scene_plan = TimedScenePlan.model_validate(
                timed_scene_plan_artifact.payload_json
            )
            render_spec = self.render_spec_engine.run(
                visual_plan=visual_plan,
                timed_scene_plan=timed_scene_plan,
            )
            validation = self.render_spec_validator.validate(
                render_spec,
                visual_plan=visual_plan,
                timed_scene_plan=timed_scene_plan,
            )
            artifact = self.store.save_artifact(
                project_id=project_id,
                run_id=run_id,
                artifact_type="render_spec",
                schema_version=render_spec.schema_version,
                payload_json=render_spec.model_dump(),
                parent_artifact_roles_json={
                    "visual_plan": visual_plan_artifact.id,
                    "timed_scene_plan": timed_scene_plan_artifact.id,
                },
                validation_json=validation,
            )
        except Exception as exc:
            self.stage_logger.log_error(project_id, run_id, "render_spec", error=exc, start_time=start)
            raise
        self.stage_logger.log_finish(project_id, run_id, "render_spec", start_time=start)
        return artifact
