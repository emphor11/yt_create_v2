from domain.render_spec import RenderSpec
from domain.validation import ValidationResult


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
    ) -> ValidationResult:
        errors: list[str] = []

        # AI Flow: Validate RenderSpec independently
        if not render_spec.scene_id.strip():
            errors.append("RenderSpec scene_id is required.")
        if not render_spec.composition.strip():
            errors.append("RenderSpec composition is required.")
        if render_spec.fps <= 0:
            errors.append("RenderSpec fps must be positive.")
        if render_spec.duration_frames <= 0:
            errors.append("RenderSpec duration_frames must be positive.")

        self._validate_frame_spans_independent(
            render_spec=render_spec,
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

    def _validate_frame_spans_independent(
        self,
        *,
        render_spec: RenderSpec,
        errors: list[str],
    ) -> None:
        if not render_spec.frame_spans:
            errors.append("RenderSpec requires at least one frame span.")
            return

        previous_end: int | None = None
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

        last_end = render_spec.frame_spans[-1].end_frame
        if last_end != render_spec.duration_frames:
            errors.append("RenderSpec frame spans must cover the full render duration.")
