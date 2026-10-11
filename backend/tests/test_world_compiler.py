"""Focused tests for the isolated world compiler."""
from __future__ import annotations

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
    SemanticRelationship,
    SemanticSpacing,
    VisualAction,
    VisualActionType,
)
from domain.voice_track import VoiceTrack, WordTimestamp
from domain.visual_world import (
    LifecyclePolicy,
    SourceReference,
    SpeechAnchor,
    StateChangeEvent,
    StateChangeKind,
    StoryboardBeat,
    TransitionIntent,
    VisualWorldSpec,
    WorldObjectSpec,
)


def _voice_track() -> VoiceTrack:
    text = (
        "The loan starts at eight point five percent and the EMI is forty three "
        "thousand three hundred ninety one rupees. The rate rises to ten point "
        "five percent. The EMI becomes forty nine thousand nine hundred nineteen rupees."
    )
    words = text.split()
    timestamps = [
        WordTimestamp(word=word, start_ms=index * 100, end_ms=(index + 1) * 100)
        for index, word in enumerate(words)
    ]
    return VoiceTrack(
        voice_id="test-voice",
        audio_file_name="loan.mp3",
        storage_key="voice/loan.mp3",
        duration_seconds=4.0,
        full_script_text=text,
        word_timestamps=timestamps,
    )


def _group_flow(flow: ContainerFlow, gap: SemanticSpacing, padding: SemanticSpacing) -> dict:
    return {
        "flow": flow.value,
        "alignment": FlowAlignment.CENTER.value,
        "justification": FlowJustification.CENTER.value,
        "gap": gap.value,
        "padding": padding.value,
    }


