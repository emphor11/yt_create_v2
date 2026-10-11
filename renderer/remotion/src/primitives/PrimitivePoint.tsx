import React from "react";
import { type PrimitiveSpec, type PointProps } from "./types";
import { evaluateAnimatedProperty } from "./animation";

interface PrimitiveComponentProps {
  spec: PrimitiveSpec<PointProps>;
  currentFrame: number;
  fps: number;
}

export const PrimitivePoint: React.FC<PrimitiveComponentProps> = ({
  spec,
  currentFrame,
  fps,
}) => {
  const { props, animations = [] } = spec;

  const currentX = evaluateAnimatedProperty(
    "x",
    props.x,
    animations,
    currentFrame,
    fps
  );

  const currentY = evaluateAnimatedProperty(
    "y",
    props.y,
    animations,
    currentFrame,
    fps
  );

  const pulseScale = evaluateAnimatedProperty(
    "pulse_scale",
    1.0,
    animations,
    currentFrame,
    fps
  );

  const radius = props.radius ?? 6.0;
  const fill = props.fill || "#3b82f6";
  const stroke = props.stroke;
  const strokeWidth = props.stroke_width ?? 0;

  return (
    <div
      style={{
        position: "absolute",
        left: `${currentX}px`,
        top: `${currentY}px`,
        transform: "translate(-50%, -50%)",
        display: "inline-flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <div
        style={{
          width: `${radius * 2}px`,
          height: `${radius * 2}px`,
          borderRadius: "9999px",
          backgroundColor: fill,
          border: stroke ? `${strokeWidth}px solid ${stroke}` : "none",
          transform: `scale(${pulseScale})`,
          boxShadow: `0 0 12px ${fill}80`,
        }}
      />
      {props.label && (
        <span
          style={{
            position: "absolute",
            top: `${radius * 2 + 4}px`,
            fontSize: "12px",
            color: "#a1a1aa",
            whiteSpace: "nowrap",
            fontWeight: 500,
          }}
        >
          {props.label}
        </span>
      )}
    </div>
  );
};
