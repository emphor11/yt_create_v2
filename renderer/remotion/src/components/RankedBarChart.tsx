import React from "react";
import type { CompiledVisualInstance } from "../world/compiledWorld";
import type { ResolvedPrimitiveFrame } from "../world/runtime/types";
import type { WorldRuntime } from "../world/runtime";

export interface ComponentProps {
  runtime: WorldRuntime;
  instance: CompiledVisualInstance;
  resolved: ResolvedPrimitiveFrame;
  frame: number;
}

export interface BarItem {
  label: string;
  value: number;
  display_value?: string;
  intent?: "neutral" | "accent" | "danger" | "success" | "warning";
  tag?: string;
}

const colorByIntent: Record<
  string,
  {
    barColor: string;
    barGradient: string;
    glow: string;
    badgeBg: string;
    badgeText: string;
    badgeBorder: string;
  }
> = {
  danger: {
    barColor: "#f43f5e",
    barGradient: "linear-gradient(90deg, rgba(244, 63, 94, 0.6) 0%, #f43f5e 100%)",
    glow: "rgba(244, 63, 94, 0.4)",
    badgeBg: "rgba(244, 63, 94, 0.15)",
    badgeText: "#fb7185",
    badgeBorder: "rgba(244, 63, 94, 0.4)",
  },
  accent: {
    barColor: "#38bdf8",
    barGradient: "linear-gradient(90deg, rgba(56, 189, 248, 0.6) 0%, #38bdf8 100%)",
    glow: "rgba(56, 189, 248, 0.4)",
    badgeBg: "rgba(56, 189, 248, 0.15)",
    badgeText: "#38bdf8",
    badgeBorder: "rgba(56, 189, 248, 0.4)",
  },
  success: {
    barColor: "#10b981",
    barGradient: "linear-gradient(90deg, rgba(16, 185, 129, 0.6) 0%, #10b981 100%)",
    glow: "rgba(16, 185, 129, 0.4)",
    badgeBg: "rgba(16, 185, 129, 0.15)",
    badgeText: "#34d399",
    badgeBorder: "rgba(16, 185, 129, 0.4)",
  },
  warning: {
    barColor: "#fbbf24",
    barGradient: "linear-gradient(90deg, rgba(245, 158, 11, 0.6) 0%, #fbbf24 100%)",
    glow: "rgba(245, 158, 11, 0.4)",
    badgeBg: "rgba(245, 158, 11, 0.15)",
    badgeText: "#fde047",
    badgeBorder: "rgba(245, 158, 11, 0.4)",
  },
  neutral: {
    barColor: "#94a3b8",
    barGradient: "linear-gradient(90deg, rgba(148, 163, 184, 0.5) 0%, #cbd5e1 100%)",
    glow: "rgba(148, 163, 184, 0.3)",
    badgeBg: "rgba(255, 255, 255, 0.08)",
    badgeText: "#cbd5e1",
    badgeBorder: "rgba(255, 255, 255, 0.15)",
  },
};

