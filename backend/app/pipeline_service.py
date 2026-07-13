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
from app.stage_handlers.script_brief_handler import ScriptBriefHandler
from app.stage_handlers.research_handler import ResearchHandler
from app.stage_handlers.narrative_plan_handler import NarrativePlanHandler
from app.stage_handlers.hook_handler import HookHandler
from app.stage_handlers.script_visual_strategy_handler import ScriptVisualStrategyHandler
from app.stage_handlers.narrative_arc_handler import NarrativeArcHandler
from app.stage_handlers.script_draft_handler import ScriptDraftHandler
from app.stage_handlers.scene_script_handler import SceneScriptHandler
from app.stage_handlers.semantic_scene_handler import SemanticSceneHandler
from app.stage_handlers.visual_event_sequence_handler import VisualEventSequenceHandler
from app.stage_handlers.visual_plan_handler import VisualPlanHandler
from app.stage_handlers.timing_handler import TimingHandler
from app.stage_handlers.render_spec_handler import RenderSpecHandler
from app.stage_handlers.render_handler import RenderHandler

from engines.render_engine import RenderEngine
from engines.research_engine import ResearchEngine
from engines.narrative_plan_engine import NarrativePlanEngine
from engines.hook_engine import HookEngine
from engines.script_visual_strategy_engine import ScriptVisualStrategyEngine
from engines.narrative_arc_engine import NarrativeArcEngine
from engines.render_spec_engine import RenderSpecEngine
from engines.scene_script_engine import SceneScriptEngine
from engines.script_brief_ai_engine import ScriptBriefAIEngine
from engines.semantic_scene_engine import SemanticSceneEngine
from engines.script_brief_engine import ScriptBriefEngine
from engines.script_draft_engine import ScriptDraftEngine
from engines.timing_engine import TimingEngine
from engines.visual_event_sequence_engine import VisualEventSequenceEngine
from engines.visual_plan_engine import VisualPlanEngine

from domain.validators.narrative_arc_validator import NarrativeArcValidator
from domain.validators.research_packet_validator import ResearchPacketValidator
from domain.validators.narrative_plan_validator import NarrativePlanValidator
from domain.validators.hook_validator import HookValidator
from domain.validators.script_visual_strategy_validator import ScriptVisualStrategyValidator
from domain.validators.render_spec_validator import RenderSpecValidator
from domain.validators.scene_script_validator import SceneScriptValidator
from domain.validators.script_brief_validator import ScriptBriefValidator
from domain.validators.script_draft_validator import ScriptDraftValidator
from domain.validators.semantic_scene_validator import SemanticSceneValidator
from domain.validators.timed_scene_plan_validator import TimedScenePlanValidator
from domain.validators.video_validator import VideoValidator
from domain.validators.visual_event_sequence_validator import VisualEventSequenceValidator
from domain.validators.visual_plan_validator import VisualPlanValidator

from providers.llm_provider import LLMProvider
from providers.media_storage import LocalMediaStorage
from providers.remotion_provider import RemotionProvider
from registries.component_registry import ComponentRegistry
from registries.finance_domain_registry import FinanceDomainRegistry


class PipelineServiceError(Exception):
    """Raised when a pipeline stage cannot run due to a business rule violation."""


# Order and mapping definition
DETERMINISTIC_STAGE_DEFINITIONS: list[tuple[str, str]] = [
    ("topic_request",           "topic_request"),
    ("script_brief",            "script_brief"),
    ("narrative_arc",           "narrative_arc"),
    ("script_draft",            "script_draft"),
    ("scene_script",            "scene_script"),
    ("semantic_scene",          "semantic_scene"),
    ("visual_event_sequence",   "visual_event_sequence"),
    ("visual_plan",             "visual_plan"),
    ("timing",                  "timed_scene_plan"),
    ("render_spec",             "render_spec"),
    ("render",                  "video"),
]

AI_STAGE_DEFINITIONS: list[tuple[str, str]] = [
    ("generate_video_request",  "generate_video_request"),
    ("research",                "research_packet"),
    ("narrative_plan",          "narrative_plan"),
    ("hook",                    "hook"),
    ("script_visual_strategy",  "script_visual_strategy"),
]

