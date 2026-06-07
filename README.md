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

Pipeline orchestration, engines, validators, stage execution, TopicRequest, and rendering logic are intentionally not implemented yet.
