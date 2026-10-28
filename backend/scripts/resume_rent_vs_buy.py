import os
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from dotenv import load_dotenv
load_dotenv(backend_dir / ".env", override=True)

# Test with gemini-3.5-flash-lite since gemini-3.6-flash has exceeded its 20 req/day free tier quota
os.environ["GEMINI_MODEL"] = "gemini-3.5-flash-lite"

from fastapi.testclient import TestClient
from app.main import create_app
from app.dependencies import get_llm_provider, get_artifact_store, get_media_storage

get_llm_provider.cache_clear()

PROJECT_ID = "project_5c945e6cd4544d46af772b6dfbe52d6e"
RUN_ID = "run_c4fbe4660a7a4fba98e6313de5ad45aa"

def main():
    print(f"Resuming Stage 7 for {PROJECT_ID} / {RUN_ID} using gemini-3.5-flash-lite...")
    app = create_app()
    client = TestClient(app)

    resp = client.post(f"/projects/{PROJECT_ID}/runs/{RUN_ID}/run/continuous_story")
    print("Status:", resp.status_code)
    if resp.status_code != 200:
        print("Error:", resp.text)
        return
    print("Stage 7 succeeded!")

    print("Now dispatching render...")
    render_resp = client.post(f"/projects/{PROJECT_ID}/runs/{RUN_ID}/run/render")
    print("Render Status:", render_resp.status_code)
    if render_resp.status_code != 200:
        print("Render Error:", render_resp.text)
        return
    print("Render succeeded!")

if __name__ == "__main__":
    main()