def _loan_world() -> VisualWorldSpec:
    all_beats = ["establish", "rate_change", "emi_change"]
    return VisualWorldSpec(
        world_id="loan_world",
        beats=[
            StoryboardBeat(
                beat_id="establish",
                source_intent_ids=["intent_loan"],
                source_references=[
                    SourceReference(kind="visual_intent", reference_id="intent_loan")
                ],
                narration=(
                    "The loan starts at eight point five percent and the EMI is forty three "
                    "thousand three hundred ninety one rupees."
                ),
                semantic_goal="Establish the loan, rate, and EMI.",
                macro_zone=MacroScreenZone.CENTER,
                layout_flow=MicroLayoutFlow(
                    flow=ContainerFlow.COLUMN,
                    alignment=FlowAlignment.CENTER,
                    justification=FlowJustification.CENTER,
                    gap=SemanticSpacing.SM,
                    padding=SemanticSpacing.MD,
                ),
                actions=[
                    VisualAction(
                        action_id="reveal_loan",
                        target_node_id="loan_panel",
                        action_type=VisualActionType.ENTER,
                        trigger_word="loan",
                    )
                ],
            ),
            StoryboardBeat(
                beat_id="rate_change",
                source_intent_ids=["intent_loan"],
                narration="The rate rises to ten point five percent.",
                semantic_goal="Transform the existing rate.",
                macro_zone=MacroScreenZone.CENTER,
                state_change_events=[
                    StateChangeEvent(
                        event_id="rate_to_high",
                        object_id="rate",
                        beat_id="rate_change",
                        kind=StateChangeKind.VALUE,
                        target_property="value",
                        from_value=8.5,
                        to_value=10.5,
                        speech_anchor=SpeechAnchor(
                            anchor_id="rate_rises",
                            beat_id="rate_change",
                            text="rises",
                        ),
                    )
                ],
                transition_intent=TransitionIntent(
                    kind="transform",
                    preserve_object_ids=["loan_panel", "rate", "emi"],
                ),
            ),
            StoryboardBeat(
                beat_id="emi_change",
                source_intent_ids=["intent_loan"],
                narration="The EMI becomes forty nine thousand nine hundred nineteen rupees.",
                semantic_goal="Transform the existing EMI.",
                macro_zone=MacroScreenZone.CENTER,
                state_change_events=[
                    StateChangeEvent(
                        event_id="emi_to_high",
                        object_id="emi",
                        beat_id="emi_change",
                        kind=StateChangeKind.VALUE,
                        target_property="value",
                        from_value=43391,
                        to_value=49919,
                        speech_anchor=SpeechAnchor(
                            anchor_id="emi_becomes",
                            beat_id="emi_change",
                            text="becomes",
                        ),
                    )
                ],
            ),
        ],
        objects=[
            WorldObjectSpec(
                object_id="loan_panel",
                primitive_type=CanonicalCapabilityType.GROUP,
                semantic_content={
                    "layout_flow": _group_flow(
                        ContainerFlow.COLUMN, SemanticSpacing.SM, SemanticSpacing.MD
                    )
                },
                initial_state={"role": "home loan"},
                lifecycle=LifecyclePolicy(mode="persistent", introduced_in_beat="establish"),
                beat_ids=all_beats,
            ),
            WorldObjectSpec(
                object_id="loan_surface",
                primitive_type=CanonicalCapabilityType.SHAPE,
                semantic_content={
                    "fill_parent": True,
                    "style_intent": {
                        "fill_role": "surface_elevated",
                        "radius_role": "card",
                        "elevation_role": "card",
                    },
                },
                parent_object_id="loan_panel",
                lifecycle=LifecyclePolicy(mode="persistent", introduced_in_beat="establish"),
                beat_ids=all_beats,
            ),
            WorldObjectSpec(
                object_id="metrics_group",
                primitive_type=CanonicalCapabilityType.GROUP,
                semantic_content={
                    "layout_flow": _group_flow(
                        ContainerFlow.ROW, SemanticSpacing.SM, SemanticSpacing.XS
                    )
                },
                parent_object_id="loan_panel",
                lifecycle=LifecyclePolicy(mode="persistent", introduced_in_beat="establish"),
                beat_ids=all_beats,
            ),
            WorldObjectSpec(
                object_id="rate",
                primitive_type=CanonicalCapabilityType.NUMBER,
                semantic_content={
                    "style_intent": {
                        "text_color_role": "accent",
                        "typography_role": "subheadline",
                    }
                },
                initial_state={"value": 8.5, "suffix": "%", "precision": 1},
                parent_object_id="metrics_group",
                lifecycle=LifecyclePolicy(mode="persistent", introduced_in_beat="establish"),
                beat_ids=all_beats,
            ),
            WorldObjectSpec(
                object_id="emi",
                primitive_type=CanonicalCapabilityType.NUMBER,
                semantic_content={
                    "style_intent": {
                        "text_color_role": "primary_text",
                        "typography_role": "subheadline",
                    }
                },
                initial_state={"value": 43391, "prefix": "₹"},
                parent_object_id="metrics_group",
                lifecycle=LifecyclePolicy(mode="persistent", introduced_in_beat="establish"),
                beat_ids=all_beats,
            ),
            WorldObjectSpec(
                object_id="rate_to_emi",
                primitive_type=CanonicalCapabilityType.CONNECTOR,
                semantic_content={
                    "overlay": True,
                    "from_anchor": {"target_id": "rate", "side": "right"},
                    "to_anchor": {"target_id": "emi", "side": "left"},
                    "routing": "curved",
                },
                parent_object_id="loan_panel",
                lifecycle=LifecyclePolicy(mode="persistent", introduced_in_beat="establish"),
                beat_ids=all_beats,
            ),
        ],
        relationships=[
            SemanticRelationship(
                source_id="rate",
                relation="causes",
                target_id="emi",
                visual_representation="state_transformation",
            )
        ],
    )


def _compiler() -> WorldCompiler:
    return WorldCompiler(
        canvas_config=CanvasConfig(width=1920, height=1080, fps=30),
    )


