import os
import sys
import json
import subprocess
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(backend_dir))

from app.dependencies import get_pipeline_service, get_artifact_store, _load_backend_dotenv

def main():
    _load_backend_dotenv()
    pipeline_service = get_pipeline_service()
    store = get_artifact_store()

    project_id = "project_da21bec1f4544c8fa3df811cf90a4cd9"
    run_id = "run_406fed4d7e0140c89e8cfd260b792472"
    voice_track_id = "artifact_aa6162555b784466824495c671ddffe4"

    print(f"=== Regenerating descendants of voice_track for run {run_id} ===")
    deleted, next_stage = pipeline_service.regenerate_descendants(project_id, run_id, voice_track_id)
    print(f"Deleted {len(deleted)} artifacts: {[a.artifact_type for a in deleted]}")
    print(f"Next stage: {next_stage}")

    print("\n=== Running video_assembly ===")
    assembly_artifact = pipeline_service.run_stage("video_assembly", project_id, run_id)
    print(f"video_assembly completed! Artifact ID: {assembly_artifact.id}")

    payload = assembly_artifact.payload_json
    scenes = payload.get("props", {}).get("scenes", [])
    print(f"Total scenes: {len(scenes)}")
    for idx, sc in enumerate(scenes):
        asset = sc.get("asset")
        asset_info = f"asset_id={asset.get('asset_id')}, path={asset.get('local_path')}" if asset else "None"
        print(f"  Scene {idx+1} ({sc.get('scene_id')}): comp={sc.get('component', {}).get('component_id')} frames={sc.get('duration_frames')}, asset: {asset_info}")

    print("\n=== Running render ===")
    render_artifact = pipeline_service.run_stage("render", project_id, run_id)
    print(f"render completed! Artifact ID: {render_artifact.id}")
    video_path = render_artifact.payload_json.get("local_path")
    print(f"Rendered video path: {video_path}")

    if video_path and Path(video_path).exists():
        print(f"Video file exists! Size: {Path(video_path).stat().st_size / (1024*1024):.2f} MB")
    else:
        print(f"Payload json: {render_artifact.payload_json}")

if __name__ == "__main__":
    main()
