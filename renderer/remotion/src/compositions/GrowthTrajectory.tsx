import React from 'react';
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { tokens } from '../design-tokens';
import { GrowthTrajectoryProps } from '../types';
import { safeAnimationWindow, safeSpringDelay } from '../animation-safety';

// ---------------------------------------------------------------------------
// Atmospheric Editorial Backdrop (Zero Dashboard Clutter)
// ---------------------------------------------------------------------------

interface EditorialBackdropProps {
  accentColorRgb: string;
}

function EditorialBackdrop({ accentColorRgb }: EditorialBackdropProps) {
  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#060911",
        overflow: "hidden",
        pointerEvents: "none",
        zIndex: 0,
      }}
    >
      {/* Deep Multi-stop Obsidian Vignette */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: "radial-gradient(ellipse 95% 75% at 50% 46%, #0b1222 0%, #060913 65%, #020408 100%)",
        }}
      />

      {/* Atmospheric Soft Radiant Bloom behind the destination apex */}
      <div
        style={{
          position: "absolute",
          width: "900px",
          height: "600px",
          right: "80px",
          top: "32%",
          transform: "translateY(-50%)",
          borderRadius: "50%",
          background: `radial-gradient(ellipse at center, rgba(${accentColorRgb}, 0.10) 0%, rgba(${accentColorRgb}, 0.02) 48%, transparent 72%)`,
          filter: "blur(60px)",
        }}
      />

      {/* Ultra-subtle Horizontal Baseline & Datum Guideline */}
      <div
        style={{
          position: "absolute",
          top: "84px",
          left: "120px",
          right: "120px",
          height: "1px",
          background: "linear-gradient(90deg, transparent 0%, rgba(255, 255, 255, 0.04) 15%, rgba(255, 255, 255, 0.04) 85%, transparent 100%)",
        }}
      />
      <div
        style={{
          position: "absolute",
          bottom: "96px",
          left: "120px",
          right: "120px",
          height: "1px",
          background: "linear-gradient(90deg, transparent 0%, rgba(255, 255, 255, 0.035) 15%, rgba(255, 255, 255, 0.035) 85%, transparent 100%)",
        }}
      />
    </AbsoluteFill>
  );
}

// ---------------------------------------------------------------------------
// Exact Analytical Cubic Bezier Position Calculator
// ---------------------------------------------------------------------------

function getCubicBezierPoint(
  t: number,
  p0: [number, number],
  p1: [number, number],
  p2: [number, number],
  p3: [number, number]
): [number, number] {
  const clampedT = Math.max(0, Math.min(1, t));
  const u = 1 - clampedT;
  const tt = clampedT * clampedT;
  const uu = u * u;
  const uuu = uu * u;
  const ttt = tt * clampedT;

  const x = uuu * p0[0] + 3 * uu * clampedT * p1[0] + 3 * u * tt * p2[0] + ttt * p3[0];
  const y = uuu * p0[1] + 3 * uu * clampedT * p1[1] + 3 * u * tt * p2[1] + ttt * p3[1];
  return [x, y];
}

// ---------------------------------------------------------------------------
// Main GrowthTrajectory Component
// ---------------------------------------------------------------------------

