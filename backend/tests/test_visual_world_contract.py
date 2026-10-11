"""Focused tests for the isolated world-scoped visual contracts."""
from __future__ import annotations

import pytest
from pydantic import ValidationError

from domain.primitives.common import CanonicalCapabilityType
from domain.storyboard import (
    MacroScreenZone,
    MicroLayoutFlow,
    SemanticRelationship,
    SemanticStyleIntent,
    VisualAction,
    VisualActionType,
)
from domain.visual_world import (
    BeatInterval,
    LifecyclePolicy,
    ObjectAnimationTrack,
    ObjectStateTrack,
    SourceReference,
    SpeechAnchor,
    StateChangeEvent,
    StateChangeKind,
    StoryboardBeat,
    TimelineDuration,
    TransitionEvent,
    TransitionIntent,
    VisibilityInterval,
    VisualWorldSpec,
    WorldObjectSpec,
    WorldTimeline,
)


def _loan_world() -> VisualWorldSpec:
    beat_1 = StoryboardBeat(
        beat_id="establish_loan",
        source_intent_ids=["intent_loan_rate"],
        narration="The home loan starts at eight point five percent and the EMI is forty three thousand three hundred ninety one rupees.",
        source_references=[
            SourceReference(
                kind="visual_intent",
                reference_id="intent_loan_rate",
                excerpt="Higher interest increases the monthly payment.",
            )
        ],
        semantic_goal="Establish the loan, baseline rate, and baseline EMI.",
        macro_zone=MacroScreenZone.CENTER,
        actions=[
            VisualAction(
                action_id="reveal_loan",
                target_node_id="loan",
                action_type=VisualActionType.ENTER,
                trigger_word="loan",
            )
        ],
    )
    beat_2 = StoryboardBeat(
        beat_id="raise_rate",
        source_intent_ids=["intent_loan_rate"],
        narration="When the rate rises to ten point five percent, the monthly burden increases.",
        source_references=[
            SourceReference(kind="narration", reference_id="script.loan.beat_2")
        ],
        semantic_goal="Transform the existing rate while keeping the loan visible.",
        relationships=[
            SemanticRelationship(
                source_id="rate",
                relation="causes",
                target_id="emi",
                visual_representation="state_transformation",
            )
        ],
        macro_zone=MacroScreenZone.CENTER,
        actions=[
            VisualAction(
                action_id="change_rate",
                target_node_id="rate",
                action_type=VisualActionType.TRANSFORM,
                trigger_word="rises",
                new_value="10.5%",
                target_property="value",
            )
        ],
        state_change_events=[
            StateChangeEvent(
                event_id="rate_to_high",
                object_id="rate",
                beat_id="raise_rate",
                kind=StateChangeKind.VALUE,
                target_property="value",
                from_value="8.5%",
                to_value="10.5%",
            )
        ],
        transition_intent=TransitionIntent(
            kind="transform",
            preserve_object_ids=["loan", "rate", "emi"],
            description="Keep the established loan world and transform the rate in place.",
        ),
    )
    beat_3 = StoryboardBeat(
        beat_id="update_emi",
        source_intent_ids=["intent_loan_rate"],
        narration="The EMI becomes forty nine thousand nine hundred nineteen rupees.",
        source_references=[
            SourceReference(kind="research", reference_id="research.fact.emi_high")
        ],
        semantic_goal="Transform the existing EMI and emphasize the added burden.",
        relationships=[
            SemanticRelationship(
                source_id="rate",
                relation="causes",
                target_id="emi",
                visual_representation="state_transformation",
            )
        ],
        macro_zone=MacroScreenZone.CENTER,
        state_change_events=[
            StateChangeEvent(
                event_id="emi_to_high",
                object_id="emi",
                beat_id="update_emi",
                kind=StateChangeKind.VALUE,
                target_property="value",
                from_value="₹43,391",
                to_value="₹49,919",
            )
        ],
    )

    return VisualWorldSpec(
        world_id="loan_rate_world",
        beats=[beat_1, beat_2, beat_3],
        objects=[
            WorldObjectSpec(
                object_id="loan",
                primitive_type=CanonicalCapabilityType.GROUP,
                semantic_content={"role": "home loan document"},
                initial_state={"label": "₹50 lakh home loan"},
                lifecycle=LifecyclePolicy(
                    mode="persistent", introduced_in_beat="establish_loan"
                ),
                beat_ids=["establish_loan", "raise_rate", "update_emi"],
            ),
            WorldObjectSpec(
                object_id="rate",
                primitive_type=CanonicalCapabilityType.NUMBER,
                semantic_content={"role": "interest rate"},
                initial_state={"value": "8.5%"},
                lifecycle=LifecyclePolicy(
                    mode="persistent", introduced_in_beat="establish_loan"
                ),
                beat_ids=["establish_loan", "raise_rate", "update_emi"],
            ),
            WorldObjectSpec(
                object_id="emi",
                primitive_type=CanonicalCapabilityType.NUMBER,
                semantic_content={"role": "monthly payment"},
                initial_state={"value": "₹43,391"},
                lifecycle=LifecyclePolicy(
                    mode="persistent", introduced_in_beat="establish_loan"
                ),
                beat_ids=["establish_loan", "raise_rate", "update_emi"],
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
        object_state_tracks=[
            ObjectStateTrack(
                object_id="rate",
                initial_state={"value": "8.5%"},
                state_changes=[
                    StateChangeEvent(
                        event_id="rate_to_high_track",
                        object_id="rate",
                        beat_id="raise_rate",
                        kind=StateChangeKind.VALUE,
                        target_property="value",
                        from_value="8.5%",
                        to_value="10.5%",
                    )
                ],
            ),
            ObjectStateTrack(
                object_id="emi",
                initial_state={"value": "₹43,391"},
                state_changes=[
                    StateChangeEvent(
                        event_id="emi_to_high_track",
                        object_id="emi",
                        beat_id="update_emi",
                        kind=StateChangeKind.VALUE,
                        target_property="value",
                        from_value="₹43,391",
                        to_value="₹49,919",
                    )
                ],
            ),
        ],
    )


def test_loan_rate_emi_are_one_stable_visual_world() -> None:
    world = _loan_world()

    assert world.world_id == "loan_rate_world"
    assert len(world.beats) == 3
    assert {obj.object_id for obj in world.objects} == {"loan", "rate", "emi"}
    assert all(obj.lifecycle.mode == "persistent" for obj in world.objects)
    assert all(
        obj.beat_ids == ["establish_loan", "raise_rate", "update_emi"]
        for obj in world.objects
    )
    assert world.object_state_tracks[0].object_id == "rate"
    assert world.object_state_tracks[1].object_id == "emi"


def test_world_timeline_uses_semantic_anchors_not_frames() -> None:
    timeline = WorldTimeline(
        world_id="loan_rate_world",
        total_duration=TimelineDuration(kind="anchor", end_anchor_id="anchor_emi"),
        speech_anchors=[
            SpeechAnchor(anchor_id="anchor_loan", beat_id="establish_loan", text="loan"),
            SpeechAnchor(anchor_id="anchor_rate", beat_id="raise_rate", text="rises"),
            SpeechAnchor(anchor_id="anchor_emi", beat_id="update_emi", text="EMI"),
        ],
        beat_intervals=[
            BeatInterval(
                beat_id="establish_loan",
                start_anchor_id="anchor_loan",
                end_anchor_id="anchor_rate",
            ),
            BeatInterval(
                beat_id="raise_rate",
                start_anchor_id="anchor_rate",
                end_anchor_id="anchor_emi",
            ),
        ],
        transition_events=[
            TransitionEvent(
                event_id="rate_transition",
                from_beat_id="establish_loan",
                to_beat_id="raise_rate",
                at_anchor_id="anchor_rate",
                intent=TransitionIntent(
                    kind="transform", preserve_object_ids=["loan", "rate", "emi"]
                ),
            )
        ],
        object_animation_tracks=[
            ObjectAnimationTrack(
                object_id="rate", state_change_event_ids=["rate_to_high_track"]
            ),
            ObjectAnimationTrack(
                object_id="emi", state_change_event_ids=["emi_to_high_track"]
            ),
        ],
        visibility_intervals=[
            VisibilityInterval(object_id="loan", start_anchor_id="anchor_loan")
        ],
    )

    serialized = timeline.model_dump()
    assert serialized["total_duration"]["kind"] == "anchor"
    assert "duration_frames" not in str(serialized)
    assert "frame" not in str(serialized).lower()


def test_world_rejects_duplicate_identity_and_dangling_relationship() -> None:
    world = _loan_world()
    raw = world.model_dump()
    raw["objects"].append(raw["objects"][0])

    with pytest.raises(ValidationError, match="Duplicate object IDs"):
        VisualWorldSpec.model_validate(raw)

    raw = _loan_world().model_dump()
    raw["relationships"][0]["target_id"] = "missing_object"
    with pytest.raises(ValidationError, match="stable object IDs"):
        VisualWorldSpec.model_validate(raw)


def test_world_rejects_pixel_geometry_and_frame_payloads() -> None:
    with pytest.raises(ValidationError, match="forbidden downstream key"):
        WorldObjectSpec(
            object_id="bad_object",
            primitive_type=CanonicalCapabilityType.NUMBER,
            semantic_content={"x": 120},
        )

    with pytest.raises(ValidationError, match="forbidden downstream key"):
        StateChangeEvent(
            event_id="bad_event",
            object_id="number",
            beat_id="beat",
            kind=StateChangeKind.VALUE,
            to_value={"start_frame": 10},
        )


def test_object_state_track_supports_value_visibility_style_layout_and_relationship() -> None:
    track = ObjectStateTrack(
        object_id="emi",
        initial_state={"value": "₹43,391", "visible": True},
        state_changes=[
            StateChangeEvent(
                event_id="emi_value",
                object_id="emi",
                beat_id="raise_rate",
                kind=StateChangeKind.VALUE,
                target_property="value",
                to_value="₹49,919",
            ),
            StateChangeEvent(
                event_id="emi_visibility",
                object_id="emi",
                beat_id="raise_rate",
                kind=StateChangeKind.VISIBILITY,
                visible=True,
            ),
            StateChangeEvent(
                event_id="emi_style",
                object_id="emi",
                beat_id="raise_rate",
                kind=StateChangeKind.STYLE,
                style_intent=SemanticStyleIntent(opacity=1.0),
            ),
            StateChangeEvent(
                event_id="emi_layout",
                object_id="emi",
                beat_id="raise_rate",
                kind=StateChangeKind.LAYOUT,
                layout_intent={
                    "macro_zone": MacroScreenZone.BOTTOM,
                    "flow": MicroLayoutFlow(),
                    "anchor": "below_rate",
                },
            ),
            StateChangeEvent(
                event_id="emi_relationship",
                object_id="emi",
                beat_id="raise_rate",
                kind=StateChangeKind.RELATIONSHIP,
                relationship=SemanticRelationship(
                    source_id="rate",
                    relation="causes",
                    target_id="emi",
                ),
                relationship_operation="update",
            ),
        ],
    )

    assert [event.kind for event in track.state_changes] == [
        StateChangeKind.VALUE,
        StateChangeKind.VISIBILITY,
        StateChangeKind.STYLE,
        StateChangeKind.LAYOUT,
        StateChangeKind.RELATIONSHIP,
    ]
