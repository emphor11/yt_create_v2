from artifact_store.models import ArtifactRecord, is_advanceable_status
from artifact_store.sqlite_store import ArtifactStore
from domain.script_brief import ScriptBrief
from domain.topic_request import TopicRequest
from domain.validators.narrative_arc_validator import NarrativeArcValidator
from domain.validators.script_brief_validator import ScriptBriefValidator
from engines.narrative_arc_engine import NarrativeArcEngine
from engines.script_brief_engine import ScriptBriefEngine
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
    ):
        self.store = store
        self.finance_registry = finance_registry
        self.script_brief_engine = script_brief_engine
        self.script_brief_validator = script_brief_validator
        self.narrative_arc_engine = narrative_arc_engine
        self.narrative_arc_validator = narrative_arc_validator

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


def build_pipeline_service(store: ArtifactStore) -> PipelineService:
    finance_registry = FinanceDomainRegistry()
    return PipelineService(
        store=store,
        finance_registry=finance_registry,
        script_brief_engine=ScriptBriefEngine(),
        script_brief_validator=ScriptBriefValidator(finance_registry),
        narrative_arc_engine=NarrativeArcEngine(),
        narrative_arc_validator=NarrativeArcValidator(),
    )
