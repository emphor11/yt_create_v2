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

## Phase 5 Boundary

Phase 5 implements the deterministic `ScriptDraft` stage.

Allowed:

- transform a valid `ScriptBrief` and valid `NarrativeArc` into one `ScriptDraft`
- write the hook, draft scene narration, and outro
- preserve ScriptBrief topic, angle, thesis, scene function labels, and recurring example
- preserve NarrativeArc scene order
- store the `script_draft` artifact with parent role map:

```json
{
  "script_brief": "artifact_123",
  "narrative_arc": "artifact_456"
}
```

Not allowed yet:

- `SceneScript`
- independent regenerable scene units
- semantic entity extraction
- semantic relationships
- visual event creation
- visual component selection
- timing
- rendering

`ScriptDraft` owns narration only. It must not create semantic roles, visual events, component props, timing spans, or render instructions.

## Phase 6 Boundary

Phase 6 implements the deterministic `SceneScript` stage.

Allowed:

- transform a valid `ScriptBrief`, valid `NarrativeArc`, and valid `ScriptDraft` into one `SceneScript`
- package `scene_01` as an independent scene unit
- copy the scene mechanism from `ScriptBrief`
- copy scene function label from `ScriptBrief`
- copy arc phases and narrative purpose from `NarrativeArc`
- copy scene narration from `ScriptDraft`
- store `story_state.recurring_example`
- store the `scene_script` artifact with parent role map:

```json
{
  "script_brief": "artifact_123",
  "narrative_arc": "artifact_456",
  "script_draft": "artifact_789"
}
```

Not allowed yet:

- semantic entity extraction
- semantic relationships
- numeric truth ownership
- visual event creation
- visual component selection
- timing
- rendering

`SceneScript` owns the independent scene unit only. It must not infer mechanism from narration, create semantic roles, choose visuals, or create render instructions.

## Phase 7 Boundary

Phase 7 implements the deterministic `SemanticScene` stage.

Allowed:

- transform a valid `SceneScript` into one `SemanticScene`
- parse INR money amounts from scene narration
- assign semantic roles:
  - `product_price`
  - `monthly_payment`
  - `unknown_money`
- attach every entity to source text
- create the `reframes` relationship when product price and monthly payment both exist
- calculate confidence
- store warnings
- store blocked semantic artifacts for debugging
- store the `semantic_scene` artifact with parent role map:

```json
{
  "scene_script": "artifact_123"
}
```

Not allowed yet:

- visual event creation
- visual component selection
- timing
- render props
- rendering

`SemanticScene` owns meaning and numeric truth. It must not choose visual primitives, component props, timing spans, or render instructions.

## Phase 8 Boundary

Phase 8 implements the deterministic `VisualEventSequence` stage.

Allowed:

- transform a valid `SemanticScene` into one `VisualEventSequence`
- create visual events only from semantic entities and relationships
- map `product_price` to `reveal_full_price`
- map `monthly_payment` to `reveal_monthly_payment`
- map `reframes` to `attention_shift`
- link every event back to a semantic entity id or relationship type
- store the `visual_event_sequence` artifact with parent role map:

```json
{
  "semantic_scene": "artifact_123"
}
```

Not allowed yet:

- visual component selection
- component props
- timing spans
- render specs
- rendering

`VisualEventSequence` owns viewer-facing event order only. It must not invent numbers, choose components, create layout props, assign timing, or create render instructions.

## Phase 9 Boundary

Phase 9 implements the deterministic `VisualPlan` stage.

Allowed:

- transform a valid `SemanticScene` and valid `VisualEventSequence` into one `VisualPlan`
- select `SplitComparison` from `ComponentRegistry`
- map `product_price` to the left side
- map `monthly_payment` to the right side
- copy raw values, numeric values, units, and semantic entity ids from `SemanticScene`
- reference the `attention_shift` event from `VisualEventSequence`
- store a selection reason
- store the `visual_plan` artifact with parent role map:

```json
{
  "semantic_scene": "artifact_123",
  "visual_event_sequence": "artifact_456"
}
```

Not allowed yet:

- timing spans
- frame math
- render specs
- rendering

`VisualPlan` owns component choice and component props only. It must not invent numbers, assign timing, convert seconds to frames, or create render instructions.

## Phase 10 Boundary

Phase 10 implements the deterministic `TimedScenePlan` stage.

Allowed:

- transform a valid `VisualPlan` and valid `VisualEventSequence` into one `TimedScenePlan`
- assign a fixed 8-second duration for the MVP scene
- store 30 FPS as planning metadata
- create one `TimedSpan` for every visual event
- preserve the visual event order from `VisualEventSequence`
- cover the full scene duration without gaps or overlaps
- store the `timed_scene_plan` artifact with parent role map:

```json
{
  "visual_plan": "artifact_123",
  "visual_event_sequence": "artifact_456"
}
```

Not allowed yet:

- frame conversion
- Remotion composition instructions
- render specs
- output storage keys
- video rendering

`TimedScenePlan` owns timing in seconds only. It must not choose components, change component props, convert seconds into frames, create animation details, or create render instructions.

## Phase 11 Boundary

Phase 11 implements the deterministic `RenderSpec` stage.

Allowed:

- transform a valid `VisualPlan` and valid `TimedScenePlan` into one `RenderSpec`
- copy the Remotion composition name from `VisualPlan.component`
- copy component props from `VisualPlan.props`
- copy FPS from `TimedScenePlan`
- convert timed spans from seconds into frame spans
- calculate total `duration_frames`
- store the `render_spec` artifact with parent role map:

```json
{
  "visual_plan": "artifact_123",
  "timed_scene_plan": "artifact_456"
}
```

Not allowed yet:

- running Remotion
- writing video files
- output storage keys
- render status tracking
- video artifact creation

`RenderSpec` owns renderer instructions only. It must not choose components, reinterpret semantic meaning, change visual props, create media files, or store render output paths.
