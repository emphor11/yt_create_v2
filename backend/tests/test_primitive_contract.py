import pytest
from pydantic import ValidationError

from domain.primitives.common import (
    CanonicalCapabilityType,
    CANONICAL_CAPABILITY_TYPES,
    PrimitiveIdentity,
    PrimitiveLayout,
    PrimitiveStyle,
    PrimitiveTiming,
    PrimitiveAnimation,
    SpringConfig,
    BoxShadow,
)
from domain.primitives.props import (
    TextProps,
    NumberProps,
    ShapeProps,
    IconProps,
    ConnectorProps,
    ConnectorAnchor,
    ConnectorLabel,
    ImageProps,
    VideoProps,
    BarProps,
    LineProps,
    LinePoint,
    PointProps,
    SegmentProps,
    ProgressProps,
    GroupProps,
)
from domain.primitives.spec import PrimitiveSpec, PrimitiveTreeSpec
from registries.primitive_registry import PrimitiveRegistry, PrimitiveRegistryError


# =============================================================================
# 1. CANONICAL REGISTRY TESTS
# =============================================================================

def test_canonical_type_list():
    assert len(CANONICAL_CAPABILITY_TYPES) == 13
    expected = [
        "text", "number", "shape", "icon", "connector",
        "image", "video", "bar", "line", "point",
        "segment", "progress", "group"
    ]
    assert set(CANONICAL_CAPABILITY_TYPES) == set(expected)


def test_registry_rejects_high_level_compositions():
    disallowed = ["card", "Card", "kpi", "KPIGrid", "hero", "MetricHero", "timeline", "splitcomparison"]
    for name in disallowed:
        with pytest.raises(PrimitiveRegistryError, match="high-level composite pattern"):
            PrimitiveRegistry.normalize_type(name)


def test_registry_rejects_unknown_type():
    with pytest.raises(PrimitiveRegistryError, match="Unknown primitive capability type"):
        PrimitiveRegistry.normalize_type("unknown_gadget")


# =============================================================================
# 2. CAPABILITY PROPS, STATES & BEHAVIORS TESTS
# =============================================================================

def test_text_capability():
    valid = {"content": "Hello World", "font_size": 36, "align": "center"}
    props = PrimitiveRegistry.validate_primitive_props("text", valid)
    assert props.content == "Hello World"
    assert props.font_size == 36

    assert PrimitiveRegistry.validate_state_change("text", "update_content")
    assert PrimitiveRegistry.validate_state_change("text", "update_highlight")
    assert PrimitiveRegistry.validate_behavior("text", "appear")
    assert PrimitiveRegistry.validate_behavior("text", "highlight")
    assert PrimitiveRegistry.validate_behavior("text", "transform")

    # Invalid align
    with pytest.raises(ValidationError):
        PrimitiveRegistry.validate_primitive_props("text", {"content": "Hi", "align": "upside_down"})


def test_number_capability():
    valid = {"value": 50000.0, "prefix": "₹", "precision": 0}
    props = PrimitiveRegistry.validate_primitive_props("number", valid)
    assert props.value == 50000.0
    assert props.prefix == "₹"

    assert PrimitiveRegistry.validate_state_change("number", "count_to")
    assert PrimitiveRegistry.validate_state_change("number", "set_delta")
    assert PrimitiveRegistry.validate_behavior("number", "count_up")
    assert PrimitiveRegistry.validate_behavior("number", "impact_settle")

    # Missing value
    with pytest.raises(ValidationError):
        PrimitiveRegistry.validate_primitive_props("number", {"prefix": "$"})


def test_shape_capability():
    valid = {"shape_type": "pill", "corner_radius": 16}
    props = PrimitiveRegistry.validate_primitive_props("shape", valid)
    assert props.shape_type == "pill"

    assert PrimitiveRegistry.validate_state_change("shape", "resize")
    assert PrimitiveRegistry.validate_state_change("shape", "recolor")
    assert PrimitiveRegistry.validate_state_change("shape", "elevate")
    assert PrimitiveRegistry.validate_behavior("shape", "scale_spring")
    assert PrimitiveRegistry.validate_behavior("shape", "pulse_glow")

    # Invalid shape_type
    with pytest.raises(ValidationError):
        PrimitiveRegistry.validate_primitive_props("shape", {"shape_type": "triangle"})


