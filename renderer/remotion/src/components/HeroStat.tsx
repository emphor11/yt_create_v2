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

export const HeroStat: React.FC<ComponentProps> = ({
  runtime,
  instance,
  resolved,
  frame,
}) => {
  const props = resolved.props;
  const label = (props.label as string) || "";
  const displayValue = (props.display_value as string) || "";
  const tag = props.tag as string | undefined;
  const subtext = props.subtext as string | undefined;
  const intent = (props.intent as string) || "neutral";

  // Intent color themes
  const intentThemes: Record<
    string,
    { accent: string; glow: string; badgeBg: string; badgeText: string; dot: string }
  > = {
    danger: {
      accent: "#f43f5e",
      glow: "rgba(244, 63, 94, 0.3)",
      badgeBg: "rgba(244, 63, 94, 0.15)",
      badgeText: "#fb7185",
      dot: "#f43f5e",
    },
    accent: {
      accent: "#38bdf8",
      glow: "rgba(56, 189, 248, 0.3)",
      badgeBg: "rgba(56, 189, 248, 0.15)",
      badgeText: "#38bdf8",
      dot: "#38bdf8",
    },
    success: {
      accent: "#10b981",
      glow: "rgba(16, 185, 129, 0.3)",
      badgeBg: "rgba(16, 185, 129, 0.15)",
      badgeText: "#34d399",
      dot: "#10b981",
    },
    warning: {
      accent: "#fbbf24",
      glow: "rgba(245, 158, 11, 0.3)",
      badgeBg: "rgba(245, 158, 11, 0.15)",
      badgeText: "#fde047",
      dot: "#fbbf24",
    },
    neutral: {
      accent: "#f8fafc",
      glow: "rgba(255, 255, 255, 0.15)",
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

  return (
    <div
      data-visual-component="HeroStat"
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
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        textAlign: "center",
        fontFamily: "Inter, ui-sans-serif, system-ui, sans-serif",
        boxSizing: "border-box",
      }}
    >
      {/* Top Tag/Badge if present */}
      {tag && (
        <div
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: 6,
            padding: "4px 12px",
            background: theme.badgeBg,
            border: `1px solid rgba(255, 255, 255, 0.12)`,
            borderRadius: 9999,
            fontSize: 11,
            fontWeight: 700,
            letterSpacing: "0.1em",
            textTransform: "uppercase",
            color: theme.badgeText,
            marginBottom: 12,
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

      {/* Label */}
      <div
        style={{
          fontSize: 13,
          fontWeight: 700,
          letterSpacing: "0.14em",
          textTransform: "uppercase",
          color: "#94a3b8",
          marginBottom: 8,
          userSelect: "none",
        }}
      >
        {label}
      </div>

      {/* Huge Focal Stat */}
      <div
        style={{
          fontSize: 64,
          fontWeight: 900,
          lineHeight: 1,
          letterSpacing: "-0.03em",
          color: theme.accent,
          textShadow: `0 0 40px ${theme.glow}`,
          fontVariantNumeric: "tabular-nums",
        }}
      >
        {renderedValue}
      </div>

      {/* Subtext Citation */}
      {subtext && (
        <div
          style={{
            fontSize: 12,
            fontWeight: 500,
            color: "#64748b",
            marginTop: 12,
            maxWidth: "80%",
            userSelect: "none",
          }}
        >
          {subtext}
        </div>
      )}
    </div>
  );
};
