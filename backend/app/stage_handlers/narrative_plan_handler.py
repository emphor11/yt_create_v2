from dataclasses import asdict
from typing import Any

from artifact_store.models import ArtifactRecord
from artifact_store.sqlite_store import ArtifactStore
from app.stage_logger import StageLogger
from domain.research_packet import ResearchPacket
from domain.validation import ValidationResult
from domain.validators.narrative_plan_validator import NarrativePlanValidator
from engines.narrative_plan_engine import NarrativePlanEngine, NarrativePlanEngineError


class NarrativePlanHandler:
    def __init__(
        self,
        *,
        store: ArtifactStore,
        narrative_plan_engine: NarrativePlanEngine,
        narrative_plan_validator: NarrativePlanValidator,
        stage_logger: StageLogger,
    ) -> None:
        self.store = store
        self.narrative_plan_engine = narrative_plan_engine
        self.narrative_plan_validator = narrative_plan_validator
        self.stage_logger = stage_logger

    def run(self, project_id: str, run_id: str) -> ArtifactRecord:
        existing = self.store.find_artifact_by_type(project_id, run_id, "narrative_plan")
        if existing is not None:
            return existing

        start = self.stage_logger.log_start(project_id, run_id, "narrative_plan")
        try:
            res_artifact = self.store.require_artifact(
                project_id, run_id, "research_packet", for_stage="narrative_plan"
            )
            research_packet = ResearchPacket.model_validate(res_artifact.payload_json)

            try:
                result = self.narrative_plan_engine.run(research_packet)
            except NarrativePlanEngineError as error:
                # Save a failed validation artifact record on LLM/validation errors
                artifact = self._save_failed_plan(
                    project_id=project_id,
                    run_id=run_id,
                    res_artifact_id=res_artifact.id,
                    error=error,
                )
                self.stage_logger.log_finish(project_id, run_id, "narrative_plan", start_time=start)
                return artifact

            plan = result.narrative_plan
            validation = self.narrative_plan_validator.validate(plan)
            payload_json = plan.model_dump()
            payload_json["provider_metadata"] = asdict(result.provider_metadata)

            artifact = self.store.save_artifact(
                project_id=project_id,
                run_id=run_id,
                artifact_type="narrative_plan",
                schema_version=plan.schema_version,
                payload_json=payload_json,
                parent_artifact_roles_json={"research_packet": res_artifact.id},
                validation_json=validation,
            )
        except Exception as exc:
            self.stage_logger.log_error(project_id, run_id, "narrative_plan", error=exc, start_time=start)
            raise

        self.stage_logger.log_finish(project_id, run_id, "narrative_plan", start_time=start)
        return artifact

    def _save_failed_plan(
        self,
        *,
        project_id: str,
        run_id: str,
        res_artifact_id: str,
        error: NarrativePlanEngineError,
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
            artifact_type="narrative_plan",
            schema_version="1",
            payload_json=payload_json,
            parent_artifact_roles_json={"research_packet": res_artifact_id},
            validation_json=ValidationResult(
                status="failed",
                errors=[str(error)],
            ),
        )
