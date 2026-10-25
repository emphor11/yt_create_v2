"""
resume_credit_card_trap_story.py — Resumes pipeline from continuous_story and render for the active Credit Card Trap run.
"""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from dotenv import load_dotenv
load_dotenv(backend_dir / ".env", override=True)

# Explicitly ensure gemini-3.6-flash is used for Stage 7
os.environ["GEMINI_MODEL"] = "gemini-3.6-flash"

from fastapi.testclient import TestClient
from app.main import create_app
from app.dependencies import get_artifact_store, get_media_storage, get_llm_provider

get_llm_provider.cache_clear()

PROJECT_ID = "project_fc2d43d32c754a10b1a1ec069f27f526"
RUN_ID = "run_ad5357234f144fb08d7f784801e3063d"

def main():
    print("=" * 75)
    print("RESUMING CREDIT CARD TRAP CONTINUOUS STORY PIPELINE (STAGE 7 & 8)")
    print(f"Project ID: {PROJECT_ID}")
    print(f"Run ID:     {RUN_ID}")
    print("=" * 75)

    llm = get_llm_provider()
    model_name = getattr(llm, "model", "N/A")
    print(f"[INIT] LLM Provider: {type(llm).__name__} (Model: {model_name})")

    app = create_app()
    client = TestClient(app)

    # 1. Check if Stage 7 (continuous_story_plan) already exists and is valid
    store = get_artifact_store()
    csp_art = store.find_artifact_by_type(PROJECT_ID, RUN_ID, "continuous_story_plan")
    if csp_art is not None and csp_art.status == "valid":
        print(f"\n[CACHE HIT] Valid continuous_story_plan already exists in store ({csp_art.id}). Skipping Stage 7 API call!")
        art_id = csp_art.id
        payload = csp_art.payload_json
        plan = payload.get("plan", {})
        objects = plan.get("objects", [])
        events = plan.get("events", [])
    else:
        print("\n---> Dispatching stage: 'continuous_story' with Gemini 3.6 Flash (Max 4 repair attempts)...")
        t0 = time.time()
        resp = client.post(f"/projects/{PROJECT_ID}/runs/{RUN_ID}/run/continuous_story")
        dt = time.time() - t0

        if resp.status_code != 200:
            print(f"[FAIL] Stage 'continuous_story' failed with status {resp.status_code} in {dt:.1f}s:")
            print(resp.text)
            sys.exit(1)

        data = resp.json()
        art = data.get("artifact", {})
        art_id = data.get("artifact_id")
        print(f"     [OK] Stage 'continuous_story' succeeded in {dt:.1f}s!")
        print(f"          Artifact ID:     {art_id}")
        print(f"          Artifact Status: {art.get('status')}")

        payload = art.get("payload_json", {})
        plan = payload.get("plan", {})
        objects = plan.get("objects", [])
        events = plan.get("events", [])
    print("\n     [CONTINUOUS STORY CHOREOGRAPHY]")
    print(f"     * Objects declared: {len(objects)}")
    for obj in objects:
        props = obj.get("cardProps") or obj.get("numberProps") or obj.get("textProps") or obj.get("connectorProps") or {}
        title = props.get("title") or props.get("label") or props.get("text") or obj.get("id")
        val = props.get("value")
        val_str = f" [Value: {val}]" if val is not None else ""
        print(f"       - [{obj.get('type'):<10}] ID: '{obj.get('id'):<22}' Layout: {obj.get('layout'):<14} '{title}'{val_str}")
    print(f"     * Choreographic events: {len(events)}")
    for ev in events[:8]:
        print(f"       - Action: {ev.get('action'):<18} Target: {ev.get('targetId'):<22} Frame: {ev.get('startFrame')} ('{ev.get('anchor')}')")
    if len(events) > 8:
        print(f"       ... and {len(events) - 8} more events")
    duration_s = (plan.get("durationInFrames", 0) / plan.get("fps", 30))
    print(f"     * Total Duration: {plan.get('durationInFrames')} frames @ {plan.get('fps')}fps ({duration_s:.1f}s)")

    # 2. Dispatch Stage 8: render
    print("\n---> Dispatching stage: 'render' (Remotion render to MP4 with Audio SFX Engine & Highlighter)...")
    t1 = time.time()
    resp_render = client.post(f"/projects/{PROJECT_ID}/runs/{RUN_ID}/run/render")
    dt1 = time.time() - t1

    if resp_render.status_code != 200:
        print(f"[FAIL] Stage 'render' failed with status {resp_render.status_code} in {dt1:.1f}s:")
        print(resp_render.text)
        sys.exit(1)

    r_data = resp_render.json()
    r_art = r_data.get("artifact", {})
    r_art_id = r_data.get("artifact_id")
    print(f"     [OK] Stage 'render' succeeded in {dt1:.1f}s!")
    print(f"          Artifact ID:     {r_art_id}")
    print(f"          Artifact Status: {r_art.get('status')}")

    # 3. Verify physical MP4 on disk
    store = get_artifact_store()
    media_storage = get_media_storage()
    video_art = store.find_artifact_by_type(PROJECT_ID, RUN_ID, "video")
    if video_art is None:
        print("[FAIL] Video artifact not found in store!")
        sys.exit(1)

    v_payload = video_art.payload_json
    storage_key = v_payload.get("storage_key")
    video_path = media_storage.path_for_key(storage_key)

    if not video_path.exists():
        print(f"[FAIL] Rendered video file does not exist at: {video_path}")
        sys.exit(1)

    file_size = video_path.stat().st_size
    print("\n" + "=" * 75)
    print("RESUMED PIPELINE RUN COMPLETED SUCCESSFULLY!")
    print("=" * 75)
    print(f"  * Physical File: {video_path}")
    print(f"  * File Size:     {file_size / (1024 * 1024):.2f} MB ({file_size:,} bytes)")
    print(f"  * Duration:      {v_payload.get('duration_frames')} frames @ {v_payload.get('fps')}fps ({(v_payload.get('duration_frames', 0) / v_payload.get('fps', 30)):.1f}s)")
    print("=" * 75)

    artifact_dir = Path("/Users/dakshyadav/.gemini/antigravity/brain/0ea3762c-60ae-40de-96c0-ce19c83dda9d")
    if artifact_dir.exists():
        dest = artifact_dir / "e2e_story.mp4"
        shutil.copy2(video_path, dest)
        print(f"  * Copied video to artifact directory: {dest}")
        dest_topic = artifact_dir / "credit_card_trap_story.mp4"
        shutil.copy2(video_path, dest_topic)
        print(f"  * Copied video to artifact directory: {dest_topic}")


if __name__ == "__main__":
    main()
