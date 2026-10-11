import React from "react";
import { spring } from "remotion";
import type { CompiledVisualInstance } from "../world/compiledWorld";
import type { ResolvedPrimitiveFrame } from "../world/runtime/types";
import type { WorldRuntime } from "../world/runtime";

export interface ComponentProps {
  runtime: WorldRuntime;
  instance: CompiledVisualInstance;
  resolved: ResolvedPrimitiveFrame;
  frame: number;
}

export interface DonutSlice {
  label: string;
  value: number;
  display_value?: string;
  intent?: "neutral" | "accent" | "danger" | "success" | "warning";
  color?: string;
  tag?: string;
}

const PALETTE: { color: string; glow: string }[] = [
  { color: "#38bdf8", glow: "rgba(56, 189, 248, 0.45)" }, // Cyan / Sky
  { color: "#818cf8", glow: "rgba(129, 140, 248, 0.45)" }, // Indigo / Violet
  { color: "#34d399", glow: "rgba(52, 211, 153, 0.45)" }, // Emerald / Green
  { color: "#fbbf24", glow: "rgba(251, 191, 36, 0.45)" }, // Amber / Gold
  { color: "#f43f5e", glow: "rgba(244, 63, 94, 0.45)" }, // Rose / Danger
  { color: "#94a3b8", glow: "rgba(148, 163, 184, 0.35)" }, // Slate / Neutral
];

const intentColorMap: Record<string, { color: string; glow: string }> = {
  accent: { color: "#38bdf8", glow: "rgba(56, 189, 248, 0.5)" },
  success: { color: "#34d399", glow: "rgba(52, 211, 153, 0.5)" },
  warning: { color: "#fbbf24", glow: "rgba(251, 191, 36, 0.5)" },
  danger: { color: "#f43f5e", glow: "rgba(244, 63, 94, 0.5)" },
  neutral: { color: "#94a3b8", glow: "rgba(148, 163, 184, 0.35)" },
};

