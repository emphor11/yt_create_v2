"""
run_fastapi_continuous_story_verification.py — Full Pipeline Integration Verification.

Executes a real request through the FastAPI HTTP entry point:
POST /projects (visual_mode="continuous_story")
-> POST /projects/{project_id}/runs/{run_id}/run/research
-> POST /projects/{project_id}/runs/{run_id}/run/narrative_plan
-> POST /projects/{project_id}/runs/{run_id}/run/hook
-> POST /projects/{project_id}/runs/{run_id}/run/script_visual_strategy
-> POST /projects/{project_id}/runs/{run_id}/run/quality_review
-> POST /projects/{project_id}/runs/{run_id}/run/voice_generation
-> POST /projects/{project_id}/runs/{run_id}/run/continuous_story (Gemini draft, atomic compile, zone validation)
-> POST /projects/{project_id}/runs/{run_id}/run/render (Remotion render to MP4)
-> GET /projects/{project_id}/runs/{run_id}/status
-> Verify final MP4 artifact exists on disk
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys
import time

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from dotenv import load_dotenv
load_dotenv(backend_dir / ".env")

from fastapi.testclient import TestClient
from app.main import create_app
from app.dependencies import get_artifact_store, get_media_storage, get_llm_provider
from domain.continuous_story_plan import ContinuousStoryPlanArtifact


def run_integration_verification():
    print("=" * 70)
    print("FASTAPI PIPELINE INTEGRATION VERIFICATION: CONTINUOUS STORY MODE")
    print("=" * 70)

    # 1. Verify Environment & Providers
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        print("[FAIL] GEMINI_API_KEY is not set.")
        sys.exit(1)

    llm = get_llm_provider()
    print(f"[INIT] LLM Provider: {type(llm).__name__} (Model: {getattr(llm, 'model', 'N/A')})")

    # 2. Initialize FastAPI Client
    app = create_app()
    client = TestClient(app)
    print("[INIT] Initialized FastAPI TestClient on app routes.")

    topic = "The real cost of a home loan rate hike"
    print(f"\n[STEP 1] Creating project via FastAPI POST /projects...")
    create_resp = client.post(
        "/projects",
        json={
            "topic": topic,
            "visual_mode": "continuous_story",
            "audience": "Indian working professionals taking a home loan",
            "language": "English",
            "style": "clear, metrics-driven, visual YouTube storytelling",
            "channel": "MindshiftFinance",
        },
    )
    if create_resp.status_code != 200:
        print(f"[FAIL] POST /projects failed: {create_resp.status_code} {create_resp.text}")
        sys.exit(1)

    project_data = create_resp.json()
    project_id = project_data["project"]["id"]
    run_id = project_data["run"]["id"]
    print(f"         Project ID: {project_id}")
    print(f"         Run ID:     {run_id}")
    print(f"         Mode:       continuous_story")

    # 3. Pipeline Stages
    stages = [
        ("research", "ResearchPacket"),
        ("narrative_plan", "NarrativePlan"),
        ("hook", "Hook"),
        ("script_visual_strategy", "ScriptVisualStrategy"),
        ("quality_review", "ReviewResult"),
        ("voice_generation", "VoiceTrack"),
        ("continuous_story", "ContinuousStoryPlanArtifact"),
        ("render", "Video"),
    ]

    print("\n[STEP 2] Sequentially dispatching pipeline stages via FastAPI POST /run/{stage}...")
    for stage_name, expected_artifact in stages:
        t0 = time.time()
        print(f"\n---> Dispatching stage: '{stage_name}' (expected: {expected_artifact})...")
        resp = client.post(f"/projects/{project_id}/runs/{run_id}/run/{stage_name}")
        dt = time.time() - t0

        if resp.status_code != 200:
            print(f"[FAIL] Stage '{stage_name}' failed with status {resp.status_code} in {dt:.1f}s:")
            print(resp.text)
            sys.exit(1)

        data = resp.json()
        art_id = data.get("artifact_id")
        art = data.get("artifact", {})
        status = art.get("status")
        art_type = art.get("artifact_type")
        val = data.get("validation", {})
        errors = val.get("errors", [])
        warnings = val.get("warnings", [])

        print(f"     [OK] Stage '{stage_name}' succeeded in {dt:.1f}s!")
        print(f"          Artifact ID:     {art_id}")
        print(f"          Artifact Type:   {art_type}")
        print(f"          Artifact Status: {status}")
        if errors:
            print(f"          Errors:          {errors}")
        if warnings:
            print(f"          Warnings:        {warnings}")

        # Deep inspection for continuous_story
        if stage_name == "continuous_story":
            payload = art.get("payload_json", {})
            plan = payload.get("plan", {})
            draft = payload.get("draft", {})
            objects = plan.get("objects", [])
            events = plan.get("events", [])
            print("\n     [CONTINUOUS STORY INSPECTION]")
            print(f"     * Raw AI Draft objects: {len(draft.get('objects', []))}, events: {len(draft.get('events', []))}")
            print(f"     * Compiled Remotion plan objects: {len(objects)}, events: {len(events)}")
            print(f"     * Duration: {plan.get('durationInFrames')} frames @ {plan.get('fps')}fps ({(plan.get('durationInFrames', 0) / plan.get('fps', 30)):.1f}s)")
            print(f"     * Safe layout zones used: {[o.get('layout') for o in objects if 'layout' in o]}")

    # 4. Check Pipeline Status via FastAPI GET /status
    print("\n[STEP 3] Checking complete pipeline run status via FastAPI GET /status...")
    status_resp = client.get(f"/projects/{project_id}/runs/{run_id}/status")
    if status_resp.status_code != 200:
        print(f"[FAIL] GET /status failed: {status_resp.status_code} {status_resp.text}")
        sys.exit(1)

    status_data = status_resp.json()
    print("\n--- Pipeline Stages Summary ---")
    for s in status_data.get("stages", []):
        st_name = s.get("stage")
        st_status = s.get("status")
        art_type = s.get("artifact_type")
        print(f"  * {st_name:<24} [{st_status:<8}] ({art_type})")

    # 5. Verify Final MP4 Artifact
    print("\n[STEP 4] Verifying final physical MP4 video artifact on disk...")
    store = get_artifact_store()
    media_storage = get_media_storage()

    video_art = store.find_artifact_by_type(project_id, run_id, "video")
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
    if file_size <= 0:
        print(f"[FAIL] Rendered video file is 0 bytes at: {video_path}")
        sys.exit(1)

    print(f"  * Artifact ID:   {video_art.id}")
    print(f"  * Storage Key:   {storage_key}")
    print(f"  * Physical File: {video_path}")
    print(f"  * File Size:     {file_size / (1024 * 1024):.2f} MB ({file_size} bytes)")
    print(f"  * Render Status: {v_payload.get('render_status')}")
    print(f"  * Scene ID:      {v_payload.get('scene_id')}")
    print(f"  * FPS:           {v_payload.get('fps')}")
    print(f"  * Frames:        {v_payload.get('duration_frames')}")

    print("\n" + "=" * 70)
    print("ALL PIPELINE INTEGRATION VERIFICATIONS PASSED CLEANLY!")
    print("=" * 70)


if __name__ == "__main__":
    run_integration_verification()
