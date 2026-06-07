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

Pipeline orchestration, engines, stage execution, script generation, semantic parsing, visual planning, and rendering logic are intentionally not implemented yet.
