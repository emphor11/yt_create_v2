# Phase 1 — Artifact Infrastructure

Phase 1 introduces persistence for immutable, run-scoped artifacts.

## Storage Model

The backend stores three tables:

```text
projects
pipeline_runs
artifacts
```

`projects` are the user-facing containers. `pipeline_runs` make artifact selection run-scoped. `artifacts` store JSON payloads, validation JSON, status, and parent role maps.

## Parent Role Maps

Artifact lineage is not stored as a plain list. Parent links are stored by role:

```json
{
  "fixture_parent": "artifact_abc"
}
```

This preserves the reason each parent was used.

## Status Policy

All artifacts are stored, including failed or blocked records:

```text
valid
warning
blocked
failed
```

Only `valid` and `warning` artifacts are advanceable in future pipeline phases. Phase 1 does not select parent artifacts for stage execution; it only defines and tests the status policy.

## API Surface

Phase 1 exposes:

```text
POST /projects
GET /projects
GET /projects/{project_id}
GET /projects/{project_id}/runs
GET /projects/{project_id}/runs/{run_id}
GET /projects/{project_id}/artifacts
GET /projects/{project_id}/runs/{run_id}/artifacts
GET /artifacts/{artifact_id}
GET /artifacts/{artifact_id}/parents
GET /artifacts/{artifact_id}/children
```

There are no stage execution endpoints in Phase 1.

## Explicitly Deferred

- TopicRequest creation
- PipelineService
- engines
- validators
- stage execution
- regeneration
- render output
- AI

