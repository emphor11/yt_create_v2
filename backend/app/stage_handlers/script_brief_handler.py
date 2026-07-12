from dataclasses import asdict
from typing import Any

from artifact_store.models import ArtifactRecord
from artifact_store.sqlite_store import ArtifactStore
from app.stage_logger import StageLogger
from domain.script_brief import ScriptBrief
from domain.topic_request import TopicRequest
from domain.validation import ValidationResult
from domain.validators.script_brief_validator import ScriptBriefValidator
from engines.script_brief_ai_engine import ScriptBriefAIEngine, ScriptBriefAIEngineError
from engines.script_brief_engine import ScriptBriefEngine
from providers.llm_provider import LLMProviderMetadata


class ScriptBriefHandler:
    def __init__(
        self,
        *,
        store: ArtifactStore,
        script_brief_engine: ScriptBriefEngine,
        script_brief_ai_engine: ScriptBriefAIEngine | None,
        script_brief_validator: ScriptBriefValidator,
        stage_logger: StageLogger,
    ) -> None:
        self.store = store
        self.script_brief_engine = script_brief_engine
        self.script_brief_ai_engine = script_brief_ai_engine
        self.script_brief_validator = script_brief_validator
        self.stage_logger = stage_logger

    def run(self, project_id: str, run_id: str) -> ArtifactRecord:
        existing = self.store.find_artifact_by_type(project_id, run_id, "script_brief")
        if existing is not None:
            return existing

        start = self.stage_logger.log_start(project_id, run_id, "script_brief")
        try:
            topic_request_artifact = self.store.require_artifact(
                project_id, run_id, "topic_request", for_stage="script_brief"
            )
            run = self.store.get_run(project_id, run_id)
            topic_request = TopicRequest.model_validate(topic_request_artifact.payload_json)

            if run.mode == "ai":
                artifact = self._run_ai(
                    project_id=project_id,
                    run_id=run_id,
                    topic_request=topic_request,
                    topic_request_artifact_id=topic_request_artifact.id,
                )
                self.stage_logger.log_finish(project_id, run_id, "script_brief", start_time=start)
                return artifact

            script_brief = self.script_brief_engine.run(topic_request)
            validation = self.script_brief_validator.validate(
                script_brief, topic_request=topic_request
            )
            artifact = self.store.save_artifact(
                project_id=project_id,
                run_id=run_id,
                artifact_type="script_brief",
                schema_version=script_brief.schema_version,
                payload_json=script_brief.model_dump(),
                parent_artifact_roles_json={"topic_request": topic_request_artifact.id},
                validation_json=validation,
            )
        except Exception as exc:
            self.stage_logger.log_error(project_id, run_id, "script_brief", error=exc, start_time=start)
            raise
        self.stage_logger.log_finish(project_id, run_id, "script_brief", start_time=start)
        return artifact

    def _run_ai(
        self,
        *,
        project_id: str,
        run_id: str,
        topic_request: TopicRequest,
        topic_request_artifact_id: str,
    ) -> ArtifactRecord:
        from app.pipeline_service import PipelineServiceError

        if self.script_brief_ai_engine is None:
            raise PipelineServiceError("AI LLM provider is not configured for script_brief.")
        try:
            ai_result = self.script_brief_ai_engine.run(topic_request)
        except ScriptBriefAIEngineError as error:
            return self._save_failed_ai_script_brief(
                project_id=project_id,
                run_id=run_id,
                topic_request_artifact_id=topic_request_artifact_id,
                error=error,
            )

        script_brief = ai_result.script_brief
        validation = self.script_brief_validator.validate(
            script_brief, topic_request=topic_request
        )
        payload_json = script_brief.model_dump()
        payload_json["provider_metadata"] = asdict(ai_result.provider_metadata)
        return self.store.save_artifact(
            project_id=project_id,
            run_id=run_id,
            artifact_type="script_brief",
            schema_version=script_brief.schema_version,
            payload_json=payload_json,
            parent_artifact_roles_json={"topic_request": topic_request_artifact_id},
            validation_json=validation,
        )

    def _save_failed_ai_script_brief(
        self,
        *,
        project_id: str,
        run_id: str,
        topic_request_artifact_id: str,
        error: ScriptBriefAIEngineError,
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
            artifact_type="script_brief",
            schema_version="1",
            payload_json=payload_json,
            parent_artifact_roles_json={"topic_request": topic_request_artifact_id},
            validation_json=ValidationResult(status="failed", errors=[str(error)]),
        )