export const RankedBarChart: React.FC<ComponentProps> = ({
  runtime,
  instance,
  resolved,
  frame,
}) => {
  const props = resolved.props;
  const header = (props.header as string) || (props.title as string) || "COMPARATIVE RANKING";
  const subtext = props.subtext as string | undefined;

  const benchmarkVal =
    typeof props.benchmark_value === "number"
      ? props.benchmark_value
      : typeof props.benchmark_value === "string"
      ? parseFloat(props.benchmark_value) || undefined
      : undefined;

  const benchmarkLabel = (props.benchmark_label as string) || "Benchmark";

  // Parse bars list safely
  let rawBars: BarItem[] = [];
  if (Array.isArray(props.bars)) {
    rawBars = props.bars.map((b: any) => {
      const numVal = typeof b?.value === "number" ? b.value : parseFloat(String(b?.value || 0)) || 0;
      return {
        label: String(b?.label ?? "Item"),
        value: numVal,
        display_value: b?.display_value ? String(b.display_value) : String(numVal),
        intent: b?.intent || "neutral",
        tag: b?.tag ? String(b.tag) : undefined,
      };
    });
  }

  // Fallback if empty
  if (rawBars.length === 0) {
    rawBars = [
      { label: "Category A", value: 75, display_value: "75%", intent: "accent" },
      { label: "Category B", value: 45, display_value: "45%", intent: "neutral" },
    ];
  }

  // Animation timing
  const enterFrame = runtime.getEntranceFrame(instance.object_id);

  // Maximum value for proportional width calculation
  const barMax = Math.max(...rawBars.map((b) => Math.max(0, b.value)));
  const allMax = benchmarkVal !== undefined ? Math.max(barMax, benchmarkVal) : barMax;
  const scaleMax = allMax === 0 ? 1 : allMax * 1.08; // 8% headroom on the right

  const cardWidth = resolved.geometry.width || 760;
  const cardHeight = resolved.geometry.height || 360;

  return (
    <div
      data-visual-component="RankedBarChart"
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
        padding: "24px 28px",
        fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
      }}
    >
      {/* Header bar */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "flex-start",
          marginBottom: 16,
        }}
      >
        <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
          <span
            style={{
              fontSize: 13,
              fontWeight: 700,
              letterSpacing: 1.5,
              textTransform: "uppercase",
              color: "rgba(255, 255, 255, 0.70)",
            }}
          >
            {header}
          </span>
          {subtext && (
            <span style={{ fontSize: 11, color: "rgba(255, 255, 255, 0.40)" }}>
              {subtext}
            </span>
          )}
        </div>

        {benchmarkVal !== undefined && (
          <div
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: 6,
              padding: "4px 10px",
              borderRadius: 6,
              backgroundColor: "rgba(255, 255, 255, 0.06)",
              border: "1px dashed rgba(255, 255, 255, 0.25)",
              color: "rgba(255, 255, 255, 0.70)",
              fontSize: 11,
              fontWeight: 600,
            }}
          >
            <span>{benchmarkLabel}:</span>
            <span style={{ color: "#ffffff", fontWeight: 700 }}>{benchmarkVal}</span>
          </div>
        )}
      </div>

      {/* Bar Stack Container */}
      <div
        style={{
          position: "relative",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-around",
          flex: 1,
          gap: 12,
        }}
      >
        {/* Benchmark Vertical Line overlay if present */}
        {benchmarkVal !== undefined && (
          <div
            style={{
              position: "absolute",
              left: `${Math.min(95, Math.max(5, (benchmarkVal / scaleMax) * 100))}%`,
              top: 0,
              bottom: 0,
              width: 1,
              borderLeft: "1.5px dashed rgba(255, 255, 255, 0.30)",
              zIndex: 1,
              pointerEvents: "none",
            }}
          />
        )}

        {rawBars.map((bar, i) => {
          const theme = colorByIntent[bar.intent || "neutral"] || colorByIntent.neutral;

          // Stagger each bar's entrance by 3 frames
          const elapsed = Math.max(0, frame - enterFrame - i * 3);
          const barDuration = 24;
          const progress = Math.min(1, Math.max(0, elapsed / barDuration));
          const eased = 1 - Math.pow(1 - progress, 3); // Cubic ease out

          const targetWidthPct = Math.min(100, Math.max(1, (bar.value / scaleMax) * 100));
          const currentWidthPct = targetWidthPct * eased;

          return (
            <div
              key={i}
              style={{
                display: "flex",
                flexDirection: "column",
                gap: 6,
                zIndex: 2,
              }}
            >
              {/* Row Header: Label + Optional Tag (left), Display Value (right) */}
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                  <span
                    style={{
                      fontSize: 13,
                      fontWeight: 600,
                      color: "rgba(255, 255, 255, 0.90)",
                      letterSpacing: 0.3,
                    }}
                  >
                    {bar.label}
                  </span>

                  {bar.tag && (
                    <span
                      style={{
                        fontSize: 10,
                        fontWeight: 700,
                        letterSpacing: 0.8,
                        textTransform: "uppercase",
                        padding: "2px 8px",
                        borderRadius: 9999,
                        backgroundColor: theme.badgeBg,
                        border: `1px solid ${theme.badgeBorder}`,
                        color: theme.badgeText,
                      }}
                    >
                      {bar.tag}
                    </span>
                  )}
                </div>

                <span
                  style={{
                    fontSize: 14,
                    fontWeight: 800,
                    letterSpacing: 0.5,
                    color: eased > 0.8 ? theme.barColor : "#ffffff",
                    textShadow: eased > 0.8 ? `0 0 12px ${theme.glow}` : "none",
                    transition: "color 0.2s ease",
                  }}
                >
                  {bar.display_value}
                </span>
              </div>

              {/* Bar Track & Fill */}
              <div
                style={{
                  width: "100%",
                  height: 10,
                  backgroundColor: "rgba(255, 255, 255, 0.06)",
                  borderRadius: 6,
                  overflow: "hidden",
                  boxShadow: "inset 0 1px 2px rgba(0, 0, 0, 0.6)",
                }}
              >
                <div
                  style={{
                    height: "100%",
                    width: `${currentWidthPct}%`,
                    background: theme.barGradient,
                    borderRadius: 6,
                    boxShadow: `0 0 12px ${theme.glow}`,
                  }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
