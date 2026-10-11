#!/usr/bin/env python3
"""Golden Slice end-to-end compilation, rendering, audio muxing, and verification.

Renders Beat 2 of the India Wealth Distribution scene:
- 2 SurfaceCards (Top 10% vs Bottom 50%)
- Badges ("TOP 10%", "BOTTOM 50%")
- MetricBlocks with verbatim qualifiers (>57%, <6%) and animated count-ups
- FlowConnector with 'vs' pill connecting the cards
- Callout banner at bottom with editorial takeaway
- Real audio narration synthesized and muxed to MP4
"""
import json
import os
import subprocess
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from compiler.models import CanvasConfig
from compiler.world_compiler import WorldCompiler
from domain.storyboard import (
    MacroScreenZone,
    VisualAction,
    VisualActionType,
)
from domain.voice_track import VoiceTrack, WordTimestamp
from domain.visual_world import (
    LifecyclePolicy,
    ObjectStateTrack,
    StateChangeEvent,
    StateChangeKind,
    StoryboardBeat,
    VisualWorldSpec,
    WorldObjectSpec,
)
from providers.remotion_provider import RemotionProvider


def generate_narration_audio(output_dir: Path) -> tuple[Path, VoiceTrack]:
    output_dir.mkdir(parents=True, exist_ok=True)
    text = (
        "The top ten percent holds over fifty seven percent of all national wealth. "
        "In contrast, the bottom fifty percent owns less than six percent. "
        "This creates an extreme divergence in economic power."
    )
    
    aiff_path = output_dir / "narration.aiff"
    mp3_path = output_dir / "narration.mp3"
    
    # 1. macOS native TTS
    subprocess.run(["say", "-v", "Daniel", "-o", str(aiff_path), text], check=True)
    
    # 2. Convert to MP3
    subprocess.run(
        ["/opt/homebrew/bin/ffmpeg", "-y", "-i", str(aiff_path), "-c:a", "libmp3lame", "-b:a", "192k", str(mp3_path)],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    
    # 3. Get audio duration
    probe = subprocess.run(
        [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(mp3_path),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    duration_seconds = float(probe.stdout.strip())
    
    # 4. Generate word timestamps strictly within duration
    words = text.split()
    duration_ms = int(duration_seconds * 1000)
    lead_in_ms = 200
    tail_ms = 500
    usable_ms = max(500, duration_ms - lead_in_ms - tail_ms)
    step_ms = usable_ms / len(words)

    timestamps = []
    for index, word in enumerate(words):
        clean_word = word.strip(".,!?;:\"'()[]{}")
        start_ms = int(lead_in_ms + index * step_ms)
        end_ms = int(lead_in_ms + (index + 1) * step_ms - 10)
        timestamps.append(
            WordTimestamp(
                word=clean_word,
                start_ms=start_ms,
                end_ms=end_ms,
            )
        )

    # Ensure voice track duration covers all frames with terminal margin
    safe_duration = max(duration_seconds, (timestamps[-1].end_ms + 600) / 1000.0)

    voice_track = VoiceTrack(
        voice_id="daniel-doc",
        audio_file_name="narration.mp3",
        storage_key="voice/narration.mp3",
        duration_seconds=safe_duration,
        full_script_text=text,
        word_timestamps=timestamps,
    )
    return mp3_path, voice_track


def build_wealth_visual_world(voice_track: VoiceTrack) -> VisualWorldSpec:
    beat = StoryboardBeat(
        beat_id="beat_wealth",
        narration=voice_track.full_script_text,
        semantic_goal="Compare wealth share between the top 10% and bottom 50%",
        macro_zone=MacroScreenZone.CENTER,
        actions=[
            VisualAction(
                action_id="act_enter_top",
                action_type=VisualActionType.ENTER,
                target_node_id="card_top_10",
                trigger_word="top",
            ),
            VisualAction(
                action_id="act_count_top",
                action_type=VisualActionType.UPDATE_VALUE,
                target_node_id="metric_top_10",
                trigger_word="seven",
                new_value=57.0,
            ),
            VisualAction(
                action_id="act_enter_bottom",
                action_type=VisualActionType.ENTER,
                target_node_id="card_bottom_50",
                trigger_word="contrast",
            ),
            VisualAction(
                action_id="act_count_bottom",
                action_type=VisualActionType.UPDATE_VALUE,
                target_node_id="metric_bottom_50",
                trigger_word="six",
                new_value=6.0,
            ),
            VisualAction(
                action_id="act_connect",
                action_type=VisualActionType.ENTER,
                target_node_id="connector_divergence",
                trigger_word="bottom",
            ),
            VisualAction(
                action_id="act_callout",
                action_type=VisualActionType.ENTER,
                target_node_id="callout_thesis",
                trigger_word="divergence",
            ),
        ],
    )

    objects = [
        # Top 10% Surface Card (SPLIT_LEFT)
        WorldObjectSpec(
            object_id="card_top_10",
            component_type="SurfaceCard",
            semantic_content={
                "macro_zone": MacroScreenZone.SPLIT_LEFT,
                "variant": "elevated",
                "header_label": "WEALTH DECILE : TOP 10%",
            },
            beat_ids=["beat_wealth"],
            lifecycle=LifecyclePolicy(mode="beat_local", introduced_in_beat="beat_wealth"),
        ),
        WorldObjectSpec(
            object_id="badge_top_10",
            component_type="Badge",
            parent_object_id="card_top_10",
            semantic_content={"text": "RICHEST 10%", "variant": "filled", "intent": "accent"},
            beat_ids=["beat_wealth"],
        ),
        WorldObjectSpec(
            object_id="metric_top_10",
            component_type="MetricBlock",
            parent_object_id="card_top_10",
            semantic_content={
                "qualifier": ">",
                "raw_value": 0.0,
                "display_value": ">57%",
                "unit": "%",
                "label": "SHARE OF NATIONAL WEALTH",
                "subtext": "Source: World Inequality Database 2024",
                "emphasis": "hero",
            },
            beat_ids=["beat_wealth"],
        ),
        # Bottom 50% Surface Card (SPLIT_RIGHT)
        WorldObjectSpec(
            object_id="card_bottom_50",
            component_type="SurfaceCard",
            semantic_content={
                "macro_zone": MacroScreenZone.SPLIT_RIGHT,
                "variant": "elevated",
                "header_label": "WEALTH DECILE : BOTTOM 50%",
            },
            beat_ids=["beat_wealth"],
            lifecycle=LifecyclePolicy(mode="beat_local", introduced_in_beat="beat_wealth"),
        ),
        WorldObjectSpec(
            object_id="badge_bottom_50",
            component_type="Badge",
            parent_object_id="card_bottom_50",
            semantic_content={"text": "LOWER 50%", "variant": "outline", "intent": "neutral"},
            beat_ids=["beat_wealth"],
        ),
        WorldObjectSpec(
            object_id="metric_bottom_50",
            component_type="MetricBlock",
            parent_object_id="card_bottom_50",
            semantic_content={
                "qualifier": "<",
                "raw_value": 0.0,
                "display_value": "<6%",
                "unit": "%",
                "label": "SHARE OF NATIONAL WEALTH",
                "subtext": "Combined lower 5 deciles",
                "emphasis": "hero",
            },
            beat_ids=["beat_wealth"],
        ),
        # Relational FlowConnector
        WorldObjectSpec(
            object_id="connector_divergence",
            component_type="FlowConnector",
            semantic_content={
                "source_id": "card_top_10",
                "target_id": "card_bottom_50",
                "relationship_type": "contrasts_with",
                "routing": "orthogonal_elbow",
                "has_arrow": True,
                "label": "vs",
            },
            beat_ids=["beat_wealth"],
        ),
        # Editorial Callout (BOTTOM)
        WorldObjectSpec(
            object_id="callout_thesis",
            component_type="Callout",
            semantic_content={
                "macro_zone": MacroScreenZone.BOTTOM,
                "text": "The top 10% holds 9.5x more wealth than the entire bottom half combined.",
                "attribution": "World Inequality Database 2024",
                "intent": "insight",
            },
            beat_ids=["beat_wealth"],
        ),
    ]

    tracks = [
        ObjectStateTrack(
            object_id="metric_top_10",
            initial_state={"value": 0.0},
            state_changes=[
                StateChangeEvent(
                    event_id="evt_count_top",
                    object_id="metric_top_10",
                    beat_id="beat_wealth",
                    kind=StateChangeKind.VALUE,
                    target_property="value",
                    to_value=57.0,
                )
            ],
        ),
        ObjectStateTrack(
            object_id="metric_bottom_50",
            initial_state={"value": 0.0},
            state_changes=[
                StateChangeEvent(
                    event_id="evt_count_bottom",
                    object_id="metric_bottom_50",
                    beat_id="beat_wealth",
                    kind=StateChangeKind.VALUE,
                    target_property="value",
                    to_value=6.0,
                )
            ],
        ),
    ]

    return VisualWorldSpec(
        world_id="wealth_distribution_slice",
        beats=[beat],
        objects=objects,
        object_state_tracks=tracks,
    )


def main():
    repo_root = Path(__file__).resolve().parent.parent
    output_dir = repo_root / "output" / "golden_slice"
    output_dir.mkdir(parents=True, exist_ok=True)

    print("Step 1: Generating audio narration...")
    audio_path, voice_track = generate_narration_audio(output_dir)
    print(f"Generated narration: {audio_path} ({voice_track.duration_seconds:.2f}s)")

    print("Step 2: Building visual world specification...")
    world_spec = build_wealth_visual_world(voice_track)

    print("Step 3: Compiling visual world...")
    compiler = WorldCompiler(canvas_config=CanvasConfig(width=1920, height=1080, fps=30))
    compiled_world = compiler.compile(world_spec, voice_track)
    print(f"Compiled world duration: {compiled_world.total_duration_frames} frames ({compiled_world.total_duration_frames / 30:.2f}s)")
    print(f"Objects count: {len(compiled_world.objects)}")
    for obj_id, obj in compiled_world.objects.items():
        print(f"  - {obj_id} ({obj.component_type or obj.primitive_type}) at {obj.local_geometry}")

    compiled_json_path = output_dir / "compiled_world.json"
    compiled_json_path.write_text(compiled_world.model_dump_json(indent=2), encoding="utf-8")
    print(f"Saved compiled world payload to: {compiled_json_path}")

    print("Step 4: Rendering video with Remotion...")
    remotion_dir = repo_root / "renderer" / "remotion"
    provider = RemotionProvider(renderer_root=remotion_dir, timeout_seconds=300)
    raw_video_path = output_dir / "golden_slice_raw.mp4"
    
    render_output = provider.render_world(
        compiled_world=compiled_world.model_dump(mode="json"),
        output_path=raw_video_path,
    )
    print(f"Raw video rendered: {render_output.output_path} ({render_output.size_bytes / (1024*1024):.2f} MB)")

    print("Step 5: Muxing narration audio with video...")
    final_video_path = output_dir / "golden_slice_wealth.mp4"
    subprocess.run(
        [
            "/opt/homebrew/bin/ffmpeg",
            "-y",
            "-i", str(raw_video_path),
            "-i", str(audio_path),
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-c:v", "copy",
            "-c:a", "aac",
            "-shortest",
            str(final_video_path),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    print(f"Final video with audio produced: {final_video_path} ({final_video_path.stat().st_size / (1024*1024):.2f} MB)")

    print("Step 6: Extracting inspection stills (frames at 25%, 50%, 75%, 95%)...")
    stills_dir = output_dir / "stills"
    stills_dir.mkdir(parents=True, exist_ok=True)
    total_frames = compiled_world.total_duration_frames
    test_frames = [
        int(total_frames * 0.25),
        int(total_frames * 0.50),
        int(total_frames * 0.75),
        int(total_frames * 0.95),
    ]
    for frame in test_frames:
        timestamp = frame / 30.0
        still_file = stills_dir / f"frame_{frame:04d}.png"
        subprocess.run(
            [
                "/opt/homebrew/bin/ffmpeg",
                "-y",
                "-ss", f"{timestamp:.3f}",
                "-i", str(final_video_path),
                "-frames:v", "1",
                "-q:v", "2",
                str(still_file),
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        print(f"  Frame {frame} ({timestamp:.2f}s) -> {still_file}")

    print("\n✅ GOLDEN SLICE END-TO-END RENDER COMPLETE!")


if __name__ == "__main__":
    main()
