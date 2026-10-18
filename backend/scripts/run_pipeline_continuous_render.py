"""
run_pipeline_continuous_render.py — Phase 2 Verification Script.

Executes a real end-to-end render stage through PipelineService & RenderHandler
in continuous_story mode:
1. Sets up real ArtifactStore with visual_mode="continuous_story"
2. Loads the validated & compiled loan StoryPlan
3. Stores real narration audio in LocalMediaStorage
4. Runs PipelineService.run_stage("render", project_id, run_id)
5. Verifies physical MP4 output, Video artifact, and status reporting
"""
import json
from pathlib import Path
import sys

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from artifact_store.sqlite_store import ArtifactStore
from domain.generate_video_request import GenerateVideoRequest, VisualMode
from domain.continuous_story_plan import ContinuousStoryPlanArtifact
from domain.validation import ValidationResult
from app.pipeline_service import build_pipeline_service
from providers.media_storage import LocalMediaStorage


def run_verification():
    print("=" * 65)
    print("PHASE 2: REAL PIPELINE RENDER STAGE VERIFICATION")
    print("=" * 65)

    repo_root = backend_dir.parent
    db_path = backend_dir / ".data" / "phase2_render_verification.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()

    store = ArtifactStore(db_path)
    store.initialize()

    media_storage = LocalMediaStorage(backend_dir / ".data" / "media")
    project = store.create_project("Phase 2 Continuous Story Render")
    run = store.create_run(project.id)
    project_id, run_id = project.id, run.id
    print(f"[1/5] Initialized project '{project_id}', run '{run_id}'.")

    # 1. Save GenerateVideoRequest with visual_mode=continuous_story
    gen_req = GenerateVideoRequest(
        topic="Home Loan Rate Hike Impact",
        visual_mode=VisualMode.CONTINUOUS_STORY,
    )
    store.save_artifact(
        project_id=project_id,
        run_id=run_id,
        artifact_type="generate_video_request",
        schema_version=gen_req.schema_version,
        payload_json=gen_req.model_dump(),
        parent_artifact_roles_json={},
        validation_json=ValidationResult(status="valid"),
    )
    print("[2/5] Saved generate_video_request (visual_mode='continuous_story').")

    # 2. Setup real narration audio in media storage
    audio_source = repo_root / "renderer" / "remotion" / "public" / "loan_narration.mp3"
    if not audio_source.exists():
        raise FileNotFoundError(f"Audio source not found: {audio_source}")

    audio_storage_key = f"projects/{project_id}/runs/{run_id}/loan_narration.mp3"
    audio_dest = media_storage.ensure_parent(audio_storage_key)
    audio_dest.write_bytes(audio_source.read_bytes())
    print(f"[3/5] Stored real narration audio in media storage ({len(audio_dest.read_bytes()) / 1024:.1f} KB).")

    # 3. Load compiled StoryPlan from Checkpoint 2
    plan_path = repo_root / "output" / "gemini_compiled_loan_plan.json"
    with open(plan_path, "r", encoding="utf-8") as f:
        compiled_plan = json.load(f)

    csp = ContinuousStoryPlanArtifact.from_compiled_plan(
        plan=compiled_plan,
        audio_storage_key=audio_storage_key,
    )
    store.save_artifact(
        project_id=project_id,
        run_id=run_id,
        artifact_type="continuous_story_plan",
        schema_version=csp.schema_version,
        payload_json=csp.model_dump(),
        parent_artifact_roles_json={},
        validation_json=ValidationResult(status="valid"),
    )
    print(f"[4/5] Saved continuous_story_plan artifact ({csp.duration_in_frames} frames / {csp.duration_in_frames / csp.fps:.1f}s).")

    # 4. Execute render stage via PipelineService
    print("[5/5] Executing render stage through PipelineService...")
    service = build_pipeline_service(store, media_storage=media_storage)
    video_record = service.run_stage("render", project_id, run_id)

    print("\n" + "=" * 65)
    print("RENDER STAGE VERIFICATION RESULTS")
    print("=" * 65)
    print(f"Artifact Type:    {video_record.artifact_type}")
    print(f"Artifact Status:  {video_record.status}")
    print(f"Parent Roles:     {video_record.parent_artifact_roles_json}")
    
    payload = video_record.payload_json
    print(f"Render Status:    {payload.get('render_status')}")
    print(f"File Name:        {payload.get('file_name')}")
    print(f"Storage Key:      {payload.get('storage_key')}")
    print(f"FPS:              {payload.get('fps')}")
    print(f"Duration Frames:  {payload.get('duration_frames')} ({payload.get('duration_frames') / payload.get('fps'):.1f}s)")
    print(f"Size:             {payload.get('size_bytes') / (1024 * 1024):.2f} MB")

    output_video_path = media_storage.path_for_key(payload["storage_key"])
    assert output_video_path.exists(), f"Rendered video does not exist: {output_video_path}"
    assert output_video_path.stat().st_size > 0, "Rendered video file is empty!"
    print(f"Physical MP4:     {output_video_path} (EXISTS & VALID)")

    # 5. Check run status reporting
    print("\n--- Pipeline Run Status Summary ---")
    status_list = service.get_run_status(project_id, run_id)
    for s in status_list:
        if s["stage"] in ("voice_generation", "continuous_story", "video_assembly", "render"):
            print(f"  * {s['stage']:<20}: {s['status']}")

    status_by_stage = {s["stage"]: s["status"] for s in status_list}
    assert status_by_stage["continuous_story"] == "valid", "continuous_story should be valid"
    assert status_by_stage["video_assembly"] == "skipped", "video_assembly must be skipped in continuous mode!"
    assert status_by_stage["render"] == "valid", "render must be valid"

    print("\n✓ ALL PHASE 2 VERIFICATIONS PASSED!")


if __name__ == "__main__":
    run_verification()
