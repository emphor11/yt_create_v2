from domain.render_spec import RenderFrameSpan, RenderSpec
from domain.timed_scene_plan import TimedScenePlan
from domain.visual_plan import VisualPlan


class RenderSpecEngine:
    def run(
        self,
        *,
        visual_plan: VisualPlan,
        timed_scene_plan: TimedScenePlan,
    ) -> RenderSpec:
        fps = timed_scene_plan.fps
        frame_spans = [
            RenderFrameSpan(
                event_id=span.event_id,
                start_frame=self._seconds_to_frames(span.start_seconds, fps),
                end_frame=self._seconds_to_frames(span.end_seconds, fps),
                duration_frames=self._seconds_to_frames(span.duration_seconds, fps),
            )
            for span in timed_scene_plan.spans
        ]

        return RenderSpec(
            scene_id=visual_plan.scene_id,
            composition=visual_plan.component,
            fps=fps,
            duration_frames=self._seconds_to_frames(
                timed_scene_plan.duration_seconds,
                fps,
            ),
            props=visual_plan.props.model_copy(deep=True),
            frame_spans=frame_spans,
        )

    @staticmethod
    def _seconds_to_frames(seconds: float, fps: int) -> int:
        return round(seconds * fps)
