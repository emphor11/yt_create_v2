from dataclasses import asdict
from typing import Any

from artifact_store.models import ArtifactRecord
from artifact_store.sqlite_store import ArtifactStore
from app.stage_logger import StageLogger
from domain.research_packet import ResearchPacket
from domain.narrative_plan import NarrativePlan
from domain.hook import Hook
from domain.script_visual_strategy import ScriptVisualStrategy
from domain.validation import ValidationResult
from domain.validators.script_visual_strategy_validator import ScriptVisualStrategyValidator
from engines.script_visual_strategy_engine import ScriptVisualStrategyEngine, ScriptVisualStrategyEngineError
from registries.component_registry import ComponentRegistry


class ScriptVisualStrategyHandler:
    def __init__(
        self,
        *,
        store: ArtifactStore,
        strategy_engine: ScriptVisualStrategyEngine,
        strategy_validator: ScriptVisualStrategyValidator,
        stage_logger: StageLogger,
        component_registry: ComponentRegistry,
    ) -> None:
        self.store = store
        self.strategy_engine = strategy_engine
        self.strategy_validator = strategy_validator
        self.stage_logger = stage_logger
        self.component_registry = component_registry

    def run(self, project_id: str, run_id: str) -> ArtifactRecord:
        existing = self.store.find_artifact_by_type(project_id, run_id, "script_visual_strategy")
        if existing is not None:
            return existing

        start = self.stage_logger.log_start(project_id, run_id, "script_visual_strategy")
        try:
            # 1. Retrieve prerequisite artifacts
            hook_artifact = self.store.require_artifact(
                project_id, run_id, "hook", for_stage="script_visual_strategy"
            )
            hook = Hook.model_validate(hook_artifact.payload_json)

            narrative_artifact = self.store.require_artifact(
                project_id, run_id, "narrative_plan", for_stage="script_visual_strategy"
            )
            narrative_plan = NarrativePlan.model_validate(narrative_artifact.payload_json)

            res_artifact = self.store.require_artifact(
                project_id, run_id, "research_packet", for_stage="script_visual_strategy"
            )
            research_packet = ResearchPacket.model_validate(res_artifact.payload_json)

            # 2. Run the Engine
            try:
                result = self.strategy_engine.run(research_packet, narrative_plan, hook)
            except ScriptVisualStrategyEngineError as error:
                # Save a failed validation artifact record on LLM/validation errors
                artifact = self._save_failed_strategy(
                    project_id=project_id,
                    run_id=run_id,
                    hook_art_id=hook_artifact.id,
                    error=error,
                )
                self.stage_logger.log_finish(project_id, run_id, "script_visual_strategy", start_time=start)
                return artifact

            strategy = result.strategy
            validation = self.strategy_validator.validate(strategy)
            payload_json = strategy.model_dump()
            payload_json["provider_metadata"] = asdict(result.provider_metadata)

            # 3. Save the unified artifact
            strategy_artifact = self.store.save_artifact(
                project_id=project_id,
                run_id=run_id,
                artifact_type="script_visual_strategy",
                schema_version=strategy.schema_version,
                payload_json=payload_json,
                parent_artifact_roles_json={
                    "hook": hook_artifact.id,
                    "narrative_plan": narrative_artifact.id,
                    "research_packet": res_artifact.id,
                },
                validation_json=validation,
            )

        except Exception as exc:
            self.stage_logger.log_error(project_id, run_id, "script_visual_strategy", error=exc, start_time=start)
            raise

        self.stage_logger.log_finish(project_id, run_id, "script_visual_strategy", start_time=start)
        return strategy_artifact

    def _save_failed_strategy(
        self,
        *,
        project_id: str,
        run_id: str,
        hook_art_id: str,
        error: ScriptVisualStrategyEngineError,
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
            artifact_type="script_visual_strategy",
            schema_version="1",
            payload_json=payload_json,
            parent_artifact_roles_json={"hook": hook_art_id},
            validation_json=ValidationResult(
                status="failed",
                errors=[str(error)],
            ),
        )
