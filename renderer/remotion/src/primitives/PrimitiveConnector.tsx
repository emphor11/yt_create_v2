import React from "react";
import { type PrimitiveSpec, type ConnectorProps, type PrimitiveTreeSpec } from "./types";
import { evaluateAnimatedProperty } from "./animation";

interface PrimitiveConnectorComponentProps {
  spec: PrimitiveSpec<ConnectorProps>;
  tree?: PrimitiveTreeSpec;
  currentFrame: number;
  fps: number;
}

export const PrimitiveConnector: React.FC<PrimitiveConnectorComponentProps> = ({
  spec,
  tree,
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

  // Compute anchor coordinates (fallback to defaults if targets not resolved)
  let x1 = props.from_anchor.x ?? 100;
  let y1 = props.from_anchor.y ?? 100;
  let x2 = props.to_anchor.x ?? 300;
  let y2 = props.to_anchor.y ?? 100;

  // Resolve target IDs if specified in tree
  if (tree && props.from_anchor.target_id && tree.primitives[props.from_anchor.target_id]) {
    const target = tree.primitives[props.from_anchor.target_id];
    const tx = target.layout?.x ?? 0;
    const ty = target.layout?.y ?? 0;
    const tw = typeof target.layout?.width === "number" ? target.layout.width : 200;
    const th = typeof target.layout?.height === "number" ? target.layout.height : 100;
    if (props.from_anchor.side === "right") {
      x1 = tx + tw;
      y1 = ty + th / 2;
    } else if (props.from_anchor.side === "bottom") {
      x1 = tx + tw / 2;
      y1 = ty + th;
    } else {
      x1 = tx + tw / 2;
      y1 = ty + th / 2;
    }
  }

  if (tree && props.to_anchor.target_id && tree.primitives[props.to_anchor.target_id]) {
    const target = tree.primitives[props.to_anchor.target_id];
    const tx = target.layout?.x ?? 0;
    const ty = target.layout?.y ?? 0;
    const tw = typeof target.layout?.width === "number" ? target.layout.width : 200;
    const th = typeof target.layout?.height === "number" ? target.layout.height : 100;
    if (props.to_anchor.side === "left") {
      x2 = tx;
      y2 = ty + th / 2;
    } else if (props.to_anchor.side === "top") {
      x2 = tx + tw / 2;
      y2 = ty;
    } else {
      x2 = tx + tw / 2;
      y2 = ty + th / 2;
    }
  }

  const dx = x2 - x1;
  const dy = y2 - y1;
  const minX = Math.min(x1, x2) - 20;
  const minY = Math.min(y1, y2) - 20;
  const width = Math.max(Math.abs(dx) + 40, 40);
  const height = Math.max(Math.abs(dy) + 40, 40);

  // Local coordinates
  const lx1 = x1 - minX;
  const ly1 = y1 - minY;
  const lx2 = x2 - minX;
  const ly2 = y2 - minY;

  let pathData = `M ${lx1} ${ly1} L ${lx2} ${ly2}`;
  if (props.routing === "curved") {
    const cx1 = lx1 + (lx2 - lx1) * 0.5;
    const cy1 = ly1;
    const cx2 = lx1 + (lx2 - lx1) * 0.5;
    const cy2 = ly2;
    pathData = `M ${lx1} ${ly1} C ${cx1} ${cy1}, ${cx2} ${cy2}, ${lx2} ${ly2}`;
  } else if (props.routing === "orthogonal_elbow") {
    const midX = lx1 + (lx2 - lx1) * 0.5;
    pathData = `M ${lx1} ${ly1} L ${midX} ${ly1} L ${midX} ${ly2} L ${lx2} ${ly2}`;
  }

  const strokeWidth = props.stroke_width ?? 2.0;

  return (
    <div
      style={{
        position: "absolute",
        left: `${minX}px`,
        top: `${minY}px`,
        width: `${width}px`,
        height: `${height}px`,
        pointerEvents: "none",
        zIndex: spec.identity.z_index ?? 1,
      }}
    >
      <svg width={width} height={height} style={{ overflow: "visible" }}>
        <defs>
          {props.has_arrow && (
            <marker
              id={`arrow-${spec.identity.id}`}
              viewBox="0 0 10 10"
              refX="6"
              refY="5"
              markerWidth="6"
              markerHeight="6"
              orient="auto-start-reverse"
            >
              <path d="M 0 1 L 10 5 L 0 9 z" fill={stroke} />
            </marker>
          )}
        </defs>
        <path
          d={pathData}
          fill="none"
          stroke={stroke}
          strokeWidth={strokeWidth}
          strokeDasharray={props.stroke_dasharray || (drawProgress < 1 ? "600" : undefined)}
          strokeDashoffset={drawProgress < 1 ? `${(1 - drawProgress) * 600}` : undefined}
          markerEnd={props.has_arrow ? `url(#arrow-${spec.identity.id})` : undefined}
        />
      </svg>
      {props.label && (
        <div
          style={{
            position: "absolute",
            left: `${(lx1 + lx2) / 2}px`,
            top: `${(ly1 + ly2) / 2 - 12}px`,
            transform: "translate(-50%, -50%)",
            backgroundColor: props.label.background || "rgba(0, 0, 0, 0.8)",
            color: stroke,
            padding: "2px 8px",
            borderRadius: "4px",
            fontSize: `${props.label.font_size ?? 14}px`,
            fontWeight: 600,
            whiteSpace: "nowrap",
          }}
        >
          {props.label.text}
        </div>
      )}
    </div>
  );
};
