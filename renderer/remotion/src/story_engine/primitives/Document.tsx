import React from "react";
import type { DocumentProps, VisualStateKind, StampProps } from "../types.ts";
import { handDrawn, handDrawnAccent } from "../hand-drawn-theme.ts";

export interface DocumentComponentProps {
  props: DocumentProps;
  visualState?: VisualStateKind;
  badge?: string;
  stamp?: StampProps;
  customAccent?: string;
  width?: number;
  height?: number;
  layout?: string;
  style?: React.CSSProperties;
}

export const DocumentPrimitive: React.FC<DocumentComponentProps> = ({
  props,
  visualState = "normal",
  badge,
  stamp,
  customAccent,
  width,
  height,
  layout,
  style,
}) => {
  const isCompact = (width ?? 480) <= 380 || (height ?? 320) <= 240;
  let accentColor: string = handDrawnAccent(visualState, customAccent || props.accentColor);
  let borderColor: string = handDrawn.colors.ink;
  let glowStyle: string = handDrawn.shadow.paper;
  let filterStyle: string | undefined = undefined;

  if (visualState === "danger") {
    accentColor = handDrawn.colors.red;
    borderColor = handDrawn.colors.red;
    glowStyle = `4px 5px 0 ${handDrawn.colors.coralSoft}, ${handDrawn.shadow.paper}`;
  } else if (visualState === "warning") {
    accentColor = handDrawn.colors.amber;
    borderColor = handDrawn.colors.amber;
    glowStyle = `4px 5px 0 ${handDrawn.colors.amberSoft}, ${handDrawn.shadow.paper}`;
  } else if (visualState === "success") {
    accentColor = handDrawn.colors.green;
    borderColor = handDrawn.colors.green;
    glowStyle = `4px 5px 0 #CBE6D1, ${handDrawn.shadow.paper}`;
  } else if (visualState === "dimmed") {
    filterStyle = "grayscale(75%) contrast(0.85)";
  }

  return (
    <div
      style={{
        position: "relative",
        display: "flex",
        flexDirection: "column",
        backgroundColor: handDrawn.colors.paperAlt,
        border: `2px solid ${borderColor}`,
        borderRadius: handDrawn.radius.card,
        padding: "24px 28px",
        boxShadow: glowStyle,
        fontFamily: handDrawn.font.body,
        boxSizing: "border-box",
        overflow: "hidden",
        filter: filterStyle,
        transition: "border 0.3s ease, box-shadow 0.3s ease",
        ...style,
      }}
    >
      {/* Background Security Watermark */}
      <div
        style={{
          position: "absolute",
          top: "40%",
          left: "20%",
          fontSize: 68,
          fontWeight: 900,
          color: `${handDrawn.colors.ink}10`,
          letterSpacing: "0.2em",
          transform: "rotate(-25deg)",
          pointerEvents: "none",
          userSelect: "none",
        }}
      >
        {props.watermark || "OFFICIAL"}
      </div>

      {/* Dynamic Rubber Stamp Overlay */}
      {stamp && (
        <div
          style={{
            position: "absolute",
            top: "35%",
            right: "15%",
            transform: `rotate(${stamp.angle ?? -14}deg)`,
            border: `3px solid ${stamp.color || "#10B981"}`,
            borderRadius: 8,
            padding: "8px 18px",
            color: stamp.color || handDrawn.colors.green,
            fontFamily: handDrawn.font.label,
            fontSize: 22,
            fontWeight: 900,
            letterSpacing: "0.2em",
            textTransform: "uppercase",
            backgroundColor: handDrawn.colors.paperAlt,
            boxShadow: handDrawn.shadow.paper,
            zIndex: 15,
            pointerEvents: "none",
          }}
        >
          {stamp.text}
        </div>
      )}

      {/* Header with Serial & Badges */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          borderBottom: `2px solid ${handDrawn.colors.ink}33`,
          paddingBottom: 12,
          marginBottom: 16,
        }}
      >
        <div>
          <div
            style={{
              fontSize: 18,
              fontWeight: 800,
              color: handDrawn.colors.ink,
              letterSpacing: "0.08em",
              textTransform: "uppercase",
            }}
          >
            {props.title}
          </div>
          {props.serialNo && (
            <div
              style={{
                fontSize: 12,
                color: handDrawn.colors.inkMuted,
                fontFamily: "monospace",
                marginTop: 2,
              }}
            >
              {props.serialNo}
            </div>
          )}
        </div>

        <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
          {badge && (
            <div
              style={{
                padding: "4px 10px",
                borderRadius: 4,
                backgroundColor: `${accentColor}26`,
                border: `1px solid ${accentColor}`,
                color: accentColor,
                fontSize: 11,
                fontWeight: 700,
                letterSpacing: "0.06em",
                textTransform: "uppercase",
              }}
            >
              {badge}
            </div>
          )}
          {props.statusBadge && (
            <div
              style={{
                padding: "4px 10px",
                borderRadius: 4,
                border: `1px solid ${accentColor}`,
                backgroundColor: `${accentColor}1A`,
                color: accentColor,
                fontSize: 11,
                fontWeight: 700,
                letterSpacing: "0.06em",
                textTransform: "uppercase",
              }}
            >
              {props.statusBadge}
            </div>
          )}
        </div>
      </div>



      {/* Document Line Items */}
      {props.items && props.items.length > 0 && (
        <div
          style={{
            marginTop: 14,
            paddingTop: 12,
            borderTop: `1px dashed ${handDrawn.colors.ink}55`,
            display: "flex",
            flexDirection: "column",
            gap: 6,
            zIndex: 2,
          }}
        >
          {props.items.map((item, idx) => (
            <div
              key={idx}
              style={{
                display: "flex",
                justifyContent: "space-between",
                fontSize: 14,
                color: handDrawn.colors.inkMuted,
              }}
            >
              <span>{item.label}</span>
              <span style={{ fontWeight: 600, color: item.color || handDrawn.colors.ink }}>
                {item.value}
              </span>
            </div>
          ))}
        </div>
      )}

      {/* Footer / Issuer */}
      {props.issuer && (
        <div
          style={{
            marginTop: 12,
            display: "flex",
            justifyContent: "space-between",
            fontSize: 12,
            color: handDrawn.colors.inkMuted,
            borderTop: `1px solid ${handDrawn.colors.ink}22`,
            paddingTop: 8,
          }}
        >
          <span>{props.issuer}</span>
          <span>{props.date || "Verified Record"}</span>
        </div>
      )}
    </div>
  );
};
