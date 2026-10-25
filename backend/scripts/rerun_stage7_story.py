"""
rerun_stage7_story.py — Rerun Stage 7 (continuous_story with Gemini 3.6 Flash) & Stage 8 (render) for an existing project.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import sys
import time

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from dotenv import load_dotenv
load_dotenv(backend_dir / ".env", override=True)

# Enforce Gemini 3.6 Flash for Stage 7 Continuous Story Choreography
os.environ["GEMINI_MODEL"] = "gemini-3.6-flash"

from fastapi.testclient import TestClient
from app.main import create_app
from app.dependencies import get_artifact_store, get_media_storage, get_llm_provider

get_llm_provider.cache_clear()


def rerun_stage7_and_render(project_id: str, run_id: str):
    print("=" * 75)
    print("RERUNNING STAGE 7 (CONTINUOUS STORY) & STAGE 8 (RENDER)")
    print(f"Project ID: {project_id}")
    print(f"Run ID:     {run_id}")
    print("=" * 75)

    llm = get_llm_provider()
    model_name = getattr(llm, "model", "N/A")
    print(f"[INIT] LLM Provider: {type(llm).__name__} (Model: {model_name})")

    app = create_app()
    client = TestClient(app)

    # Clean up existing continuous_story_plan and video artifacts to force fresh regeneration
    store = get_artifact_store()
    existing_story = store.find_artifact_by_type(project_id, run_id, "continuous_story_plan")
    existing_video = store.find_artifact_by_type(project_id, run_id, "video")
    ids_to_delete = []
    if existing_story:
        ids_to_delete.append(existing_story.id)
    if existing_video:
        ids_to_delete.append(existing_video.id)
    if ids_to_delete:
        store.delete_artifacts(ids_to_delete)
        print(f"[CLEANUP] Deleted existing artifacts to force re-run: {ids_to_delete}")

    # 1. Dispatch Stage 7: continuous_story
    print("\n---> Dispatching stage: 'continuous_story' with Gemini 3.6 Flash...")
    t0 = time.time()
    resp = client.post(f"/projects/{project_id}/runs/{run_id}/run/continuous_story")
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
        print(f"       - [{obj.get('type'):<10}] ID: '{obj.get('id'):<24}' Layout: {obj.get('layout'):<14} '{title}'{val_str}")
    print(f"     * Choreographic events: {len(events)}")
    for ev in events[:12]:
        print(f"       - Action: {ev.get('action'):<18} Target: {ev.get('targetId'):<24} Frame: {ev.get('startFrame')} ('{ev.get('anchor')}')")
    if len(events) > 12:
        print(f"       ... and {len(events) - 12} more events")
    duration_s = (plan.get("durationInFrames", 0) / plan.get("fps", 30))
    print(f"     * Total Duration: {plan.get('durationInFrames')} frames @ {plan.get('fps')}fps ({duration_s:.1f}s)")

    # 2. Dispatch Stage 8: render
    print("\n---> Dispatching stage: 'render' (Remotion render to MP4)...")
    t0 = time.time()
    render_resp = client.post(f"/projects/{project_id}/runs/{run_id}/run/render")
    dt = time.time() - t0

    if render_resp.status_code != 200:
        print(f"[FAIL] Stage 'render' failed with status {render_resp.status_code} in {dt:.1f}s:")
        print(render_resp.text)
        sys.exit(1)

    r_data = render_resp.json()
    r_art = r_data.get("artifact", {})
    print(f"     [OK] Stage 'render' succeeded in {dt:.1f}s!")
    print(f"          Artifact ID:     {r_data.get('artifact_id')}")
    print(f"          Artifact Status: {r_art.get('status')}")

    # 3. Verify MP4 video on disk
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
    print("\n" + "=" * 75)
    print("STAGE 7 & RENDER COMPLETED SUCCESSFULLY!")
    print("=" * 75)
    print(f"  * Physical File: {video_path}")
    print(f"  * File Size:     {file_size / (1024 * 1024):.2f} MB ({file_size:,} bytes)")
    print(f"  * Duration:      {v_payload.get('duration_frames')} frames @ {v_payload.get('fps')}fps ({(v_payload.get('duration_frames', 0) / v_payload.get('fps', 30)):.1f}s)")
    print("=" * 75)

    ws_dir = Path("/Users/dakshyadav/Documents/YTcreate_V2")
    slug = "the_mutual_fund_1_percent_expense_ratio_trap"
    ws_dest = ws_dir / f"{slug}.mp4"
    shutil.copy2(video_path, ws_dest)
    print(f"  * Copied video to workspace: {ws_dest}")

    artifact_dir = Path("/Users/dakshyadav/.gemini/antigravity/brain/0ea3762c-60ae-40de-96c0-ce19c83dda9d")
    if artifact_dir.exists():
        dest = artifact_dir / "e2e_story.mp4"
        shutil.copy2(video_path, dest)
        dest_topic = artifact_dir / f"{slug}.mp4"
        shutil.copy2(video_path, dest_topic)
        print(f"  * Copied video to artifact directory: {dest_topic}")

        # Write player HTML for this video
        player_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>The Mutual Fund 1% Expense Ratio Trap — Continuous Story Video Player</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0b1120; color: #f8fafc; margin: 0; padding: 32px 24px; display: flex; flex-direction: column; align-items: center; }}
    .container {{ max-width: 980px; width: 100%; }}
    h1 {{ font-size: 26px; font-weight: 700; margin: 0 0 8px; color: #38bdf8; }}
    p.subtitle {{ color: #94a3b8; font-size: 15px; margin: 0 0 20px; }}
    .video-wrapper {{ position: relative; width: 100%; background: #000; border-radius: 12px; overflow: hidden; box-shadow: 0 20px 40px rgba(0,0,0,0.6); border: 1px solid #1e293b; }}
    video {{ width: 100%; height: auto; display: block; }}
  </style>
</head>
<body>
  <div class="container">
    <h1>The Mutual Fund 1% Expense Ratio Trap</h1>
    <p class="subtitle">How an innocent-looking 1% fee difference between Regular and Direct plans quietly wipes out ₹45 Lakhs in retirement wealth over 25 years</p>
    <div class="video-wrapper">
      <video id="player" controls autoplay playsinline preload="auto">
        <source src="{slug}.mp4" type="video/mp4">
        Your browser does not support the video tag.
      </video>
    </div>
  </div>
</body>
</html>"""
        player_path = artifact_dir / f"{slug}_player.html"
        player_path.write_text(player_html, encoding="utf-8")
        print(f"  * Created interactive player: {player_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rerun Stage 7 & 8 for an existing run.")
    parser.add_argument("--project-id", default="project_427bc84c7e864f34a523fe9229bd8285", help="Project ID")
    parser.add_argument("--run-id", default="run_407e6bdc0bd048b4a461e9df5b49571f", help="Run ID")
    args = parser.parse_args()

    rerun_stage7_and_render(args.project_id, args.run_id)
