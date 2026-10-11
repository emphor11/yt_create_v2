import React from "react";
import { type PrimitiveSpec, type IconProps } from "./types";
import { evaluateAnimatedProperty } from "./animation";

interface PrimitiveComponentProps {
  spec: PrimitiveSpec<IconProps>;
  currentFrame: number;
  fps: number;
}

export const PrimitiveIcon: React.FC<PrimitiveComponentProps> = ({
  spec,
  currentFrame,
  fps,
}) => {
  const { props, animations = [] } = spec;

  const color = evaluateAnimatedProperty(
    "color",
    props.color || "#ffffff",
    animations,
    currentFrame,
    fps
  );

  const scale = evaluateAnimatedProperty(
    "scale",
    1.0,
    animations,
    currentFrame,
    fps
  );

  const size = props.size ?? 32;
  const name = props.name;

  return (
    <div
      style={{
        display: "inline-flex",
        alignItems: "center",
        justifyContent: "center",
        width: `${size}px`,
        height: `${size}px`,
        color,
        transform: `scale(${scale})`,
        transformOrigin: "center center",
      }}
    >
      {/* SVG icon or symbol */}
      {name.startsWith("http") || name.endsWith(".svg") ? (
        <img src={name} alt="" style={{ width: "100%", height: "100%", objectFit: "contain" }} />
      ) : (
        <span style={{ fontSize: `${Math.round(size * 0.85)}px`, lineHeight: 1 }}>
          {name === "briefcase" ? "💼" : name === "chart" ? "📈" : name === "check" ? "✓" : name === "alert" ? "⚠️" : name}
        </span>
      )}
    </div>
  );
};
