# Phase 13 — MVP Hardening

Phase 13 makes the MVP easier to trust and inspect.

## What Hardening Means

Hardening means the system is not only able to run.

It is also able to explain:

- which stages exist
- which stages passed
- which stages are missing
- which stage has errors or warnings
- where a final video came from
- which descendants should be cleared before regeneration

## New Inspection Tools

Phase 13 adds:

```text
GET /projects/{project_id}/runs/{run_id}/status
GET /artifacts/{artifact_id}/trace
POST /projects/{project_id}/runs/{run_id}/artifacts/{artifact_id}/regenerate-descendants
```

## Run Status

Run status returns one summary row per pipeline stage.

Each row includes:

- stage name
- artifact type
- artifact id
- status
- error count
- warning count
- validation messages

This lets the UI show a compact validation summary.

## Artifact Trace

Artifact trace returns:

- recursive ancestors
- recursive descendants

This is important for debugging.

Example:

```text
Video
-> RenderSpec
-> VisualPlan
-> SemanticScene
```

If the video shows the wrong number, the trace tells us which semantic artifact owned that number.

## Regenerate Descendants

The regenerate-descendants endpoint clears downstream artifacts for a selected artifact.

It does not mutate the selected artifact.

It does not mutate parent artifacts.

It deletes downstream artifacts so the user can rerun stages and recreate them.

Example:

```text
Clear descendants of SemanticScene
```

This removes:

```text
VisualEventSequence
VisualPlan
TimedScenePlan
RenderSpec
Video
```

Then the user can run:

```text
VisualEventSequence -> VisualPlan -> Timing -> RenderSpec -> Render
```

## Golden Pipeline Test

Phase 13 adds a full monthly-payment pipeline test.

It proves:

- every stage can run
- every stage is valid
- video artifact is created
- video can trace back to SemanticScene
- SemanticScene owns `80000` and `6667`

## Explicitly Deferred

- AI
- voice
- publishing
- quality score loops
- automatic regeneration with creative repair
- multi-run editing and forks
