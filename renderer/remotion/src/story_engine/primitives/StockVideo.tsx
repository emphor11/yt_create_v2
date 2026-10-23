import React from "react";
import { OffthreadVideo, staticFile } from "remotion";
import type { StockVideoProps } from "../types.ts";
import { tokens } from "../../design-tokens.ts";

interface StockVideoPrimitiveProps {
  props: StockVideoProps;
  style?: React.CSSProperties;
}

export const StockVideoPrimitive: React.FC<StockVideoPrimitiveProps> = ({ props, style }) => {
  const { alt, caption, fit = "cover", overlayTint } = props;

  // Resolve local public or absolute src (supports both src and assetId gracefully)
  const rawSrc = props.src || props.assetId || "";
  const videoSrc = !rawSrc
    ? ""
    : rawSrc.startsWith("http") || rawSrc.startsWith("data:")
    ? rawSrc
    : staticFile(rawSrc);

  return (
    <div
      style={{
        position: "relative",
        width: "100%",
        height: "100%",
        overflow: "hidden",
        backgroundColor: "#000000",
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
            "linear-gradient(180deg, rgba(0, 0, 0, 0.2) 0%, rgba(0, 0, 0, 0.5) 100%)",
          pointerEvents: "none",
          zIndex: 2,
        }}
      />

      {/* Main Stock Video footage rendered via OffthreadVideo for rock-solid deterministic frame extraction */}
      {videoSrc ? (
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
      ) : (
        <div
          style={{
            width: "100%",
            height: caption ? "86%" : "100%",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            color: tokens.text.muted,
            fontSize: 16,
            fontFamily: tokens.font.family,
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
            backgroundColor: "rgba(10, 10, 15, 0.85)",
            backdropFilter: "blur(8px)",
            borderTop: "1px solid rgba(255, 255, 255, 0.08)",
            padding: "0 24px",
            display: "flex",
            alignItems: "center",
            fontFamily: tokens.font.family,
            fontSize: 14,
            fontWeight: 500,
            color: tokens.text.secondary,
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
