#!/usr/bin/env python3
"""Run full end-to-end multi-beat project with rich Remotion visual components.

Coordinates:
1. Storyboard stage (AI visual director using VisualComponentRegistry components)
2. World Compiler stage (deterministic multi-beat geometry & timing compilation)
3. Remotion World Renderer stage (cinematic 1080p video with audio narration muxed)
4. Extraction of frame stills across multiple beats for visual inspection
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.dependencies import get_artifact_store, get_pipeline_service, get_media_storage, _load_backend_dotenv
from artifact_store.models import PipelineRunRecord

_load_backend_dotenv()

PROJECT_ID = "project_b8368e0d8b0a4ca4ad34426eeb204c24"
SOURCE_RUN_ID = "run_fa1ffb0d985d4691adbacd4de5042724"


def main():
    store = get_artifact_store()
    storage = get_media_storage()
    pipeline_service = get_pipeline_service()

    project = store.get_project(PROJECT_ID)
    print(f"\n=======================================================")
    print(f"MULTI-BEAT PROJECT: {project.title}")
    print(f"Project ID: {PROJECT_ID}")
    print(f"=======================================================\n")

    if len(sys.argv) > 1 and sys.argv[1].startswith("run_"):
        new_run_id = sys.argv[1]
        print(f"Continuing pipeline run: {new_run_id}")
    else:
        # 1. Create a new clean run
        new_run = store.create_run(
            project_id=PROJECT_ID,
            mode="ai",
        )
        new_run_id = new_run.id
        print(f"Created new pipeline run: {new_run_id}")

        # 2. Copy prerequisite artifacts from source run
        prereq_types = [
            "generate_video_request",
            "research_packet",
            "narrative_plan",
            "hook",
            "visual_intent",
            "script_visual_strategy",
            "review_result",
            "voice_track",
        ]
        source_artifacts = store.list_project_artifacts(PROJECT_ID, SOURCE_RUN_ID)
        by_type = {a.artifact_type: a for a in source_artifacts}

        print("\nCopying prerequisite artifacts to new run...")
        id_map = {}
        for art_type in prereq_types:
            source_art = by_type.get(art_type)
            if not source_art:
                print(f"Missing prerequisite artifact '{art_type}' in source run!")
                sys.exit(1)
            
            payload = dict(source_art.payload_json)
            # If voice_track, ensure media storage key points to the shared audio
            if art_type == "voice_track":
                old_key = payload.get("storage_key")
                old_path = storage.path_for_key(old_key)
                new_key = f"projects/{PROJECT_ID}/runs/{new_run_id}/narration.mp3"
                new_path = storage.ensure_parent(new_key)
                if old_path.exists() and not new_path.exists():
                    import shutil
                    shutil.copy2(old_path, new_path)
                payload["storage_key"] = new_key

            new_parents = {}
            for role, parent_id in (source_art.parent_artifact_roles_json or {}).items():
                if parent_id in id_map:
                    new_parents[role] = id_map[parent_id]

            saved = store.save_artifact(
                project_id=PROJECT_ID,
                run_id=new_run_id,
                artifact_type=art_type,
                schema_version=source_art.schema_version,
                payload_json=payload,
                parent_artifact_roles_json=new_parents,
                validation_json=source_art.validation_json,
            )
            id_map[source_art.id] = saved.id
            print(f"  ✓ Copied {art_type:<25} (status={source_art.status})")

    # 3. Execute Stage: Storyboard
    print(f"\n=======================================================")
    print(f"STAGE 1: GENERATING STORYBOARD WITH RICH VISUAL COMPONENTS")
    print(f"=======================================================")
    storyboard_artifact = pipeline_service.run_stage("storyboard", PROJECT_ID, new_run_id)
    print(f"Storyboard generated! Status: {storyboard_artifact.status}")
    sb_payload = storyboard_artifact.payload_json
    beats = sb_payload.get("beats", [])
    print(f"Beats count: {len(beats)}")
    for i, b in enumerate(beats, 1):
        print(f"  Beat {i}: {b.get('beat_id')} - {b.get('visual_goal')}")
        elem_list = b.get("elements", [])
        comps = [str(e.get("component_type") or e.get("primitive_type") or e.get("object_id")) for e in elem_list]
        print(f"    Elements ({len(elem_list)}): {', '.join(comps)}")

    # 4. Execute Stage: World Compiler
    print(f"\n=======================================================")
    print(f"STAGE 2: COMPILING MULTI-BEAT VISUAL WORLD")
    print(f"=======================================================")
    compiled_world_artifact = pipeline_service.run_stage("world_compiler", PROJECT_ID, new_run_id)
    print(f"World compiled! Status: {compiled_world_artifact.status}")
    cw_payload = compiled_world_artifact.payload_json
    print(f"Total duration: {cw_payload.get('total_duration_frames')} frames ({cw_payload.get('total_duration_frames', 0) / 30:.2f}s)")
    objs = cw_payload.get("objects", {})
    print(f"Compiled objects count: {len(objs)}")

    # 5. Execute Stage: Render Video with Remotion
    print(f"\n=======================================================")
    print(f"STAGE 3: RENDERING REMOTION WORLD VIDEO")
    print(f"=======================================================")
    video_artifact = pipeline_service.run_stage("render", PROJECT_ID, new_run_id)
    print(f"Render completed! Status: {video_artifact.status}")
    v_payload = video_artifact.payload_json
    video_storage_key = v_payload.get("storage_key")
    video_path = storage.path_for_key(video_storage_key)
    print(f"Final video file: {video_path}")
    print(f"Size: {video_path.stat().st_size / (1024*1024):.2f} MB")

    # 6. Extract frame stills across different beats
    print(f"\n=======================================================")
    print(f"STAGE 4: EXTRACTING MULTI-BEAT INSPECTION STILLS")
    print(f"=======================================================")
    stills_dir = video_path.parent / "stills"
    stills_dir.mkdir(parents=True, exist_ok=True)
    beat_intervals = cw_payload.get("beat_intervals", [])
    for b in beat_intervals:
        sample_frame = b["start_frame"] + int((b["end_frame"] - b["start_frame"]) * 0.75)
        timestamp = sample_frame / 30.0
        still_file = stills_dir / f"beat_{b['beat_id']}_frame_{sample_frame:05d}.png"
        subprocess.run(
            [
                "/opt/homebrew/bin/ffmpeg",
                "-y",
                "-ss", f"{timestamp:.3f}",
                "-i", str(video_path),
                "-frames:v", "1",
                "-q:v", "2",
                str(still_file),
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        print(f"  Beat {b['beat_id']} (frame {sample_frame}, {timestamp:.1f}s) -> {still_file}")

    print(f"\n=======================================================")
    print(f"✅ MULTI-BEAT PROJECT PIPELINE COMPLETE!")
    print(f"Video: {video_path}")
    print(f"=======================================================\n")


if __name__ == "__main__":
    main()
