from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.stage_logger import StageLogger
from artifact_store.models import ArtifactRecord
from artifact_store.sqlite_store import ArtifactStore
from domain.continuous_story_plan import ContinuousStoryDraft
from domain.research_packet import ResearchPacket
from domain.script_visual_strategy import ScriptVisualStrategy
from domain.validation import ValidationResult
from domain.validators.continuous_story_plan_validator import ContinuousStoryPlanValidator
from domain.voice_track import VoiceTrack
from engines.continuous_story_compiler import ContinuousStoryCompiler
from engines.continuous_story_engine import ContinuousStoryEngine, build_continuous_story_prompt
from providers.llm_provider import LLMProvider


class ContinuousStoryHandler:
    """
    Stage handler for the 'continuous_story' pipeline stage.

    Coordinates:
    1. Parent artifact retrieval (voice_track, script_visual_strategy, research_packet).
    2. Delegation to ContinuousStoryEngine.
    3. Artifact envelope validation (ContinuousStoryPlanValidator).
    4. Saving the ContinuousStoryPlanArtifact with full parent lineage.
    5. Saving the ContinuousStoryDebug artifact recording all Gemini attempts and validation errors.
    """

    def __init__(
        self,
        *,
        store: ArtifactStore,
        story_engine: ContinuousStoryEngine | None = None,
        artifact_validator: ContinuousStoryPlanValidator | None = None,
        stage_logger: StageLogger | None = None,
        llm_provider: LLMProvider | None = None,
        compiler: ContinuousStoryCompiler | None = None,
        asset_resolver: Any = None,
    ) -> None:
        self.store = store
        self.story_engine = story_engine or ContinuousStoryEngine(
            llm_provider=llm_provider,
            compiler=compiler,
            asset_resolver=asset_resolver,
        )
        self.artifact_validator = artifact_validator or ContinuousStoryPlanValidator()
        self.stage_logger = stage_logger or StageLogger()

    def _save_debug_artifact(
        self,
        project_id: str,
        run_id: str,
        call_history: list[dict[str, Any]],
        status: str,
        error_message: str | None = None,
        parent_artifact_roles: dict[str, str] | None = None,
    ) -> ArtifactRecord | None:
        try:
            debug_payload = {
                "project_id": project_id,
                "run_id": run_id,
                "status": status,
                "error_message": error_message,
                "total_calls": len(call_history),
                "calls": call_history,
            }
            # 1. Write to run-specific directory on disk
            disk_dir = (
                Path(__file__).resolve().parents[2]
                / ".data"
                / "media"
                / "projects"
                / project_id
                / "runs"
                / run_id
            )
            disk_dir.mkdir(parents=True, exist_ok=True)
            debug_file = disk_dir / "continuous_story_debug.json"
            debug_file.write_text(json.dumps(debug_payload, indent=2, default=str), encoding="utf-8")

            # 2. Persist to ArtifactStore
            existing_debug = self.store.find_artifact_by_type(project_id, run_id, "continuous_story_debug")
            if existing_debug is not None:
                self.store.delete_artifacts([existing_debug.id])

            valid_roles: dict[str, str] = {}
            if parent_artifact_roles:
                for role, art_id in parent_artifact_roles.items():
                    try:
                        self.store.get_artifact(art_id)
                        valid_roles[role] = art_id
                    except Exception:
                        pass

            validation = ValidationResult(
                status="valid" if status == "valid" else "failed",
                errors=[error_message] if error_message else [],
                warnings=[],
            )

            return self.store.save_artifact(
                project_id=project_id,
                run_id=run_id,
                artifact_type="continuous_story_debug",
                schema_version="1.0.0",
                payload_json=debug_payload,
                parent_artifact_roles_json=valid_roles,
                validation_json=validation,
            )
        except Exception as e:
            # Diagnostics must never crash the main pipeline flow
            print(f"[WARN] Failed to save continuous_story_debug artifact: {e}")
            return None

    def run(
        self,
        project_id: str,
        run_id: str,
        mock_draft: ContinuousStoryDraft | dict[str, Any] | None = None,
    ) -> ArtifactRecord:
        existing = self.store.find_artifact_by_type(project_id, run_id, "continuous_story_plan")
        if existing is not None and existing.status not in ("failed", "error"):
            return existing

        start = self.stage_logger.log_start(project_id, run_id, "continuous_story")
        parent_roles: dict[str, str] = {}
        try:
            # 1. Retrieve required parent artifacts
            voice_track_artifact = self.store.require_artifact(
                project_id, run_id, "voice_track", for_stage="continuous_story"
            )
            voice_track = VoiceTrack.model_validate(voice_track_artifact.payload_json)
            parent_roles["voice_track"] = voice_track_artifact.id

            strategy_artifact = self.store.require_artifact(
                project_id, run_id, "script_visual_strategy", for_stage="continuous_story"
            )
            strategy = ScriptVisualStrategy.model_validate(strategy_artifact.payload_json)
            parent_roles["script_visual_strategy"] = strategy_artifact.id

            research_artifact = self.store.require_artifact(
                project_id, run_id, "research_packet", for_stage="continuous_story"
            )
            research_packet = ResearchPacket.model_validate(research_artifact.payload_json)
            parent_roles["research_packet"] = research_artifact.id

            # 2. Resolve approved facts from parent artifact payload_json if present
            approved_facts: dict[str, Any] | None = None
            if isinstance(strategy_artifact.payload_json, dict) and strategy_artifact.payload_json.get("approved_facts"):
                approved_facts = strategy_artifact.payload_json["approved_facts"]
            elif isinstance(research_artifact.payload_json, dict) and research_artifact.payload_json.get("approved_facts"):
                approved_facts = research_artifact.payload_json["approved_facts"]

            # 3. Execute the engine
            result = self.story_engine.run(
                project_id=project_id,
                voice_track=voice_track,
                strategy=strategy,
                research_packet=research_packet,
                approved_facts=approved_facts,
                mock_draft=mock_draft,
            )

            # 4. Save debug artifact on success
            self._save_debug_artifact(
                project_id=project_id,
                run_id=run_id,
                call_history=result.call_history,
                status="valid",
                parent_artifact_roles=parent_roles,
            )

            # 5. Validate envelope
            validation_result = self.artifact_validator.validate(result.artifact)

            # 6. Persist to ArtifactStore with lineage
            payload_data = result.artifact.model_dump()
            payload_data["raw_gemini_draft"] = result.raw_payload

            artifact_record = self.store.save_artifact(
                project_id=project_id,
                run_id=run_id,
                artifact_type="continuous_story_plan",
                schema_version=result.artifact.schema_version,
                payload_json=payload_data,
                parent_artifact_roles_json=parent_roles,
                validation_json=validation_result,
            )
            self.stage_logger.log_finish(project_id, run_id, "continuous_story", start_time=start)
            return artifact_record
        except Exception as exc:
            call_history = getattr(exc, "call_history", None) or getattr(self.story_engine, "last_call_history", [])
            self._save_debug_artifact(
                project_id=project_id,
                run_id=run_id,
                call_history=call_history,
                status="failed",
                error_message=str(exc),
                parent_artifact_roles=parent_roles,
            )
            self.stage_logger.log_error(project_id, run_id, "continuous_story", error=exc, start_time=start)
            raise
