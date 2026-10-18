"""Run one real topic through the continuous-story production path.

This intentionally uses the existing PipelineService stages.  It is not a
second pipeline and it does not use the loan fixture or a precompiled plan.
"""
from __future__ import annotations

import sys
import uuid
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.pipeline_service import build_pipeline_service
from artifact_store.sqlite_store import ArtifactStore
from domain.generate_video_request import GenerateVideoRequest, VisualMode
from domain.validation import ValidationResult
from providers.media_storage import LocalMediaStorage
from app.dependencies import get_llm_provider


def run(topic: str) -> None:
    repo_root = backend_dir.parent
    run_token = uuid.uuid4().hex[:10]
    db_path = backend_dir / ".data" / f"continuous_story_e2e_{run_token}.db"
    media_root = backend_dir / ".data" / "media"
    store = ArtifactStore(db_path)
    store.initialize()
    media_storage = LocalMediaStorage(media_root)
    llm_provider = get_llm_provider()
    if llm_provider is None:
        raise RuntimeError("No LLM provider configured. Set GEMINI_API_KEY/GEMINI_MODEL in backend/.env.")

    project = store.create_project(f"Continuous Story E2E: {topic}")
    run_record = store.create_run(project.id, mode="ai")
    request_model = GenerateVideoRequest(
        topic=topic,
        audience="Indian working professionals learning personal finance",
        language="English",
        style="clear, visual, explanatory YouTube storytelling",
        channel="YTCreate",
        visual_mode=VisualMode.CONTINUOUS_STORY,
    )
    store.save_artifact(
        project_id=project.id,
        run_id=run_record.id,
        artifact_type="generate_video_request",
        schema_version=request_model.schema_version,
        payload_json=request_model.model_dump(mode="json"),
        parent_artifact_roles_json={},
        validation_json=ValidationResult(status="valid"),
    )

    service = build_pipeline_service(
        store,
        llm_provider=llm_provider,
        media_storage=media_storage,
    )
    stages = [
        "research",
        "narrative_plan",
        "hook",
        "script_visual_strategy",
        "quality_review",
        "voice_generation",
        "continuous_story",
        "render",
    ]
    print(f"Project: {project.id}")
    print(f"Run:     {run_record.id}")
    print(f"Topic:   {topic}")
    print("Mode:    continuous_story")
    for stage in stages:
        print(f"\n[{stage}] running...")
        artifact = service.run_stage(stage, project.id, run_record.id)
        print(f"[{stage}] {artifact.status} ({artifact.artifact_type})")

    print("\n--- final pipeline status ---")
    statuses = service.get_run_status(project.id, run_record.id)
    for item in statuses:
        if item["stage"] in {
            "research", "narrative_plan", "hook", "script_visual_strategy",
            "quality_review", "voice_generation", "continuous_story",
            "video_assembly", "render",
        }:
            print(f"{item['stage']:<24} {item['status']}")

    video = store.find_artifact_by_type(project.id, run_record.id, "video")
    if video is None:
        raise RuntimeError("E2E run completed without a video artifact.")
    video_payload = video.payload_json
    video_path = media_storage.path_for_key(video_payload["storage_key"])
    print("\n--- final video ---")
    print(f"Artifact: {video.id}")
    print(f"Path:    {video_path}")
    print(f"Bytes:   {video_path.stat().st_size}")
    print("\nE2E CONTINUOUS STORY RUN PASSED")


if __name__ == "__main__":
    run("The real cost of a home loan rate hike")