def test_complete_loan_world_compiles_once_with_stable_ids() -> None:
    compiled = _compiler().compile(_loan_world(), _voice_track())

    assert compiled.world_id == "loan_world"
    assert compiled.total_duration_frames == 120
    assert set(compiled.primitives) == {
        "loan_panel",
        "loan_surface",
        "metrics_group",
        "rate",
        "emi",
        "rate_to_emi",
    }
    assert {track.object_id for track in compiled.lifecycle_tracks} == set(compiled.primitives)
    assert {track.object_id for track in compiled.state_tracks} == set(compiled.primitives)
    assert [interval.beat_id for interval in compiled.beat_intervals] == [
        "establish",
        "rate_change",
        "emi_change",
    ]


def test_voice_anchor_resolves_to_exact_global_frame() -> None:
    compiled = _compiler().compile(_loan_world(), _voice_track())
    anchor = next(anchor for anchor in compiled.speech_anchors if anchor.anchor_id == "rate_rises")

    assert anchor.start_ms == 2200
    assert anchor.global_frame == round(2.2 * 30)
    assert any(
        animation.object_id == "rate" and animation.trigger_frame == anchor.global_frame
        for animation in compiled.animation_tracks
    )


def test_geometry_is_parent_local_and_nested() -> None:
    compiled = _compiler().compile(_loan_world(), _voice_track())

    panel = compiled.primitives["loan_panel"].local_geometry
    nested_group = compiled.primitives["metrics_group"].local_geometry
    rate = compiled.primitives["rate"].local_geometry

    assert panel.x > 0
    assert nested_group.x < panel.width
    assert rate.x < nested_group.width
    assert rate.x != panel.x + 40
    assert rate.x >= 0


def test_parent_local_contract_never_reemits_parent_offset() -> None:
    world = _loan_world().model_copy(deep=True)
    for beat in world.beats:
        beat.macro_zone = MacroScreenZone.LEFT
    world.objects[0].semantic_content["macro_zone"] = "left"
    compiler = WorldCompiler(
        canvas_config=CanvasConfig(
            width=1920,
            height=1080,
            fps=30,
            safe_margin_x=500,
            safe_margin_y=80,
        )
    )

    compiled = compiler.compile(world, _voice_track())
    panel = compiled.primitives["loan_panel"].local_geometry
    rate = compiled.primitives["rate"].local_geometry

    assert panel.x == 500
    assert rate.x == 8
    assert rate.x != 540


def test_group_is_structural_and_surface_is_explicit_shape() -> None:
    compiled = _compiler().compile(_loan_world(), _voice_track())

    panel = compiled.primitives["loan_panel"]
    surface = compiled.primitives["loan_surface"]
    assert panel.primitive_type == CanonicalCapabilityType.GROUP
    assert panel.style.fill is None
    assert surface.primitive_type == CanonicalCapabilityType.SHAPE
    assert surface.style.fill == "#27272a"
    assert surface.local_geometry.width == panel.local_geometry.width
    assert surface.local_geometry.height == panel.local_geometry.height


def test_connector_is_fully_resolved_without_target_ids() -> None:
    compiled = _compiler().compile(_loan_world(), _voice_track())
    connector = compiled.primitives["rate_to_emi"]

    assert connector.connector_path is not None
    assert connector.connector_path.parent_object_id == "loan_panel"
    assert len(connector.connector_path.points) >= 2
    assert connector.connector_path.from_point.x == pytest.approx(574.48)
    assert connector.connector_path.from_point.y == pytest.approx(53.6)
    assert connector.connector_path.to_point.x == pytest.approx(590.48)
    assert connector.connector_path.to_point.y == pytest.approx(53.6)
    assert connector.connector_path.points[0].x == pytest.approx(574.48)
    assert connector.connector_path.points[-1].x == pytest.approx(590.48)
    assert connector.properties == {"has_arrow": True}
    assert "target_id" not in str(connector.model_dump())


