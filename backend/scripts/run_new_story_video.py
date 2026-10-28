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
    os.environ["GEMINI_MODEL"] = "gemini-3.5-flash-lite"
    get_llm_provider.cache_clear()

    for stage_name, expected_artifact in stages:
        if stage_name == "continuous_story":
            os.environ["GEMINI_MODEL"] = "gemini-3.6-flash"
            get_llm_provider.cache_clear()
            print("     [MODEL ROUTING] Switched to gemini-3.6-flash for Continuous Story Choreography.")

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
    import shutil
    slug = "".join(c if c.isalnum() else "_" for c in topic.lower()).strip("_")[:28]
    ws_dest = Path("/Users/dakshyadav/Documents/YTcreate_V2") / f"{slug}.mp4"
    shutil.copy2(video_path, ws_dest)
    print(f"  * Copied video to workspace: {ws_dest}")

    if artifact_dir.exists():
        dest = artifact_dir / "e2e_story.mp4"
        shutil.copy2(video_path, dest)
        print(f"  * Copied video to artifact directory: {dest}")
        dest_topic = artifact_dir / f"{slug}.mp4"
        shutil.copy2(video_path, dest_topic)
        print(f"  * Copied video to artifact directory: {dest_topic}")

        # Extract choreographic highlights for player
        scenes_cards_html = ""
        csp_art = store.find_artifact_by_type(project_id, run_id, "continuous_story_plan")
        if csp_art:
            csp_plan = csp_art.payload_json.get("plan", {})
            objs_by_id = {o.get("id"): o for o in csp_plan.get("objects", [])}
            fps = csp_plan.get("fps", 30)
            seen_targets = set()
            for ev in csp_plan.get("events", []):
                target_id = ev.get("targetId")
                action = ev.get("action")
                if action in ("enter", "highlight", "transform_number") and target_id not in seen_targets:
                    seen_targets.add(target_id)
                    obj = objs_by_id.get(target_id, {})
                    obj_type = obj.get("type", "element")
                    layout = obj.get("layout", "center")
                    props = obj.get("cardProps") or obj.get("numberProps") or obj.get("textProps") or obj.get("chartProps") or obj.get("imageProps") or {}
                    title = props.get("title") or props.get("label") or props.get("text") or target_id
                    frame = ev.get("startFrame", 0)
                    sec = frame / fps
                    mm = int(sec // 60)
                    ss = int(sec % 60)
                    badge_class = "badge-hero" if layout == "center" else ("badge-split" if "split" in layout else "badge-compress")
                    scenes_cards_html += f"""
        <div class="scene-card" onclick="seek({sec:.1f})">
          <span class="time">{mm:02d}:{ss:02d}</span>
          <span class="title">[{obj_type.upper()}] {title[:32]}</span>
          <span class="desc">Layout: {layout} &bull; Action: {action}</span>
          <span class="badge {badge_class}">{layout}</span>
        </div>"""
                    if len(seen_targets) >= 8:
                        break

        # Write player HTML for this new video
        player_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{topic} — Living Canvas Video</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background: #0f1110;
      color: #f7f4ee;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      padding: 32px 20px;
      display: flex;
      flex-direction: column;
      align-items: center;
    }}
    .header {{
      text-align: center;
      margin-bottom: 24px;
      max-width: 900px;
    }}
    .header h1 {{
      font-size: 26px;
      font-weight: 700;
      color: #38bdf8;
      margin-bottom: 8px;
      letter-spacing: -0.02em;
    }}
    .header p {{
      font-size: 14px;
      color: #a1a1aa;
      line-height: 1.5;
    }}
    .player-container {{
      width: 100%;
      max-width: 1080px;
      background: #181b19;
      border: 1px solid #272a27;
      border-radius: 14px;
      padding: 16px;
      box-shadow: 0 20px 40px rgba(0,0,0,0.5);
    }}
    video {{
      width: 100%;
      border-radius: 8px;
      display: block;
      background: #000;
      aspect-ratio: 16 / 9;
    }}
    .scenes-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
      gap: 12px;
      margin-top: 20px;
    }}
    .scene-card {{
      background: #202421;
      border: 1px solid #2f3430;
      border-radius: 8px;
      padding: 12px 14px;
      cursor: pointer;
      transition: all 0.2s ease;
      display: flex;
      flex-direction: column;
      gap: 4px;
    }}
    .scene-card:hover {{
      background: #282d29;
      border-color: #38bdf8;
      transform: translateY(-2px);
    }}
    .scene-card .time {{
      font-family: monospace;
      font-size: 12px;
      font-weight: 700;
      color: #38bdf8;
    }}
    .scene-card .title {{
      font-size: 13px;
      font-weight: 600;
      color: #f7f4ee;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}
    .scene-card .desc {{
      font-size: 11px;
      color: #94a3b8;
      line-height: 1.4;
    }}
    .badge {{
      display: inline-block;
      align-self: flex-start;
      padding: 2px 6px;
      border-radius: 4px;
      font-size: 9px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin-top: 4px;
    }}
    .badge-hero {{ background: #38bdf822; color: #38bdf8; border: 1px solid #38bdf844; }}
    .badge-split {{ background: #10b98122; color: #10b981; border: 1px solid #10b98144; }}
    .badge-compress {{ background: #f59e0b22; color: #f59e0b; border: 1px solid #f59e0b44; }}
  </style>
</head>
<body>
  <div class="header">
    <h1>{topic}</h1>
    <p>{angle}</p>
  </div>
  <div class="player-container">
    <video id="videoPlayer" controls autoplay playsinline preload="auto">
      <source src="{slug}.mp4" type="video/mp4">
      Your browser does not support the video tag.
    </video>
    <div class="scenes-grid">
      {scenes_cards_html}
    </div>
  </div>
  <script>
    const player = document.getElementById('videoPlayer');
    function seek(sec) {{
      player.currentTime = sec;
      player.play();
    }}
  </script>
</body>
</html>"""
        (artifact_dir / f"{slug}_player.html").write_text(player_html, encoding="utf-8")
        print(f"  * Created interactive player: {artifact_dir / f'{slug}_player.html'}")



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
