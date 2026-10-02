# YTCreate Visual Architecture Audit and Migration Map

Audit date: 2026-10-02

Scope: read-only inspection of the current repository architecture. No runtime source, prompt, schema, renderer, test, artifact, or database behavior was changed to produce this audit.

Authoritative companion: [`YTCREATE_VISUAL_SYSTEM.md`](./YTCREATE_VISUAL_SYSTEM.md).

## Executive finding

YTCreate V2 currently contains two visual architectures at different levels of completion:

1. The active production path is a unified strategy artifact with an optional composition plan. In composition mode it runs `VisualIntentEngine → CompositionPlannerEngine → CompositionDataFillerEngine → CompositionAssemblyEngine → RenderSpec → Remotion`. Without a composition plan it runs the legacy `VideoAssemblyEngine` path.
2. The repository also contains a documented Phase 7–12 semantic pipeline—`SemanticScene → VisualEventSequence → VisualPlan → TimedScenePlan → RenderSpec → Video`—but those phases are not the active `PipelineService` path and their corresponding runtime domain/engine artifacts are not present as a complete implementation.

The migration should therefore reconcile an active composition-selection system with an aspirational staged semantic system. It should not assume that adding another parallel pipeline is progress.

## 1. Current runtime map

The active AI run is wired in `backend/app/pipeline_service.py` and `backend/app/pipeline_router.py` as:

```text
GenerateVideoRequest
  ↓
ResearchHandler / ResearchEngine
  ↓ research_packet
NarrativePlanHandler / NarrativePlanEngine
  ↓ narrative_plan
HookHandler / HookEngine
  ↓ hook
ScriptVisualStrategyHandler / ScriptVisualStrategyEngine
  ├─ ScriptVisualStrategy
  ├─ VisualIntentArtifact (composition mode)
  └─ FullCompositionPlan / CompositionBeat[] (composition mode)
  ↓
QualityReviewHandler
  ↓ review_result
VoiceGenerationHandler / VoiceProvider
  ↓ voice_track with word timestamps
VideoAssemblyHandler
  ├─ CompositionAssemblyEngine when composition_plan exists
  └─ VideoAssemblyEngine otherwise
  ↓ render_spec
RenderHandler / RenderEngine / RemotionProvider
  ↓ video
YoutubeMetadataHandler → thumbnail → YoutubeUploadHandler
```

The visual decision boundary is concentrated inside `ScriptVisualStrategyHandler` and the composition engines, not in a separate story/treatment/scene compiler layer.

### Active composition path in detail

```text
strategy narration
  ↓
VisualIntentEngine (LLM; semantic relationship/evidence output)
  ↓ persisted VisualIntentArtifact + provenance
CompositionPlannerEngine
  ├─ CompositionSelector (deterministic relationship → composition routing)
  ├─ LLM planner (closed CompositionRegistry catalog)
  └─ CompositionDataFillerEngine (LLM composition schema filling)
  ↓ CompositionBeat[]
CompositionAssemblyEngine
  ├─ TimelineBuilder (voice timing)
  ├─ AssetResolver (stock media)
  ├─ CompositionResolver (composition → Remotion component/props)
  └─ RenderSpecBuilder
  ↓
RenderSpec.props.scenes[]
  ↓
Remotion VideoAssembly / registered components
```

The current unit of assembly is a timed `SceneSpec` whose component is selected before rendering. The renderer sequences scene rectangles with `Series.Sequence`; it does not maintain a shared object world across neighboring scene specs.

## 2. Existing concepts and future roles

