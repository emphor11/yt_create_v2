# Phase 3 — ScriptBrief

Phase 3 adds the first deterministic stage after `TopicRequest`.

## What ScriptBrief Means

`ScriptBrief` is the strategy artifact.

It says:

- what the thesis is
- which finance mechanisms are being used
- what concrete example will recur
- what the first scene should do

It does not write narration or choose visuals.

## Deterministic Output

For the MVP topic, the deterministic engine creates:

```json
{
  "recurring_example": "₹80,000 phone",
  "primary_mechanisms": [
    "payment_pain_reduction",
    "affordability_illusion"
  ]
}
```

## Engine Boundary

`ScriptBriefEngine` is pure.

It accepts:

```text
TopicRequest
```

It returns:

```text
ScriptBrief
```

It does not:

- read the database
- write artifacts
- call FastAPI
- validate
- render

## PipelineService Boundary

`PipelineService` handles orchestration for this stage:

```text
find topic_request artifact
check it can advance
deserialize TopicRequest
call ScriptBriefEngine
validate ScriptBrief
store script_brief artifact
return stored artifact
```

Only `script_brief` is implemented in Phase 3.

## Validation

`ScriptBriefValidator` checks:

- thesis exists
- topic and angle match the TopicRequest
- recurring example is exactly `₹80,000 phone`
- mechanisms are supported by `FinanceDomainRegistry`
- at least one scene function exists
- scene function mechanism is also in primary mechanisms

## Explicitly Deferred

- NarrativeArc
- ScriptDraft
- SceneScript
- SemanticScene
- VisualEventSequence
- VisualPlan
- TimedScenePlan
- RenderSpec
- Video rendering
- AI

