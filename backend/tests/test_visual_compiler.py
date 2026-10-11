"""Unit and Fixture Tests for the Deterministic Visual Compiler.

Tests all 15 compiler requirements and verifies the 2-scene salary/rent fixture.
"""
from __future__ import annotations

import pytest
from compiler.connector_resolver import ConnectorResolver
from compiler.macro_layout import MacroLayoutResolver
from compiler.micro_layout import MicroLayoutEngine
from compiler.models import (
    CanvasConfig,
    CompiledProjectResult,
    CompiledSceneResult,
    Rect,
    VisualCompilerError,
)
from compiler.persistence_manager import PersistenceManager
from compiler.timing_resolver import TimingResolver
from compiler.token_resolver import TokenResolver
from compiler.visual_compiler import VisualCompiler
from domain.primitives.common import (
    CanonicalCapabilityType,
    PrimitiveIdentity,
    PrimitiveLayout,
    PrimitiveStyle,
    PrimitiveTiming,
)
from domain.primitives.spec import PrimitiveSpec, PrimitiveTreeSpec
from domain.storyboard import (
    ContainerFlow,
    FlowAlignment,
    FlowJustification,
    MacroScreenZone,
    MicroLayoutFlow,
    MotionPreset,
    ProjectStoryboardSpec,
    SceneStoryboardSpec,
    SemanticColorRole,
    SemanticElevationRole,
    SemanticRadiusRole,
    SemanticRelationship,
    SemanticSpacing,
    SemanticStyleIntent,
    SemanticTypographyRole,
    StoryboardNode,
    VisualAction,
    VisualActionType,
)
from domain.voice_track import VoiceTrack, WordTimestamp


# =============================================================================
# Helper Fixtures
# =============================================================================
@pytest.fixture
def canvas_config() -> CanvasConfig:
    return CanvasConfig(
        width=1920,
        height=1080,
        fps=30,
        safe_margin_x=120.0,
        safe_margin_y=80.0,
    )


@pytest.fixture
def token_resolver() -> TokenResolver:
    return TokenResolver()


@pytest.fixture
def salary_rent_voice_track() -> VoiceTrack:
    """Authoritative VoiceTrack for the 2-scene fixture."""
    words = [
        # Scene 1: "You got a ten percent raise, but rent increased twenty two percent,"
        ("You", 0, 200),
        ("got", 200, 420),
        ("a", 420, 510),
        ("ten", 510, 850),
        ("percent", 850, 1250),
        ("raise", 1250, 1680),
        ("but", 1680, 1880),
        ("rent", 1880, 2200),
        ("increased", 2200, 2750),
        ("twenty", 2750, 3100),
        ("two", 3100, 3450),
        ("percent", 3450, 3900),
        # Scene 2: "so your purchasing power dropped three point five percent."
        ("so", 4100, 4320),
        ("your", 4320, 4550),
        ("purchasing", 4550, 5050),
        ("power", 5050, 5450),
        ("dropped", 5450, 5950),
        ("three", 5950, 6300),
        ("point", 6300, 6600),
        ("five", 6600, 6950),
        ("percent", 6950, 7400),
    ]
    timestamps = [
        WordTimestamp(word=w, start_ms=s, end_ms=e)
        for w, s, e in words
    ]
    script_text = (
        "You got a ten percent raise, but rent increased twenty two percent, "
        "so your purchasing power dropped three point five percent."
    )
    return VoiceTrack(
        voice_id="Danielle",
        audio_file_name="salary_rent.mp3",
        storage_key="voice/salary_rent.mp3",
        duration_seconds=7.8,
        full_script_text=script_text,
        word_timestamps=timestamps,
    )


# =============================================================================
# Test 1: Center Macro Zone Resolution
# =============================================================================
def test_macro_layout_center_zone(canvas_config: CanvasConfig):
    safe = canvas_config.safe_rect
    rect = MacroLayoutResolver.resolve_zone(MacroScreenZone.CENTER, canvas_config)

    assert rect.x >= safe.x
    assert rect.y >= safe.y
    assert rect.right <= safe.right
    assert rect.bottom <= safe.bottom
    # Check centered alignment within safe area
    assert pytest.approx(rect.center_x, abs=0.5) == safe.center_x
    assert pytest.approx(rect.center_y, abs=0.5) == safe.center_y
    assert rect.width == round(safe.width * 0.70, 2)
    assert rect.height == round(safe.height * 0.80, 2)


