import React from "react";
import { type PrimitiveSpec, type LineProps } from "./types";
import { evaluateAnimatedProperty } from "./animation";

interface PrimitiveComponentProps {
  spec: PrimitiveSpec<LineProps>;
  currentFrame: number;
  fps: number;
}

export const PrimitiveLine: React.FC<PrimitiveComponentProps> = ({
  spec,
  currentFrame,
  fps,
}) => {
  const { props, animations = [] } = spec;

  const stroke = evaluateAnimatedProperty(
    "stroke",
    props.stroke || "#3b82f6",
    animations,
    currentFrame,
    fps
  );

  const drawProgress = evaluateAnimatedProperty(
    "draw_progress",
    1.0,
    animations,
    currentFrame,
    fps
  );

  let points = props.points || [];
  if (points.length < 2) {
    points = [
      { x: 10, y: 110 },
      { x: 310, y: 10 },
    ];
  }

  // Calculate bounding box
  const xs = points.map((p) => p.x);
  const ys = points.map((p) => p.y);
  const minX = Math.min(...xs);
  const maxX = Math.max(...xs);
  const minY = Math.min(...ys);
  const maxY = Math.max(...ys);
  const width = Math.max(maxX - minX + 40, 40);
  const height = Math.max(maxY - minY + 40, 40);

  // Construct SVG path string
  let d = `M ${points[0].x} ${points[0].y}`;
  if (props.curve_type === "monotone_cubic") {
    for (let i = 1; i < points.length; i++) {
      const p0 = points[i - 1];
      const p1 = points[i];
      const mx = (p0.x + p1.x) / 2;
      d += ` C ${mx} ${p0.y}, ${mx} ${p1.y}, ${p1.x} ${p1.y}`;
    }
  } else if (props.curve_type === "step") {
    for (let i = 1; i < points.length; i++) {
      d += ` H ${points[i].x} V ${points[i].y}`;
    }
  } else {
    for (let i = 1; i < points.length; i++) {
      d += ` L ${points[i].x} ${points[i].y}`;
    }
  }

  const strokeWidth = props.stroke_width ?? 3.0;

  return (
    <svg
      width={width}
      height={height}
      style={{ overflow: "visible", position: "relative" }}
    >
      {props.area_fill && (
        <path
          d={`${d} L ${points[points.length - 1].x} ${maxY + 20} L ${points[0].x} ${maxY + 20} Z`}
          fill={props.area_fill}
          opacity={0.15}
        />
      )}
      <path
        d={d}
        fill="none"
        stroke={stroke}
        strokeWidth={strokeWidth}
        strokeDasharray={drawProgress < 1 ? "1000" : undefined}
        strokeDashoffset={drawProgress < 1 ? `${(1 - drawProgress) * 1000}` : undefined}
      />
    </svg>
  );
};
