import React from "react";
import { Loop, OffthreadVideo, staticFile } from "remotion";
import { type PrimitiveSpec, type VideoProps } from "./types";
import { evaluateAnimatedProperty } from "./animation";

interface PrimitiveComponentProps {
  spec: PrimitiveSpec<VideoProps>;
  currentFrame: number;
  fps: number;
}

export const PrimitiveVideo: React.FC<PrimitiveComponentProps> = ({
  spec,
  currentFrame,
  fps,
}) => {
  const { props, layout = {}, animations = [] } = spec;

  const opacity = evaluateAnimatedProperty(
    "opacity",
    1.0,
    animations,
    currentFrame,
    fps
  );

  const source = props.source;
  const src = source.startsWith("http") ? source : staticFile(source);

  const videoElement = (
    <OffthreadVideo
      src={src}
      playbackRate={props.playback_rate ?? 1.0}
      muted={props.muted ?? true}
      style={{
        width: "100%",
        height: "100%",
        objectFit: "cover",
      }}
    />
  );

  return (
    <div
      style={{
        width: layout.width !== undefined && layout.width !== null ? (typeof layout.width === "number" ? `${layout.width}px` : layout.width) : "100%",
        height: layout.height !== undefined && layout.height !== null ? (typeof layout.height === "number" ? `${layout.height}px` : layout.height) : "100%",
        overflow: "hidden",
        opacity,
      }}
    >
      {props.loop && props.loop_duration_frames ? (
        <Loop durationInFrames={props.loop_duration_frames}>
          {videoElement}
        </Loop>
      ) : (
        videoElement
      )}
    </div>
  );
};
