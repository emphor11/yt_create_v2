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

from domain.composition_plan import FullCompositionPlan, HookCompositionPlan, IdeaCompositionPlan
from domain.visual_intent_artifact import (
    VisualIntentArtifact,
    build_visual_intent_provenance,
)
from engines.visual_intent_engine import VisualIntentEngine
from engines.composition_planner_engine import CompositionPlannerEngine


class ScriptVisualStrategyHandler:
    def __init__(
        self,
        *,
        store: ArtifactStore,
        strategy_engine: ScriptVisualStrategyEngine,
        strategy_validator: ScriptVisualStrategyValidator,
        stage_logger: StageLogger,
        visual_intent_engine: VisualIntentEngine | None = None,
        composition_planner_engine: CompositionPlannerEngine | None = None,
    ) -> None:
        self.store = store
        self.strategy_engine = strategy_engine
        self.strategy_validator = strategy_validator
        self.stage_logger = stage_logger
        self.visual_intent_engine = visual_intent_engine
        self.composition_planner_engine = composition_planner_engine

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

            req_artifact = (
                self.store.find_artifact_by_type(project_id, run_id, "generate_video_request")
                or self.store.find_artifact_by_type(project_id, run_id, "topic_request")
            )
            duration_profile = "short_2min"
            visual_mode = "legacy"
            if req_artifact and isinstance(req_artifact.payload_json, dict):
                duration_profile = req_artifact.payload_json.get("duration_profile", "short_2min")
                visual_mode = req_artifact.payload_json.get("visual_mode", "legacy")

            # 2. Run the Engine
            try:
                result = self.strategy_engine.run(
                    research_packet,
                    narrative_plan,
                    hook,
                    duration_profile=duration_profile,
                )
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

            # Stamp visual_mode so VideoAssemblyHandler can detect which assembly path to use.
            payload_json["visual_mode"] = visual_mode

            # In composition mode, persist the validated intent sequence before
            # composition planning. The artifact ID is then copied into every
            # CompositionBeat so the plan can be traced back to exact source data.
            if visual_mode == "composition":
                if not self.visual_intent_engine or not self.composition_planner_engine:
                    raise RuntimeError(
                        "Composition mode requires VisualIntent and CompositionPlanner engines."
                    )

                existing_intent_artifact = self.store.find_artifact_by_type(
                    project_id, run_id, "visual_intent"
                )
                if existing_intent_artifact is not None:
                    intent_artifact = VisualIntentArtifact.model_validate(
                        existing_intent_artifact.payload_json
                    )
                    visual_intent_artifact_id = existing_intent_artifact.id
                else:
                    sequences = []
                    provenance = []
                    provider_metadata = []

                    if hook and hook.script_text and hook.script_text.strip():
                        hook_intent_res = self.visual_intent_engine.run(
                            idea_id="hook",
                            narration=hook.script_text,
                            topic=research_packet.topic,
                            audience=research_packet.audience,
                            is_hook=True,
                        )
                        sequences.append(hook_intent_res.sequence)
                        provenance.extend(
                            build_visual_intent_provenance(
                                hook_intent_res.sequence,
                                source_kind="hook",
                            )
                        )
                        provider_metadata.append(asdict(hook_intent_res.provider_metadata))

                    for idea in strategy.ideas:
                        intent_res = self.visual_intent_engine.run(
                            idea_id=idea.idea_id,
                            narration=idea.narration,
                            topic=research_packet.topic,
                            audience=research_packet.audience,
                        )
                        sequences.append(intent_res.sequence)
                        provenance.extend(
                            build_visual_intent_provenance(
                                intent_res.sequence,
                                source_kind="idea",
                            )
                        )
                        provider_metadata.append(asdict(intent_res.provider_metadata))

                    intent_artifact = VisualIntentArtifact(
                        sequences=sequences,
                        provenance=provenance,
                        provider_metadata=provider_metadata,
                    )
                    saved_intent_artifact = self.store.save_artifact(
                        project_id=project_id,
                        run_id=run_id,
                        artifact_type="visual_intent",
                        schema_version=intent_artifact.schema_version,
                        payload_json=intent_artifact.model_dump(),
                        parent_artifact_roles_json={
                            "hook": hook_artifact.id,
                            "narrative_plan": narrative_artifact.id,
                            "research_packet": res_artifact.id,
                        },
                        validation_json=ValidationResult(status="valid"),
                    )
                    visual_intent_artifact_id = saved_intent_artifact.id

                sequence_by_idea_id = {
                    sequence.idea_id: sequence for sequence in intent_artifact.sequences
                }

                # Plan Hook Composition Beats from the persisted source sequence.
                hook_plan = None
                if hook and hook.script_text and hook.script_text.strip():
                    hook_sequence = sequence_by_idea_id.get("hook")
                    if hook_sequence is None:
                        raise ValueError("Persisted visual_intent artifact is missing the hook sequence.")
                    hook_beats = []
                    for b_idx, intent in enumerate(hook_sequence.intents):
                        beat_id = f"beat_hook_{b_idx + 1:02d}"
                        plan_res = self.composition_planner_engine.run(
                            intent=intent,
                            beat_id=beat_id,
                            topic=research_packet.topic,
                            audience=research_packet.audience,
                            source_idea_id=hook_sequence.idea_id,
                            source_visual_intent_artifact_id=visual_intent_artifact_id,
                        )
                        hook_beats.append(plan_res.beat)
                    hook_plan = HookCompositionPlan(
                        hook_id="hook",
                        narration=hook_sequence.narration,
                        beats=hook_beats,
                    )

                # Plan body ideas from the persisted source sequences.
                comp_ideas = []
                for idea_idx, idea in enumerate(strategy.ideas):
                    sequence = sequence_by_idea_id.get(idea.idea_id)
                    if sequence is None:
                        raise ValueError(
                            f"Persisted visual_intent artifact is missing sequence for idea '{idea.idea_id}'."
                        )
                    beats = []
                    for b_idx, intent in enumerate(sequence.intents):
                        beat_id = f"beat_{idea_idx + 1:02d}_{b_idx + 1:02d}"
                        plan_res = self.composition_planner_engine.run(
                            intent=intent,
                            beat_id=beat_id,
                            topic=research_packet.topic,
                            audience=research_packet.audience,
                            source_idea_id=sequence.idea_id,
                            source_visual_intent_artifact_id=visual_intent_artifact_id,
                        )
                        beats.append(plan_res.beat)
                    comp_ideas.append(
                        IdeaCompositionPlan(
                            idea_id=idea.idea_id,
                            narration=sequence.narration,
                            beats=beats,
                        )
                    )
                full_comp_plan = FullCompositionPlan(
                    thesis=strategy.thesis,
                    visual_mode="composition",
                    hook_plan=hook_plan,
                    ideas=comp_ideas,
                )
                payload_json["composition_plan"] = full_comp_plan.model_dump()
            else:
                visual_intent_artifact_id = None

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
                    **(
                        {"visual_intent": visual_intent_artifact_id}
                        if visual_intent_artifact_id is not None
                        else {}
                    ),
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
