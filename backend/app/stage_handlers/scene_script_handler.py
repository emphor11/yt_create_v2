from artifact_store.models import ArtifactRecord
from artifact_store.sqlite_store import ArtifactStore
from app.stage_logger import StageLogger
from domain.narrative_arc import NarrativeArc
from domain.script_brief import ScriptBrief
from domain.script_draft import ScriptDraft
from domain.validators.scene_script_validator import SceneScriptValidator
from engines.scene_script_engine import SceneScriptEngine


class SceneScriptHandler:
    def __init__(
        self,
        *,
        store: ArtifactStore,
        scene_script_engine: SceneScriptEngine,
        scene_script_validator: SceneScriptValidator,
        stage_logger: StageLogger,
    ) -> None:
        self.store = store
        self.scene_script_engine = scene_script_engine
        self.scene_script_validator = scene_script_validator
        self.stage_logger = stage_logger

    def run(self, project_id: str, run_id: str) -> ArtifactRecord:
        from app.pipeline_service import PipelineServiceError

        existing = self.store.find_artifact_by_type(project_id, run_id, "scene_script")
        if existing is not None:
            return existing

        run = self.store.get_run(project_id, run_id)
        if run.mode == "ai":
            raise PipelineServiceError("AI mode is not implemented for scene_script yet.")

        start = self.stage_logger.log_start(project_id, run_id, "scene_script")
        try:
            script_brief_artifact = self.store.require_artifact(
                project_id, run_id, "script_brief", for_stage="scene_script"
            )
            narrative_arc_artifact = self.store.require_artifact(
                project_id, run_id, "narrative_arc", for_stage="scene_script"
            )
            script_draft_artifact = self.store.require_artifact(
                project_id, run_id, "script_draft", for_stage="scene_script"
            )
            script_brief = ScriptBrief.model_validate(script_brief_artifact.payload_json)
            narrative_arc = NarrativeArc.model_validate(narrative_arc_artifact.payload_json)
            script_draft = ScriptDraft.model_validate(script_draft_artifact.payload_json)
            scene_script = self.scene_script_engine.run(
                script_brief=script_brief,
                narrative_arc=narrative_arc,
                script_draft=script_draft,
            )
            validation = self.scene_script_validator.validate(
                scene_script,
                script_brief=script_brief,
                narrative_arc=narrative_arc,
                script_draft=script_draft,
            )
            artifact = self.store.save_artifact(
                project_id=project_id,
                run_id=run_id,
                artifact_type="scene_script",
                schema_version=scene_script.schema_version,
                payload_json=scene_script.model_dump(),
                parent_artifact_roles_json={
                    "script_brief": script_brief_artifact.id,
                    "narrative_arc": narrative_arc_artifact.id,
                    "script_draft": script_draft_artifact.id,
                },
                validation_json=validation,
            )
        except Exception as exc:
            self.stage_logger.log_error(project_id, run_id, "scene_script", error=exc, start_time=start)
            raise
        self.stage_logger.log_finish(project_id, run_id, "scene_script", start_time=start)
        return artifact