| Existing concept | Current location | Current responsibility | Future role | Migration disposition |
|---|---|---|---|---|
| `ScriptVisualStrategy` | `backend/domain/script_visual_strategy.py` | Body narration, teaching intent, key evidence, voice cues | Script/semantic input to Visual Intent | Keep; do not overload with scene graph fields |
| `VisualIntent` | `backend/domain/visual_intent.py` | Meaning, relationship type, evidence mode, measurements, entities, semantic dynamics | Semantic foundation and fact/evidence boundary | Keep; remove its responsibility for primary composition choice over time |
| `VisualIntentArtifact` | `backend/domain/visual_intent_artifact.py` | Persisted intent sequences and exact narration provenance | Source lineage for story/treatment/scene artifacts | Keep and extend only with compatible lineage fields |
| `CompositionSelector` | `backend/engines/composition_selector.py` | Deterministic relationship/evidence → composition ID routing | Temporary compatibility adapter; later capability eligibility helper | Reduce gradually; do not make it the new creative director |
| `CompositionRegistry` | `backend/registries/composition_registry.py` | Closed catalog of finished compositions, schemas, Remotion IDs, fallbacks | Capability registry containing primitive and specialized modules | Reuse definitions while adding capability metadata; avoid wholesale rewrite |
| `CompositionPlannerEngine` | `backend/engines/composition_planner_engine.py` | LLM selects a registered composition and requests data | Temporary legacy planner or adapter from Treatment to specialized module | Keep behind compatibility boundary during migration |
| `CompositionDataFillerEngine` | `backend/engines/composition_data_filler_engine.py` | LLM fills selected composition schema | Retire as a general fact-producing layer; replace with evidence-bound scene compilation | High-priority boundary to constrain |
| `CompositionBeat` | `backend/domain/composition_plan.py` | One selected composition beat with source refs and data | Legacy adapter input or trace record | Preserve lineage; do not make it the future scene contract |
| `FullCompositionPlan` | `backend/domain/composition_plan.py` | Video-level list of composition beats | Compatibility representation during migration | Keep until scene pipeline proves replacement |
| `CompositionResolver` | `backend/engines/video_assembly/composition_resolver.py` | Composition ID/data → Remotion component props | Specialized-module resolver called by Scene Compiler | Keep and narrow; no editorial fallback decisions |
| `ComponentRegistry` | `backend/registries/component_registry.py` | Generic component schemas and aliases | Primitive/capability registry | Reuse generic components as renderer capabilities |
| `TimelineBuilder` | `backend/engines/video_assembly/timeline_builder.py` | Voice-derived beat timing and trigger-word mapping | Timing input for speech anchors and compiler | Keep; move timing policy behind scene compiler boundary |
| `AssetResolver` | `backend/engines/video_assembly/asset_resolver.py` | Stock image/video query and cache resolution | Media capability provider selected by Treatment | Keep; B-roll must be intentional, not fallback |
| `VideoAssemblyEngine` | `backend/engines/video_assembly_engine.py` | Legacy narration beat → generic component assembly | Legacy adapter | Keep until scene path comparison passes |
| `CompositionAssemblyEngine` | `backend/engines/composition_assembly_engine.py` | Composition beat → specialized component assembly | Compatibility adapter from old plan to RenderSpec | Keep during migration; later become a compiler backend |
| `RenderSpec` | `backend/domain/render_spec.py` | Renderer-ready scene/component props and frame spans | Stable execution boundary receiving compiled scene instructions | Keep; extend compatibly or version explicitly |
| `RenderSpecBuilder` | `backend/engines/video_assembly/render_spec_builder.py` | Builds `RenderSpec` from timed segments/components/assets | Scene Compiler backend or adapter | Keep deterministic; remove editorial responsibility |
| `RenderEngine` | `backend/engines/render_engine.py` | Invokes Remotion and creates `Video` artifact | Runtime/render boundary | Keep unchanged in first slice |
| `VideoAssembly.tsx` | `renderer/remotion/src/VideoAssembly.tsx` | Sequences scene specs and dispatches component IDs | Runtime host for compiled scene renderer and specialized modules | Keep; add scene-driven runtime behind an explicit path |
| Remotion components | `renderer/remotion/src` | Generic and specialized visual implementations | Reusable visual capabilities | Keep and wrap; do not duplicate for cosmetic variants |
| Phase 7–12 docs | `docs/phase_7_*` through `docs/phase_12_*` | Earlier semantic pipeline contracts | Inputs to reconciliation, not proof of live implementation | Preserve as historical design context; update links/status as migration lands |

## 3. Overlap and drift

### 3.1 Semantic pipeline vs active composition pipeline

The Phase 7–12 documents define `SemanticScene`, `VisualEventSequence`, `VisualPlan`, `TimedScenePlan`, and `RenderSpec`. The active codebase instead persists `VisualIntentArtifact` and embeds `FullCompositionPlan` inside `script_visual_strategy`. The `PipelineStage` enum names both sets, but `AI_STAGE_DEFINITIONS`, `NEXT_STAGE_BY_ARTIFACT_TYPE`, and `build_pipeline_service()` route the active run through `video_assembly` directly.

This is not merely naming overlap: the documented `VisualPlan` owns component choice, while the target architecture explicitly moves creative choice toward Visual Story and Visual Treatment. The documented Phase 9 concept should not be carried forward unchanged.

### 3.2 Relationship types and composition IDs

`VisualIntent` contains both semantic `relationship_type` and renderer-facing `composition_id`, and its model validator can derive one from the other. `CompositionSelector` also maps relationship types to composition IDs. This creates duplicate routing authority.