def test_unresolved_speech_anchor_fails_without_timing_fallback() -> None:
    world = _loan_world().model_copy(deep=True)
    world.beats[1].state_change_events[0].speech_anchor.text = "not spoken"

    with pytest.raises(WorldCompilerError, match="was not found"):
        _compiler().compile(world, _voice_track())


def test_zone_overlap_is_rejected() -> None:
    world = _loan_world().model_copy(deep=True)
    world.objects[0].semantic_content["macro_zone"] = "center"
    second_root = WorldObjectSpec(
        object_id="overlap_root",
        primitive_type=CanonicalCapabilityType.GROUP,
        semantic_content={"macro_zone": "left"},
        lifecycle=LifecyclePolicy(mode="persistent", introduced_in_beat="establish"),
        beat_ids=["establish", "rate_change", "emi_change"],
    )
    world.objects.append(second_root)

    with pytest.raises(WorldCompilerError, match="overlap"):
        _compiler().compile(world, _voice_track())


def test_intrinsic_overflow_is_rejected() -> None:
    world = _loan_world().model_copy(deep=True)
    for beat in world.beats:
        beat.macro_zone = MacroScreenZone.TOP
    world.objects[0].semantic_content["layout_flow"] = _group_flow(
        ContainerFlow.COLUMN, SemanticSpacing.MD, SemanticSpacing.MD
    )
    world.objects.append(
        WorldObjectSpec(
            object_id="overflow_text",
            primitive_type=CanonicalCapabilityType.TEXT,
            semantic_content={"content": "x" * 1000},
            parent_object_id="loan_panel",
            lifecycle=LifecyclePolicy(mode="persistent", introduced_in_beat="establish"),
            beat_ids=["establish", "rate_change", "emi_change"],
        )
    )

    with pytest.raises(WorldCompilerError, match="overflow"):
        _compiler().compile(world, _voice_track())


def test_painted_group_is_rejected() -> None:
    world = _loan_world().model_copy(deep=True)
    world.objects[0].semantic_content["style_intent"] = {"fill_role": "surface"}

    with pytest.raises(WorldCompilerError, match="painted styles"):
        _compiler().compile(world, _voice_track())


def test_compiled_world_serialization_roundtrip() -> None:
    compiled = _compiler().compile(_loan_world(), _voice_track())
    reconstructed = CompiledWorld.model_validate(compiled.model_dump())

    assert reconstructed == compiled


def test_compiled_world_contains_canvas_config_and_explicit_terminal_hold() -> None:
    compiled = _compiler().compile(_loan_world(), _voice_track())

    assert compiled.canvas_config.width == 1920
    assert compiled.canvas_config.height == 1080
    assert compiled.canvas_config.fps == 30
    assert compiled.terminal_hold is not None
    assert compiled.terminal_hold.start_frame == 114
    assert compiled.terminal_hold.end_frame == 120


def test_visibility_is_explicit_for_immediate_late_entry_and_persistent_objects() -> None:
    world = _loan_world().model_copy(deep=True)
    world.objects[3].lifecycle = LifecyclePolicy(
        mode="persistent", introduced_in_beat="rate_change"
    )
    compiled = _compiler().compile(world, _voice_track())

    intervals = {
        interval.object_id: (interval.start_frame, interval.end_frame)
        for interval in compiled.visibility_intervals
    }
    assert intervals["loan_panel"] == (3, 120)
    assert intervals["rate"] == (60, 120)
    assert intervals["emi"] == (0, 120)


def test_visibility_is_explicit_for_an_object_with_an_exit() -> None:
    world = _loan_world().model_copy(deep=True)
    world.objects[-1].lifecycle = LifecyclePolicy(
        mode="until_exit",
        introduced_in_beat="establish",
        exit_event_id="connector_exit",
    )
    world.beats[-1].state_change_events.append(
        StateChangeEvent(
            event_id="connector_exit",
            object_id="rate_to_emi",
            beat_id="emi_change",
            kind=StateChangeKind.VISIBILITY,
            target_property="visible",
            visible=False,
        )
    )

    compiled = _compiler().compile(world, _voice_track())
    connector_interval = next(
        interval
        for interval in compiled.visibility_intervals
        if interval.object_id == "rate_to_emi"
    )
    assert (connector_interval.start_frame, connector_interval.end_frame) == (0, 84)


