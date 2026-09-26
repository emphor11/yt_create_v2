import React from 'react';
import { AbsoluteFill, interpolate, spring, useCurrentFrame } from 'remotion';
import { tokens } from '../design-tokens';
import { GrowthTrajectoryProps } from '../types';
import { safeAnimationWindow, safeSpringDelay } from '../animation-safety';

export function GrowthTrajectory(childProps: {
  scene_id: string;
  composition: string;
  fps: number;
  duration_frames: number;
  props: GrowthTrajectoryProps;
  frame_spans?: any[];
}) {
  const { props, duration_frames, fps = 30 } = childProps;
  const frame = useCurrentFrame();

  const {
    headerLabel = "GROWTH TRAJECTORY",
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
  } = props;

  // Scene fade-in (frames 0..8)
  const sceneOpacity = interpolate(
    frame,
    [0, Math.min(8, Math.max(1, duration_frames - 1))],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // 1. Establish: Entrance of start card and header
  const headerDelay = safeSpringDelay(4, duration_frames, 0.1);
  const headerSpring = spring({
    frame: Math.max(0, frame - headerDelay),
    fps,
    config: tokens.motion.reveal,
  });

  const startCardDelay = safeSpringDelay(8, duration_frames, 0.18);
  const startCardSpring = spring({
    frame: Math.max(0, frame - startCardDelay),
    fps,
    config: tokens.motion.reveal,
  });

  // 2. Trajectory drawing window (e.g. frames 18..75 scaled to duration)
  const [curveStart, curveEnd] = safeAnimationWindow(18, 75, duration_frames);
  const curveProgress = interpolate(
    frame,
    [curveStart, curveEnd],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // 3. Optional inflection / milestone reveal (triggers around 50% along the path)
  const isCompoundingOrAccelerating =
    growthType === "compound" ||
    growthType === "accelerating" ||
    variant === "compounding_snowball" ||
    variant === "accelerating_growth" ||
    variant === "milestone_progression";

  const hasMilestone = Boolean(milestoneValue || milestoneLabel || isCompoundingOrAccelerating);
  const milestoneDelay = safeSpringDelay(38, duration_frames, 0.48);
  const milestoneSpring = spring({
    frame: Math.max(0, frame - milestoneDelay),
    fps,
    config: tokens.motion.gentle,
  });

  // 4. Payoff / target card reveal (settles once curve arrives at terminus)
  const payoffDelay = safeSpringDelay(56, duration_frames, 0.68);
  const payoffSpring = spring({
    frame: Math.max(0, frame - payoffDelay),
    fps,
    config: tokens.motion.impact,
  });

  // SVG Coordinate Geometry (960 x 360 coordinate space)
  const svgWidth = 960;
  const svgHeight = 360;
  const xStart = 80;
  const yStart = 290; // baseline
  const xEnd = 880;
  const yEnd = 65;   // peak target
  const dx = xEnd - xStart;
  const dy = yStart - yEnd; // positive height difference (225px)

  // Curve profile based on growth regime
  let cp1x: number;
  let cp1y: number;
  let cp2x: number;
  let cp2y: number;
  let inflectionX = xStart + dx * 0.52;
  let inflectionY = yStart - dy * 0.28;

  if (growthType === "linear" || variant === "linear_accumulation") {
    // Gentle steady upward linear trajectory
    cp1x = Math.round(xStart + dx * 0.33);
    cp1y = Math.round(yStart - dy * 0.33);
    cp2x = Math.round(xStart + dx * 0.66);
    cp2y = Math.round(yStart - dy * 0.66);
    inflectionX = Math.round(xStart + dx * 0.5);
    inflectionY = Math.round(yStart - dy * 0.5);
  } else if (growthType === "accelerating" || variant === "accelerating_growth") {
    // Gradual start, bending noticeably upward in the middle
    cp1x = Math.round(xStart + dx * 0.42);
    cp1y = Math.round(yStart - dy * 0.16);
    cp2x = Math.round(xStart + dx * 0.72);
    cp2y = Math.round(yStart - dy * 0.60);
    inflectionX = Math.round(xStart + dx * 0.50);
    inflectionY = Math.round(yStart - dy * 0.30);
  } else {
    // Classic compounding hockey stick / wealth snowball
    cp1x = Math.round(xStart + dx * 0.52);
    cp1y = Math.round(yStart - dy * 0.10);
    cp2x = Math.round(xStart + dx * 0.78);
    cp2y = Math.round(yStart - dy * 0.45);
    inflectionX = Math.round(xStart + dx * 0.54);
    inflectionY = Math.round(yStart - dy * 0.22);
  }

  const pathData = `M ${xStart} ${yStart} C ${cp1x} ${cp1y}, ${cp2x} ${cp2y}, ${xEnd} ${yEnd}`;
  const areaFillData = `${pathData} L ${xEnd} 320 L ${xStart} 320 Z`;
  const pathTotalLength = 1100;
  const strokeOffset = pathTotalLength * (1 - curveProgress);

  // Position of lead marker along curve
  const currentLeadX = interpolate(curveProgress, [0, 1], [xStart, xEnd]);
  const currentLeadY = interpolate(
    curveProgress,
    [0, 0.5, 1],
    [yStart, inflectionY, yEnd]
  );

  const displayStartValue = startValue || startLabel || "";
  const displayEndValue = endValue || endLabel || "";

  return (
    <AbsoluteFill
      style={{
        backgroundColor: tokens.bg.base,
        fontFamily: tokens.font.family,
        opacity: sceneOpacity,
        display: "flex",
        flexDirection: "column",
        justifyContent: "space-between",
        padding: "50px 70px",
        overflow: "hidden",
      }}
    >
      {/* Top Header Bar */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          opacity: headerSpring,
          transform: `translateY(${interpolate(headerSpring, [0, 1], [-20, 0])}px)`,
          width: "100%",
          paddingBottom: "12px",
          borderBottom: `1px solid ${tokens.bg.border}`,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
          <div
            style={{
              width: "12px",
              height: "12px",
              borderRadius: "50%",
              backgroundColor: tokens.accent.emerald,
              boxShadow: `0 0 14px ${tokens.accent.emerald}`,
            }}
          />
          <span
            style={{
              fontSize: "19px",
              fontWeight: 700,
              textTransform: "uppercase",
              letterSpacing: "0.12em",
              color: tokens.text.secondary,
            }}
          >
            {headerLabel}
          </span>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          {growthRate && (
            <div
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: "8px",
                fontSize: "15px",
                fontWeight: 700,
                color: tokens.accent.amber,
                backgroundColor: "rgba(245, 158, 11, 0.12)",
                border: "1px solid rgba(245, 158, 11, 0.35)",
                padding: "6px 14px",
                borderRadius: tokens.radius.chip,
              }}
            >
              📈 {growthRate}
            </div>
          )}
          {timeHorizon && (
            <div
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: "8px",
                fontSize: "15px",
                fontWeight: 700,
                color: tokens.accent.cyan,
                backgroundColor: "rgba(56, 189, 248, 0.12)",
                border: "1px solid rgba(56, 189, 248, 0.35)",
                padding: "6px 14px",
                borderRadius: tokens.radius.chip,
              }}
            >
              ⏱ {timeHorizon}
            </div>
          )}
        </div>
      </div>

      {/* Main Content: Split Storytelling Layout */}
      <div
        style={{
          display: "flex",
          flexDirection: "row",
          alignItems: "center",
          justifyContent: "space-between",
          flex: 1,
          gap: "40px",
          marginTop: "20px",
          marginBottom: "10px",
        }}
      >
        {/* Left: Starting Anchor Card */}
        <div
          style={{
            opacity: startCardSpring,
            transform: `translateX(${interpolate(startCardSpring, [0, 1], [-35, 0])}px)`,
            flex: 0.75,
            maxWidth: "360px",
            backgroundColor: tokens.bg.cardLeft,
            borderRadius: tokens.radius.card,
            border: `1px solid ${tokens.bg.border}`,
            borderLeft: `4px solid ${tokens.accent.cyan}`,
            padding: "32px 28px",
            display: "flex",
            flexDirection: "column",
            justifyContent: "space-between",
            boxShadow: "0 16px 36px -12px rgba(0, 0, 0, 0.5)",
          }}
        >
          <div>
            <div
              style={{
                fontSize: "15px",
                fontWeight: 700,
                textTransform: "uppercase",
                letterSpacing: "0.08em",
                color: tokens.accent.cyan,
                marginBottom: "8px",
              }}
            >
              {startLabel}
            </div>
            <div
              style={{
                fontSize: displayStartValue.length > 14 ? "30px" : displayStartValue.length > 8 ? "40px" : "54px",
                fontWeight: 800,
                color: tokens.text.primary,
                lineHeight: 1.1,
                marginBottom: "12px",
              }}
            >
              {displayStartValue}
            </div>
            <div
              style={{
                fontSize: "15px",
                color: tokens.text.muted,
                lineHeight: 1.4,
              }}
            >
              {growthType === "compound"
                ? "Early foundation built strictly through disciplined savings"
                : "Baseline accumulation starting point"}
            </div>
          </div>

          <div
            style={{
              marginTop: "24px",
              padding: "10px 14px",
              borderRadius: tokens.radius.chip,
              backgroundColor: "rgba(255, 255, 255, 0.04)",
              border: `1px solid ${tokens.bg.border}`,
              fontSize: "14px",
              fontWeight: 600,
              color: tokens.text.secondary,
            }}
          >
            Phase 1: Linear Accumulation
          </div>
        </div>

        {/* Center Canvas: The Animated Growth Trajectory Chart */}
        <div
          style={{
            flex: 1.8,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            position: "relative",
            minHeight: "360px",
          }}
        >
          <svg
            viewBox={`0 0 ${svgWidth} ${svgHeight}`}
            style={{ width: "100%", height: "100%", overflow: "visible" }}
          >
            <defs>
              <linearGradient id="growthAreaGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor={tokens.accent.cyan} stopOpacity="0.04" />
                <stop offset="50%" stopColor={tokens.accent.emerald} stopOpacity="0.16" />
                <stop offset="100%" stopColor={tokens.accent.amber} stopOpacity="0.28" />
              </linearGradient>

              <linearGradient id="growthLineGrad" x1="0%" y1="100%" x2="100%" y2="0%">
                <stop offset="0%" stopColor={tokens.accent.cyan} />
                <stop offset="52%" stopColor={tokens.accent.emerald} />
                <stop offset="100%" stopColor={tokens.accent.amber} />
              </linearGradient>

              <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
                <feGaussianBlur stdDeviation="4" result="blur" />
                <feComposite in="SourceGraphic" in2="blur" operator="over" />
              </filter>
            </defs>

            {/* Horizontal Grid & Time Axis Guide Lines */}
            <line
              x1={xStart}
              y1={yStart}
              x2={xEnd}
              y2={yStart}
              stroke="rgba(255, 255, 255, 0.12)"
              strokeWidth="2"
            />
            <line
              x1={xStart}
              y1={Math.round((yStart + yEnd) / 2)}
              x2={xEnd}
              y2={Math.round((yStart + yEnd) / 2)}
              stroke="rgba(255, 255, 255, 0.05)"
              strokeWidth="1"
              strokeDasharray="4 4"
            />
            <line
              x1={xStart}
              y1={yEnd}
              x2={xEnd}
              y2={yEnd}
              stroke="rgba(255, 255, 255, 0.08)"
              strokeWidth="1"
              strokeDasharray="4 4"
            />

            {/* Area Fill under the growth curve */}
            <path
              d={areaFillData}
              fill="url(#growthAreaGrad)"
              opacity={interpolate(curveProgress, [0, 0.3], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })}
            />

            {/* The Main Growth Curve */}
            <path
              d={pathData}
              fill="none"
              stroke="url(#growthLineGrad)"
              strokeWidth="5"
              strokeLinecap="round"
              strokeDasharray={pathTotalLength}
              strokeDashoffset={strokeOffset}
              filter="url(#glow)"
            />

            {/* Starting Node Dot */}
            <circle
              cx={xStart}
              cy={yStart}
              r={startCardSpring * 6}
              fill={tokens.accent.cyan}
              stroke="#fff"
              strokeWidth="2"
            />

            {/* Optional Inflection / Transition Marker */}
            {hasMilestone && (
              <g opacity={milestoneSpring}>
                {/* Vertical Dotted Guide Line */}
                <line
                  x1={inflectionX}
                  y1={yStart}
                  x2={inflectionX}
                  y2={inflectionY}
                  stroke={tokens.accent.emerald}
                  strokeWidth="2"
                  strokeDasharray="3 3"
                  opacity="0.65"
                />

                {/* Inflection Node Pulse */}
                <circle
                  cx={inflectionX}
                  cy={inflectionY}
                  r={8 * milestoneSpring}
                  fill={tokens.accent.emerald}
                  stroke="#fff"
                  strokeWidth="2"
                />
                <circle
                  cx={inflectionX}
                  cy={inflectionY}
                  r={15 * milestoneSpring}
                  fill="none"
                  stroke={tokens.accent.emerald}
                  strokeWidth="1.5"
                  opacity="0.45"
                />
              </g>
            )}

            {/* Lead Moving Dot along the animated path */}
            {curveProgress > 0.02 && curveProgress < 0.98 && (
              <circle
                cx={currentLeadX}
                cy={currentLeadY}
                r="7"
                fill="#fff"
                filter="url(#glow)"
              />
            )}

            {/* Terminal Payoff Node Dot */}
            <circle
              cx={xEnd}
              cy={yEnd}
              r={payoffSpring * 9}
              fill={tokens.accent.amber}
              stroke="#fff"
              strokeWidth="3"
              filter="url(#glow)"
            />
          </svg>

          {/* Floating Inflection Callout Badge */}
          {hasMilestone && (
            <div
              style={{
                position: "absolute",
                left: `${(inflectionX / svgWidth) * 100}%`,
                top: `${(inflectionY / svgHeight) * 100}%`,
                transform: `translate(-50%, -125%) scale(${milestoneSpring})`,
                opacity: milestoneSpring,
                backgroundColor: "rgba(16, 185, 129, 0.16)",
                border: "1px solid rgba(16, 185, 129, 0.5)",
                padding: "8px 14px",
                borderRadius: tokens.radius.chip,
                backdropFilter: "blur(6px)",
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                whiteSpace: "nowrap",
                pointerEvents: "none",
              }}
            >
              <span
                style={{
                  fontSize: "14px",
                  fontWeight: 800,
                  color: tokens.accent.emerald,
                  letterSpacing: "0.04em",
                }}
              >
                {milestoneValue || "TIPPING POINT"}
              </span>
              <span
                style={{
                  fontSize: "12px",
                  fontWeight: 600,
                  color: tokens.text.secondary,
                  marginTop: "2px",
                }}
              >
                {milestoneLabel || "Returns begin compounding"}
              </span>
            </div>
          )}

          {/* Time Axis Labels along bottom of chart */}
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              width: "100%",
              paddingLeft: "70px",
              paddingRight: "70px",
              marginTop: "8px",
              fontSize: "13px",
              fontWeight: 600,
              textTransform: "uppercase",
              letterSpacing: "0.08em",
              color: tokens.text.muted,
            }}
          >
            <span>Time: Start</span>
            {hasMilestone && (
              <span style={{ color: tokens.accent.emerald }}>
                Growth Acceleration
              </span>
            )}
            <span>{timeHorizon || "Target Horizon"}</span>
          </div>
        </div>

        {/* Right: Eventual Payoff / Climax Card */}
        <div
          style={{
            opacity: payoffSpring,
            transform: `translateX(${interpolate(payoffSpring, [0, 1], [35, 0])}px)`,
            flex: 0.85,
            maxWidth: "380px",
            backgroundColor: tokens.bg.cardRight,
            borderRadius: tokens.radius.card,
            border: "1px solid rgba(245, 158, 11, 0.35)",
            borderLeft: `4px solid ${tokens.accent.amber}`,
            padding: "32px 28px",
            display: "flex",
            flexDirection: "column",
            justifyContent: "space-between",
            boxShadow: "0 20px 48px -12px rgba(245, 158, 11, 0.22)",
          }}
        >
          <div>
            <div
              style={{
                fontSize: "15px",
                fontWeight: 700,
                textTransform: "uppercase",
                letterSpacing: "0.08em",
                color: tokens.accent.amber,
                marginBottom: "8px",
              }}
            >
              {endLabel}
            </div>
            <div
              style={{
                fontSize: displayEndValue.length > 14 ? "30px" : displayEndValue.length > 8 ? "40px" : "54px",
                fontWeight: 800,
                color: tokens.accent.amber,
                lineHeight: 1.1,
                marginBottom: "12px",
              }}
            >
              {displayEndValue}
            </div>
            <div
              style={{
                fontSize: "15px",
                color: tokens.text.secondary,
                lineHeight: 1.4,
              }}
            >
              {annotation ||
                (growthType === "compound"
                  ? "The compounding snowball drives exponential wealth expansion"
                  : "Final accumulated wealth achieved over time")}
            </div>
          </div>

          <div
            style={{
              marginTop: "24px",
              padding: "10px 14px",
              borderRadius: tokens.radius.chip,
              backgroundColor: "rgba(245, 158, 11, 0.12)",
              border: "1px solid rgba(245, 158, 11, 0.3)",
              fontSize: "14px",
              fontWeight: 700,
              color: tokens.accent.amber,
              textAlign: "center",
            }}
          >
            🚀 Payoff: Wealth Acceleration
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
}