# =============================================================================
# Test 2: Split Layout Resolution
# =============================================================================
def test_macro_layout_split_columns(canvas_config: CanvasConfig):
    safe = canvas_config.safe_rect
    left_rect = MacroLayoutResolver.resolve_zone(MacroScreenZone.SPLIT_LEFT, canvas_config)
    right_rect = MacroLayoutResolver.resolve_zone(MacroScreenZone.SPLIT_RIGHT, canvas_config)

    # Both must be inside safe region
    assert left_rect.x >= safe.x
    assert right_rect.right <= safe.right
    # Must be completely non-overlapping horizontally
    assert left_rect.right <= right_rect.x
    # Symmetrical width
    assert left_rect.width == right_rect.width
    assert left_rect.height == right_rect.height


# =============================================================================
# Test 3: Nested Group Auto-Layout Cascading
# =============================================================================
def test_micro_layout_nested_group(token_resolver: TokenResolver):
    engine = MicroLayoutEngine(token_resolver)

    # Parent group: column flow with padding=24, gap=16
    parent = StoryboardNode(
        id="parent_group",
        type=CanonicalCapabilityType.GROUP,
        flow=MicroLayoutFlow(
            flow=ContainerFlow.COLUMN,
            gap=SemanticSpacing.SM,  # 16px
            padding=SemanticSpacing.MD,  # 24px
            alignment=FlowAlignment.START,
        ),
        children=[
            StoryboardNode(
                id="child_header",
                type=CanonicalCapabilityType.TEXT,
                props={"content": "Header Text", "font_size": 32.0, "line_height": 1.2},
            ),
            # Nested row group: row flow with padding=8, gap=8
            StoryboardNode(
                id="nested_row",
                type=CanonicalCapabilityType.GROUP,
                flow=MicroLayoutFlow(
                    flow=ContainerFlow.ROW,
                    gap=SemanticSpacing.XS,  # 8px
                    padding=SemanticSpacing.XS,  # 8px
                    alignment=FlowAlignment.CENTER,
                ),
                children=[
                    StoryboardNode(
                        id="nested_icon",
                        type=CanonicalCapabilityType.ICON,
                        props={"name": "trending-up", "size": 32.0},
                    ),
                    StoryboardNode(
                        id="nested_number",
                        type=CanonicalCapabilityType.NUMBER,
                        props={"value": 10.0, "font_size": 48.0},
                    ),
                ],
            ),
        ],
    )

    allocated = Rect(x=100.0, y=100.0, width=600.0, height=400.0)
    layouts = engine.layout_node_tree(parent, allocated)

    assert "parent_group" in layouts
    assert "child_header" in layouts
    assert "nested_row" in layouts
    assert "nested_icon" in layouts
    assert "nested_number" in layouts

    parent_layout = layouts["parent_group"]
    header_layout = layouts["child_header"]
    nested_row_layout = layouts["nested_row"]
    icon_layout = layouts["nested_icon"]
    num_layout = layouts["nested_number"]

    # Child header starts inside parent padding
    assert header_layout.x == parent_layout.x + 24.0
    assert header_layout.y == parent_layout.y + 24.0

    # Nested row starts below child header + gap (16px)
    expected_row_y = header_layout.y + header_layout.height + 16.0
    assert pytest.approx(nested_row_layout.y, abs=0.1) == expected_row_y

    # In nested row: icon and number sit side-by-side
    assert icon_layout.x < num_layout.x
    assert pytest.approx(icon_layout.x + icon_layout.width + 8.0, abs=0.1) == num_layout.x


