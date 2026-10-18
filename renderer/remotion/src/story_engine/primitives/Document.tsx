import React from "react";
import type { DocumentProps, VisualStateKind, StampProps } from "../types.ts";
import { tokens } from "../../design-tokens.ts";

interface DocumentComponentProps {
  props: DocumentProps;
  visualState?: VisualStateKind;
  badge?: string;
  stamp?: StampProps;
  customAccent?: string;
  style?: React.CSSProperties;
}

export const DocumentPrimitive: React.FC<DocumentComponentProps> = ({
  props,
  visualState = "normal",
  badge,
  stamp,
  customAccent,
  style,
}) => {
  let accentColor = customAccent || props.accentColor || tokens.accent.cyan;
  let borderColor = tokens.bg.border;
  let glowStyle = "0 25px 50px -12px rgba(0, 0, 0, 0.7)";
  let filterStyle: string | undefined = undefined;

  if (visualState === "danger") {
    accentColor = "#EF4444";
    borderColor = "#EF4444";
    glowStyle = "0 0 35px 5px rgba(239, 68, 68, 0.5), 0 25px 50px -12px rgba(0, 0, 0, 0.7)";
  } else if (visualState === "warning") {
    accentColor = "#F59E0B";
    borderColor = "#F59E0B";
    glowStyle = "0 0 28px 3px rgba(245, 158, 11, 0.4), 0 25px 50px -12px rgba(0, 0, 0, 0.7)";
  } else if (visualState === "success") {
    accentColor = "#10B981";
    borderColor = "#10B981";
    glowStyle = "0 0 30px 4px rgba(16, 185, 129, 0.45), 0 25px 50px -12px rgba(0, 0, 0, 0.7)";
  } else if (visualState === "dimmed") {
    filterStyle = "grayscale(75%) contrast(0.85)";
  }

  return (
    <div
      style={{
        position: "relative",
        display: "flex",
        flexDirection: "column",
        backgroundColor: "#0D111A",
        border: `1.5px solid ${borderColor}`,
        borderRadius: 12,
        padding: "24px 28px",
        boxShadow: glowStyle,
        fontFamily: tokens.font.family,
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
          color: "rgba(255, 255, 255, 0.03)",
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
            color: stamp.color || "#10B981",
            fontFamily: tokens.font.family,
            fontSize: 22,
            fontWeight: 900,
            letterSpacing: "0.2em",
            textTransform: "uppercase",
            backgroundColor: "rgba(0, 0, 0, 0.45)",
            boxShadow: `0 0 20px ${stamp.color || "#10B981"}55`,
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
          borderBottom: "1px solid rgba(255, 255, 255, 0.1)",
          paddingBottom: 12,
          marginBottom: 16,
        }}
      >
        <div>
          <div
            style={{
              fontSize: 18,
              fontWeight: 800,
              color: tokens.text.primary,
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
                color: tokens.text.muted,
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
            borderTop: "1px dashed rgba(255, 255, 255, 0.12)",
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
                color: tokens.text.secondary,
              }}
            >
              <span>{item.label}</span>
              <span style={{ fontWeight: 600, color: item.color || tokens.text.primary }}>
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
            color: tokens.text.muted,
            borderTop: "1px solid rgba(255, 255, 255, 0.06)",
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
