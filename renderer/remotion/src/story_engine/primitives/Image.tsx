import React from "react";
import { staticFile } from "remotion";
import type { ImageProps } from "../types.ts";
import { handDrawn } from "../hand-drawn-theme.ts";

export interface ImagePrimitiveProps {
  props: ImageProps;
  width?: number;
  height?: number;
  layout?: string;
  style?: React.CSSProperties;
}

export const ImagePrimitive: React.FC<ImagePrimitiveProps> = ({
  props,
  width,
  height,
  layout,
  style,
}) => {
  const { alt, caption, badge, borderColor, borderRadius = 16, fit = "cover" } = props;

  const isCompact = (height ?? 240) <= 210 || (width ?? 420) <= 380;
  const captionHeightPx = caption ? (isCompact ? 26 : 32) : 0;

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
        backgroundColor: handDrawn.colors.paperAlt,
        border: `2px solid ${borderColor || handDrawn.colors.ink}`,
        boxShadow: handDrawn.shadow.paper,
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
            top: isCompact ? 8 : 12,
            right: isCompact ? 8 : 12,
            backgroundColor: handDrawn.colors.paperAlt,
            border: `1px solid ${handDrawn.colors.ink}`,
            borderRadius: handDrawn.radius.pill,
            padding: isCompact ? "2px 6px" : "4px 8px",
            fontFamily: handDrawn.font.label,
            fontSize: isCompact ? 10 : 11,
            fontWeight: 600,
            color: handDrawn.colors.ink,
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
          bottom: captionHeightPx,
          background: props.overlayTint || "linear-gradient(180deg, rgba(247, 241, 229, 0.02) 0%, rgba(32, 37, 34, 0.38) 100%)",
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
            height: caption ? `calc(100% - ${captionHeightPx}px)` : "100%",
            objectFit: fit,
            display: "block",
          }}
        />
      ) : (
        <div
          style={{
            width: "100%",
            height: caption ? `calc(100% - ${captionHeightPx}px)` : "100%",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            color: handDrawn.colors.inkMuted,
            fontSize: 14,
            fontFamily: handDrawn.font.body,
          }}
        >
          {props.assetId || "Media Asset"}
        </div>
      )}

      {/* Caption Bar */}
      {caption && (
        <div
          style={{
            height: captionHeightPx,
            backgroundColor: handDrawn.colors.paperAlt,
            borderTop: `1px solid ${handDrawn.colors.ink}33`,
            padding: isCompact ? "0 10px" : "0 14px",
            display: "flex",
            alignItems: "center",
            fontFamily: handDrawn.font.body,
            fontSize: isCompact ? 11 : 12,
            color: handDrawn.colors.inkMuted,
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
