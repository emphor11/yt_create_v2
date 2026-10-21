import React from "react";
import { staticFile } from "remotion";
import type { ImageProps } from "../types.ts";
import { tokens } from "../../design-tokens.ts";

interface ImagePrimitiveProps {
  props: ImageProps;
  style?: React.CSSProperties;
}

export const ImagePrimitive: React.FC<ImagePrimitiveProps> = ({ props, style }) => {
  const { alt, caption, badge, borderColor, borderRadius = 16, fit = "cover" } = props;

  // Resolve local public or absolute src (supports both src and assetId gracefully)
  const rawSrc = props.src || props.assetId || "";
  const imageSrc = !rawSrc
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
        borderRadius,
        overflow: "hidden",
        backgroundColor: tokens.bg.surface,
        border: `1px solid ${borderColor || tokens.bg.border}`,
        boxShadow: "0 20px 40px -15px rgba(0, 0, 0, 0.5)",
        display: "flex",
        flexDirection: "column",
        ...style,
      }}
    >
      {/* Badge Overlay */}
      {badge && (
        <div
          style={{
            position: "absolute",
            top: 12,
            right: 12,
            backgroundColor: "rgba(15, 23, 42, 0.85)",
            backdropFilter: "blur(6px)",
            border: "1px solid rgba(255, 255, 255, 0.2)",
            borderRadius: 6,
            padding: "4px 8px",
            fontFamily: tokens.font.family,
            fontSize: 11,
            fontWeight: 600,
            color: tokens.text.primary,
            letterSpacing: "0.05em",
            textTransform: "uppercase",
            zIndex: 5,
          }}
        >
          {badge}
        </div>
      )}

      {/* Dark Overlay / Tint Treatment */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          right: 0,
          bottom: caption ? "18%" : 0,
          background: props.overlayTint || "linear-gradient(180deg, rgba(15, 23, 42, 0.15) 0%, rgba(15, 23, 42, 0.6) 100%)",
          pointerEvents: "none",
          zIndex: 2,
        }}
      />

      {/* Main Image */}
      {imageSrc ? (
        <img
          src={imageSrc}
          alt={alt ?? "story media"}
          style={{
            width: "100%",
            height: caption ? "82%" : "100%",
            objectFit: fit,
            display: "block",
          }}
        />
      ) : (
        <div
          style={{
            width: "100%",
            height: caption ? "82%" : "100%",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            color: tokens.text.muted,
            fontSize: 14,
            fontFamily: tokens.font.family,
          }}
        >
          {props.assetId || "Media Asset"}
        </div>
      )}

      {/* Caption Bar */}
      {caption && (
        <div
          style={{
            height: "18%",
            backgroundColor: "rgba(15, 23, 42, 0.9)",
            borderTop: "1px solid rgba(255, 255, 255, 0.08)",
            padding: "0 14px",
            display: "flex",
            alignItems: "center",
            fontFamily: tokens.font.family,
            fontSize: 12,
            color: tokens.text.secondary,
            whiteSpace: "nowrap",
            overflow: "hidden",
            textOverflow: "ellipsis",
          }}
        >
          {caption}
        </div>
      )}
    </div>
  );
};