# =============================================================================
# Test 4: Semantic Spacing Scale Mapping
# =============================================================================
def test_semantic_spacing_scale(token_resolver: TokenResolver):
    assert token_resolver.resolve_spacing(SemanticSpacing.NONE) == 0.0
    assert token_resolver.resolve_spacing(SemanticSpacing.XS) == 8.0
    assert token_resolver.resolve_spacing(SemanticSpacing.SM) == 16.0
    assert token_resolver.resolve_spacing(SemanticSpacing.MD) == 24.0
    assert token_resolver.resolve_spacing(SemanticSpacing.LG) == 32.0
    assert token_resolver.resolve_spacing(SemanticSpacing.XL) == 48.0


# =============================================================================
# Test 5: Token Resolver Translates Semantic Styles to PrimitiveStyle
# =============================================================================
def test_token_resolver_style(token_resolver: TokenResolver):
    intent = SemanticStyleIntent(
        fill_role=SemanticColorRole.SURFACE,
        stroke_role=SemanticColorRole.BORDER,
        radius_role=SemanticRadiusRole.CARD,
        elevation_role=SemanticElevationRole.CARD,
        opacity=0.95,
    )
    style = token_resolver.resolve_style(intent)

    assert style.fill == "#18181b"
    assert style.stroke == "#3f3f46"
    assert style.stroke_width == 2.0
    assert style.corner_radius == 16.0
    assert style.shadow is not None
    assert style.shadow.blur == 16.0
    assert style.opacity == 0.95


# =============================================================================
# Test 6: Connector Bounds and Anchor Points Match Primitives
# =============================================================================
def test_connector_bounds_and_anchors():
    primitives: dict[str, PrimitiveSpec] = {
        "source_card": PrimitiveSpec(
            identity=PrimitiveIdentity(id="source_card", type=CanonicalCapabilityType.SHAPE),
            layout=PrimitiveLayout(x=100.0, y=200.0, width=300.0, height=100.0),
            props={"shape_type": "rectangle"},
        ),
        "target_card": PrimitiveSpec(
            identity=PrimitiveIdentity(id="target_card", type=CanonicalCapabilityType.SHAPE),
            layout=PrimitiveLayout(x=600.0, y=200.0, width=300.0, height=100.0),
            props={"shape_type": "rectangle"},
        ),
        "flow_connector": PrimitiveSpec(
            identity=PrimitiveIdentity(id="flow_connector", type=CanonicalCapabilityType.CONNECTOR),
            layout=PrimitiveLayout(),
            props={
                "from_anchor": {"target_id": "source_card", "side": "right"},
                "to_anchor": {"target_id": "target_card", "side": "left"},
            },
        ),
    }

    ConnectorResolver.resolve_connectors("scene_test", primitives)
    conn = primitives["flow_connector"]

    # Source right side: x = 100 + 300 = 400, y = 200 + 50 = 250
    assert conn.props["from_anchor"]["x"] == 400.0
    assert conn.props["from_anchor"]["y"] == 250.0

    # Target left side: x = 600, y = 200 + 50 = 250
    assert conn.props["to_anchor"]["x"] == 600.0
    assert conn.props["to_anchor"]["y"] == 250.0

    # Enclosing connector bounds
    assert conn.layout.x == 400.0
    assert conn.layout.y == 250.0
    assert conn.layout.width == 200.0
    assert conn.layout.height == 1.0


# =============================================================================
# Test 7: Spoken Trigger Words Resolve to Exact Frame Numbers
# =============================================================================
def test_timing_resolver_frame_formula(salary_rent_voice_track: VoiceTrack):
    resolver = TimingResolver(salary_rent_voice_track, fps=30)

    # "ten" starts at 510ms -> round(510 / 1000 * 30) = round(15.3) = 15
    res_ten = resolver.resolve_trigger(
        scene_id="s1",
        scene_narration="You got a ten percent raise",
        trigger_word="ten",
        trigger_occurrence=1,
        scene_start_ms=0,
    )
    assert res_ten.start_ms == 510
    assert res_ten.trigger_frame == round(510 / 1000.0 * 30)
    assert res_ten.trigger_frame == 15

    # "twenty" starts at 2750ms -> round(2750 / 1000 * 30) = round(82.5) = 82 or 83
    res_twenty = resolver.resolve_trigger(
        scene_id="s1",
        scene_narration="increased twenty two percent",
        trigger_word="twenty",
        trigger_occurrence=1,
        scene_start_ms=0,
    )
    assert res_twenty.start_ms == 2750
    assert res_twenty.trigger_frame == round(2750 / 1000.0 * 30)


