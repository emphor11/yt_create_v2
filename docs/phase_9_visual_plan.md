# Phase 9 — VisualPlan

Phase 9 chooses the visual component and creates component props.

## What VisualPlan Means

`VisualPlan` decides which component should show the scene.

For the MVP, it always selects:

```text
SplitComparison
```

It maps:

```text
product_price -> left side
monthly_payment -> right side
```

It does not decide timing.

It does not create render specs.

It does not render.

## Input and Output

Input:

```text
SemanticScene + VisualEventSequence
```

Output:

```text
VisualPlan
```

Example output:

```json
{
  "scene_id": "scene_01",
  "primary_concept": "payment_pain_reduction",
  "component": "SplitComparison",
  "selection_reason": "Selected SplitComparison because payment_pain_reduction contains product_price and monthly_payment with an attention_shift event.",
  "props": {
    "left": {
      "role": "product_price",
      "semantic_entity_id": "entity_price",
      "label": "Full price",
      "raw": "₹80,000",
      "value": 80000,
      "unit": "INR"
    },
    "right": {
      "role": "monthly_payment",
      "semantic_entity_id": "entity_emi",
      "label": "Monthly payment",
      "raw": "₹6,667",
      "value": 6667,
      "unit": "INR"
    },
    "attention_shift_event_id": "event_attention_shift"
  }
}
```

## ComponentRegistry

Phase 9 registers only one component:

```json
{
  "component": "SplitComparison",
  "required_roles": ["product_price", "monthly_payment"],
  "supported_events": [
    "reveal_full_price",
    "reveal_monthly_payment",
    "attention_shift"
  ],
  "constraints": {
    "left_role": "product_price",
    "right_role": "monthly_payment"
  }
}
```

## Engine Boundary

`VisualPlanEngine` is pure.

It accepts:

```text
SemanticScene
VisualEventSequence
```

It returns:

```text
VisualPlan
```

It does not:

- read the database
- write artifacts
- call FastAPI
- read narration
- assign timing
- create frame counts
- render

## Eligibility

`SplitComparison` is eligible when:

- `SemanticScene` has `product_price`
- `SemanticScene` has `monthly_payment`
- `VisualEventSequence` has `reveal_full_price`
- `VisualEventSequence` has `reveal_monthly_payment`
- `VisualEventSequence` has `attention_shift`
- no semantic money entity is left unlinked
- component is registered

## PipelineService Boundary

`PipelineService` handles orchestration:

```text
find semantic_scene artifact
check it can advance
find visual_event_sequence artifact
check it can advance
deserialize parents
call VisualPlanEngine
validate VisualPlan
store visual_plan artifact
return stored artifact
```

Only stages through `visual_plan` are implemented by Phase 9.

## Validation

`VisualPlanValidator` checks:

- scene id matches both parents
- primary concept matches both parents
- component is registered
- required semantic roles exist
- required event primitives exist
- left side uses `product_price`
- right side uses `monthly_payment`
- prop values match `SemanticScene`
- prop raw text matches `SemanticScene`
- prop units match `SemanticScene`
- every semantic money entity is linked
- attention shift event id references the `attention_shift` event
- downstream timing and render fields are not accepted

## Explicitly Deferred

- TimedScenePlan
- RenderSpec
- Video rendering
- AI
