from artifact_store.models import ArtifactRecord
from artifact_store.sqlite_store import ArtifactStore
from app.stage_logger import StageLogger
from domain.scene_script import SceneScript
from domain.validators.semantic_scene_validator import SemanticSceneValidator
from engines.semantic_scene_engine import SemanticSceneEngine


class SemanticSceneHandler:
    def __init__(
        self,
        *,
        store: ArtifactStore,
        semantic_scene_engine: SemanticSceneEngine,
        semantic_scene_validator: SemanticSceneValidator,
        stage_logger: StageLogger,
    ) -> None:
        self.store = store
        self.semantic_scene_engine = semantic_scene_engine
        self.semantic_scene_validator = semantic_scene_validator
        self.stage_logger = stage_logger

    def run(self, project_id: str, run_id: str) -> ArtifactRecord:
        from app.pipeline_service import PipelineServiceError

        existing = self.store.find_artifact_by_type(project_id, run_id, "semantic_scene")
        if existing is not None:
            return existing

        run = self.store.get_run(project_id, run_id)
        if run.mode == "ai":
            raise PipelineServiceError("AI mode is not implemented for semantic_scene yet.")

        start = self.stage_logger.log_start(project_id, run_id, "semantic_scene")
        try:
            scene_script_artifact = self.store.require_artifact(
                project_id, run_id, "scene_script", for_stage="semantic_scene"
            )
            scene_script = SceneScript.model_validate(scene_script_artifact.payload_json)
            semantic_scene = self.semantic_scene_engine.run(scene_script)
            validation = self.semantic_scene_validator.validate(
                semantic_scene, scene_script=scene_script
            )
            artifact = self.store.save_artifact(
                project_id=project_id,
                run_id=run_id,
                artifact_type="semantic_scene",
                schema_version=semantic_scene.schema_version,
                payload_json=semantic_scene.model_dump(),
                parent_artifact_roles_json={"scene_script": scene_script_artifact.id},
                validation_json=validation,
            )
        except Exception as exc:
            self.stage_logger.log_error(project_id, run_id, "semantic_scene", error=exc, start_time=start)
            raise
        self.stage_logger.log_finish(project_id, run_id, "semantic_scene", start_time=start)
        return artifact
