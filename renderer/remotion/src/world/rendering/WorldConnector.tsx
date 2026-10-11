import React from "react";

import type { CompiledPrimitive, CompiledWorld } from "../compiledWorld";
import type { ResolvedPrimitiveFrame } from "../../runtime";

interface ParentSpace {
  width: number;
  height: number;
}

export interface WorldConnectorProps {
  world: CompiledWorld;
  primitive: CompiledPrimitive;
  frame: number;
  parentSpace: ParentSpace;
  resolved: ResolvedPrimitiveFrame;
}

export const WorldConnector: React.FC<WorldConnectorProps> = ({
  world,
  primitive,
  parentSpace,
  resolved,
}) => {
  const path = primitive.connector_path;
  if (!path) {
    throw new Error(`Connector path is missing for '${primitive.object_id}'.`);
  }

  const d = connectorPathToSvg(path.points, path.routing);
  const hasArrow = resolved.props.has_arrow === true;
  const stroke = resolved.style.stroke ?? "#000000";
  const strokeWidth = resolved.style.stroke_width ?? 1;
  const markerId = `world-arrow-${world.world_id}-${primitive.object_id}`;

  return (
    <svg
      data-world-object-id={primitive.object_id}
      width={parentSpace.width}
      height={parentSpace.height}
      viewBox={`0 0 ${parentSpace.width} ${parentSpace.height}`}
      style={{
        position: "absolute",
        left: 0,
        top: 0,
        width: parentSpace.width,
        height: parentSpace.height,
        overflow: "visible",
        pointerEvents: "none",
        opacity: resolved.opacity,
      }}
    >
      {hasArrow && (
        <defs>
          <marker
            id={markerId}
            viewBox="0 0 10 10"
            refX="6"
            refY="5"
            markerWidth="6"
            markerHeight="6"
            orient="auto-start-reverse"
          >
            <path d="M 0 1 L 10 5 L 0 9 z" fill={stroke} />
          </marker>
        </defs>
      )}

      <path
        d={d}
        fill="none"
        stroke={stroke}
        strokeWidth={strokeWidth}
        markerEnd={hasArrow ? `url(#${markerId})` : undefined}
      />
    </svg>
  );
};

function connectorPathToSvg(
  points: readonly { x: number; y: number }[],
  routing: "straight" | "curved" | "orthogonal_elbow",
): string {
  const first = points[0];
  const last = points[points.length - 1];
  if (!first || !last) throw new Error("Compiled connector path must contain points.");

  if (routing === "curved" && points.length >= 4) {
    const controls = points.slice(1, -1);
    const controlA = controls[0];
    const controlB = controls[controls.length - 1];
    return `M ${first.x} ${first.y} C ${controlA.x} ${controlA.y}, ${controlB.x} ${controlB.y}, ${last.x} ${last.y}`;
  }

  return `M ${first.x} ${first.y} ${points
    .slice(1)
    .map((point) => `L ${point.x} ${point.y}`)
    .join(" ")}`;
}
