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

Visual planning, timing, and rendering logic are intentionally not implemented yet.
