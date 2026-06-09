from domain.render_spec import RenderSpec
from domain.timed_scene_plan import TimedScenePlan
from domain.validation import ValidationResult
from domain.visual_plan import VisualPlan


FORBIDDEN_DOWNSTREAM_KEYS = {
    "output_path",
    "storage_key",
    "video_path",
    "render_status",
}


class RenderSpecValidator:
    def validate(
        self,
        render_spec: RenderSpec,
        *,
        visual_plan: VisualPlan,
        timed_scene_plan: TimedScenePlan,
    ) -> ValidationResult:
        errors: list[str] = []

        if render_spec.scene_id != visual_plan.scene_id:
            errors.append("RenderSpec scene_id must match VisualPlan scene_id.")
        if render_spec.scene_id != timed_scene_plan.scene_id:
            errors.append("RenderSpec scene_id must match TimedScenePlan scene_id.")
        if render_spec.composition != visual_plan.component:
            errors.append("RenderSpec composition must be copied from VisualPlan component.")
        if render_spec.props != visual_plan.props:
            errors.append("RenderSpec props must exactly match VisualPlan props.")
        if render_spec.fps != timed_scene_plan.fps:
            errors.append("RenderSpec fps must match TimedScenePlan fps.")

        expected_duration_frames = self._seconds_to_frames(
            timed_scene_plan.duration_seconds,
            timed_scene_plan.fps,
        )
        if render_spec.duration_frames != expected_duration_frames:
            errors.append("RenderSpec duration_frames must match timed duration and fps.")

        timed_event_ids = [span.event_id for span in timed_scene_plan.spans]
        render_event_ids = [span.event_id for span in render_spec.frame_spans]
        if render_event_ids != timed_event_ids:
            errors.append("RenderSpec frame spans must match TimedScenePlan span order exactly.")

        self._validate_frame_spans(
            render_spec=render_spec,
            timed_scene_plan=timed_scene_plan,
            errors=errors,
        )

        leaked_keys = FORBIDDEN_DOWNSTREAM_KEYS.intersection(render_spec.model_dump().keys())
        if leaked_keys:
            errors.append(
                "RenderSpec must not contain downstream fields: "
                + ", ".join(sorted(leaked_keys))
                + "."
            )

        if errors:
            return ValidationResult(status="blocked", errors=errors)

        return ValidationResult(status="valid")

    def _validate_frame_spans(
        self,
        *,
        render_spec: RenderSpec,
        timed_scene_plan: TimedScenePlan,
        errors: list[str],
    ) -> None:
        if not render_spec.frame_spans:
            errors.append("RenderSpec requires at least one frame span.")
            return

        previous_end: int | None = None
        timed_span_by_event_id = {
            span.event_id: span
            for span in timed_scene_plan.spans
        }
        for index, frame_span in enumerate(render_spec.frame_spans):
            if not frame_span.event_id.strip():
                errors.append("Render frame span event_id is required.")
            if frame_span.start_frame < 0:
                errors.append(
                    f"Render frame span {frame_span.event_id} start_frame cannot be negative."
                )
            if frame_span.end_frame <= frame_span.start_frame:
                errors.append(
                    f"Render frame span {frame_span.event_id} must end after it starts."
                )
            if frame_span.duration_frames != frame_span.end_frame - frame_span.start_frame:
                errors.append(
                    f"Render frame span {frame_span.event_id} duration_frames must match end minus start."
                )
            if index == 0 and frame_span.start_frame != 0:
                errors.append("RenderSpec first frame span must start at frame 0.")
            if previous_end is not None and frame_span.start_frame != previous_end:
                errors.append("RenderSpec frame spans must be contiguous and non-overlapping.")
            previous_end = frame_span.end_frame

            timed_span = timed_span_by_event_id.get(frame_span.event_id)
            if timed_span is None:
                continue
            expected_start_frame = self._seconds_to_frames(
                timed_span.start_seconds,
                timed_scene_plan.fps,
            )
            expected_end_frame = self._seconds_to_frames(
                timed_span.end_seconds,
                timed_scene_plan.fps,
            )
            if frame_span.start_frame != expected_start_frame:
                errors.append(
                    f"Render frame span {frame_span.event_id} start_frame must match TimedScenePlan."
                )
            if frame_span.end_frame != expected_end_frame:
                errors.append(
                    f"Render frame span {frame_span.event_id} end_frame must match TimedScenePlan."
                )

        last_end = render_spec.frame_spans[-1].end_frame
        if last_end != render_spec.duration_frames:
            errors.append("RenderSpec frame spans must cover the full render duration.")

    @staticmethod
    def _seconds_to_frames(seconds: float, fps: int) -> int:
        return round(seconds * fps)