def test_icon_capability():
    valid = {"name": "briefcase", "size": 32, "color": "#38bdf8"}
    props = PrimitiveRegistry.validate_primitive_props("icon", valid)
    assert props.name == "briefcase"

    assert PrimitiveRegistry.validate_state_change("icon", "change_icon")
    assert PrimitiveRegistry.validate_state_change("icon", "change_color")
    assert PrimitiveRegistry.validate_behavior("icon", "bloom")
    assert PrimitiveRegistry.validate_behavior("icon", "pop")

    # Missing name
    with pytest.raises(ValidationError):
        PrimitiveRegistry.validate_primitive_props("icon", {"size": 32})


def test_connector_capability():
    valid = {
        "from_anchor": {"target_id": "box_a", "side": "right"},
        "to_anchor": {"target_id": "box_b", "side": "left"},
        "routing": "orthogonal_elbow",
        "has_arrow": True,
        "label": {"text": "leads to", "font_size": 14},
    }
    props = PrimitiveRegistry.validate_primitive_props("connector", valid)
    assert props.from_anchor.target_id == "box_a"
    assert props.routing == "orthogonal_elbow"
    assert props.label.text == "leads to"

    assert PrimitiveRegistry.validate_state_change("connector", "redirect")
    assert PrimitiveRegistry.validate_state_change("connector", "activate")
    assert PrimitiveRegistry.validate_behavior("connector", "draw_path")
    assert PrimitiveRegistry.validate_behavior("connector", "label_reveal")

    # Invalid routing
    with pytest.raises(ValidationError):
        PrimitiveRegistry.validate_primitive_props("connector", {
            "from_anchor": {}, "to_anchor": {}, "routing": "zigzag"
        })


def test_image_capability():
    valid = {"source": "assets/photo.jpg", "object_fit": "cover"}
    props = PrimitiveRegistry.validate_primitive_props("image", valid)
    assert props.source == "assets/photo.jpg"

    assert PrimitiveRegistry.validate_state_change("image", "swap_source")
    assert PrimitiveRegistry.validate_behavior("image", "ken_burns")
    assert PrimitiveRegistry.validate_behavior("image", "fade_in")

    with pytest.raises(ValidationError):
        PrimitiveRegistry.validate_primitive_props("image", {"source": "photo.jpg", "object_fit": "stretch_diagonal"})


def test_video_capability():
    valid = {"source": "assets/bg.mp4", "loop": True, "muted": True, "playback_rate": 1.0}
    props = PrimitiveRegistry.validate_primitive_props("video", valid)
    assert props.loop is True

    assert PrimitiveRegistry.validate_state_change("video", "seek")
    assert PrimitiveRegistry.validate_behavior("video", "looping_playback")

    with pytest.raises(ValidationError):
        PrimitiveRegistry.validate_primitive_props("video", {})


def test_bar_capability():
    valid = {"orientation": "horizontal", "fill_percentage": 0.75, "max_length": 400.0}
    props = PrimitiveRegistry.validate_primitive_props("bar", valid)
    assert props.fill_percentage == 0.75

    assert PrimitiveRegistry.validate_state_change("bar", "update_fill")
    assert PrimitiveRegistry.validate_state_change("bar", "change_polarity")
    assert PrimitiveRegistry.validate_behavior("bar", "grow")

    with pytest.raises(ValidationError):
        PrimitiveRegistry.validate_primitive_props("bar", {"fill_percentage": 1.5})


def test_line_capability():
    valid = {
        "points": [{"x": 0, "y": 100}, {"x": 50, "y": 80}, {"x": 100, "y": 20}],
        "curve_type": "monotone_cubic",
    }
    props = PrimitiveRegistry.validate_primitive_props("line", valid)
    assert len(props.points) == 3

    assert PrimitiveRegistry.validate_state_change("line", "append_point")
    assert PrimitiveRegistry.validate_state_change("line", "morph_points")
    assert PrimitiveRegistry.validate_behavior("line", "draw_line")


def test_point_capability():
    valid = {"x": 120.0, "y": 450.0, "radius": 8.0, "label": "Milestone A"}
    props = PrimitiveRegistry.validate_primitive_props("point", valid)
    assert props.x == 120.0

    assert PrimitiveRegistry.validate_state_change("point", "move_to")
    assert PrimitiveRegistry.validate_state_change("point", "pulse")
    assert PrimitiveRegistry.validate_behavior("point", "beacon_pulse")


