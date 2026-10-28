import React from "react";
import { useCurrentFrame, spring } from "remotion";
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
  const frame = useCurrentFrame();
  const boxW = width ?? 680;
  const boxH = height ?? 380;

  const activeVisualState = visualState || props.visualState || "normal";
  let accentColor: string = handDrawnAccent(activeVisualState, customAccent || props.accentColor);
  let borderColor: string = handDrawn.colors.ink;
  let glowStyle: string = handDrawn.shadow.paper;
  let filterStyle: string | undefined = undefined;

  if (activeVisualState === "danger") {
    accentColor = handDrawn.colors.red;
    borderColor = handDrawn.colors.red;
    glowStyle = `4px 5px 0 ${handDrawn.colors.coralSoft}, ${handDrawn.shadow.paper}`;
  } else if (activeVisualState === "warning") {
    accentColor = handDrawn.colors.amber;
    borderColor = handDrawn.colors.amber;
    glowStyle = `4px 5px 0 ${handDrawn.colors.amberSoft}, ${handDrawn.shadow.paper}`;
  } else if (activeVisualState === "success") {
    accentColor = handDrawn.colors.green;
    borderColor = handDrawn.colors.green;
    glowStyle = `4px 5px 0 #CBE6D1, ${handDrawn.shadow.paper}`;
  } else if (activeVisualState === "dimmed") {
    filterStyle = "grayscale(75%) contrast(0.85)";
  }

  // Animated highlighter swipe progress
  const highlightProgress = spring({
    frame: Math.max(0, frame - 8),
    fps: 30,
    config: {
      damping: 15,
      stiffness: 90,
    },
  });

  // Animated rubber stamp impact
  const stampProgress = spring({
    frame: Math.max(0, frame - 18),
    fps: 30,
    config: {
      damping: 10,
      mass: 1.4,
      stiffness: 120,
    },
  });

  // Split docBody around highlightPhrase if present
  const docBody = props.docBody || "";
  const highlightPhrase = props.highlightPhrase?.trim() || "";

  let bodyPrefix = docBody;
  let bodyHighlighted = "";
  let bodySuffix = "";

  if (highlightPhrase && docBody.toLowerCase().includes(highlightPhrase.toLowerCase())) {
    const idx = docBody.toLowerCase().indexOf(highlightPhrase.toLowerCase());
    bodyPrefix = docBody.slice(0, idx);
    bodyHighlighted = docBody.slice(idx, idx + highlightPhrase.length);
    bodySuffix = docBody.slice(idx + highlightPhrase.length);
  }

  const stampText = props.stampText || stamp?.text;
  const isDangerStamp = activeVisualState === "danger" || activeVisualState === "warning";
  const stampColor = stamp?.color || (isDangerStamp ? handDrawn.colors.red : handDrawn.colors.green);

  return (
    <div
      style={{
        position: "relative",
        width: boxW,
        height: boxH,
        display: "flex",
        flexDirection: "column",
        backgroundColor: handDrawn.colors.paperAlt,
        border: `2px solid ${borderColor}`,
        borderRadius: handDrawn.radius.card,
        padding: "22px 26px",
        boxShadow: glowStyle,
        fontFamily: handDrawn.font.body,
        boxSizing: "border-box",
        overflow: "hidden",
        filter: filterStyle,
        ...style,
      }}
    >
      {/* Background Archival Security Watermark */}
      <div
        style={{
          position: "absolute",
          top: "42%",
          left: "50%",
          transform: "translate(-50%, -50%) rotate(-22deg)",
          fontSize: Math.min(boxW * 0.11, 72),
          fontWeight: 900,
          fontFamily: handDrawn.font.label,
          color: `${handDrawn.colors.ink}0E`,
          letterSpacing: "0.22em",
          pointerEvents: "none",
          userSelect: "none",
          whiteSpace: "nowrap",
          zIndex: 1,
        }}
      >
        {props.watermark || "OFFICIAL FILING"}
      </div>

      {/* Official Header: Seal & Title */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "flex-start",
          borderBottom: `2px solid ${handDrawn.colors.ink}26`,
          paddingBottom: 10,
          marginBottom: 14,
          zIndex: 3,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          {/* Institutional Emblem / Official Seal Icon */}
          <div
            style={{
              width: 38,
              height: 38,
              borderRadius: "50%",
              border: `2px solid ${handDrawn.colors.ink}`,
              backgroundColor: `${handDrawn.colors.paper}`,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              flexShrink: 0,
            }}
          >
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="12" r="9" stroke={handDrawn.colors.ink} strokeWidth="1.5" />
              <path
                d="M12 5V19M5 12H19M7 8L17 16M17 8L7 16"
                stroke={handDrawn.colors.inkMuted}
                strokeWidth="1.2"
                strokeLinecap="round"
              />
            </svg>
          </div>

          <div>
            <div
              style={{
                fontSize: 16,
                fontWeight: 800,
                color: handDrawn.colors.ink,
                letterSpacing: "0.06em",
                textTransform: "uppercase",
                lineHeight: 1.2,
              }}
            >
              {props.title || "REGULATORY PROOF DOCUMENT"}
            </div>
            {(props.docReference || props.serialNo) && (
              <div
                style={{
                  fontSize: 11,
                  color: handDrawn.colors.inkMuted,
                  fontFamily: "monospace",
                  marginTop: 3,
                  letterSpacing: "0.08em",
                }}
              >
                {props.docReference || props.serialNo}
              </div>
            )}
          </div>
        </div>

        {/* Status Badges */}
        <div style={{ display: "flex", gap: 6, alignItems: "center" }}>
          {(badge || props.statusBadge) && (
            <div
              style={{
                padding: "3px 9px",
                borderRadius: 4,
                backgroundColor: `${accentColor}1F`,
                border: `1.5px solid ${accentColor}`,
                color: accentColor,
                fontSize: 10,
                fontWeight: 800,
                letterSpacing: "0.08em",
                textTransform: "uppercase",
                fontFamily: handDrawn.font.label,
              }}
            >
              {badge || props.statusBadge}
            </div>
          )}
        </div>
      </div>

      {/* Document Excerpt Body with Animated Yellow Highlighter Swipe */}
      {docBody ? (
        <div
          style={{
            flex: 1,
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
            padding: "8px 4px",
            zIndex: 3,
            position: "relative",
          }}
        >
          <div
            style={{
              fontFamily: '"Newsreader", "Georgia", "Times New Roman", serif',
              fontSize: boxW > 650 ? 20 : 17,
              lineHeight: 1.55,
              color: handDrawn.colors.ink,
              textAlign: "left",
            }}
          >
            {bodyHighlighted ? (
              <>
                <span>{bodyPrefix}</span>
                <span
                  style={{
                    position: "relative",
                    display: "inline",
                    fontWeight: 700,
                    color: handDrawn.colors.ink,
                    padding: "2px 4px",
                    margin: "0 2px",
                  }}
                >
                  {/* Yellow Highlighter Stroke Effect */}
                  <span
                    style={{
                      position: "absolute",
                      left: 0,
                      top: 1,
                      bottom: 0,
                      width: `${Math.min(100, Math.max(0, highlightProgress * 100))}%`,
                      backgroundColor: "rgba(250, 204, 21, 0.45)",
                      borderRadius: 4,
                      zIndex: -1,
                      transform: "rotate(-0.4deg)",
                      boxShadow: "0 0 8px rgba(250, 204, 21, 0.35)",
                      borderBottom: "2px solid rgba(234, 179, 8, 0.6)",
                    }}
                  />
                  {bodyHighlighted}
                </span>
                <span>{bodySuffix}</span>
              </>
            ) : (
              <span>{docBody}</span>
            )}
          </div>
        </div>
      ) : props.items && props.items.length > 0 ? (
        /* Fallback Document Line Items */
        <div
          style={{
            flex: 1,
            display: "flex",
            flexDirection: "column",
            gap: 8,
            justifyContent: "center",
            zIndex: 3,
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
      ) : null}

      {/* Dynamic Rubber Stamp Overlay (Animated Slam) */}
      {stampText && (
        <div
          style={{
            position: "absolute",
            bottom: "18%",
            right: "12%",
            transform: `scale(${Math.max(0.1, stampProgress)}) rotate(${stamp?.angle ?? -12}deg)`,
            opacity: Math.min(1, stampProgress * 1.5),
            border: `3.5px double ${stampColor}`,
            borderRadius: 6,
            padding: "6px 16px",
            color: stampColor,
            fontFamily: handDrawn.font.label,
            fontSize: 20,
            fontWeight: 900,
            letterSpacing: "0.22em",
            textTransform: "uppercase",
            backgroundColor: `${handDrawn.colors.paperAlt}E6`,
            boxShadow: `3px 3px 0 ${stampColor}33`,
            zIndex: 10,
            pointerEvents: "none",
          }}
        >
          {stampText}
        </div>
      )}

      {/* Official Archival Footer */}
      <div
        style={{
          marginTop: "auto",
          paddingTop: 8,
          borderTop: `1px solid ${handDrawn.colors.ink}22`,
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          fontSize: 11,
          color: handDrawn.colors.inkMuted,
          fontFamily: "monospace",
          zIndex: 3,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
          {/* Decorative mini barcode */}
          <div style={{ display: "flex", gap: 1.5, height: 12, alignItems: "center" }}>
            {[3, 1, 2, 4, 1, 3, 2, 1, 4, 2].map((w, i) => (
              <div
                key={i}
                style={{
                  width: w,
                  height: 12,
                  backgroundColor: `${handDrawn.colors.ink}66`,
                }}
              />
            ))}
          </div>
          <span>{props.issuer || "ARCHIVAL EVIDENCE REGISTRY"}</span>
        </div>
        <span>{props.date || "OFFICIAL RECORD // AUDITED"}</span>
      </div>
    </div>
  );
};