# =============================================================================
# Test 8: Repeated Trigger Occurrence Resolves Correctly
# =============================================================================
def test_repeated_trigger_occurrence(salary_rent_voice_track: VoiceTrack):
    resolver = TimingResolver(salary_rent_voice_track, fps=30)
    narration = "You got a ten percent raise, but rent increased twenty two percent,"

    # First "percent" starts at 850ms
    res1 = resolver.resolve_trigger(
        scene_id="s1",
        scene_narration=narration,
        trigger_word="percent",
        trigger_occurrence=1,
        scene_start_ms=0,
    )
    assert res1.start_ms == 850
    assert res1.trigger_frame == round(850 / 1000.0 * 30)

    # Second "percent" starts at 3450ms
    res2 = resolver.resolve_trigger(
        scene_id="s1",
        scene_narration=narration,
        trigger_word="percent",
        trigger_occurrence=2,
        scene_start_ms=0,
    )
    assert res2.start_ms == 3450
    assert res2.trigger_frame == round(3450 / 1000.0 * 30)
    assert res2.trigger_frame > res1.trigger_frame


# =============================================================================
# Test 9: Unresolvable Trigger Words Raise Descriptive Errors
# =============================================================================
def test_unresolvable_trigger_fails(salary_rent_voice_track: VoiceTrack):
    resolver = TimingResolver(salary_rent_voice_track, fps=30)

    # Trigger word not in scene narration
    with pytest.raises(VisualCompilerError, match="Unresolved required trigger word 'inflation'"):
        resolver.resolve_trigger(
            scene_id="s1",
            scene_narration="You got a ten percent raise",
            trigger_word="inflation",
            trigger_occurrence=1,
        )

    # Requested occurrence 3 when only 2 exist
    with pytest.raises(VisualCompilerError, match="requests occurrence 3, but only appears 2"):
        resolver.resolve_trigger(
            scene_id="s1",
            scene_narration="ten percent raise, twenty two percent",
            trigger_word="percent",
            trigger_occurrence=3,
        )


# =============================================================================
# Test 10: Object Transformations Compile to Keyframed Animations
# =============================================================================
def test_object_transformations_compile_to_animations(salary_rent_voice_track: VoiceTrack):
    compiler = VisualCompiler()

    scene = SceneStoryboardSpec(
        scene_id="scene_transform",
        narration="increased twenty two percent",
        root_nodes=[
            StoryboardNode(
                id="rent_number",
                type=CanonicalCapabilityType.NUMBER,
                props={"value": 15.0},
            )
        ],
        actions=[
            VisualAction(
                action_id="act_update",
                target_node_id="rent_number",
                action_type=VisualActionType.UPDATE_VALUE,
                trigger_word="twenty",
                new_value=22.0,
                motion_preset=MotionPreset.IMPACT,
            ),
            VisualAction(
                action_id="act_transform",
                target_node_id="rent_number",
                action_type=VisualActionType.TRANSFORM,
                trigger_word="increased",
                target_property="scale",
                new_value=1.2,
                motion_preset=MotionPreset.SETTLE,
            ),
        ],
    )

    result = compiler.compile_scene(scene, salary_rent_voice_track, scene_start_ms=2000)
    prim = result.tree_spec.primitives["rent_number"]

    assert len(prim.animations) == 2
    update_anim = [a for a in prim.animations if a.action_id == "act_update"][0]
    transform_anim = [a for a in prim.animations if a.action_id == "act_transform"][0]

    assert update_anim.behavior == "update_value"
    assert update_anim.from_value == 15.0
    assert update_anim.to_value == 22.0
    assert update_anim.spring_config is not None

    assert transform_anim.behavior == "transform"
    assert transform_anim.target_property == "scale"
    assert transform_anim.to_value == 1.2
    assert prim.current_state["current_value"] == 22.0


