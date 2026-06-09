from artifact_store.models import ArtifactRecord, is_advanceable_status
from artifact_store.sqlite_store import ArtifactStore
from domain.narrative_arc import NarrativeArc
from domain.scene_script import SceneScript
from domain.script_brief import ScriptBrief
from domain.script_draft import ScriptDraft
from domain.topic_request import TopicRequest
from domain.semantic_scene import SemanticScene
from domain.visual_event_sequence import VisualEventSequence
from domain.visual_plan import VisualPlan
from domain.validators.narrative_arc_validator import NarrativeArcValidator
from domain.validators.scene_script_validator import SceneScriptValidator
from domain.validators.semantic_scene_validator import SemanticSceneValidator
from domain.validators.script_brief_validator import ScriptBriefValidator
from domain.validators.script_draft_validator import ScriptDraftValidator
from domain.validators.timed_scene_plan_validator import TimedScenePlanValidator
from domain.validators.visual_event_sequence_validator import VisualEventSequenceValidator
from domain.validators.visual_plan_validator import VisualPlanValidator
from engines.narrative_arc_engine import NarrativeArcEngine
from engines.scene_script_engine import SceneScriptEngine
from engines.semantic_scene_engine import SemanticSceneEngine
from engines.script_brief_engine import ScriptBriefEngine
from engines.script_draft_engine import ScriptDraftEngine
from engines.timing_engine import TimingEngine
from engines.visual_event_sequence_engine import VisualEventSequenceEngine
from engines.visual_plan_engine import VisualPlanEngine
from registries.component_registry import ComponentRegistry
from registries.finance_domain_registry import FinanceDomainRegistry


class PipelineServiceError(Exception):
    """Raised when a pipeline stage cannot run."""


