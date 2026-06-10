# Phase 12 — Video Rendering

Phase 12 renders the MVP scene video.

## What Video Means

`Video` is the artifact that records the render result.

For a successful render, it stores:

- scene id
- render status
- file name
- content type
- FPS
- frame duration
- storage key
- file size

It does not store an absolute path.

## Storage Key

The video artifact stores:

```text
projects/{project_id}/runs/{run_id}/scene_01.mp4
```

This is called a storage key.

A storage key is not tied to one computer. Today it maps to local disk. Later it can map to S3 or another cloud storage provider.

## Input and Output

Input:

```text
RenderSpec
```

Output:

```text
Video
```

Example output:

```json
{
  "scene_id": "scene_01",
  "render_status": "succeeded",
  "file_name": "scene_01.mp4",
  "content_type": "video/mp4",
  "fps": 30,
  "duration_frames": 240,
  "storage_key": "projects/project_1/runs/run_1/scene_01.mp4",
  "size_bytes": 184000
}
```

## Engine Boundary

`RenderEngine` accepts:

```text
RenderSpec
project_id
run_id
```

It returns:

```text
Video
```

It does not:

- read the database
- write artifacts
- call FastAPI
- choose a component
- inspect narration
- inspect SemanticScene
- change props
- change frame spans

## Provider Boundary

`RemotionProvider` owns the external render call.

It:

- writes a temporary render request JSON file
- calls the local Remotion render script
- checks the output file exists
- returns file size

It does not make meaning decisions.

## Remotion Boundary

The Remotion renderer contains:

```text
SplitComparison
```

It draws only from RenderSpec props and frame spans.

It does not:

- read narration
- infer labels
- invent numbers
- choose components
- change timing

## PipelineService Boundary

`PipelineService` handles orchestration:

```text
find render_spec artifact
check it can advance
deserialize RenderSpec
call RenderEngine
validate Video
store video artifact
return stored artifact
```

Only stages through `render` are implemented by Phase 12.

## Validation

`VideoValidator` checks:

- scene id matches RenderSpec
- FPS matches RenderSpec
- duration frames match RenderSpec
- file name is `scene_01.mp4`
- content type is `video/mp4`
- successful videos have a safe storage key
- successful videos have positive size
- failed videos store an error message
- failed videos do not store a storage key

## Explicitly Deferred

- regeneration
- render retry UI
- quality dashboards
- audio
- voice
- publishing
- AI
