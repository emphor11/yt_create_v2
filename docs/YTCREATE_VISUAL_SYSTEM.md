# YTCreate Visual System Constitution

Status: authoritative architecture contract for the visual-system migration.

This document is the source of truth for future visual-system work in YTCreate V2. It was created from the read-only architecture audit recorded in [`VISUAL_ARCHITECTURE_MIGRATION.md`](./VISUAL_ARCHITECTURE_MIGRATION.md). It defines ownership and contracts; it does not itself change runtime behavior.

## 1. Mission

YTCreate is evolving from a component-selection video generator into a scene-driven visual storytelling system.

The goal is not a larger library of finished templates. The goal is to describe a visual world of objects and relationships that persists, changes, and explains the narrative over time, then render that description deterministically.

The central separation is:

```text
Visual meaning
    ↓
Visual story: what should happen?
    ↓
Visual treatment: how should it look and behave?
    ↓
Visual scene graph: what exists on screen?
    ↓
Choreography: how does it continue across scenes?
    ↓
Scene compiler: deterministic renderer instructions
    ↓
Remotion: pixels and media
```

## 2. Target architecture

```text
Research
  → Narrative
  → Script
  → Visual Intent
  → Visual Story Director
  → Visual Treatment Director
  → Visual Scene Graph
  → Visual Choreographer
  → Scene Compiler
  → RenderSpec
  → Remotion Runtime
  → Video QA
```

The existing Research, Narrative, Script, artifact, audio, storage, and Remotion infrastructure remains in scope for reuse. The migration primarily changes the decision layer between semantic intent and rendering.

## 3. Ownership rules

Every layer has one job. A downstream layer may execute an upstream decision, but may not reinterpret its ownership.

| Layer | Owns | Must not own |
|---|---|---|
| Research | sourced evidence and citations | visual form or invented values |
| Narrative | viewer question, arc, and progression | renderer components or coordinates |
| Script | narration and speech cues | factual values not supported by research |
| Visual Intent | semantic meaning, factual grounding, relationships, and source lineage | React components, layout coordinates, or render instructions |
| Visual Story Director | the sequence of visual events needed to teach the meaning | new facts, component names, TSX, or pixel positions |
| Visual Treatment Director | medium, objects, relationships, layout intent, continuity, emphasis, and behavior | new facts, arbitrary coordinates, or renderer code |
| Visual Scene Graph | machine-readable visual world and its event references | editorial invention or provider calls |
| Visual Choreographer | continuity and transitions across neighboring scenes | factual reinterpretation or renderer implementation |
| Scene Compiler | validation and deterministic translation to render instructions | editorial decisions, missing-data repair, or LLM calls at render time |
| RenderSpec | complete, explicit renderer input | unresolved meaning, hidden defaults, or missing evidence |
| Remotion | deterministic drawing, animation, media playback, and frame execution | choosing what to show or inventing data |
| Video QA | deterministic and editorial quality checks | silently rewriting the scene |

### Non-negotiable rules

1. Never invent factual values. Missing evidence remains missing.
2. Every factual display value must be copied from approved evidence or derived by a declared deterministic transformation whose inputs are approved.
3. LLMs must not generate arbitrary React, TSX, JavaScript, or renderer code.
4. LLMs must not directly control pixel-level rendering.
5. Visual Intent must not select renderer components as its primary responsibility.
6. The renderer must not make editorial decisions.
7. Components are implementation capabilities, not the visual story.
8. Prefer persistent objects that transform over unrelated scene cuts when the narrative describes state change.
9. Reusable primitives are encouraged; repetitive finished templates are not.
10. B-roll is an intentional visual medium, not a generic fallback for a difficult concept.
11. Existing working components, design tokens, audio timing, artifact lineage, and renderer infrastructure are preserved whenever possible.
12. Do not redesign unrelated pipeline stages.
13. Do not delete the current pipeline until the replacement has passed a controlled vertical slice and comparison.
14. Every architectural change must add contract tests and preserve artifact lineage.
15. Deterministic execution takes precedence over LLM-generated runtime behavior.

## 4. Visual concepts

These terms are deliberately distinct:

### Meaning

The viewer understanding that must be achieved. Example: “A higher interest rate increases the borrower’s monthly payment.” This belongs to Visual Intent and remains grounded in source evidence.

### Visual story

The ordered visual progression. Example: establish the loan, establish the baseline rate, show the baseline EMI, change the rate, transform the EMI, emphasize the additional burden. It answers **what should happen visually?**

### Visual treatment

