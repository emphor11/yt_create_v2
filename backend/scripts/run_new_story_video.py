"""
run_new_story_video.py — End-to-End Pipeline Execution for a New Story Topic.

Runs a real request through the FastAPI HTTP entry point:
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

import argparse
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


def run_pipeline_for_topic(topic: str, angle: str, audience: str, channel: str, delay_seconds: float = 14.0):
    print("=" * 75)
    print(f"EXECUTING CONTINUOUS STORY PIPELINE: {topic}")
    print(f"Angle: {angle}")
    print("=" * 75)

    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        print("[FAIL] GEMINI_API_KEY is not set.")
        sys.exit(1)

    llm = get_llm_provider()
    print(f"[INIT] LLM Provider: {type(llm).__name__} (Model: {getattr(llm, 'model', 'N/A')})")

    app = create_app()
    client = TestClient(app)
    print("[INIT] Initialized FastAPI TestClient on app routes.")

    print(f"\n[STEP 1] Creating project via FastAPI POST /projects...")
    create_resp = client.post(
        "/projects",
        json={
            "topic": topic,
            "angle": angle,
            "visual_mode": "continuous_story",
            "audience": audience,
            "language": "English",
            "style": "clear, metrics-driven, high-retention visual YouTube storytelling",
            "channel": channel,
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

        if stage_name == "continuous_story":
            payload = art.get("payload_json", {})
            plan = payload.get("plan", {})
            draft = payload.get("draft", {})
            objects = plan.get("objects", [])
            events = plan.get("events", [])
            print("\n     [CONTINUOUS STORY CHOREOGRAPHY]")
            print(f"     * Objects declared: {len(objects)}")
            for obj in objects:
                props = obj.get("cardProps") or obj.get("numberProps") or obj.get("textProps") or obj.get("connectorProps") or {}
                title = props.get("title") or props.get("label") or props.get("text") or obj.get("id")
                val = props.get("value")
                val_str = f" [Value: {val}]" if val is not None else ""
                print(f"       - [{obj.get('type'):<10}] ID: '{obj.get('id'):<20}' Layout: {obj.get('layout'):<14} '{title}'{val_str}")
            print(f"     * Choreographic events: {len(events)}")
            for ev in events[:6]:
                print(f"       - Action: {ev.get('action'):<18} Target: {ev.get('targetId'):<20} Frame: {ev.get('startFrame')} ('{ev.get('anchor')}')")
            if len(events) > 6:
                print(f"       ... and {len(events) - 6} more events")
            duration_s = (plan.get("durationInFrames", 0) / plan.get("fps", 30))
            print(f"     * Total Duration: {plan.get('durationInFrames')} frames @ {plan.get('fps')}fps ({duration_s:.1f}s)")

        if delay_seconds > 0 and stage_name != stages[-1][0]:
            print(f"     [PACING] Waiting {delay_seconds:.1f}s to strictly respect Gemini rate limits...")
            time.sleep(delay_seconds)

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

    print("\n" + "=" * 75)
    print("NEW VIDEO GENERATION COMPLETED SUCCESSFULLY!")
    print("=" * 75)
    print(f"  * Project ID:    {project_id}")
    print(f"  * Run ID:        {run_id}")
    print(f"  * Topic:         {topic}")
    print(f"  * Artifact ID:   {video_art.id}")
    print(f"  * Storage Key:   {storage_key}")
    print(f"  * Physical File: {video_path}")
    print(f"  * File Size:     {file_size / (1024 * 1024):.2f} MB ({file_size:,} bytes)")
    print(f"  * Render Status: {v_payload.get('render_status')}")
    print(f"  * Duration:      {v_payload.get('duration_frames')} frames @ {v_payload.get('fps')}fps ({(v_payload.get('duration_frames', 0) / v_payload.get('fps', 30)):.1f}s)")
    print("=" * 75)

    artifact_dir = Path("/Users/dakshyadav/.gemini/antigravity/brain/0ea3762c-60ae-40de-96c0-ce19c83dda9d")
    if artifact_dir.exists():
        import shutil
        dest = artifact_dir / "e2e_story.mp4"
        shutil.copy2(video_path, dest)
        print(f"  * Copied video to artifact directory: {dest}")
        dest_cc = artifact_dir / "e2e_credit_card_trap_story.mp4"
        shutil.copy2(video_path, dest_cc)
        print(f"  * Copied video to artifact directory: {dest_cc}")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run full continuous story pipeline for a new topic.")
    parser.add_argument("--topic", default="The Credit Card Minimum Payment Trap", help="Video topic")
    parser.add_argument("--angle", default="How paying only the 5% minimum balance turns a ₹1,00,000 purchase into an 18-year debt spiral costing over ₹3,00,000", help="Video angle")
    parser.add_argument("--audience", default="Young urban cardholders and professionals", help="Target audience")
    parser.add_argument("--channel", default="FinWise India", help="Channel brand name")
    parser.add_argument("--delay", type=float, default=14.0, help="Pacing delay in seconds between stages to respect rate limits")
    args = parser.parse_args()

    run_pipeline_for_topic(
        topic=args.topic,
        angle=args.angle,
        audience=args.audience,
        channel=args.channel,
        delay_seconds=args.delay,
    )
