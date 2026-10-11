import React from "react";
import { Img, staticFile } from "remotion";
import { type PrimitiveSpec, type ImageProps } from "./types";
import { evaluateAnimatedProperty } from "./animation";

interface PrimitiveComponentProps {
  spec: PrimitiveSpec<ImageProps>;
  currentFrame: number;
  fps: number;
}

export const PrimitiveImage: React.FC<PrimitiveComponentProps> = ({
  spec,
  currentFrame,
  fps,
}) => {
  const { props, layout = {}, animations = [] } = spec;

  const scale = evaluateAnimatedProperty(
    "scale",
    1.0,
    animations,
    currentFrame,
    fps
  );

  const opacity = evaluateAnimatedProperty(
    "opacity",
    1.0,
    animations,
    currentFrame,
    fps
  );

  const source = props.source;
  const src = source.startsWith("http") || source.startsWith("data:") ? source : staticFile(source);

  return (
    <div
      style={{
        width: layout.width !== undefined && layout.width !== null ? (typeof layout.width === "number" ? `${layout.width}px` : layout.width) : "100%",
        height: layout.height !== undefined && layout.height !== null ? (typeof layout.height === "number" ? `${layout.height}px` : layout.height) : "100%",
        overflow: "hidden",
        borderRadius: `${props.border_radius ?? 0}px`,
        opacity,
      }}
    >
      <Img
        src={src}
        style={{
          width: "100%",
          height: "100%",
          objectFit: props.object_fit || "cover",
          transform: `scale(${scale})`,
          transformOrigin: "center center",
        }}
      />
    </div>
  );
};