def test_state_target_property_and_null_from_value_are_compiler_resolved() -> None:
    world = _loan_world().model_copy(deep=True)
    world.beats[1].state_change_events[0].from_value = None

    compiled = _compiler().compile(world, _voice_track())
    change = next(
        change
        for track in compiled.state_tracks
        for change in track.changes
        if change.event_id == "rate_to_high"
    )
    animation = next(
        animation
        for animation in compiled.animation_tracks
        if animation.animation_id == "rate_to_high"
    )

    assert change.target_property == "value"
    assert change.from_value == 8.5
    assert animation.target_property == "value"
    assert animation.from_value == 8.5


def test_animation_semantics_are_concrete_and_deterministic() -> None:
    compiled = _compiler().compile(_loan_world(), _voice_track())

    assert all(animation.easing in {"linear", "spring", "ease-out", "bezier"} for animation in compiled.animation_tracks)
    assert all(animation.from_value is not None for animation in compiled.animation_tracks)
    reveal = next(animation for animation in compiled.animation_tracks if animation.animation_id == "reveal_loan")
    assert reveal.target_property == "opacity"
    assert reveal.from_value == 0.0
    assert reveal.to_value == 1.0
    assert reveal.easing == "spring"
    assert reveal.motion_preset == "reveal"


def test_compiled_facts_have_single_authoritative_sources() -> None:
    compiled = _compiler().compile(_loan_world(), _voice_track())

    for primitive in compiled.primitives.values():
        assert "initial_state" not in primitive.model_dump()
        if primitive.primitive_type == CanonicalCapabilityType.GROUP:
            assert primitive.properties == {}
        if primitive.primitive_type == CanonicalCapabilityType.NUMBER:
            assert not {
                "value",
                "start_value",
                "prefix",
                "suffix",
                "precision",
            } & set(primitive.properties)

    connector = compiled.primitives["rate_to_emi"]
    assert set(connector.properties) == {"has_arrow"}
    assert connector.connector_path is not None


def test_multi_beat_roots_sharing_macro_zone_do_not_collide() -> None:
    world = _loan_world().model_copy(deep=True)
    # Add a root group in beat 'rate_change' with macro_zone 'center'
    second_beat_root = WorldObjectSpec(
        object_id="second_beat_card",
        primitive_type=CanonicalCapabilityType.GROUP,
        semantic_content={"macro_zone": "center"},
        lifecycle=LifecyclePolicy(mode="beat_local", introduced_in_beat="rate_change"),
        beat_ids=["rate_change"],
    )
    # Add a text child that wraps
    second_beat_text = WorldObjectSpec(
        object_id="second_beat_text",
        primitive_type=CanonicalCapabilityType.TEXT,
        semantic_content={"content": "A very long descriptive sentence that will wrap cleanly onto multiple lines inside the container."},
        parent_object_id="second_beat_card",
        lifecycle=LifecyclePolicy(mode="beat_local", introduced_in_beat="rate_change"),
        beat_ids=["rate_change"],
    )
    # loan_panel is active only in 'establish' for this test so they don't co-occur in rate_change
    world.objects[0].beat_ids = ["establish"]
    world.objects.extend([second_beat_root, second_beat_text])

    compiled = _compiler().compile(world, _voice_track())
    assert "second_beat_card" in compiled.primitives
    assert "second_beat_text" in compiled.primitives