Future rule: Visual Intent may expose semantic relationships and evidence; a compatibility adapter may map them to legacy compositions, but the new story/treatment path must not depend on composition IDs.

### 3.3 Composition catalog vs component catalog

`CompositionRegistry` describes finished authored compositions with data models, variants, Remotion IDs, and fallbacks. `ComponentRegistry` describes generic renderer components. The target system needs a capability registry that can expose primitives, layouts, behaviors, media, and specialized modules without making a finished composition the primary creative unit.

The safe migration is additive metadata and adapters, not an immediate deletion of either registry.

### 3.4 Factual evidence vs composition-schema pressure

The existing audit found that factual preservation at the composition-filling boundary is the highest-risk issue. A selected composition can require fields that are absent from the source intent, and downstream resolver/component defaults can make the result look complete. The target constitution therefore makes evidence references and deterministic derivations mandatory for factual scene content.

### 3.5 Beat timing vs scene continuity

`TimelineBuilder` provides useful voice-track timing and trigger-word mapping, but the resulting `SceneSpec[]` is still a sequence of component scenes. Timing is not yet a persistent-object choreography model. The migration should reuse timestamps as anchors while changing the object/event representation.

## 4. Files and boundaries

### Semantic and planning boundary

- `backend/domain/visual_intent.py`
- `backend/domain/visual_intent_artifact.py`
- `backend/engines/visual_intent_engine.py`
- `backend/engines/composition_selector.py`
- `backend/domain/composition_plan.py`
- `backend/engines/composition_planner_engine.py`
- `backend/engines/composition_data_filler_engine.py`
- `backend/registries/composition_registry.py`
- `backend/registries/component_registry.py`
- `backend/app/stage_handlers/script_visual_strategy_handler.py`

### Assembly and timing boundary

- `backend/engines/video_assembly_engine.py`
- `backend/engines/composition_assembly_engine.py`
- `backend/engines/video_assembly/timeline_builder.py`
- `backend/engines/video_assembly/asset_resolver.py`
- `backend/engines/video_assembly/composition_resolver.py`
- `backend/engines/video_assembly/component_resolver.py`
- `backend/engines/video_assembly/render_spec_builder.py`
- `backend/domain/video_assembly_props.py`
- `backend/app/stage_handlers/video_assembly_handler.py`

### Render boundary

- `backend/domain/render_spec.py`
- `backend/engines/render_engine.py`
- `backend/providers/remotion_provider.py`
- `backend/app/stage_handlers/render_handler.py`
- `renderer/remotion/src/VideoAssembly.tsx`
- `renderer/remotion/src/Root.tsx`
- `renderer/remotion/src/compositions/*.tsx`

### Existing contracts and evidence

- `docs/ownership_rules.md`
- `docs/phase_7_semantic_scene.md`
- `docs/phase_8_visual_event_sequence.md`
- `docs/phase_9_visual_plan.md`
- `docs/phase_10_timed_scene_plan.md`
- `docs/phase_11_render_spec.md`
- `docs/phase_12_video_rendering.md`
- `YTcreate_V2_UNIVERSAL_VIDEO_SYSTEM_AUDIT.md`
- `backend/tests/test_visual_intent_engine.py`
- `backend/tests/test_composition_planner_engine.py`
- `backend/tests/test_composition_data_filler_engine.py`
- `backend/tests/test_pipeline_composition_path.py`
- `backend/tests/test_composition_timeline_alignment.py`
- `backend/tests/test_pipeline_video_assembly.py`
- `backend/tests/test_pipeline_render.py`

## 5. Migration boundaries

### Boundary A — keep Research/Narrative/Script stable

No migration work should alter these stages merely to support the new visual architecture. The scene system consumes their existing artifacts, evidence, narration, and voice timing.

### Boundary B — preserve Visual Intent as semantic source

Visual Intent remains the first visual-system artifact. It should gain stronger provenance/evidence semantics only when needed. It must not become a scene graph or a renderer plan.

### Boundary C — introduce Story and Treatment after intent

The first new artifacts should be explicit visual story and treatment contracts. They should be pure, inspectable, and source-linked. They must not contain React component names or pixel coordinates.

### Boundary D — introduce Scene Graph before changing Remotion

The Scene Graph and compiler contract must be testable without video rendering. Remotion changes should follow a valid compiled vertical slice; do not begin by rewriting the renderer.

### Boundary E — adapt old compositions, do not delete them

Existing specialized compositions remain callable capabilities. A scene compiler may select one as an implementation module when treatment requires it, but the treatment is not defined by that module.

### Boundary F — retain RenderSpec as the execution seam

