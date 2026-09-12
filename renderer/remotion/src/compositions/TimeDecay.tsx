import React from 'react';
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { tokens } from '../design-tokens';
import { TimeDecayProps } from '../types';

export function TimeDecay(props: TimeDecayProps | any) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const resolvedProps: TimeDecayProps = (props as any).props || props;
  const duration_frames = (props as any).duration_frames || 180;

  const fixedAmount = resolvedProps.fixedAmount || "0";
  const amountLabel = resolvedProps.amountLabel || "Fixed Sum";
  const timePeriod = resolvedProps.timePeriod || "Over Time";
  const annotation = resolvedProps.annotation || null;
  const showChart = resolvedProps.showChart !== false;

  // Scene fade
  const sceneOpacity = interpolate(frame, [0, 8], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Left anchor motion
  const anchorSpring = spring({
    frame: Math.max(0, frame - 8),
    fps,
    config: { damping: 15, stiffness: 105 },
  });
  const anchorY = interpolate(anchorSpring, [0, 1], [30, 0]);
  const anchorOpacity = interpolate(anchorSpring, [0, 1], [0, 1]);

  // Curve draw progress
  const curveProgress = interpolate(
    frame,
    [24, Math.min(duration_frames * 0.65, 80)],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // Origin dot spring
  const startDotSpring = spring({
    frame: Math.max(0, frame - 20),
    fps,
    config: { damping: 12, stiffness: 140 },
  });

  // End hollow ring spring
  const endDotSpring = spring({
    frame: Math.max(0, frame - 65),
    fps,
    config: { damping: 12, stiffness: 130 },
  });

  // Annotation callout spring
  const annotSpring = spring({
    frame: Math.max(0, frame - 72),
    fps,
    config: { damping: 14, stiffness: 110 },
  });
  const annotY = interpolate(annotSpring, [0, 1], [24, 0]);
  const annotOpacity = interpolate(annotSpring, [0, 1], [0, 1]);

  // SVG dimensions for chart
  const svgWidth = 720;
  const svgHeight = 280;
  const pathData = `M 40 40 C 260 40, 420 220, 680 230`;

  return (
    <AbsoluteFill
      style={{
        backgroundColor: tokens.bg.base,
        fontFamily: tokens.font.family,
        opacity: sceneOpacity,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "60px 100px",
        overflow: "hidden",
      }}
    >
      <div
        style={{
          display: "flex",
          flexDirection: "row",
          alignItems: "center",
          justifyContent: "space-between",
          width: "100%",
          maxWidth: "1600px",
          gap: "60px",
        }}
      >
        {/* Left: Fixed Nominal Anchor */}
        <div
          style={{
            opacity: anchorOpacity,
            transform: `translateY(${anchorY}px)`,
            flex: 0.9,
            maxWidth: "460px",
            backgroundColor: tokens.bg.cardLeft,
            borderRadius: tokens.radius.card,
            border: `1px solid ${tokens.bg.border}`,
            padding: "44px 40px",
            display: "flex",
            flexDirection: "column",
            boxShadow: "0 20px 40px -15px rgba(0, 0, 0, 0.5)",
          }}
        >
          <div
            style={{
              fontSize: "18px",
              fontWeight: 600,
              textTransform: "uppercase",
              letterSpacing: "0.06em",
              color: tokens.text.secondary,
              marginBottom: "16px",
            }}
          >
            {amountLabel}
          </div>
          <div
            style={{
              fontSize: "68px",
              fontWeight: 800,
              color: tokens.text.primary,
              lineHeight: 1.1,
              marginBottom: "24px",
            }}
          >
            {fixedAmount}
          </div>
          <div
            style={{
              fontSize: "20px",
              fontWeight: 600,
              color: tokens.accent.cyan,
              backgroundColor: "rgba(56, 189, 248, 0.1)",
              padding: "10px 18px",
              borderRadius: tokens.radius.chip,
              alignSelf: "flex-start",
              border: `1px solid rgba(56, 189, 248, 0.25)`,
            }}
          >
            Horizon: {timePeriod}
          </div>
        </div>

        {/* Right: Decay Trajectory Panel */}
        <div
          style={{
            flex: 1.3,
            backgroundColor: tokens.bg.surface,
            borderRadius: tokens.radius.card,
            border: `1px solid ${tokens.bg.border}`,
            padding: "36px 44px",
            display: "flex",
            flexDirection: "column",
            boxShadow: "0 20px 40px -15px rgba(0, 0, 0, 0.6)",
            position: "relative",
          }}
        >
          {/* Axis Labels */}
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              marginBottom: "12px",
              fontSize: "16px",
              fontWeight: 600,
              textTransform: "uppercase",
              letterSpacing: "0.06em",
              color: tokens.text.muted,
            }}
          >
            <span>Starting (Day 1)</span>
            <span>{timePeriod}</span>
          </div>

          {showChart ? (
            <div style={{ position: "relative", width: `${svgWidth}px`, height: `${svgHeight}px` }}>
              <svg width={svgWidth} height={svgHeight} viewBox={`0 0 ${svgWidth} ${svgHeight}`}>
                <defs>
                  <linearGradient id="decayGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor={tokens.accent.emerald} />
                    <stop offset="50%" stopColor={tokens.accent.amber} />
                    <stop offset="100%" stopColor={tokens.accent.rose} />
                  </linearGradient>
                </defs>

                {/* Grid guidelines */}
                <line x1="40" y1="40" x2="680" y2="40" stroke="rgba(255,255,255,0.06)" strokeDasharray="4 4" />
                <line x1="40" y1="230" x2="680" y2="230" stroke="rgba(255,255,255,0.06)" strokeDasharray="4 4" />

                {/* Animated decaying curve */}
                <path
                  d={pathData}
                  stroke="url(#decayGrad)"
                  strokeWidth="5"
                  fill="none"
                  strokeLinecap="round"
                  strokeDasharray="900"
                  strokeDashoffset={900 * (1 - curveProgress)}
                />

                {/* Start origin dot */}
                <circle
                  cx="40"
                  cy="40"
                  r={7 * startDotSpring}
                  fill={tokens.accent.emerald}
                  stroke="#ffffff"
                  strokeWidth="2"
                />

                {/* End hollow depleted marker */}
                <circle
                  cx="680"
                  cy="230"
                  r={8 * endDotSpring}
                  fill="none"
                  stroke={tokens.accent.rose}
                  strokeWidth="3.5"
                />
              </svg>
            </div>
          ) : (
            <div style={{ height: "160px", display: "flex", alignItems: "center", justifyContent: "center" }}>
              <div style={{ fontSize: "32px", fontWeight: 700, color: tokens.accent.rose }}>
                Substantial Real-Value Decline
              </div>
            </div>
          )}

          {/* Editorial Callout */}
          {annotation && (
            <div
              style={{
                opacity: annotOpacity,
                transform: `translateY(${annotY}px)`,
                marginTop: "16px",
                padding: "16px 24px",
                borderRadius: tokens.radius.chip,
                backgroundColor: "rgba(244, 63, 94, 0.12)",
                border: `1px solid rgba(244, 63, 94, 0.35)`,
                borderLeft: `5px solid ${tokens.accent.rose}`,
                color: tokens.text.primary,
                fontSize: "20px",
                fontWeight: 600,
                display: "flex",
                alignItems: "center",
              }}
            >
              {annotation}
            </div>
          )}
        </div>
      </div>
    </AbsoluteFill>
  );
};
