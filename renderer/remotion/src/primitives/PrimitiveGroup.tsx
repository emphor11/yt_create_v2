import React from "react";
import { type PrimitiveSpec, type GroupProps, type PrimitiveTreeSpec } from "./types";
import { evaluateAnimatedProperty } from "./animation";
import { renderPrimitiveNode } from "./registry";

interface PrimitiveGroupComponentProps {
  spec: PrimitiveSpec<GroupProps>;
  tree?: PrimitiveTreeSpec;
  currentFrame: number;
  fps: number;
}

export const PrimitiveGroup: React.FC<PrimitiveGroupComponentProps> = ({
  spec,
  tree,
  currentFrame,
  fps,
}) => {
  const { props, layout = {}, style = {}, animations = [] } = spec;

  const shiftX = evaluateAnimatedProperty(
    "shift_x",
    0,
    animations,
    currentFrame,
    fps
  );

  const shiftY = evaluateAnimatedProperty(
    "shift_y",
    0,
    animations,
    currentFrame,
    fps
  );

  const groupOpacity = evaluateAnimatedProperty(
    "group_opacity",
    style.opacity ?? 1.0,
    animations,
    currentFrame,
    fps
  );

  const layoutFlow = props.layout_flow || "none";
  const gap = props.gap ?? 0;
  const alignItems = props.align_items || "flex-start";
  const justifyContent = props.justify_content || "flex-start";

  const isFlex = layoutFlow === "row" || layoutFlow === "column";
  const childIds = props.child_ids || [];

  // Sort children by z_index
  const sortedChildren = childIds
    .map((cid) => tree?.primitives[cid])
    .filter((child): child is PrimitiveSpec => Boolean(child))
    .sort((a, b) => (a.identity.z_index ?? 0) - (b.identity.z_index ?? 0));

  const padding = layout.padding;

  return (
    <div
      style={{
        display: isFlex ? "flex" : "block",
        flexDirection: layoutFlow === "row" ? "row" : layoutFlow === "column" ? "column" : undefined,
        gap: isFlex && gap > 0 ? `${gap}px` : undefined,
        alignItems: isFlex ? alignItems : undefined,
        justifyContent: isFlex ? justifyContent : undefined,
        position: layout.position_mode === "absolute" ? "absolute" : "relative",
        left: layout.x !== undefined && layout.x !== null ? `${layout.x}px` : undefined,
        top: layout.y !== undefined && layout.y !== null ? `${layout.y}px` : undefined,
        width: layout.width !== undefined && layout.width !== null ? (typeof layout.width === "number" ? `${layout.width}px` : layout.width) : undefined,
        height: layout.height !== undefined && layout.height !== null ? (typeof layout.height === "number" ? `${layout.height}px` : layout.height) : undefined,
        paddingTop: padding?.top !== undefined ? `${padding.top}px` : undefined,
        paddingRight: padding?.right !== undefined ? `${padding.right}px` : undefined,
        paddingBottom: padding?.bottom !== undefined ? `${padding.bottom}px` : undefined,
        paddingLeft: padding?.left !== undefined ? `${padding.left}px` : undefined,
        transform: `translate(${shiftX}px, ${shiftY}px)`,
        opacity: groupOpacity,
        zIndex: spec.identity.z_index ?? 0,
        boxSizing: "border-box",
      }}
    >
      {sortedChildren.map((childSpec) => renderPrimitiveNode(childSpec, tree, currentFrame, fps))}
    </div>
  );
};
