# Phase 4 — NarrativeArc

Phase 4 adds explicit story progression after `ScriptBrief`.

## What NarrativeArc Means

`NarrativeArc` describes how the viewer's understanding should move.

For the MVP, the arc is:

```text
curiosity
comfort
reversal
realization
```

It does not write narration.

It does not decide visuals.

## Input and Output

Input:

```text
ScriptBrief
```

Output:

```text
NarrativeArc
```

Example output:

```json
{
  "viewer_question": "If the phone costs ₹80,000, why does ₹6,667 per month feel easier to accept?",
  "arc": ["curiosity", "comfort", "reversal", "realization"],
  "scene_arc_steps": [
    {
      "scene_id": "scene_01",
      "scene_function_label": "full_price_vs_monthly_payment",
      "arc_phases": ["curiosity", "comfort", "reversal", "realization"],
      "is_payoff_scene": true
    }
  ]
}
```

## Engine Boundary

`NarrativeArcEngine` is pure.

It accepts:

```text
ScriptBrief
```

It returns:

```text
NarrativeArc
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
deserialize ScriptBrief
call NarrativeArcEngine
validate NarrativeArc
store narrative_arc artifact
return stored artifact
```

Only `script_brief` and `narrative_arc` are implemented by Phase 4.

## Validation

`NarrativeArcValidator` checks:

- topic matches ScriptBrief
- thesis matches ScriptBrief
- viewer question exists
- arc is curiosity, comfort, reversal, realization
- every ScriptBrief scene function has an arc step
- at least one payoff scene exists
- arc steps do not reference unknown scenes

## Explicitly Deferred

- ScriptDraft
- SceneScript
- SemanticScene
- VisualEventSequence
- VisualPlan
- TimedScenePlan
- RenderSpec
- Video rendering
- AI

