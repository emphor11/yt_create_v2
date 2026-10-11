"""End-to-end tests for compiler layout and sizing of rich visual components."""
from __future__ import annotations

import pytest

from compiler.models import CanvasConfig
from compiler.world_compiler import WorldCompiler, WorldCompilerError
from compiler.world_models import CompiledObjectKind, CompiledWorld
from domain.storyboard import (
    MacroScreenZone,
    VisualAction,
    VisualActionType,
)
from domain.voice_track import VoiceTrack, WordTimestamp
from domain.visual_world import (
    LifecyclePolicy,
    StoryboardBeat,
    VisualWorldSpec,
    WorldObjectSpec,
)


def _voice_track() -> VoiceTrack:
    text = (
        "The top ten percent holds over fifty seven percent of all national wealth. "
        "In contrast, the bottom fifty percent owns less than six percent. "
        "This creates a nine point five times divergence in economic power."
    )
    words = text.split()
    timestamps = [
        WordTimestamp(word=word, start_ms=index * 150, end_ms=(index + 1) * 150)
        for index, word in enumerate(words)
    ]
    return VoiceTrack(
        voice_id="wealth-voice",
        audio_file_name="wealth.mp3",
        storage_key="voice/wealth.mp3",
        duration_seconds=len(words) * 0.15 + 0.5,
        full_script_text=text,
        word_timestamps=timestamps,
    )


