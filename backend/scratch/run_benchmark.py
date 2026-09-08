#!/usr/bin/env python3
import json
import os
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path

# Add backend directory to sys.path
backend_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(backend_root))

from app.dependencies import (
    _load_backend_dotenv,
    get_artifact_store,
    get_media_storage,
    get_pipeline_service,
)
_load_backend_dotenv()

from domain.generate_video_request import GenerateVideoRequest
from domain.validators.generate_video_request_validator import GenerateVideoRequestValidator


def run_benchmark():
    print("=" * 80)
    print("YTcreate_V2 5-Minute Real Production Pipeline Benchmark")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 80)

    # 1. Pipeline Inputs
    topic = "The Death of the 4% Retirement Rule: Why Safe Withdrawal Math Just Broke"
    angle = "A deep dive into how inflation spikes, bond market shifts, and rising longevity have broken William Bengen's 1994 Trinity study math, forcing retirees from 4% down to 2.8% to avoid running out of money before age 90."
    audience = "Working professionals and pre-retirees planning long-term financial independence"
    style = "analytical, metrics-driven, and actionable"
    channel = "MindshiftFinance"

    print("\n1. INPUT CONFIGURATION:")
    print(f"   Topic:    {topic}")
    print(f"   Angle:    {angle}")
    print(f"   Audience: {audience}")
    print(f"   Style:    {style}")
    print(f"   Channel:  {channel}")

    store = get_artifact_store()
    media_storage = get_media_storage()
    pipeline_service = get_pipeline_service()

    project = store.create_project(topic)
    run = store.create_run(project.id, mode="ai")
    project_id = project.id
    run_id = run.id

    print(f"   Project ID: {project_id}")
    print(f"   Run ID:     {run_id}")

    # Create generate_video_request artifact
    gen_req = GenerateVideoRequest(
        topic=topic,
        angle=angle,
        audience=audience,
        language="English",
        style=style,
        channel=channel,
    )
    val = GenerateVideoRequestValidator().validate(gen_req)
    req_art = store.save_artifact(
        project_id=project_id,
        run_id=run_id,
        artifact_type="generate_video_request",
        schema_version=gen_req.schema_version,
        payload_json=gen_req.model_dump(),
        parent_artifact_roles_json={},
        validation_json=val,
    )
    print("   Created generate_video_request artifact:", req_art.id)

    stages = [
        "research",
        "narrative_plan",
        "hook",
        "script_visual_strategy",
        "quality_review",
        "voice_generation",
        "video_assembly",
        "render",
        "youtube_metadata",
        "thumbnail",
        "youtube_upload",
    ]

    metrics = {
        "project_id": project_id,
        "run_id": run_id,
        "topic": topic,
        "angle": angle,
        "stages": {},
    }

    first_failure = None

    for stage_name in stages:
        print("\n" + "-" * 70)
        print(f"EXECUTING STAGE: {stage_name.upper()}")
        print("-" * 70)
        t0 = time.time()
        try:
            artifact = pipeline_service.run_stage(stage_name, project_id, run_id)
            duration = time.time() - t0
            status = artifact.status
            payload = artifact.payload_json or {}
            val_json = artifact.validation_json.model_dump() if artifact.validation_json else {}

            stage_data = {
                "duration_seconds": round(duration, 3),
                "status": status,
                "validation": val_json,
                "artifact_id": artifact.id,
            }
            metrics["stages"][stage_name] = stage_data

            print(f"--> Stage '{stage_name}' finished in {duration:.2f}s with status: {status}")

            # Specific stage inspections
            if stage_name == "research":
                facts = len(payload.get("verified_facts", []))
                stats = len(payload.get("statistics", []))
                concepts = len(payload.get("concepts", []))
                payload_str = json.dumps(payload)
                stage_data["verified_facts_count"] = facts
                stage_data["statistics_count"] = stats
                stage_data["concepts_count"] = concepts
                stage_data["payload_chars"] = len(payload_str)
                print(f"    Facts: {facts}, Stats: {stats}, Concepts: {concepts}, Raw Size: {len(payload_str)} chars")

            elif stage_name == "narrative_plan":
                scene_beats = payload.get("scene_beats", [])
                stage_data["scene_beats_count"] = len(scene_beats)
                stage_data["scene_titles"] = [b.get("title") for b in scene_beats]
                stage_data["thesis"] = payload.get("thesis")
                print(f"    Scene Beats: {len(scene_beats)}")
                for b in scene_beats:
                    print(f"      - [{b.get('scene_id')}] {b.get('title')}: {b.get('core_teaching_point')}")

            elif stage_name == "hook":
                script = payload.get("script_text", "")
                words = len(script.split())
                chars = len(script)
                directives = payload.get("visual_directives", [])
                stage_data["hook_word_count"] = words
                stage_data["hook_char_count"] = chars
                stage_data["visual_directives_count"] = len(directives)
                print(f"    Hook words: {words}, chars: {chars}, visual directives: {len(directives)}")
                print(f"    Hook Script: {script[:100]}...")

            elif stage_name == "script_visual_strategy":
                ideas = payload.get("ideas", [])
                stage_data["ideas_count"] = len(ideas)
                total_words = 0
                total_chars = 0
                total_beats = 0
                components_used = []
                for idea in ideas:
                    narration = idea.get("narration", "")
                    w_count = len(narration.split())
                    c_count = len(narration)
                    total_words += w_count
                    total_chars += c_count
                    beats = idea.get("visual_sequence", [])
                    total_beats += len(beats)
                    for b in beats:
                        components_used.append(b.get("preferred_component"))
                stage_data["total_narration_words"] = total_words
                stage_data["total_narration_chars"] = total_chars
                stage_data["total_visual_beats"] = total_beats
                stage_data["components_used"] = components_used
                print(f"    Ideas count: {len(ideas)}")
                print(f"    Total Narration Words: {total_words}")
                print(f"    Total Narration Chars: {total_chars}")
                print(f"    Total Visual Beats in Ideas: {total_beats}")
                print(f"    Components distribution: {dict((c, components_used.count(c)) for c in set(components_used))}")

            elif stage_name == "quality_review":
                approved = payload.get("approved")
                checks = payload.get("validation_checks", [])
                stage_data["approved"] = approved
                stage_data["checks_count"] = len(checks)
                print(f"    Approved: {approved}")
                for c in checks:
                    print(f"      - {c.get('check_name')}: passed={c.get('passed')} (msg: {c.get('message')})")

            elif stage_name == "voice_generation":
                dur_sec = payload.get("duration_seconds", 0)
                word_ts = payload.get("word_timestamps", [])
                chunks = payload.get("chunks", [])
                stage_data["master_duration_seconds"] = dur_sec
                stage_data["total_speech_marks"] = len(word_ts)
                stage_data["chunks_count"] = len(chunks)
                print(f"    Master Duration: {dur_sec:.2f}s ({dur_sec/60:.2f} mins)")
                print(f"    Total Speech Marks: {len(word_ts)}")
                print(f"    TTS Chunks Count: {len(chunks)}")
                chunk_summaries = []
                for ch in chunks:
                    ch_summary = {
                        "chunk_id": ch.get("chunk_id"),
                        "sequence": ch.get("sequence"),
                        "source_id": ch.get("source_id"),
                        "char_count": len(ch.get("text", "")),
                        "duration_ms": ch.get("duration_ms"),
                        "word_count": len(ch.get("word_timestamps", [])),
                    }
                    chunk_summaries.append(ch_summary)
                    print(f"      * Chunk {ch.get('chunk_id')} [{ch.get('source_id')}]: {len(ch.get('text', ''))} chars, {ch.get('duration_ms')}ms, {len(ch.get('word_timestamps', []))} words")
                stage_data["chunk_summaries"] = chunk_summaries

            elif stage_name == "video_assembly":
                timed_intervals = payload.get("timed_intervals", [])
                assets = payload.get("assets", [])
                fps = payload.get("fps")
                dur_frames = payload.get("duration_frames")
                stage_data["timed_intervals_count"] = len(timed_intervals)
                stage_data["duration_frames"] = dur_frames
                stage_data["fps"] = fps
                stage_data["assets_count"] = len(assets)
                print(f"    Timed Intervals: {len(timed_intervals)}")
                print(f"    Duration Frames: {dur_frames} ({dur_frames / fps:.2f}s at {fps}fps)")
                print(f"    Assets: {len(assets)}")
                for a in assets:
                    print(f"      * Asset {a.get('asset_id')}: type={a.get('asset_type')}, source={a.get('source')}, status={a.get('asset_status')}")

            elif stage_name == "render":
                size_bytes = payload.get("size_bytes", 0)
                fps = payload.get("fps", 30)
                dur_frames = payload.get("duration_frames", 0)
                render_fps = (dur_frames / duration) if duration > 0 else 0
                stage_data["size_bytes"] = size_bytes
                stage_data["size_mb"] = round(size_bytes / (1024 * 1024), 2)
                stage_data["render_fps"] = round(render_fps, 2)
                print(f"    Rendered MP4: {stage_data['size_mb']} MB")
                print(f"    Render Speed: {render_fps:.2f} fps ({duration:.1f}s total render time)")

            elif stage_name == "youtube_metadata":
                title = payload.get("title", "")
                tags = payload.get("tags", [])
                desc = payload.get("description", "")
                stage_data["title"] = title
                stage_data["tags_count"] = len(tags)
                stage_data["description_length"] = len(desc)
                print(f"    Title: {title}")
                print(f"    Tags: {len(tags)}")
                print(f"    Description: {len(desc)} chars")

            elif stage_name == "thumbnail":
                w = payload.get("width")
                h = payload.get("height")
                size = payload.get("size_bytes", 0)
                stage_data["dimensions"] = f"{w}x{h}"
                stage_data["size_bytes"] = size
                print(f"    Thumbnail: {w}x{h}, size: {size} bytes")

            elif stage_name == "youtube_upload":
                yt_id = payload.get("youtube_video_id")
                yt_url = payload.get("youtube_url")
                stage_data["youtube_video_id"] = yt_id
                stage_data["youtube_url"] = yt_url
                print(f"    Uploaded Video ID: {yt_id}")
                print(f"    YouTube URL: {yt_url}")

            if status not in ("valid", "succeeded"):
                first_failure = {
                    "stage": stage_name,
                    "status": status,
                    "errors": val_json.get("errors", []),
                }
                print(f"!!! Stage '{stage_name}' produced non-advanceable status '{status}'!")
                break

        except Exception as exc:
            duration = time.time() - t0
            err_msg = f"{type(exc).__name__}: {str(exc)}"
            tb = traceback.format_exc()
            print(f"!!! EXCEPTION IN STAGE '{stage_name}' after {duration:.2f}s:")
            print(err_msg)
            print(tb)
            first_failure = {
                "stage": stage_name,
                "error": err_msg,
                "traceback": tb,
            }
            metrics["stages"][stage_name] = {
                "duration_seconds": round(duration, 3),
                "error": err_msg,
                "traceback": tb,
            }
            break

    # Save metrics JSON to scratch
    out_file = Path(backend_root) / "scratch" / "benchmark_5min_results.json"
    out_file.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print("\n" + "=" * 80)
    print(f"BENCHMARK COMPLETE. Results written to: {out_file}")
    if first_failure:
        print(f"FIRST FAILURE POINT: Stage '{first_failure.get('stage')}'")
        print(f"Details: {first_failure}")
    else:
        print("ALL STAGES COMPLETED SUCCESSFULLY!")
    print("=" * 80)


if __name__ == "__main__":
    run_benchmark()
