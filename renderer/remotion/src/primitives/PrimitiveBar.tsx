import React from "react";
import { type PrimitiveSpec, type BarProps } from "./types";
import { evaluateAnimatedProperty } from "./animation";

interface PrimitiveComponentProps {
  spec: PrimitiveSpec<BarProps>;
  currentFrame: number;
  fps: number;
}

export const PrimitiveBar: React.FC<PrimitiveComponentProps> = ({
  spec,
  currentFrame,
  fps,
}) => {
  const { props, animations = [] } = spec;

  const fillPercentage = evaluateAnimatedProperty(
    "fill_percentage",
    props.fill_percentage ?? 1.0,
    animations,
    currentFrame,
    fps
  );

  const fgColor = evaluateAnimatedProperty(
    "foreground_color",
    props.foreground_color || "#3b82f6",
    animations,
    currentFrame,
    fps
  );

  const isHorizontal = (props.orientation || "horizontal") === "horizontal";
  const maxLength = props.max_length ?? 300.0;
  const thickness = props.thickness ?? 24.0;
  const cornerRadius = props.corner_radius ?? 6.0;
  const trackColor = props.background_track_color || "rgba(255, 255, 255, 0.08)";

  const currentLength = Math.max(0, Math.min(1.0, fillPercentage)) * maxLength;

  return (
    <div
      style={{
        width: isHorizontal ? `${maxLength}px` : `${thickness}px`,
        height: isHorizontal ? `${thickness}px` : `${maxLength}px`,
        backgroundColor: trackColor,
        borderRadius: `${cornerRadius}px`,
        overflow: "hidden",
        position: "relative",
        display: "flex",
        alignItems: isHorizontal ? "center" : "flex-end",
      }}
    >
      <div
        style={{
          width: isHorizontal ? `${currentLength}px` : "100%",
          height: isHorizontal ? "100%" : `${currentLength}px`,
          backgroundColor: fgColor,
          borderRadius: `${cornerRadius}px`,
          transition: "none",
        }}
      />
    </div>
  );
};
