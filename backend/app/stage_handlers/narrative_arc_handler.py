from artifact_store.models import ArtifactRecord
from artifact_store.sqlite_store import ArtifactStore
from app.stage_logger import StageLogger
from domain.script_brief import ScriptBrief
from domain.validators.narrative_arc_validator import NarrativeArcValidator
from engines.narrative_arc_engine import NarrativeArcEngine


class NarrativeArcHandler:
    def __init__(
        self,
        *,
        store: ArtifactStore,
        narrative_arc_engine: NarrativeArcEngine,
        narrative_arc_validator: NarrativeArcValidator,
        stage_logger: StageLogger,
    ) -> None:
        self.store = store
        self.narrative_arc_engine = narrative_arc_engine
        self.narrative_arc_validator = narrative_arc_validator
        self.stage_logger = stage_logger

    def run(self, project_id: str, run_id: str) -> ArtifactRecord:
        from app.pipeline_service import PipelineServiceError

        existing = self.store.find_artifact_by_type(project_id, run_id, "narrative_arc")
        if existing is not None:
            return existing

        run = self.store.get_run(project_id, run_id)
        if run.mode == "ai":
            raise PipelineServiceError("AI mode is not implemented for narrative_arc yet.")

        start = self.stage_logger.log_start(project_id, run_id, "narrative_arc")
        try:
            script_brief_artifact = self.store.require_artifact(
                project_id, run_id, "script_brief", for_stage="narrative_arc"
            )
            script_brief = ScriptBrief.model_validate(script_brief_artifact.payload_json)
            narrative_arc = self.narrative_arc_engine.run(script_brief)
            validation = self.narrative_arc_validator.validate(
                narrative_arc, script_brief=script_brief
            )
            artifact = self.store.save_artifact(
                project_id=project_id,
                run_id=run_id,
                artifact_type="narrative_arc",
                schema_version=narrative_arc.schema_version,
                payload_json=narrative_arc.model_dump(),
                parent_artifact_roles_json={"script_brief": script_brief_artifact.id},
                validation_json=validation,
            )
        except Exception as exc:
            self.stage_logger.log_error(project_id, run_id, "narrative_arc", error=exc, start_time=start)
            raise
        self.stage_logger.log_finish(project_id, run_id, "narrative_arc", start_time=start)
        return artifact
