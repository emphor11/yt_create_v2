# Phase 6 — SceneScript

Phase 6 turns the draft narration into an independent scene unit.

## What SceneScript Means

`SceneScript` is one scene packaged with the context it needs.

For the MVP, it creates:

```text
scene_01
```

It contains:

- scene id
- topic
- angle
- thesis
- mechanism
- scene function label
- arc phases
- narrative purpose
- narration
- story state

It does not create semantic roles.

It does not decide visuals.

It does not decide timing.

## Input and Output

Input:

```text
ScriptBrief + NarrativeArc + ScriptDraft
```

Output:

```text
SceneScript
```

Example output:

```json
{
  "scene_id": "scene_01",
  "mechanism": "payment_pain_reduction",
  "scene_function_label": "full_price_vs_monthly_payment",
  "narration": "The phone costs ₹80,000. But the EMI is shown as ₹6,667 per month...",
  "story_state": {
    "recurring_example": "₹80,000 phone"
  }
}
```

## Engine Boundary

`SceneScriptEngine` is pure.

It accepts:

```text
ScriptBrief
NarrativeArc
ScriptDraft
```

It returns:

```text
SceneScript
```

It does not:

- read the database
- write artifacts
- call FastAPI
- validate
- render
- infer mechanism from narration

## PipelineService Boundary

`PipelineService` handles orchestration:

```text
find script_brief artifact
check it can advance
find narrative_arc artifact
check it can advance
find script_draft artifact
check it can advance
deserialize parents
call SceneScriptEngine
validate SceneScript
store scene_script artifact
return stored artifact
```

Only `script_brief`, `narrative_arc`, `script_draft`, and `scene_script` are implemented by Phase 6.

## Validation

`SceneScriptValidator` checks:

- topic matches `ScriptBrief`
- angle matches `ScriptBrief`
- thesis matches `ScriptBrief`
- `ScriptDraft` still matches `ScriptBrief`
- `NarrativeArc` still matches `ScriptBrief`
- scene id exists
- mechanism matches `ScriptBrief`
- scene label matches parent artifacts
- arc phases match `NarrativeArc`
- narrative purpose matches `NarrativeArc`
- narration matches `ScriptDraft`
- `story_state.recurring_example` matches `ScriptBrief`
- later-stage fields are not accepted

## Explicitly Deferred

- SemanticScene
- VisualEventSequence
- VisualPlan
- TimedScenePlan
- RenderSpec
- Video rendering
- AI
