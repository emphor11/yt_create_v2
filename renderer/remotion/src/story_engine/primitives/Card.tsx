import React from "react";
import type { CardProps, VisualStateKind, StampProps } from "../types.ts";
import { handDrawn, handDrawnAccent } from "../hand-drawn-theme.ts";

interface CardComponentProps {
  props: CardProps;
  currentDisplayValue?: string;
  currentValue?: number;
  currentSubtitle?: string;
  visualState?: VisualStateKind;
  badge?: string;
  stamp?: StampProps;
  customAccent?: string;
  style?: React.CSSProperties;
}

function formatINR(val: number): string {
  const rounded = Math.round(val);
  return `₹${rounded.toLocaleString("en-IN")}`;
}

function formatPercentage(val: number, decimals: number = 1): string {
  return `${val.toFixed(decimals)}%`;
}

function formatValue(
  val: number,
  fmt: "currency_inr" | "percentage" | "plain" = "currency_inr",
  decimals: number = 1,
  prefix?: string,
  suffix?: string
): string {
  let str = "";
  if (fmt === "currency_inr") {
    str = formatINR(val);
  } else if (fmt === "percentage") {
    str = formatPercentage(val, decimals);
  } else {
    str = Number.isInteger(val) ? val.toLocaleString() : val.toString();
  }
  if (prefix) str = `${prefix}${str}`;
  if (suffix) str = `${str}${suffix}`;
  return str;
}

export const Card: React.FC<CardComponentProps> = ({
  props,
  currentDisplayValue,
  currentValue,
  currentSubtitle,
  visualState: dynamicVisualState,
  badge: dynamicBadge,
  stamp,
  customAccent,
  style,
}) => {
  const activeVisualState = dynamicVisualState || props.visualState || "normal";
  const activeBadge = dynamicBadge || props.badge;
  const activeSubtitle = currentSubtitle || props.subtitle;

  let accentColor: string = handDrawnAccent(activeVisualState, customAccent || props.accentColor);
  let borderColor: string = handDrawn.colors.ink;
  let glowStyle: string = handDrawn.shadow.paper;
  let filterStyle: string | undefined = undefined;
  let borderStyle = "solid";

  if (activeVisualState === "danger") {
    accentColor = handDrawn.colors.red;
    borderColor = handDrawn.colors.red;
    glowStyle = `4px 5px 0 ${handDrawn.colors.coralSoft}, ${handDrawn.shadow.paper}`;
  } else if (activeVisualState === "warning") {
    accentColor = handDrawn.colors.amber;
    borderColor = handDrawn.colors.amber;
    glowStyle = `4px 5px 0 ${handDrawn.colors.amberSoft}, ${handDrawn.shadow.paper}`;
  } else if (activeVisualState === "success") {
    accentColor = handDrawn.colors.green;
    borderColor = handDrawn.colors.green;
    glowStyle = `4px 5px 0 #CBE6D1, ${handDrawn.shadow.paper}`;
  } else if (activeVisualState === "dimmed") {
    filterStyle = "grayscale(75%) contrast(0.85)";
  } else if (activeVisualState === "eroded") {
    borderColor = handDrawn.colors.red;
    borderStyle = "dashed";
    glowStyle = handDrawn.shadow.paper;
  }

  // Value resolution for atomic card
  const displayToUse = currentDisplayValue || props.displayValue;
  const valToDisplay = currentValue !== undefined ? currentValue : props.value;
  const hasValue = Boolean(displayToUse) || (valToDisplay !== undefined && valToDisplay !== null);

  const formattedValue = displayToUse
    ? displayToUse
    : (valToDisplay !== undefined && valToDisplay !== null)
    ? formatValue(
        valToDisplay,
        props.format ?? "plain",
        props.decimals ?? 1,
        props.prefix,
        props.suffix
      )
    : "";

  return (
    <div
      style={{
        position: "relative",
        display: "flex",
        flexDirection: "column",
        justifyContent: "space-between",
        backgroundColor: handDrawn.colors.paperAlt,
        border: `${activeVisualState === "normal" ? 2 : 2.5}px ${borderStyle} ${borderColor}`,
        borderRadius: handDrawn.radius.card,
        padding: "26px 30px",
        boxShadow: glowStyle,
        boxSizing: "border-box",
        overflow: "hidden",
        fontFamily: handDrawn.font.body,
        filter: filterStyle,
        transition: "border 0.3s ease, box-shadow 0.3s ease",
        ...style,
      }}
    >
      {/* Accent top indicator strip */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          right: 0,
          height: 8,
          backgroundColor: accentColor,
          opacity: 0.92,
        }}
      />

      {/* Dynamic Status Badge (e.g. "BURDEN SURGE", "30% SURCHARGE") */}
      {activeBadge && (
        <div
          style={{
            position: "absolute",
            top: 16,
            right: 20,
            padding: "4px 10px",
            borderRadius: handDrawn.radius.pill,
            backgroundColor: handDrawn.colors.paper,
            border: `1px solid ${accentColor}`,
            color: accentColor,
            fontFamily: handDrawn.font.label,
            fontSize: 11,
            fontWeight: 700,
            letterSpacing: "0.06em",
            textTransform: "uppercase",
            zIndex: 4,
          }}
        >
          {activeBadge}
        </div>
      )}

      {/* Dynamic Rubber Stamp Overlay */}
      {stamp && (
        <div
          style={{
            position: "absolute",
            top: "30%",
            right: "12%",
            transform: `rotate(${stamp.angle ?? -14}deg)`,
            border: `3px solid ${stamp.color || "#EF4444"}`,
            borderRadius: 8,
            padding: "6px 14px",
            color: stamp.color || "#EF4444",
            fontFamily: handDrawn.font.label,
            fontSize: 18,
            fontWeight: 900,
            letterSpacing: "0.15em",
            textTransform: "uppercase",
            backgroundColor: handDrawn.colors.paperAlt,
            boxShadow: handDrawn.shadow.paper,
            zIndex: 10,
            pointerEvents: "none",
          }}
        >
          {stamp.text}
        </div>
      )}

      {/* Header / Title */}
      {props.title && (
        <div
          style={{
            fontSize: 17,
            fontWeight: 600,
            color: handDrawn.colors.inkMuted,
            letterSpacing: "0.05em",
            textTransform: "uppercase",
            marginBottom: 8,
            paddingRight: activeBadge ? 90 : 0,
            whiteSpace: "nowrap",
            overflow: "hidden",
            textOverflow: "ellipsis",
          }}
        >
          {props.title}
        </div>
      )}

      {/* Card Content (Direct Numeric Value + Children) */}
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          gap: 6,
          flex: 1,
          justifyContent: "center",
          zIndex: 2,
        }}
      >
        {hasValue && (
          <div
            style={{
              fontFamily: handDrawn.font.display,
              fontSize: 50,
              fontWeight: 800,
            color: handDrawn.colors.ink,
              letterSpacing: "-0.03em",
              lineHeight: 1.1,
              fontVariantNumeric: "tabular-nums",
            }}
          >
            {formattedValue}
          </div>
        )}
      </div>

      {/* Subtitle / Context Label */}
      {activeSubtitle && (
        <div
          style={{
            fontSize: 14,
              color: handDrawn.colors.inkMuted,
            marginTop: 6,
            zIndex: 2,
            lineHeight: 1.35,
            display: "-webkit-box",
            WebkitLineClamp: 2,
            WebkitBoxOrient: "vertical",
            overflow: "hidden",
            textOverflow: "ellipsis",
          }}
        >
          {activeSubtitle}
        </div>
      )}
    </div>
  );
};
