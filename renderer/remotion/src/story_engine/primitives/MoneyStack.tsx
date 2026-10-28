import React from "react";
import { useCurrentFrame, spring } from "remotion";
import type { MoneyStackProps, VisualStateKind } from "../types.ts";
import { handDrawn } from "../hand-drawn-theme.ts";

export interface MoneyStackPrimitiveProps {
  props: MoneyStackProps;
  visualState?: VisualStateKind;
  badge?: string;
  customAccent?: string;
  width?: number;
  height?: number;
  layout?: string;
  style?: React.CSSProperties;
}

export const MoneyStackPrimitive: React.FC<MoneyStackPrimitiveProps> = ({
  props,
  visualState,
  badge,
  customAccent,
  width,
  height,
  style,
}) => {
  const frame = useCurrentFrame();
  const boxW = width ?? 680;
  const boxH = height ?? 380;

  const mode = props.stackMode || "single_tower";
  const activeVisualState = visualState || props.visualState || "normal";
  const isDanger = activeVisualState === "danger";

  // Staggered drop spring animation
  const animProgress = spring({
    frame,
    fps: 30,
    config: {
      damping: 12,
      mass: 1.2,
      stiffness: 85,
    },
  });

  const totalLayers = 10;
  const visibleLayers = Math.max(1, Math.min(totalLayers, Math.round(animProgress * totalLayers)));

  return (
    <div
      style={{
        position: "relative",
        width: boxW,
        height: boxH,
        backgroundColor: handDrawn.colors.paperAlt,
        borderRadius: handDrawn.radius.card,
        border: `2px solid ${isDanger ? handDrawn.colors.red : handDrawn.colors.ink}`,
        boxShadow: isDanger
          ? `4px 5px 0 ${handDrawn.colors.coralSoft}, ${handDrawn.shadow.paper}`
          : handDrawn.shadow.paper,
        boxSizing: "border-box",
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
          backgroundColor: isDanger ? handDrawn.colors.red : "#10B981",
        }}
      />

      {/* Header / Title */}
      <div
        style={{
          position: "absolute",
          top: 14,
          left: 20,
          right: 140,
          display: "flex",
          flexDirection: "column",
          gap: 2,
          zIndex: 4,
        }}
      >
        <span
          style={{
            fontSize: 13,
            fontWeight: 800,
            fontFamily: handDrawn.font.label,
            color: handDrawn.colors.inkMuted,
            letterSpacing: "0.08em",
            textTransform: "uppercase",
          }}
        >
          {props.title || "SCALE VISUALIZER // TANGIBLE CAPITAL"}
        </span>
        {props.unitLabel && (
          <span
            style={{
              fontSize: 11,
              fontWeight: 600,
              color: handDrawn.colors.inkMuted,
            }}
          >
            Unit: 1 Brick = {props.unitLabel}
          </span>
        )}
      </div>

      {/* Dynamic Status Badge */}
      {(badge || props.badge) && (
        <div
          style={{
            position: "absolute",
            top: 14,
            right: 18,
            padding: "3px 10px",
            borderRadius: handDrawn.radius.pill,
            backgroundColor: handDrawn.colors.paper,
            border: `1.5px solid ${isDanger ? handDrawn.colors.red : "#10B981"}`,
            color: isDanger ? handDrawn.colors.red : "#059669",
            fontFamily: handDrawn.font.label,
            fontSize: 11,
            fontWeight: 800,
            letterSpacing: "0.06em",
            textTransform: "uppercase",
            zIndex: 4,
          }}
        >
          {badge || props.badge}
        </div>
      )}

      {/* Ground Line */}
      <div
        style={{
          position: "absolute",
          bottom: 36,
          left: 30,
          right: 30,
          height: 2,
          backgroundColor: handDrawn.colors.ink,
          opacity: 0.25,
        }}
      />

      {mode === "single_tower" ? (
        /* MODE A: SINGLE TOWERING SKYSCRAPER STACK */
        <div
          style={{
            position: "absolute",
            inset: 0,
            top: 55,
            bottom: 38,
            display: "flex",
            alignItems: "flex-end",
            justifyContent: "space-between",
            padding: "0 36px",
            boxSizing: "border-box",
          }}
        >
          {/* Human Scale Reference Stick Figure */}
          {props.showHumanScale !== false && (
            <div
              style={{
                width: 90,
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                opacity: 0.85,
                marginBottom: 2,
              }}
            >
              {/* Stick Figure Silhouette */}
              <svg width="34" height="65" viewBox="0 0 34 65" fill="none">
                <circle cx="17" cy="10" r="7" stroke={handDrawn.colors.ink} strokeWidth="2.5" fill={handDrawn.colors.paper} />
                <line x1="17" y1="17" x2="17" y2="42" stroke={handDrawn.colors.ink} strokeWidth="2.5" />
                <line x1="7" y1="26" x2="27" y2="26" stroke={handDrawn.colors.ink} strokeWidth="2.5" />
                <line x1="17" y1="42" x2="9" y2="62" stroke={handDrawn.colors.ink} strokeWidth="2.5" />
                <line x1="17" y1="42" x2="25" y2="62" stroke={handDrawn.colors.ink} strokeWidth="2.5" />
              </svg>
              <span
                style={{
                  fontSize: 10,
                  fontWeight: 800,
                  fontFamily: handDrawn.font.label,
                  color: handDrawn.colors.inkMuted,
                  letterSpacing: "0.05em",
                  marginTop: 3,
                  whiteSpace: "nowrap",
                }}
              >
                HUMAN SCALE
              </span>
            </div>
          )}

          {/* Tower Stack of Cash Bricks */}
          <div
            style={{
              flex: 1,
              display: "flex",
              flexDirection: "column-reverse",
              alignItems: "center",
              gap: 3,
              marginBottom: 4,
              zIndex: 3,
            }}
          >
            {Array.from({ length: totalLayers }).map((_, idx) => {
              const isVisible = idx < visibleLayers;
              const brickW = Math.min(220, Math.max(150, boxW * 0.28));
              const brickH = Math.max(14, (boxH - 140) / totalLayers);

              if (!isVisible) {
                return <div key={idx} style={{ height: brickH, opacity: 0 }} />;
              }

              return (
                <div
                  key={idx}
                  style={{
                    width: brickW,
                    height: brickH,
                    backgroundColor: "#DCFCE7",
                    border: `1.8px solid ${handDrawn.colors.ink}`,
                    borderRadius: 4,
                    boxShadow: "2px 2px 0 rgba(0,0,0,0.08)",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    padding: "0 8px",
                    boxSizing: "border-box",
                  }}
                >
                  <span style={{ fontSize: 9, fontWeight: 700, color: "#166534", whiteSpace: "nowrap" }}>
                    ₹ {props.unitLabel || "1,000 Cr"}
                  </span>
                  <div style={{ width: 10, height: 6, borderRadius: 2, border: "1px solid #166534" }} />
                </div>
              );
            })}
          </div>

          {/* Big Total Value Metric Callout on Right */}
          <div
            style={{
              minWidth: 180,
              maxWidth: 220,
              display: "flex",
              flexDirection: "column",
              alignItems: "flex-start",
              padding: "8px 14px",
              backgroundColor: handDrawn.colors.paper,
              border: `2px solid ${handDrawn.colors.ink}`,
              borderRadius: 10,
              boxShadow: "0 4px 12px rgba(0,0,0,0.06)",
              marginBottom: 10,
              boxSizing: "border-box",
              zIndex: 4,
            }}
          >
            <span
              style={{
                fontSize: 10,
                fontWeight: 800,
                fontFamily: handDrawn.font.label,
                color: handDrawn.colors.inkMuted,
                textTransform: "uppercase",
                letterSpacing: "0.05em",
              }}
            >
              TOTAL MAGNITUDE
            </span>
            <span
              style={{
                fontSize: 21,
                fontWeight: 900,
                fontFamily: handDrawn.font.display,
                color: handDrawn.colors.ink,
                letterSpacing: "-0.03em",
                fontVariantNumeric: "tabular-nums",
                lineHeight: 1.1,
                marginTop: 2,
                whiteSpace: "nowrap",
              }}
            >
              {props.totalDisplayValue || "₹25,000 Cr"}
            </span>
          </div>
        </div>
      ) : (
        /* MODE B: COMPARATIVE DIVIDE (Side-by-Side Piles) */
        <div
          style={{
            position: "absolute",
            inset: 0,
            top: 55,
            bottom: 38,
            display: "flex",
            alignItems: "flex-end",
            justifyContent: "space-around",
            padding: "0 40px",
            boxSizing: "border-box",
          }}
        >
          {/* Left Small Pile (e.g. Monthly Savings) */}
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              gap: 6,
            }}
          >
            <div
              style={{
                width: 130,
                height: 22,
                backgroundColor: "#FEF3C7",
                border: `2px solid ${handDrawn.colors.ink}`,
                borderRadius: 4,
                boxShadow: "2px 2px 0 rgba(0,0,0,0.08)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <span style={{ fontSize: 10, fontWeight: 800, color: handDrawn.colors.ink }}>
                1 Bundle
              </span>
            </div>
            <div style={{ textAlign: "center" }}>
              <div style={{ fontSize: 12, fontWeight: 800, color: handDrawn.colors.inkMuted }}>
                {props.comparisonLeftLabel || "Monthly Savings"}
              </div>
              <div style={{ fontSize: 20, fontWeight: 900, color: handDrawn.colors.ink }}>
                {props.comparisonLeftValue || "₹25,000"}
              </div>
            </div>
          </div>

          {/* Versus Divider Badge */}
          <div
            style={{
              padding: "4px 8px",
              borderRadius: handDrawn.radius.pill,
              backgroundColor: handDrawn.colors.paper,
              border: `1.5px solid ${handDrawn.colors.ink}`,
              fontSize: 11,
              fontWeight: 800,
              fontFamily: handDrawn.font.label,
              marginBottom: 40,
            }}
          >
            VS
          </div>

          {/* Right Towering Pile (e.g. Corporate Profit / Wealthiest) */}
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              gap: 6,
            }}
          >
            <div
              style={{
                display: "flex",
                flexDirection: "column-reverse",
                gap: 2,
              }}
            >
              {Array.from({ length: 8 }).map((_, idx) => (
                <div
                  key={idx}
                  style={{
                    width: 140,
                    height: 14,
                    backgroundColor: "#DCFCE7",
                    border: `1.5px solid ${handDrawn.colors.ink}`,
                    borderRadius: 3,
                    boxShadow: "2px 2px 0 rgba(0,0,0,0.08)",
                  }}
                />
              ))}
            </div>
            <div style={{ textAlign: "center" }}>
              <div style={{ fontSize: 12, fontWeight: 800, color: handDrawn.colors.inkMuted }}>
                {props.comparisonRightLabel || "Corporate Daily Gain"}
              </div>
              <div style={{ fontSize: 24, fontWeight: 900, color: isDanger ? handDrawn.colors.red : handDrawn.colors.ink }}>
                {props.comparisonRightValue || "₹4.8 Crore"}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
