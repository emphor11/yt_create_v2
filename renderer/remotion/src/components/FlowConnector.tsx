import React from "react";
import type { CompiledVisualInstance } from "../world/compiledWorld";
import type { ResolvedPrimitiveFrame } from "../world/runtime/types";
import type { WorldRuntime } from "../world/runtime";

export interface ComponentProps {
  runtime: WorldRuntime;
  instance: CompiledVisualInstance;
  resolved: ResolvedPrimitiveFrame;
  frame: number;
}

export const FlowConnector: React.FC<ComponentProps> = ({
  instance,
  resolved,
}) => {
  const path = instance.connector_path;
  if (!path || path.points.length < 2) return null;

  const props = resolved.props;
  const relationship = (props.relationship_type as string) || "causes";
  const hasArrow = props.has_arrow !== false;
  const label = props.label as string | undefined;
  const styleIntent = (props.style_intent as string) || "solid";

  const colorMap: Record<string, string> = {
    causes: "#38bdf8",
    flows_to: "#38bdf8",
    contrasts_with: "#f43f5e",
    subtracts: "#fb7185",
    absorbs: "#a78bfa",
  };
  const strokeColor = resolved.style.stroke || colorMap[relationship] || "#38bdf8";

  // Convert points to SVG-local coordinates relative to resolved.geometry
  const localPoints = path.points.map((p) => ({
    x: p.x - resolved.geometry.x,
    y: p.y - resolved.geometry.y,
  }));

  // Build SVG path data
  const pathD = localPoints.reduce(
    (acc, pt, index) => `${acc} ${index === 0 ? "M" : "L"} ${pt.x} ${pt.y}`,
    ""
  );

  // Compute middle point for the label
  const midIndex = Math.floor(localPoints.length / 2);
  const midPt = localPoints[midIndex] || localPoints[0];

  const markerId = `arrow-${instance.object_id}`;

  return (
    <div
      data-visual-component="FlowConnector"
      data-object-id={instance.object_id}
      style={{
        position: "absolute",
        left: resolved.geometry.x,
        top: resolved.geometry.y,
        width: resolved.geometry.width,
        height: resolved.geometry.height,
        opacity: resolved.opacity,
        pointerEvents: "none",
        overflow: "visible",
      }}
    >
      <svg
        style={{
          width: "100%",
          height: "100%",
          overflow: "visible",
        }}
      >
        <defs>
          <marker
            id={markerId}
            viewBox="0 0 10 10"
            refX="7"
            refY="5"
            markerWidth="6"
            markerHeight="6"
            orient="auto-start-reverse"
          >
            <path d="M 0 1 L 9 5 L 0 9 z" fill={strokeColor} />
          </marker>
        </defs>

        <path
          d={pathD}
          fill="none"
          stroke={strokeColor}
          strokeWidth={resolved.style.stroke_width || 2.5}
          strokeDasharray={styleIntent === "dashed" ? "6 4" : undefined}
          markerEnd={hasArrow ? `url(#${markerId})` : undefined}
          strokeLinecap="round"
          strokeLinejoin="round"
          style={{
            filter: `drop-shadow(0 0 6px ${strokeColor}66)`,
          }}
        />
      </svg>

      {/* Central Connector Label (e.g. 'vs', 'causes') */}
      {label && (
        <div
          style={{
            position: "absolute",
            left: midPt.x,
            top: midPt.y,
            transform: "translate(-50%, -50%)",
            background: "#0f172a",
            border: `1px solid ${strokeColor}88`,
            borderRadius: 9999,
            padding: "2px 10px",
            fontSize: 11,
            fontWeight: 700,
            textTransform: "uppercase",
            letterSpacing: "0.08em",
            color: "#f1f5f9",
            fontFamily: "Inter, ui-sans-serif, system-ui, sans-serif",
            boxShadow: "0 4px 12px rgba(0, 0, 0, 0.6)",
            userSelect: "none",
            pointerEvents: "auto",
          }}
        >
          {label}
        </div>
      )}
    </div>
  );
};
