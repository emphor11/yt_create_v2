"""World-scoped visual architecture contracts.

These models describe semantic visual continuity before compilation.  They are
deliberately independent of pixels, frames, Remotion, and scene-composition
mounting.  A ``StoryboardBeat`` is an editorial unit; a ``VisualWorldSpec``
owns stable objects; and ``WorldTimeline`` describes semantic timing anchors.
"""
from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from domain.primitives.common import CanonicalCapabilityType
from domain.storyboard import (
    MacroScreenZone,
    MicroLayoutFlow,
    SemanticRelationship,
    SemanticStyleIntent,
    VisualAction,
    extract_narration_words,
)


_FORBIDDEN_DOWNSTREAM_KEYS = {
    "x",
    "y",
    "left",
    "right",
    "top",
    "bottom",
    "width",
    "height",
    "pixel",
    "px",
    "frame",
    "frames",
    "start_frame",
    "end_frame",
    "duration_frames",
    "timestamp",
    "timestamps",
    "remotion",
    "component",
    "component_id",
}


def _assert_semantic_payload(value: Any, path: str = "payload") -> None:
    """Reject renderer geometry/timing concepts from open semantic payloads."""
    if isinstance(value, dict):
        for key, nested in value.items():
            if str(key).lower() in _FORBIDDEN_DOWNSTREAM_KEYS:
                raise ValueError(
                    f"Semantic payload '{path}' contains forbidden downstream key '{key}'."
                )
            _assert_semantic_payload(nested, f"{path}.{key}")
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            _assert_semantic_payload(nested, f"{path}[{index}]")


class SourceReference(BaseModel):
    """Lineage reference to an upstream semantic or narration artifact."""

    model_config = ConfigDict(extra="forbid")

    kind: Literal[
        "visual_intent",
        "narration",
        "script",
        "research",
        "voice_track",
        "storyboard",
    ]
    reference_id: str = Field(..., min_length=1)
    excerpt: str | None = None


class SpeechAnchor(BaseModel):
    """A semantic speech location resolved later by the timing compiler."""

    model_config = ConfigDict(extra="forbid")

    anchor_id: str = Field(..., min_length=1)
    beat_id: str = Field(..., min_length=1)
    text: str = Field(..., min_length=1)
    occurrence: int = Field(default=1, ge=1)


class TransitionIntent(BaseModel):
    """Editorial continuity intent between adjacent beats."""

    model_config = ConfigDict(extra="forbid")

    kind: Literal[
        "continue",
        "transform",
        "hold",
        "focus",
        "cut",
        "introduce_world",
    ]
    description: str | None = None
    preserve_object_ids: list[str] = Field(default_factory=list)


class LayoutIntentState(BaseModel):
    """Semantic layout state; it contains no resolved geometry."""

    model_config = ConfigDict(extra="forbid")

    macro_zone: MacroScreenZone | None = None
    flow: MicroLayoutFlow | None = None
    anchor: str | None = None
    relative_to_object_id: str | None = None


class StateChangeKind(str, Enum):
    VALUE = "value"
    VISIBILITY = "visibility"
    STYLE = "style"
    LAYOUT = "layout"
    RELATIONSHIP = "relationship"


class StateChangeEvent(BaseModel):
    """A semantic state change applied to one stable world object."""

    model_config = ConfigDict(extra="forbid")

    event_id: str = Field(..., min_length=1)
    object_id: str = Field(..., min_length=1)
    beat_id: str = Field(..., min_length=1)
    kind: StateChangeKind
    target_property: str | None = None
    from_value: Any | None = None
    to_value: Any | None = None
    visible: bool | None = None
    style_intent: SemanticStyleIntent | None = None
    layout_intent: LayoutIntentState | None = None
    relationship: SemanticRelationship | None = None
    relationship_operation: Literal["add", "remove", "update"] | None = None
    speech_anchor: SpeechAnchor | None = None
    description: str | None = None

    @model_validator(mode="after")
    def validate_change_shape(self) -> "StateChangeEvent":
        if self.kind == StateChangeKind.VISIBILITY and self.visible is None:
            raise ValueError(f"Visibility event '{self.event_id}' requires visible.")
        if self.kind == StateChangeKind.LAYOUT and self.layout_intent is None:
            raise ValueError(f"Layout event '{self.event_id}' requires layout_intent.")
        if self.kind == StateChangeKind.RELATIONSHIP:
            if self.relationship is None or self.relationship_operation is None:
                raise ValueError(
                    f"Relationship event '{self.event_id}' requires relationship and operation."
                )
        if self.kind == StateChangeKind.STYLE and self.style_intent is None and self.to_value is None:
            raise ValueError(
                f"Style event '{self.event_id}' requires style_intent or to_value."
            )

        _assert_semantic_payload(self.from_value, f"event[{self.event_id}].from_value")
        _assert_semantic_payload(self.to_value, f"event[{self.event_id}].to_value")
        return self


