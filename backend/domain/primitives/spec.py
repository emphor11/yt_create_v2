from __future__ import annotations

from typing import Any
from pydantic import BaseModel, ConfigDict, Field, model_validator

from domain.primitives.common import (
    CanonicalCapabilityType,
    PrimitiveIdentity,
    PrimitiveLayout,
    PrimitiveStyle,
    PrimitiveTiming,
    PrimitiveAnimation,
)


class PrimitiveSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    identity: PrimitiveIdentity
    layout: PrimitiveLayout = Field(default_factory=PrimitiveLayout)
    style: PrimitiveStyle = Field(default_factory=PrimitiveStyle)
    timing: PrimitiveTiming = Field(default_factory=PrimitiveTiming)
    props: dict[str, Any] = Field(default_factory=dict)
    current_state: dict[str, Any] = Field(default_factory=dict)
    animations: list[PrimitiveAnimation] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_props_against_type(self) -> PrimitiveSpec:
        from registries.primitive_registry import PrimitiveRegistry

        PrimitiveRegistry.validate_primitive_props(
            self.identity.type, self.props
        )
        return self


class PrimitiveTreeSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scene_id: str
    duration_frames: int = Field(gt=0)
    root_primitive_ids: list[str] = Field(default_factory=list)
    primitives: dict[str, PrimitiveSpec] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_tree_integrity(self) -> PrimitiveTreeSpec:
        # 1. Validate that all root_primitive_ids exist
        for root_id in self.root_primitive_ids:
            if root_id not in self.primitives:
                raise ValueError(f"Root primitive ID '{root_id}' not found in primitives map.")
            root_prim = self.primitives[root_id]
            if root_prim.identity.parent_id is not None:
                raise ValueError(
                    f"Root primitive '{root_id}' cannot have a parent_id ('{root_prim.identity.parent_id}')."
                )

        # 2. Validate all parent-child references
        for prim_id, prim in self.primitives.items():
            if prim.identity.id != prim_id:
                raise ValueError(
                    f"Mismatch between primitive key '{prim_id}' and identity.id '{prim.identity.id}'."
                )

            # Check parent exists
            if prim.identity.parent_id is not None:
                if prim.identity.parent_id not in self.primitives:
                    raise ValueError(
                        f"Primitive '{prim_id}' references non-existent parent '{prim.identity.parent_id}'."
                    )
                parent_prim = self.primitives[prim.identity.parent_id]
                if parent_prim.identity.type != CanonicalCapabilityType.GROUP:
                    raise ValueError(
                        f"Parent '{prim.identity.parent_id}' of primitive '{prim_id}' must be of type 'group', got '{parent_prim.identity.type}'."
                    )

            # Check group children
            if prim.identity.type == CanonicalCapabilityType.GROUP:
                child_ids = prim.props.get("child_ids", [])
                for cid in child_ids:
                    if cid not in self.primitives:
                        raise ValueError(
                            f"Group '{prim_id}' references non-existent child '{cid}'."
                        )
                    child_prim = self.primitives[cid]
                    if child_prim.identity.parent_id != prim_id:
                        raise ValueError(
                            f"Child '{cid}' of group '{prim_id}' has inconsistent parent_id '{child_prim.identity.parent_id}'."
                        )

            # Check connector targets
            if prim.identity.type == CanonicalCapabilityType.CONNECTOR:
                from_anchor = prim.props.get("from_anchor", {})
                to_anchor = prim.props.get("to_anchor", {})
                if isinstance(from_anchor, dict) and from_anchor.get("target_id"):
                    tid = from_anchor["target_id"]
                    if tid not in self.primitives:
                        raise ValueError(
                            f"Connector '{prim_id}' from_anchor references non-existent target '{tid}'."
                        )
                if isinstance(to_anchor, dict) and to_anchor.get("target_id"):
                    tid = to_anchor["target_id"]
                    if tid not in self.primitives:
                        raise ValueError(
                            f"Connector '{prim_id}' to_anchor references non-existent target '{tid}'."
                        )

        # 3. Detect cyclic parent relationships
        for prim_id in self.primitives:
            visited = set()
            curr = prim_id
            while curr is not None:
                if curr in visited:
                    raise ValueError(f"Cyclic parent-child reference detected involving primitive '{curr}'.")
                visited.add(curr)
                parent_id = self.primitives[curr].identity.parent_id
                curr = parent_id

        return self