def test_multi_move_layout_continuity_preserved() -> None:
    world = _loan_world().model_copy(deep=True)
    from domain.visual_world import LayoutIntentState

    # loan_panel moves from initial (center) to left in beat 2, then to right in beat 3
    world.beats[1].state_change_events.append(
        StateChangeEvent(
            event_id="panel_move_left",
            object_id="loan_panel",
            beat_id="rate_change",
            kind=StateChangeKind.LAYOUT,
            layout_intent=LayoutIntentState(macro_zone=MacroScreenZone.LEFT),
            speech_anchor=SpeechAnchor(
                anchor_id="anchor_panel_left",
                beat_id="rate_change",
                text="rises",
            ),
        )
    )

    world.beats[2].state_change_events.append(
        StateChangeEvent(
            event_id="panel_move_right",
            object_id="loan_panel",
            beat_id="emi_change",
            kind=StateChangeKind.LAYOUT,
            layout_intent=LayoutIntentState(
                macro_zone=MacroScreenZone.RIGHT
            ),
            speech_anchor=SpeechAnchor(
                anchor_id="anchor_panel_right",
                beat_id="emi_change",
                text="becomes",
            ),
        )
    )

    compiled = _compiler().compile(world, _voice_track())

    panel_track = next(
        track for track in compiled.state_tracks if track.object_id == "loan_panel"
    )
    layout_changes = [c for c in panel_track.changes if c.kind == "layout"]
    assert len(layout_changes) == 2

    first_move = layout_changes[0]
    second_move = layout_changes[1]

    # The second move MUST start from the destination of the first move!
    assert first_move.to_value == second_move.from_value
    assert first_move.from_value != first_move.to_value
    assert second_move.from_value != second_move.to_value

    # Verify animation tracks also reflect unbroken continuity
    panel_anim_tracks = [
        anim for anim in compiled.animation_tracks
        if anim.object_id == "loan_panel" and anim.target_property == "layout"
    ]
    assert len(panel_anim_tracks) == 2
    assert panel_anim_tracks[0].to_value == panel_anim_tracks[1].from_value


def test_multi_action_value_continuity_preserved() -> None:
    world = _loan_world().model_copy(deep=True)
    # Clear existing state_change_events on rate so we cleanly test consecutive actions
    world.beats[1].state_change_events = []

    # Add two consecutive update_value actions on 'rate' across beats
    world.beats[0].actions.append(
        VisualAction(
            action_id="act_rate_step1",
            target_node_id="rate",
            action_type=VisualActionType.UPDATE_VALUE,
            target_property="value",
            new_value=10.5,
            trigger_word="starts",
        )
    )
    world.beats[1].actions.append(
        VisualAction(
            action_id="act_rate_step2",
            target_node_id="rate",
            action_type=VisualActionType.UPDATE_VALUE,
            target_property="value",
            new_value=14.0,
            trigger_word="rises",
        )
    )

    compiled = _compiler().compile(world, _voice_track())

    anim1 = next(a for a in compiled.animation_tracks if a.animation_id == "act_rate_step1")
    anim2 = next(a for a in compiled.animation_tracks if a.animation_id == "act_rate_step2")

    # Initial rate is 8.5
    assert anim1.from_value == 8.5
    assert anim1.to_value == 10.5

    # Second animation MUST carry forward the accumulated current state (10.5), not the birth state (8.5)!
    assert anim2.from_value == 10.5
    assert anim2.to_value == 14.0


def test_tail_action_clamped_to_world_duration() -> None:
    world = _loan_world()
    # Trigger an action on the very last word of the narration (near audio boundary)
    world.beats[-1].actions.append(
        VisualAction(
            action_id="act_tail_last_word",
            target_node_id="rate",
            action_type=VisualActionType.HIGHLIGHT,
            trigger_word="rupees",
        )
    )
    compiled = _compiler().compile(world, _voice_track())
    for anim in compiled.animation_tracks:
        assert anim.trigger_frame + anim.duration_frames <= compiled.total_duration_frames
        assert anim.duration_frames > 0