The authored visual expression of that progression. Example: use a persistent financial document, attach the rate to it, place the EMI below it, transform the existing values, and focus the changed burden. It answers **how should it look and behave?**

### Rendering

The technical execution of a treatment through scene objects, layout resolution, animation behavior, frame timing, media, and Remotion primitives.

## 5. Visual language

The visual language is a capability vocabulary, not a finished-template catalog.

### Objects

The initial vocabulary may include:

```text
text, number, label, card, document, circle, rectangle, line, arrow,
connector, icon, image, video, chart, graph, badge, tag, node, container,
background
```

### Layout intents

```text
center, stack, row, column, grid, split, radial, timeline, flow,
anchored, freeform
```

The LLM may express relationships such as “rate is top-right of loan” or “EMI is below loan.” The layout engine resolves coordinates, bounds, safe areas, spacing, and responsive scale.

### Behaviors

```text
appear, disappear, move, scale, fade, reveal, transform, morph, connect,
disconnect, expand, compress, split, merge, accumulate, decompose,
highlight, focus, trace, rearrange
```

### Camera behaviors

```text
hold, push_in, pull_out, pan, focus, follow
```

### Materials

```text
editorial_graphic, financial_document, data_visualization, diagram,
photographic, video, UI, minimal_2d
```

These lists are extensible only through an explicit capability-contract change. New vocabulary must be implemented by deterministic renderer capabilities before an LLM is allowed to request it.

## 6. Visual Scene Graph contract

The Visual Scene Graph is the machine-readable description of one visual world. It is not React props and is not a list of independent composition rectangles.

The initial contract is intentionally abstract:

```json
{
  "schema_version": "1",
  "scene_id": "loan_01",
  "visual_goal": "Show how higher interest increases monthly burden",
  "source_refs": [
    {
      "kind": "visual_intent",
      "id": "idea_02/intent_01"
    }
  ],
  "objects": [
    {
      "id": "loan",
      "type": "document",
      "material": "financial_document",
      "content": {
        "title": "Home loan",
        "amount": {
          "raw": "₹50 lakh",
          "evidence_ref": "research.fact.loan_amount"
        }
      },
      "layout": {
        "anchor": "center"
      },
      "persistence": "persistent"
    },
    {
      "id": "rate",
      "type": "number",
      "content": {
        "raw": "8.5%",
        "evidence_ref": "research.fact.rate_baseline"
      },
      "layout": {
        "relative_to": "loan",
        "placement": "top_right"
      },
      "persistence": "persistent"
    },
    {
      "id": "emi",
      "type": "number",
      "content": {
        "raw": "₹43,391",
        "evidence_ref": "research.fact.emi_baseline"
      },
      "layout": {
        "relative_to": "loan",
        "placement": "bottom"
      },
      "persistence": "persistent"
    }
  ],
  "relationships": [
    {
      "id": "rate_causes_emi",
      "from": "rate",
      "to": "emi",
      "type": "causes",
      "label": "changes monthly payment"
    }
  ],
  "events": [
    {
      "id": "establish_loan",
      "at": { "kind": "speech_anchor", "ref": "₹50 lakh home loan" },
      "behavior": "reveal",
      "targets": ["loan"]
    },
    {
      "id": "change_rate",
      "at": { "kind": "speech_anchor", "ref": "rate rises" },
      "behavior": "transform",
      "targets": ["rate"],
      "from": "8.5%",
      "to": "10.5%",
      "evidence_refs": ["research.fact.rate_baseline", "research.fact.rate_high"]
    },
    {
      "id": "change_emi",
      "at": { "kind": "speech_anchor", "ref": "₹49,919" },
      "behavior": "transform",
      "targets": ["emi"],
      "from": "₹43,391",
      "to": "₹49,919",
      "evidence_refs": ["research.fact.emi_baseline", "research.fact.emi_high"]
    }
  ],
  "camera": {
    "behavior": "focus",
    "target": "emi",
    "reason": "emphasize additional monthly burden"
  }
}
```

### Contract requirements

- Object IDs are stable within a scene and are the identity used for continuity.
- Events target existing object IDs or explicitly declare a deterministic creation/destruction operation.
- Relationships reference existing objects and explain why an edge is present.
- Layout is expressed as intent and constraints; raw `x`, `y`, or arbitrary pixel coordinates are not an LLM output contract.
- Timing may refer to speech anchors or semantic order. Frame conversion belongs to the compiler.
- Factual content carries an evidence reference or an explicit deterministic-derivation reference.
- A scene must distinguish factual content from illustrative decoration. Illustrative content may not look like sourced data unless it is explicitly labeled.
- A persistent object that changes state keeps its ID across the relevant events.
- Unknown values are represented as missing/unknown, never as plausible defaults.
- The compiler must reject dangling references, unsupported object types, unsupported behaviors, invalid evidence references, and conflicting transformations.

