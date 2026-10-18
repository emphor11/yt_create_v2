import React from "react";
import type { CardProps, VisualStateKind, StampProps } from "../types.ts";
import { tokens } from "../../design-tokens.ts";

interface CardComponentProps {
  props: CardProps;
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
    str = Math.round(val).toLocaleString();
  }
  if (prefix) str = `${prefix}${str}`;
  if (suffix) str = `${str}${suffix}`;
  return str;
}

export const Card: React.FC<CardComponentProps> = ({
  props,
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

  let accentColor = customAccent || props.accentColor || tokens.accent.primary;
  let borderColor = tokens.bg.border;
  let glowStyle = "0 20px 40px -15px rgba(0, 0, 0, 0.5)";
  let filterStyle: string | undefined = undefined;
  let borderStyle = "solid";

  if (activeVisualState === "danger") {
    accentColor = "#EF4444";
    borderColor = "#EF4444";
    glowStyle = "0 0 32px 4px rgba(239, 68, 68, 0.45), 0 20px 40px -15px rgba(0, 0, 0, 0.6)";
  } else if (activeVisualState === "warning") {
    accentColor = "#F59E0B";
    borderColor = "#F59E0B";
    glowStyle = "0 0 25px 2px rgba(245, 158, 11, 0.35), 0 20px 40px -15px rgba(0, 0, 0, 0.6)";
  } else if (activeVisualState === "success") {
    accentColor = "#10B981";
    borderColor = "#10B981";
    glowStyle = "0 0 28px 3px rgba(16, 185, 129, 0.4), 0 20px 40px -15px rgba(0, 0, 0, 0.6)";
  } else if (activeVisualState === "dimmed") {
    filterStyle = "grayscale(75%) contrast(0.85)";
  } else if (activeVisualState === "eroded") {
    borderColor = "rgba(239, 68, 68, 0.8)";
    borderStyle = "dashed";
    glowStyle = "0 0 20px rgba(239, 68, 68, 0.25)";
  }

  // Value resolution for atomic card
  const valToDisplay = currentValue !== undefined ? currentValue : props.value;
  const hasValue = valToDisplay !== undefined;
  const formattedValue = hasValue
    ? formatValue(
        valToDisplay,
        props.format ?? "currency_inr",
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
        backgroundColor: tokens.bg.surface,
        border: `1.5px ${borderStyle} ${borderColor}`,
        borderRadius: tokens.radius.card,
        padding: "26px 30px",
        boxShadow: glowStyle,
        backdropFilter: "blur(12px)",
        boxSizing: "border-box",
        overflow: "hidden",
        fontFamily: tokens.font.family,
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
          height: 4,
          backgroundColor: accentColor,
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
            borderRadius: 6,
            backgroundColor: `${accentColor}26`,
            border: `1px solid ${accentColor}`,
            color: accentColor,
            fontFamily: tokens.font.family,
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
            fontFamily: tokens.font.family,
            fontSize: 18,
            fontWeight: 900,
            letterSpacing: "0.15em",
            textTransform: "uppercase",
            backgroundColor: "rgba(0, 0, 0, 0.35)",
            boxShadow: `0 0 15px ${stamp.color || "#EF4444"}44`,
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
            color: tokens.text.secondary,
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
              fontFamily: tokens.font.family,
              fontSize: 50,
              fontWeight: 800,
              color: tokens.text.primary,
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
            color: tokens.text.muted,
            marginTop: 6,
            zIndex: 2,
            whiteSpace: "nowrap",
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
