from domain.timed_scene_plan import TimedScenePlan
from domain.validation import ValidationResult
from domain.visual_event_sequence import VisualEventSequence
from domain.visual_plan import VisualPlan


FORBIDDEN_DOWNSTREAM_KEYS = {
    "composition",
    "render_spec",
    "frames",
    "output_path",
    "storage_key",
}


class TimedScenePlanValidator:
    def validate(
        self,
        timed_scene_plan: TimedScenePlan,
        *,
        visual_plan: VisualPlan,
        visual_event_sequence: VisualEventSequence,
    ) -> ValidationResult:
        errors: list[str] = []

        if timed_scene_plan.scene_id != visual_plan.scene_id:
            errors.append("TimedScenePlan scene_id must match VisualPlan scene_id.")
        if timed_scene_plan.scene_id != visual_event_sequence.scene_id:
            errors.append("TimedScenePlan scene_id must match VisualEventSequence scene_id.")
        if timed_scene_plan.duration_seconds != 8.0:
            errors.append("TimedScenePlan duration_seconds must be 8.0 for the MVP.")
        if timed_scene_plan.fps != 30:
            errors.append("TimedScenePlan fps must be 30 for the MVP.")

        event_ids = [event.event_id for event in visual_event_sequence.events]
        span_event_ids = [span.event_id for span in timed_scene_plan.spans]
        if span_event_ids != event_ids:
            errors.append(
                "TimedScenePlan spans must match VisualEventSequence event order exactly."
            )
        if len(set(span_event_ids)) != len(span_event_ids):
            errors.append("TimedScenePlan spans must not contain duplicate event ids.")

        self._validate_span_coverage(timed_scene_plan, errors)

        leaked_keys = FORBIDDEN_DOWNSTREAM_KEYS.intersection(timed_scene_plan.model_dump().keys())
        if leaked_keys:
            errors.append(
                "TimedScenePlan must not contain downstream fields: "
                + ", ".join(sorted(leaked_keys))
                + "."
            )

        if errors:
            return ValidationResult(status="blocked", errors=errors)

        return ValidationResult(status="valid")

    @staticmethod
    def _validate_span_coverage(
        timed_scene_plan: TimedScenePlan,
        errors: list[str],
    ) -> None:
        if not timed_scene_plan.spans:
            errors.append("TimedScenePlan requires at least one timed span.")
            return

        previous_end: float | None = None
        for index, span in enumerate(timed_scene_plan.spans):
            if not span.event_id.strip():
                errors.append("Timed span event_id is required.")
            if span.start_seconds < 0:
                errors.append(f"Timed span {span.event_id} start_seconds cannot be negative.")
            if span.end_seconds <= span.start_seconds:
                errors.append(f"Timed span {span.event_id} must end after it starts.")
            expected_duration = round(span.end_seconds - span.start_seconds, 3)
            if span.duration_seconds != expected_duration:
                errors.append(
                    f"Timed span {span.event_id} duration_seconds must match end minus start."
                )
            if index == 0 and span.start_seconds != 0.0:
                errors.append("TimedScenePlan first span must start at 0.0 seconds.")
            if previous_end is not None and span.start_seconds != previous_end:
                errors.append("TimedScenePlan spans must be contiguous and non-overlapping.")
            previous_end = span.end_seconds

        last_end = timed_scene_plan.spans[-1].end_seconds
        if last_end != timed_scene_plan.duration_seconds:
            errors.append("TimedScenePlan spans must cover the full scene duration.")
