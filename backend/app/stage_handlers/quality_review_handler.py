import re
from typing import Any

from artifact_store.models import ArtifactRecord
from artifact_store.sqlite_store import ArtifactStore
from app.stage_logger import StageLogger
from domain.research_packet import ResearchPacket
from domain.script_visual_strategy import ScriptVisualStrategy
from domain.review_result import ReviewResult, ValidationCheck
from domain.validators.review_result_validator import ReviewResultValidator


class QualityReviewHandler:
    def __init__(
        self,
        *,
        store: ArtifactStore,
        review_validator: ReviewResultValidator,
        stage_logger: StageLogger,
    ) -> None:
        self.store = store
        self.review_validator = review_validator
        self.stage_logger = stage_logger

    def run(self, project_id: str, run_id: str) -> ArtifactRecord:
        existing = self.store.find_artifact_by_type(project_id, run_id, "review_result")
        if existing is not None:
            return existing

        start = self.stage_logger.log_start(project_id, run_id, "quality_review")
        try:
            # 1. Fetch prerequisite artifacts
            strategy_artifact = self.store.require_artifact(
                project_id, run_id, "script_visual_strategy", for_stage="quality_review"
            )
            strategy = ScriptVisualStrategy.model_validate(strategy_artifact.payload_json)

            research_artifact = self.store.require_artifact(
                project_id, run_id, "research_packet", for_stage="quality_review"
            )
            research_packet = ResearchPacket.model_validate(research_artifact.payload_json)

            # 2. Run the deterministic validation gate checks
            checks = []
            approved = True

            # Check A: Concept Alignment Check
            concept_check_passed = True
            concept_msg = "All script concepts are present in research."
            verified_concepts = {c.lower().strip() for c in research_packet.concepts}
            for idea in strategy.ideas:
                concept = idea.focus_concept.lower().strip()
                # Verify that the concept is in verified_concepts (or contained in any concept string)
                matched = False
                for vc in verified_concepts:
                    if concept in vc or vc in concept:
                        matched = True
                        break
                if not matched:
                    concept_check_passed = False
                    concept_msg = f"Script concept '{idea.focus_concept}' is not present in the verified research concepts."
                    approved = False
                    break
            checks.append(
                ValidationCheck(
                    name="Concept Alignment",
                    status="passed" if concept_check_passed else "failed",
                    message=concept_msg,
                )
            )

            # Check B: Statistic Verification Check
            stat_check_passed = True
            stat_msg = "All numeric statistics in script are verified in research."
            
            # Combine verified facts and statistics to search against
            research_sources = research_packet.verified_facts + research_packet.statistics
            research_sources_joined = " ".join(research_sources).lower()

            for idea in strategy.ideas:
                # 1. Check numbers in narration text
                narration_numbers = re.findall(r"\d+", idea.narration)
                for num in narration_numbers:
                    if len(num) > 1:  # Skip single digits like 0-9 as they are common filler words
                        # Check if the number appears anywhere in the research facts/statistics
                        if num not in research_sources_joined:
                            # Also check if it's written in words or similar, but strict match is safer for stats
                            stat_check_passed = False
                            stat_msg = f"Statistic '{num}' mentioned in narration is not verified in research facts."
                            approved = False
                            break
                if not stat_check_passed:
                    break

                # 2. Check numbers inside SplitComparison component_data
                for beat in idea.visual_sequence:
                    if beat.preferred_component == "SplitComparison" and beat.component_data:
                        data = beat.component_data
                        for val_key in ["left_value", "right_value"]:
                            val = data.get(val_key)
                            if val is not None and isinstance(val, (int, float)):
                                # Skip checking if it's 0 or 1
                                if val > 9:
                                    val_str = str(int(val))
                                    if val_str not in research_sources_joined:
                                        stat_check_passed = False
                                        stat_msg = f"Value '{val_str}' used in SplitComparison '{val_key}' is not verified in research facts."
                                        approved = False
                                        break
                    if not stat_check_passed:
                        break

            checks.append(
                ValidationCheck(
                    name="Statistic Verification",
                    status="passed" if stat_check_passed else "failed",
                    message=stat_msg,
                )
            )

            # Check C: Visual Component Configuration Check
            visual_check_passed = True
            visual_msg = "All visual component configurations are valid."
            # Confirm SplitComparison component has valid properties if selected
            for idea in strategy.ideas:
                for beat in idea.visual_sequence:
                    if beat.preferred_component == "SplitComparison":
                        data = beat.component_data
                        if not data or not data.get("left_label") or not data.get("right_label"):
                            visual_check_passed = False
                            visual_msg = f"Visual beat '{beat.beat_id}' is SplitComparison but lacks left/right labels."
                            approved = False
                            break
                        left_val = data.get("left_value")
                        right_val = data.get("right_value")
                        if left_val is None or right_val is None or left_val <= 0 or right_val <= 0:
                            visual_check_passed = False
                            visual_msg = f"Visual beat '{beat.beat_id}' has invalid numeric split comparison values."
                            approved = False
                            break
                if not visual_check_passed:
                    break

            checks.append(
                ValidationCheck(
                    name="Visual Configuration",
                    status="passed" if visual_check_passed else "failed",
                    message=visual_msg,
                )
            )

            # 3. Instantiate and validate the ReviewResult
            review_result = ReviewResult(
                approved=approved,
                checks=checks,
                feedback="All checks passed successfully." if approved else "Quality review rejected script strategy.",
            )
            validation = self.review_validator.validate(review_result)

            # 4. Save the artifact record
            artifact = self.store.save_artifact(
                project_id=project_id,
                run_id=run_id,
                artifact_type="review_result",
                schema_version=review_result.schema_version,
                payload_json=review_result.model_dump(),
                parent_artifact_roles_json={"script_visual_strategy": strategy_artifact.id},
                validation_json=validation,
            )

        except Exception as exc:
            self.stage_logger.log_error(project_id, run_id, "quality_review", error=exc, start_time=start)
            raise

        self.stage_logger.log_finish(project_id, run_id, "quality_review", start_time=start)
        return artifact
