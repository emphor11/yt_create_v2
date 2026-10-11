import React from "react";
import { type PrimitiveSpec, type SegmentProps } from "./types";
import { evaluateAnimatedProperty } from "./animation";

interface PrimitiveComponentProps {
  spec: PrimitiveSpec<SegmentProps>;
  currentFrame: number;
  fps: number;
}

export const PrimitiveSegment: React.FC<PrimitiveComponentProps> = ({
  spec,
  currentFrame,
  fps,
}) => {
  const { props, animations = [] } = spec;

  const startRatio = evaluateAnimatedProperty(
    "start_ratio",
    props.start_ratio ?? 0.0,
    animations,
    currentFrame,
    fps
  );

  const lengthRatio = evaluateAnimatedProperty(
    "length_ratio",
    props.length_ratio ?? 1.0,
    animations,
    currentFrame,
    fps
  );

  const fill = props.fill || "#3b82f6";

  return (
    <div
      style={{
        position: "absolute",
        left: `${startRatio * 100}%`,
        width: `${lengthRatio * 100}%`,
        height: "100%",
        backgroundColor: fill,
        borderRadius: "4px",
        overflow: "hidden",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      {props.label && (
        <span style={{ fontSize: "12px", color: "#ffffff", fontWeight: 600, padding: "0 4px", whiteSpace: "nowrap" }}>
          {props.label}
        </span>
      )}
    </div>
  );
};
