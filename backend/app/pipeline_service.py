"""Top-level pipeline service and stage router coordination.

Responsibilities
----------------
1. Orchestration: coordinates run lifecycle state machine transitions
   (pending -> running -> completed/failed) during execution.
2. Delegation: parses string stage names into PipelineStage enum values
   and dispatches execution to PipelineRouter.
3. Status summary & Descendant regeneration: core database coordination tasks.
"""
from __future__ import annotations

from typing import Any

from artifact_store.lineage import get_artifact_descendants
from artifact_store.models import ArtifactRecord
from artifact_store.sqlite_store import ArtifactStore
from domain.pipeline_stage import PipelineStage
from app.pipeline_router import PipelineRouter
from app.stage_logger import StageLogger

from app.stage_handlers.research_handler import ResearchHandler
from app.stage_handlers.narrative_plan_handler import NarrativePlanHandler
from app.stage_handlers.hook_handler import HookHandler
from app.stage_handlers.script_visual_strategy_handler import ScriptVisualStrategyHandler
from app.stage_handlers.quality_review_handler import QualityReviewHandler
from app.stage_handlers.voice_generation_handler import VoiceGenerationHandler
from app.stage_handlers.video_assembly_handler import VideoAssemblyHandler
from app.stage_handlers.render_handler import RenderHandler
from app.stage_handlers.youtube_metadata_handler import YoutubeMetadataHandler
from app.stage_handlers.thumbnail_handler import ThumbnailHandler
from app.stage_handlers.youtube_upload_handler import YoutubeUploadHandler

from engines.render_engine import RenderEngine
from engines.research_engine import ResearchEngine
from engines.narrative_plan_engine import NarrativePlanEngine
from engines.hook_engine import HookEngine
from engines.script_visual_strategy_engine import ScriptVisualStrategyEngine
from engines.visual_intent_engine import VisualIntentEngine
from engines.composition_planner_engine import CompositionPlannerEngine
from engines.composition_data_filler_engine import CompositionDataFillerEngine
from engines.video_assembly_engine import VideoAssemblyEngine
from engines.youtube_metadata_engine import YoutubeMetadataEngine
from engines.thumbnail_engine import ThumbnailEngine
from engines.youtube_upload_engine import YoutubeUploadEngine

from domain.validators.research_packet_validator import ResearchPacketValidator
from domain.validators.narrative_plan_validator import NarrativePlanValidator
from domain.validators.hook_validator import HookValidator
from domain.validators.script_visual_strategy_validator import ScriptVisualStrategyValidator
from domain.validators.review_result_validator import ReviewResultValidator
from domain.validators.voice_track_validator import VoiceTrackValidator
from domain.validators.render_spec_validator import RenderSpecValidator
from domain.validators.video_validator import VideoValidator
from domain.validators.youtube_metadata_validator import YoutubeMetadataValidator
from domain.validators.thumbnail_validator import ThumbnailValidator
from domain.validators.youtube_upload_validator import YoutubeUploadValidator

from providers.llm_provider import LLMProvider
from providers.media_storage import LocalMediaStorage
from providers.voice_provider import PollyVoiceProvider
from providers.remotion_provider import RemotionProvider
from providers.youtube_provider import YouTubeProvider
from registries.component_registry import ComponentRegistry



class PipelineServiceError(Exception):
    """Raised when a pipeline stage cannot run due to a business rule violation."""


OPTIONAL_STAGES: set[str] = {"thumbnail"}

AI_STAGE_DEFINITIONS: list[tuple[str, str]] = [
    ("generate_video_request",  "generate_video_request"),
    ("research",                "research_packet"),
    ("narrative_plan",          "narrative_plan"),
    ("hook",                    "hook"),
    ("script_visual_strategy",  "script_visual_strategy"),
    ("quality_review",          "review_result"),
    ("voice_generation",        "voice_track"),
    ("video_assembly",          "render_spec"),
    ("render",                  "video"),
    ("youtube_metadata",        "youtube_metadata"),
    ("thumbnail",               "thumbnail"),
    ("youtube_upload",          "youtube_upload"),
]

NEXT_STAGE_BY_ARTIFACT_TYPE: dict[str, str | None] = {
    "generate_video_request": "research",
    "research_packet":        "narrative_plan",
    "narrative_plan":         "hook",
    "hook":                   "script_visual_strategy",
    "script_visual_strategy": "quality_review",
    "review_result":          "voice_generation",
    "voice_track":            "video_assembly",
    "render_spec":            "render",
    "video":                  "youtube_metadata",
    "youtube_metadata":       "youtube_upload",
    "thumbnail":              "youtube_upload",
    "youtube_upload":         None,
}



