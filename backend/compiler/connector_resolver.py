"""Deterministic Connector Anchor Coordinate Resolver.

Calculates actual pixel anchor coordinates (from_x, from_y, to_x, to_y) from final resolved
primitive bounding geometry and semantic anchor sides (left, right, top, bottom, center).
"""
from __future__ import annotations

from compiler.models import VisualCompilerError
from domain.primitives.common import CanonicalCapabilityType, PrimitiveLayout
from domain.primitives.spec import PrimitiveSpec


class ConnectorResolver:
    """Resolves semantic connector target IDs and anchor sides into exact pixel coordinates."""

    @classmethod
    def compute_side_coordinate(
        cls,
        layout: PrimitiveLayout,
        side: str | None = "center",
    ) -> tuple[float, float]:
        """Calculates (x, y) anchor point on a primitive's boundary based on side."""
        x = float(layout.x or 0.0)
        y = float(layout.y or 0.0)
        w = float(layout.width if isinstance(layout.width, (int, float)) else 100.0)
        h = float(layout.height if isinstance(layout.height, (int, float)) else 50.0)

        side_norm = (side or "center").strip().lower()

        if side_norm == "left":
            return round(x, 2), round(y + h / 2.0, 2)
        elif side_norm == "right":
            return round(x + w, 2), round(y + h / 2.0, 2)
        elif side_norm == "top":
            return round(x + w / 2.0, 2), round(y, 2)
        elif side_norm == "bottom":
            return round(x + w / 2.0, 2), round(y + h, 2)
        else:  # center
            return round(x + w / 2.0, 2), round(y + h / 2.0, 2)

    @classmethod
    def resolve_connectors(
        cls,
        scene_id: str,
        primitives: dict[str, PrimitiveSpec],
    ) -> None:
        """Resolves all connectors in the primitive map in-place."""
        for prim_id, prim in primitives.items():
            if prim.identity.type != CanonicalCapabilityType.CONNECTOR:
                continue

            from_anchor = prim.props.get("from_anchor")
            to_anchor = prim.props.get("to_anchor")

            if not isinstance(from_anchor, dict) or not isinstance(to_anchor, dict):
                raise VisualCompilerError(
                    f"Connector '{prim_id}' in scene '{scene_id}' missing required from_anchor or to_anchor dict."
                )

            from_target_id = from_anchor.get("target_id")
            to_target_id = to_anchor.get("target_id")

            from_x: float = float(from_anchor.get("x") or 0.0)
            from_y: float = float(from_anchor.get("y") or 0.0)
            to_x: float = float(to_anchor.get("x") or 0.0)
            to_y: float = float(to_anchor.get("y") or 0.0)

            if from_target_id:
                if from_target_id not in primitives:
                    raise VisualCompilerError(
                        f"Connector '{prim_id}' in scene '{scene_id}' from_anchor targets unknown primitive '{from_target_id}'."
                    )
                target_layout = primitives[from_target_id].layout
                from_x, from_y = cls.compute_side_coordinate(
                    target_layout, from_anchor.get("side", "center")
                )
                from_anchor["x"] = from_x
                from_anchor["y"] = from_y

            if to_target_id:
                if to_target_id not in primitives:
                    raise VisualCompilerError(
                        f"Connector '{prim_id}' in scene '{scene_id}' to_anchor targets unknown primitive '{to_target_id}'."
                    )
                target_layout = primitives[to_target_id].layout
                to_x, to_y = cls.compute_side_coordinate(
                    target_layout, to_anchor.get("side", "center")
                )
                to_anchor["x"] = to_x
                to_anchor["y"] = to_y

            # Enclosing bounding rect for connector primitive
            min_x = min(from_x, to_x)
            min_y = min(from_y, to_y)
            width = max(1.0, abs(to_x - from_x))
            height = max(1.0, abs(to_y - from_y))

            prim.layout.x = round(min_x, 2)
            prim.layout.y = round(min_y, 2)
            prim.layout.width = round(width, 2)
            prim.layout.height = round(height, 2)
