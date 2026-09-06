import os
import sys
import json
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

    print(f"=== Running youtube_metadata for {run_id} ===")
    metadata_artifact = pipeline_service.run_stage("youtube_metadata", project_id, run_id)
    print("youtube_metadata succeeded! ID:", metadata_artifact.id)
    print("Title:", metadata_artifact.payload_json.get("title"))
    print("Thumbnail concept:", metadata_artifact.payload_json.get("thumbnail_concept"))

    print(f"\n=== Running AI thumbnail generation for {run_id} ===")
    thumb_artifact = pipeline_service.run_stage("thumbnail", project_id, run_id)
    print("thumbnail stage succeeded! ID:", thumb_artifact.id)
    print("Thumbnail payload:")
    print(json.dumps(thumb_artifact.payload_json, indent=2))

    storage_key = thumb_artifact.payload_json.get("storage_key")
    from providers.media_storage import LocalMediaStorage
    repo_root = Path(__file__).resolve().parents[2]
    media_storage = LocalMediaStorage(repo_root / "backend" / ".data" / "media")
    full_path = media_storage.path_for_key(storage_key)
    print(f"\nFull thumbnail path: {full_path}")
    if full_path.exists():
        print(f"File exists! Size: {full_path.stat().st_size} bytes")
        from PIL import Image
        img = Image.open(full_path)
        print(f"Verified Image: format={img.format}, size={img.size}")
    else:
        print("ERROR: File does not exist!")

if __name__ == "__main__":
    main()