def test_segment_capability():
    valid = {"parent_track_id": "total_bar", "start_ratio": 0.2, "length_ratio": 0.5, "fill": "#10b981"}
    props = PrimitiveRegistry.validate_primitive_props("segment", valid)
    assert props.start_ratio == 0.2

    assert PrimitiveRegistry.validate_state_change("segment", "resize_ratio")
    assert PrimitiveRegistry.validate_behavior("segment", "slide_and_expand")

    with pytest.raises(ValidationError):
        PrimitiveRegistry.validate_primitive_props("segment", {
            "parent_track_id": "b1", "start_ratio": -0.1, "length_ratio": 0.5
        })


def test_progress_capability():
    valid = {"variant": "radial_ring", "progress_ratio": 0.82, "radius": 75.0}
    props = PrimitiveRegistry.validate_primitive_props("progress", valid)
    assert props.progress_ratio == 0.82

    assert PrimitiveRegistry.validate_state_change("progress", "set_progress")
    assert PrimitiveRegistry.validate_behavior("progress", "sweep")


def test_group_capability():
    valid = {"child_ids": ["c1", "c2"], "layout_flow": "column", "gap": 16.0}
    props = PrimitiveRegistry.validate_primitive_props("group", valid)
    assert props.layout_flow == "column"
    assert props.child_ids == ["c1", "c2"]

    assert PrimitiveRegistry.validate_state_change("group", "shift")
    assert PrimitiveRegistry.validate_state_change("group", "fade_group")
    assert PrimitiveRegistry.validate_behavior("group", "group_cascade")


# =============================================================================
# 3. PRIMITIVE SPEC & ANIMATION VALIDATION
# =============================================================================

def test_primitive_spec_serialization():
    anim = PrimitiveAnimation(
        action_id="fade_in_num",
        trigger_frame=15,
        duration_frames=30,
        behavior="appear",
        target_property="value",
        from_value=0,
        to_value=100,
        spring_config=SpringConfig(damping=16, stiffness=120),
    )
    spec = PrimitiveSpec(
        identity=PrimitiveIdentity(id="num_01", type=CanonicalCapabilityType.NUMBER),
        layout=PrimitiveLayout(x=100, y=200, width=300, height=80),
        style=PrimitiveStyle(fill="#ffffff", opacity=1.0),
        timing=PrimitiveTiming(enter_frame=0, visible=True),
        props={"value": 100, "prefix": "$"},
        animations=[anim],
    )
    raw = spec.model_dump()
    reconstructed = PrimitiveSpec.model_validate(raw)
    assert reconstructed.identity.id == "num_01"
    assert reconstructed.props["prefix"] == "$"
    assert reconstructed.animations[0].trigger_frame == 15


# =============================================================================
# 4. COMPOSITE INTEGRATION-LEVEL TESTS (NO HIGH-LEVEL TEMPLATES)
# =============================================================================

def test_composition_a_salary_card():
    """
    Prove that a 'Salary Card' can be cleanly composed using only:
    group -> shape, icon, text, number
    """
    card_group = PrimitiveSpec(
        identity=PrimitiveIdentity(id="card_group", type=CanonicalCapabilityType.GROUP),
        layout=PrimitiveLayout(x=100, y=100, width=400, height=220),
        props={"child_ids": ["bg_shape", "card_icon", "card_title", "card_num"], "layout_flow": "column"},
    )
    bg_shape = PrimitiveSpec(
        identity=PrimitiveIdentity(id="bg_shape", type=CanonicalCapabilityType.SHAPE, parent_id="card_group"),
        style=PrimitiveStyle(fill="rgba(24, 24, 27, 0.9)", corner_radius=16),
        props={"shape_type": "rectangle"},
    )
    card_icon = PrimitiveSpec(
        identity=PrimitiveIdentity(id="card_icon", type=CanonicalCapabilityType.ICON, parent_id="card_group"),
        props={"name": "briefcase", "size": 28},
    )
    card_title = PrimitiveSpec(
        identity=PrimitiveIdentity(id="card_title", type=CanonicalCapabilityType.TEXT, parent_id="card_group"),
        props={"content": "Gross Salary", "font_size": 24},
    )
    card_num = PrimitiveSpec(
        identity=PrimitiveIdentity(id="card_num", type=CanonicalCapabilityType.NUMBER, parent_id="card_group"),
        props={"value": 50000, "prefix": "₹"},
    )

    tree = PrimitiveTreeSpec(
        scene_id="scene_hook",
        duration_frames=180,
        root_primitive_ids=["card_group"],
        primitives={
            "card_group": card_group,
            "bg_shape": bg_shape,
            "card_icon": card_icon,
            "card_title": card_title,
            "card_num": card_num,
        },
    )
    assert tree.scene_id == "scene_hook"
    assert len(tree.primitives) == 5