class LifecyclePolicy(BaseModel):
    """Semantic lifetime of an object in the continuous world."""

    model_config = ConfigDict(extra="forbid")

    mode: Literal["persistent", "beat_local", "until_exit"] = "persistent"
    introduced_in_beat: str | None = None
    exit_event_id: str | None = None

    @model_validator(mode="after")
    def validate_lifecycle(self) -> "LifecyclePolicy":
        if self.mode == "until_exit" and not self.exit_event_id:
            raise ValueError("until_exit lifecycle requires exit_event_id.")
        if self.mode != "until_exit" and self.exit_event_id is not None:
            raise ValueError("exit_event_id is only valid for until_exit lifecycle.")
        return self


class StoryboardBeat(BaseModel):
    model_config = ConfigDict(extra="forbid")

    beat_id: str = Field(..., min_length=1)
    source_intent_ids: list[str] = Field(default_factory=list)
    narration: str = Field(..., min_length=1)
    source_references: list[SourceReference] = Field(default_factory=list)
    semantic_goal: str = Field(..., min_length=1)
    relationships: list[SemanticRelationship] = Field(default_factory=list)

    # Legacy beat-level compatibility; element_layouts is the new source.
    macro_zone: MacroScreenZone | None = None
    layout_flow: MicroLayoutFlow | None = None

    # Per-object semantic placement/layout chosen by the storyboard.
    element_layouts: dict[str, LayoutIntentState] = Field(default_factory=dict)

    actions: list[VisualAction] = Field(default_factory=list)
    state_change_events: list[StateChangeEvent] = Field(default_factory=list)
    transition_intent: TransitionIntent | None = None

    @model_validator(mode="after")
    def validate_beat(self) -> "StoryboardBeat":
        event_ids: set[str] = set()
        for event in self.state_change_events:
            if event.event_id in event_ids:
                raise ValueError(
                    f"Duplicate state-change event '{event.event_id}' in beat '{self.beat_id}'."
                )
            event_ids.add(event.event_id)
            if event.beat_id != self.beat_id:
                raise ValueError(
                    f"State-change event '{event.event_id}' belongs to beat '{event.beat_id}', "
                    f"not '{self.beat_id}'."
                )

        words = {word.lower() for word in extract_narration_words(self.narration)}
        for action in self.actions:
            trigger = action.trigger_word.strip().strip(".,!?;:\"'()[]{}").lower()
            if trigger not in words:
                raise ValueError(
                    f"Action '{action.action_id}' trigger word '{action.trigger_word}' "
                    f"is not present in beat '{self.beat_id}' narration."
                )
        return self


class WorldObjectSpec(BaseModel):
    """One stable semantic object in a visual world."""

    model_config = ConfigDict(extra="forbid")

    object_id: str = Field(..., min_length=1)
    primitive_type: CanonicalCapabilityType | None = None
    component_type: str | None = None
    semantic_content: dict[str, Any] = Field(default_factory=dict)
    parent_object_id: str | None = None
    initial_state: dict[str, Any] = Field(default_factory=dict)
    lifecycle: LifecyclePolicy = Field(default_factory=LifecyclePolicy)
    beat_ids: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_spec(self) -> "WorldObjectSpec":
        if self.primitive_type is None and self.component_type is None:
            raise ValueError(
                f"WorldObjectSpec '{self.object_id}' must specify either primitive_type or component_type."
            )
        if self.primitive_type is not None and self.component_type is not None:
            raise ValueError(
                f"WorldObjectSpec '{self.object_id}' cannot specify both primitive_type and component_type."
            )
        if self.component_type is not None:
            try:
                from registries.visual_component_registry import VisualComponentRegistry
            except ImportError:
                from backend.registries.visual_component_registry import VisualComponentRegistry
            if not VisualComponentRegistry.is_registered(self.component_type):
                raise ValueError(
                    f"Unknown visual component_type '{self.component_type}' on '{self.object_id}'."
                )
            try:
                VisualComponentRegistry.validate_props(self.component_type, self.semantic_content)
            except Exception as e:
                raise ValueError(
                    f"WorldObjectSpec '{self.object_id}' of component_type '{self.component_type}' has invalid semantic_content: {e}"
                ) from e
        _assert_semantic_payload(self.semantic_content, f"object[{self.object_id}].semantic_content")
        _assert_semantic_payload(self.initial_state, f"object[{self.object_id}].initial_state")
        return self


