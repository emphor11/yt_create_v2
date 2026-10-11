import React from "react";
import { type PrimitiveSpec, type ShapeProps } from "./types";
import { evaluateAnimatedProperty } from "./animation";

interface PrimitiveComponentProps {
  spec: PrimitiveSpec<ShapeProps>;
  currentFrame: number;
  fps: number;
}

export const PrimitiveShape: React.FC<PrimitiveComponentProps> = ({
  spec,
  currentFrame,
  fps,
}) => {
  const { props, style = {}, layout = {}, animations = [] } = spec;

  const fill = evaluateAnimatedProperty(
    "style.fill",
    style.fill || "rgba(24, 24, 27, 0.85)",
    animations,
    currentFrame,
    fps
  );

  const stroke = evaluateAnimatedProperty(
    "style.stroke",
    style.stroke || "rgba(255, 255, 255, 0.08)",
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

  const shapeType = props.shape_type || "rectangle";
  let borderRadius: string | number = 16;

  if (shapeType === "circle" || shapeType === "pill" || shapeType === "capsule") {
    borderRadius = "9999px";
  } else if (props.corner_radius !== undefined && props.corner_radius !== null) {
    if (Array.isArray(props.corner_radius)) {
      borderRadius = props.corner_radius.map((r) => `${r}px`).join(" ");
    } else {
      borderRadius = `${props.corner_radius}px`;
    }
  } else if (style.corner_radius !== undefined && style.corner_radius !== null) {
    if (Array.isArray(style.corner_radius)) {
      borderRadius = style.corner_radius.map((r) => `${r}px`).join(" ");
    } else {
      borderRadius = `${style.corner_radius}px`;
    }
  }

  const strokeWidth = style.stroke_width ?? 1;
  const shadow = style.shadow;
  const blurBackdrop = style.blur_backdrop ?? 0;

  return (
    <div
      style={{
        width: layout.width !== undefined && layout.width !== null ? (typeof layout.width === "number" ? `${layout.width}px` : layout.width) : "100%",
        height: layout.height !== undefined && layout.height !== null ? (typeof layout.height === "number" ? `${layout.height}px` : layout.height) : "100%",
        backgroundColor: fill,
        border: stroke ? `${strokeWidth}px solid ${stroke}` : "none",
        borderRadius,
        boxShadow: shadow ? `${shadow.x}px ${shadow.y}px ${shadow.blur}px ${shadow.color}` : "none",
        backdropFilter: blurBackdrop > 0 ? `blur(${blurBackdrop}px)` : "none",
        transform: `scale(${scale})`,
        transformOrigin: "center center",
        boxSizing: "border-box",
      }}
    />
  );
};