def test_composition_b_two_sided_comparison():
    """
    Prove that a 'Split Comparison' can be represented entirely by:
    group -> group (left card), group (right card), connector (arrow)
    """
    root = PrimitiveSpec(
        identity=PrimitiveIdentity(id="split_group", type=CanonicalCapabilityType.GROUP),
        layout=PrimitiveLayout(),
        props={"child_ids": ["left_col", "right_col", "arrow"], "layout_flow": "row", "gap": 80},
    )
    left_col = PrimitiveSpec(
        identity=PrimitiveIdentity(id="left_col", type=CanonicalCapabilityType.GROUP, parent_id="split_group"),
        props={"child_ids": ["left_txt"]},
    )
    left_txt = PrimitiveSpec(
        identity=PrimitiveIdentity(id="left_txt", type=CanonicalCapabilityType.TEXT, parent_id="left_col"),
        props={"content": "Option A: Renting"},
    )
    right_col = PrimitiveSpec(
        identity=PrimitiveIdentity(id="right_col", type=CanonicalCapabilityType.GROUP, parent_id="split_group"),
        props={"child_ids": ["right_txt"]},
    )
    right_txt = PrimitiveSpec(
        identity=PrimitiveIdentity(id="right_txt", type=CanonicalCapabilityType.TEXT, parent_id="right_col"),
        props={"content": "Option B: Buying"},
    )
    arrow = PrimitiveSpec(
        identity=PrimitiveIdentity(id="arrow", type=CanonicalCapabilityType.CONNECTOR, parent_id="split_group"),
        props={
            "from_anchor": {"target_id": "left_col", "side": "right"},
            "to_anchor": {"target_id": "right_col", "side": "left"},
            "routing": "straight",
            "has_arrow": True,
        },
    )

    tree = PrimitiveTreeSpec(
        scene_id="scene_vs",
        duration_frames=240,
        root_primitive_ids=["split_group"],
        primitives={
            "split_group": root,
            "left_col": left_col,
            "left_txt": left_txt,
            "right_col": right_col,
            "right_txt": right_txt,
            "arrow": arrow,
        },
    )
    assert "arrow" in tree.primitives


def test_composition_c_number_transformation():
    """
    Prove that a 'Number Transformation' operates on initial state + animated transform action.
    """
    num = PrimitiveSpec(
        identity=PrimitiveIdentity(id="salary_num", type=CanonicalCapabilityType.NUMBER),
        props={"value": 50000, "start_value": 0, "prefix": "₹"},
        current_state={"current_value": 50000},
        animations=[
            PrimitiveAnimation(
                action_id="count_init",
                trigger_frame=0,
                duration_frames=30,
                behavior="appear",
                target_property="value",
                from_value=0,
                to_value=50000,
            ),
            PrimitiveAnimation(
                action_id="rent_drop",
                trigger_frame=60,
                duration_frames=30,
                behavior="transform",
                target_property="value",
                from_value=50000,
                to_value=30000,
            ),
        ],
    )
    tree = PrimitiveTreeSpec(
        scene_id="scene_transform",
        duration_frames=120,
        root_primitive_ids=["salary_num"],
        primitives={"salary_num": num},
    )
    assert len(tree.primitives["salary_num"].animations) == 2


