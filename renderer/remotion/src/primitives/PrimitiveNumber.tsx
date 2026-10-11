import React from "react";
import { type PrimitiveSpec, type NumberProps } from "./types";
import { evaluateAnimatedProperty } from "./animation";

interface PrimitiveComponentProps {
  spec: PrimitiveSpec<NumberProps>;
  currentFrame: number;
  fps: number;
}

function formatNumber(val: number, precision?: number | null): string {
  if (precision !== undefined && precision !== null) {
    return val.toFixed(precision);
  }
  const isFloat = val % 1 !== 0;
  if (isFloat) {
    return val.toFixed(1);
  }
  return Math.round(val).toLocaleString();
}

export const PrimitiveNumber: React.FC<PrimitiveComponentProps> = ({
  spec,
  currentFrame,
  fps,
}) => {
  const { props, style = {}, animations = [] } = spec;

  const rawValue = evaluateAnimatedProperty(
    "value",
    props.value,
    animations,
    currentFrame,
    fps
  );

  const fill = evaluateAnimatedProperty(
    "style.fill",
    style.fill || "#ffffff",
    animations,
    currentFrame,
    fps
  );

  const fontSize = props.font_size ?? 48;
  const fontWeight = props.font_weight ?? 700;
  const prefix = props.prefix || "";
  const suffix = props.suffix || "";
  const formatted = formatNumber(rawValue, props.precision);

  return (
    <div
      style={{
        color: fill,
        fontSize: `${fontSize}px`,
        fontWeight,
        fontFamily: "Inter, ui-sans-serif, system-ui, sans-serif",
        fontVariantNumeric: props.tabular_nums ? "tabular-nums lining-nums" : "normal",
        display: "inline-flex",
        alignItems: "baseline",
        letterSpacing: "-0.02em",
      }}
    >
      {prefix && (
        <span style={{ fontSize: `${Math.round(fontSize * 0.85)}px`, opacity: 0.85, marginRight: "4px" }}>
          {prefix}
        </span>
      )}
      <span>{formatted}</span>
      {suffix && (
        <span style={{ fontSize: `${Math.round(fontSize * 0.75)}px`, opacity: 0.85, marginLeft: "4px" }}>
          {suffix}
        </span>
      )}
    </div>
  );
};
