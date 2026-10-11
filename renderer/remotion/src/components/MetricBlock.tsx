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

function formatDigits(val: number): string {
  const isFloat = val % 1 !== 0;
  if (isFloat) {
    return val.toFixed(1);
  }
  return Math.round(val).toLocaleString();
}

export const MetricBlock: React.FC<ComponentProps> = ({
  runtime,
  instance,
  resolved,
  frame,
}) => {
  const props = resolved.props;
  const qualifier = props.qualifier as string | undefined;
  const prefix = props.prefix as string | undefined;
  const unit = props.unit as string | undefined;
  const label = (props.label as string) || "";
  const subtext = props.subtext as string | undefined;
  const emphasis = (props.emphasis as string) || "standard";

  // Check if a dynamic counter value was resolved by FrameResolver
  let numericValue: number | undefined;
  if (typeof props.value === "number") {
    numericValue = props.value;
  } else if (typeof props.raw_value === "number") {
    numericValue = props.raw_value;
  }

  if (numericValue !== undefined) {
    const enterFrame = runtime.getEntranceFrame(instance.object_id);
    const countDuration = 25;
    const elapsed = Math.max(0, frame - enterFrame);
    const countProgress = Math.min(1, Math.max(0, elapsed / countDuration));
    const easedProgress = 1 - Math.pow(1 - countProgress, 3);
    const startVal = typeof props.start_value === "number" ? props.start_value : 0;
    const targetVal = numericValue;
    numericValue = startVal + (targetVal - startVal) * easedProgress;
  }

  // Authoritative display text fallback if no numeric counter is used
  const displayValue = (props.display_value as string) || "";

  // Sizing tiers
  const fontSizes = {
    hero: { num: 56, unit: 24, label: 12 },
    standard: { num: 44, unit: 20, label: 11 },
    compact: { num: 32, unit: 16, label: 10 },
    danger: { num: 44, unit: 20, label: 11 },
    positive: { num: 44, unit: 20, label: 11 },
    secondary: { num: 36, unit: 18, label: 11 },
    supporting: { num: 32, unit: 16, label: 10 },
  }[emphasis] || { num: 44, unit: 20, label: 11 };

  const numColor = resolved.style.fill || "#f8fafc";

  return (
    <div
      data-visual-component="MetricBlock"
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
        justifyContent: "center",
        fontFamily: "Inter, ui-sans-serif, system-ui, sans-serif",
        boxSizing: "border-box",
      }}
    >
      {/* Category / Dimension Label */}
      <div
        style={{
          fontSize: fontSizes.label,
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

      {/* Main Quantitative Number Row */}
      <div
        style={{
          display: "inline-flex",
          alignItems: "baseline",
          lineHeight: 1,
        }}
      >
        {/* Fixed Verbatim Qualifier (e.g. '>', '<') */}
        {qualifier && (
          <span
            style={{
              fontSize: fontSizes.num * 0.75,
              fontWeight: 500,
              color: "#94a3b8",
              marginRight: 4,
              userSelect: "none",
            }}
          >
            {qualifier}
          </span>
        )}

        {/* Currency or Symbol Prefix */}
        {prefix && (
          <span
            style={{
              fontSize: fontSizes.unit,
              fontWeight: 600,
              color: "#cbd5e1",
              marginRight: 2,
            }}
          >
            {prefix}
          </span>
        )}

        {/* Formatted Number or Authoritative String */}
        <span
          style={{
            fontSize: fontSizes.num,
            fontWeight: 800,
            letterSpacing: "-0.02em",
            color: numColor,
            fontVariantNumeric: "tabular-nums lining-nums",
          }}
        >
          {numericValue !== undefined ? formatDigits(numericValue) : displayValue.replace(/^[><~]/, "")}
        </span>

        {/* Unit / Suffix (e.g. '%', 'LPA') */}
        {unit && (
          <span
            style={{
              fontSize: fontSizes.unit,
              fontWeight: 600,
              color: "#94a3b8",
              marginLeft: 6,
              letterSpacing: "-0.01em",
            }}
          >
            {unit}
          </span>
        )}
      </div>

      {/* Proof / Citation / Subtext Row */}
      {subtext && (
        <div
          style={{
            fontSize: 11,
            fontWeight: 500,
            color: "#64748b",
            marginTop: 8,
            display: "flex",
            alignItems: "center",
            gap: 6,
          }}
        >
          <span
            style={{
              display: "inline-block",
              width: 4,
              height: 4,
              borderRadius: "50%",
              backgroundColor: "#475569",
            }}
          />
          <span>{subtext}</span>
        </div>
      )}
    </div>
  );
};
