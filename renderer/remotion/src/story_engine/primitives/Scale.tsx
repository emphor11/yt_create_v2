import React from "react";
import { useCurrentFrame, spring } from "remotion";
import type { ScaleProps, VisualStateKind } from "../types.ts";
import { handDrawn } from "../hand-drawn-theme.ts";

export interface ScalePrimitiveProps {
  props: ScaleProps;
  visualState?: VisualStateKind;
  badge?: string;
  customAccent?: string;
  width?: number;
  height?: number;
  layout?: string;
  style?: React.CSSProperties;
}

export const ScalePrimitive: React.FC<ScalePrimitiveProps> = ({
  props,
  visualState,
  badge,
  customAccent,
  width,
  height,
  style,
}) => {
  const frame = useCurrentFrame();
  const boxW = width ?? 680;
  const boxH = height ?? 380;

  const activeVisualState = visualState || props.visualState || "normal";
  const leftVal = props.leftNumericValue ?? 1;
  const rightVal = props.rightNumericValue ?? 1;

  // Resolve target tilt angle based on explicit direction or relative values
  let targetAngleDeg = 0;
  if (props.tiltDirection === "left") {
    targetAngleDeg = -14;
  } else if (props.tiltDirection === "right") {
    targetAngleDeg = 14;
  } else if (props.tiltDirection === "balanced") {
    targetAngleDeg = 0;
  } else {
    const diff = rightVal - leftVal;
    const maxVal = Math.max(Math.abs(leftVal), Math.abs(rightVal), 1);
    const ratio = Math.max(-1, Math.min(1, diff / maxVal));
    targetAngleDeg = Math.round(ratio * 14);
  }

  // Smooth mechanical spring physics with authentic overshoot & wobble
  const springProgress = spring({
    frame,
    fps: 30,
    config: {
      damping: 14,
      mass: 1.6,
      stiffness: 75,
    },
  });

  const currentAngleDeg = targetAngleDeg * springProgress;
  const angleRad = (currentAngleDeg * Math.PI) / 180;

  // Geometry dimensions
  const centerX = boxW / 2;
  const pivotY = boxH * 0.30;
  const beamHalfLength = Math.min(boxW * 0.36, 240);
  const chainLength = Math.min(boxH * 0.22, 90);
  const panWidth = Math.min(boxW * 0.32, 210);
  const panHeight = Math.min(boxH * 0.28, 110);

  // Left & right beam endpoints
  const leftX = centerX - Math.cos(angleRad) * beamHalfLength;
  const leftY = pivotY - Math.sin(angleRad) * beamHalfLength;

  const rightX = centerX + Math.cos(angleRad) * beamHalfLength;
  const rightY = pivotY + Math.sin(angleRad) * beamHalfLength;

  // Pan positions (chains hang vertically under gravity)
  const leftPanX = leftX;
  const leftPanY = leftY + chainLength;

  const rightPanX = rightX;
  const rightPanY = rightY + chainLength;

  // Colors based on state
  const isDanger = activeVisualState === "danger" || Math.abs(currentAngleDeg) >= 10;
  const accentColor = customAccent || props.accentColor || (isDanger ? handDrawn.colors.red : handDrawn.colors.ink);

  return (
    <div
      style={{
        position: "relative",
        width: boxW,
        height: boxH,
        backgroundColor: handDrawn.colors.paperAlt,
        borderRadius: handDrawn.radius.card,
        border: `2px solid ${isDanger ? handDrawn.colors.red : handDrawn.colors.ink}`,
        boxShadow: isDanger
          ? `4px 5px 0 ${handDrawn.colors.coralSoft}, ${handDrawn.shadow.paper}`
          : handDrawn.shadow.paper,
        boxSizing: "border-box",
        overflow: "hidden",
        fontFamily: handDrawn.font.body,
        ...style,
      }}
    >
      {/* Top Accent Strip */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          right: 0,
          height: 6,
          backgroundColor: isDanger ? handDrawn.colors.red : "#3B82F6",
        }}
      />

      {/* Header / Title */}
      {props.title && (
        <div
          style={{
            position: "absolute",
            top: 14,
            left: 20,
            fontSize: 14,
            fontWeight: 800,
            fontFamily: handDrawn.font.label,
            color: handDrawn.colors.inkMuted,
            letterSpacing: "0.08em",
            textTransform: "uppercase",
            zIndex: 4,
          }}
        >
          {props.title}
        </div>
      )}

      {/* Dynamic Status Badge */}
      {(badge || (Math.abs(currentAngleDeg) >= 8 && "IMBALANCE ALERT")) && (
        <div
          style={{
            position: "absolute",
            top: 12,
            right: 18,
            padding: "3px 10px",
            borderRadius: handDrawn.radius.pill,
            backgroundColor: handDrawn.colors.paper,
            border: `1.5px solid ${isDanger ? handDrawn.colors.red : handDrawn.colors.amber}`,
            color: isDanger ? handDrawn.colors.red : handDrawn.colors.amber,
            fontFamily: handDrawn.font.label,
            fontSize: 11,
            fontWeight: 800,
            letterSpacing: "0.06em",
            textTransform: "uppercase",
            zIndex: 4,
          }}
        >
          {badge || "IMBALANCE ALERT"}
        </div>
      )}

      {/* SVG Mechanical Rig (Pillar, Fulcrum, Crossbeam, Chains) */}
      <svg
        width={boxW}
        height={boxH}
        style={{ position: "absolute", inset: 0, pointerEvents: "none", zIndex: 2 }}
      >
        {/* Base Pillar */}
        <line
          x1={centerX}
          y1={pivotY}
          x2={centerX}
          y2={boxH - 30}
          stroke={handDrawn.colors.ink}
          strokeWidth={4}
          strokeLinecap="round"
        />

        {/* Pillar Pedestal */}
        <polygon
          points={`
            ${centerX - 40},${boxH - 24}
            ${centerX + 40},${boxH - 24}
            ${centerX + 26},${boxH - 36}
            ${centerX - 26},${boxH - 36}
          `}
          fill={handDrawn.colors.paper}
          stroke={handDrawn.colors.ink}
          strokeWidth={2.5}
        />

        {/* Central Fulcrum Triangular Cap */}
        <polygon
          points={`
            ${centerX},${pivotY - 14}
            ${centerX - 16},${pivotY + 12}
            ${centerX + 16},${pivotY + 12}
          `}
          fill={handDrawn.colors.paperAlt}
          stroke={handDrawn.colors.ink}
          strokeWidth={2.5}
        />

        {/* Balance Crossbeam */}
        <line
          x1={leftX}
          y1={leftY}
          x2={rightX}
          y2={rightY}
          stroke={accentColor}
          strokeWidth={5}
          strokeLinecap="round"
        />

        {/* Center Pivot Pin */}
        <circle cx={centerX} cy={pivotY} r={6} fill={accentColor} stroke={handDrawn.colors.ink} strokeWidth={2} />

        {/* Left Beam Tip Ring */}
        <circle cx={leftX} cy={leftY} r={4.5} fill={handDrawn.colors.paper} stroke={handDrawn.colors.ink} strokeWidth={2} />

        {/* Right Beam Tip Ring */}
        <circle cx={rightX} cy={rightY} r={4.5} fill={handDrawn.colors.paper} stroke={handDrawn.colors.ink} strokeWidth={2} />

        {/* Left Suspended Chains */}
        <line
          x1={leftX}
          y1={leftY}
          x2={leftPanX - panWidth * 0.38}
          y2={leftPanY}
          stroke={handDrawn.colors.inkMuted}
          strokeWidth={1.8}
          strokeDasharray="3 3"
        />
        <line
          x1={leftX}
          y1={leftY}
          x2={leftPanX + panWidth * 0.38}
          y2={leftPanY}
          stroke={handDrawn.colors.inkMuted}
          strokeWidth={1.8}
          strokeDasharray="3 3"
        />

        {/* Right Suspended Chains */}
        <line
          x1={rightX}
          y1={rightY}
          x2={rightPanX - panWidth * 0.38}
          y2={rightPanY}
          stroke={handDrawn.colors.inkMuted}
          strokeWidth={1.8}
          strokeDasharray="3 3"
        />
        <line
          x1={rightX}
          y1={rightY}
          x2={rightPanX + panWidth * 0.38}
          y2={rightPanY}
          stroke={handDrawn.colors.inkMuted}
          strokeWidth={1.8}
          strokeDasharray="3 3"
        />
      </svg>

      {/* LEFT PAN CONTAINER */}
      <div
        style={{
          position: "absolute",
          left: leftPanX - panWidth / 2,
          top: leftPanY,
          width: panWidth,
          height: panHeight,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "8px 12px",
          backgroundColor: handDrawn.colors.paper,
          border: `2px solid ${handDrawn.colors.ink}`,
          borderRadius: 12,
          boxShadow: "0 4px 10px rgba(0,0,0,0.06)",
          boxSizing: "border-box",
          zIndex: 3,
        }}
      >
        <div
          style={{
            fontSize: 12,
            fontWeight: 800,
            fontFamily: handDrawn.font.label,
            color: handDrawn.colors.inkMuted,
            textTransform: "uppercase",
            letterSpacing: "0.05em",
            textAlign: "center",
            whiteSpace: "nowrap",
            overflow: "hidden",
            textOverflow: "ellipsis",
            width: "100%",
          }}
        >
          {props.leftTitle}
        </div>

        <div
          style={{
            fontSize: panWidth <= 160 ? 20 : 26,
            fontWeight: 800,
            fontFamily: handDrawn.font.display,
            color: handDrawn.colors.ink,
            letterSpacing: "-0.02em",
            lineHeight: 1.1,
            fontVariantNumeric: "tabular-nums",
          }}
        >
          {props.leftDisplayValue || (props.leftNumericValue !== undefined ? String(props.leftNumericValue) : "")}
        </div>

        {props.leftBadge && (
          <div
            style={{
              fontSize: 10,
              fontWeight: 800,
              padding: "1px 6px",
              borderRadius: 6,
              backgroundColor: handDrawn.colors.paperAlt,
              border: `1px solid ${handDrawn.colors.inkMuted}`,
              color: handDrawn.colors.ink,
            }}
          >
            {props.leftBadge}
          </div>
        )}
      </div>

      {/* RIGHT PAN CONTAINER */}
      <div
        style={{
          position: "absolute",
          left: rightPanX - panWidth / 2,
          top: rightPanY,
          width: panWidth,
          height: panHeight,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "8px 12px",
          backgroundColor: handDrawn.colors.paper,
          border: `2px solid ${isDanger ? handDrawn.colors.red : handDrawn.colors.ink}`,
          borderRadius: 12,
          boxShadow: isDanger
            ? `0 4px 12px ${handDrawn.colors.coralSoft}`
            : "0 4px 10px rgba(0,0,0,0.06)",
          boxSizing: "border-box",
          zIndex: 3,
        }}
      >
        <div
          style={{
            fontSize: 12,
            fontWeight: 800,
            fontFamily: handDrawn.font.label,
            color: isDanger ? handDrawn.colors.red : handDrawn.colors.inkMuted,
            textTransform: "uppercase",
            letterSpacing: "0.05em",
            textAlign: "center",
            whiteSpace: "nowrap",
            overflow: "hidden",
            textOverflow: "ellipsis",
            width: "100%",
          }}
        >
          {props.rightTitle}
        </div>

        <div
          style={{
            fontSize: panWidth <= 160 ? 20 : 26,
            fontWeight: 800,
            fontFamily: handDrawn.font.display,
            color: isDanger ? handDrawn.colors.red : handDrawn.colors.ink,
            letterSpacing: "-0.02em",
            lineHeight: 1.1,
            fontVariantNumeric: "tabular-nums",
          }}
        >
          {props.rightDisplayValue || (props.rightNumericValue !== undefined ? String(props.rightNumericValue) : "")}
        </div>

        {props.rightBadge && (
          <div
            style={{
              fontSize: 10,
              fontWeight: 800,
              padding: "1px 6px",
              borderRadius: 6,
              backgroundColor: isDanger ? handDrawn.colors.coralSoft : handDrawn.colors.paperAlt,
              border: `1px solid ${isDanger ? handDrawn.colors.red : handDrawn.colors.inkMuted}`,
              color: isDanger ? handDrawn.colors.red : handDrawn.colors.ink,
            }}
          >
            {props.rightBadge}
          </div>
        )}
      </div>
    </div>
  );
};
