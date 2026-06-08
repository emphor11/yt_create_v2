# Phase 8 — VisualEventSequence

Phase 8 turns structured meaning into viewer-facing visual events.

## What VisualEventSequence Means

`VisualEventSequence` describes what the viewer should see happen.

For the MVP, it creates:

- reveal the full price
- reveal the monthly payment
- shift attention between them

It does not choose a component.

It does not decide layout.

It does not decide timing.

It does not render.

## Input and Output

Input:

```text
SemanticScene
```

Output:

```text
VisualEventSequence
```

Example output:

```json
{
  "scene_id": "scene_01",
  "primary_concept": "payment_pain_reduction",
  "events": [
    {
      "event_id": "event_full_price",
      "semantic_entity_id": "entity_price",
      "primitive": "reveal_full_price",
      "intent": "establish_real_cost",
      "world_object": "full_price"
    },
    {
      "event_id": "event_monthly_payment",
      "semantic_entity_id": "entity_emi",
      "primitive": "reveal_monthly_payment",
      "intent": "create_comfort",
      "world_object": "monthly_payment"
    },
    {
      "event_id": "event_attention_shift",
      "semantic_relationship_type": "reframes",
      "primitive": "attention_shift",
      "intent": "create_realization",
      "world_object": "comparison_focus"
    }
  ]
}
```

## Engine Boundary

`VisualEventSequenceEngine` is pure.

It accepts:

```text
SemanticScene
```

It returns:

```text
VisualEventSequence
```

It does not:

- read the database
- write artifacts
- call FastAPI
- read narration
- choose components
- create props
- assign timing
- render

## Event Mapping

MVP mapping:

```text
product_price -> reveal_full_price
monthly_payment -> reveal_monthly_payment
reframes -> attention_shift
```

Every event must link back to one of these:

```text
semantic_entity_id
semantic_relationship_type
```

## PipelineService Boundary

`PipelineService` handles orchestration:

```text
find semantic_scene artifact
check it can advance
deserialize SemanticScene
call VisualEventSequenceEngine
validate VisualEventSequence
store visual_event_sequence artifact
return stored artifact
```

Only stages through `visual_event_sequence` are implemented by Phase 8.

## Validation

`VisualEventSequenceValidator` checks:

- scene id matches `SemanticScene`
- primary concept matches `SemanticScene`
- events exist
- event ids are unique
- each event references either a semantic entity or relationship
- entity events reference known semantic entity ids
- relationship events reference known relationship types
- primitives match their semantic roles
- required MVP events exist
- downstream component, timing, and render fields are not accepted

## Explicitly Deferred

- VisualPlan
- TimedScenePlan
- RenderSpec
- Video rendering
- AI