NEXT_STAGE_BY_ARTIFACT_TYPE: dict[str, str | None] = {
    "topic_request":          "script_brief",
    "generate_video_request": "research",
    "research_packet":        "narrative_plan",
    "narrative_plan":         "hook",
    "hook":                   "script_visual_strategy",
    "script_visual_strategy": "timing",
    "script_brief":           "narrative_arc",
    "narrative_arc":          "script_draft",
    "script_draft":           "scene_script",
    "scene_script":           "semantic_scene",
    "semantic_scene":         "visual_event_sequence",
    "visual_event_sequence":  "visual_plan",
    "visual_plan":            "timing",
    "timed_scene_plan":       "render_spec",
    "render_spec":            "render",
    "video":                  None,
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

    def run_stage(self, stage: str, project_id: str, run_id: str) -> ArtifactRecord:
        try:
            stage_enum = PipelineStage(stage)
        except ValueError as exc:
            raise PipelineServiceError(f"Stage '{stage}' is not implemented.") from exc

        # Update run state to 'running'
        self.store.update_run_state(
            project_id=project_id,
            run_id=run_id,
            state="running",
            current_stage=stage_enum.value,
        )

        try:
            artifact = self.router.execute(stage_enum, project_id, run_id)
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
        run = self.store.get_run(project_id, run_id)
        stage_definitions = (
            AI_STAGE_DEFINITIONS if run.mode == "ai" else DETERMINISTIC_STAGE_DEFINITIONS
        )
        summaries: list[dict[str, Any]] = []
        for stage, artifact_type in stage_definitions:
            artifact = self.store.find_artifact_by_type(project_id, run_id, artifact_type)
            validation = artifact.validation_json if artifact is not None else None
            summaries.append(
                {
                    "stage": stage,
                    "artifact_type": artifact_type,
                    "artifact_id": artifact.id if artifact is not None else None,
                    "status": artifact.status if artifact is not None else "missing",
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

    # Legacy method aliases for backward-compatible tests
    def run_research(self, project_id: str, run_id: str) -> ArtifactRecord:
        return self.run_stage(PipelineStage.RESEARCH.value, project_id, run_id)

    def run_narrative_plan(self, project_id: str, run_id: str) -> ArtifactRecord:
        return self.run_stage(PipelineStage.NARRATIVE_PLAN.value, project_id, run_id)

    def run_hook(self, project_id: str, run_id: str) -> ArtifactRecord:
        return self.run_stage(PipelineStage.HOOK.value, project_id, run_id)

    def run_script_visual_strategy(self, project_id: str, run_id: str) -> ArtifactRecord:
        return self.run_stage(PipelineStage.SCRIPT_VISUAL_STRATEGY.value, project_id, run_id)

    def run_script_brief(self, project_id: str, run_id: str) -> ArtifactRecord:
        return self.run_stage(PipelineStage.SCRIPT_BRIEF.value, project_id, run_id)

    def run_narrative_arc(self, project_id: str, run_id: str) -> ArtifactRecord:
        return self.run_stage(PipelineStage.NARRATIVE_ARC.value, project_id, run_id)

    def run_script_draft(self, project_id: str, run_id: str) -> ArtifactRecord:
        return self.run_stage(PipelineStage.SCRIPT_DRAFT.value, project_id, run_id)

    def run_scene_script(self, project_id: str, run_id: str) -> ArtifactRecord:
        return self.run_stage(PipelineStage.SCENE_SCRIPT.value, project_id, run_id)

    def run_semantic_scene(self, project_id: str, run_id: str) -> ArtifactRecord:
        return self.run_stage(PipelineStage.SEMANTIC_SCENE.value, project_id, run_id)

    def run_visual_event_sequence(self, project_id: str, run_id: str) -> ArtifactRecord:
        return self.run_stage(PipelineStage.VISUAL_EVENT_SEQUENCE.value, project_id, run_id)

    def run_visual_plan(self, project_id: str, run_id: str) -> ArtifactRecord:
        return self.run_stage(PipelineStage.VISUAL_PLAN.value, project_id, run_id)

    def run_timing(self, project_id: str, run_id: str) -> ArtifactRecord:
        return self.run_stage(PipelineStage.TIMING.value, project_id, run_id)

    def run_render_spec(self, project_id: str, run_id: str) -> ArtifactRecord:
        return self.run_stage(PipelineStage.RENDER_SPEC.value, project_id, run_id)

    def run_render(self, project_id: str, run_id: str) -> ArtifactRecord:
        return self.run_stage(PipelineStage.RENDER.value, project_id, run_id)


def build_pipeline_service(
    store: ArtifactStore,
    *,
    render_engine: RenderEngine | None = None,
    llm_provider: LLMProvider | None = None,
) -> PipelineService:
    from pathlib import Path

    finance_registry = FinanceDomainRegistry()
    component_registry = ComponentRegistry()
    stage_logger = StageLogger()

    if render_engine is None:
        repo_root = Path(__file__).resolve().parents[2]
        render_engine = RenderEngine(
            media_storage=LocalMediaStorage(repo_root / "backend" / ".data" / "media"),
            remotion_provider=RemotionProvider(repo_root / "renderer" / "remotion"),
        )

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
            component_registry=component_registry,
        ),
        PipelineStage.SCRIPT_BRIEF: ScriptBriefHandler(
            store=store,
            script_brief_engine=ScriptBriefEngine(),
            script_brief_ai_engine=(
                ScriptBriefAIEngine(llm_provider) if llm_provider is not None else None
            ),
            script_brief_validator=ScriptBriefValidator(finance_registry),
            stage_logger=stage_logger,
        ),
        PipelineStage.NARRATIVE_ARC: NarrativeArcHandler(
            store=store,
            narrative_arc_engine=NarrativeArcEngine(),
            narrative_arc_validator=NarrativeArcValidator(),
            stage_logger=stage_logger,
        ),
        PipelineStage.SCRIPT_DRAFT: ScriptDraftHandler(
            store=store,
            script_draft_engine=ScriptDraftEngine(),
            script_draft_validator=ScriptDraftValidator(),
            stage_logger=stage_logger,
        ),
        PipelineStage.SCENE_SCRIPT: SceneScriptHandler(
            store=store,
            scene_script_engine=SceneScriptEngine(),
            scene_script_validator=SceneScriptValidator(),
            stage_logger=stage_logger,
        ),
        PipelineStage.SEMANTIC_SCENE: SemanticSceneHandler(
            store=store,
            semantic_scene_engine=SemanticSceneEngine(finance_registry),
            semantic_scene_validator=SemanticSceneValidator(finance_registry),
            stage_logger=stage_logger,
        ),
        PipelineStage.VISUAL_EVENT_SEQUENCE: VisualEventSequenceHandler(
            store=store,
            visual_event_sequence_engine=VisualEventSequenceEngine(),
            visual_event_sequence_validator=VisualEventSequenceValidator(),
            stage_logger=stage_logger,
        ),
        PipelineStage.VISUAL_PLAN: VisualPlanHandler(
            store=store,
            visual_plan_engine=VisualPlanEngine(component_registry),
            visual_plan_validator=VisualPlanValidator(component_registry),
            stage_logger=stage_logger,
        ),
        PipelineStage.TIMING: TimingHandler(
            store=store,
            timing_engine=TimingEngine(),
            timed_scene_plan_validator=TimedScenePlanValidator(),
            stage_logger=stage_logger,
        ),
        PipelineStage.RENDER_SPEC: RenderSpecHandler(
            store=store,
            render_spec_engine=RenderSpecEngine(),
            render_spec_validator=RenderSpecValidator(),
            stage_logger=stage_logger,
        ),
        PipelineStage.RENDER: RenderHandler(
            store=store,
            render_engine=render_engine,
            video_validator=VideoValidator(),
            stage_logger=stage_logger,
        ),
    }

    router = PipelineRouter(handlers)

    return PipelineService(
        store=store,
        router=router,
        stage_logger=stage_logger,
    )
