"""Deterministic Micro Auto-Layout Engine.

Resolves hierarchical group layouts using the Storyboarder's container flow (row, column, free),
alignment, justification, semantic gap, and padding.
Computes intrinsic content sizes and resolves child coordinates and bounds deterministically.
"""
from __future__ import annotations

import math
from typing import Any
from compiler.models import Rect, VisualCompilerError
from compiler.token_resolver import TokenResolver
from domain.primitives.common import CanonicalCapabilityType, MarginPadding, PrimitiveLayout
from domain.storyboard import (
    ContainerFlow,
    FlowAlignment,
    FlowJustification,
    MicroLayoutFlow,
    StoryboardNode,
)


class MicroLayoutEngine:
    """Calculates deterministic bounding geometry for primitives and hierarchical groups."""

    def __init__(self, token_resolver: TokenResolver | None = None):
        self.token_resolver = token_resolver or TokenResolver()

    def estimate_intrinsic_size(
        self,
        node: StoryboardNode,
        max_available_width: float = 1200.0,
    ) -> tuple[float, float]:
        """Calculates the intrinsic (width, height) of a primitive node."""
        ntype = node.type.value if hasattr(node.type, "value") else str(node.type)

        # 1. Text Primitive
        if ntype == CanonicalCapabilityType.TEXT.value:
            typo = self.token_resolver.resolve_typography(node.style.typography_role)
            font_size = float(node.props.get("font_size", typo["font_size"]))
            line_height = float(node.props.get("line_height", typo["line_height"]))
            content = str(node.props.get("content", node.name or "Text"))
            
            # Approximate character width based on typography scale
            char_w = font_size * 0.58
            single_line_w = max(40.0, len(content) * char_w)
            line_h = font_size * line_height

            wrap = bool(node.props.get("wrap", True))
            if wrap and single_line_w > max_available_width:
                lines = math.ceil(single_line_w / max_available_width)
                return round(max_available_width, 2), round(lines * line_h, 2)
            return round(single_line_w, 2), round(line_h, 2)

        # 2. Number Primitive
        elif ntype == CanonicalCapabilityType.NUMBER.value:
            typo = self.token_resolver.resolve_typography(node.style.typography_role)
            font_size = float(node.props.get("font_size", typo["font_size"]))
            val = node.props.get("value", 0)
            prefix = str(node.props.get("prefix", ""))
            suffix = str(node.props.get("suffix", ""))
            formatted = f"{prefix}{val}{suffix}"
            char_w = font_size * 0.62
            w = max(60.0, len(formatted) * char_w)
            h = font_size * 1.2
            return round(w, 2), round(h, 2)

        # 3. Icon Primitive
        elif ntype == CanonicalCapabilityType.ICON.value:
            size = float(node.props.get("size", 40.0))
            return size, size

        # 4. Shape Primitive
        elif ntype == CanonicalCapabilityType.SHAPE.value:
            stype = str(node.props.get("shape_type", "rectangle"))
            if stype == "circle":
                return 80.0, 80.0
            elif stype in ("pill", "capsule"):
                return 160.0, 48.0
            return 320.0, 200.0

        # 5. Bar Primitive
        elif ntype == CanonicalCapabilityType.BAR.value:
            orientation = str(node.props.get("orientation", "horizontal"))
            max_len = float(node.props.get("max_length", 320.0))
            thickness = float(node.props.get("thickness", 28.0))
            if orientation == "vertical":
                return thickness, max_len
            return max_len, thickness

        # 6. Line Primitive
        elif ntype == CanonicalCapabilityType.LINE.value:
            return 400.0, 240.0

        # 7. Point Primitive
        elif ntype == CanonicalCapabilityType.POINT.value:
            r = float(node.props.get("radius", 8.0))
            return r * 2, r * 2

        # 8. Segment Primitive
        elif ntype == CanonicalCapabilityType.SEGMENT.value:
            return 280.0, 24.0

        # 9. Progress Primitive
        elif ntype == CanonicalCapabilityType.PROGRESS.value:
            r = float(node.props.get("radius", 64.0))
            return r * 2, r * 2

        # 10. Image & Video Primitives
        elif ntype in (CanonicalCapabilityType.IMAGE.value, CanonicalCapabilityType.VIDEO.value):
            return 480.0, 270.0

        # 11. Connector Primitive
        elif ntype == CanonicalCapabilityType.CONNECTOR.value:
            return 120.0, 40.0

        # 12. Group Primitive (Recursive intrinsic sizing)
        elif ntype == CanonicalCapabilityType.GROUP.value:
            flow_spec = node.flow or MicroLayoutFlow()
            flow_dir = flow_spec.flow.value if hasattr(flow_spec.flow, "value") else str(flow_spec.flow)
            gap = self.token_resolver.resolve_spacing(flow_spec.gap)
            padding = self.token_resolver.resolve_spacing(flow_spec.padding)

            if not node.children:
                # Default empty group size
                return round(200.0 + 2 * padding, 2), round(100.0 + 2 * padding, 2)

            child_sizes = [
                self.estimate_intrinsic_size(c, max_available_width - 2 * padding)
                for c in node.children
            ]

            if flow_dir == ContainerFlow.COLUMN.value:
                content_w = max(cw for cw, _ in child_sizes)
                content_h = sum(ch for _, ch in child_sizes) + max(0, len(child_sizes) - 1) * gap
                return round(content_w + 2 * padding, 2), round(content_h + 2 * padding, 2)
            elif flow_dir == ContainerFlow.ROW.value:
                content_w = sum(cw for cw, _ in child_sizes) + max(0, len(child_sizes) - 1) * gap
                content_h = max(ch for _, ch in child_sizes)
                return round(content_w + 2 * padding, 2), round(content_h + 2 * padding, 2)
            else:  # Free layout
                content_w = max(cw for cw, _ in child_sizes)
                content_h = max(ch for _, ch in child_sizes)
                return round(content_w + 2 * padding, 2), round(content_h + 2 * padding, 2)

        return 200.0, 100.0

    def layout_node_tree(
        self,
        node: StoryboardNode,
        allocated_bounds: Rect,
        parent_id: str | None = None,
    ) -> dict[str, PrimitiveLayout]:
        """Recursively computes deterministic PrimitiveLayout for a node and all its descendants.

        Returns a dictionary mapping node_id -> PrimitiveLayout.
        """
        results: dict[str, PrimitiveLayout] = {}
        ntype = node.type.value if hasattr(node.type, "value") else str(node.type)

        if ntype != CanonicalCapabilityType.GROUP.value:
            # Leaf primitive gets allocated bounds
            results[node.id] = PrimitiveLayout(
                position_mode="relative" if parent_id else "absolute",
                x=round(allocated_bounds.x, 2),
                y=round(allocated_bounds.y, 2),
                width=round(allocated_bounds.width, 2),
                height=round(allocated_bounds.height, 2),
                anchor_origin="top-left",
            )
            return results

        # Group primitive
        flow_spec = node.flow or MicroLayoutFlow()
        flow_dir = flow_spec.flow.value if hasattr(flow_spec.flow, "value") else str(flow_spec.flow)
        align = flow_spec.alignment.value if hasattr(flow_spec.alignment, "value") else str(flow_spec.alignment)
        justify = flow_spec.justification.value if hasattr(flow_spec.justification, "value") else str(flow_spec.justification)
        gap = self.token_resolver.resolve_spacing(flow_spec.gap)
        padding = self.token_resolver.resolve_spacing(flow_spec.padding)

        # Group's own layout
        group_layout = PrimitiveLayout(
            position_mode="relative" if parent_id else "absolute",
            x=round(allocated_bounds.x, 2),
            y=round(allocated_bounds.y, 2),
            width=round(allocated_bounds.width, 2),
            height=round(allocated_bounds.height, 2),
            anchor_origin="top-left",
            padding=MarginPadding(top=padding, right=padding, bottom=padding, left=padding),
        )
        results[node.id] = group_layout

        if not node.children:
            return results

        # Compute sizes of each child
        child_sizes = [
            self.estimate_intrinsic_size(child, allocated_bounds.width - 2 * padding)
            for child in node.children
        ]

        # Inner bounds available for children
        inner_x = allocated_bounds.x + padding
        inner_y = allocated_bounds.y + padding
        inner_w = max(10.0, allocated_bounds.width - 2 * padding)
        inner_h = max(10.0, allocated_bounds.height - 2 * padding)

        if flow_dir == ContainerFlow.COLUMN.value:
            total_content_h = sum(ch for _, ch in child_sizes) + max(0, len(node.children) - 1) * gap
            current_y = inner_y

            # Handle main-axis vertical justification if extra vertical space exists
            extra_h = inner_h - total_content_h
            if justify == FlowJustification.CENTER.value and extra_h > 0:
                current_y += extra_h / 2.0
            elif justify == FlowJustification.END.value and extra_h > 0:
                current_y += extra_h

            for child, (cw, ch) in zip(node.children, child_sizes):
                # Cross-axis (X) alignment
                if align == FlowAlignment.CENTER.value:
                    child_x = inner_x + (inner_w - cw) / 2.0
                    child_w = cw
                elif align == FlowAlignment.END.value:
                    child_x = inner_x + inner_w - cw
                    child_w = cw
                elif align == FlowAlignment.STRETCH.value:
                    child_x = inner_x
                    child_w = inner_w
                else:  # START
                    child_x = inner_x
                    child_w = cw

                child_rect = Rect(x=child_x, y=current_y, width=child_w, height=ch)
                child_layouts = self.layout_node_tree(child, child_rect, parent_id=node.id)
                results.update(child_layouts)
                current_y += ch + gap

        elif flow_dir == ContainerFlow.ROW.value:
            total_content_w = sum(cw for cw, _ in child_sizes) + max(0, len(node.children) - 1) * gap
            current_x = inner_x

            # Handle main-axis horizontal justification
            extra_w = inner_w - total_content_w
            if justify == FlowJustification.CENTER.value and extra_w > 0:
                current_x += extra_w / 2.0
            elif justify == FlowJustification.END.value and extra_w > 0:
                current_x += extra_w
            elif justify == FlowJustification.SPACE_BETWEEN.value and len(node.children) > 1 and extra_w > 0:
                gap += extra_w / (len(node.children) - 1)

            for child, (cw, ch) in zip(node.children, child_sizes):
                # Cross-axis (Y) alignment
                if align == FlowAlignment.CENTER.value:
                    child_y = inner_y + (inner_h - ch) / 2.0
                    child_h = ch
                elif align == FlowAlignment.END.value:
                    child_y = inner_y + inner_h - ch
                    child_h = ch
                elif align == FlowAlignment.STRETCH.value:
                    child_y = inner_y
                    child_h = inner_h
                else:  # START
                    child_y = inner_y
                    child_h = ch

                child_rect = Rect(x=current_x, y=child_y, width=cw, height=child_h)
                child_layouts = self.layout_node_tree(child, child_rect, parent_id=node.id)
                results.update(child_layouts)
                current_x += cw + gap

        else:  # FREE
            for child, (cw, ch) in zip(node.children, child_sizes):
                child_rect = Rect(x=inner_x, y=inner_y, width=cw, height=ch)
                child_layouts = self.layout_node_tree(child, child_rect, parent_id=node.id)
                results.update(child_layouts)

        return results
