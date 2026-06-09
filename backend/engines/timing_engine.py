from domain.timed_scene_plan import TimedScenePlan, TimedSpan
from domain.visual_event_sequence import VisualEventSequence
from domain.visual_plan import VisualPlan


class TimingEngine:
    def run(
        self,
        *,
        visual_plan: VisualPlan,
        visual_event_sequence: VisualEventSequence,
    ) -> TimedScenePlan:
        duration_seconds = 8.0
        fps = 30
        event_count = len(visual_event_sequence.events)
        if event_count == 0:
            return TimedScenePlan(
                scene_id=visual_plan.scene_id,
                duration_seconds=duration_seconds,
                fps=fps,
                spans=[],
            )

        span_length = duration_seconds / event_count
        spans = []
        for index, event in enumerate(visual_event_sequence.events):
            start_seconds = round(index * span_length, 3)
            end_seconds = (
                duration_seconds
                if index == event_count - 1
                else round((index + 1) * span_length, 3)
            )
            spans.append(
                TimedSpan(
                    event_id=event.event_id,
                    start_seconds=start_seconds,
                    end_seconds=end_seconds,
                    duration_seconds=round(end_seconds - start_seconds, 3),
                )
            )

        return TimedScenePlan(
            scene_id=visual_plan.scene_id,
            duration_seconds=duration_seconds,
            fps=fps,
            spans=spans,
        )