def test_compile_wealth_distribution_components() -> None:
    """Verifies that rich Remotion components are compiled directly without primitive expansion."""
    vt = _voice_track()

    beat = StoryboardBeat(
        beat_id="beat_wealth",
        narration=vt.full_script_text,
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
                action_id="act_enter_bottom",
                action_type=VisualActionType.ENTER,
                target_node_id="card_bottom_50",
                trigger_word="bottom",
            ),
            VisualAction(
                action_id="act_connect",
                action_type=VisualActionType.ENTER,
                target_node_id="connector_divergence",
                trigger_word="contrast",
            ),
        ],
    )

    objects = [
        # Top 10% Card (Left Split)
        WorldObjectSpec(
            object_id="card_top_10",
            component_type="SurfaceCard",
            semantic_content={"macro_zone": MacroScreenZone.SPLIT_LEFT, "variant": "elevated", "header_label": "TOP DECILE"},
            beat_ids=["beat_wealth"],
            lifecycle=LifecyclePolicy(mode="beat_local", introduced_in_beat="beat_wealth"),
        ),
        WorldObjectSpec(
            object_id="badge_top_10",
            component_type="Badge",
            parent_object_id="card_top_10",
            semantic_content={"text": "TOP 10%", "variant": "filled", "intent": "accent"},
            beat_ids=["beat_wealth"],
        ),
        WorldObjectSpec(
            object_id="metric_top_10",
            component_type="MetricBlock",
            parent_object_id="card_top_10",
            semantic_content={
                "qualifier": ">",
                "raw_value": 57.0,
                "display_value": ">57%",
                "unit": "%",
                "label": "SHARE OF NATIONAL WEALTH",
                "subtext": "Source: World Inequality Database 2024",
                "emphasis": "hero",
            },
            beat_ids=["beat_wealth"],
        ),
        # Bottom 50% Card (Right Split)
        WorldObjectSpec(
            object_id="card_bottom_50",
            component_type="SurfaceCard",
            semantic_content={"macro_zone": MacroScreenZone.SPLIT_RIGHT, "variant": "elevated", "header_label": "BOTTOM HALF"},
            beat_ids=["beat_wealth"],
            lifecycle=LifecyclePolicy(mode="beat_local", introduced_in_beat="beat_wealth"),
        ),
        WorldObjectSpec(
            object_id="badge_bottom_50",
            component_type="Badge",
            parent_object_id="card_bottom_50",
            semantic_content={"text": "BOTTOM 50%", "variant": "outline", "intent": "neutral"},
            beat_ids=["beat_wealth"],
        ),
        WorldObjectSpec(
            object_id="metric_bottom_50",
            component_type="MetricBlock",
            parent_object_id="card_bottom_50",
            semantic_content={
                "qualifier": "<",
                "raw_value": 6.0,
                "display_value": "<6%",
                "unit": "%",
                "label": "SHARE OF NATIONAL WEALTH",
                "subtext": "Combined lower deciles",
                "emphasis": "hero",
            },
            beat_ids=["beat_wealth"],
        ),
        # Relational Link
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
        # Editorial Callout
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

    world = VisualWorldSpec(
        world_id="world_wealth_comp",
        beats=[beat],
        objects=objects,
    )

    compiler = WorldCompiler(canvas_config=CanvasConfig(width=1920, height=1080, fps=30))
    compiled = compiler.compile(world, vt)

    # 1. Authoritative objects dictionary contains all components directly
    assert len(compiled.objects) == 8
    for obj_id, inst in compiled.objects.items():
        assert inst.kind == CompiledObjectKind.COMPONENT
        assert inst.component_type is not None

    # 2. Card layout sizing & parent-local child geometry
    card_top = compiled.objects["card_top_10"]
    card_bottom = compiled.objects["card_bottom_50"]
    assert card_top.local_geometry.width > 300.0
    assert card_top.local_geometry.height >= 240.0
    assert card_bottom.local_geometry.width > 300.0
    assert card_bottom.local_geometry.height >= 240.0

    # Ensure cards are horizontally split and do not overlap
    assert card_top.local_geometry.x + card_top.local_geometry.width <= card_bottom.local_geometry.x

    # 3. Parent-local child positioning inside card_top_10
    badge_top = compiled.objects["badge_top_10"]
    metric_top = compiled.objects["metric_top_10"]
    assert badge_top.parent_object_id == "card_top_10"
    assert metric_top.parent_object_id == "card_top_10"

    # Children must have parent-local coordinates starting at card padding (24px)
    assert badge_top.local_geometry.x == 24.0
    assert badge_top.local_geometry.y == 24.0
    assert badge_top.local_geometry.height == 32.0

    # MetricBlock follows badge with 16px gap
    assert metric_top.local_geometry.x == 24.0
    assert metric_top.local_geometry.y == 24.0 + 32.0 + 16.0  # 72.0
    assert metric_top.local_geometry.width <= card_top.local_geometry.width - 48.0

    # 4. Qualifier and exact display string preservation
    assert metric_top.properties["qualifier"] == ">"
    assert metric_top.properties["display_value"] == ">57%"
    assert metric_top.properties["raw_value"] == 57.0

    metric_bottom = compiled.objects["metric_bottom_50"]
    assert metric_bottom.properties["qualifier"] == "<"
    assert metric_bottom.properties["display_value"] == "<6%"
    assert metric_bottom.properties["raw_value"] == 6.0

    # 5. Connector path resolution
    connector = compiled.objects["connector_divergence"]
    assert connector.connector_path is not None
    assert len(connector.connector_path.points) >= 2
    assert connector.properties["relationship_type"] == "contrasts_with"
    assert connector.properties["label"] == "vs"

    # 6. Callout geometry at bottom zone
    callout = compiled.objects["callout_thesis"]
    assert callout.local_geometry.y > card_top.local_geometry.y  # Situated below top cards
    assert callout.properties["intent"] == "insight"

    # 7. Animation tracks generated
    anim_targets = {anim.object_id for anim in compiled.animation_tracks}
    assert "card_top_10" in anim_targets
    assert "card_bottom_50" in anim_targets
    assert "connector_divergence" in anim_targets


def test_invalid_component_type() -> None:
    """Verifies that unregistered visual components are rejected at spec creation."""
    with pytest.raises(ValueError, match="Unknown visual component_type 'MysteryWidget'"):
        WorldObjectSpec(
            object_id="bad_obj",
            component_type="MysteryWidget",
            beat_ids=["beat_1"],
        )


def test_component_parenting_validation() -> None:
    """Verifies that non-container components cannot parent other objects."""
    beat = StoryboardBeat(
        beat_id="beat_1",
        narration="Test narration for component parenting.",
        semantic_goal="Verify parenting constraints",
    )
    # Badge is a VISUAL_LEAF, not a container
    objects = [
        WorldObjectSpec(
            object_id="parent_badge",
            component_type="Badge",
            semantic_content={"text": "BADGE"},
            beat_ids=["beat_1"],
        ),
        WorldObjectSpec(
            object_id="child_metric",
            component_type="MetricBlock",
            parent_object_id="parent_badge",
            semantic_content={"display_value": "100", "label": "METRIC"},
            beat_ids=["beat_1"],
        ),
    ]
    with pytest.raises(ValueError, match="must be a group primitive or structural container component"):
        VisualWorldSpec(
            world_id="world_bad_parent",
            beats=[beat],
            objects=objects,
        )


def test_component_state_evolution_counter() -> None:
    """Verifies state evolution and counter animation track on MetricBlock."""
    from domain.visual_world import StateChangeEvent, StateChangeKind

    vt = _voice_track()
    beat = StoryboardBeat(
        beat_id="beat_wealth",
        narration=vt.full_script_text,
        semantic_goal="Metric counter update",
        state_change_events=[
            StateChangeEvent(
                event_id="evt_update_val",
                object_id="metric_counter",
                beat_id="beat_wealth",
                kind=StateChangeKind.VALUE,
                from_value=57.0,
                to_value=65.0,
            )
        ],
    )
    objects = [
        WorldObjectSpec(
            object_id="metric_counter",
            component_type="MetricBlock",
            semantic_content={"display_value": "57%", "raw_value": 57.0, "label": "TEST"},
            beat_ids=["beat_wealth"],
        )
    ]
    world = VisualWorldSpec(
        world_id="world_counter",
        beats=[beat],
        objects=objects,
    )
    compiler = WorldCompiler(canvas_config=CanvasConfig(width=1920, height=1080, fps=30))
    compiled = compiler.compile(world, vt)

    assert "metric_counter" in compiled.objects
    # Check that state track and animation track for value update were generated
    state_track = next(st for st in compiled.state_tracks if st.object_id == "metric_counter")
    assert len(state_track.changes) == 1
    assert state_track.changes[0].from_value == 57.0
    assert state_track.changes[0].to_value == 65.0


def test_vertical_flow_connector_auto_sides() -> None:
    """Verifies auto side calculation when source is above target."""
    vt = _voice_track()
    beat = StoryboardBeat(
        beat_id="beat_wealth",
        narration=vt.full_script_text,
        semantic_goal="Connector vertical auto sides",
    )
    objects = [
        WorldObjectSpec(
            object_id="card_upper",
            component_type="SurfaceCard",
            semantic_content={"macro_zone": MacroScreenZone.SPLIT_TOP, "variant": "elevated"},
            beat_ids=["beat_wealth"],
        ),
        WorldObjectSpec(
            object_id="callout_lower",
            component_type="Callout",
            semantic_content={"macro_zone": MacroScreenZone.BOTTOM, "text": "Thesis statement"},
            beat_ids=["beat_wealth"],
        ),
        WorldObjectSpec(
            object_id="connector_down",
            component_type="FlowConnector",
            semantic_content={
                "source_id": "card_upper",
                "target_id": "callout_lower",
                "routing": "straight",
            },
            beat_ids=["beat_wealth"],
        ),
    ]
    world = VisualWorldSpec(
        world_id="world_vert_connector",
        beats=[beat],
        objects=objects,
    )
    compiler = WorldCompiler(canvas_config=CanvasConfig(width=1920, height=1080, fps=30))
    compiled = compiler.compile(world, vt)

    conn = compiled.objects["connector_down"]
    assert conn.connector_path is not None
    # Source is top, target is bottom, so from_point.y should be less than to_point.y
    assert conn.connector_path.from_point.y < conn.connector_path.to_point.y


def test_compile_self_contained_storytelling_composition() -> None:
    """Verifies compilation of self-contained MetricCard split composition with FlowConnector and Callout."""
    vt = _voice_track()
    beat = StoryboardBeat(
        beat_id="beat_wealth",
        narration=vt.full_script_text,
        semantic_goal="Compare wealth share using self-contained cards",
        actions=[
            VisualAction(
                action_id="act_enter_left",
                action_type=VisualActionType.ENTER,
                target_node_id="card_left",
                trigger_word="top",
            ),
            VisualAction(
                action_id="act_enter_right",
                action_type=VisualActionType.ENTER,
                target_node_id="card_right",
                trigger_word="bottom",
            ),
            VisualAction(
                action_id="act_enter_conn",
                action_type=VisualActionType.ENTER,
                target_node_id="connector_vs",
                trigger_word="contrast",
            ),
            VisualAction(
                action_id="act_enter_callout",
                action_type=VisualActionType.ENTER,
                target_node_id="callout_thesis",
                trigger_word="times",
            ),
        ],
    )
    objects = [
        WorldObjectSpec(
            object_id="card_left",
            component_type="MetricCard",
            semantic_content={
                "macro_zone": MacroScreenZone.SPLIT_LEFT,
                "header": "TOP DECILE",
                "display_value": ">57%",
                "label": "SHARE OF NATIONAL WEALTH",
                "tag": "TOP 10%",
                "subtext": "Source: WID 2024",
                "raw_value": 57.0,
                "intent": "accent",
            },
            beat_ids=["beat_wealth"],
        ),
        WorldObjectSpec(
            object_id="card_right",
            component_type="MetricCard",
            semantic_content={
                "macro_zone": MacroScreenZone.SPLIT_RIGHT,
                "header": "BOTTOM HALF",
                "display_value": "<6%",
                "label": "SHARE OF NATIONAL WEALTH",
                "tag": "BOTTOM 50%",
                "subtext": "Source: WID 2024",
                "raw_value": 6.0,
                "intent": "neutral",
            },
            beat_ids=["beat_wealth"],
        ),
        WorldObjectSpec(
            object_id="connector_vs",
            component_type="FlowConnector",
            semantic_content={
                "source_id": "card_left",
                "target_id": "card_right",
                "label": "vs",
                "has_arrow": True,
            },
            beat_ids=["beat_wealth"],
        ),
        WorldObjectSpec(
            object_id="callout_thesis",
            component_type="Callout",
            semantic_content={
                "macro_zone": MacroScreenZone.BOTTOM,
                "text": "This creates a nine point five times divergence in economic power.",
                "attribution": "World Inequality Database 2024",
                "intent": "insight",
            },
            beat_ids=["beat_wealth"],
        ),
    ]

    world = VisualWorldSpec(
        world_id="world_split_composition",
        beats=[beat],
        objects=objects,
    )

    compiler = WorldCompiler(canvas_config=CanvasConfig(width=1920, height=1080, fps=30))
    compiled = compiler.compile(world, vt)

    # All 4 components compiled
    assert "card_left" in compiled.objects
    assert "card_right" in compiled.objects
    assert "connector_vs" in compiled.objects
    assert "callout_thesis" in compiled.objects

    left_geom = compiled.objects["card_left"].local_geometry
    right_geom = compiled.objects["card_right"].local_geometry
    callout_geom = compiled.objects["callout_thesis"].local_geometry

    # Left card is on left side, right card is on right side
    assert left_geom.x < right_geom.x
    assert left_geom.x + left_geom.width <= right_geom.x

    # Connector connects left card to right card
    conn = compiled.objects["connector_vs"]
    assert conn.connector_path is not None
    assert conn.connector_path.from_point.x < conn.connector_path.to_point.x

    # Callout is placed at bottom
    assert callout_geom.y > left_geom.y


def test_black_void_elimination_and_readout_window() -> None:
    """Verifies that late primary entrance is clamped to beat_start and secondary elements are clamped for readability."""
    words = [
        "In", "this", "critical", "financial", "scenario", "we", "observe", "how", "rapid", "rate",
        "hikes", "alter", "the", "entire", "landscape", "of", "borrowing", "and", "liquidity", "across",
        "multiple", "banking", "sectors", "creating", "severe", "duration", "risk", "and", "pressuring", "every",
        "single", "household", "budget", "forcing", "consumers", "to", "radically", "reconsider", "their", "monthly",
        "cash", "flow", "and", "long", "term", "wealth", "accumulation", "strategy", "today", "now"
    ]
    timestamps = [
        WordTimestamp(word=w, start_ms=i * 200, end_ms=(i + 1) * 200)
        for i, w in enumerate(words)
    ]
    text = " ".join(words)
    vt = VoiceTrack(
        voice_id="timing-voice",
        audio_file_name="timing.mp3",
        storage_key="voice/timing.mp3",
        duration_seconds=len(words) * 0.2 + 0.5,
        full_script_text=text,
        word_timestamps=timestamps,
    )

    # Primary card triggered at word "reconsider" (index 37 => 7400ms => frame 222, far into beat)
    # Callout triggered at word "now" (last word, index 49 => 9800ms, only 200ms before beat end)
    beat = StoryboardBeat(
        beat_id="beat_timing",
        narration=text,
        semantic_goal="Verify timely visual entrance",
        macro_zone=MacroScreenZone.CENTER,
        actions=[
            VisualAction(
                action_id="act_hero",
                action_type=VisualActionType.ENTER,
                target_node_id="hero_card",
                trigger_word="reconsider",
            ),
            VisualAction(
                action_id="act_callout",
                action_type=VisualActionType.ENTER,
                target_node_id="tip_callout",
                trigger_word="now",
            ),
        ],
    )

    objects = [
        WorldObjectSpec(
            object_id="hero_card",
            component_type="HeroStat",
            semantic_content={"label": "TOTAL EXPOSURE", "display_value": "₹15 LAKH"},
            beat_ids=["beat_timing"],
            lifecycle=LifecyclePolicy(mode="beat_local", introduced_in_beat="beat_timing"),
        ),
        WorldObjectSpec(
            object_id="tip_callout",
            component_type="Callout",
            semantic_content={"text": "Master amortization to protect your wealth."},
            beat_ids=["beat_timing"],
            lifecycle=LifecyclePolicy(mode="beat_local", introduced_in_beat="beat_timing"),
        ),
    ]

    world = VisualWorldSpec(
        world_id="world_timing_test",
        beats=[beat],
        objects=objects,
    )

    compiler = WorldCompiler(canvas_config=CanvasConfig(width=1920, height=1080, fps=30))
    compiled = compiler.compile(world, vt)

    # 1. Primary HeroStat entrance was clamped to beat_start (frame 0) instead of frame 222
    hero_anchor = next(a for a in compiled.speech_anchors if a.anchor_id == "action:beat_timing:act_hero")
    assert hero_anchor.global_frame == 0
    hero_vis = next(v for v in compiled.visibility_intervals if v.object_id == "hero_card")
    assert hero_vis.start_frame == 0

    # 2. Callout entrance was clamped to beat_end - 60 so viewers have at least 2 seconds (60 frames)
    callout_anchor = next(a for a in compiled.speech_anchors if a.anchor_id == "action:beat_timing:act_callout")
    beat_interval = compiled.beat_intervals[0]
    assert callout_anchor.global_frame <= beat_interval.end_frame - 60


def test_compile_trend_line_chart_component() -> None:
    """Verifies that TrendLineChart compiles cleanly with proper geometry and properties."""
    text = "Over the past five years, the rupee followed a steep downward trajectory."
    words = text.split()
    timestamps = [
        WordTimestamp(word=word, start_ms=index * 150, end_ms=(index + 1) * 150)
        for index, word in enumerate(words)
    ]
    vt = VoiceTrack(
        voice_id="trend-voice",
        audio_file_name="trend.mp3",
        storage_key="voice/trend.mp3",
        duration_seconds=len(words) * 0.15 + 0.5,
        full_script_text=text,
        word_timestamps=timestamps,
    )

    beat = StoryboardBeat(
        beat_id="beat_trend",
        narration=text,
        semantic_goal="Show rupee trajectory",
        macro_zone=MacroScreenZone.CENTER,
        actions=[
            VisualAction(
                action_id="act_trend",
                action_type=VisualActionType.ENTER,
                target_node_id="rupee_trend",
                trigger_word="trajectory",
            )
        ],
    )

    objects = [
        WorldObjectSpec(
            object_id="rupee_trend",
            component_type="TrendLineChart",
            semantic_content={
                "header": "USD / INR 5-YEAR TRAJECTORY",
                "data_points": [
                    {"label": "2020", "value": 73.5},
                    {"label": "2021", "value": 74.3},
                    {"label": "2022", "value": 79.8},
                    {"label": "2023", "value": 82.9},
                    {"label": "2024", "value": 88.5},
                ],
                "trend": "down",
                "highlight_point": {"label": "2024 PEAK", "value": "₹88.50"},
                "subtext": "Historical annual averages",
            },
            beat_ids=["beat_trend"],
            lifecycle=LifecyclePolicy(mode="beat_local", introduced_in_beat="beat_trend"),
        )
    ]

    world = VisualWorldSpec(
        world_id="world_trend_test",
        beats=[beat],
        objects=objects,
    )

    compiler = WorldCompiler(canvas_config=CanvasConfig(width=1920, height=1080, fps=30))
    compiled = compiler.compile(world, vt)

    assert "rupee_trend" in compiled.objects
    obj = compiled.objects["rupee_trend"]
    assert obj.kind == CompiledObjectKind.COMPONENT
    assert obj.component_type == "TrendLineChart"
    assert obj.local_geometry.width == 860.0
    assert obj.local_geometry.height == 400.0
    assert obj.properties["header"] == "USD / INR 5-YEAR TRAJECTORY"
    assert obj.properties["trend"] == "down"
    assert obj.properties["intent"] == "danger"
    assert len(obj.properties["data_points"]) == 5


def test_compile_ranked_bar_chart_component() -> None:
    """Verifies that RankedBarChart compiles directly with auto-derived display_value and accurate geometry."""
    vt = _voice_track()

    beat = StoryboardBeat(
        beat_id="beat_ranking",
        narration=vt.full_script_text,
        semantic_goal="Show ranking of market share",
        macro_zone=MacroScreenZone.CENTER,
        actions=[
            VisualAction(
                action_id="act_enter_ranking",
                action_type=VisualActionType.ENTER,
                target_node_id="upi_ranking",
                trigger_word="top",
            ),
        ],
    )

    objects = [
        WorldObjectSpec(
            object_id="upi_ranking",
            component_type="RankedBarChart",
            semantic_content={
                "header": "UPI MARKET SHARE BY APP",
                "bars": [
                    {"label": "PhonePe", "value": 48.6, "tag": "#1"},
                    {"label": "Google Pay", "value": 36.2},
                    {"label": "Paytm", "value": 8.1},
                ],
                "benchmark_value": 50.0,
                "benchmark_label": "50% Market Cap",
                "subtext": "Monthly transaction volume",
            },
            beat_ids=["beat_ranking"],
            lifecycle=LifecyclePolicy(mode="beat_local", introduced_in_beat="beat_ranking"),
        )
    ]

    world = VisualWorldSpec(
        world_id="world_ranked_bar_test",
        beats=[beat],
        objects=objects,
    )

    compiler = WorldCompiler(canvas_config=CanvasConfig(width=1920, height=1080, fps=30))
    compiled = compiler.compile(world, vt)

    assert "upi_ranking" in compiled.objects
    obj = compiled.objects["upi_ranking"]
    assert obj.kind == CompiledObjectKind.COMPONENT
    assert obj.component_type == "RankedBarChart"
    # Sizing for 3 bars (100 + 3 * 48 + 20 subtext + 15 benchmark = 279.0, width min(1640, 860) = 860.0)
    assert obj.local_geometry.width == 860.0
    assert obj.local_geometry.height == 279.0
    assert obj.properties["header"] == "UPI MARKET SHARE BY APP"
    assert len(obj.properties["bars"]) == 3
    assert obj.properties["bars"][0]["display_value"] == "48.6"
    assert obj.properties["benchmark_value"] == 50.0


def test_compile_allocation_donut_component() -> None:
    """Verifies that AllocationDonut compiles directly with auto-derived display_value and accurate geometry."""
    vt = _voice_track()

    beat = StoryboardBeat(
        beat_id="beat_allocation",
        narration=vt.full_script_text,
        semantic_goal="Show portfolio asset allocation",
        macro_zone=MacroScreenZone.CENTER,
        actions=[
            VisualAction(
                action_id="act_enter_donut",
                action_type=VisualActionType.ENTER,
                target_node_id="asset_donut",
                trigger_word="top",
            ),
        ],
    )

    objects = [
        WorldObjectSpec(
            object_id="asset_donut",
            component_type="AllocationDonut",
            semantic_content={
                "header": "PORTFOLIO ASSET ALLOCATION",
                "slices": [
                    {"label": "Equities", "value": 60.0, "tag": "Core"},
                    {"label": "Debt", "value": 30.0},
                    {"label": "Gold", "value": 10.0, "display_value": "10%"},
                ],
                "center_label": "TOTAL ALLOCATION",
                "center_value": "100%",
                "subtext": "Balanced asset mix",
            },
            beat_ids=["beat_allocation"],
            lifecycle=LifecyclePolicy(mode="beat_local", introduced_in_beat="beat_allocation"),
        )
    ]

    world = VisualWorldSpec(
        world_id="world_donut_test",
        beats=[beat],
        objects=objects,
    )

    compiler = WorldCompiler(canvas_config=CanvasConfig(width=1920, height=1080, fps=30))
    compiled = compiler.compile(world, vt)

    assert "asset_donut" in compiled.objects
    obj = compiled.objects["asset_donut"]
    assert obj.kind == CompiledObjectKind.COMPONENT
    assert obj.component_type == "AllocationDonut"
    # Sizing: max(360, 120 + 3*46) + 20 subtext = 380.0
    assert obj.local_geometry.width == 860.0
    assert obj.local_geometry.height == 380.0
    assert obj.properties["header"] == "PORTFOLIO ASSET ALLOCATION"
    assert len(obj.properties["slices"]) == 3
    assert obj.properties["slices"][1]["display_value"] == "30"
    assert obj.properties["center_value"] == "100%"


def test_compile_waterfall_bridge_component() -> None:
    """Verifies that WaterfallBridge compiles directly with auto-derived display_value and accurate geometry."""
    vt = _voice_track()

    beat = StoryboardBeat(
        beat_id="beat_bridge",
        narration=vt.full_script_text,
        semantic_goal="Show profit margin waterfall",
        macro_zone=MacroScreenZone.CENTER,
        actions=[
            VisualAction(
                action_id="act_enter_bridge",
                action_type=VisualActionType.ENTER,
                target_node_id="margin_bridge",
                trigger_word="top",
            ),
        ],
    )

    objects = [
        WorldObjectSpec(
            object_id="margin_bridge",
            component_type="WaterfallBridge",
            semantic_content={
                "header": "REVENUE TO NET PROFIT BRIDGE",
                "steps": [
                    {"label": "Gross Revenue", "value": 100.0, "is_total": True},
                    {"label": "COGS", "value": -40.0},
                    {"label": "OpEx", "value": -25.0, "display_value": "-₹25 Cr"},
                    {"label": "Net Profit", "value": 35.0, "is_total": True},
                ],
                "subtext": "Operational EBITDA bridge",
            },
            beat_ids=["beat_bridge"],
            lifecycle=LifecyclePolicy(mode="beat_local", introduced_in_beat="beat_bridge"),
        )
    ]

    world = VisualWorldSpec(
        world_id="world_bridge_test",
        beats=[beat],
        objects=objects,
    )

    compiler = WorldCompiler(canvas_config=CanvasConfig(width=1920, height=1080, fps=30))
    compiled = compiler.compile(world, vt)

    assert "margin_bridge" in compiled.objects
    obj = compiled.objects["margin_bridge"]
    assert obj.kind == CompiledObjectKind.COMPONENT
    assert obj.component_type == "WaterfallBridge"
    # Sizing: width min(1640, 880) = 880.0, height 400 + 20 subtext = 420.0
    assert obj.local_geometry.width == 880.0
    assert obj.local_geometry.height == 420.0
    assert obj.properties["header"] == "REVENUE TO NET PROFIT BRIDGE"
    assert len(obj.properties["steps"]) == 4
    assert obj.properties["steps"][1]["display_value"] == "-40"
    assert obj.properties["steps"][2]["display_value"] == "-₹25 Cr"


def test_multiple_elements_and_actions_on_same_trigger_word() -> None:
    """Verifies that multiple elements and multiple actions in the same beat can trigger on the exact same word."""
    vt = _voice_track()
    # Script: "The top ten percent holds over fifty seven percent of all national wealth..."
    # "top" only appears ONCE in the narration.

    beat = StoryboardBeat(
        beat_id="beat_multi_trigger",
        narration=vt.full_script_text,
        semantic_goal="Two elements enter on the exact same word 'top'",
        macro_zone=MacroScreenZone.CENTER,
        actions=[
            # Action 1 on 'top'
            VisualAction(
                action_id="act_enter_elem1",
                action_type=VisualActionType.ENTER,
                target_node_id="elem1",
                trigger_word="top",
                trigger_occurrence=1,
            ),
            # Action 2 on 'top' for a second element
            VisualAction(
                action_id="act_enter_elem2",
                action_type=VisualActionType.ENTER,
                target_node_id="elem2",
                trigger_word="top",
                trigger_occurrence=1,
            ),
            # Action 3 on 'top': a pulse on the first element on that same word
            VisualAction(
                action_id="act_pulse_elem1",
                action_type=VisualActionType.PULSE,
                target_node_id="elem1",
                trigger_word="top",
                trigger_occurrence=1,
            ),
        ],
    )

    objects = [
        WorldObjectSpec(
            object_id="elem1",
            component_type="HeroStat",
            semantic_content={"label": "WEALTH SHARE", "display_value": "57%"},
            beat_ids=["beat_multi_trigger"],
            lifecycle=LifecyclePolicy(mode="beat_local", introduced_in_beat="beat_multi_trigger"),
        ),
        WorldObjectSpec(
            object_id="elem2",
            component_type="Callout",
            semantic_content={"text": "Top wealth concentration"},
            beat_ids=["beat_multi_trigger"],
            lifecycle=LifecyclePolicy(mode="beat_local", introduced_in_beat="beat_multi_trigger"),
        ),
    ]

    world = VisualWorldSpec(
        world_id="world_multi_trigger_test",
        beats=[beat],
        objects=objects,
    )

    compiler = WorldCompiler(canvas_config=CanvasConfig(width=1920, height=1080, fps=30))
    compiled = compiler.compile(world, vt)

    assert "elem1" in compiled.objects
    assert "elem2" in compiled.objects


def test_clamped_trigger_occurrence_compiles_resiliently() -> None:
    """Verifies that an action requesting occurrence 2 of a single-occurrence word gracefully clamps rather than crashing."""
    vt = _voice_track()
    # "top" only appears ONCE in the narration.

    beat = StoryboardBeat(
        beat_id="beat_clamp_trigger",
        narration=vt.full_script_text,
        semantic_goal="Element requests occurrence 2 when only 1 exists",
        macro_zone=MacroScreenZone.CENTER,
        actions=[
            VisualAction(
                action_id="act_enter_clamped",
                action_type=VisualActionType.ENTER,
                target_node_id="stat_clamped",
                trigger_word="top",
                trigger_occurrence=2,  # occurrence 2 requested when only 1 exists!
            ),
        ],
    )

    objects = [
        WorldObjectSpec(
            object_id="stat_clamped",
            component_type="HeroStat",
            semantic_content={"label": "TOP STAT", "display_value": "10%"},
            beat_ids=["beat_clamp_trigger"],
            lifecycle=LifecyclePolicy(mode="beat_local", introduced_in_beat="beat_clamp_trigger"),
        ),
    ]

    world = VisualWorldSpec(
        world_id="world_clamp_test",
        beats=[beat],
        objects=objects,
    )

    compiler = WorldCompiler(canvas_config=CanvasConfig(width=1920, height=1080, fps=30))
    compiled = compiler.compile(world, vt)

    assert "stat_clamped" in compiled.objects


def test_auto_layout_transition_across_beats() -> None:
    """Verifies that an anchor element moving from center to split_left across beats
    automatically receives a Layout state change event and compiles a spring slide track.
    """
    from domain.storyboard_foundation import (
        WorldFoundationSpec,
        StoryboardBeatPlan,
        StoryboardVisualElement,
        StoryboardActionPlan,
    )
    from engines.scene_storyboarder_engine import SceneStoryboarderEngine

    narration_1 = "Ninety-three percent of retail traders lose money. Not a few. Nearly all of them."
    narration_2 = "So where does the money go? Of every hundred rupees lost, forty-one go to costs, and the rest to counterparties."

    foundation = WorldFoundationSpec(
        world_id="test_anchor_slide_world",
        beats=[
            StoryboardBeatPlan(
                beat_id="beat_1",
                narration=narration_1,
                visual_goal="Introduce headline loss",
                visual_strategy="Solo HeroStat in center",
                elements=[
                    StoryboardVisualElement(
                        object_id="retail_stat",
                        component_type="HeroStat",
                        macro_zone=MacroScreenZone.CENTER,
                        role="primary",
                        semantic_content={"label": "RETAIL LOSS", "display_value": "93%"},
                        actions=[
                            StoryboardActionPlan(
                                action_type=VisualActionType.ENTER,
                                trigger_word="percent",
                            )
                        ],
                    )
                ],
            ),
            StoryboardBeatPlan(
                beat_id="beat_2",
                narration=narration_2,
                visual_goal="Show loss destination",
                visual_strategy="Glide anchor to split_left and show donut in split_right",
                elements=[
                    StoryboardVisualElement(
                        object_id="retail_stat",
                        component_type="HeroStat",
                        macro_zone=MacroScreenZone.SPLIT_LEFT,
                        role="supporting",
                        semantic_content={"label": "RETAIL LOSS", "display_value": "93%"},
                    ),
                    StoryboardVisualElement(
                        object_id="loss_donut",
                        component_type="AllocationDonut",
                        macro_zone=MacroScreenZone.SPLIT_RIGHT,
                        role="primary",
                        semantic_content={
                            "header": "DESTINATIONS",
                            "slices": [
                                {"label": "Costs", "value": 41},
                                {"label": "Firms", "value": 59},
                            ],
                        },
                        actions=[
                            StoryboardActionPlan(
                                action_type=VisualActionType.ENTER,
                                trigger_word="hundred",
                            )
                        ],
                    ),
                    StoryboardVisualElement(
                        object_id="connector_flow",
                        component_type="FlowConnector",
                        semantic_content={
                            "source_id": "retail_stat",
                            "target_id": "loss_donut",
                            "relationship_type": "flows_to",
                        },
                        actions=[
                            StoryboardActionPlan(
                                action_type=VisualActionType.APPEAR,
                                trigger_word="rest",
                            )
                        ],
                    ),
                ],
            ),
        ],
    )

    visual_world = SceneStoryboarderEngine.assemble_visual_world(foundation)

    # Verify auto-layout bridge injected layout event into beat_2
    beat_2_events = visual_world.beats[1].state_change_events
    layout_events = [e for e in beat_2_events if e.object_id == "retail_stat" and e.layout_intent is not None]
    assert len(layout_events) == 1, "Expected exactly 1 auto-synthesized layout transition event"
    assert layout_events[0].layout_intent.macro_zone == MacroScreenZone.SPLIT_LEFT

    # Verify compilation succeeds and emits spring layout track
    words = []
    t = 0
    import re
    full_text = f"{narration_1} {narration_2}"
    for tok in re.findall(r"[a-zA-Z0-9'%-]+", full_text):
        words.append(WordTimestamp(word=tok, start_ms=t, end_ms=t + 250))
        t += 300

    vt = VoiceTrack(
        voice_id="test_voice",
        audio_file_name="test.mp3",
        storage_key="test.mp3",
        duration_seconds=t / 1000.0,
        full_script_text=full_text,
        word_timestamps=words,
    )

    compiler = WorldCompiler(canvas_config=CanvasConfig(width=1920, height=1080, fps=30))
    compiled = compiler.compile(visual_world, vt)

    layout_tracks = [t for t in compiled.animation_tracks if t.object_id == "retail_stat" and t.target_property == "layout"]
    assert len(layout_tracks) == 1, "Expected 1 layout animation track for retail_stat"
    assert layout_tracks[0].easing == "spring"
    assert layout_tracks[0].from_value["x"] > layout_tracks[0].to_value["x"], "Should slide from center (higher x) to split_left (lower x)"









