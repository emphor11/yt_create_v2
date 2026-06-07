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

## Phase 2 Boundary

Phase 2 implements the first artifact in the pipeline: `TopicRequest`.

Allowed:

- accept user topic and angle during project creation
- create one deterministic pipeline run
- store one root `topic_request` artifact in that run
- validate topic and angle as present or blocked

Not allowed yet:

- `PipelineService`
- stage execution
- `ScriptBrief`
- mechanism selection
- narration generation
- semantic parsing
- visual planning
- rendering

`TopicRequest` captures user intent only. It does not decide finance mechanisms, scene functions, script structure, semantic roles, components, timing, or render props.

## Phase 3 Boundary

Phase 3 implements the deterministic `ScriptBrief` stage.

Allowed:

- transform a valid `TopicRequest` into one `ScriptBrief`
- use `FinanceDomainRegistry` for allowed mechanisms
- store the `script_brief` artifact with parent role map `{ "topic_request": "..." }`
- return the existing `script_brief` artifact if the stage is run again in the same run

Not allowed yet:

- `NarrativeArc`
- narration writing
- scene script generation
- semantic extraction
- visual event creation
- visual component selection
- timing
- rendering

`ScriptBrief` owns strategy only. It may name mechanisms, thesis, recurring example, and scene function. It must not create narration, semantic roles, visual props, or render instructions.

## Phase 4 Boundary

Phase 4 implements the deterministic `NarrativeArc` stage.

Allowed:

- transform a valid `ScriptBrief` into one `NarrativeArc`
- define the viewer question
- define the arc phases: curiosity, comfort, reversal, realization
- map every ScriptBrief scene function to a scene arc step
- identify at least one payoff scene
- store the `narrative_arc` artifact with parent role map `{ "script_brief": "..." }`

Not allowed yet:

- narration writing
- `ScriptDraft`
- scene script generation
- semantic extraction
- visual event creation
- visual component selection
- timing
- rendering

`NarrativeArc` owns story progression only. It must not write narration, extract numbers, choose visuals, or create render instructions.
