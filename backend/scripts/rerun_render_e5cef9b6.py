import os
import sys
import time
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(backend_dir))

from app.dependencies import get_pipeline_service, get_artifact_store, _load_backend_dotenv

def main():
    _load_backend_dotenv()
    pipeline_service = get_pipeline_service()
    store = get_artifact_store()

    project_id = "project_69a8fb52d16744b4816dae34273f4d4c"
    run_id = "run_e5cef9b619854a6d863d6e7c96565a83"

    print(f"==================================================")
    print(f"RE-RENDERING EXACT RUN: {run_id}")
    print(f"Project: {project_id}")
    print(f"==================================================")

    # Check render_spec
    render_spec_art = store.find_artifact_by_type(project_id, run_id, "render_spec")
    if not render_spec_art:
        print("ERROR: render_spec artifact not found!")
        sys.exit(1)

    payload = render_spec_art.payload_json
    duration_frames = payload.get("duration_frames")
    fps = payload.get("fps")
    scenes = payload.get("props", {}).get("scenes", [])
    print(f"Render Spec ID: {render_spec_art.id}")
    print(f"Total Duration: {duration_frames} frames ({duration_frames / fps:.2f}s @ {fps}fps)")
    print(f"Total Scenes: {len(scenes)}")

    # Check Scene 5 specifically
    if len(scenes) >= 5:
        sc5 = scenes[4]
        print(f"Scene 5: id={sc5.get('scene_id')}, frames={sc5.get('duration_frames')}, comp={sc5.get('component', {}).get('component_id')}")

    print("\nStarting render stage execution...")
    t0 = time.time()
    video_artifact = pipeline_service.run_stage("render", project_id, run_id)
    elapsed = time.time() - t0

    print(f"\nRender completed in {elapsed:.1f}s!")
    print(f"Video Artifact ID: {video_artifact.id}")
    print(f"Status: {video_artifact.status}")
    print(f"Validation: {video_artifact.validation_json}")

    video_payload = video_artifact.payload_json
    print(f"Render Status: {video_payload.get('render_status')}")
    print(f"Output File: {video_payload.get('file_name')}")
    print(f"Duration Frames: {video_payload.get('duration_frames')}")
    print(f"Size Bytes: {video_payload.get('size_bytes')}")
    if video_payload.get("error_message"):
        print(f"Error Message: {video_payload.get('error_message')}")

    storage_key = video_payload.get("storage_key")
    if storage_key:
        from app.dependencies import get_media_storage
        media_storage = get_media_storage()
        full_path = media_storage.resolve_path(storage_key)
        print(f"Video Local Path: {full_path}")
        if full_path.exists():
            mb = full_path.stat().st_size / (1024 * 1024)
            print(f"SUCCESS: Video file exists on disk! Size: {mb:.2f} MB")
        else:
            print("WARNING: Video file does not exist at local path.")

if __name__ == "__main__":
    main()