export const AllocationDonut: React.FC<ComponentProps> = ({
  runtime,
  instance,
  resolved,
  frame,
}) => {
  const props = resolved.props;
  const header = (props.header as string) || (props.title as string) || "PORTFOLIO ALLOCATION";
  const subtext = props.subtext as string | undefined;
  const centerLabel = (props.center_label as string) || undefined;
  const centerValue = (props.center_value as string) || undefined;

  // Parse slices
  let rawSlices: DonutSlice[] = [];
  if (Array.isArray(props.slices)) {
    rawSlices = props.slices.map((s: any) => {
      const numVal = typeof s?.value === "number" ? s.value : parseFloat(String(s?.value || 0)) || 0;
      return {
        label: String(s?.label ?? "Slice"),
        value: numVal,
        display_value: s?.display_value ? String(s.display_value) : undefined,
        intent: s?.intent,
        color: s?.color,
        tag: s?.tag ? String(s.tag) : undefined,
      };
    });
  }

  // Fallback if empty
  if (rawSlices.length === 0) {
    rawSlices = [
      { label: "Equities", value: 60, display_value: "60%", intent: "accent" },
      { label: "Fixed Income", value: 30, display_value: "30%", intent: "neutral" },
      { label: "Gold & Cash", value: 10, display_value: "10%", intent: "warning" },
    ];
  }

  // Calculate total and percentages
  const totalValue = rawSlices.reduce((acc, s) => acc + Math.max(0, s.value), 0) || 1;
  const slicesWithProportions = rawSlices.map((s, idx) => {
    const validVal = Math.max(0, s.value);
    const pct = (validVal / totalValue) * 100;
    const theme =
      (s.intent && intentColorMap[s.intent]) ||
      (s.color ? { color: s.color, glow: "rgba(255,255,255,0.2)" } : PALETTE[idx % PALETTE.length]);
    return {
      ...s,
      percentage: pct,
      display_value: s.display_value || `${Math.round(pct)}%`,
      theme,
    };
  });

  // Entrance timing
  const enterFrame = runtime.getEntranceFrame(instance.object_id);
  const localFrame = Math.max(0, frame - enterFrame);

  // Card geometry
  const cardWidth = resolved.geometry.width || 840;
  const cardHeight = resolved.geometry.height || 380;

  // Donut geometry
  const size = Math.min(220, cardHeight - 110);
  const strokeWidth = 26;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const cx = size / 2;
  const cy = size / 2;

  // Overall chart rotation / draw spring
  const drawProgress = spring({
    frame: localFrame,
    fps: 30,
    config: { damping: 18, stiffness: 100, mass: 0.8 },
  });

  return (
    <div
      data-visual-component="AllocationDonut"
      data-object-id={instance.object_id}
      style={{
        position: "absolute",
        left: resolved.geometry.x,
        top: resolved.geometry.y,
        width: cardWidth,
        height: cardHeight,
        opacity: resolved.opacity,
        transform: resolved.transform,
        transformOrigin: "center center",
        background: "linear-gradient(180deg, #131722 0%, #0d111a 100%)",
        border: "1px solid rgba(255, 255, 255, 0.10)",
        borderRadius: 16,
        boxShadow: "0 24px 48px -12px rgba(0, 0, 0, 0.8), 0 0 0 1px rgba(255, 255, 255, 0.04) inset",
        boxSizing: "border-box",
        overflow: "hidden",
        display: "flex",
        flexDirection: "column",
        justifyContent: "space-between",
        padding: "24px 30px",
        fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
      }}
    >
      {/* Header section */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "flex-start",
          marginBottom: 12,
        }}
      >
        <div>
          <div
            style={{
              fontSize: 11,
              fontWeight: 800,
              letterSpacing: "0.14em",
              color: "#64748b",
              textTransform: "uppercase",
              marginBottom: 4,
            }}
          >
            ASSET & CAPITAL BREAKDOWN
          </div>
          <div
            style={{
              fontSize: 20,
              fontWeight: 700,
              letterSpacing: "-0.01em",
              color: "#f8fafc",
            }}
          >
            {header}
          </div>
        </div>

        {subtext && (
          <div
            style={{
              fontSize: 12,
              fontWeight: 500,
              color: "#94a3b8",
              backgroundColor: "rgba(255, 255, 255, 0.04)",
              border: "1px solid rgba(255, 255, 255, 0.08)",
              padding: "4px 10px",
              borderRadius: 6,
              maxWidth: 320,
              textAlign: "right",
            }}
          >
            {subtext}
          </div>
        )}
      </div>

      {/* Main Content: Donut + Legend */}
      <div
        style={{
          flex: 1,
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          gap: 32,
        }}
      >
        {/* Donut Chart with Center Text */}
        <div
          style={{
            position: "relative",
            width: size,
            height: size,
            flexShrink: 0,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <svg
            width={size}
            height={size}
            viewBox={`0 0 ${size} ${size}`}
            style={{
              transform: "rotate(-90deg)",
              overflow: "visible",
            }}
          >
            {/* Background track circle */}
            <circle
              cx={cx}
              cy={cy}
              r={radius}
              fill="transparent"
              stroke="rgba(255, 255, 255, 0.05)"
              strokeWidth={strokeWidth}
            />

            {/* Slices rendered with stroke-dasharray */}
            {(() => {
              let accumulatedAngle = 0;
              const gapOffset = slicesWithProportions.length > 1 ? 2.5 : 0; // px gap between segments

              return slicesWithProportions.map((slice, index) => {
                const sliceRatio = slice.percentage / 100;
                const rawLength = sliceRatio * circumference;
                const strokeLength = Math.max(0, rawLength - gapOffset);
                const currentOffset = accumulatedAngle;
                accumulatedAngle += rawLength;

                const segmentAnim = spring({
                  frame: Math.max(0, localFrame - index * 3),
                  fps: 30,
                  config: { damping: 16, stiffness: 90 },
                });

                const animatedStrokeLength = strokeLength * drawProgress * segmentAnim;

                return (
                  <circle
                    key={index}
                    cx={cx}
                    cy={cy}
                    r={radius}
                    fill="transparent"
                    stroke={slice.theme.color}
                    strokeWidth={strokeWidth}
                    strokeDasharray={`${animatedStrokeLength} ${circumference - animatedStrokeLength}`}
                    strokeDashoffset={-currentOffset}
                    strokeLinecap="round"
                    style={{
                      filter: `drop-shadow(0 0 6px ${slice.theme.glow})`,
                      transition: "stroke 0.2s ease",
                    }}
                  />
                );
              });
            })()}
          </svg>

          {/* Donut Center Display */}
          <div
            style={{
              position: "absolute",
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              textAlign: "center",
              pointerEvents: "none",
              maxWidth: size - strokeWidth * 2 - 16,
            }}
          >
            {centerValue ? (
              <span
                style={{
                  fontSize: 22,
                  fontWeight: 800,
                  letterSpacing: "-0.02em",
                  color: "#ffffff",
                  lineHeight: 1.1,
                  textShadow: "0 2px 10px rgba(0,0,0,0.8)",
                }}
              >
                {centerValue}
              </span>
            ) : (
              <span
                style={{
                  fontSize: 20,
                  fontWeight: 800,
                  color: "#38bdf8",
                  letterSpacing: "-0.01em",
                }}
              >
                {`${slicesWithProportions.length} SLICES`}
              </span>
            )}
            <span
              style={{
                fontSize: 9,
                fontWeight: 700,
                letterSpacing: "0.12em",
                color: "#64748b",
                textTransform: "uppercase",
                marginTop: 2,
              }}
            >
              {centerLabel || "TOTAL SHARE"}
            </span>
          </div>
        </div>

        {/* Legend / Slice Breakdown List */}
        <div
          style={{
            flex: 1,
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
            gap: 10,
          }}
        >
          {slicesWithProportions.map((slice, index) => {
            const itemSpring = spring({
              frame: Math.max(0, localFrame - 4 - index * 4),
              fps: 30,
              config: { damping: 15, stiffness: 120 },
            });

            return (
              <div
                key={index}
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  padding: "8px 14px",
                  borderRadius: 8,
                  backgroundColor: "rgba(255, 255, 255, 0.025)",
                  border: "1px solid rgba(255, 255, 255, 0.05)",
                  opacity: itemSpring,
                  transform: `translateX(${(1 - itemSpring) * 16}px)`,
                }}
              >
                {/* Left: Indicator + Label + Tag */}
                <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                  <div
                    style={{
                      width: 10,
                      height: 10,
                      borderRadius: "50%",
                      backgroundColor: slice.theme.color,
                      boxShadow: `0 0 8px ${slice.theme.glow}`,
                      flexShrink: 0,
                    }}
                  />
                  <span
                    style={{
                      fontSize: 13,
                      fontWeight: 600,
                      color: "#e2e8f0",
                      letterSpacing: "0.01em",
                    }}
                  >
                    {slice.label}
                  </span>
                  {slice.tag && (
                    <span
                      style={{
                        fontSize: 9,
                        fontWeight: 700,
                        color: slice.theme.color,
                        backgroundColor: "rgba(255, 255, 255, 0.05)",
                        border: `1px solid ${slice.theme.color}40`,
                        padding: "2px 6px",
                        borderRadius: 4,
                        letterSpacing: "0.06em",
                        textTransform: "uppercase",
                      }}
                    >
                      {slice.tag}
                    </span>
                  )}
                </div>

                {/* Right: Value & Percentage */}
                <div style={{ display: "flex", alignItems: "baseline", gap: 8 }}>
                  <span
                    style={{
                      fontSize: 15,
                      fontWeight: 700,
                      color: "#f8fafc",
                      letterSpacing: "-0.01em",
                    }}
                  >
                    {slice.display_value}
                  </span>
                  {slice.display_value !== `${Math.round(slice.percentage)}%` && (
                    <span
                      style={{
                        fontSize: 11,
                        fontWeight: 600,
                        color: "#64748b",
                      }}
                    >
                      ({Math.round(slice.percentage)}%)
                    </span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
