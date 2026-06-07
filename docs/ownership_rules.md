# YTCreate V2 Ownership Rules

Phase 0 establishes the architecture rules before pipeline code exists.

## Core Rule

No downstream stage may reinterpret upstream ownership.

Each stage owns exactly one transformation boundary. Later phases must preserve these boundaries:

- domain models describe typed payload shape
- validators enforce contract rules
- engines perform pure transformations
- `PipelineService` orchestrates storage and stage execution
- providers call external tools without making meaning decisions
- frontend displays artifacts and requests stage execution
- renderer draws only from render props

## Phase 0 Boundary

Phase 0 intentionally does not implement:

- projects
- pipeline runs
- artifacts
- storage
- engines
- validators beyond the shared `ValidationResult` contract
- Remotion `SplitComparison`
- video rendering
- AI

## Phase 1 Boundary

Phase 1 implements storage and inspection only.

Allowed:

- create project records
- create deterministic pipeline run records
- save immutable artifact records through `ArtifactStore`
- inspect artifacts as JSON
- inspect parents and children through role-map lineage

Not allowed yet:

- stage execution
- `PipelineService`
- `TopicRequest`
- engines
- validators beyond the shared `ValidationResult` contract
- renderer integration
- AI

Artifacts are stored with `project_id` and `run_id`. Parent lineage must use role names:

```json
{
  "script_brief": "artifact_123"
}
```

Parent artifacts must belong to the same project and run as the child artifact.

All artifact statuses are stored:

```text
valid
warning
blocked
failed
```

Only `valid` and `warning` may advance in future phases. Phase 1 exposes this policy but does not implement stage advancement.