The current `RenderSpec`/`RenderEngine`/`RemotionProvider` boundary is useful. The new compiler should emit a versioned compatible RenderSpec or an explicitly versioned successor, with no hidden defaults.

### Boundary G — preserve audio timing

Voice track word timestamps, SSML, and chunk lineage remain upstream timing inputs. Speech anchors should resolve through the existing audio artifacts rather than guessed durations.

## 6. Proposed artifact lineage

The intended lineage for the new path is:

```text
research_packet
  + narrative_plan / script_visual_strategy
  + voice_track
        ↓
visual_intent
        ↓
visual_story
        ↓
visual_treatment
        ↓
visual_scene_graph
        ↓
visual_choreography (video-level, when available)
        ↓
render_spec
        ↓
video
```

Every downstream visual artifact should preserve parent artifact IDs and source references. The legacy composition plan may remain as a sibling compatibility branch during migration, not as a hidden prerequisite of the new scene graph.

## 7. Risks

| Risk | Why it matters | Mitigation |
|---|---|---|
| Two active architectures drift further | Developers may add the same concept to both paths | Treat this document as the reconciliation map; require migration status in changes |
| Factual values are invented during treatment/filling | Polished visuals can be factually wrong | Evidence references, deterministic derivation records, strict compiler validation |
| Composition names leak into new contracts | The new system becomes another template selector | Schema and prompt tests forbid renderer IDs in Story/Treatment |
| Arbitrary LLM layout | Scenes become fragile and untestable | Layout intents plus deterministic constraint solver |
| Persistent identity is lost at scene boundaries | State changes look like unrelated cards | Stable object IDs and world-state transition tests |
| Renderer becomes an editorial fallback | Missing data is hidden at the last layer | Compiler fails or emits explicit non-factual treatment; renderer never repairs |
| Existing components are duplicated | Maintenance and visual inconsistency increase | Capability registry and adapters around current modules |
| Choreography is added too early | Video-level policy masks weak scene contracts | Prove one scene/world vertical slice first |
| Audio and visual timing diverge | Transformations land away from spoken claims | Reuse `VoiceTrack` timestamps and test speech-anchor alignment |
| Dirty working tree is overwritten | Unrelated user work can be lost | This audit only adds docs; future changes must preserve unrelated modifications |

## 8. Recommended implementation order

1. Constitution and migration map — this audit.
2. Define versioned Visual Story, Visual Treatment, and Scene Graph contracts.
3. Build deterministic validation for object identity, evidence references, relationships, layout intents, and events.
4. Build a small layout/motion compiler with only the capabilities needed by the loan slice.
5. Add a scene-driven Remotion runtime path without changing the existing path.
6. Run the controlled loan example through the new path.
7. Compare old and new outputs for continuity, clarity, factual integrity, relationship visibility, repetition, and animation quality.
8. Add an adapter from selected existing composition capabilities into the scene compiler.
9. Add deterministic continuity/choreography rules, then the LLM Choreographer.
10. Expand visual vocabulary and migrate one grammar at a time.
11. Add visual memory and the video-level quality gate.
12. Retire legacy decision layers only after measured validation.

## 9. First vertical slice definition

The first slice is the loan transformation:

```text
₹50 lakh home loan
→ 8.5% interest rate
→ ₹43,391 EMI
→ rate transforms to 10.5%
→ EMI transforms to ₹49,919
→ additional monthly burden is emphasized
```

### Required inputs

- source-backed loan amount;
- source-backed baseline and higher rates;
- source-backed baseline and higher EMI values, or an explicitly declared deterministic calculation from source-backed inputs;
- narration or speech anchors for each reveal/change;
- one approved Visual Intent describing the causal meaning.

### Required scene behavior

- the loan document persists;
- the rate object persists and transforms;
- the EMI object persists and transforms;
- the rate-to-EMI relationship remains visible;
- the final burden is emphasized without changing the underlying facts;
- the compiler emits deterministic frame spans and renderer instructions;
- the output is comparable with an existing composition-path render.

### Out of scope for the first slice

- broad LLM Story/Treatment prompting;
- twenty new primitives;
- full video-level choreography;
- visual memory;
- replacing the current `RenderSpec` or `RenderEngine`;
- deleting or renaming existing compositions;
- changes to Research, Narrative, Script, publishing, or thumbnails.

## 10. Audit conclusion

The repository already contains valuable pieces: strong artifact lineage, semantic Visual Intent fields, voice timing, specialized visual modules, deterministic Remotion execution, and a large test surface. The main architectural change is not a wholesale renderer rewrite. It is moving creative responsibility from “select and fill a finished composition” to “describe, treat, and compile a persistent visual scene,” while preserving the working infrastructure underneath.