class ObjectStateTrack(BaseModel):
    """Ordered semantic state evolution for one stable world object."""

    model_config = ConfigDict(extra="forbid")

    object_id: str = Field(..., min_length=1)
    initial_state: dict[str, Any] = Field(default_factory=dict)
    state_changes: list[StateChangeEvent] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_track(self) -> "ObjectStateTrack":
        _assert_semantic_payload(self.initial_state, f"track[{self.object_id}].initial_state")
        event_ids: set[str] = set()
        for event in self.state_changes:
            if event.object_id != self.object_id:
                raise ValueError(
                    f"State event '{event.event_id}' targets '{event.object_id}', "
                    f"not track object '{self.object_id}'."
                )
            if event.event_id in event_ids:
                raise ValueError(
                    f"Duplicate state event '{event.event_id}' in track '{self.object_id}'."
                )
            event_ids.add(event.event_id)
        return self


class VisualWorldSpec(BaseModel):
    """Complete semantic visual world before compilation."""

    model_config = ConfigDict(extra="forbid")

    schema_version: str = "1"
    world_id: str = Field(..., min_length=1)
    beats: list[StoryboardBeat] = Field(default_factory=list)
    objects: list[WorldObjectSpec] = Field(default_factory=list)
    relationships: list[SemanticRelationship] = Field(default_factory=list)
    object_state_tracks: list[ObjectStateTrack] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_world(self) -> "VisualWorldSpec":
        beat_ids = self._unique_ids([beat.beat_id for beat in self.beats], "beat")
        object_ids = self._unique_ids([obj.object_id for obj in self.objects], "object")
        self._unique_ids(
            [track.object_id for track in self.object_state_tracks], "state-track object"
        )

        object_map = {obj.object_id: obj for obj in self.objects}
        for obj in self.objects:
            for beat_id in obj.beat_ids:
                if beat_id not in beat_ids:
                    raise ValueError(
                        f"Object '{obj.object_id}' references unknown beat '{beat_id}'."
                    )
            if obj.lifecycle.introduced_in_beat and obj.lifecycle.introduced_in_beat not in beat_ids:
                raise ValueError(
                    f"Object '{obj.object_id}' has unknown introduction beat "
                    f"'{obj.lifecycle.introduced_in_beat}'."
                )
            if obj.parent_object_id:
                if obj.parent_object_id not in object_ids:
                    raise ValueError(
                        f"Object '{obj.object_id}' references unknown parent "
                        f"'{obj.parent_object_id}'."
                    )
                parent_obj = object_map[obj.parent_object_id]
                is_group = parent_obj.primitive_type == CanonicalCapabilityType.GROUP
                is_container_comp = False
                if parent_obj.component_type:
                    try:
                        from registries.visual_component_registry import VisualComponentRegistry, ComponentCategory
                    except ImportError:
                        from backend.registries.visual_component_registry import VisualComponentRegistry, ComponentCategory
                    desc = VisualComponentRegistry.get_descriptor(parent_obj.component_type)
                    is_container_comp = (desc.category == ComponentCategory.STRUCTURAL_CONTAINER)
                if not (is_group or is_container_comp):
                    raise ValueError(
                        f"Object '{obj.object_id}' parent '{obj.parent_object_id}' "
                        "must be a group primitive or structural container component."
                    )
                if is_container_comp and obj.component_type:
                    desc = VisualComponentRegistry.get_descriptor(parent_obj.component_type)
                    if desc.supported_children and obj.component_type not in desc.supported_children:
                        raise ValueError(
                            f"Parent '{parent_obj.object_id}' of type '{parent_obj.component_type}' "
                            f"does not support child component '{obj.component_type}'."
                        )
                if obj.parent_object_id == obj.object_id:
                    raise ValueError(f"Object '{obj.object_id}' cannot parent itself.")

        self._validate_parent_cycles(object_map)

        for relationship in self.relationships:
            if relationship.source_id not in object_ids or relationship.target_id not in object_ids:
                raise ValueError(
                    "World relationships must reference stable object IDs: "
                    f"'{relationship.source_id}' -> '{relationship.target_id}'."
                )

        event_ids: set[str] = set()
        for beat in self.beats:
            for relationship in beat.relationships:
                if relationship.source_id not in object_ids or relationship.target_id not in object_ids:
                    raise ValueError(
                        "Beat relationships must reference stable object IDs: "
                        f"'{relationship.source_id}' -> '{relationship.target_id}'."
                    )
            for action in beat.actions:
                if action.target_node_id not in object_ids:
                    raise ValueError(
                        f"Action '{action.action_id}' targets unknown world object "
                        f"'{action.target_node_id}'."
                    )
            for event in beat.state_change_events:
                if event.object_id not in object_ids:
                    raise ValueError(
                        f"State event '{event.event_id}' targets unknown world object "
                        f"'{event.object_id}'."
                    )
                if event.relationship and (
                    event.relationship.source_id not in object_ids
                    or event.relationship.target_id not in object_ids
                ):
                    raise ValueError(
                        f"State event '{event.event_id}' contains a relationship with "
                        "an unknown world object."
                    )
                if event.event_id in event_ids:
                    raise ValueError(f"Duplicate world state event '{event.event_id}'.")
                event_ids.add(event.event_id)

        for track in self.object_state_tracks:
            if track.object_id not in object_ids:
                raise ValueError(
                    f"State track references unknown world object '{track.object_id}'."
                )
            for event in track.state_changes:
                if event.event_id in event_ids:
                    raise ValueError(
                        f"State event '{event.event_id}' is declared both in a beat and a track."
                    )
                if event.beat_id not in beat_ids:
                    raise ValueError(
                        f"State event '{event.event_id}' references unknown beat '{event.beat_id}'."
                    )
                if event.relationship and (
                    event.relationship.source_id not in object_ids
                    or event.relationship.target_id not in object_ids
                ):
                    raise ValueError(
                        f"State event '{event.event_id}' contains a relationship with "
                        "an unknown world object."
                    )
                event_ids.add(event.event_id)

        for obj in self.objects:
            if obj.lifecycle.exit_event_id and obj.lifecycle.exit_event_id not in event_ids:
                raise ValueError(
                    f"Object '{obj.object_id}' references unknown exit event "
                    f"'{obj.lifecycle.exit_event_id}'."
                )

        for beat in self.beats:
            if beat.transition_intent:
                unknown_ids = set(beat.transition_intent.preserve_object_ids) - object_ids
                if unknown_ids:
                    raise ValueError(
                        f"Beat '{beat.beat_id}' transition preserves unknown objects: "
                        f"{sorted(unknown_ids)}."
                    )

        return self

    @staticmethod
    def _unique_ids(values: list[str], label: str) -> set[str]:
        if len(values) != len(set(values)):
            duplicates = sorted({value for value in values if values.count(value) > 1})
            raise ValueError(f"Duplicate {label} IDs: {duplicates}.")
        return set(values)

    @staticmethod
    def _validate_parent_cycles(objects: dict[str, WorldObjectSpec]) -> None:
        for object_id in objects:
            visited: set[str] = set()
            current: str | None = object_id
            while current is not None:
                if current in visited:
                    raise ValueError(f"Cyclic world object parentage involves '{current}'.")
                visited.add(current)
                current = objects[current].parent_object_id


