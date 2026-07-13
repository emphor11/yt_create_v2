from dataclasses import asdict
from typing import Any

from artifact_store.models import ArtifactRecord
from artifact_store.sqlite_store import ArtifactStore
from app.stage_logger import StageLogger
from domain.research_packet import ResearchPacket
from domain.narrative_plan import NarrativePlan
from domain.hook import Hook
from domain.script_visual_strategy import ScriptVisualStrategy
from domain.scene_script import SceneScript, SceneStoryState
from domain.semantic_scene import SemanticScene, SemanticEntity
from domain.visual_event_sequence import VisualEvent, VisualEventSequence
from domain.visual_plan import VisualPlan, SplitComparisonProps, VisualPlanSide
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

            # 4. If valid, compile and save legacy artifacts for production stages backward compatibility
            if validation.status == "valid" and strategy.ideas:
                self._compile_legacy_artifacts(
                    project_id=project_id,
                    run_id=run_id,
                    research_packet=research_packet,
                    strategy=strategy,
                    strategy_art_id=strategy_artifact.id,
                )

        except Exception as exc:
            self.stage_logger.log_error(project_id, run_id, "script_visual_strategy", error=exc, start_time=start)
            raise

        self.stage_logger.log_finish(project_id, run_id, "script_visual_strategy", start_time=start)
        return strategy_artifact

    def _compile_legacy_artifacts(
        self,
        *,
        project_id: str,
        run_id: str,
        research_packet: ResearchPacket,
        strategy: ScriptVisualStrategy,
        strategy_art_id: str,
    ) -> None:
        first_idea = strategy.ideas[0]

        # Extract SplitComparison values
        comp_data = {}
        for beat in first_idea.visual_sequence:
            if beat.preferred_component == "SplitComparison" and beat.component_data:
                comp_data = beat.component_data
                break

        left_role = comp_data.get("left_role", "product_price")
        left_label = comp_data.get("left_label", "Left Option")
        left_value = comp_data.get("left_value", 100)
        left_unit = comp_data.get("left_unit", "units")

        right_role = comp_data.get("right_role", "monthly_payment")
        right_label = comp_data.get("right_label", "Right Option")
        right_value = comp_data.get("right_value", 200)
        right_unit = comp_data.get("right_unit", "units")

        # A. Compile scene_script
        scene_script = SceneScript(
            scene_id="scene_01",
            topic=research_packet.topic,
            angle="AI strategy",
            thesis=strategy.thesis,
            mechanism="SplitComparison",
            scene_function_label=first_idea.title,
            arc_phases=["body"],
            narrative_purpose=first_idea.core_teaching_point,
            narration=first_idea.narration,
            story_state=SceneStoryState(recurring_example="standard"),
        )
        self.store.save_artifact(
            project_id=project_id,
            run_id=run_id,
            artifact_type="scene_script",
            schema_version=scene_script.schema_version,
            payload_json=scene_script.model_dump(),
            parent_artifact_roles_json={"script_visual_strategy": strategy_art_id},
            validation_json=ValidationResult(status="valid"),
        )

        # B. Compile semantic_scene
        semantic_scene = SemanticScene(
            scene_id="scene_01",
            primary_concept=first_idea.focus_concept,
            confidence=1.0,
            entities=[
                SemanticEntity(
                    id="left_entity_01",
                    role=left_role,
                    raw=f"{left_value} {left_unit}",
                    value=left_value,
                    unit=left_unit,
                    source_text="left comparison cost",
                ),
                SemanticEntity(
                    id="right_entity_01",
                    role=right_role,
                    raw=f"{right_value} {right_unit}",
                    value=right_value,
                    unit=right_unit,
                    source_text="right comparison cost",
                ),
            ],
            relationships=[],
        )
        self.store.save_artifact(
            project_id=project_id,
            run_id=run_id,
            artifact_type="semantic_scene",
            schema_version=semantic_scene.schema_version,
            payload_json=semantic_scene.model_dump(),
            parent_artifact_roles_json={"script_visual_strategy": strategy_art_id},
            validation_json=ValidationResult(status="valid"),
        )

        # C. Compile visual_event_sequence
        events = []
        for idx, beat in enumerate(first_idea.visual_sequence):
            events.append(
                VisualEvent(
                    event_id=f"evt_text_{beat.beat_id}",
                    primitive="reveal_full_price" if idx == 0 else "reveal_monthly_payment",
                    intent=beat.visual_goal,
                    world_object=beat.preferred_component,
                    semantic_entity_id="left_entity_01" if idx == 0 else "right_entity_01",
                )
            )
        events.append(
            VisualEvent(
                event_id="evt_shift_01",
                primitive="attention_shift",
                intent="focus comparison",
                world_object="SplitComparison",
                semantic_entity_id=None,
            )
        )

        visual_event_sequence = VisualEventSequence(
            scene_id="scene_01",
            primary_concept=first_idea.focus_concept,
            events=events,
        )
        self.store.save_artifact(
            project_id=project_id,
            run_id=run_id,
            artifact_type="visual_event_sequence",
            schema_version=visual_event_sequence.schema_version,
            payload_json=visual_event_sequence.model_dump(),
            parent_artifact_roles_json={"script_visual_strategy": strategy_art_id},
            validation_json=ValidationResult(status="valid"),
        )

        # D. Compile visual_plan
        visual_plan = VisualPlan(
            scene_id="scene_01",
            primary_concept=first_idea.focus_concept,
            component="SplitComparison",
            selection_reason="Split comparison data strategy",
            props=SplitComparisonProps(
                left=VisualPlanSide(
                    role=left_role,
                    semantic_entity_id="left_entity_01",
                    label=left_label,
                    raw=f"{left_value} {left_unit}",
                    value=left_value,
                    unit=left_unit,
                ),
                right=VisualPlanSide(
                    role=right_role,
                    semantic_entity_id="right_entity_01",
                    label=right_label,
                    raw=f"{right_value} {right_unit}",
                    value=right_value,
                    unit=right_unit,
                ),
                attention_shift_event_id="evt_shift_01",
            ),
        )
        self.store.save_artifact(
            project_id=project_id,
            run_id=run_id,
            artifact_type="visual_plan",
            schema_version=visual_plan.schema_version,
            payload_json=visual_plan.model_dump(),
            parent_artifact_roles_json={"script_visual_strategy": strategy_art_id},
            validation_json=ValidationResult(status="valid"),
        )

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