class PipelineService:
    def __init__(
        self,
        *,
        store: ArtifactStore,
        router: PipelineRouter,
        stage_logger: StageLogger,
    ) -> None:
        self.store = store
        self.router = router
        self.stage_logger = stage_logger

    def run_stage(self, stage: str, project_id: str, run_id: str, **kwargs) -> ArtifactRecord:
        try:
            stage_enum = PipelineStage(stage)
        except ValueError as exc:
            raise PipelineServiceError(f"Stage '{stage}' is not implemented.") from exc

        # Delete failed/blocked artifact of this stage so the run can be retried cleanly
        artifact_type = None
        for s_name, a_type in AI_STAGE_DEFINITIONS:
            if s_name == stage_enum.value:
                artifact_type = a_type
                break

        from artifact_store.models import is_advanceable_status
        if artifact_type:
            existing = self.store.find_artifact_by_type(project_id, run_id, artifact_type)
            if existing is not None and not is_advanceable_status(existing.status):
                descendants = get_artifact_descendants(self.store, existing.id)
                ids_to_delete = [existing.id] + [d.id for d in descendants]
                self.store.delete_artifacts(ids_to_delete)

        # Update run state to 'running'
        self.store.update_run_state(
            project_id=project_id,
            run_id=run_id,
            state="running",
            current_stage=stage_enum.value,
        )

        try:
            artifact = self.router.execute(stage_enum, project_id, run_id, **kwargs)
        except Exception as exc:
            # Transition to 'failed' state on exception
            self.store.update_run_state(
                project_id=project_id,
                run_id=run_id,
                state="failed",
                current_stage=stage_enum.value,
                error_message=str(exc),
            )
            raise

        from artifact_store.models import is_advanceable_status

        if not is_advanceable_status(artifact.status):
            # If the artifact is not advanceable (failed/blocked), the run has failed
            self.store.update_run_state(
                project_id=project_id,
                run_id=run_id,
                state="failed",
                current_stage=stage_enum.value,
                error_message=f"Stage '{stage}' resulted in a non-advanceable status '{artifact.status}'."
            )
        else:
            # Check if this is the final stage
            next_stage = NEXT_STAGE_BY_ARTIFACT_TYPE.get(artifact.artifact_type)
            new_state = "completed" if next_stage is None else "running"
            self.store.update_run_state(
                project_id=project_id,
                run_id=run_id,
                state=new_state,
                current_stage=stage_enum.value,
            )

        return artifact

    def get_run_status(self, project_id: str, run_id: str) -> list[dict[str, Any]]:
        self.store.get_run(project_id, run_id)
        summaries: list[dict[str, Any]] = []
        for stage, artifact_type in AI_STAGE_DEFINITIONS:
            artifact = self.store.find_artifact_by_type(project_id, run_id, artifact_type)
            validation = artifact.validation_json if artifact is not None else None
            status = (
                artifact.status
                if artifact is not None
                else ("skipped" if stage in OPTIONAL_STAGES else "missing")
            )
            summaries.append(
                {
                    "stage": stage,
                    "artifact_type": artifact_type,
                    "artifact_id": artifact.id if artifact is not None else None,
                    "status": status,
                    "error_count": len(validation.errors) if validation is not None else 0,
                    "warning_count": len(validation.warnings) if validation is not None else 0,
                    "errors": validation.errors if validation is not None else [],
                    "warnings": validation.warnings if validation is not None else [],
                }
            )
        return summaries

    def regenerate_descendants(
        self,
        project_id: str,
        run_id: str,
        artifact_id: str,
    ) -> tuple[list[ArtifactRecord], str | None]:
        target_artifact = self.store.get_artifact(artifact_id)
        if target_artifact.project_id != project_id or target_artifact.run_id != run_id:
            raise PipelineServiceError(
                f"Artifact {artifact_id} does not belong to project {project_id} "
                f"and run {run_id}."
            )
        descendants = get_artifact_descendants(self.store, artifact_id)
        deleted_artifacts = self.store.delete_artifacts(
            [artifact.id for artifact in descendants]
        )
        return (
            deleted_artifacts,
            NEXT_STAGE_BY_ARTIFACT_TYPE.get(target_artifact.artifact_type),
        )