class TimelineDuration(BaseModel):
    """Semantic total-duration reference resolved later from an authoritative source."""

    model_config = ConfigDict(extra="forbid")

    kind: Literal["voice_track", "narration", "anchor"]
    end_anchor_id: str | None = None

    @model_validator(mode="after")
    def validate_duration(self) -> "TimelineDuration":
        if self.kind == "anchor" and not self.end_anchor_id:
            raise ValueError("Anchor-based total duration requires end_anchor_id.")
        if self.kind != "anchor" and self.end_anchor_id is not None:
            raise ValueError("end_anchor_id is only valid for anchor-based duration.")
        return self


class BeatInterval(BaseModel):
    """Semantic interval for one beat, bounded by speech anchors."""

    model_config = ConfigDict(extra="forbid")

    beat_id: str = Field(..., min_length=1)
    start_anchor_id: str = Field(..., min_length=1)
    end_anchor_id: str = Field(..., min_length=1)


class TransitionEvent(BaseModel):
    """Semantic transition between adjacent beats."""

    model_config = ConfigDict(extra="forbid")

    event_id: str = Field(..., min_length=1)
    from_beat_id: str = Field(..., min_length=1)
    to_beat_id: str = Field(..., min_length=1)
    at_anchor_id: str = Field(..., min_length=1)
    intent: TransitionIntent