### Scene-world continuity

The intended runtime model is one world that evolves:

```text
loan exists; rate = 8.5%; EMI = ₹43,391
        ↓ change_rate
loan exists; rate = 10.5%; EMI = ₹43,391
        ↓ change_emi
loan exists; rate = 10.5%; EMI = ₹49,919
```

This is different from rendering three unrelated cards. Scene boundaries may still occur, but a boundary must be an intentional editorial choice rather than an accidental consequence of a sentence or component change.

## 7. Compiler and renderer contract

The Scene Compiler is the only boundary that translates the abstract scene graph into renderer instructions.

It must:

1. validate the scene graph and all source/evidence references;
2. resolve layout intents through deterministic layout rules;
3. resolve behaviors through shared motion semantics;
4. resolve speech anchors into time and then frames using the voice track;
5. select registered primitive/specialized capability implementations;
6. emit the existing or extended `RenderSpec` shape with explicit scene objects, actions, assets, and timing;
7. preserve source lineage and compiler diagnostics in the artifact;
8. fail clearly when required evidence or capabilities are unavailable.

The compiler may use existing specialized visual modules as implementation capabilities. It must not silently convert a missing scene into a generic template or B-roll treatment.

Remotion receives a complete, validated render contract. It may animate and draw that contract, but it may not infer meaning, choose a different composition, fill missing values, or read narration to make decisions.

## 8. Choreography contract

The Visual Choreographer operates at video level. It receives the previous, current, and next visual scene plus duration, importance, recent visual history, current medium, and available capabilities.

It may decide:

```text
continue, transform, cut, hold, transition, return, zoom, pull_back,
introduce_new_visual_world
```

It must preserve factual identity and may not rewrite scene meaning. Its purpose is to prevent sentence-by-sentence visual isolation, repeated layouts, and arbitrary medium switching.

Until the choreographer exists, the migration must not claim to provide video-level continuity. The first vertical slice may use deterministic continuity rules.

## 9. Quality gate

Every new scene-driven path must be checked at two levels.

### Deterministic checks

- all factual values are source-backed or declared deterministic derivations;
- object and relationship references resolve;
- event targets resolve;
- no unsupported capability is requested;
- layout fits the safe area with no unapproved overlap;
- speech anchors and frame spans are monotonic and within duration;
- persistent object IDs survive intended transformations;
- no implicit factual defaults appear in the compiled output;
- lineage connects scene output to Visual Intent, script, and research artifacts.

### Editorial checks

- each important visual has a purpose;
- the visual adds information beyond the narration;
- causal relationships are visible when they matter;
- the scene evolves when the story describes a change;
- the medium is appropriate rather than a fallback;
- the sequence does not repeat the same treatment without a reason;
- the complete video feels like one authored visual story.

## 10. Migration rules

- Keep the current legacy and composition paths available during migration.
- Introduce adapters at artifact boundaries rather than duplicating orchestration.
- Do not make the new scene graph depend on Remotion component names.
- Do not migrate all compositions at once.
- Start with one controlled, fact-locked loan example and compare it with the existing composition path.
- Promote a capability only after it has a deterministic renderer implementation, schema validation, and a focused test.
- Retire old decision-making only after an equivalent or better scene-driven path is validated in production-like runs.

## 11. First implementation slice

The first implementation is deliberately small:

```text
approved Visual Intent
  → hand-authored Visual Story
  → hand-authored Visual Treatment
  → validated Scene Graph
  → deterministic layout/motion compiler
  → one Remotion scene
```

Use the controlled example:

```text
₹50 lakh home loan
→ 8.5% rate
→ ₹43,391 EMI
→ 10.5% rate
→ ₹49,919 EMI
```

Success means the same loan, rate, and EMI objects visibly persist and transform, the values remain fact-locked, and the compiled output can be compared against the current path. It does not require a new LLM prompt, a large primitive catalog, or the deletion of existing compositions.

## 12. Forbidden shortcuts

Do not:

- start by adding twenty new compositions;
- let an LLM generate React/TSX or arbitrary renderer code;
- accept arbitrary pixel coordinates from an LLM;
- rewrite Remotion;
- delete the current composition pipeline before validation;
- change Research, Narrative, or Script without a demonstrated visual-system need;
- make every sentence a new scene;
- use B-roll as generic fallback;
- invent factual values or silently replace missing evidence;
- sacrifice deterministic rendering for creative freedom.

