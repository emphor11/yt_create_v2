# YTCreate V2

YTCreate V2 is a greenfield, deterministic-first video pipeline.

Phase 0 established the runnable skeleton:

- FastAPI backend with `GET /health`
- React/Vite frontend shell
- Remotion renderer scaffold
- ownership documentation
- smoke tests

Phase 1 adds run-scoped artifact infrastructure:

- SQLite `projects`, `pipeline_runs`, and `artifacts`
- `ArtifactStore`
- project, run, artifact, parent, and child inspection APIs
- frontend project/run/artifact inspection shell

Phase 2 adds the first real pipeline artifact:

- `TopicRequest`
- `TopicRequestValidator`
- project creation with topic and angle
- automatic root TopicRequest artifact inside the deterministic run

Phase 3 adds the first deterministic stage:

- `ScriptBrief`
- `SceneFunction`
- `FinanceDomainRegistry`
- pure `ScriptBriefEngine`
- `ScriptBriefValidator`
- `PipelineService` support for `script_brief`
- `POST /projects/{project_id}/runs/{run_id}/run/script_brief`

Phase 4 adds explicit story progression:

- `NarrativeArc`
- `SceneArcStep`
- pure `NarrativeArcEngine`
- `NarrativeArcValidator`
- `PipelineService` support for `narrative_arc`
- `POST /projects/{project_id}/runs/{run_id}/run/narrative_arc`

Phase 5 adds deterministic narration drafting:

- `ScriptDraft`
- `DraftScene`
- pure `ScriptDraftEngine`
- `ScriptDraftValidator`
- `PipelineService` support for `script_draft`
- `POST /projects/{project_id}/runs/{run_id}/run/script_draft`

Phase 6 adds independent scene units:

- `SceneScript`
- `SceneStoryState`
- pure `SceneScriptEngine`
- `SceneScriptValidator`
- `PipelineService` support for `scene_script`
- `POST /projects/{project_id}/runs/{run_id}/run/scene_script`

Phase 7 adds semantic scene parsing:

- `SemanticScene`
- `SemanticEntity`
- `SemanticRelationship`
- deterministic INR parser and role assignment
- pure `SemanticSceneEngine`
- `SemanticSceneValidator`
- `PipelineService` support for `semantic_scene`
- `POST /projects/{project_id}/runs/{run_id}/run/semantic_scene`

Phase 8 adds visual event sequencing:

- `VisualEventSequence`
- `VisualEvent`
- pure `VisualEventSequenceEngine`
- `VisualEventSequenceValidator`
- semantic role to event primitive mapping
- `PipelineService` support for `visual_event_sequence`
- `POST /projects/{project_id}/runs/{run_id}/run/visual_event_sequence`

Phase 9 adds visual planning:

- `ComponentRegistry` with `SplitComparison`
- `VisualPlan`
- `SplitComparisonProps`
- pure `VisualPlanEngine`
- `VisualPlanValidator`
- component and prop mapping from semantic entities/events
- `PipelineService` support for `visual_plan`
- `POST /projects/{project_id}/runs/{run_id}/run/visual_plan`

Phase 10 adds visual timing:

- `TimedScenePlan`
- `TimedSpan`
- pure `TimingEngine`
- `TimedScenePlanValidator`
- fixed 8-second scene duration
- 30 FPS planning metadata
- one timed span per visual event
- `PipelineService` support for `timing`
- `POST /projects/{project_id}/runs/{run_id}/run/timing`

Phase 11 adds renderer instructions:

- `RenderSpec`
- `RenderFrameSpan`
- pure `RenderSpecEngine`
- `RenderSpecValidator`
- seconds-to-frames conversion
- composition copied from `VisualPlan`
- props copied from `VisualPlan`
- `PipelineService` support for `render_spec`
- `POST /projects/{project_id}/runs/{run_id}/run/render_spec`

Phase 12 adds video rendering:

- `Video`
- `RenderEngine`
- `VideoValidator`
- `RemotionProvider`
- `LocalMediaStorage`
- Remotion `SplitComparison`
- `scene_01.mp4` local render output
- storage-key based video artifacts
- media serving API
- frontend render output preview
- `PipelineService` support for `render`
- `POST /projects/{project_id}/runs/{run_id}/run/render`

Phase 13 adds MVP hardening:

- recursive artifact trace
- run validation summary
- descendant clearing for regeneration
- full monthly-payment golden pipeline tests
- video-to-semantic trace coverage
- frontend validation summary panel
- `GET /projects/{project_id}/runs/{run_id}/status`
- `GET /artifacts/{artifact_id}/trace`
- `POST /projects/{project_id}/runs/{run_id}/artifacts/{artifact_id}/regenerate-descendants`

Phase 14 foundation adds the first controlled AI boundary:

- `LLMProvider` interface
- structured JSON request and response objects
- provider/model metadata shape
- real `GeminiProvider` adapter
- `GEMINI_API_KEY` and `GEMINI_MODEL` environment wiring
- automatic `backend/.env` loading
- committed `backend/.env.example` template
- structured output requests to Gemini `generateContent`
- `deterministic` and `ai` run modes
- `ScriptBriefAIEngine` for AI-mode `script_brief`
- provider metadata stored inside AI-generated ScriptBrief artifacts
- AI-mode guards that keep later stages blocked until their AI engines exist

Real Gemini API calls are available when `GEMINI_API_KEY` is configured.

Voice, publishing, non-Gemini AI providers, and AI-backed stages after ScriptBrief are intentionally not implemented yet.