# =============================================================================
# Test 11: Cross-Scene Persistent Objects Suppress Entrance in Later Scenes
# =============================================================================
def test_persistent_objects_suppress_entrance(salary_rent_voice_track: VoiceTrack):
    compiler = VisualCompiler()
    persistence_mgr = PersistenceManager()

    # Scene 1: salary appears at "ten"
    scene_1 = SceneStoryboardSpec(
        scene_id="scene_01",
        narration="You got a ten percent raise",
        root_nodes=[
            StoryboardNode(
                id="salary_metric_s1",
                type=CanonicalCapabilityType.NUMBER,
                persistence_key="salary_persistent_key",
                persistence_scope="cross_scene",
                props={"value": 10.0},
            )
        ],
        actions=[
            VisualAction(
                action_id="act_appear_s1",
                target_node_id="salary_metric_s1",
                action_type=VisualActionType.APPEAR,
                trigger_word="ten",
            )
        ],
    )

    # Scene 2: salary continues into scene 2; has redundant appear action + highlight action
    scene_2 = SceneStoryboardSpec(
        scene_id="scene_02",
        narration="so your purchasing power dropped three point five percent.",
        root_nodes=[
            StoryboardNode(
                id="salary_metric_s2",
                type=CanonicalCapabilityType.NUMBER,
                persistence_key="salary_persistent_key",
                persistence_scope="cross_scene",
                props={"value": 10.0},
            )
        ],
        actions=[
            # This appearance action MUST be suppressed
            VisualAction(
                action_id="act_redundant_appear",
                target_node_id="salary_metric_s2",
                action_type=VisualActionType.APPEAR,
                trigger_word="purchasing",
            ),
            # This highlight action must be compiled
            VisualAction(
                action_id="act_highlight",
                target_node_id="salary_metric_s2",
                action_type=VisualActionType.HIGHLIGHT,
                trigger_word="dropped",
            ),
        ],
    )

    res_1 = compiler.compile_scene(
        scene_1, salary_rent_voice_track, persistence_manager=persistence_mgr, scene_start_ms=0
    )
    res_2 = compiler.compile_scene(
        scene_2, salary_rent_voice_track, persistence_manager=persistence_mgr, scene_start_ms=4000
    )

    prim_s1 = res_1.tree_spec.primitives["salary_metric_s1"]
    prim_s2 = res_2.tree_spec.primitives["salary_metric_s2"]

    # Scene 1 has appear animation
    assert len(prim_s1.animations) == 1
    assert prim_s1.animations[0].behavior == "appear"
    assert prim_s1.timing.enter_frame > 0

    # Scene 2 suppressed the appear action; only highlight remains!
    assert len(prim_s2.animations) == 1
    assert prim_s2.animations[0].behavior == "highlight"
    assert prim_s2.timing.enter_frame == 0  # Already visible at frame 0


# =============================================================================
# Test 12: Unknown or Disallowed Primitive Types are Rejected
# =============================================================================
def test_unknown_primitive_types_rejected():
    # 1. Disallowed composition type at domain model creation
    with pytest.raises((ValueError, Exception), match="Input should be 'text'|Cannot use 'kpi_card'"):
        StoryboardNode(
            id="bad_node",
            type="kpi_card",  # type: ignore
        )

    # 2. Defense-in-depth: Compiler rejects disallowed composition types
    compiler = VisualCompiler()

    class MockDisallowedNode:
        id = "card_1"
        type = "kpi_card"
        children = []

    with pytest.raises(VisualCompilerError, match="Disallowed composition type 'kpi_card'"):
        compiler._collect_and_validate_nodes("s_bad", [MockDisallowedNode()])  # type: ignore

    # 3. Compiler rejects unknown capability types
    class MockUnknownNode:
        id = "unknown_1"
        type = "floating_particles"
        children = []

    with pytest.raises(VisualCompilerError, match="Unknown capability type 'floating_particles'"):
        compiler._collect_and_validate_nodes("s_bad", [MockUnknownNode()])  # type: ignore


