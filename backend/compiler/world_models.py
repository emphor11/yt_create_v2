"""Compiled world-scoped render contract.

This module is intentionally separate from the existing scene compiler models.
Its geometry is parent-local, its timing is global, and connector paths are
fully resolved before a renderer could consume the result.
"""
from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from compiler.models import CanvasConfig
from domain.primitives.common import CanonicalCapabilityType, PrimitiveStyle, SpringConfig
from domain.storyboard import MacroScreenZone
from domain.visual_world import SourceReference


class LocalRect(BaseModel):
    model_config = ConfigDict(extra="forbid")

    x: float
    y: float
    width: float = Field(..., gt=0)
    height: float = Field(..., gt=0)


class Point2D(BaseModel):
    model_config = ConfigDict(extra="forbid")

    x: float
    y: float


class CompiledSpeechAnchor(BaseModel):
    model_config = ConfigDict(extra="forbid")

    anchor_id: str
    beat_id: str
    text: str
    occurrence: int = Field(..., ge=1)
    start_ms: int = Field(..., ge=0)
    end_ms: int = Field(..., ge=0)
    global_frame: int = Field(..., ge=0)

    @model_validator(mode="after")
    def validate_span(self) -> "CompiledSpeechAnchor":
        if self.end_ms < self.start_ms:
            raise ValueError(f"Speech anchor '{self.anchor_id}' has an inverted timestamp span.")
        return self


class CompiledBeatInterval(BaseModel):
    model_config = ConfigDict(extra="forbid")

    beat_id: str
    start_ms: int = Field(..., ge=0)
    end_ms: int = Field(..., ge=0)
    start_frame: int = Field(..., ge=0)
    end_frame: int = Field(..., ge=0)

    @property
    def duration_frames(self) -> int:
        return self.end_frame - self.start_frame

    @model_validator(mode="after")
    def validate_interval(self) -> "CompiledBeatInterval":
        if self.end_ms < self.start_ms or self.end_frame < self.start_frame:
            raise ValueError(f"Beat interval '{self.beat_id}' is inverted.")
        return self


class CompiledTransitionEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_id: str
    from_beat_id: str
    to_beat_id: str
    global_frame: int = Field(..., ge=0)
    kind: str
    preserve_object_ids: list[str] = Field(default_factory=list)


class ResolvedConnectorPath(BaseModel):
    """Complete connector path in the connector parent's local space.

    ``parent_object_id`` is the coordinate-space owner of every point.  The
    connector primitive's ``local_geometry`` is only its resolved bounds for
    bookkeeping; it is not an additional transform for this path.
    """

    model_config = ConfigDict(extra="forbid")

    parent_object_id: str | None
    from_point: Point2D
    to_point: Point2D
    points: list[Point2D] = Field(min_length=2)
    routing: Literal["straight", "curved", "orthogonal_elbow"]


class CompiledAnimationTrack(BaseModel):
    model_config = ConfigDict(extra="forbid")

    animation_id: str
    object_id: str
    trigger_frame: int = Field(..., ge=0)
    duration_frames: int = Field(..., gt=0)
    easing: Literal["linear", "ease-out", "spring", "bezier"]
    spring_config: SpringConfig | None = None
    motion_preset: str | None = None
    behavior: str
    target_property: str = Field(..., min_length=1)
    from_value: Any
    to_value: Any = None

    @model_validator(mode="after")
    def validate_values(self) -> "CompiledAnimationTrack":
        if self.from_value is None:
            raise ValueError(
                f"Animation '{self.animation_id}' must contain a compiler-resolved from_value."
            )
        return self