class ObjectAnimationTrack(BaseModel):
    """Semantic animation/state-track reference for one world object."""

    model_config = ConfigDict(extra="forbid")

    object_id: str = Field(..., min_length=1)
    state_change_event_ids: list[str] = Field(default_factory=list)


class VisibilityInterval(BaseModel):
    """Visibility interval bounded by semantic anchors, not numeric frames."""

    model_config = ConfigDict(extra="forbid")

    object_id: str = Field(..., min_length=1)
    start_anchor_id: str = Field(..., min_length=1)
    end_anchor_id: str | None = None
    visible: bool = True


class WorldTimeline(BaseModel):
    """Semantic timeline for one continuous visual world."""

    model_config = ConfigDict(extra="forbid")

    schema_version: str = "1"
    world_id: str = Field(..., min_length=1)
    total_duration: TimelineDuration
    beat_intervals: list[BeatInterval] = Field(default_factory=list)
    speech_anchors: list[SpeechAnchor] = Field(default_factory=list)
    transition_events: list[TransitionEvent] = Field(default_factory=list)
    object_animation_tracks: list[ObjectAnimationTrack] = Field(default_factory=list)
    visibility_intervals: list[VisibilityInterval] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_timeline(self) -> "WorldTimeline":
        beat_ids = {interval.beat_id for interval in self.beat_intervals}
        if len(beat_ids) != len(self.beat_intervals):
            raise ValueError("World timeline cannot contain duplicate beat intervals.")

        anchor_ids = {anchor.anchor_id for anchor in self.speech_anchors}
        if len(anchor_ids) != len(self.speech_anchors):
            raise ValueError("World timeline cannot contain duplicate speech anchors.")

        if self.total_duration.end_anchor_id and self.total_duration.end_anchor_id not in anchor_ids:
            raise ValueError(
                f"Total duration references unknown anchor '{self.total_duration.end_anchor_id}'."
            )

        for interval in self.beat_intervals:
            if interval.start_anchor_id not in anchor_ids or interval.end_anchor_id not in anchor_ids:
                raise ValueError(
                    f"Beat interval '{interval.beat_id}' references an unknown speech anchor."
                )

        transition_ids: set[str] = set()
        for event in self.transition_events:
            if event.event_id in transition_ids:
                raise ValueError(f"Duplicate transition event '{event.event_id}'.")
            transition_ids.add(event.event_id)
            if event.from_beat_id not in beat_ids or event.to_beat_id not in beat_ids:
                raise ValueError(
                    f"Transition '{event.event_id}' references unknown beat(s)."
                )
            if event.at_anchor_id not in anchor_ids:
                raise ValueError(
                    f"Transition '{event.event_id}' references unknown anchor "
                    f"'{event.at_anchor_id}'."
                )

        object_track_ids = [track.object_id for track in self.object_animation_tracks]
        if len(object_track_ids) != len(set(object_track_ids)):
            raise ValueError("World timeline cannot contain duplicate object animation tracks.")

        for interval in self.visibility_intervals:
            if interval.start_anchor_id not in anchor_ids:
                raise ValueError(
                    f"Visibility interval for '{interval.object_id}' references unknown start anchor."
                )
            if interval.end_anchor_id and interval.end_anchor_id not in anchor_ids:
                raise ValueError(
                    f"Visibility interval for '{interval.object_id}' references unknown end anchor."
                )
        return self
