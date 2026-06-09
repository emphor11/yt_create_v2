# Phase 11 — RenderSpec

Phase 11 creates exact renderer instructions.

## What RenderSpec Means

`RenderSpec` tells the renderer what to render.

It includes:

- composition name
- component props
- FPS
- total frame count
- frame spans for visual events

It does not render video.

It does not store output files.

It does not choose the component.

## Input and Output

Input:

```text
VisualPlan + TimedScenePlan
```

Output:

```text
RenderSpec
```

Example output:

```json
{
  "scene_id": "scene_01",
  "composition": "SplitComparison",
  "fps": 30,
  "duration_frames": 240,
  "props": {
    "left": {
      "role": "product_price",
      "semantic_entity_id": "entity_price",
      "label": "Full price",
      "raw": "₹80,000",
      "value": 80000,
      "unit": "INR"
    },
    "right": {
      "role": "monthly_payment",
      "semantic_entity_id": "entity_emi",
      "label": "Monthly payment",
      "raw": "₹6,667",
      "value": 6667,
      "unit": "INR"
    },
    "attention_shift_event_id": "event_attention_shift"
  },
  "frame_spans": [
    {
      "event_id": "event_full_price",
      "start_frame": 0,
      "end_frame": 80,
      "duration_frames": 80
    },
    {
      "event_id": "event_monthly_payment",
      "start_frame": 80,
      "end_frame": 160,
      "duration_frames": 80
    },
    {
      "event_id": "event_attention_shift",
      "start_frame": 160,
      "end_frame": 240,
      "duration_frames": 80
    }
  ]
}
```

## Engine Boundary

`RenderSpecEngine` is pure.

It accepts:

```text
VisualPlan
TimedScenePlan
```

It returns:

```text
RenderSpec
```

It does not:

- read the database
- write artifacts
- call FastAPI
- choose a component
- inspect SemanticScene
- inspect narration
- run Remotion
- write video files

## Frame Conversion Rule

The engine converts seconds to frames:

```text
frames = round(seconds * fps)
```

For the MVP:

```text
8 seconds * 30 fps = 240 frames
```

The three timing spans become:

```text
0 -> 80
80 -> 160
160 -> 240
```

## PipelineService Boundary

`PipelineService` handles orchestration:

```text
find visual_plan artifact
check it can advance
find timed_scene_plan artifact
check it can advance
deserialize parents
call RenderSpecEngine
validate RenderSpec
store render_spec artifact
return stored artifact
```

Only stages through `render_spec` are implemented by Phase 11.

## Validation

`RenderSpecValidator` checks:

- scene id matches `VisualPlan`
- scene id matches `TimedScenePlan`
- composition matches `VisualPlan.component`
- props exactly match `VisualPlan.props`
- FPS matches `TimedScenePlan.fps`
- duration frames match timed duration and FPS
- every timed span has one frame span
- frame span order matches timed span order
- first frame span starts at frame 0
- final frame span ends at `duration_frames`
- frame spans are contiguous and non-overlapping
- video output fields are not accepted

## Explicitly Deferred

- Remotion execution
- Video artifact
- output storage key
- render failure storage
- playback UI
- AI