# =============================================================================
# Test 13: Invalid Group Child References Raise Compiler Errors
# =============================================================================
def test_invalid_group_child_references_fail():
    # Tree validation directly
    with pytest.raises(ValueError, match="Group 'group_1' references non-existent child 'ghost_node'"):
        PrimitiveTreeSpec(
            scene_id="s1",
            duration_frames=100,
            root_primitive_ids=["group_1"],
            primitives={
                "group_1": PrimitiveSpec(
                    identity=PrimitiveIdentity(id="group_1", type=CanonicalCapabilityType.GROUP),
                    props={"child_ids": ["ghost_node"]},
                )
            },
        )


# =============================================================================
# Test 14: Semantic Relationships are Preserved in Output Metadata
# =============================================================================
def test_semantic_relationships_preserved(salary_rent_voice_track: VoiceTrack):
    compiler = VisualCompiler()

    rel = SemanticRelationship(
        source_id="salary_metric",
        relation="compared_with",
        target_id="rent_metric",
        visual_representation="side_by_side_contrast",
    )

    scene = SceneStoryboardSpec(
        scene_id="s_rel",
        narration="You got a ten percent raise, but rent increased twenty two percent,",
        root_nodes=[
            StoryboardNode(
                id="salary_metric",
                type=CanonicalCapabilityType.NUMBER,
                props={"value": 10.0},
            ),
            StoryboardNode(
                id="rent_metric",
                type=CanonicalCapabilityType.NUMBER,
                props={"value": 22.0},
            ),
        ],
        relationships=[rel],
    )

    result = compiler.compile_scene(scene, salary_rent_voice_track)
    assert len(result.relationships) == 1
    assert result.relationships[0].source_id == "salary_metric"
    assert result.relationships[0].relation == "compared_with"
    assert result.relationships[0].target_id == "rent_metric"


