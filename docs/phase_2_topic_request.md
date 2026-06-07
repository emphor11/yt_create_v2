# Phase 2 — TopicRequest

Phase 2 adds the first real pipeline artifact.

## What TopicRequest Means

`TopicRequest` is the user's starting intent.

Example:

```json
{
  "schema_version": "1",
  "topic": "Why Monthly Payments Feel Cheap",
  "angle": "How EMIs hide total cost"
}
```

It answers:

- what the video is about
- what angle the video should take

It does not answer:

- which finance mechanism to use
- what scenes exist
- what narration says
- what semantic roles exist
- what component renders the scene

Those decisions belong to later phases.

## Project Creation

`POST /projects` now creates:

```text
Project
PipelineRun
TopicRequest artifact
```

The TopicRequest artifact is the root artifact. Its parent role map is empty:

```json
{}
```

## Validation

`TopicRequestValidator` checks:

- topic is not empty
- angle is not empty

If both are present, the artifact is `valid`.

If either is missing, the artifact is `blocked`.

Blocked artifacts are still stored so the user can inspect what went wrong.

## Explicitly Deferred

- ScriptBrief
- engines
- PipelineService
- stage execution
- semantic parsing
- visual planning
- rendering
- AI

