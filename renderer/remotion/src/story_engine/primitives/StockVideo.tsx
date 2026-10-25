import React from "react";
import { Loop, OffthreadVideo, staticFile, useVideoConfig } from "remotion";
import type { StockVideoProps } from "../types.ts";
import { handDrawn } from "../hand-drawn-theme.ts";

interface StockVideoPrimitiveProps {
  props: StockVideoProps;
  style?: React.CSSProperties;
}

export const StockVideoPrimitive: React.FC<StockVideoPrimitiveProps> = ({ props, style }) => {
  const { alt, caption, fit = "cover", overlayTint, durationSeconds } = props;
  const { fps } = useVideoConfig();

  // Resolve local public or absolute src (supports both src and assetId gracefully)
  const rawSrc = props.src || props.assetId || "";
  const videoSrc = !rawSrc
    ? ""
    : rawSrc.startsWith("http") || rawSrc.startsWith("data:")
    ? rawSrc
    : staticFile(rawSrc);

  const loopDurationInFrames = durationSeconds && Number.isFinite(durationSeconds) && durationSeconds > 0
    ? Math.max(1, Math.ceil(durationSeconds * fps))
    : null;

  const videoElement = (
    <OffthreadVideo
      src={videoSrc}
      muted
      volume={0}
      style={{
        width: "100%",
        height: caption ? "86%" : "100%",
        objectFit: fit,
        display: "block",
      }}
      aria-label={alt ?? "Stock documentary video footage"}
    />
  );

  return (
    <div
      style={{
        position: "relative",
        width: "100%",
        height: "100%",
        overflow: "hidden",
        backgroundColor: handDrawn.colors.paper,
        display: "flex",
        flexDirection: "column",
        ...style,
      }}
    >
      {/* Dark Overlay / Tint Treatment for Text/Subtitle Readability */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          right: 0,
          bottom: caption ? "14%" : 0,
          background:
            overlayTint ||
            "linear-gradient(180deg, rgba(247, 241, 229, 0.03) 0%, rgba(32, 37, 34, 0.42) 100%)",
          pointerEvents: "none",
          zIndex: 2,
        }}
      />

      {/* Main Stock Video footage rendered via OffthreadVideo, looped seamlessly if interval exceeds duration */}
      {videoSrc ? (
        loopDurationInFrames ? (
          <Loop durationInFrames={loopDurationInFrames}>{videoElement}</Loop>
        ) : (
          videoElement
        )
      ) : (
        <div
          style={{
            width: "100%",
            height: caption ? "86%" : "100%",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            color: handDrawn.colors.inkMuted,
            fontSize: 16,
            fontFamily: handDrawn.font.body,
          }}
        >
          {props.assetId || "Stock Video Asset"}
        </div>
      )}

      {/* Optional Caption Bar */}
      {caption && (
        <div
          style={{
            height: "14%",
            backgroundColor: handDrawn.colors.paperAlt,
            borderTop: `2px solid ${handDrawn.colors.ink}33`,
            padding: "0 24px",
            display: "flex",
            alignItems: "center",
            fontFamily: handDrawn.font.body,
            fontSize: 14,
            fontWeight: 500,
            color: handDrawn.colors.ink,
            whiteSpace: "nowrap",
            overflow: "hidden",
            textOverflow: "ellipsis",
            zIndex: 3,
          }}
        >
          {caption}
        </div>
      )}
    </div>
  );
};
