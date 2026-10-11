from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from pydantic import BaseModel

from domain.primitives.common import CanonicalCapabilityType, CANONICAL_CAPABILITY_TYPES, FORBIDDEN_COMPOSITION_TYPES
from domain.primitives.props import (
    TextProps, TextState,
    NumberProps, NumberState,
    ShapeProps, ShapeState,
    IconProps, IconState,
    ConnectorProps, ConnectorState,
    ImageProps, ImageState,
    VideoProps, VideoState,
    BarProps, BarState,
    LineProps, LineState,
    PointProps, PointState,
    SegmentProps, SegmentState,
    ProgressProps, ProgressState,
    GroupProps, GroupState,
)


@dataclass(frozen=True)
class CapabilityDescriptor:
    type_name: CanonicalCapabilityType
    props_model: type[BaseModel]
    state_model: type[BaseModel]
    supported_state_changes: tuple[str, ...]
    supported_behaviors: tuple[str, ...]
    renderer_component: str


class PrimitiveRegistryError(Exception):
    """Raised when an invalid primitive operation or disallowed composition is encountered."""


class PrimitiveRegistry:
    """
    Canonical Python Primitive Registry.
    Guarantees that only genuine low-level visual capabilities can be registered and validated.
    Disallows any high-level composition names (cards, KPIs, templates).
    """

    CAPABILITIES: dict[CanonicalCapabilityType, CapabilityDescriptor] = {
        CanonicalCapabilityType.TEXT: CapabilityDescriptor(
            type_name=CanonicalCapabilityType.TEXT,
            props_model=TextProps,
            state_model=TextState,
            supported_state_changes=("update_content", "update_highlight"),
            supported_behaviors=("appear", "highlight", "transform"),
            renderer_component="PrimitiveText",
        ),
        CanonicalCapabilityType.NUMBER: CapabilityDescriptor(
            type_name=CanonicalCapabilityType.NUMBER,
            props_model=NumberProps,
            state_model=NumberState,
            supported_state_changes=("count_to", "set_delta"),
            supported_behaviors=("count_up", "impact_settle"),
            renderer_component="PrimitiveNumber",
        ),
        CanonicalCapabilityType.SHAPE: CapabilityDescriptor(
            type_name=CanonicalCapabilityType.SHAPE,
            props_model=ShapeProps,
            state_model=ShapeState,
            supported_state_changes=("resize", "recolor", "elevate"),
            supported_behaviors=("scale_spring", "pulse_glow"),
            renderer_component="PrimitiveShape",
        ),
        CanonicalCapabilityType.ICON: CapabilityDescriptor(
            type_name=CanonicalCapabilityType.ICON,
            props_model=IconProps,
            state_model=IconState,
            supported_state_changes=("change_icon", "change_color"),
            supported_behaviors=("bloom", "pop"),
            renderer_component="PrimitiveIcon",
        ),
        CanonicalCapabilityType.CONNECTOR: CapabilityDescriptor(
            type_name=CanonicalCapabilityType.CONNECTOR,
            props_model=ConnectorProps,
            state_model=ConnectorState,
            supported_state_changes=("redirect", "activate"),
            supported_behaviors=("draw_path", "label_reveal"),
            renderer_component="PrimitiveConnector",
        ),
        CanonicalCapabilityType.IMAGE: CapabilityDescriptor(
            type_name=CanonicalCapabilityType.IMAGE,
            props_model=ImageProps,
            state_model=ImageState,
            supported_state_changes=("swap_source",),
            supported_behaviors=("ken_burns", "fade_in"),
            renderer_component="PrimitiveImage",
        ),
        CanonicalCapabilityType.VIDEO: CapabilityDescriptor(
            type_name=CanonicalCapabilityType.VIDEO,
            props_model=VideoProps,
            state_model=VideoState,
            supported_state_changes=("seek",),
            supported_behaviors=("looping_playback",),
            renderer_component="PrimitiveVideo",
        ),
        CanonicalCapabilityType.BAR: CapabilityDescriptor(
            type_name=CanonicalCapabilityType.BAR,
            props_model=BarProps,
            state_model=BarState,
            supported_state_changes=("update_fill", "change_polarity"),
            supported_behaviors=("grow",),
            renderer_component="PrimitiveBar",
        ),
        CanonicalCapabilityType.LINE: CapabilityDescriptor(
            type_name=CanonicalCapabilityType.LINE,
            props_model=LineProps,
            state_model=LineState,
            supported_state_changes=("append_point", "morph_points"),
            supported_behaviors=("draw_line",),
            renderer_component="PrimitiveLine",
        ),
        CanonicalCapabilityType.POINT: CapabilityDescriptor(
            type_name=CanonicalCapabilityType.POINT,
            props_model=PointProps,
            state_model=PointState,
            supported_state_changes=("move_to", "pulse"),
            supported_behaviors=("beacon_pulse",),
            renderer_component="PrimitivePoint",
        ),
        CanonicalCapabilityType.SEGMENT: CapabilityDescriptor(
            type_name=CanonicalCapabilityType.SEGMENT,
            props_model=SegmentProps,
            state_model=SegmentState,
            supported_state_changes=("resize_ratio",),
            supported_behaviors=("slide_and_expand"),
            renderer_component="PrimitiveSegment",
        ),
        CanonicalCapabilityType.PROGRESS: CapabilityDescriptor(
            type_name=CanonicalCapabilityType.PROGRESS,
            props_model=ProgressProps,
            state_model=ProgressState,
            supported_state_changes=("set_progress",),
            supported_behaviors=("sweep",),
            renderer_component="PrimitiveProgress",
        ),
        CanonicalCapabilityType.GROUP: CapabilityDescriptor(
            type_name=CanonicalCapabilityType.GROUP,
            props_model=GroupProps,
            state_model=GroupState,
            supported_state_changes=("shift", "fade_group"),
            supported_behaviors=("group_cascade",),
            renderer_component="PrimitiveGroup",
        ),
    }

    # Explicit disallowed composition names (cannot be primitives)
    DISALLOWED_COMPOSITIONS = FORBIDDEN_COMPOSITION_TYPES

    @classmethod
    def normalize_type(cls, capability_type: str | CanonicalCapabilityType) -> CanonicalCapabilityType:
        if isinstance(capability_type, CanonicalCapabilityType):
            return capability_type

        cleaned = str(capability_type).strip().lower()
        if cleaned in cls.DISALLOWED_COMPOSITIONS:
            raise PrimitiveRegistryError(
                f"'{capability_type}' is a high-level composite pattern, NOT a canonical primitive. "
                f"Construct it by composing groups, shapes, text, numbers, etc."
            )

        try:
            return CanonicalCapabilityType(cleaned)
        except ValueError:
            raise PrimitiveRegistryError(
                f"Unknown primitive capability type '{capability_type}'. "
                f"Must be one of: {CANONICAL_CAPABILITY_TYPES}"
            )

    @classmethod
    def get_descriptor(cls, capability_type: str | CanonicalCapabilityType) -> CapabilityDescriptor:
        norm = cls.normalize_type(capability_type)
        return cls.CAPABILITIES[norm]

    @classmethod
    def validate_primitive_props(
        cls,
        capability_type: str | CanonicalCapabilityType,
        props: dict[str, Any]
    ) -> BaseModel:
        desc = cls.get_descriptor(capability_type)
        return desc.props_model.model_validate(props)

    @classmethod
    def validate_state_change(
        cls,
        capability_type: str | CanonicalCapabilityType,
        state_change: str
    ) -> bool:
        desc = cls.get_descriptor(capability_type)
        return state_change in desc.supported_state_changes

    @classmethod
    def validate_behavior(
        cls,
        capability_type: str | CanonicalCapabilityType,
        behavior: str
    ) -> bool:
        desc = cls.get_descriptor(capability_type)
        return behavior in desc.supported_behaviors

    @classmethod
    def get_renderer_mapping(
        cls,
        capability_type: str | CanonicalCapabilityType
    ) -> str:
        desc = cls.get_descriptor(capability_type)
        return desc.renderer_component
