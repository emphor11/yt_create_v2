import React from "react";
import { useCurrentFrame, spring } from "remotion";
import type { CapitalFlowProps, VisualStateKind } from "../types.ts";
import { handDrawn, handDrawnAccent } from "../hand-drawn-theme.ts";

export interface CapitalFlowPrimitiveProps {
  props: CapitalFlowProps;
  visualState?: VisualStateKind;
  badge?: string;
  customAccent?: string;
  width?: number;
  height?: number;
  layout?: string;
  style?: React.CSSProperties;
}

export const CapitalFlowPrimitive: React.FC<CapitalFlowPrimitiveProps> = ({
  props,
  visualState,
  badge,
  customAccent,
  width,
  height,
  layout,
  style,
}) => {
  const frame = useCurrentFrame();
  const boxW = width ?? 860;
  const boxH = height ?? 380;

  const activeVisualState = visualState || props.visualState || "normal";
  const isDanger = activeVisualState === "danger";
  const isWarning = activeVisualState === "warning";

  let accentColor = customAccent || props.accentColor || (isDanger ? handDrawn.colors.red : isWarning ? handDrawn.colors.amber : "#2563EB");
  let glowStyle = isDanger
    ? `4px 5px 0 ${handDrawn.colors.coralSoft}, ${handDrawn.shadow.paper}`
    : handDrawn.shadow.paper;

  const direction = props.flowDirection || "left_to_right";
  const isReverse = direction === "right_to_left";

  // Staggered springs for node hubs and central flow pill
  const sourceSpring = spring({
    frame,
    fps: 30,
    config: { damping: 14, stiffness: 90 },
  });

  const targetSpring = spring({
    frame: Math.max(0, frame - 4),
    fps: 30,
    config: { damping: 14, stiffness: 90 },
  });

  const pillSpring = spring({
    frame: Math.max(0, frame - 8),
    fps: 30,
    config: { damping: 12, stiffness: 100 },
  });

  // Animated dash offset for flight vector
  const dashSpeed = 2.4;
  const dashOffset = isReverse ? frame * dashSpeed : -frame * dashSpeed;

  return (
    <div
      style={{
        position: "relative",
        width: boxW,
        height: boxH,
        backgroundColor: handDrawn.colors.paperAlt,
        borderRadius: handDrawn.radius.card,
        border: `2px solid ${isDanger ? handDrawn.colors.red : handDrawn.colors.ink}`,
        boxShadow: glowStyle,
        boxSizing: "border-box",
        padding: "20px 26px",
        display: "flex",
        flexDirection: "column",
        overflow: "hidden",
        fontFamily: handDrawn.font.body,
        ...style,
      }}
    >
      {/* Top Accent Strip */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          right: 0,
          height: 6,
          backgroundColor: isDanger ? handDrawn.colors.red : "#2563EB",
        }}
      />

      {/* Header */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          borderBottom: `2px solid ${handDrawn.colors.ink}22`,
          paddingBottom: 10,
          marginBottom: 16,
          zIndex: 3,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div
            style={{
              width: 26,
              height: 26,
              borderRadius: 6,
              backgroundColor: `${accentColor}1A`,
              border: `1.5px solid ${accentColor}`,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none">
              <path
                d="M5 12H19M19 12L13 6M19 12L13 18"
                stroke={accentColor}
                strokeWidth="2.5"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </div>
          <span
            style={{
              fontSize: 15,
              fontWeight: 800,
              letterSpacing: "0.08em",
              color: handDrawn.colors.ink,
              textTransform: "uppercase",
              fontFamily: handDrawn.font.label,
            }}
          >
            {props.title || "CAPITAL FLOW ROUTE"}
          </span>
        </div>

        {(badge || props.badge) && (
          <span
            style={{
              fontSize: 11,
              fontWeight: 800,
              letterSpacing: "0.08em",
              textTransform: "uppercase",
              padding: "3px 9px",
              borderRadius: 4,
              border: `1.5px solid ${accentColor}`,
              backgroundColor: `${accentColor}1A`,
              color: accentColor,
              fontFamily: handDrawn.font.label,
            }}
          >
            {badge || props.badge}
          </span>
        )}
      </div>

      {/* Flow Architecture Canvas */}
      <div
        style={{
          flex: 1,
          position: "relative",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          zIndex: 2,
        }}
      >
        {/* Origin Node Hub */}
        <div
          style={{
            width: boxW > 700 ? 220 : 180,
            padding: "16px 18px",
            backgroundColor: handDrawn.colors.paper,
            border: `2px solid ${isDanger ? handDrawn.colors.red : handDrawn.colors.ink}`,
            borderRadius: 12,
            boxShadow: handDrawn.shadow.paper,
            opacity: sourceSpring,
            transform: `scale(${0.92 + sourceSpring * 0.08})`,
            zIndex: 4,
            display: "flex",
            flexDirection: "column",
            gap: 6,
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <span
              style={{
                fontSize: 10,
                fontWeight: 800,
                color: isDanger ? handDrawn.colors.red : handDrawn.colors.inkMuted,
                fontFamily: "monospace",
                letterSpacing: "0.08em",
              }}
            >
              {isReverse ? "DESTINATION" : "ORIGIN // OUTFLOW"}
            </span>
            <div
              style={{
                width: 10,
                height: 10,
                borderRadius: "50%",
                backgroundColor: isDanger ? handDrawn.colors.red : "#3B82F6",
              }}
            />
          </div>

          <div
            style={{
              fontSize: 15,
              fontWeight: 800,
              color: handDrawn.colors.ink,
              lineHeight: 1.25,
            }}
          >
            {props.sourceLabel}
          </div>

          {props.sourceSublabel && (
            <div
              style={{
                fontSize: 11,
                color: handDrawn.colors.inkMuted,
                lineHeight: 1.3,
              }}
            >
              {props.sourceSublabel}
            </div>
          )}
        </div>

        {/* Flight Route Corridor: Animated Vector Line */}
        <div
          style={{
            position: "absolute",
            left: boxW > 700 ? 210 : 170,
            right: boxW > 700 ? 210 : 170,
            top: "50%",
            transform: "translateY(-50%)",
            height: 48,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 2,
          }}
        >
          {/* Animated SVG Flight Path */}
          <svg
            style={{
              position: "absolute",
              width: "100%",
              height: 24,
              overflow: "visible",
            }}
          >
            <line
              x1="0"
              y1="12"
              x2="100%"
              y2="12"
              stroke={isDanger ? handDrawn.colors.red : "#2563EB"}
              strokeWidth="3.5"
              strokeDasharray="10 8"
              strokeDashoffset={dashOffset}
              strokeLinecap="round"
            />
          </svg>

          {/* Central Hero Flow Pill */}
          <div
            style={{
              position: "relative",
              zIndex: 5,
              backgroundColor: handDrawn.colors.paperAlt,
              border: `2px solid ${isDanger ? handDrawn.colors.red : "#2563EB"}`,
              borderRadius: 30,
              padding: "8px 22px",
              boxShadow: isDanger
                ? `0 4px 14px rgba(239, 68, 68, 0.25)`
                : `0 4px 14px rgba(37, 99, 235, 0.20)`,
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              gap: 2,
              opacity: pillSpring,
              transform: `scale(${0.9 + pillSpring * 0.1})`,
            }}
          >
            <div
              style={{
                fontSize: 10,
                fontWeight: 800,
                letterSpacing: "0.1em",
                textTransform: "uppercase",
                color: isDanger ? handDrawn.colors.red : "#2563EB",
                fontFamily: handDrawn.font.label,
              }}
            >
              {props.flowLabel || "CAPITAL IN FLIGHT"}
            </div>
            <div
              style={{
                fontSize: boxW > 700 ? 20 : 17,
                fontWeight: 900,
                fontFamily: "monospace",
                color: handDrawn.colors.ink,
                letterSpacing: "0.02em",
                whiteSpace: "nowrap",
              }}
            >
              {props.flowDisplayValue}
            </div>
          </div>
        </div>

        {/* Destination Node Hub */}
        <div
          style={{
            width: boxW > 700 ? 220 : 180,
            padding: "16px 18px",
            backgroundColor: handDrawn.colors.paper,
            border: `2px solid ${handDrawn.colors.ink}`,
            borderRadius: 12,
            boxShadow: handDrawn.shadow.paper,
            opacity: targetSpring,
            transform: `scale(${0.92 + targetSpring * 0.08})`,
            zIndex: 4,
            display: "flex",
            flexDirection: "column",
            gap: 6,
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <span
              style={{
                fontSize: 10,
                fontWeight: 800,
                color: handDrawn.colors.inkMuted,
                fontFamily: "monospace",
                letterSpacing: "0.08em",
              }}
            >
              {isReverse ? "ORIGIN" : "DESTINATION // INFLOW"}
            </span>
            <div
              style={{
                width: 10,
                height: 10,
                borderRadius: "50%",
                backgroundColor: "#10B981",
              }}
            />
          </div>

          <div
            style={{
              fontSize: 15,
              fontWeight: 800,
              color: handDrawn.colors.ink,
              lineHeight: 1.25,
            }}
          >
            {props.targetLabel}
          </div>

          {props.targetSublabel && (
            <div
              style={{
                fontSize: 11,
                color: handDrawn.colors.inkMuted,
                lineHeight: 1.3,
              }}
            >
              {props.targetSublabel}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
