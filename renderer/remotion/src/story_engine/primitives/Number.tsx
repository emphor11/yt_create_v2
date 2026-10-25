import React from "react";
import { NumberProps } from "../types";
import { handDrawn } from "../hand-drawn-theme.ts";

interface NumberComponentProps {
  props: NumberProps;
  currentDisplayValue?: string;
  currentValue?: number;
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

  return (
    <div
      style={{
        position: "relative",
        display: "inline-block",
        fontFamily: handDrawn.font.display,
        fontSize: 54,
        fontWeight: 800,
        color: handDrawn.colors.ink,
        letterSpacing: "-0.03em",
        lineHeight: 1.1,
        fontVariantNumeric: "tabular-nums",
        ...style,
      }}
    >
      {formatted}
      <div
        aria-hidden="true"
        style={{
          height: 6,
          width: "68%",
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
