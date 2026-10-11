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

const colorByIntent: Record<string, { text: string; bg: string; border: string; dot: string }> = {
  danger: {
    text: "#fb7185",
    bg: "rgba(244, 63, 94, 0.15)",
    border: "rgba(244, 63, 94, 0.4)",
    dot: "#f43f5e",
  },
  accent: {
    text: "#38bdf8",
    bg: "rgba(56, 189, 248, 0.15)",
    border: "rgba(56, 189, 248, 0.4)",
    dot: "#38bdf8",
  },
  success: {
    text: "#34d399",
    bg: "rgba(16, 185, 129, 0.15)",
    border: "rgba(16, 185, 129, 0.4)",
    dot: "#10b981",
  },
  warning: {
    text: "#fde047",
    bg: "rgba(245, 158, 11, 0.15)",
    border: "rgba(245, 158, 11, 0.4)",
    dot: "#fbbf24",
  },
  neutral: {
    text: "#94a3b8",
    bg: "rgba(255, 255, 255, 0.08)",
    border: "rgba(255, 255, 255, 0.15)",
    dot: "#94a3b8",
  },
};

export const ComparisonCard: React.FC<ComponentProps> = ({
  runtime,
  instance,
  resolved,
  frame,
}) => {
  const props = resolved.props;
  const header = props.header as string | undefined;
  const leftLabel = (props.left_label as string) || "LEFT";
  const leftValue = (props.left_value as string) || "";
  const leftTag = props.left_tag as string | undefined;
  const leftIntent = (props.left_intent as string) || "danger";

  const rightLabel = (props.right_label as string) || "RIGHT";
  const rightValue = (props.right_value as string) || "";
  const rightTag = props.right_tag as string | undefined;
  const rightIntent = (props.right_intent as string) || "neutral";

  const subtext = props.subtext as string | undefined;

  const leftTheme = colorByIntent[leftIntent] || colorByIntent.danger;
  const rightTheme = colorByIntent[rightIntent] || colorByIntent.neutral;

  return (
    <div
      data-visual-component="ComparisonCard"
      data-object-id={instance.object_id}
      style={{
        position: "absolute",
        left: resolved.geometry.x,
        top: resolved.geometry.y,
        width: resolved.geometry.width,
        height: resolved.geometry.height,
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
        padding: "20px 24px",
        fontFamily: "Inter, ui-sans-serif, system-ui, sans-serif",
      }}
    >
      {/* Top Header */}
      {header && (
        <div
          style={{
            fontSize: 11,
            fontWeight: 700,
            letterSpacing: "0.12em",
            textTransform: "uppercase",
            color: "#64748b",
            marginBottom: 10,
            userSelect: "none",
          }}
        >
          {header}
        </div>
      )}

      {/* Comparison Split Columns */}
      {(() => {
        const enterFrame = runtime.getEntranceFrame(instance.object_id);
        const elapsed = Math.max(0, frame - enterFrame);
        const leftProgress = Math.min(1, Math.max(0, elapsed / 10));
        const vsProgress = Math.min(1, Math.max(0, (elapsed - 6) / 8));
        const rightProgress = Math.min(1, Math.max(0, (elapsed - 12) / 10));

        return (
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              flex: 1,
              gap: 16,
            }}
          >
            {/* Left Column */}
            <div
              style={{
                flex: 1,
                display: "flex",
                flexDirection: "column",
                gap: 4,
                opacity: leftProgress,
                transform: `translateY(${((1 - leftProgress) * 6).toFixed(1)}px)`,
              }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <span
                  style={{
                    fontSize: 11,
                    fontWeight: 700,
                    letterSpacing: "0.08em",
                    textTransform: "uppercase",
                    color: "#94a3b8",
                  }}
                >
                  {leftLabel}
                </span>
                {leftTag && (
                  <span
                    style={{
                      fontSize: 9,
                      fontWeight: 700,
                      padding: "2px 6px",
                      borderRadius: 9999,
                      background: leftTheme.bg,
                      color: leftTheme.text,
                      border: `1px solid ${leftTheme.border}`,
                      textTransform: "uppercase",
                    }}
                  >
                    {leftTag}
                  </span>
                )}
              </div>
              <div
                style={{
                  fontSize: 38,
                  fontWeight: 800,
                  lineHeight: 1,
                  color: leftTheme.text,
                  fontVariantNumeric: "tabular-nums",
                }}
              >
                {leftValue}
              </div>
            </div>

            {/* Center Divider / VS */}
            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                padding: "4px 8px",
                borderRadius: 9999,
                background: "rgba(255, 255, 255, 0.05)",
                border: "1px solid rgba(255, 255, 255, 0.1)",
                fontSize: 10,
                fontWeight: 800,
                color: "#64748b",
                textTransform: "uppercase",
                opacity: vsProgress,
                transform: `scale(${(0.8 + 0.2 * vsProgress).toFixed(2)})`,
              }}
            >
              vs
            </div>

            {/* Right Column */}
            <div
              style={{
                flex: 1,
                display: "flex",
                flexDirection: "column",
                gap: 4,
                textAlign: "right",
                opacity: rightProgress,
                transform: `translateY(${((1 - rightProgress) * 6).toFixed(1)}px)`,
              }}
            >
              <div style={{ display: "flex", alignItems: "center", justifyContent: "flex-end", gap: 8 }}>
                {rightTag && (
                  <span
                    style={{
                      fontSize: 9,
                      fontWeight: 700,
                      padding: "2px 6px",
                      borderRadius: 9999,
                      background: rightTheme.bg,
                      color: rightTheme.text,
                      border: `1px solid ${rightTheme.border}`,
                      textTransform: "uppercase",
                    }}
                  >
                    {rightTag}
                  </span>
                )}
                <span
                  style={{
                    fontSize: 11,
                    fontWeight: 700,
                    letterSpacing: "0.08em",
                    textTransform: "uppercase",
                    color: "#94a3b8",
                  }}
                >
                  {rightLabel}
                </span>
              </div>
              <div
                style={{
                  fontSize: 38,
                  fontWeight: 800,
                  lineHeight: 1,
                  color: rightTheme.text,
                  fontVariantNumeric: "tabular-nums",
                }}
              >
                {rightValue}
              </div>
            </div>
          </div>
        );
      })()}

      {/* Subtext Footer */}
      {subtext && (
        <div
          style={{
            fontSize: 11,
            color: "#64748b",
            marginTop: 10,
            lineHeight: 1.3,
            userSelect: "none",
          }}
        >
          {subtext}
        </div>
      )}
    </div>
  );
};
