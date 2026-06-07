# Phase 5 — ScriptDraft

Phase 5 adds the first narration artifact after strategy and story progression are already known.

## What ScriptDraft Means

`ScriptDraft` is the rough spoken script.

It contains:

- hook
- draft scene narration
- outro

It does not create semantic roles.

It does not decide visuals.

It does not decide timing.

## Input and Output

Input:

```text
ScriptBrief + NarrativeArc
```

Output:

```text
ScriptDraft
```

Example output:

```json
{
  "topic": "Why Monthly Payments Feel Cheap",
  "angle": "How EMIs hide total cost",
  "hook": "An ₹80,000 phone sounds expensive. But when the same phone is shown as ₹6,667 per month, it suddenly feels easier to say yes.",
  "scenes": [
    {
      "scene_id": "scene_01",
      "scene_function_label": "full_price_vs_monthly_payment",
      "narration": "The phone costs ₹80,000. But the EMI is shown as ₹6,667 per month..."
    }
  ],
  "outro": "That is the trick of monthly payments..."
}
```

## Engine Boundary

`ScriptDraftEngine` is pure.

It accepts:

```text
ScriptBrief
NarrativeArc
```

It returns:

```text
ScriptDraft
```

It does not:

- read the database
- write artifacts
- call FastAPI
- validate
- render

## PipelineService Boundary

`PipelineService` handles orchestration:

```text
find script_brief artifact
check it can advance
find narrative_arc artifact
check it can advance
deserialize parents
call ScriptDraftEngine
validate ScriptDraft
store script_draft artifact
return stored artifact
```

Only `script_brief`, `narrative_arc`, and `script_draft` are implemented by Phase 5.

## Validation

`ScriptDraftValidator` checks:

- topic matches `ScriptBrief`
- angle matches `ScriptBrief`
- thesis matches `ScriptBrief`
- `NarrativeArc` still matches `ScriptBrief`
- hook exists
- outro exists
- draft scenes exist
- draft scene order matches `ScriptBrief`
- draft scene order matches `NarrativeArc`
- scene labels match parent artifacts
- recurring example stays `₹80,000 phone`
- narration stays focused on EMI or monthly payment framing
- later-stage fields are not accepted

## Explicitly Deferred

- SceneScript
- SemanticScene
- VisualEventSequence
- VisualPlan
- TimedScenePlan
- RenderSpec
- Video rendering
- AI