class PipelineService:
    def __init__(
        self,
        *,
        store: ArtifactStore,
        finance_registry: FinanceDomainRegistry,
        script_brief_engine: ScriptBriefEngine,
        script_brief_validator: ScriptBriefValidator,
        narrative_arc_engine: NarrativeArcEngine,
        narrative_arc_validator: NarrativeArcValidator,
        script_draft_engine: ScriptDraftEngine,
        script_draft_validator: ScriptDraftValidator,
        scene_script_engine: SceneScriptEngine,
        scene_script_validator: SceneScriptValidator,
        semantic_scene_engine: SemanticSceneEngine,
        semantic_scene_validator: SemanticSceneValidator,
        visual_event_sequence_engine: VisualEventSequenceEngine,
        visual_event_sequence_validator: VisualEventSequenceValidator,
        visual_plan_engine: VisualPlanEngine,
        visual_plan_validator: VisualPlanValidator,
        timing_engine: TimingEngine,
        timed_scene_plan_validator: TimedScenePlanValidator,
    ):
        self.store = store
        self.finance_registry = finance_registry
        self.script_brief_engine = script_brief_engine
        self.script_brief_validator = script_brief_validator
        self.narrative_arc_engine = narrative_arc_engine
        self.narrative_arc_validator = narrative_arc_validator
        self.script_draft_engine = script_draft_engine
        self.script_draft_validator = script_draft_validator
        self.scene_script_engine = scene_script_engine
        self.scene_script_validator = scene_script_validator
        self.semantic_scene_engine = semantic_scene_engine
        self.semantic_scene_validator = semantic_scene_validator
        self.visual_event_sequence_engine = visual_event_sequence_engine
        self.visual_event_sequence_validator = visual_event_sequence_validator
        self.visual_plan_engine = visual_plan_engine
        self.visual_plan_validator = visual_plan_validator
        self.timing_engine = timing_engine
        self.timed_scene_plan_validator = timed_scene_plan_validator

    def run_script_brief(self, project_id: str, run_id: str) -> ArtifactRecord:
        existing_artifact = self.store.find_artifact_by_type(project_id, run_id, "script_brief")
        if existing_artifact is not None:
            return existing_artifact

        topic_request_artifact = self.store.find_artifact_by_type(
            project_id,
            run_id,
            "topic_request",
        )
        if topic_request_artifact is None:
            raise PipelineServiceError("Cannot run script_brief without a topic_request artifact.")
        if not is_advanceable_status(topic_request_artifact.status):
            raise PipelineServiceError(
                "Cannot run script_brief because the topic_request artifact is not advanceable."
            )

        topic_request = TopicRequest.model_validate(topic_request_artifact.payload_json)
        script_brief = self.script_brief_engine.run(topic_request)
        validation = self.script_brief_validator.validate(
            script_brief,
            topic_request=topic_request,
        )

        return self.store.save_artifact(
            project_id=project_id,
            run_id=run_id,
            artifact_type="script_brief",
            schema_version=script_brief.schema_version,
            payload_json=script_brief.model_dump(),
            parent_artifact_roles_json={"topic_request": topic_request_artifact.id},
            validation_json=validation,
        )

    def run_narrative_arc(self, project_id: str, run_id: str) -> ArtifactRecord:
        existing_artifact = self.store.find_artifact_by_type(project_id, run_id, "narrative_arc")
        if existing_artifact is not None:
            return existing_artifact

        script_brief_artifact = self.store.find_artifact_by_type(
            project_id,
            run_id,
            "script_brief",
        )
        if script_brief_artifact is None:
            raise PipelineServiceError("Cannot run narrative_arc without a script_brief artifact.")
        if not is_advanceable_status(script_brief_artifact.status):
            raise PipelineServiceError(
                "Cannot run narrative_arc because the script_brief artifact is not advanceable."
            )

        script_brief = ScriptBrief.model_validate(script_brief_artifact.payload_json)
        narrative_arc = self.narrative_arc_engine.run(script_brief)
        validation = self.narrative_arc_validator.validate(
            narrative_arc,
            script_brief=script_brief,
        )

        return self.store.save_artifact(
            project_id=project_id,
            run_id=run_id,
            artifact_type="narrative_arc",
            schema_version=narrative_arc.schema_version,
            payload_json=narrative_arc.model_dump(),
            parent_artifact_roles_json={"script_brief": script_brief_artifact.id},
            validation_json=validation,
        )

    def run_script_draft(self, project_id: str, run_id: str) -> ArtifactRecord:
        existing_artifact = self.store.find_artifact_by_type(project_id, run_id, "script_draft")
        if existing_artifact is not None:
            return existing_artifact

        script_brief_artifact = self.store.find_artifact_by_type(
            project_id,
            run_id,
            "script_brief",
        )
        if script_brief_artifact is None:
            raise PipelineServiceError("Cannot run script_draft without a script_brief artifact.")
        if not is_advanceable_status(script_brief_artifact.status):
            raise PipelineServiceError(
                "Cannot run script_draft because the script_brief artifact is not advanceable."
            )

        narrative_arc_artifact = self.store.find_artifact_by_type(
            project_id,
            run_id,
            "narrative_arc",
        )
        if narrative_arc_artifact is None:
            raise PipelineServiceError("Cannot run script_draft without a narrative_arc artifact.")
        if not is_advanceable_status(narrative_arc_artifact.status):
            raise PipelineServiceError(
                "Cannot run script_draft because the narrative_arc artifact is not advanceable."
            )

        script_brief = ScriptBrief.model_validate(script_brief_artifact.payload_json)
        narrative_arc = NarrativeArc.model_validate(narrative_arc_artifact.payload_json)
        script_draft = self.script_draft_engine.run(
            script_brief=script_brief,
            narrative_arc=narrative_arc,
        )
        validation = self.script_draft_validator.validate(
            script_draft,
            script_brief=script_brief,
            narrative_arc=narrative_arc,
        )

        return self.store.save_artifact(
            project_id=project_id,
            run_id=run_id,
            artifact_type="script_draft",
            schema_version=script_draft.schema_version,
            payload_json=script_draft.model_dump(),
            parent_artifact_roles_json={
                "script_brief": script_brief_artifact.id,
                "narrative_arc": narrative_arc_artifact.id,
            },
            validation_json=validation,
        )

    def run_scene_script(self, project_id: str, run_id: str) -> ArtifactRecord:
        existing_artifact = self.store.find_artifact_by_type(project_id, run_id, "scene_script")
        if existing_artifact is not None:
            return existing_artifact

        script_brief_artifact = self.store.find_artifact_by_type(
            project_id,
            run_id,
            "script_brief",
        )
        if script_brief_artifact is None:
            raise PipelineServiceError("Cannot run scene_script without a script_brief artifact.")
        if not is_advanceable_status(script_brief_artifact.status):
            raise PipelineServiceError(
                "Cannot run scene_script because the script_brief artifact is not advanceable."
            )

        narrative_arc_artifact = self.store.find_artifact_by_type(
            project_id,
            run_id,
            "narrative_arc",
        )
        if narrative_arc_artifact is None:
            raise PipelineServiceError("Cannot run scene_script without a narrative_arc artifact.")
        if not is_advanceable_status(narrative_arc_artifact.status):
            raise PipelineServiceError(
                "Cannot run scene_script because the narrative_arc artifact is not advanceable."
            )

        script_draft_artifact = self.store.find_artifact_by_type(
            project_id,
            run_id,
            "script_draft",
        )
        if script_draft_artifact is None:
            raise PipelineServiceError("Cannot run scene_script without a script_draft artifact.")
        if not is_advanceable_status(script_draft_artifact.status):
            raise PipelineServiceError(
                "Cannot run scene_script because the script_draft artifact is not advanceable."
            )

        script_brief = ScriptBrief.model_validate(script_brief_artifact.payload_json)
        narrative_arc = NarrativeArc.model_validate(narrative_arc_artifact.payload_json)
        script_draft = ScriptDraft.model_validate(script_draft_artifact.payload_json)
        scene_script = self.scene_script_engine.run(
            script_brief=script_brief,
            narrative_arc=narrative_arc,
            script_draft=script_draft,
        )
        validation = self.scene_script_validator.validate(
            scene_script,
            script_brief=script_brief,
            narrative_arc=narrative_arc,
            script_draft=script_draft,
        )

        return self.store.save_artifact(
            project_id=project_id,
            run_id=run_id,
            artifact_type="scene_script",
            schema_version=scene_script.schema_version,
            payload_json=scene_script.model_dump(),
            parent_artifact_roles_json={
                "script_brief": script_brief_artifact.id,
                "narrative_arc": narrative_arc_artifact.id,
                "script_draft": script_draft_artifact.id,
            },
            validation_json=validation,
        )

    def run_semantic_scene(self, project_id: str, run_id: str) -> ArtifactRecord:
        existing_artifact = self.store.find_artifact_by_type(project_id, run_id, "semantic_scene")
        if existing_artifact is not None:
            return existing_artifact

        scene_script_artifact = self.store.find_artifact_by_type(
            project_id,
            run_id,
            "scene_script",
        )
        if scene_script_artifact is None:
            raise PipelineServiceError("Cannot run semantic_scene without a scene_script artifact.")
        if not is_advanceable_status(scene_script_artifact.status):
            raise PipelineServiceError(
                "Cannot run semantic_scene because the scene_script artifact is not advanceable."
            )

        scene_script = SceneScript.model_validate(scene_script_artifact.payload_json)
        semantic_scene = self.semantic_scene_engine.run(scene_script)
        validation = self.semantic_scene_validator.validate(
            semantic_scene,
            scene_script=scene_script,
        )

        return self.store.save_artifact(
            project_id=project_id,
            run_id=run_id,
            artifact_type="semantic_scene",
            schema_version=semantic_scene.schema_version,
            payload_json=semantic_scene.model_dump(),
            parent_artifact_roles_json={"scene_script": scene_script_artifact.id},
            validation_json=validation,
        )

    def run_visual_event_sequence(self, project_id: str, run_id: str) -> ArtifactRecord:
        existing_artifact = self.store.find_artifact_by_type(
            project_id,
            run_id,
            "visual_event_sequence",
        )
        if existing_artifact is not None:
            return existing_artifact

        semantic_scene_artifact = self.store.find_artifact_by_type(
            project_id,
            run_id,
            "semantic_scene",
        )
        if semantic_scene_artifact is None:
            raise PipelineServiceError(
                "Cannot run visual_event_sequence without a semantic_scene artifact."
            )
        if not is_advanceable_status(semantic_scene_artifact.status):
            raise PipelineServiceError(
                "Cannot run visual_event_sequence because the semantic_scene artifact is not advanceable."
            )

        semantic_scene = SemanticScene.model_validate(semantic_scene_artifact.payload_json)
        visual_event_sequence = self.visual_event_sequence_engine.run(semantic_scene)
        validation = self.visual_event_sequence_validator.validate(
            visual_event_sequence,
            semantic_scene=semantic_scene,
        )

        return self.store.save_artifact(
            project_id=project_id,
            run_id=run_id,
            artifact_type="visual_event_sequence",
            schema_version=visual_event_sequence.schema_version,
            payload_json=visual_event_sequence.model_dump(),
            parent_artifact_roles_json={"semantic_scene": semantic_scene_artifact.id},
            validation_json=validation,
        )

    def run_visual_plan(self, project_id: str, run_id: str) -> ArtifactRecord:
        existing_artifact = self.store.find_artifact_by_type(project_id, run_id, "visual_plan")
        if existing_artifact is not None:
            return existing_artifact

        semantic_scene_artifact = self.store.find_artifact_by_type(
            project_id,
            run_id,
            "semantic_scene",
        )
        if semantic_scene_artifact is None:
            raise PipelineServiceError("Cannot run visual_plan without a semantic_scene artifact.")
        if not is_advanceable_status(semantic_scene_artifact.status):
            raise PipelineServiceError(
                "Cannot run visual_plan because the semantic_scene artifact is not advanceable."
            )

        visual_event_sequence_artifact = self.store.find_artifact_by_type(
            project_id,
            run_id,
            "visual_event_sequence",
        )
        if visual_event_sequence_artifact is None:
            raise PipelineServiceError(
                "Cannot run visual_plan without a visual_event_sequence artifact."
            )
        if not is_advanceable_status(visual_event_sequence_artifact.status):
            raise PipelineServiceError(
                "Cannot run visual_plan because the visual_event_sequence artifact is not advanceable."
            )

        semantic_scene = SemanticScene.model_validate(semantic_scene_artifact.payload_json)
        visual_event_sequence = VisualEventSequence.model_validate(
            visual_event_sequence_artifact.payload_json
        )
        visual_plan = self.visual_plan_engine.run(
            semantic_scene=semantic_scene,
            visual_event_sequence=visual_event_sequence,
        )
        validation = self.visual_plan_validator.validate(
            visual_plan,
            semantic_scene=semantic_scene,
            visual_event_sequence=visual_event_sequence,
        )

        return self.store.save_artifact(
            project_id=project_id,
            run_id=run_id,
            artifact_type="visual_plan",
            schema_version=visual_plan.schema_version,
            payload_json=visual_plan.model_dump(),
            parent_artifact_roles_json={
                "semantic_scene": semantic_scene_artifact.id,
                "visual_event_sequence": visual_event_sequence_artifact.id,
            },
            validation_json=validation,
        )

    def run_timing(self, project_id: str, run_id: str) -> ArtifactRecord:
        existing_artifact = self.store.find_artifact_by_type(
            project_id,
            run_id,
            "timed_scene_plan",
        )
        if existing_artifact is not None:
            return existing_artifact

        visual_plan_artifact = self.store.find_artifact_by_type(
            project_id,
            run_id,
            "visual_plan",
        )
        if visual_plan_artifact is None:
            raise PipelineServiceError("Cannot run timing without a visual_plan artifact.")
        if not is_advanceable_status(visual_plan_artifact.status):
            raise PipelineServiceError(
                "Cannot run timing because the visual_plan artifact is not advanceable."
            )

        visual_event_sequence_artifact = self.store.find_artifact_by_type(
            project_id,
            run_id,
            "visual_event_sequence",
        )
        if visual_event_sequence_artifact is None:
            raise PipelineServiceError(
                "Cannot run timing without a visual_event_sequence artifact."
            )
        if not is_advanceable_status(visual_event_sequence_artifact.status):
            raise PipelineServiceError(
                "Cannot run timing because the visual_event_sequence artifact is not advanceable."
            )

        visual_plan = VisualPlan.model_validate(visual_plan_artifact.payload_json)
        visual_event_sequence = VisualEventSequence.model_validate(
            visual_event_sequence_artifact.payload_json
        )
        timed_scene_plan = self.timing_engine.run(
            visual_plan=visual_plan,
            visual_event_sequence=visual_event_sequence,
        )
        validation = self.timed_scene_plan_validator.validate(
            timed_scene_plan,
            visual_plan=visual_plan,
            visual_event_sequence=visual_event_sequence,
        )

        return self.store.save_artifact(
            project_id=project_id,
            run_id=run_id,
            artifact_type="timed_scene_plan",
            schema_version=timed_scene_plan.schema_version,
            payload_json=timed_scene_plan.model_dump(),
            parent_artifact_roles_json={
                "visual_plan": visual_plan_artifact.id,
                "visual_event_sequence": visual_event_sequence_artifact.id,
            },
            validation_json=validation,
        )


def build_pipeline_service(store: ArtifactStore) -> PipelineService:
    finance_registry = FinanceDomainRegistry()
    component_registry = ComponentRegistry()
    return PipelineService(
        store=store,
        finance_registry=finance_registry,
        script_brief_engine=ScriptBriefEngine(),
        script_brief_validator=ScriptBriefValidator(finance_registry),
        narrative_arc_engine=NarrativeArcEngine(),
        narrative_arc_validator=NarrativeArcValidator(),
        script_draft_engine=ScriptDraftEngine(),
        script_draft_validator=ScriptDraftValidator(),
        scene_script_engine=SceneScriptEngine(),
        scene_script_validator=SceneScriptValidator(),
        semantic_scene_engine=SemanticSceneEngine(finance_registry),
        semantic_scene_validator=SemanticSceneValidator(finance_registry),
        visual_event_sequence_engine=VisualEventSequenceEngine(),
        visual_event_sequence_validator=VisualEventSequenceValidator(),
        visual_plan_engine=VisualPlanEngine(component_registry),
        visual_plan_validator=VisualPlanValidator(component_registry),
        timing_engine=TimingEngine(),
        timed_scene_plan_validator=TimedScenePlanValidator(),
    )
