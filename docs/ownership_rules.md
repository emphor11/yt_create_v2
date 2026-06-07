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

