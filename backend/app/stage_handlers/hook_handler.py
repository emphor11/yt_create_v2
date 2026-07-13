from dataclasses import asdict
from typing import Any

from artifact_store.models import ArtifactRecord
from artifact_store.sqlite_store import ArtifactStore
from app.stage_logger import StageLogger
from domain.research_packet import ResearchPacket
from domain.narrative_plan import NarrativePlan
from domain.validation import ValidationResult
from domain.validators.hook_validator import HookValidator
from engines.hook_engine import HookEngine, HookEngineError


class HookHandler:
    def __init__(
        self,
        *,
        store: ArtifactStore,
        hook_engine: HookEngine,
        hook_validator: HookValidator,
        stage_logger: StageLogger,
    ) -> None:
        self.store = store
        self.hook_engine = hook_engine
        self.hook_validator = hook_validator
        self.stage_logger = stage_logger

    def run(self, project_id: str, run_id: str) -> ArtifactRecord:
        existing = self.store.find_artifact_by_type(project_id, run_id, "hook")
        if existing is not None:
            return existing

        start = self.stage_logger.log_start(project_id, run_id, "hook")
        try:
            # 1. Retrieve the prerequisite artifacts
            narrative_artifact = self.store.require_artifact(
                project_id, run_id, "narrative_plan", for_stage="hook"
            )
            narrative_plan = NarrativePlan.model_validate(narrative_artifact.payload_json)

            res_artifact = self.store.require_artifact(
                project_id, run_id, "research_packet", for_stage="hook"
            )
            research_packet = ResearchPacket.model_validate(res_artifact.payload_json)

            # 2. Execute the engine
            try:
                result = self.hook_engine.run(research_packet, narrative_plan)
            except HookEngineError as error:
                # Save a failed validation artifact record on LLM/validation errors
                artifact = self._save_failed_hook(
                    project_id=project_id,
                    run_id=run_id,
                    narrative_art_id=narrative_artifact.id,
                    error=error,
                )
                self.stage_logger.log_finish(project_id, run_id, "hook", start_time=start)
                return artifact

            hook = result.hook
            validation = self.hook_validator.validate(hook)
            payload_json = hook.model_dump()
            payload_json["provider_metadata"] = asdict(result.provider_metadata)

            artifact = self.store.save_artifact(
                project_id=project_id,
                run_id=run_id,
                artifact_type="hook",
                schema_version=hook.schema_version,
                payload_json=payload_json,
                parent_artifact_roles_json={
                    "narrative_plan": narrative_artifact.id,
                    "research_packet": res_artifact.id,
                },
                validation_json=validation,
            )
        except Exception as exc:
            self.stage_logger.log_error(project_id, run_id, "hook", error=exc, start_time=start)
            raise

        self.stage_logger.log_finish(project_id, run_id, "hook", start_time=start)
        return artifact

    def _save_failed_hook(
        self,
        *,
        project_id: str,
        run_id: str,
        narrative_art_id: str,
        error: HookEngineError,
    ) -> ArtifactRecord:
        payload_json: dict[str, Any] = {
            "schema_version": "1",
            "raw_ai_payload": error.raw_payload,
        }
        if error.provider_metadata is not None:
            payload_json["provider_metadata"] = asdict(error.provider_metadata)

        return self.store.save_artifact(
            project_id=project_id,
            run_id=run_id,
            artifact_type="hook",
            schema_version="1",
            payload_json=payload_json,
            parent_artifact_roles_json={"narrative_plan": narrative_art_id},
            validation_json=ValidationResult(
                status="failed",
                errors=[str(error)],
            ),
        )
