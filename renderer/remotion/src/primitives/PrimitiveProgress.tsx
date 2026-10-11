import React from "react";
import { type PrimitiveSpec, type ProgressProps } from "./types";
import { evaluateAnimatedProperty } from "./animation";

interface PrimitiveComponentProps {
  spec: PrimitiveSpec<ProgressProps>;
  currentFrame: number;
  fps: number;
}

export const PrimitiveProgress: React.FC<PrimitiveComponentProps> = ({
  spec,
  currentFrame,
  fps,
}) => {
  const { props, animations = [] } = spec;

  const progressRatio = evaluateAnimatedProperty(
    "progress_ratio",
    props.progress_ratio ?? 0.5,
    animations,
    currentFrame,
    fps
  );

  const clamped = Math.max(0, Math.min(1.0, progressRatio));
  const isRadial = (props.variant || "radial_ring") === "radial_ring";
  const strokeWidth = props.stroke_width ?? 8.0;
  const trackColor = props.track_color || "rgba(255, 255, 255, 0.1)";
  const fillColor = props.fill_color || "#3b82f6";

  if (!isRadial) {
    // Linear meter
    return (
      <div
        style={{
          width: "100%",
          height: `${strokeWidth * 2}px`,
          backgroundColor: trackColor,
          borderRadius: "9999px",
          overflow: "hidden",
          position: "relative",
        }}
      >
        <div
          style={{
            width: `${clamped * 100}%`,
            height: "100%",
            backgroundColor: fillColor,
            borderRadius: "9999px",
          }}
        />
      </div>
    );
  }

  // Radial ring
  const radius = props.radius ?? 60.0;
  const size = (radius + strokeWidth) * 2;
  const normalizedRadius = radius;
  const circumference = normalizedRadius * 2 * Math.PI;
  const strokeDashoffset = circumference - clamped * circumference;

  return (
    <div
      style={{
        width: `${size}px`,
        height: `${size}px`,
        position: "relative",
        display: "inline-flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <svg width={size} height={size} style={{ transform: "rotate(-90deg)" }}>
        <circle
          stroke={trackColor}
          fill="transparent"
          strokeWidth={strokeWidth}
          r={normalizedRadius}
          cx={size / 2}
          cy={size / 2}
        />
        <circle
          stroke={fillColor}
          fill="transparent"
          strokeWidth={strokeWidth}
          strokeDasharray={`${circumference} ${circumference}`}
          style={{ strokeDashoffset }}
          strokeLinecap="round"
          r={normalizedRadius}
          cx={size / 2}
          cy={size / 2}
        />
      </svg>
      {props.center_label && (
        <span
          style={{
            position: "absolute",
            fontSize: `${Math.round(radius * 0.4)}px`,
            fontWeight: 700,
            color: "#ffffff",
          }}
        >
          {props.center_label}
        </span>
      )}
    </div>
  );
};
