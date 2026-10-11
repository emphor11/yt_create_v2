import sys
import time
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parents[1]
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.dependencies import get_pipeline_service

def main():
    project_id = "project_71e74f156f8c4856bc5614257aca5b63"
    run_id = "run_76264dca8de2424ebb1f7d35c66d2e57"
    
    print(f"=== Starting Render Stage for {project_id} / {run_id} ===", flush=True)
    t0 = time.time()
    
    pipeline_service = get_pipeline_service()
    
    # Run the render stage
    artifact = pipeline_service.run_stage("render", project_id=project_id, run_id=run_id)
    
    elapsed = time.time() - t0
    print(f"\n=== Render Stage Completed in {elapsed:.1f}s ({elapsed/60:.2f} mins) ===", flush=True)
    print(f"Video Artifact ID: {artifact.id}", flush=True)
    print(f"Status: {artifact.status}", flush=True)
    print(f"Payload: {artifact.payload_json}", flush=True)

if __name__ == "__main__":
    main()
