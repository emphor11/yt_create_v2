import React from "react";
import { NumberProps } from "../types";
import { handDrawn } from "../hand-drawn-theme.ts";

export interface NumberComponentProps {
  props: NumberProps;
  currentDisplayValue?: string;
  currentValue?: number;
  width?: number;
  height?: number;
  layout?: string;
  style?: React.CSSProperties;
}

function formatINR(val: number): string {
  const rounded = Math.round(val);
  return `₹${rounded.toLocaleString("en-IN")}`;
}

function formatPercentage(val: number, decimals: number = 1): string {
  return `${val.toFixed(decimals)}%`;
}

export const NumberPrimitive: React.FC<NumberComponentProps> = ({
  props,
  currentDisplayValue,
  currentValue,
  width,
  height,
  layout,
  style,
}) => {
  const displayToUse = currentDisplayValue || props.displayValue;
  const val = currentValue !== undefined ? currentValue : props.value;

  let formatted = "";
  if (displayToUse) {
    formatted = displayToUse;
  } else if (val !== undefined && val !== null && !isNaN(val)) {
    if (props.format === "currency_inr") {
      formatted = formatINR(val);
    } else if (props.format === "percentage") {
      formatted = formatPercentage(val, props.decimals ?? 1);
    } else {
      formatted = Number.isInteger(val) ? val.toLocaleString() : val.toString();
    }
  } else {
    formatted = "";
  }

  if (!displayToUse && formatted) {
    if (props.prefix) formatted = `${props.prefix}${formatted}`;
    if (props.suffix) formatted = `${formatted}${props.suffix}`;
  }

  // Dynamic responsive font sizing based on character length, layout context, and container dimensions
  const len = formatted.length;
  const isCenterHero = layout === "center" || (width ?? 360) >= 600;
  const isCompact = (width ?? 360) <= 320 || (height ?? 180) <= 140;
  let fontSize = 54;
  if (isCenterHero) {
    if (len > 18) {
      fontSize = 58;
    } else if (len > 14) {
      fontSize = 70;
    } else if (len > 10) {
      fontSize = 82;
    } else if (len > 6) {
      fontSize = 94;
    } else {
      fontSize = 106;
    }
  } else {
    if (len > 18) {
      fontSize = isCompact ? 28 : 34;
    } else if (len > 14) {
      fontSize = isCompact ? 34 : 40;
    } else if (len > 10) {
      fontSize = isCompact ? 40 : 46;
    } else if (len > 6) {
      fontSize = isCompact ? 44 : 50;
    } else {
      fontSize = isCompact ? 48 : 56;
    }
  }

  const underlineWidth = Math.min(90, Math.max(48, len * 5.4));

  return (
    <div
      style={{
        position: "relative",
        display: "inline-block",
        fontFamily: handDrawn.font.display,
        fontSize,
        fontWeight: 800,
        color: handDrawn.colors.ink,
        letterSpacing: "-0.03em",
        lineHeight: 1.1,
        fontVariantNumeric: "tabular-nums",
        whiteSpace: "nowrap",
        ...style,
      }}
    >
      {formatted}
      <div
        aria-hidden="true"
        style={{
          height: Math.max(4, Math.round(fontSize * 0.1)),
          width: `${underlineWidth}%`,
          marginTop: 5,
          borderRadius: handDrawn.radius.pill,
          backgroundColor: handDrawn.colors.coral,
          transform: "rotate(-1.5deg)",
          opacity: 0.8,
        }}
      />
    </div>
  );
};