class CompiledStateChange(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_id: str
    object_id: str
    beat_id: str
    global_frame: int = Field(..., ge=0)
    kind: str
    target_property: str = Field(..., min_length=1)
    from_value: Any
    to_value: Any | None = None
    visible: bool | None = None


class CompiledStateTrack(BaseModel):
    model_config = ConfigDict(extra="forbid")

    object_id: str
    initial_state: dict[str, Any] = Field(default_factory=dict)
    changes: list[CompiledStateChange] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_changes(self) -> "CompiledStateTrack":
        if any(change.object_id != self.object_id for change in self.changes):
            raise ValueError(f"State track '{self.object_id}' contains another object's change.")
        if any(
            self.changes[index].global_frame > self.changes[index + 1].global_frame
            for index in range(len(self.changes) - 1)
        ):
            raise ValueError(f"State track '{self.object_id}' is not ordered by global frame.")
        return self


class CompiledLifecycleTrack(BaseModel):
    model_config = ConfigDict(extra="forbid")

    object_id: str
    introduced_frame: int = Field(..., ge=0)
    exit_frame: int | None = Field(default=None, ge=0)
    mode: Literal["persistent", "beat_local", "until_exit"]

    @model_validator(mode="after")
    def validate_lifecycle(self) -> "CompiledLifecycleTrack":
        if self.exit_frame is not None and self.exit_frame < self.introduced_frame:
            raise ValueError(f"Lifecycle for '{self.object_id}' exits before introduction.")
        return self


class CompiledVisibilityInterval(BaseModel):
    """A visible half-open interval ``[start_frame, end_frame)``."""

    model_config = ConfigDict(extra="forbid")

    object_id: str
    start_frame: int = Field(..., ge=0)
    end_frame: int = Field(..., gt=0)

    @model_validator(mode="after")
    def validate_interval(self) -> "CompiledVisibilityInterval":
        if self.end_frame <= self.start_frame:
            raise ValueError(f"Visibility interval for '{self.object_id}' is empty or inverted.")
        return self


class CompiledTerminalHold(BaseModel):
    """Explicit final hold after the last editorial beat, if one exists."""

    model_config = ConfigDict(extra="forbid")

    start_frame: int = Field(..., ge=0)
    end_frame: int = Field(..., gt=0)

    @model_validator(mode="after")
    def validate_hold(self) -> "CompiledTerminalHold":
        if self.end_frame <= self.start_frame:
            raise ValueError("Terminal hold must contain at least one frame.")
        return self


class CompiledMacroZoneAllocation(BaseModel):
    """Optional compiler/debug metadata; not renderer input."""

    model_config = ConfigDict(extra="forbid")

    object_id: str
    zone: MacroScreenZone
    rect: LocalRect


class CompiledPrimitive(BaseModel):
    """One stable world object with parent-local compiled geometry."""

    model_config = ConfigDict(extra="forbid")

    object_id: str
    primitive_type: CanonicalCapabilityType
    parent_object_id: str | None = None
    child_object_ids: list[str] = Field(default_factory=list)
    local_geometry: LocalRect
    style: PrimitiveStyle = Field(default_factory=PrimitiveStyle)
    properties: dict[str, Any] = Field(default_factory=dict)
    connector_path: ResolvedConnectorPath | None = None

    @model_validator(mode="after")
    def validate_compiled_primitive(self) -> "CompiledPrimitive":
        if self.primitive_type == CanonicalCapabilityType.GROUP:
            painted = (
                self.style.fill is not None
                or self.style.stroke is not None
                or self.style.corner_radius is not None
                or self.style.shadow is not None
            )
            if painted:
                raise ValueError(
                    f"Group '{self.object_id}' cannot carry painted styles; use a shape child."
                )
        if self.primitive_type == CanonicalCapabilityType.CONNECTOR and self.connector_path is None:
            raise ValueError(f"Connector '{self.object_id}' requires a resolved connector path.")
        if self.primitive_type != CanonicalCapabilityType.CONNECTOR and self.connector_path is not None:
            raise ValueError(
                f"Non-connector '{self.object_id}' cannot carry connector geometry."
            )
        if self.primitive_type == CanonicalCapabilityType.GROUP and "child_ids" in self.properties:
            raise ValueError(
                f"Group '{self.object_id}' duplicates child_object_ids in properties; "
                "child_object_ids is authoritative."
            )
        if self.primitive_type == CanonicalCapabilityType.CONNECTOR:
            forbidden = {"from_anchor", "to_anchor", "routing"} & set(self.properties)
            if forbidden:
                raise ValueError(
                    f"Connector '{self.object_id}' duplicates resolved path facts: "
                    f"{sorted(forbidden)}."
                )
        if self.primitive_type == CanonicalCapabilityType.NUMBER:
            duplicated_state = {"value", "start_value", "prefix", "suffix", "precision"} & set(
                self.properties
            )
            if duplicated_state:
                raise ValueError(
                    f"Number '{self.object_id}' duplicates state-owned properties: "
                    f"{sorted(duplicated_state)}."
                )
        if _contains_forbidden_connector_reference(self.properties):
            raise ValueError(
                f"Compiled primitive '{self.object_id}' contains unresolved connector target IDs."
            )
        return self


class CompiledObjectKind(str, Enum):
    PRIMITIVE = "primitive"
    COMPONENT = "component"


class CompiledVisualInstance(BaseModel):
    """Authoritative compiled visual instance (primitive or rich component)."""

    model_config = ConfigDict(extra="forbid")

    object_id: str
    kind: CompiledObjectKind = CompiledObjectKind.PRIMITIVE
    primitive_type: CanonicalCapabilityType | None = None
    component_type: str | None = None
    parent_object_id: str | None = None
    child_object_ids: list[str] = Field(default_factory=list)
    local_geometry: LocalRect
    style: PrimitiveStyle = Field(default_factory=PrimitiveStyle)
    properties: dict[str, Any] = Field(default_factory=dict)
    connector_path: ResolvedConnectorPath | None = None

    @model_validator(mode="after")
    def validate_instance(self) -> "CompiledVisualInstance":
        if self.kind == CompiledObjectKind.PRIMITIVE:
            if self.primitive_type is None:
                raise ValueError(f"Primitive visual instance '{self.object_id}' requires primitive_type.")
            if self.component_type is not None:
                raise ValueError(f"Primitive visual instance '{self.object_id}' cannot set component_type.")
            if self.primitive_type == CanonicalCapabilityType.GROUP:
                painted = (
                    self.style.fill is not None
                    or self.style.stroke is not None
                    or self.style.corner_radius is not None
                    or self.style.shadow is not None
                )
                if painted:
                    raise ValueError(
                        f"Group '{self.object_id}' cannot carry painted styles; use a shape child."
                    )
            if self.primitive_type == CanonicalCapabilityType.CONNECTOR and self.connector_path is None:
                raise ValueError(f"Connector '{self.object_id}' requires a resolved connector path.")
            if self.primitive_type != CanonicalCapabilityType.CONNECTOR and self.connector_path is not None:
                raise ValueError(
                    f"Non-connector '{self.object_id}' cannot carry connector geometry."
                )
        elif self.kind == CompiledObjectKind.COMPONENT:
            if self.component_type is None:
                raise ValueError(f"Component visual instance '{self.object_id}' requires component_type.")
            if self.primitive_type is not None:
                raise ValueError(f"Component visual instance '{self.object_id}' cannot set primitive_type.")
            from registries.visual_component_registry import VisualComponentRegistry
            if not VisualComponentRegistry.is_registered(self.component_type):
                raise ValueError(
                    f"Component visual instance '{self.object_id}' references unknown component_type '{self.component_type}'."
                )
            if self.component_type == "FlowConnector" and self.connector_path is None:
                raise ValueError(f"FlowConnector '{self.object_id}' requires a resolved connector path.")
        return self


class CompiledWorld(BaseModel):
    """Validated, one-world compiled result."""

    model_config = ConfigDict(extra="forbid")

    schema_version: str = "2.0"
    world_id: str
    canvas_config: CanvasConfig
    total_duration_frames: int = Field(..., gt=0)
    beat_intervals: list[CompiledBeatInterval] = Field(default_factory=list)
    speech_anchors: list[CompiledSpeechAnchor] = Field(default_factory=list)
    transition_events: list[CompiledTransitionEvent] = Field(default_factory=list)
    objects: dict[str, CompiledVisualInstance] = Field(default_factory=dict)
    primitives: dict[str, CompiledPrimitive] = Field(default_factory=dict)
    lifecycle_tracks: list[CompiledLifecycleTrack] = Field(default_factory=list)
    visibility_intervals: list[CompiledVisibilityInterval] = Field(default_factory=list)
    state_tracks: list[CompiledStateTrack] = Field(default_factory=list)
    animation_tracks: list[CompiledAnimationTrack] = Field(default_factory=list)
    terminal_hold: CompiledTerminalHold | None = None
    macro_zone_allocations: list[CompiledMacroZoneAllocation] = Field(default_factory=list)
    semantic_lineage: list[SourceReference] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def normalize_world_data(cls, data: Any) -> Any:
        if isinstance(data, dict):
            prims = data.get("primitives", {})
            objs = data.get("objects", {})
            if prims and not objs:
                data["objects"] = {
                    pid: {
                        "object_id": p.get("object_id", pid) if isinstance(p, dict) else p.object_id,
                        "kind": "primitive",
                        "primitive_type": p.get("primitive_type") if isinstance(p, dict) else p.primitive_type,
                        "parent_object_id": p.get("parent_object_id") if isinstance(p, dict) else p.parent_object_id,
                        "child_object_ids": p.get("child_object_ids", []) if isinstance(p, dict) else p.child_object_ids,
                        "local_geometry": p.get("local_geometry") if isinstance(p, dict) else p.local_geometry,
                        "style": p.get("style", {}) if isinstance(p, dict) else p.style,
                        "properties": p.get("properties", {}) if isinstance(p, dict) else p.properties,
                        "connector_path": p.get("connector_path") if isinstance(p, dict) else p.connector_path,
                    }
                    for pid, p in prims.items()
                }
            elif objs and not prims:
                data["primitives"] = {
                    oid: {
                        "object_id": o.get("object_id", oid) if isinstance(o, dict) else o.object_id,
                        "primitive_type": o.get("primitive_type", "group") if isinstance(o, dict) else (getattr(o, "primitive_type", None) or "group"),
                        "parent_object_id": o.get("parent_object_id") if isinstance(o, dict) else o.parent_object_id,
                        "child_object_ids": o.get("child_object_ids", []) if isinstance(o, dict) else o.child_object_ids,
                        "local_geometry": o.get("local_geometry") if isinstance(o, dict) else o.local_geometry,
                        "style": o.get("style", {}) if isinstance(o, dict) else o.style,
                        "properties": o.get("properties", {}) if isinstance(o, dict) else o.properties,
                        "connector_path": o.get("connector_path") if isinstance(o, dict) else o.connector_path,
                    }
                    for oid, o in objs.items()
                    if (isinstance(o, dict) and o.get("kind") == "primitive") or (getattr(o, "kind", None) == CompiledObjectKind.PRIMITIVE)
                }
        return data

    @model_validator(mode="after")
    def validate_world(self) -> "CompiledWorld":
        from registries.visual_component_registry import VisualComponentRegistry

        target_map = self.objects if self.objects else self.primitives
        target_ids = set(target_map)
        primitive_ids = target_ids
        roots: set[str] = set()

        for obj_id, obj in target_map.items():
            if obj_id != obj.object_id:
                raise ValueError(f"Registry key '{obj_id}' mismatches object ID.")
            if obj.parent_object_id is None:
                roots.add(obj_id)
            elif obj.parent_object_id not in target_ids:
                raise ValueError(
                    f"Object '{obj_id}' references unknown parent "
                    f"'{obj.parent_object_id}'."
                )
            else:
                parent = target_map[obj.parent_object_id]
                if getattr(parent, "kind", None) == CompiledObjectKind.COMPONENT:
                    desc = VisualComponentRegistry.get_descriptor(parent.component_type)
                    if desc.category.value != "structural_container":
                        raise ValueError(f"Component '{obj_id}' has non-container component parent '{parent.component_type}'.")
                elif getattr(parent, "primitive_type", None) != CanonicalCapabilityType.GROUP:
                    raise ValueError(f"Object '{obj_id}' must have a group or container parent.")

            for child_id in obj.child_object_ids:
                if child_id not in target_ids:
                    raise ValueError(
                        f"Object '{obj_id}' references unknown child '{child_id}'."
                    )
                if target_map[child_id].parent_object_id != obj_id:
                    raise ValueError(
                        f"Child '{child_id}' is not parented by '{obj_id}'."
                    )

        for obj_id in target_ids:
            visited: set[str] = set()
            current: str | None = obj_id
            while current is not None:
                if current in visited:
                    raise ValueError(f"Compiled world contains a parent cycle at '{current}'.")
                visited.add(current)
                current = target_map[current].parent_object_id

        beat_ids = [interval.beat_id for interval in self.beat_intervals]
        if len(beat_ids) != len(set(beat_ids)):
            raise ValueError("Compiled world contains duplicate beat intervals.")
        if any(
            self.beat_intervals[index].start_frame > self.beat_intervals[index + 1].start_frame
            for index in range(len(self.beat_intervals) - 1)
        ):
            raise ValueError("Compiled beat intervals are not ordered globally.")
        if self.beat_intervals and self.beat_intervals[-1].end_frame > self.total_duration_frames:
            raise ValueError("A compiled beat exceeds the world duration.")
        if any(
            self.beat_intervals[index].end_frame > self.beat_intervals[index + 1].start_frame
            for index in range(len(self.beat_intervals) - 1)
        ):
            raise ValueError("Compiled beat intervals overlap globally.")
        if self.beat_intervals:
            if self.terminal_hold is None and self.beat_intervals[-1].end_frame != self.total_duration_frames:
                raise ValueError(
                    "A compiled world with a trailing timeline gap requires an explicit terminal hold."
                )
            if self.terminal_hold is not None:
                if self.terminal_hold.start_frame != self.beat_intervals[-1].end_frame:
                    raise ValueError("Terminal hold must begin at the final beat's end frame.")
                if self.terminal_hold.end_frame != self.total_duration_frames:
                    raise ValueError("Terminal hold must end at the world duration.")

        anchor_ids = [anchor.anchor_id for anchor in self.speech_anchors]
        if len(anchor_ids) != len(set(anchor_ids)):
            raise ValueError("Compiled world contains duplicate speech anchors.")
        if any(anchor.global_frame > self.total_duration_frames for anchor in self.speech_anchors):
            raise ValueError("A speech anchor exceeds the world duration.")
        if any(event.global_frame > self.total_duration_frames for event in self.transition_events):
            raise ValueError("A transition event exceeds the world duration.")

        lifecycle_ids = [track.object_id for track in self.lifecycle_tracks]
        if len(lifecycle_ids) != len(set(lifecycle_ids)):
            raise ValueError("Compiled world contains duplicate lifecycle tracks.")
        if set(lifecycle_ids) != primitive_ids:
            raise ValueError("Every compiled primitive must have exactly one lifecycle track.")
        if any(
            track.introduced_frame > self.total_duration_frames
            or (track.exit_frame is not None and track.exit_frame > self.total_duration_frames)
            for track in self.lifecycle_tracks
        ):
            raise ValueError("A lifecycle track exceeds the world duration.")

        visibility_ids = {interval.object_id for interval in self.visibility_intervals}
        if visibility_ids - primitive_ids:
            raise ValueError("A visibility interval references an unknown primitive.")
        if any(
            interval.end_frame > self.total_duration_frames
            for interval in self.visibility_intervals
        ):
            raise ValueError("A visibility interval exceeds the world duration.")
        for object_id in primitive_ids:
            intervals = sorted(
                (interval for interval in self.visibility_intervals if interval.object_id == object_id),
                key=lambda interval: interval.start_frame,
            )
            if any(
                intervals[index].end_frame > intervals[index + 1].start_frame
                for index in range(len(intervals) - 1)
            ):
                raise ValueError(f"Visibility intervals for '{object_id}' overlap.")

        state_ids = [track.object_id for track in self.state_tracks]
        if len(state_ids) != len(set(state_ids)):
            raise ValueError("Compiled world contains duplicate state tracks.")
        if any(track.object_id not in primitive_ids for track in self.state_tracks):
            raise ValueError("A compiled state track references an unknown primitive.")
        if any(
            change.global_frame > self.total_duration_frames
            for track in self.state_tracks
            for change in track.changes
        ):
            raise ValueError("A state change exceeds the world duration.")

        if any(animation.object_id not in primitive_ids for animation in self.animation_tracks):
            raise ValueError("A compiled animation track references an unknown primitive.")
        animation_ids = [animation.animation_id for animation in self.animation_tracks]
        if len(animation_ids) != len(set(animation_ids)):
            raise ValueError("Compiled world contains duplicate animation IDs.")
        if any(
            animation.trigger_frame + animation.duration_frames > self.total_duration_frames
            for animation in self.animation_tracks
        ):
            raise ValueError("A compiled animation exceeds the world duration.")
        by_property: dict[tuple[str, str], list[CompiledAnimationTrack]] = {}
        for animation in self.animation_tracks:
            by_property.setdefault((animation.object_id, animation.target_property), []).append(animation)
        for key, tracks in by_property.items():
            ordered = sorted(tracks, key=lambda track: (track.trigger_frame, track.animation_id))
            if any(
                ordered[index].trigger_frame + ordered[index].duration_frames
                > ordered[index + 1].trigger_frame
                for index in range(len(ordered) - 1)
            ):
                raise ValueError(
                    f"Animations for '{key[0]}.{key[1]}' overlap without a deterministic authority."
                )

        return self


def _contains_forbidden_connector_reference(value: Any) -> bool:
    if isinstance(value, dict):
        if "target_id" in value or "target_ids" in value:
            return True
        return any(_contains_forbidden_connector_reference(nested) for nested in value.values())
    if isinstance(value, list):
        return any(_contains_forbidden_connector_reference(nested) for nested in value)
    return False