export function GrowthTrajectory(rawProps: GrowthTrajectoryProps | any) {
  const frame = useCurrentFrame();
  const videoConfig = useVideoConfig();

  // Robust prop unwrapping supporting VideoAssembly wrapper and direct calls
  const resolvedProps: GrowthTrajectoryProps = (rawProps as any)?.props || rawProps || {};
  const duration_frames = (rawProps as any)?.duration_frames || videoConfig?.durationInFrames || 180;
  const fps = (rawProps as any)?.fps || videoConfig?.fps || 30;

  const {
    headerLabel,
    startValue,
    startLabel = "Starting Point",
    endValue,
    endLabel = "Target Corpus",
    timeHorizon,
    growthRate,
    growthType = "unspecified",
    milestoneValue,
    milestoneLabel,
    annotation,
    variant = "standard",
  } = resolvedProps;

  // Scene fade-in (frames 0..8)
  const sceneOpacity = interpolate(
    frame,
    [0, Math.min(8, Math.max(1, duration_frames - 1))],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // Sub-threshold camera motion: subtle atmospheric zoom (1.000 -> 1.006)
  const cameraScale = interpolate(
    frame,
    [0, Math.max(1, duration_frames)],
    [1.000, 1.006],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // -------------------------------------------------------------------------
  // Color Palette & Polarity Staging
  // -------------------------------------------------------------------------
  const isDeclining =
    variant === "declining_trajectory" ||
    (growthRate && growthRate.includes("-")) ||
    (endValue && endValue.startsWith("-"));

  const accentColor = isDeclining ? (tokens.accent.rose || "#f43f5e") : (tokens.accent.emerald || "#10b981");
  const accentColorRgb = isDeclining ? "244, 63, 94" : "16, 185, 129";
  const startColor = "#38bdf8"; // Cyan for baseline/foundation

  // -------------------------------------------------------------------------
  // Duration-Adaptive Choreography Windows
  // -------------------------------------------------------------------------
  const scaleRatio = Math.min(1, duration_frames / 120);

  // 1. Header & Datum Entrance
  const headerDelay = safeSpringDelay(Math.round(3 * scaleRatio), duration_frames, 0.08);
  const headerSpring = spring({
    frame: Math.max(0, frame - headerDelay),
    fps,
    config: tokens.motion.reveal,
  });

  // 2. Start Origin Anchor Entrance
  const startDelay = safeSpringDelay(Math.round(6 * scaleRatio), duration_frames, 0.14);
  const startSpring = spring({
    frame: Math.max(0, frame - startDelay),
    fps,
    config: tokens.motion.reveal,
  });

  // 3. Trajectory Curve Progressive Reveal Window
  const [curveStart, curveEnd] = safeAnimationWindow(
    Math.round(14 * scaleRatio),
    Math.round(58 * scaleRatio),
    duration_frames
  );
  const curveProgress = interpolate(
    frame,
    [curveStart, curveEnd],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // 4. Milestone / Inflection Activation Window (triggers when path crosses ~50% progress)
  const milestoneDelay = safeSpringDelay(
    Math.round(34 * scaleRatio),
    duration_frames,
    0.46
  );
  const milestoneSpring = spring({
    frame: Math.max(0, frame - milestoneDelay),
    fps,
    config: tokens.motion.gentle,
  });

  // 5. Climax / End Value Arrival
  const endDelay = safeSpringDelay(
    Math.round(48 * scaleRatio),
    duration_frames,
    0.62
  );
  const endSpring = spring({
    frame: Math.max(0, frame - endDelay),
    fps,
    config: tokens.motion.impact,
  });

  // Footnote entrance
  const annotationDelay = safeSpringDelay(
    Math.round(58 * scaleRatio),
    duration_frames,
    0.72
  );
  const annotationSpring = spring({
    frame: Math.max(0, frame - annotationDelay),
    fps,
    config: tokens.motion.gentle,
  });

  // -------------------------------------------------------------------------
  // Sweeping Full-Canvas Trajectory Geometry (1920 x 1080 Viewport)
  // -------------------------------------------------------------------------
  const svgWidth = 1920;
  const svgHeight = 1080;

  // Origin coordinate
  const xStart = 240;
  const yStart = isDeclining ? 340 : 730;

  // Apex / Destination coordinate
  const xEnd = 1680;
  const yEnd = isDeclining ? 730 : 340;

  const dx = xEnd - xStart;
  const dy = yStart - yEnd;

  // Exact mathematical Bezier Control Points by growth variant
  let cp1: [number, number];
  let cp2: [number, number];
  let milestoneT = 0.50; // parameter t along curve where milestone sits

  if (isDeclining) {
    // Graceful descent
    cp1 = [xStart + dx * 0.40, yStart + dy * 0.20];
    cp2 = [xStart + dx * 0.75, yStart + dy * 0.85];
    milestoneT = 0.48;
  } else if (growthType === "linear" || variant === "linear_accumulation") {
    // Steady disciplined linear accumulation
    cp1 = [xStart + dx * 0.33, yStart - dy * 0.33];
    cp2 = [xStart + dx * 0.67, yStart - dy * 0.67];
    milestoneT = 0.50;
  } else if (growthType === "accelerating" || variant === "accelerating_growth") {
    // Noticeable mid-stage upward inflection
    cp1 = [xStart + dx * 0.38, yStart - dy * 0.12];
    cp2 = [xStart + dx * 0.70, yStart - dy * 0.62];
    milestoneT = 0.52;
  } else {
    // Classic Compounding Snowball (Hockey Stick)
    // Starts shallow/flat during early capital accumulation, then exponentially surges
    cp1 = [xStart + dx * 0.50, yStart - dy * 0.08];
    cp2 = [xStart + dx * 0.80, yStart - dy * 0.52];
    milestoneT = 0.55;
  }

  const p0: [number, number] = [xStart, yStart];
  const p3: [number, number] = [xEnd, yEnd];

  const pathData = `M ${p0[0]} ${p0[1]} C ${cp1[0]} ${cp1[1]}, ${cp2[0]} ${cp2[1]}, ${p3[0]} ${p3[1]}`;
  const baselineY = 820;
  const areaFillData = `M ${p0[0]} ${p0[1]} C ${cp1[0]} ${cp1[1]}, ${cp2[0]} ${cp2[1]}, ${p3[0]} ${p3[1]} L ${xEnd} ${baselineY} L ${xStart} ${baselineY} Z`;

  // Calculated SVG path length
  const totalLength = 1750;
  const strokeOffset = totalLength * (1 - curveProgress);

  // Exact lead marker position along curve
  const [leadX, leadY] = getCubicBezierPoint(curveProgress, p0, cp1, cp2, p3);
  const [milestoneX, milestoneY] = getCubicBezierPoint(milestoneT, p0, cp1, cp2, p3);

  // Determine milestone presence
  const hasExplicitMilestone = Boolean(milestoneValue || milestoneLabel);
  const isCompoundingSnowball = variant === "compounding_snowball" || growthType === "compound";
  const displayMilestone = hasExplicitMilestone || isCompoundingSnowball;

  const milestonePrimaryText = milestoneValue || (isDeclining ? "CRITICAL THRESHOLD" : "INFLECTION POINT");
  const milestoneSecondaryText = milestoneLabel || (isDeclining ? "Accelerating erosion" : "Compounding kicks in");

  // Dynamic typography sizing based on length to prevent layout wrapping
  const startValStr = startValue || "";
  const endValStr = endValue || "";

  const startFontSize = startValStr.length > 14 ? 34 : startValStr.length > 9 ? 42 : 52;
  const endFontSize = endValStr.length > 14 ? 54 : endValStr.length > 9 ? 66 : 82;

  // Editorial category title
  const effectiveHeader = (headerLabel || (
    isDeclining
      ? "DECAY TRAJECTORY"
      : isCompoundingSnowball
      ? "COMPOUNDING TRAJECTORY"
      : "GROWTH TRAJECTORY"
  )).toUpperCase();

  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#060911",
        fontFamily: tokens.font.family,
        opacity: sceneOpacity,
        transform: `scale(${cameraScale})`,
        overflow: "hidden",
      }}
    >
      <EditorialBackdrop accentColorRgb={accentColorRgb} />

      {/* ----------------------------------------------------------------- */}
      {/* 1. TOP EDITORIAL SAFE ZONE (Header & Temporal Chips)             */}
      {/* ----------------------------------------------------------------- */}
      <div
        style={{
          position: "absolute",
          top: "44px",
          left: "120px",
          right: "120px",
          height: "48px",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          opacity: headerSpring,
          transform: `translateY(${interpolate(headerSpring, [0, 1], [-14, 0])}px)`,
          zIndex: 10,
        }}
      >
        {/* Left: Section Topic / Category Tag */}
        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          <div
            style={{
              width: "8px",
              height: "8px",
              borderRadius: "50%",
              backgroundColor: accentColor,
              boxShadow: `0 0 10px ${accentColor}`,
            }}
          />
          <span
            style={{
              fontSize: "14px",
              fontWeight: 700,
              textTransform: "uppercase",
              letterSpacing: "0.16em",
              color: "#94a3b8",
            }}
          >
            {effectiveHeader}
          </span>
        </div>

        {/* Right: Temporal & Rate Badges (Restrained Editorial Style) */}
        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          {timeHorizon && (
            <div
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: "7px",
                fontSize: "13px",
                fontWeight: 600,
                color: "#cbd5e1",
                backgroundColor: "rgba(255, 255, 255, 0.04)",
                border: "1px solid rgba(255, 255, 255, 0.08)",
                padding: "6px 14px",
                borderRadius: tokens.radius.chip,
                letterSpacing: "0.06em",
                textTransform: "uppercase",
              }}
            >
              <span style={{ color: "#64748b" }}>HORIZON</span>
              <span style={{ color: "#f8fafc", fontWeight: 700 }}>{timeHorizon}</span>
            </div>
          )}

          {growthRate && (
            <div
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: "7px",
                fontSize: "13px",
                fontWeight: 600,
                color: accentColor,
                backgroundColor: `rgba(${accentColorRgb}, 0.08)`,
                border: `1px solid rgba(${accentColorRgb}, 0.28)`,
                padding: "6px 14px",
                borderRadius: tokens.radius.chip,
                letterSpacing: "0.06em",
                textTransform: "uppercase",
              }}
            >
              <span>{isDeclining ? "▼" : "▲"}</span>
              <span style={{ fontWeight: 800 }}>{growthRate}</span>
            </div>
          )}
        </div>
      </div>

      {/* ----------------------------------------------------------------- */}
      {/* 2. SWEEPING FULL-CANVAS SVG TRAJECTORY                            */}
      {/* ----------------------------------------------------------------- */}
      <svg
        viewBox={`0 0 ${svgWidth} ${svgHeight}`}
        style={{
          position: "absolute",
          inset: 0,
          width: "100%",
          height: "100%",
          overflow: "visible",
          zIndex: 5,
        }}
      >
        <defs>
          {/* Subtle Area Gradient under Trajectory */}
          <linearGradient id="editorialAreaGrad" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor={accentColor} stopOpacity="0.12" />
            <stop offset="65%" stopColor={accentColor} stopOpacity="0.02" />
            <stop offset="100%" stopColor={accentColor} stopOpacity="0.0" />
          </linearGradient>

          {/* Linear Line Gradient from Origin to Destination */}
          <linearGradient id="editorialLineGrad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor={startColor} />
            <stop offset="45%" stopColor="#38bdf8" />
            <stop offset="78%" stopColor={accentColor} />
            <stop offset="100%" stopColor={accentColor} />
          </linearGradient>

          {/* Soft Editorial Line Glow Filter */}
          <filter id="trajectoryGlow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="3.5" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
          </filter>

          {/* Progressive Reveal Clip for Area Fill to eliminate premature ghosting */}
          <clipPath id="trajectoryAreaClip">
            <rect x="0" y="0" width={Math.max(xStart, leadX)} height={svgHeight} />
          </clipPath>
        </defs>

        {/* Faint Horizontal Metric Guide Grid */}
        <line
          x1={xStart - 40}
          y1={baselineY}
          x2={xEnd + 80}
          y2={baselineY}
          stroke="rgba(255, 255, 255, 0.05)"
          strokeWidth="1.5"
        />
        <line
          x1={xStart - 40}
          y1={yStart}
          x2={xEnd + 80}
          y2={yStart}
          stroke="rgba(255, 255, 255, 0.03)"
          strokeWidth="1"
          strokeDasharray="4 8"
        />
        <line
          x1={xStart - 40}
          y1={yEnd}
          x2={xEnd + 80}
          y2={yEnd}
          stroke="rgba(255, 255, 255, 0.03)"
          strokeWidth="1"
          strokeDasharray="4 8"
        />

        {/* Delicate Area Fill Under Curve (Reveals in sync with trajectory stroke) */}
        <path
          d={areaFillData}
          fill="url(#editorialAreaGrad)"
          clipPath="url(#trajectoryAreaClip)"
          opacity={interpolate(curveProgress, [0, 0.35], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          })}
        />

        {/* The Sweeping Editorial Trajectory Curve */}
        <path
          d={pathData}
          fill="none"
          stroke="url(#editorialLineGrad)"
          strokeWidth="4.5"
          strokeLinecap="round"
          strokeDasharray={totalLength}
          strokeDashoffset={strokeOffset}
          filter="url(#trajectoryGlow)"
        />

        {/* Origin Node Anchor */}
        <g opacity={startSpring} transform={`scale(${startSpring})`} style={{ transformOrigin: `${p0[0]}px ${p0[1]}px` }}>
          <circle cx={p0[0]} cy={p0[1]} r="6" fill={startColor} />
          <circle cx={p0[0]} cy={p0[1]} r="13" fill="none" stroke={startColor} strokeWidth="1.5" opacity="0.35" />
        </g>

        {/* Inflection / Milestone Marker & Vertical Datum Guideline */}
        {displayMilestone && (
          <g opacity={milestoneSpring}>
            {/* Delicate Vertical Datum Rule */}
            <line
              x1={milestoneX}
              y1={milestoneY}
              x2={milestoneX}
              y2={baselineY}
              stroke="rgba(255, 255, 255, 0.12)"
              strokeWidth="1.5"
              strokeDasharray="4 4"
            />
            {/* Inflection Node Indicator */}
            <circle cx={milestoneX} cy={milestoneY} r="5" fill="#f8fafc" />
            <circle
              cx={milestoneX}
              cy={milestoneY}
              r={12 * milestoneSpring}
              fill="none"
              stroke={accentColor}
              strokeWidth="1.5"
              opacity="0.5"
            />
          </g>
        )}

        {/* Kinetic Traveling Lead Point (Active during path traversal) */}
        {curveProgress > 0.01 && curveProgress < 0.99 && (
          <g>
            <circle
              cx={leadX}
              cy={leadY}
              r="4.5"
              fill="#ffffff"
              style={{ filter: "drop-shadow(0 0 6px #ffffff)" }}
            />
            <circle
              cx={leadX}
              cy={leadY}
              r="10"
              fill="none"
              stroke={accentColor}
              strokeWidth="1.5"
              opacity="0.65"
            />
          </g>
        )}

        {/* Destination Climax Node Dot */}
        <g opacity={endSpring} transform={`scale(${endSpring})`} style={{ transformOrigin: `${p3[0]}px ${p3[1]}px` }}>
          {/* Subtle Terminal Vertical Datum Rule */}
          <line
            x1={p3[0]}
            y1={p3[1]}
            x2={p3[0]}
            y2={baselineY}
            stroke="rgba(255, 255, 255, 0.10)"
            strokeWidth="1.5"
            strokeDasharray="4 4"
          />
          <circle cx={p3[0]} cy={p3[1]} r="7.5" fill={accentColor} />
          <circle
            cx={p3[0]}
            cy={p3[1]}
            r={16 * endSpring}
            fill="none"
            stroke={accentColor}
            strokeWidth="2"
            opacity="0.45"
          />
          <circle
            cx={p3[0]}
            cy={p3[1]}
            r={24 * endSpring}
            fill="none"
            stroke={accentColor}
            strokeWidth="1"
            opacity="0.2"
          />
        </g>
      </svg>

      {/* ----------------------------------------------------------------- */}
      {/* 3. DIRECTLY TIED EDITORIAL VALUE OVERLAYS (NO CARDS)              */}
      {/* ----------------------------------------------------------------- */}

      {/* A. ORIGIN VALUE ANCHOR (Tied directly to left origin) */}
      <div
        style={{
          position: "absolute",
          left: `${xStart - 40}px`,
          top: isDeclining ? `${yStart - 170}px` : `${yStart - 160}px`,
          width: "360px",
          display: "flex",
          flexDirection: "column",
          alignItems: "flex-start",
          opacity: startSpring,
          transform: `translateY(${interpolate(startSpring, [0, 1], [18, 0])}px)`,
          zIndex: 8,
          pointerEvents: "none",
        }}
      >
        {/* Origin Category Tag */}
        <div
          style={{
            fontSize: "12px",
            fontWeight: 700,
            textTransform: "uppercase",
            letterSpacing: "0.14em",
            color: "#64748b",
            marginBottom: "4px",
          }}
        >
          {startLabel.toUpperCase()}
        </div>

        {/* Start Value */}
        {startValue && (
          <div
            style={{
              fontSize: `${startFontSize}px`,
              fontWeight: 800,
              fontVariantNumeric: "tabular-nums",
              color: "#e2e8f0",
              lineHeight: 1.05,
              letterSpacing: "-0.02em",
            }}
          >
            {startValue}
          </div>
        )}

        {/* Subtle Phase Subtitle */}
        <div
          style={{
            fontSize: "13px",
            fontWeight: 500,
            color: "#64748b",
            marginTop: "6px",
            letterSpacing: "0.02em",
          }}
        >
          {isDeclining ? "Initial baseline position" : "Initial capital base"}
        </div>
      </div>

      {/* B. INFLECTION MILESTONE CALLOUT (Floating at inflection node) */}
      {displayMilestone && (
        <div
          style={{
            position: "absolute",
            left: `${milestoneX}px`,
            top: isDeclining ? `${milestoneY + 28}px` : `${milestoneY - 88}px`,
            transform: `translate(-50%, ${interpolate(milestoneSpring, [0, 1], [isDeclining ? -8 : 8, 0])}px) scale(${milestoneSpring})`,
            opacity: milestoneSpring,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            padding: "8px 18px",
            borderRadius: "6px",
            backgroundColor: "rgba(11, 18, 34, 0.88)",
            border: `1px solid rgba(${accentColorRgb}, 0.35)`,
            backdropFilter: "blur(10px)",
            boxShadow: "0 12px 28px -6px rgba(0, 0, 0, 0.6)",
            whiteSpace: "nowrap",
            zIndex: 9,
            pointerEvents: "none",
          }}
        >
          <div
            style={{
              fontSize: "13px",
              fontWeight: 800,
              color: "#f8fafc",
              letterSpacing: "0.06em",
              textTransform: "uppercase",
            }}
          >
            {milestonePrimaryText}
          </div>
          <div
            style={{
              fontSize: "12px",
              fontWeight: 500,
              color: "#94a3b8",
              marginTop: "2px",
            }}
          >
            {milestoneSecondaryText}
          </div>
        </div>
      )}

      {/* C. TERMINAL PAYOFF CLIMAX (Tied directly to right terminus) */}
      <div
        style={{
          position: "absolute",
          left: `${xEnd - 320}px`,
          top: isDeclining ? `${yEnd + 26}px` : `${yEnd - 180}px`,
          width: "480px",
          display: "flex",
          flexDirection: "column",
          alignItems: "flex-start",
          opacity: endSpring,
          transform: `translateY(${interpolate(endSpring, [0, 1], [isDeclining ? -20 : 20, 0])}px)`,
          zIndex: 8,
          pointerEvents: "none",
        }}
      >
        {/* Terminal Category Tag */}
        <div
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: "8px",
            fontSize: "13px",
            fontWeight: 700,
            textTransform: "uppercase",
            letterSpacing: "0.14em",
            color: accentColor,
            marginBottom: "4px",
          }}
        >
          <span style={{ fontSize: "11px" }}>●</span>
          <span>{endLabel.toUpperCase()}</span>
        </div>

        {/* Hero Climax Value */}
        {endValue && (
          <div
            style={{
              fontSize: `${endFontSize}px`,
              fontWeight: 800,
              fontVariantNumeric: "tabular-nums",
              color: isDeclining ? "#f43f5e" : "#f8fafc",
              lineHeight: 1.02,
              letterSpacing: "-0.03em",
              textShadow: `0 0 35px rgba(${accentColorRgb}, 0.32)`,
            }}
          >
            {endValue}
          </div>
        )}

        {/* Editorial Annotation Subtitle */}
        {annotation && (
          <div
            style={{
              fontSize: "14px",
              fontWeight: 500,
              color: "#94a3b8",
              marginTop: "10px",
              maxWidth: "420px",
              lineHeight: 1.45,
              opacity: annotationSpring,
              transform: `translateY(${interpolate(annotationSpring, [0, 1], [6, 0])}px)`,
            }}
          >
            {annotation}
          </div>
        )}
      </div>

      {/* ----------------------------------------------------------------- */}
      {/* 4. BASELINE HORIZONTAL TIMELINE LABELS                            */}
      {/* ----------------------------------------------------------------- */}
      <div
        style={{
          position: "absolute",
          bottom: "64px",
          left: `${xStart}px`,
          right: `${svgWidth - xEnd}px`,
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          fontSize: "12px",
          fontWeight: 600,
          textTransform: "uppercase",
          letterSpacing: "0.12em",
          color: "#475569",
          opacity: headerSpring,
          zIndex: 6,
          pointerEvents: "none",
        }}
      >
        <span>T = 0 (ORIGIN)</span>
        {displayMilestone && (
          <span style={{ color: "rgba(148, 163, 184, 0.7)" }}>
            {(() => {
              const digits = timeHorizon?.replace(/[^0-9]/g, '');
              if (digits && Number(digits) > 0) {
                return `MIDPOINT (~${Math.round(Number(digits) / 2)} YRS)`;
              }
              return "INFLECTION PHASE";
            })()}
          </span>
        )}
        <span>{timeHorizon ? `MATURITY (${timeHorizon})` : "TERMINUS"}</span>
      </div>
    </AbsoluteFill>
  );
}