def build_pipeline_service(
    store: ArtifactStore,
    *,
    render_engine: RenderEngine | None = None,
    llm_provider: LLMProvider | None = None,
    image_generation_provider: Any = None,
    media_storage: LocalMediaStorage | None = None,
) -> PipelineService:
    from pathlib import Path

    component_registry = ComponentRegistry()
    stage_logger = StageLogger()

    repo_root = Path(__file__).resolve().parents[2]
    if media_storage is None:
        media_storage = LocalMediaStorage(repo_root / "backend" / ".data" / "media")

    voice_provider = PollyVoiceProvider()

    remotion_provider = RemotionProvider(repo_root / "renderer" / "remotion")
    if render_engine is None:
        render_engine = RenderEngine(
            media_storage=media_storage,
            remotion_provider=remotion_provider,
        )

    from providers.image_generation_provider import ImageGenerationProvider, build_image_generation_provider
    from engines.thumbnail_prompt_engine import ThumbnailPromptEngine

    if image_generation_provider is None:
        image_generation_provider = build_image_generation_provider()

    youtube_provider = YouTubeProvider()
    thumbnail_engine = ThumbnailEngine(
        media_storage=media_storage,
        image_provider=image_generation_provider,
        prompt_engine=ThumbnailPromptEngine(llm_provider),
    )
    youtube_metadata_engine = (
        YoutubeMetadataEngine(llm_provider) if llm_provider is not None else None
    )
    youtube_upload_engine = YoutubeUploadEngine(
        youtube_provider=youtube_provider,
        media_storage=media_storage,
    )

    import os
    thumbnail_enabled = os.getenv("ENABLE_THUMBNAIL_GENERATION", "false").lower() in {"true", "1", "yes"}

    handlers = {
        PipelineStage.RESEARCH: ResearchHandler(
            store=store,
            research_engine=ResearchEngine(llm_provider) if llm_provider is not None else None,
            research_packet_validator=ResearchPacketValidator(),
            stage_logger=stage_logger,
        ),
        PipelineStage.NARRATIVE_PLAN: NarrativePlanHandler(
            store=store,
            narrative_plan_engine=NarrativePlanEngine(llm_provider) if llm_provider is not None else None,
            narrative_plan_validator=NarrativePlanValidator(),
            stage_logger=stage_logger,
        ),
        PipelineStage.HOOK: HookHandler(
            store=store,
            hook_engine=HookEngine(llm_provider) if llm_provider is not None else None,
            hook_validator=HookValidator(),
            stage_logger=stage_logger,
        ),
        PipelineStage.SCRIPT_VISUAL_STRATEGY: ScriptVisualStrategyHandler(
            store=store,
            strategy_engine=ScriptVisualStrategyEngine(llm_provider) if llm_provider is not None else None,
            strategy_validator=ScriptVisualStrategyValidator(),
            stage_logger=stage_logger,
            visual_intent_engine=VisualIntentEngine(llm_provider) if llm_provider is not None else None,
            composition_planner_engine=(
                CompositionPlannerEngine(
                    llm_provider,
                    filler_engine=CompositionDataFillerEngine(llm_provider),
                )
                if llm_provider is not None else None
            ),
        ),
        PipelineStage.QUALITY_REVIEW: QualityReviewHandler(
            store=store,
            review_validator=ReviewResultValidator(),
            stage_logger=stage_logger,
        ),
        PipelineStage.VOICE_GENERATION: VoiceGenerationHandler(
            store=store,
            media_storage=media_storage,
            voice_provider=voice_provider,
            voice_validator=VoiceTrackValidator(),
            stage_logger=stage_logger,
        ),
        PipelineStage.RENDER: RenderHandler(
            store=store,
            render_engine=render_engine,
            video_validator=VideoValidator(),
            stage_logger=stage_logger,
        ),
        PipelineStage.VIDEO_ASSEMBLY: VideoAssemblyHandler(
            store=store,
            media_storage=media_storage,
            assembly_engine=VideoAssemblyEngine(),
            render_spec_validator=RenderSpecValidator(),
            stage_logger=stage_logger,
        ),
        PipelineStage.YOUTUBE_METADATA: YoutubeMetadataHandler(
            store=store,
            metadata_engine=youtube_metadata_engine,
            metadata_validator=YoutubeMetadataValidator(),
            stage_logger=stage_logger,
        ),
        PipelineStage.THUMBNAIL: ThumbnailHandler(
            store=store,
            thumbnail_engine=thumbnail_engine,
            thumbnail_validator=ThumbnailValidator(),
            stage_logger=stage_logger,
            enabled=thumbnail_enabled,
        ),
        PipelineStage.YOUTUBE_UPLOAD: YoutubeUploadHandler(
            store=store,
            upload_engine=youtube_upload_engine,
            upload_validator=YoutubeUploadValidator(),
            stage_logger=stage_logger,
        ),
    }

    router = PipelineRouter(handlers)

    return PipelineService(
        store=store,
        router=router,
        stage_logger=stage_logger,
    )