# =============================================================================
# Test 15: Full Salary/Rent 2-Scene Storyboard Fixture Compiles End-to-End
# =============================================================================
def test_full_salary_rent_fixture(salary_rent_voice_track: VoiceTrack):
    """End-to-end integration fixture compiling the canonical salary/rent narrative."""
    # Scene 1: Contrast between salary (+10%) and rent (+22%)
    scene_1 = SceneStoryboardSpec(
        scene_id="scene_01",
        narration="You got a ten percent raise, but rent increased twenty two percent,",
        source_intent_ids=["intent_salary_vs_rent"],
        root_nodes=[
            # Left Card: Salary Raise
            StoryboardNode(
                id="salary_card",
                type=CanonicalCapabilityType.GROUP,
                persistence_key="salary_persistent_entity",
                persistence_scope="cross_scene",
                macro_zone=MacroScreenZone.SPLIT_LEFT,
                flow=MicroLayoutFlow(
                    flow=ContainerFlow.COLUMN,
                    gap=SemanticSpacing.SM,
                    padding=SemanticSpacing.MD,
                    alignment=FlowAlignment.START,
                ),
                style=SemanticStyleIntent(
                    fill_role=SemanticColorRole.SURFACE,
                    stroke_role=SemanticColorRole.BORDER,
                    radius_role=SemanticRadiusRole.CARD,
                    elevation_role=SemanticElevationRole.CARD,
                ),
                children=[
                    StoryboardNode(
                        id="salary_label",
                        type=CanonicalCapabilityType.TEXT,
                        style=SemanticStyleIntent(
                            text_color_role=SemanticColorRole.SECONDARY_TEXT,
                            typography_role=SemanticTypographyRole.EYEBROW,
                        ),
                        props={"content": "Salary Raise"},
                    ),
                    StoryboardNode(
                        id="salary_number",
                        type=CanonicalCapabilityType.NUMBER,
                        style=SemanticStyleIntent(
                            text_color_role=SemanticColorRole.SUCCESS,
                            typography_role=SemanticTypographyRole.DISPLAY,
                        ),
                        props={"value": 10.0, "prefix": "+", "suffix": "%"},
                    ),
                ],
            ),
            # Right Card: Rent Increase
            StoryboardNode(
                id="rent_card",
                type=CanonicalCapabilityType.GROUP,
                persistence_key="rent_persistent_entity",
                persistence_scope="cross_scene",
                macro_zone=MacroScreenZone.SPLIT_RIGHT,
                flow=MicroLayoutFlow(
                    flow=ContainerFlow.COLUMN,
                    gap=SemanticSpacing.SM,
                    padding=SemanticSpacing.MD,
                    alignment=FlowAlignment.START,
                ),
                style=SemanticStyleIntent(
                    fill_role=SemanticColorRole.SURFACE,
                    stroke_role=SemanticColorRole.BORDER,
                    radius_role=SemanticRadiusRole.CARD,
                    elevation_role=SemanticElevationRole.CARD,
                ),
                children=[
                    StoryboardNode(
                        id="rent_label",
                        type=CanonicalCapabilityType.TEXT,
                        style=SemanticStyleIntent(
                            text_color_role=SemanticColorRole.SECONDARY_TEXT,
                            typography_role=SemanticTypographyRole.EYEBROW,
                        ),
                        props={"content": "Rent Growth"},
                    ),
                    StoryboardNode(
                        id="rent_number",
                        type=CanonicalCapabilityType.NUMBER,
                        style=SemanticStyleIntent(
                            text_color_role=SemanticColorRole.DANGER,
                            typography_role=SemanticTypographyRole.DISPLAY,
                        ),
                        props={"value": 22.0, "prefix": "+", "suffix": "%"},
                    ),
                ],
            ),
        ],
        actions=[
            VisualAction(
                action_id="act_salary_appear",
                target_node_id="salary_card",
                action_type=VisualActionType.APPEAR,
                trigger_word="ten",
                motion_preset=MotionPreset.IMPACT,
            ),
            VisualAction(
                action_id="act_rent_appear",
                target_node_id="rent_card",
                action_type=VisualActionType.APPEAR,
                trigger_word="twenty",
                motion_preset=MotionPreset.IMPACT,
            ),
        ],
        relationships=[
            SemanticRelationship(
                source_id="salary_card",
                relation="compared_with",
                target_id="rent_card",
                visual_representation="split_comparison",
                description="Salary growth contrasted with steeper rent growth",
            )
        ],
    )

    # Scene 2: Consequence on Purchasing Power (-3.5%)
    scene_2 = SceneStoryboardSpec(
        scene_id="scene_02",
        narration="so your purchasing power dropped three point five percent.",
        source_intent_ids=["intent_purchasing_power_drop"],
        root_nodes=[
            # Persistent Rent Card continues from scene 1
            StoryboardNode(
                id="rent_card_s2",
                type=CanonicalCapabilityType.GROUP,
                persistence_key="rent_persistent_entity",
                persistence_scope="cross_scene",
                macro_zone=MacroScreenZone.TOP,
                flow=MicroLayoutFlow(
                    flow=ContainerFlow.COLUMN,
                    gap=SemanticSpacing.XS,
                    padding=SemanticSpacing.SM,
                ),
                style=SemanticStyleIntent(
                    fill_role=SemanticColorRole.SURFACE,
                    stroke_role=SemanticColorRole.BORDER,
                    radius_role=SemanticRadiusRole.CARD,
                ),
                children=[
                    StoryboardNode(
                        id="rent_s2_number",
                        type=CanonicalCapabilityType.NUMBER,
                        style=SemanticStyleIntent(text_color_role=SemanticColorRole.DANGER),
                        props={"value": 22.0, "suffix": "%"},
                    ),
                ],
            ),
            # Purchasing Power Consequence Card
            StoryboardNode(
                id="purchasing_power_card",
                type=CanonicalCapabilityType.GROUP,
                macro_zone=MacroScreenZone.CENTER,
                flow=MicroLayoutFlow(
                    flow=ContainerFlow.COLUMN,
                    gap=SemanticSpacing.SM,
                    padding=SemanticSpacing.MD,
                    alignment=FlowAlignment.CENTER,
                ),
                style=SemanticStyleIntent(
                    fill_role=SemanticColorRole.SURFACE_ELEVATED,
                    stroke_role=SemanticColorRole.DANGER,
                    radius_role=SemanticRadiusRole.CARD,
                    elevation_role=SemanticElevationRole.GLOW,
                ),
                children=[
                    StoryboardNode(
                        id="pp_label",
                        type=CanonicalCapabilityType.TEXT,
                        style=SemanticStyleIntent(
                            text_color_role=SemanticColorRole.PRIMARY_TEXT,
                            typography_role=SemanticTypographyRole.SUBHEADLINE,
                        ),
                        props={"content": "Real Purchasing Power"},
                    ),
                    StoryboardNode(
                        id="pp_number",
                        type=CanonicalCapabilityType.NUMBER,
                        style=SemanticStyleIntent(
                            text_color_role=SemanticColorRole.DANGER,
                            typography_role=SemanticTypographyRole.DISPLAY,
                        ),
                        props={"value": -3.5, "suffix": "%", "precision": 1},
                    ),
                ],
            ),
            # Connector linking rent growth to purchasing power decline
            StoryboardNode(
                id="cause_connector",
                type=CanonicalCapabilityType.CONNECTOR,
                style=SemanticStyleIntent(stroke_role=SemanticColorRole.DANGER),
                props={
                    "from_anchor": {"target_id": "rent_card_s2", "side": "bottom"},
                    "to_anchor": {"target_id": "purchasing_power_card", "side": "top"},
                    "routing": "curved",
                    "has_arrow": True,
                },
            ),
        ],
        actions=[
            VisualAction(
                action_id="act_pp_appear",
                target_node_id="purchasing_power_card",
                action_type=VisualActionType.APPEAR,
                trigger_word="dropped",
                motion_preset=MotionPreset.IMPACT,
            ),
            VisualAction(
                action_id="act_pp_pulse",
                target_node_id="pp_number",
                action_type=VisualActionType.PULSE,
                trigger_word="point",
                motion_preset=MotionPreset.SETTLE,
            ),
        ],
        relationships=[
            SemanticRelationship(
                source_id="rent_card_s2",
                relation="contributes_to",
                target_id="purchasing_power_card",
                visual_representation="causal_connector",
                description="Higher rent directly causes purchasing power to drop",
            )
        ],
    )

    project_storyboard = ProjectStoryboardSpec(
        scenes=[scene_1, scene_2],
    )

    compiler = VisualCompiler()
    result: CompiledProjectResult = compiler.compile(project_storyboard, salary_rent_voice_track)

    # 1. Project level assertions
    assert len(result.scenes) == 2
    assert result.total_duration_frames > 0
    assert result.total_duration_seconds > 0.0
    assert "scene_01" in result.scene_trees
    assert "scene_02" in result.scene_trees

    # 2. Scene 1 assertions
    s1_res = result.scenes[0]
    s1_tree = s1_res.tree_spec
    assert s1_tree.scene_id == "scene_01"
    assert "salary_card" in s1_tree.root_primitive_ids
    assert "rent_card" in s1_tree.root_primitive_ids
    assert "salary_label" in s1_tree.primitives
    assert "salary_number" in s1_tree.primitives
    assert "rent_label" in s1_tree.primitives
    assert "rent_number" in s1_tree.primitives

    salary_card_layout = s1_tree.primitives["salary_card"].layout
    rent_card_layout = s1_tree.primitives["rent_card"].layout
    # Split left and split right must not overlap
    assert salary_card_layout.x + (salary_card_layout.width or 0) <= rent_card_layout.x

    # 3. Scene 2 assertions
    s2_res = result.scenes[1]
    s2_tree = s2_res.tree_spec
    assert s2_tree.scene_id == "scene_02"
    assert "rent_card_s2" in s2_tree.primitives
    assert "purchasing_power_card" in s2_tree.primitives
    assert "cause_connector" in s2_tree.primitives

    # Persistent rent card has enter_frame == 0 in scene 2
    assert s2_tree.primitives["rent_card_s2"].timing.enter_frame == 0

    # Connector properly linked
    conn = s2_tree.primitives["cause_connector"]
    assert conn.props["from_anchor"]["target_id"] == "rent_card_s2"
    assert conn.props["to_anchor"]["target_id"] == "purchasing_power_card"
    assert conn.layout.width > 0
    assert conn.layout.height > 0

    # Relationships verified
    assert len(s1_res.relationships) == 1
    assert s1_res.relationships[0].relation == "compared_with"
    assert len(s2_res.relationships) == 1
    assert s2_res.relationships[0].relation == "contributes_to"
