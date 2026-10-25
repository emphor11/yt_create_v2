import React from "react";
import type { CardProps, VisualStateKind, StampProps } from "../types.ts";
import { handDrawn, handDrawnAccent } from "../hand-drawn-theme.ts";

export interface CardComponentProps {
  props: CardProps;
  currentDisplayValue?: string;
  currentValue?: number;
  currentSubtitle?: string;
  visualState?: VisualStateKind;
  badge?: string;
  stamp?: StampProps;
  customAccent?: string;
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
  width,
  height,
  layout,
  style,
}) => {
  const activeVisualState = dynamicVisualState || props.visualState || "normal";
  const activeBadge = dynamicBadge || props.badge;
  const activeSubtitle = currentSubtitle || props.subtitle;

  const cardW = width ?? 420;
  const cardH = height ?? 240;
  const isCenter = layout === "center" || cardW >= 700;
  const isWide = cardW >= 480 && !isCenter;
  const isCompact = cardW <= 380 || cardH <= 210;

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

  // Dynamic responsive typography scaling based on string length, layout context, and container size
  const valLen = formattedValue.length;
  let valFontSize = 50;
  if (isCenter) {
    if (valLen > 18) {
      valFontSize = 38;
    } else if (valLen > 14) {
      valFontSize = 48;
    } else if (valLen > 10) {
      valFontSize = 60;
    } else if (valLen > 6) {
      valFontSize = 70;
    } else {
      valFontSize = 80;
    }
  } else if (isWide) {
    if (valLen > 18) {
      valFontSize = 32;
    } else if (valLen > 14) {
      valFontSize = 38;
    } else if (valLen > 10) {
      valFontSize = 48;
    } else if (valLen > 6) {
      valFontSize = 58;
    } else {
      valFontSize = 66;
    }
  } else {
    if (valLen > 18) {
      valFontSize = isCompact ? 24 : 30;
    } else if (valLen > 14) {
      valFontSize = isCompact ? 28 : 34;
    } else if (valLen > 10) {
      valFontSize = isCompact ? 34 : 40;
    } else if (valLen > 6) {
      valFontSize = isCompact ? 40 : 46;
    } else {
      valFontSize = isCompact ? 44 : 50;
    }
  }

  const titleFontSize = isCenter ? 20 : isCompact ? 13 : isWide ? 17 : 15;
  const subtitleFontSize = isCenter ? 17 : isCompact ? 12 : isWide ? 15 : 14;
  const paddingStyle = isCenter ? "32px 38px" : isCompact ? "16px 20px" : isWide ? "24px 30px" : "20px 24px";
  const badgeRightReserve = activeBadge ? (isCenter ? 110 : isCompact ? 76 : 94) : 0;

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
        padding: paddingStyle,
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
          height: isCompact ? 5 : 7,
          backgroundColor: accentColor,
          opacity: 0.92,
        }}
      />

      {/* Dynamic Status Badge (e.g. "BURDEN SURGE", "30% SURCHARGE") */}
      {activeBadge && (
        <div
          style={{
            position: "absolute",
            top: isCompact ? 12 : 16,
            right: isCompact ? 14 : 20,
            padding: isCompact ? "2px 7px" : "4px 10px",
            borderRadius: handDrawn.radius.pill,
            backgroundColor: handDrawn.colors.paper,
            border: `1px solid ${accentColor}`,
            color: accentColor,
            fontFamily: handDrawn.font.label,
            fontSize: isCompact ? 10 : 11,
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
            top: "28%",
            right: "10%",
            transform: `rotate(${stamp.angle ?? -14}deg)`,
            border: `3px solid ${stamp.color || "#EF4444"}`,
            borderRadius: 8,
            padding: isCompact ? "4px 10px" : "6px 14px",
            color: stamp.color || "#EF4444",
            fontFamily: handDrawn.font.label,
            fontSize: isCompact ? 14 : 18,
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
            fontSize: titleFontSize,
            fontWeight: 700,
            color: handDrawn.colors.inkMuted,
            letterSpacing: "0.05em",
            textTransform: "uppercase",
            marginBottom: 6,
            paddingRight: badgeRightReserve,
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
          gap: 4,
          flex: 1,
          justifyContent: "center",
          zIndex: 2,
          minHeight: 0,
        }}
      >
        {hasValue && (
          <div
            style={{
              fontFamily: handDrawn.font.display,
              fontSize: valFontSize,
              fontWeight: 800,
              color: handDrawn.colors.ink,
              letterSpacing: "-0.03em",
              lineHeight: 1.1,
              fontVariantNumeric: "tabular-nums",
              whiteSpace: "nowrap",
              overflow: "hidden",
              textOverflow: "ellipsis",
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
            fontSize: subtitleFontSize,
            color: handDrawn.colors.inkMuted,
            marginTop: 4,
            zIndex: 2,
            lineHeight: 1.3,
            display: "-webkit-box",
            WebkitLineClamp: isCompact ? 1 : 2,
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