def test_composition_d_progress_visual():
    """
    Prove that a gauge/progress visual can be composed of:
    progress -> text
    """
    prog = PrimitiveSpec(
        identity=PrimitiveIdentity(id="gauge", type=CanonicalCapabilityType.PROGRESS),
        props={"variant": "radial_ring", "progress_ratio": 0.75, "radius": 80.0},
    )
    lbl = PrimitiveSpec(
        identity=PrimitiveIdentity(id="lbl", type=CanonicalCapabilityType.TEXT),
        props={"content": "75% Capacity", "font_size": 24},
    )
    tree = PrimitiveTreeSpec(
        scene_id="scene_prog",
        duration_frames=90,
        root_primitive_ids=["gauge", "lbl"],
        primitives={"gauge": prog, "lbl": lbl},
    )
    assert len(tree.root_primitive_ids) == 2


def test_composition_e_data_story():
    """
    Prove that a chart/data story can be composed of:
    group -> bar, bar, bar, text
    """
    chart_grp = PrimitiveSpec(
        identity=PrimitiveIdentity(id="chart_grp", type=CanonicalCapabilityType.GROUP),
        layout=PrimitiveLayout(),
        props={"child_ids": ["bar_1", "bar_2", "bar_3", "legend"], "layout_flow": "column", "gap": 16},
    )
    bar_1 = PrimitiveSpec(
        identity=PrimitiveIdentity(id="bar_1", type=CanonicalCapabilityType.BAR, parent_id="chart_grp"),
        props={"fill_percentage": 0.4, "max_length": 500.0, "foreground_color": "#38bdf8"},
    )
    bar_2 = PrimitiveSpec(
        identity=PrimitiveIdentity(id="bar_2", type=CanonicalCapabilityType.BAR, parent_id="chart_grp"),
        props={"fill_percentage": 0.7, "max_length": 500.0, "foreground_color": "#3b82f6"},
    )
    bar_3 = PrimitiveSpec(
        identity=PrimitiveIdentity(id="bar_3", type=CanonicalCapabilityType.BAR, parent_id="chart_grp"),
        props={"fill_percentage": 0.95, "max_length": 500.0, "foreground_color": "#1d4ed8"},
    )
    legend = PrimitiveSpec(
        identity=PrimitiveIdentity(id="legend", type=CanonicalCapabilityType.TEXT, parent_id="chart_grp"),
        props={"content": "Growth by Quarter", "font_size": 20},
    )

    tree = PrimitiveTreeSpec(
        scene_id="scene_data",
        duration_frames=180,
        root_primitive_ids=["chart_grp"],
        primitives={
            "chart_grp": chart_grp,
            "bar_1": bar_1,
            "bar_2": bar_2,
            "bar_3": bar_3,
            "legend": legend,
        },
    )
    assert len(tree.primitives["chart_grp"].props["child_ids"]) == 4


# =============================================================================
# 5. TREE INTEGRITY & CYCLE DETECTION
# =============================================================================

def test_tree_rejects_missing_child():
    grp = PrimitiveSpec(
        identity=PrimitiveIdentity(id="g1", type=CanonicalCapabilityType.GROUP),
        props={"child_ids": ["missing_child"]},
    )
    with pytest.raises(ValueError, match="references non-existent child"):
        PrimitiveTreeSpec(
            scene_id="s1",
            duration_frames=60,
            root_primitive_ids=["g1"],
            primitives={"g1": grp},
        )


def test_tree_rejects_missing_parent():
    item = PrimitiveSpec(
        identity=PrimitiveIdentity(id="item", type=CanonicalCapabilityType.TEXT, parent_id="missing_parent"),
        props={"content": "orphan"},
    )
    with pytest.raises(ValueError, match="references non-existent parent"):
        PrimitiveTreeSpec(
            scene_id="s1",
            duration_frames=60,
            root_primitive_ids=[],
            primitives={"item": item},
        )


def test_tree_rejects_cyclic_hierarchy():
    g1 = PrimitiveSpec(
        identity=PrimitiveIdentity(id="g1", type=CanonicalCapabilityType.GROUP, parent_id="g2"),
        props={"child_ids": []},
    )
    g2 = PrimitiveSpec(
        identity=PrimitiveIdentity(id="g2", type=CanonicalCapabilityType.GROUP, parent_id="g1"),
        props={"child_ids": []},
    )
    with pytest.raises(ValueError, match="Cyclic parent-child reference"):
        PrimitiveTreeSpec(
            scene_id="s1",
            duration_frames=60,
            root_primitive_ids=[],
            primitives={"g1": g1, "g2": g2},
        )
