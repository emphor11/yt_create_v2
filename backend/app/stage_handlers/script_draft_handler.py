from artifact_store.models import ArtifactRecord
from artifact_store.sqlite_store import ArtifactStore
from app.stage_logger import StageLogger
from domain.narrative_arc import NarrativeArc
from domain.script_brief import ScriptBrief
from domain.validators.script_draft_validator import ScriptDraftValidator
from engines.script_draft_engine import ScriptDraftEngine


class ScriptDraftHandler:
    def __init__(
        self,
        *,
        store: ArtifactStore,
        script_draft_engine: ScriptDraftEngine,
        script_draft_validator: ScriptDraftValidator,
        stage_logger: StageLogger,
    ) -> None:
        self.store = store
        self.script_draft_engine = script_draft_engine
        self.script_draft_validator = script_draft_validator
        self.stage_logger = stage_logger

    def run(self, project_id: str, run_id: str) -> ArtifactRecord:
        from app.pipeline_service import PipelineServiceError

        existing = self.store.find_artifact_by_type(project_id, run_id, "script_draft")
        if existing is not None:
            return existing

        run = self.store.get_run(project_id, run_id)
        if run.mode == "ai":
            raise PipelineServiceError("AI mode is not implemented for script_draft yet.")

        start = self.stage_logger.log_start(project_id, run_id, "script_draft")
        try:
            script_brief_artifact = self.store.require_artifact(
                project_id, run_id, "script_brief", for_stage="script_draft"
            )
            narrative_arc_artifact = self.store.require_artifact(
                project_id, run_id, "narrative_arc", for_stage="script_draft"
            )
            script_brief = ScriptBrief.model_validate(script_brief_artifact.payload_json)
            narrative_arc = NarrativeArc.model_validate(narrative_arc_artifact.payload_json)
            script_draft = self.script_draft_engine.run(
                script_brief=script_brief, narrative_arc=narrative_arc
            )
            validation = self.script_draft_validator.validate(
                script_draft, script_brief=script_brief, narrative_arc=narrative_arc
            )
            artifact = self.store.save_artifact(
                project_id=project_id,
                run_id=run_id,
                artifact_type="script_draft",
                schema_version=script_draft.schema_version,
                payload_json=script_draft.model_dump(),
                parent_artifact_roles_json={
                    "script_brief": script_brief_artifact.id,
                    "narrative_arc": narrative_arc_artifact.id,
                },
                validation_json=validation,
            )
        except Exception as exc:
            self.stage_logger.log_error(project_id, run_id, "script_draft", error=exc, start_time=start)
            raise
        self.stage_logger.log_finish(project_id, run_id, "script_draft", start_time=start)
        return artifact
