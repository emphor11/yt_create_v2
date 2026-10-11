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

function formatNumberWithDecimals(val: number, decimals?: number): string {
  if (decimals !== undefined) {
    if (decimals === 0) {
      return Math.round(val).toLocaleString("en-US");
    }
    return val.toLocaleString("en-US", {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    });
  }
  const isFloat = val % 1 !== 0;
  if (isFloat) {
    return val.toFixed(2).replace(/\.?0+$/, "");
  }
  return Math.round(val).toLocaleString("en-US");
}

function formatWithDisplayTemplate(
  displayValue: string,
  currentVal: number,
  targetVal: number,
  isFinished: boolean
): string {
  if (!displayValue) {
    return formatNumberWithDecimals(currentVal);
  }

  const match = displayValue.match(/[\d,]+(?:\.\d+)?/);
  if (!match) {
    return displayValue;
  }

  const numStr = match[0];
  const decimalPart = numStr.includes(".") ? numStr.split(".")[1] : "";
  const decimals = decimalPart.length;

  const templateNum = Number(numStr.replace(/,/g, ""));
  if (isFinished && Math.abs(currentVal - templateNum) < 1e-6) {
    return displayValue;
  }

  const formattedAnim = formatNumberWithDecimals(currentVal, decimals);
  return displayValue.replace(numStr, formattedAnim);
}

