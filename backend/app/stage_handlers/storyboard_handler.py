from __future__ import annotations

from typing import Any
from artifact_store.models import ArtifactRecord
from artifact_store.sqlite_store import ArtifactStore
from app.stage_logger import StageLogger
from domain.storyboard import StoryboardInputContext
from domain.visual_intent_artifact import VisualIntentArtifact
from domain.narrative_plan import NarrativePlan
from domain.research_packet import ResearchPacket
from domain.voice_track import VoiceTrack
from domain.validators.storyboard_semantic_validator import StoryboardSemanticValidator
from engines.scene_storyboarder_engine import SceneStoryboarderEngine, SceneStoryboarderEngineError
from providers.llm_provider import LLMProvider


class StoryboardHandler:
    """Stage handler for generating the continuous VisualWorldSpec via SceneStoryboarderEngine."""

    def __init__(
        self,
        *,
        store: ArtifactStore,
        llm_provider: LLMProvider | None,
        stage_logger: StageLogger,
        semantic_validator: StoryboardSemanticValidator | None = None,
    ) -> None:
        self.store = store
        self.storyboard_engine = SceneStoryboarderEngine(llm_provider) if llm_provider else None
        self.semantic_validator = semantic_validator or StoryboardSemanticValidator()
        self.stage_logger = stage_logger

    def run(self, project_id: str, run_id: str) -> ArtifactRecord:
        from app.pipeline_service import PipelineServiceError

        existing = self.store.find_artifact_by_type(project_id, run_id, "storyboard")
        if existing is not None and existing.status not in ("failed", "error"):
            return existing

        if self.storyboard_engine is None:
            raise PipelineServiceError("LLM provider is not configured for StoryboardHandler.")

        start = self.stage_logger.log_start(project_id, run_id, "storyboard")
        try:
            # 1. Require parent artifacts
            voice_track_artifact = self.store.require_artifact(
                project_id, run_id, "voice_track", for_stage="storyboard"
            )
            vt_payload = voice_track_artifact.payload_json
            full_script = vt_payload.get("full_script_text") or ""
            if not full_script:
                segments = vt_payload.get("segments", [])
                full_script = " ".join(s.get("text", "") for s in segments if s.get("text"))

            vi_artifact = self.store.require_artifact(
                project_id, run_id, "visual_intent", for_stage="storyboard"
            )
            visual_intent_artifact = VisualIntentArtifact.model_validate(vi_artifact.payload_json)

            np_artifact = self.store.require_artifact(
                project_id, run_id, "narrative_plan", for_stage="storyboard"
            )
            narrative_plan = NarrativePlan.model_validate(np_artifact.payload_json)

            rp_artifact = self.store.require_artifact(
                project_id, run_id, "research_packet", for_stage="storyboard"
            )
            research_packet = ResearchPacket.model_validate(rp_artifact.payload_json)
            verified_facts = research_packet.verified_facts

            # 2. Build input context & run 2-pass storyboarder engine
            context = StoryboardInputContext(
                visual_intent_artifact=visual_intent_artifact,
                full_script=full_script,
                narrative_plan=narrative_plan,
                verified_facts=verified_facts,
            )

            result = self.storyboard_engine.run(context)
            storyboard = result.storyboard
            validation = self.semantic_validator.validate(storyboard)

            payload_json = result.world_foundation if result.world_foundation else storyboard.model_dump()

            # 3. Save storyboard artifact
            artifact = self.store.save_artifact(
                project_id=project_id,
                run_id=run_id,
                artifact_type="storyboard",
                schema_version="2.0.0",
                payload_json=payload_json,
                parent_artifact_roles_json={
                    "voice_track": voice_track_artifact.id,
                    "visual_intent": vi_artifact.id,
                    "narrative_plan": np_artifact.id,
                    "research_packet": rp_artifact.id,
                },
                validation_json=validation,
            )
        except Exception as exc:
            self.stage_logger.log_error(project_id, run_id, "storyboard", error=exc, start_time=start)
            raise
        self.stage_logger.log_finish(project_id, run_id, "storyboard", start_time=start)
        return artifact
