"""Focused architecture tests for the hardened world layout contract.

Validates that:
1. Root group uses allocated macro-zone region;
2. Inactive beat objects do not consume current beat flow space;
3. Persistent identity remains unchanged;
4. Overlay/background does not consume flow space;
5. Active flow children are parent-local;
6. Root does not overflow merely because it contains many world objects;
7. Genuine overflow still fails loudly with diagnostic context;
8. Nested groups remain correct;
9. The loan-world fixture still compiles;
10. The real salary project passes the geometry stage.
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
import pytest

from compiler.models import CanvasConfig
from compiler.world_compiler import WorldCompiler, WorldCompilerError
from compiler.world_models import CompiledWorld
from domain.primitives.common import CanonicalCapabilityType
from domain.storyboard import (
    ContainerFlow,
    FlowAlignment,
    FlowJustification,
    MacroScreenZone,
    MicroLayoutFlow,
    SemanticSpacing,
)
from domain.voice_track import VoiceTrack, WordTimestamp
from domain.visual_world import (
    LifecyclePolicy,
    StoryboardBeat,
    VisualWorldSpec,
    WorldObjectSpec,
)
from tests.test_world_compiler import _loan_world, _voice_track, _group_flow


def _simple_voice_track() -> VoiceTrack:
    text = "first beat narration and second beat narration here"
    words = text.split()
    timestamps = [
        WordTimestamp(word=word, start_ms=i * 100, end_ms=(i + 1) * 100)
        for i, word in enumerate(words)
    ]
    return VoiceTrack(
        voice_id="test-voice",
        audio_file_name="test.mp3",
        storage_key="voice/test.mp3",
        duration_seconds=2.0,
        full_script_text=text,
        word_timestamps=timestamps,
    )


def test_1_root_group_uses_allocated_macro_zone_region() -> None:
    world = VisualWorldSpec(
        world_id="macro_allocation_world",
        beats=[
            StoryboardBeat(
                beat_id="beat_1",
                narration="first beat narration",
                semantic_goal="Test root macro zone allocation.",
                macro_zone=MacroScreenZone.CENTER,
            )
        ],
        objects=[
            WorldObjectSpec(
                object_id="root_container",
                primitive_type=CanonicalCapabilityType.GROUP,
                lifecycle=LifecyclePolicy(mode="persistent", introduced_in_beat="beat_1"),
                beat_ids=["beat_1"],
            )
        ],
    )
    compiler = WorldCompiler(canvas_config=CanvasConfig(width=1920, height=1080, fps=30))
    compiled = compiler.compile(world, _simple_voice_track())

    root = compiled.primitives["root_container"]
    expected_region = compiler._zone_rect(MacroScreenZone.CENTER)
    assert root.local_geometry.x == pytest.approx(expected_region.x)
    assert root.local_geometry.y == pytest.approx(expected_region.y)
    assert root.local_geometry.width == pytest.approx(expected_region.width)
    assert root.local_geometry.height == pytest.approx(expected_region.height)


def test_2_inactive_beat_objects_do_not_consume_current_beat_flow_space() -> None:
    world = VisualWorldSpec(
        world_id="beat_flow_world",
        beats=[
            StoryboardBeat(
                beat_id="beat_1",
                narration="first beat narration",
                semantic_goal="Test beat 1.",
            ),
            StoryboardBeat(
                beat_id="beat_2",
                narration="second beat narration here",
                semantic_goal="Test beat 2.",
            ),
        ],
        objects=[
            WorldObjectSpec(
                object_id="root",
                primitive_type=CanonicalCapabilityType.GROUP,
                lifecycle=LifecyclePolicy(mode="persistent", introduced_in_beat="beat_1"),
                beat_ids=["beat_1", "beat_2"],
            ),
            WorldObjectSpec(
                object_id="item_b1",
                primitive_type=CanonicalCapabilityType.TEXT,
                semantic_content={"content": "Item in beat 1 only"},
                parent_object_id="root",
                lifecycle=LifecyclePolicy(mode="persistent", introduced_in_beat="beat_1"),
                beat_ids=["beat_1"],
            ),
            WorldObjectSpec(
                object_id="item_b2",
                primitive_type=CanonicalCapabilityType.TEXT,
                semantic_content={"content": "Item in beat 2 only"},
                parent_object_id="root",
                lifecycle=LifecyclePolicy(mode="persistent", introduced_in_beat="beat_2"),
                beat_ids=["beat_2"],
            ),
        ],
    )
    compiler = WorldCompiler()
    compiler._reset(world)
    sz_beat1 = compiler._intrinsic_size("root", world.beats[0])
    sz_beat2 = compiler._intrinsic_size("root", world.beats[1])

    # Each beat only includes 1 text item, so height is around 1 item + 2*padding, not 2 items
    item1_sz = compiler._intrinsic_size("item_b1", world.beats[0])
    padding = compiler.token_resolver.resolve_spacing("md")
    assert sz_beat1[1] == pytest.approx(item1_sz[1] + 2 * padding)
    assert sz_beat2[1] == pytest.approx(item1_sz[1] + 2 * padding)


def test_3_persistent_identity_remains_unchanged() -> None:
    world = VisualWorldSpec(
        world_id="identity_world",
        beats=[
            StoryboardBeat(
                beat_id="beat_1",
                narration="first beat narration",
                semantic_goal="Test beat 1.",
            ),
            StoryboardBeat(
                beat_id="beat_2",
                narration="second beat narration here",
                semantic_goal="Test beat 2.",
            ),
        ],
        objects=[
            WorldObjectSpec(
                object_id="container",
                primitive_type=CanonicalCapabilityType.GROUP,
                lifecycle=LifecyclePolicy(mode="persistent", introduced_in_beat="beat_1"),
                beat_ids=["beat_1", "beat_2"],
            ),
            WorldObjectSpec(
                object_id="salary_metric",
                primitive_type=CanonicalCapabilityType.NUMBER,
                semantic_content={"value": 100000},
                parent_object_id="container",
                lifecycle=LifecyclePolicy(mode="persistent", introduced_in_beat="beat_1"),
                beat_ids=["beat_1", "beat_2"],
            ),
        ],
    )
    compiled = WorldCompiler().compile(world, _simple_voice_track())
    assert "salary_metric" in compiled.primitives
    assert compiled.primitives["salary_metric"].object_id == "salary_metric"


def test_4_overlay_and_background_do_not_consume_flow_space() -> None:
    world = VisualWorldSpec(
        world_id="overlay_flow_world",
        beats=[
            StoryboardBeat(
                beat_id="beat_1",
                narration="first beat narration",
                semantic_goal="Test background surface non-flow.",
            ),
        ],
        objects=[
            WorldObjectSpec(
                object_id="card",
                primitive_type=CanonicalCapabilityType.GROUP,
                lifecycle=LifecyclePolicy(mode="persistent", introduced_in_beat="beat_1"),
                beat_ids=["beat_1"],
            ),
            WorldObjectSpec(
                object_id="surface_background",
                primitive_type=CanonicalCapabilityType.SHAPE,
                semantic_content={"fill_role": "surface"},
                parent_object_id="card",
                lifecycle=LifecyclePolicy(mode="persistent", introduced_in_beat="beat_1"),
                beat_ids=["beat_1"],
            ),
            WorldObjectSpec(
                object_id="headline",
                primitive_type=CanonicalCapabilityType.TEXT,
                semantic_content={"content": "Headline Text"},
                parent_object_id="card",
                lifecycle=LifecyclePolicy(mode="persistent", introduced_in_beat="beat_1"),
                beat_ids=["beat_1"],
            ),
        ],
    )
    compiler = WorldCompiler()
    compiler._reset(world)
    card_sz = compiler._intrinsic_size("card", world.beats[0])
    text_sz = compiler._intrinsic_size("headline", world.beats[0])
    padding = compiler.token_resolver.resolve_spacing("md")

    # Card height should only be text height + 2*padding, NOT inflated by surface_background (320x200)
    assert card_sz[1] == pytest.approx(text_sz[1] + 2 * padding)
    assert card_sz[1] < 100.0


def test_5_active_flow_children_are_parent_local() -> None:
    compiled = WorldCompiler().compile(_loan_world(), _voice_track())
    rate_geom = compiled.primitives["rate"].local_geometry
    metrics_geom = compiled.primitives["metrics_group"].local_geometry
    panel_geom = compiled.primitives["loan_panel"].local_geometry

    # rate is inside metrics_group; its x/y are relative to metrics_group
    assert rate_geom.x >= 0
    assert rate_geom.y >= 0
    assert rate_geom.x < metrics_geom.width
    assert rate_geom.y < metrics_geom.height

    # metrics_group is inside loan_panel
    assert metrics_geom.x >= 0
    assert metrics_geom.y >= 0
    assert metrics_geom.x < panel_geom.width
    assert metrics_geom.y < panel_geom.height


def _multi_beat_voice_track(count: int = 10) -> tuple[list[str], VoiceTrack]:
    word_names = ["alpha", "bravo", "charlie", "delta", "echo", "foxtrot", "golf", "hotel", "india", "juliet"]
    phrases = [f"narration phrase {word_names[i]}" for i in range(count)]
    full_text = " ".join(phrases)
    words = full_text.split()
    timestamps = [
        WordTimestamp(word=w, start_ms=i * 100, end_ms=(i + 1) * 100)
        for i, w in enumerate(words)
    ]
    vt = VoiceTrack(
        voice_id="test-voice",
        audio_file_name="test.mp3",
        storage_key="voice/test.mp3",
        duration_seconds=len(words) * 0.1 + 0.5,
        full_script_text=full_text,
        word_timestamps=timestamps,
    )
    return phrases, vt


def test_6_root_does_not_overflow_merely_because_it_contains_many_world_objects() -> None:
    # 20 objects across 10 beats (2 per beat), would overflow if all counted simultaneously
    phrases, vt = _multi_beat_voice_track(10)
    beats = [
        StoryboardBeat(
            beat_id=f"beat_{i:02d}",
            narration=phrases[i - 1],
            semantic_goal=f"Beat {i} goal.",
        )
        for i in range(1, 11)
    ]
    objects = [
        WorldObjectSpec(
            object_id="root_container",
            primitive_type=CanonicalCapabilityType.GROUP,
            lifecycle=LifecyclePolicy(mode="persistent", introduced_in_beat="beat_01"),
            beat_ids=[b.beat_id for b in beats],
        )
    ]
    for i in range(1, 11):
        bid = f"beat_{i:02d}"
        for j in range(2):
            objects.append(
                WorldObjectSpec(
                    object_id=f"metric_{i}_{j}",
                    primitive_type=CanonicalCapabilityType.NUMBER,
                    semantic_content={"value": i * 10 + j},
                    parent_object_id="root_container",
                    lifecycle=LifecyclePolicy(mode="persistent", introduced_in_beat=bid),
                    beat_ids=[bid],
                )
            )

    world = VisualWorldSpec(world_id="many_objects_world", beats=beats, objects=objects)
    compiler = WorldCompiler()
    # Should compile without overflow
    compiled = compiler.compile(world, vt)
    assert len(compiled.primitives) == 21


def test_7_genuine_overflow_still_fails_loudly_with_diagnostics() -> None:
    world = VisualWorldSpec(
        world_id="genuine_overflow_world",
        beats=[
            StoryboardBeat(
                beat_id="beat_1",
                narration="first beat narration",
                semantic_goal="Test overflow failure.",
                macro_zone=MacroScreenZone.CENTER,
            )
        ],
        objects=[
            WorldObjectSpec(
                object_id="small_container",
                primitive_type=CanonicalCapabilityType.GROUP,
                lifecycle=LifecyclePolicy(mode="persistent", introduced_in_beat="beat_1"),
                beat_ids=["beat_1"],
            ),
            # Giant text that cannot fit inside any normal container
            WorldObjectSpec(
                object_id="giant_text",
                primitive_type=CanonicalCapabilityType.TEXT,
                semantic_content={"content": "W" * 500},
                parent_object_id="small_container",
                lifecycle=LifecyclePolicy(mode="persistent", introduced_in_beat="beat_1"),
                beat_ids=["beat_1"],
            ),
        ],
    )
    with pytest.raises(WorldCompilerError) as exc_info:
        WorldCompiler().compile(world, _simple_voice_track())

    error_msg = str(exc_info.value)
    assert "overflow" in error_msg.lower()
    assert "small_container" in error_msg
    assert "beat_1" in error_msg
    assert "available=" in error_msg
    assert "required=" in error_msg
    assert "giant_text" in error_msg


def test_8_nested_groups_remain_correct() -> None:
    world = VisualWorldSpec(
        world_id="nested_group_world",
        beats=[
            StoryboardBeat(
                beat_id="beat_1",
                narration="first beat narration",
                semantic_goal="Test nested groups.",
            ),
        ],
        objects=[
            WorldObjectSpec(
                object_id="outer_card",
                primitive_type=CanonicalCapabilityType.GROUP,
                lifecycle=LifecyclePolicy(mode="persistent", introduced_in_beat="beat_1"),
                beat_ids=["beat_1"],
            ),
            WorldObjectSpec(
                object_id="inner_row",
                primitive_type=CanonicalCapabilityType.GROUP,
                semantic_content={
                    "layout_flow": _group_flow(
                        ContainerFlow.ROW, SemanticSpacing.SM, SemanticSpacing.SM
                    )
                },
                parent_object_id="outer_card",
                lifecycle=LifecyclePolicy(mode="persistent", introduced_in_beat="beat_1"),
                beat_ids=["beat_1"],
            ),
            WorldObjectSpec(
                object_id="item_a",
                primitive_type=CanonicalCapabilityType.NUMBER,
                semantic_content={"value": 10},
                parent_object_id="inner_row",
                lifecycle=LifecyclePolicy(mode="persistent", introduced_in_beat="beat_1"),
                beat_ids=["beat_1"],
            ),
            WorldObjectSpec(
                object_id="item_b",
                primitive_type=CanonicalCapabilityType.NUMBER,
                semantic_content={"value": 20},
                parent_object_id="inner_row",
                lifecycle=LifecyclePolicy(mode="persistent", introduced_in_beat="beat_1"),
                beat_ids=["beat_1"],
            ),
        ],
    )
    compiled = WorldCompiler().compile(world, _simple_voice_track())
    outer = compiled.primitives["outer_card"].local_geometry
    inner = compiled.primitives["inner_row"].local_geometry
    item_a = compiled.primitives["item_a"].local_geometry
    item_b = compiled.primitives["item_b"].local_geometry

    assert inner.width < outer.width
    assert inner.height < outer.height
    assert item_b.x > item_a.x  # In row flow, item_b is placed after item_a


def test_9_loan_world_fixture_still_compiles() -> None:
    compiled = WorldCompiler().compile(_loan_world(), _voice_track())
    assert isinstance(compiled, CompiledWorld)
    assert len(compiled.primitives) == 6
    assert compiled.world_id == "loan_world"


def test_10_real_salary_project_passes_geometry_stage() -> None:
    artifact_path = Path("/Users/dakshyadav/.gemini/antigravity/brain/4d3bebca-deaf-4d89-b531-1f38803605d1/project_3b35_hardened_storyboard_result.json")
    if not artifact_path.exists():
        pytest.skip("Real storyboard artifact not found")

    with open(artifact_path) as f:
        spec_data = json.load(f)
    spec = VisualWorldSpec.model_validate(spec_data)

    conn = sqlite3.connect("backend/.data/ytcreate_v2.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT payload_json FROM artifacts WHERE project_id=? AND artifact_type=?",
        ("project_3b357ab4412f4946b898960afacd6716", "voice_track"),
    )
    row = cursor.fetchone()
    assert row is not None, "Voice track artifact must exist in database"
    vt = VoiceTrack.model_validate_json(row[0])

    compiler = WorldCompiler()
    compiled = compiler.compile(spec, vt)

    assert isinstance(compiled, CompiledWorld)
    assert compiled.world_id == "salary_purchasing_power_world"
    assert len(compiled.primitives) == 13
    assert len(compiled.beat_intervals) == 8
    assert len(compiled.speech_anchors) == 13

    # Verify root container fits macro zone
    root_geom = compiled.primitives["main_container"].local_geometry
    macro_region = compiler._zone_rect(MacroScreenZone.CENTER)
    assert root_geom.width == pytest.approx(macro_region.width)
    assert root_geom.height == pytest.approx(macro_region.height)
