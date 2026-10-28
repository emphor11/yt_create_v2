import React from "react";
import { useCurrentFrame, spring } from "remotion";
import type { WaterfallProps, VisualStateKind } from "../types.ts";
import { handDrawn, handDrawnAccent } from "../hand-drawn-theme.ts";

export interface WaterfallPrimitiveProps {
  props: WaterfallProps;
  visualState?: VisualStateKind;
  badge?: string;
  customAccent?: string;
  width?: number;
  height?: number;
  layout?: string;
  style?: React.CSSProperties;
}

export const WaterfallPrimitive: React.FC<WaterfallPrimitiveProps> = ({
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
  const boxW = width ?? 840;
  const boxH = height ?? 440;

  const activeVisualState = visualState || props.visualState || "normal";
  const isDanger = activeVisualState === "danger";
  const isWarning = activeVisualState === "warning";

  let accentColor = customAccent || props.accentColor || (isDanger ? handDrawn.colors.red : isWarning ? handDrawn.colors.amber : handDrawn.colors.ink);
  let glowStyle = isDanger
    ? `4px 5px 0 ${handDrawn.colors.coralSoft}, ${handDrawn.shadow.paper}`
    : handDrawn.shadow.paper;

  const initVal = props.initialValue && props.initialValue > 0 ? props.initialValue : 100000;
  const steps = props.steps || [];

  // Compute surviving ratio
  const finalVal = props.finalValue !== undefined ? props.finalValue : Math.max(0, initVal - steps.reduce((acc, s) => acc + (s.stepType === "addition" ? -s.value : s.value), 0));
  const survivingPct = Math.round((finalVal / initVal) * 100);

  // Staggered spring animations for steps
  const initSpring = spring({
    frame,
    fps: 30,
    config: { damping: 14, stiffness: 90 },
  });

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
        padding: "20px 24px",
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
          backgroundColor: isDanger ? handDrawn.colors.red : isWarning ? handDrawn.colors.amber : "#3B82F6",
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
          marginBottom: 12,
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
                d="M12 3V21M12 21L6 15M12 21L18 15"
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
            {props.title || "CASH FLOW WATERFALL"}
          </span>
        </div>

        <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
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
          <span
            style={{
              fontSize: 11,
              fontWeight: 700,
              color: handDrawn.colors.inkMuted,
              fontFamily: "monospace",
            }}
          >
            {survivingPct}% SURVIVING
          </span>
        </div>
      </div>

      {/* Waterfall Body */}
      <div
        style={{
          flex: 1,
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          gap: 6,
        }}
      >
        {/* 1. Initial Starting Value (Gross 100%) */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 12,
            opacity: initSpring,
            transform: `translateY(${(1 - initSpring) * -8}px)`,
          }}
        >
          <div style={{ width: 160, flexShrink: 0 }}>
            <div style={{ fontSize: 13, fontWeight: 700, color: handDrawn.colors.ink }}>
              {props.initialLabel}
            </div>
            <div style={{ fontSize: 10, color: handDrawn.colors.inkMuted, fontFamily: "monospace" }}>
              STARTING 100%
            </div>
          </div>

          <div
            style={{
              flex: 1,
              height: 24,
              backgroundColor: `${handDrawn.colors.ink}15`,
              borderRadius: 4,
              overflow: "hidden",
              position: "relative",
              border: `1px solid ${handDrawn.colors.ink}33`,
            }}
          >
            <div
              style={{
                height: "100%",
                width: `${Math.min(100, initSpring * 100)}%`,
                backgroundColor: "#2563EB",
                borderRadius: 3,
              }}
            />
          </div>

          <div
            style={{
              width: 120,
              textAlign: "right",
              fontSize: 14,
              fontWeight: 800,
              fontFamily: "monospace",
              color: "#2563EB",
              flexShrink: 0,
            }}
          >
            {props.initialDisplayValue}
          </div>
        </div>

        {/* 2. Cascading Steps (Deductions / Additions) */}
        {steps.map((step, idx) => {
          const stepSpring = spring({
            frame: Math.max(0, frame - 5 - idx * 4),
            fps: 30,
            config: { damping: 14, stiffness: 95 },
          });

          const isDeduction = step.stepType !== "addition";
          const barRatio = Math.max(0.05, Math.min(0.95, (step.value || (initVal * 0.2)) / initVal));
          const stepColor = isDeduction ? handDrawn.colors.red : handDrawn.colors.green;

          return (
            <div
              key={idx}
              style={{
                display: "flex",
                alignItems: "center",
                gap: 12,
                opacity: stepSpring,
                transform: `translateX(${(1 - stepSpring) * 12}px)`,
              }}
            >
              <div style={{ width: 160, flexShrink: 0 }}>
                <div
                  style={{
                    fontSize: 12,
                    fontWeight: 600,
                    color: handDrawn.colors.ink,
                    whiteSpace: "nowrap",
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                  }}
                >
                  {step.label}
                </div>
                <div
                  style={{
                    fontSize: 10,
                    color: stepColor,
                    fontFamily: "monospace",
                    fontWeight: 700,
                  }}
                >
                  {isDeduction ? "▼ DEDUCTION" : "▲ ADDITION"}
                </div>
              </div>

              <div
                style={{
                  flex: 1,
                  height: 20,
                  backgroundColor: `${handDrawn.colors.ink}0A`,
                  borderRadius: 4,
                  overflow: "hidden",
                  position: "relative",
                  border: `1px dashed ${handDrawn.colors.ink}26`,
                }}
              >
                <div
                  style={{
                    height: "100%",
                    width: `${Math.min(100, barRatio * stepSpring * 100)}%`,
                    backgroundColor: isDeduction ? "#EF4444" : "#10B981",
                    borderRadius: 3,
                  }}
                />
              </div>

              <div
                style={{
                  width: 120,
                  textAlign: "right",
                  fontSize: 13,
                  fontWeight: 700,
                  fontFamily: "monospace",
                  color: stepColor,
                  flexShrink: 0,
                }}
              >
                {step.displayValue}
              </div>
            </div>
          );
        })}

        {/* 3. Final Bottom Line (Net Surviving Cash) */}
        {(() => {
          const finalSpring = spring({
            frame: Math.max(0, frame - 8 - steps.length * 4),
            fps: 30,
            config: { damping: 12, stiffness: 100 },
          });

          const finalBarRatio = Math.max(0.04, Math.min(1.0, finalVal / initVal));
          const finalColor = isDanger || survivingPct <= 15 ? handDrawn.colors.red : handDrawn.colors.green;

          return (
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: 12,
                marginTop: 4,
                paddingTop: 8,
                borderTop: `2px solid ${handDrawn.colors.ink}26`,
                opacity: finalSpring,
                transform: `scale(${0.96 + finalSpring * 0.04})`,
              }}
            >
              <div style={{ width: 160, flexShrink: 0 }}>
                <div
                  style={{
                    fontSize: 14,
                    fontWeight: 900,
                    color: handDrawn.colors.ink,
                    letterSpacing: "0.04em",
                  }}
                >
                  {props.finalLabel}
                </div>
                <div
                  style={{
                    fontSize: 10,
                    color: finalColor,
                    fontFamily: "monospace",
                    fontWeight: 800,
                  }}
                >
                  BOTTOM LINE CASH
                </div>
              </div>

              <div
                style={{
                  flex: 1,
                  height: 28,
                  backgroundColor: `${finalColor}15`,
                  borderRadius: 4,
                  overflow: "hidden",
                  position: "relative",
                  border: `2px solid ${finalColor}`,
                }}
              >
                <div
                  style={{
                    height: "100%",
                    width: `${Math.min(100, finalBarRatio * finalSpring * 100)}%`,
                    backgroundColor: finalColor,
                    borderRadius: 2,
                  }}
                />
              </div>

              <div
                style={{
                  width: 120,
                  textAlign: "right",
                  fontSize: 17,
                  fontWeight: 900,
                  fontFamily: "monospace",
                  color: finalColor,
                  flexShrink: 0,
                }}
              >
                {props.finalDisplayValue}
              </div>
            </div>
          );
        })()}
      </div>
    </div>
  );
};
