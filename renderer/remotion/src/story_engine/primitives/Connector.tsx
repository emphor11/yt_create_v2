import React from "react";
import type { ConnectorProps } from "../types.ts";
import { handDrawn } from "../hand-drawn-theme.ts";

interface ConnectorComponentProps {
  props: ConnectorProps;
  fromPoint: { x: number; y: number };
  toPoint: { x: number; y: number };
  progress: number; // 0 (hidden) to 1 (fully drawn)
  intensityMultiplier?: number;
}

export const Connector: React.FC<ConnectorComponentProps> = ({
  props,
  fromPoint,
  toPoint,
  progress,
  intensityMultiplier = 1,
}) => {
  if (progress <= 0) return null;

  // Path from start to end (using a subtle bezier curve)
  const dx = toPoint.x - fromPoint.x;
  const dy = toPoint.y - fromPoint.y;
  const cx1 = fromPoint.x + dx * 0.5;
  const cy1 = fromPoint.y;
  const cx2 = fromPoint.x + dx * 0.5;
  const cy2 = toPoint.y;

  const pathData = `M ${fromPoint.x} ${fromPoint.y} C ${cx1} ${cy1}, ${cx2} ${cy2}, ${toPoint.x} ${toPoint.y}`;

  // Approximate length for dash animation
  const length = Math.sqrt(dx * dx + dy * dy) * 1.2 + 20;
  const strokeDashoffset = length * (1 - Math.min(1, Math.max(0, progress)));

  const strokeColor = intensityMultiplier > 1.2 ? handDrawn.colors.red : handDrawn.colors.teal;
  const strokeWidth = 3.5 * intensityMultiplier;
  const glowWidth = 7 * intensityMultiplier;

  // Midpoint for label
  const midX = (fromPoint.x + toPoint.x) / 2;
  const midY = (fromPoint.y + toPoint.y) / 2;

  return (
    <svg
      style={{
        position: "absolute",
        top: 0,
        left: 0,
        width: "100%",
        height: "100%",
        pointerEvents: "none",
        zIndex: 5,
        overflow: "visible",
      }}
    >
      <defs>
        <marker
          id={`arrow-${props.fromId}-${props.toId}`}
          viewBox="0 0 10 10"
          refX="6"
          refY="5"
          markerWidth={8 * intensityMultiplier}
          markerHeight={8 * intensityMultiplier}
          orient="auto-start-reverse"
        >
          <path d="M 0 1 L 10 5 L 0 9 z" fill={strokeColor} />
        </marker>
      </defs>

      {/* Background glow path */}
      <path
        d={pathData}
        fill="none"
        stroke={strokeColor}
        strokeWidth={glowWidth}
        strokeOpacity={Math.min(0.28, 0.14 * progress * intensityMultiplier)}
        strokeDasharray={length}
        strokeDashoffset={strokeDashoffset}
      />

      {/* Main connector path */}
      <path
        d={pathData}
        fill="none"
        stroke={strokeColor}
        strokeWidth={strokeWidth}
        strokeDasharray={props.style === "dashed" ? "8 6" : `${length}`}
        strokeDashoffset={strokeDashoffset}
        markerEnd={props.arrow ? `url(#arrow-${props.fromId}-${props.toId})` : undefined}
      />

      {/* Optional Label */}
      {props.label && progress > 0.6 && (
        <g
          transform={`translate(${midX}, ${midY})`}
          style={{
            opacity: (progress - 0.6) / 0.4,
            transition: "opacity 0.2s",
          }}
        >
          <rect
            x={-60}
            y={-14}
            width={120}
            height={28}
            rx={6}
            fill={handDrawn.colors.paperAlt}
            stroke={strokeColor}
            strokeWidth={2}
          />
          <text
            x={0}
            y={4}
            textAnchor="middle"
            fill={handDrawn.colors.ink}
            fontSize={13}
            fontWeight={700}
            fontFamily={handDrawn.font.label}
          >
            {props.label}
          </text>
        </g>
      )}
    </svg>
  );
};
