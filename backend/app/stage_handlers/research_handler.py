from dataclasses import asdict
from typing import Any

from artifact_store.models import ArtifactRecord
from artifact_store.sqlite_store import ArtifactStore
from app.stage_logger import StageLogger
from domain.generate_video_request import GenerateVideoRequest
from domain.validation import ValidationResult
from domain.validators.research_packet_validator import ResearchPacketValidator
from engines.research_engine import ResearchEngine, ResearchEngineError


class ResearchHandler:
    def __init__(
        self,
        *,
        store: ArtifactStore,
        research_engine: ResearchEngine,
        research_packet_validator: ResearchPacketValidator,
        stage_logger: StageLogger,
    ) -> None:
        self.store = store
        self.research_engine = research_engine
        self.research_packet_validator = research_packet_validator
        self.stage_logger = stage_logger

    def run(self, project_id: str, run_id: str) -> ArtifactRecord:
        existing = self.store.find_artifact_by_type(project_id, run_id, "research_packet")
        if existing is not None:
            return existing

        start = self.stage_logger.log_start(project_id, run_id, "research")
        try:
            req_artifact = self.store.require_artifact(
                project_id, run_id, "generate_video_request", for_stage="research"
            )
            request = GenerateVideoRequest.model_validate(req_artifact.payload_json)

            try:
                result = self.research_engine.run(request)
            except ResearchEngineError as error:
                # Save a failed validation artifact record on LLM/validation errors
                artifact = self._save_failed_research(
                    project_id=project_id,
                    run_id=run_id,
                    req_artifact_id=req_artifact.id,
                    error=error,
                )
                self.stage_logger.log_finish(project_id, run_id, "research", start_time=start)
                return artifact

            packet = result.research_packet
            validation = self.research_packet_validator.validate(packet)
            payload_json = packet.model_dump()
            payload_json["provider_metadata"] = asdict(result.provider_metadata)

            artifact = self.store.save_artifact(
                project_id=project_id,
                run_id=run_id,
                artifact_type="research_packet",
                schema_version=packet.schema_version,
                payload_json=payload_json,
                parent_artifact_roles_json={"generate_video_request": req_artifact.id},
                validation_json=validation,
            )
        except Exception as exc:
            self.stage_logger.log_error(project_id, run_id, "research", error=exc, start_time=start)
            raise

        self.stage_logger.log_finish(project_id, run_id, "research", start_time=start)
        return artifact

    def _save_failed_research(
        self,
        *,
        project_id: str,
        run_id: str,
        req_artifact_id: str,
        error: ResearchEngineError,
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
            artifact_type="research_packet",
            schema_version="1",
            payload_json=payload_json,
            parent_artifact_roles_json={"generate_video_request": req_artifact_id},
            validation_json=ValidationResult(
                status="failed",
                errors=[str(error)],
            ),
        )
