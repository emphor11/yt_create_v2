"""
recompile_and_rerender_home_loan.py — Recompiles Stage 7 plan with responsive charts and re-renders Stage 8 MP4.
"""
from __future__ import annotations

import argparse
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

PROJECT_ID = "project_f9f00fa037dc4364bd5948994985269f"
RUN_ID = "run_6564ce106c894f51b1d80cf592ff911c"

from app.dependencies import get_pipeline_service, get_media_storage
from domain.continuous_story_plan import ContinuousStoryDraft
from domain.pipeline_stage import PipelineStage


def main():
    parser = argparse.ArgumentParser(description="Recompile and Re-render Home Loan Video with Responsive Charts")
    parser.add_argument("--compile-only", action="store_true", help="Only recompile and validate without running Remotion render")
    args = parser.parse_args()

    print("=" * 75)
    print("RECOMPILING & RE-RENDERING HOME LOAN STORY WITH RESPONSIVE CHARTS")
    print(f"Project ID: {PROJECT_ID}")
    print(f"Run ID:     {RUN_ID}")
    print("=" * 75)

    svc = get_pipeline_service()
    store = svc.store
    media_storage = get_media_storage()

    # 1. Fetch existing continuous_story_plan
    existing_csp = store.find_artifact_by_type(PROJECT_ID, RUN_ID, "continuous_story_plan")
    if not existing_csp:
        print("[FAIL] continuous_story_plan artifact not found in store!")
        sys.exit(1)

    payload = existing_csp.payload_json
    raw_draft = payload.get("raw_gemini_draft") or payload.get("draft")
    if not raw_draft:
        print("[FAIL] No draft found in continuous_story_plan payload!")
        sys.exit(1)

    print(f"[FOUND] Existing continuous_story_plan artifact: {existing_csp.id}")
    draft_obj = ContinuousStoryDraft.model_validate(raw_draft)
    print(f"        Draft objects: {len(draft_obj.objects)}, events: {len(draft_obj.events)}")

    # Promote standalone solitary charts from full_bottom to center hero layout
    for obj in draft_obj.objects:
        if obj.id in ("amortization_chart", "return_comparison_chart"):
            object.__setattr__(obj, "layout", "center")
            print(f"[HERO PROMOTION] Upgraded '{obj.id}' to layout='center' (1440x560 Broadcast Hero Graphic)")

    # 2. Check existing video artifact
    existing_video = store.find_artifact_by_type(PROJECT_ID, RUN_ID, "video")

    # Delete existing artifacts to allow clean regeneration
    ids_to_del = [existing_csp.id]
    if existing_video:
        ids_to_del.append(existing_video.id)
    store.delete_artifacts(ids_to_del)
    print(f"[CLEANUP] Deleted old artifacts: {ids_to_del}")

    # 3. Re-run Stage 7 with mock_draft using updated ContinuousStoryCompiler
    print("\n---> [STAGE 7] Recompiling story plan with updated responsive compiler...")
    t0 = time.time()
    new_csp_record = svc.router.execute(PipelineStage.CONTINUOUS_STORY, PROJECT_ID, RUN_ID, mock_draft=draft_obj)
    dt = time.time() - t0
    print(f"     [OK] Stage 7 recompiled successfully in {dt:.1f}s!")
    print(f"          New Artifact ID: {new_csp_record.id}")

    # Inspect compiled chart objects
    new_plan = new_csp_record.payload_json.get("plan", {})
    charts = [o for o in new_plan.get("objects", []) if o.get("type") == "chart"]
    print(f"\n     [COMPILED CHART GEOMETRY AUDIT] ({len(charts)} charts):")
    for c in charts:
        props = c.get("chartProps", {})
        print(f"       - ID: {c.get('id'):<26} Layout: {c.get('layout'):<12} Size: {c.get('width')}x{c.get('height')} Type: {props.get('chartType')}")
        if c.get("layout") == "full_bottom":
            assert c.get("height") == 260, f"Expected height 260 for full_bottom, got {c.get('height')}"
            assert c.get("width") == 1760, f"Expected width 1760 for full_bottom, got {c.get('width')}"

    print("     [VERIFIED] All full_bottom charts compiled to 1760x260px collision-free responsive geometry!")

    if args.compile_only:
        print("\n[INFO] --compile-only specified. Exiting before render.")
        return

    # 4. Dispatch Stage 8: render
    print("\n---> [STAGE 8] Dispatching Remotion render to MP4...")
    t0 = time.time()
    video_record = svc.router.execute(PipelineStage.RENDER, PROJECT_ID, RUN_ID)
    dt = time.time() - t0
    print(f"     [OK] Stage 8 render completed in {dt:.1f}s ({dt/60:.1f} min)!")
    print(f"          Video Artifact ID: {video_record.id}")
    print(f"          Video Status:      {video_record.status}")

    v_payload = video_record.payload_json
    storage_key = v_payload.get("storage_key")
    video_path = media_storage.path_for_key(storage_key)

    if not video_path.exists():
        print(f"[FAIL] Rendered video file does not exist at: {video_path}")
        sys.exit(1)

    file_size = video_path.stat().st_size
    print(f"\n[OUTPUT] Video Path: {video_path}")
    print(f"         File Size:  {file_size / (1024 * 1024):.2f} MB ({file_size:,} bytes)")
    print(f"         Duration:   {v_payload.get('duration_frames')} frames @ {v_payload.get('fps')}fps ({(v_payload.get('duration_frames', 0) / v_payload.get('fps', 30)):.1f}s)")

    # Copy to artifacts directory
    artifact_dir = Path("/Users/dakshyadav/.gemini/antigravity/brain/0ea3762c-60ae-40de-96c0-ce19c83dda9d")
    dest_video = artifact_dir / "the_home_loan_prepayment_par.mp4"
    shutil.copy2(video_path, dest_video)
    print(f"  * Copied updated video to artifact: {dest_video}")

    # Extract stills at 38s, 119s, 135s to confirm in rendered video
    for sec in [38, 119, 135]:
        out_frame = artifact_dir / f"hl_rendered_frame_{sec:03d}s.png"
        cmd = [
            "ffmpeg", "-y", "-ss", str(sec), "-i", str(video_path),
            "-vframes", "1", "-q:v", "2", str(out_frame)
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0 and out_frame.exists():
            print(f"  * Extracted confirmation frame at {sec}s: {out_frame.name}")


if __name__ == "__main__":
    main()
