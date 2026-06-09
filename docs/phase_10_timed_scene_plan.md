# Phase 10 — TimedScenePlan

Phase 10 assigns timing to the visual events.

## What TimedScenePlan Means

`TimedScenePlan` says when each visual event starts and ends.

It does not decide what the scene means.

It does not choose the component.

It does not create render specs.

It does not render video.

## Input and Output

Input:

```text
VisualPlan + VisualEventSequence
```

Output:

```text
TimedScenePlan
```

Example output:

```json
{
  "scene_id": "scene_01",
  "duration_seconds": 8.0,
  "fps": 30,
  "spans": [
    {
      "event_id": "event_full_price",
      "start_seconds": 0.0,
      "end_seconds": 2.667,
      "duration_seconds": 2.667
    },
    {
      "event_id": "event_monthly_payment",
      "start_seconds": 2.667,
      "end_seconds": 5.333,
      "duration_seconds": 2.666
    },
    {
      "event_id": "event_attention_shift",
      "start_seconds": 5.333,
      "end_seconds": 8.0,
      "duration_seconds": 2.667
    }
  ]
}
```

## Engine Boundary

`TimingEngine` is pure.

It accepts:

```text
VisualPlan
VisualEventSequence
```

It returns:

```text
TimedScenePlan
```

It does not:

- read the database
- write artifacts
- call FastAPI
- choose a component
- change component props
- convert seconds to frames
- render video

## Timing Rule

The MVP scene is fixed at:

```text
8 seconds
30 FPS
```

The engine divides the 8 seconds across the visual events in their existing order.

For the MVP three-event sequence:

```text
full price reveal -> monthly payment reveal -> attention shift
```

the output is three contiguous spans.

## PipelineService Boundary

`PipelineService` handles orchestration:

```text
find visual_plan artifact
check it can advance
find visual_event_sequence artifact
check it can advance
deserialize parents
call TimingEngine
validate TimedScenePlan
store timed_scene_plan artifact
return stored artifact
```

Only stages through `timing` are implemented by Phase 10.

## Validation

`TimedScenePlanValidator` checks:

- scene id matches `VisualPlan`
- scene id matches `VisualEventSequence`
- duration is exactly 8 seconds
- FPS is exactly 30
- every visual event has one timed span
- timed spans match visual event order exactly
- no duplicate event ids exist
- first span starts at 0 seconds
- final span ends at 8 seconds
- spans are contiguous and non-overlapping
- span duration equals end time minus start time
- downstream render fields are not accepted

## Explicitly Deferred

- RenderSpec
- frame conversion
- Remotion render instructions
- Video artifact
- output storage keys
- AI