export const MetricCard: React.FC<ComponentProps> = ({
  runtime,
  instance,
  resolved,
  frame,
}) => {
  const props = resolved.props;
  const header = props.header as string | undefined;
  const label = (props.label as string) || "";
  const displayValue = (props.display_value as string) || "";
  const tag = props.tag as string | undefined;
  const subtext = props.subtext as string | undefined;
  const intent = (props.intent as string) || "neutral";
  const variant = (props.variant as string) || "elevated";

  // Intent color themes
  const intentThemes: Record<
    string,
    { border: string; accent: string; glow: string; badgeBg: string; badgeText: string; dot: string }
  > = {
    danger: {
      border: "rgba(244, 63, 94, 0.35)",
      accent: "#f43f5e",
      glow: "rgba(244, 63, 94, 0.2)",
      badgeBg: "rgba(244, 63, 94, 0.15)",
      badgeText: "#fb7185",
      dot: "#f43f5e",
    },
    accent: {
      border: "rgba(56, 189, 248, 0.35)",
      accent: "#38bdf8",
      glow: "rgba(56, 189, 248, 0.2)",
      badgeBg: "rgba(56, 189, 248, 0.15)",
      badgeText: "#38bdf8",
      dot: "#38bdf8",
    },
    success: {
      border: "rgba(16, 185, 129, 0.35)",
      accent: "#10b981",
      glow: "rgba(16, 185, 129, 0.2)",
      badgeBg: "rgba(16, 185, 129, 0.15)",
      badgeText: "#34d399",
      dot: "#10b981",
    },
    warning: {
      border: "rgba(245, 158, 11, 0.35)",
      accent: "#fbbf24",
      glow: "rgba(245, 158, 11, 0.2)",
      badgeBg: "rgba(245, 158, 11, 0.15)",
      badgeText: "#fde047",
      dot: "#fbbf24",
    },
    neutral: {
      border: "rgba(255, 255, 255, 0.10)",
      accent: "#94a3b8",
      glow: "rgba(255, 255, 255, 0.05)",
      badgeBg: "rgba(255, 255, 255, 0.08)",
      badgeText: "#e2e8f0",
      dot: "#94a3b8",
    },
  };

  const theme = intentThemes[intent] || intentThemes.neutral;

  // Resolve numeric target value from props.value, props.raw_value, or display_value template
  let targetVal: number | undefined;
  if (typeof props.value === "number") {
    targetVal = props.value;
  } else if (typeof props.raw_value === "number") {
    targetVal = props.raw_value;
  } else if (typeof props.raw_value === "string" && !isNaN(Number(props.raw_value))) {
    targetVal = Number(props.raw_value);
  } else if (displayValue && !displayValue.includes("–") && !displayValue.includes("-")) {
    const isYear = /^(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)/i.test(displayValue.trim());
    const match = displayValue.match(/[\d,]+(?:\.\d+)?/);
    if (match && !isYear) {
      const parsed = parseFloat(match[0].replace(/,/g, ""));
      if (!isNaN(parsed)) {
        targetVal = parsed;
      }
    }
  }

  let renderedValue = displayValue;
  if (typeof targetVal === "number") {
    const enterFrame = runtime.getEntranceFrame(instance.object_id);
    const countDuration = 25;
    const elapsed = Math.max(0, frame - enterFrame);
    const countProgress = Math.min(1, Math.max(0, elapsed / countDuration));
    const easedProgress = 1 - Math.pow(1 - countProgress, 3);
    const startVal = typeof props.start_value === "number" ? props.start_value : 0;
    const animatedVal = startVal + (targetVal - startVal) * easedProgress;
    const isFinished = elapsed >= countDuration;

    renderedValue = formatWithDisplayTemplate(displayValue, animatedVal, targetVal, isFinished);
  }

  const showTopAccent = variant === "accent_top" || intent === "accent" || intent === "danger";

  return (
    <div
      data-visual-component="MetricCard"
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
        border: `1px solid ${theme.border}`,
        borderRadius: 16,
        boxShadow: `0 24px 48px -12px rgba(0, 0, 0, 0.8), 0 0 24px -6px ${theme.glow}`,
        boxSizing: "border-box",
        overflow: "hidden",
        display: "flex",
        flexDirection: "column",
        justifyContent: "space-between",
        padding: "20px 24px",
        fontFamily: "Inter, ui-sans-serif, system-ui, sans-serif",
      }}
    >
      {/* Top Accent Strip */}
      {showTopAccent && (
        <div
          style={{
            position: "absolute",
            top: 0,
            left: 0,
            right: 0,
            height: 3,
            background: theme.accent,
            boxShadow: `0 0 10px ${theme.accent}`,
          }}
        />
      )}

      {/* Top Bar: Header (Left) and Tag/Badge (Right) */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          minHeight: 24,
          marginBottom: 8,
        }}
      >
        {header ? (
          <span
            style={{
              fontSize: 11,
              fontWeight: 700,
              letterSpacing: "0.12em",
              textTransform: "uppercase",
              color: "#64748b",
              userSelect: "none",
            }}
          >
            {header}
          </span>
        ) : (
          <span />
        )}

        {tag && (
          <div
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: 6,
              padding: "3px 10px",
              background: theme.badgeBg,
              border: `1px solid ${theme.border}`,
              borderRadius: 9999,
              fontSize: 10,
              fontWeight: 700,
              letterSpacing: "0.08em",
              textTransform: "uppercase",
              color: theme.badgeText,
              userSelect: "none",
            }}
          >
            <span
              style={{
                width: 6,
                height: 6,
                borderRadius: "50%",
                backgroundColor: theme.dot,
                boxShadow: `0 0 6px ${theme.dot}`,
              }}
            />
            {tag}
          </div>
        )}
      </div>

      {/* Center Section: Dimension Label + Huge Prominent Number */}
      <div>
        <div
          style={{
            fontSize: 12,
            fontWeight: 700,
            letterSpacing: "0.1em",
            textTransform: "uppercase",
            color: "#94a3b8",
            marginBottom: 6,
            userSelect: "none",
          }}
        >
          {label}
        </div>

        <div
          style={{
            fontSize: 48,
            fontWeight: 800,
            lineHeight: 1,
            letterSpacing: "-0.02em",
            color: "#f8fafc",
            fontVariantNumeric: "tabular-nums",
          }}
        >
          {renderedValue}
        </div>
      </div>

      {/* Bottom Citation / Explanation Subtext */}
      {subtext ? (
        <div
          style={{
            fontSize: 11,
            fontWeight: 500,
            color: "#64748b",
            marginTop: 10,
            lineHeight: 1.3,
            userSelect: "none",
          }}
        >
          {subtext}
        </div>
      ) : (
        <div style={{ height: 4 }} />
      )}
    </div>
  );
};
