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
  const { alt, caption, badge, borderColor, borderRadius = 8, fit = "cover" } = props;

  const isDoc = Boolean(
    (caption || "").toLowerCase().includes("document") ||
    (caption || "").toLowerCase().includes("contract") ||
    (caption || "").toLowerCase().includes("statement") ||
    (caption || "").toLowerCase().includes("agreement") ||
    (caption || "").toLowerCase().includes("letter") ||
    (caption || "").toLowerCase().includes("report") ||
    (caption || "").toLowerCase().includes("form") ||
    (caption || "").toLowerCase().includes("circular") ||
    (caption || "").toLowerCase().includes("policy") ||
    (alt || "").toLowerCase().includes("document") ||
    (alt || "").toLowerCase().includes("contract") ||
    (alt || "").toLowerCase().includes("agreement")
  );

  const isCompact = (height ?? 240) <= 220 || (width ?? 420) <= 400;
  const captionHeightPx = caption ? (isCompact ? 28 : 36) : 0;

  // Resolve local public or absolute src (supports both src and assetId gracefully)
  const rawSrc = props.src || props.assetId || "";
  const imageSrc = !rawSrc
    ? ""
    : rawSrc.startsWith("http") || rawSrc.startsWith("data:")
    ? rawSrc
    : staticFile(rawSrc);

  // Document Page Styling (Johnny Harris / Vox archival sheet on desk)
  if (isDoc) {
    return (
      <div
        style={{
          position: "relative",
          width: "100%",
          height: "100%",
          borderRadius: 4, // Crisp real paper corners
          overflow: "hidden",
          backgroundColor: "#FCFBF7", // Real A4 document paper backing
          border: `1px solid ${borderColor || "rgba(40, 45, 42, 0.40)"}`,
          boxShadow: "0 22px 50px -12px rgba(0, 0, 0, 0.30), 0 6px 18px -4px rgba(0, 0, 0, 0.15), 0 0 0 1px rgba(0, 0, 0, 0.05)",
          display: "flex",
          flexDirection: "column",
          transform: "rotate(-1.0deg)", // Johnny Harris physical desk tilt
          transformOrigin: "center center",
          ...style,
        }}
      >
        {/* Archival Document Header Badge */}
        <div
          style={{
            position: "absolute",
            top: isCompact ? 8 : 12,
            right: isCompact ? 8 : 12,
            backgroundColor: "rgba(252, 251, 247, 0.96)",
            border: `1px solid rgba(40, 45, 42, 0.65)`,
            borderRadius: 3,
            padding: isCompact ? "2px 6px" : "3px 8px",
            fontFamily: handDrawn.font.label,
            fontSize: isCompact ? 9 : 10,
            fontWeight: 800,
            color: handDrawn.colors.ink,
            letterSpacing: "0.10em",
            textTransform: "uppercase",
            zIndex: 5,
            boxShadow: "0 2px 4px rgba(0, 0, 0, 0.12)",
          }}
        >
          {badge || "RECORD // VERIFIED"}
        </div>

        {/* Paper Sheen Overlay */}
        <div
          style={{
            position: "absolute",
            top: 0,
            left: 0,
            right: 0,
            bottom: captionHeightPx,
            background: "linear-gradient(135deg, rgba(255, 255, 255, 0.45) 0%, rgba(40, 45, 42, 0.04) 100%)",
            pointerEvents: "none",
            zIndex: 2,
          }}
        />

        {/* Document Body */}
        {imageSrc ? (
          <img
            src={imageSrc}
            alt={alt ?? "documentary legal record"}
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
            {props.assetId || "Legal Record"}
          </div>
        )}

        {/* Anchored Document Caption Bar */}
        {caption && (
          <div
            style={{
              height: captionHeightPx,
              backgroundColor: "#FCFBF7",
              borderTop: "1px solid rgba(40, 45, 42, 0.25)",
              padding: isCompact ? "0 10px" : "0 14px",
              display: "flex",
              alignItems: "center",
              fontFamily: handDrawn.font.body,
              fontSize: isCompact ? 11 : 13,
              fontWeight: 600,
              color: handDrawn.colors.ink,
              letterSpacing: "0.02em",
              whiteSpace: "nowrap",
              overflow: "hidden",
              textOverflow: "ellipsis",
            }}
          >
            <span style={{ opacity: 0.6, fontSize: isCompact ? 9 : 10, marginRight: 6, fontWeight: 800, letterSpacing: "0.08em" }}>
              DOCUMENT //
            </span>
            {caption}
          </div>
        )}
      </div>
    );
  }

  // Classic Archival Photographic Print (Magnates / Casual Finances museum mount)
  return (
    <div
      style={{
        position: "relative",
        width: "100%",
        height: "100%",
        borderRadius: 8,
        overflow: "hidden",
        backgroundColor: "#F4F1EA", // Archival photo print backing
        border: `1px solid ${borderColor || "rgba(32, 37, 34, 0.40)"}`,
        boxShadow: "0 20px 48px -10px rgba(0, 0, 0, 0.32), 0 6px 16px -3px rgba(0, 0, 0, 0.12)",
        display: "flex",
        flexDirection: "column",
        padding: "8px 8px 0px 8px", // Archival photo mount border
        boxSizing: "border-box",
        ...style,
      }}
    >
      {/* Badge Overlay (Archival Plate Label) */}
      {badge && (
        <div
          style={{
            position: "absolute",
            top: isCompact ? 12 : 16,
            right: isCompact ? 12 : 16,
            backgroundColor: "rgba(244, 241, 234, 0.94)",
            border: `1px solid rgba(32, 37, 34, 0.65)`,
            borderRadius: 4,
            padding: isCompact ? "2px 6px" : "3px 8px",
            fontFamily: handDrawn.font.label,
            fontSize: isCompact ? 9 : 10,
            fontWeight: 700,
            color: handDrawn.colors.ink,
            letterSpacing: "0.08em",
            textTransform: "uppercase",
            zIndex: 5,
            boxShadow: "0 2px 4px rgba(0, 0, 0, 0.10)",
          }}
        >
          {badge}
        </div>
      )}

      {/* Subtle Vignette Overlay for Photographic Immersion */}
      <div
        style={{
          position: "absolute",
          top: 8,
          left: 8,
          right: 8,
          bottom: captionHeightPx + 4,
          background: props.overlayTint || "linear-gradient(180deg, rgba(32, 37, 34, 0.02) 0%, rgba(32, 37, 34, 0.28) 100%)",
          pointerEvents: "none",
          borderRadius: 4,
          zIndex: 2,
        }}
      />

      {/* Main Photographic Image inside mount */}
      <div
        style={{
          position: "relative",
          width: "100%",
          height: caption ? `calc(100% - ${captionHeightPx}px)` : "100%",
          borderRadius: 4,
          overflow: "hidden",
        }}
      >
        {imageSrc ? (
          <img
            src={imageSrc}
            alt={alt ?? "documentary media"}
            style={{
              width: "100%",
              height: "100%",
              objectFit: fit,
              display: "block",
            }}
          />
        ) : (
          <div
            style={{
              width: "100%",
              height: "100%",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: handDrawn.colors.inkMuted,
              fontSize: 14,
              fontFamily: handDrawn.font.body,
            }}
          >
            {props.assetId || "Documentary Media"}
          </div>
        )}
      </div>

      {/* Anchored Archival Caption Bar */}
      {caption && (
        <div
          style={{
            height: captionHeightPx,
            backgroundColor: "#F4F1EA",
            padding: isCompact ? "0 8px" : "0 10px",
            display: "flex",
            alignItems: "center",
            fontFamily: handDrawn.font.body,
            fontSize: isCompact ? 11 : 12,
            fontWeight: 600,
            color: handDrawn.colors.ink,
            letterSpacing: "0.02em",
            whiteSpace: "nowrap",
            overflow: "hidden",
            textOverflow: "ellipsis",
          }}
        >
          <span style={{ opacity: 0.6, fontSize: isCompact ? 9 : 10, marginRight: 6, fontWeight: 700, letterSpacing: "0.06em" }}>
            EVIDENCE //
          </span>
          {caption}
        </div>
      )}
    </div>
  );
};
