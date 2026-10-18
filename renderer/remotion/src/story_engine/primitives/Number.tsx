import React from "react";
import { NumberProps } from "../types";
import { tokens } from "../../design-tokens";

interface NumberComponentProps {
  props: NumberProps;
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
  currentValue,
  style,
}) => {
  const val = currentValue !== undefined ? currentValue : props.value;

  let formatted = "";
  if (props.format === "currency_inr") {
    formatted = formatINR(val);
  } else if (props.format === "percentage") {
    formatted = formatPercentage(val, props.decimals ?? 1);
  } else {
    formatted = Math.round(val).toLocaleString();
  }

  if (props.prefix) formatted = `${props.prefix}${formatted}`;
  if (props.suffix) formatted = `${formatted}${props.suffix}`;

  return (
    <div
      style={{
        fontFamily: tokens.font.family,
        fontSize: 54,
        fontWeight: 800,
        color: tokens.text.primary,
        letterSpacing: "-0.03em",
        lineHeight: 1.1,
        fontVariantNumeric: "tabular-nums",
        ...style,
      }}
    >
      {formatted}
    </div>
  );
};
