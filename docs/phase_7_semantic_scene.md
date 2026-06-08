# Phase 7 — SemanticScene

Phase 7 turns a scene script into structured meaning.

## What SemanticScene Means

`SemanticScene` owns meaning and numeric truth.

For the MVP, it extracts:

- full product price
- monthly payment
- relationship between them
- confidence
- warnings

It does not decide visuals.

It does not decide timing.

It does not render.

## Input and Output

Input:

```text
SceneScript
```

Output:

```text
SemanticScene
```

Example output:

```json
{
  "scene_id": "scene_01",
  "primary_concept": "payment_pain_reduction",
  "confidence": 1.0,
  "warnings": [],
  "entities": [
    {
      "id": "entity_price",
      "role": "product_price",
      "raw": "₹80,000",
      "value": 80000,
      "unit": "INR",
      "source_text": "The phone costs ₹80,000."
    },
    {
      "id": "entity_emi",
      "role": "monthly_payment",
      "raw": "₹6,667",
      "value": 6667,
      "unit": "INR",
      "source_text": "But the EMI is shown as ₹6,667 per month."
    }
  ],
  "relationships": [
    {
      "type": "reframes",
      "from_entity_id": "entity_emi",
      "to_entity_id": "entity_price"
    }
  ]
}
```

## Engine Boundary

`SemanticSceneEngine` is pure.

It accepts:

```text
SceneScript
```

It returns:

```text
SemanticScene
```

It does not:

- read the database
- write artifacts
- call FastAPI
- choose visuals
- create render props

## Parser Rules

The MVP parser supports:

```text
₹80,000
Rs. 80,000
80,000
₹ 80,000
₹6,667/month
per month
monthly installment
EMI
```

Role rules:

- sentence containing `costs`, `price`, `full price`, or `total price` becomes `product_price`
- sentence containing `EMI`, `per month`, `/month`, `monthly`, or `installment` becomes `monthly_payment`
- money without a clear role becomes `unknown_money`

## Confidence

Confidence score:

- required roles present: `+0.4`
- every entity has source text: `+0.2`
- mechanism exists in `FinanceDomainRegistry`: `+0.2`
- `reframes` relationship detected: `+0.2`

Score below `0.75` creates a low-confidence warning.

## PipelineService Boundary

`PipelineService` handles orchestration:

```text
find scene_script artifact
check it can advance
deserialize SceneScript
call SemanticSceneEngine
validate SemanticScene
store semantic_scene artifact
return stored artifact
```

Only stages through `semantic_scene` are implemented by Phase 7.

## Validation

`SemanticSceneValidator` checks:

- scene id matches `SceneScript`
- primary concept matches `SceneScript.mechanism`
- primary concept is supported by `FinanceDomainRegistry`
- required roles exist
- entities have ids, roles, raw values, numeric values, INR unit, and source text
- `reframes` points from monthly payment to product price
- relationships reference known entities
- low confidence is reported as a warning
- downstream visual/render fields are not accepted

## Explicitly Deferred

- VisualEventSequence
- VisualPlan
- TimedScenePlan
- RenderSpec
- Video rendering
- AI
