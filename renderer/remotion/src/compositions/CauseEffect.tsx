import React from 'react';
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { tokens } from '../design-tokens';
import { CauseEffectProps } from '../types';
import { safeAnimationWindow, safeSpringDelay } from '../animation-safety';

export function CauseEffect(props: CauseEffectProps | any) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const resolvedProps: CauseEffectProps = (props as any).props || props;
  const duration_frames = (props as any).duration_frames || 180;

  const rawCauses = Array.isArray(resolvedProps.causes) && resolvedProps.causes.length > 0
    ? resolvedProps.causes
    : [{ label: "Contributing Cause", value: null }];
  const causes = rawCauses.slice(0, 3);
  const connector = (resolvedProps.connector || "leads to").trim();
  const outcomeLabel = resolvedProps.outcomeLabel || "Outcome";
  const outcomeValue = resolvedProps.outcomeValue || null;
  const outcomeSeverity = resolvedProps.outcomeSeverity || "neutral";
  const outcomeHeaderLabel = resolvedProps.outcomeHeaderLabel || null;
  const outcomeNote = resolvedProps.outcomeNote || null;
  const polarity = resolvedProps.polarity || outcomeSeverity;
  const headerLabel = resolvedProps.headerLabel || null;

  // Determine severity aesthetics and colors
  const effectivePolarity = (polarity || outcomeSeverity || "neutral").toLowerCase();

  let severityColor = tokens.accent.primary;
  let severityBg = "rgba(99, 102, 241, 0.12)";
  let severityBorder = "rgba(99, 102, 241, 0.40)";
  let glowColor = "rgba(99, 102, 241, 0.25)";
  let badgeText = "CAUSAL IMPACT";

  if (effectivePolarity === "positive") {
    severityColor = tokens.accent.emerald || "#10b981";
    severityBg = "rgba(16, 185, 129, 0.12)";
    severityBorder = "rgba(16, 185, 129, 0.45)";
    glowColor = "rgba(16, 185, 129, 0.30)";
    badgeText = "POSITIVE PAYOFF";
  } else if (effectivePolarity === "negative" || effectivePolarity === "critical") {
    severityColor = tokens.accent.rose || "#f43f5e";
    severityBg = "rgba(244, 63, 94, 0.12)";
    severityBorder = "rgba(244, 63, 94, 0.45)";
    glowColor = "rgba(244, 63, 94, 0.32)";
    badgeText = effectivePolarity === "critical" ? "CRITICAL OUTCOME" : "SYSTEMIC RISK";
  } else if (effectivePolarity === "warning") {
    severityColor = tokens.accent.amber || "#f59e0b";
    severityBg = "rgba(245, 158, 11, 0.12)";
    severityBorder = "rgba(245, 158, 11, 0.45)";
    glowColor = "rgba(245, 158, 11, 0.28)";
    badgeText = "DOWNSIDE EXPOSURE";
  } else {
    severityColor = tokens.accent.cyan || "#06b6d4";
    severityBg = "rgba(6, 182, 212, 0.12)";
    severityBorder = "rgba(6, 182, 212, 0.40)";
    glowColor = "rgba(6, 182, 212, 0.25)";
    badgeText = "RESULTING OUTCOME";
  }

  if (outcomeHeaderLabel) {
    badgeText = outcomeHeaderLabel;
  }

  // Duration-safe scene fade
  const sceneOpacity = interpolate(
    frame,
    [0, Math.min(8, Math.max(1, duration_frames - 1))],
    [0, 1],
    {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    }
  );

  // Dynamic spline draw progress
  const [arrowStart, arrowEnd] = safeAnimationWindow(22, 48, duration_frames);
  const arrowProgress = interpolate(frame, [arrowStart, arrowEnd], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Connector pill fade
  const pillOpacity = interpolate(frame, [arrowStart + 6, arrowEnd + 6], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Outcome card motion
  const outcomeDelay = safeSpringDelay(36, duration_frames, 0.60);
  const outcomeSpring = spring({
    frame: Math.max(0, frame - outcomeDelay),
    fps,
    config: { damping: 14, stiffness: 100 },
  });
  const outcomeX = interpolate(outcomeSpring, [0, 1], [40, 0]);
  const outcomeScale = interpolate(outcomeSpring, [0, 1], [0.95, 1]);
  const outcomeOpacity = interpolate(outcomeSpring, [0, 1], [0, 1]);

  // Stage geometry: H = 460px
  const causeCount = causes.length;
  let cardHeight = 190;
  let cardGap = 0;
  if (causeCount === 2) {
    cardHeight = 135;
    cardGap = 30;
  } else if (causeCount === 3) {
    cardHeight = 105;
    cardGap = 20;
  }

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
      {/* Background subtle radial ambient light */}
      <div
        style={{
          position: "absolute",
          width: "1200px",
          height: "800px",
          background: `radial-gradient(circle at 65% 50%, ${glowColor} 0%, rgba(10, 15, 29, 0) 65%)`,
          pointerEvents: "none",
          opacity: 0.6,
        }}
      />

      {/* Optional Top Eyebrow Header */}
      {headerLabel && (
        <div
          style={{
            position: "absolute",
            top: "60px",
            left: "100px",
            display: "flex",
            alignItems: "center",
            gap: "10px",
          }}
        >
          <div
            style={{
              fontSize: "14px",
              fontWeight: 700,
              textTransform: "uppercase",
              letterSpacing: "0.14em",
              color: tokens.text.muted,
            }}
          >
            {headerLabel}
          </div>
        </div>
      )}

      {/* Main Causal Stage */}
      <div
        style={{
          display: "flex",
          flexDirection: "row",
          alignItems: "center",
          justifyContent: "center",
          width: "100%",
          maxWidth: "1560px",
          height: "460px",
          gap: "24px",
          position: "relative",
          zIndex: 1,
        }}
      >
        {/* ================================================================ */}
        {/* LEFT: Causes Column                                              */}
        {/* ================================================================ */}
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
            gap: `${cardGap}px`,
            width: "460px",
            height: "460px",
            flexShrink: 0,
          }}
        >
          {causes.map((cause, index) => {
            const causeDelay = safeSpringDelay(6 + index * 10, duration_frames, 0.35);
            const causeSpring = spring({
              frame: Math.max(0, frame - causeDelay),
              fps,
              config: { damping: 15, stiffness: 110 },
            });
            const cX = interpolate(causeSpring, [0, 1], [-40, 0]);
            const cOpacity = interpolate(causeSpring, [0, 1], [0, 1]);

            return (
              <div
                key={index}
                style={{
                  opacity: cOpacity,
                  transform: `translateX(${cX}px)`,
                  height: `${cardHeight}px`,
                  backgroundColor: "rgba(17, 24, 39, 0.85)",
                  borderRadius: tokens.radius.card || "16px",
                  border: "1px solid rgba(255, 255, 255, 0.10)",
                  borderLeft: `4px solid ${tokens.accent.primary || "#6366f1"}`,
                  padding: causeCount === 3 ? "16px 24px" : causeCount === 2 ? "22px 28px" : "28px 32px",
                  display: "flex",
                  alignItems: "center",
                  boxShadow: "0 12px 30px -8px rgba(0, 0, 0, 0.5)",
                  backdropFilter: "blur(12px)",
                  boxSizing: "border-box",
                }}
              >
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "16px",
                    width: "100%",
                  }}
                >
                  {/* Number or Icon badge */}
                  <div
                    style={{
                      width: causeCount === 3 ? "32px" : "38px",
                      height: causeCount === 3 ? "32px" : "38px",
                      borderRadius: "8px",
                      backgroundColor: "rgba(255, 255, 255, 0.08)",
                      border: "1px solid rgba(255, 255, 255, 0.12)",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      fontSize: causeCount === 3 ? "14px" : "16px",
                      fontWeight: 700,
                      color: tokens.text.secondary,
                      flexShrink: 0,
                    }}
                  >
                    {cause.icon || `0${index + 1}`}
                  </div>

                  {/* Text content */}
                  <div style={{ flex: 1, minWidth: 0 }}>
                    {causeCount === 1 && (
                      <div
                        style={{
                          fontSize: "12px",
                          fontWeight: 700,
                          textTransform: "uppercase",
                          letterSpacing: "0.10em",
                          color: tokens.text.secondary,
                          marginBottom: "6px",
                        }}
                      >
                        PRIMARY DRIVER
                      </div>
                    )}
                    <div
                      style={{
                        fontSize: causeCount === 3 ? "20px" : causeCount === 2 ? "22px" : "26px",
                        fontWeight: 600,
                        color: tokens.text.primary,
                        lineHeight: 1.25,
                        overflow: "hidden",
                        textOverflow: "ellipsis",
                        whiteSpace: causeCount === 3 ? "nowrap" : "normal",
                      }}
                    >
                      {cause.label}
                    </div>
                    {cause.value && (
                      <div
                        style={{
                          fontSize: causeCount === 3 ? "16px" : "19px",
                          fontWeight: 700,
                          color: tokens.accent.cyan || "#38bdf8",
                          marginTop: "4px",
                          letterSpacing: "0.02em",
                        }}
                      >
                        {cause.value}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* ================================================================ */}
        {/* CENTER: Dynamic Connector & Splines                              */}
        {/* ================================================================ */}
        <div
          style={{
            width: "280px",
            height: "460px",
            position: "relative",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            flexShrink: 0,
          }}
        >
          {/* Dynamic Splines SVG */}
          <svg
            width="280"
            height="460"
            viewBox="0 0 280 460"
            style={{ overflow: "visible", position: "absolute", inset: 0 }}
          >
            <defs>
              <filter id="splineGlow" filterUnits="userSpaceOnUse" x="-50" y="-50" width="380" height="560">
                <feDropShadow dx="0" dy="0" stdDeviation="3" floodColor={severityColor} floodOpacity="0.55" />
              </filter>
            </defs>

            {/* Case 1: Single Cause (Straight beam from y=230 to y=230) */}
            {causeCount === 1 && (
              <>
                <path
                  d="M 0 230 L 265 230"
                  stroke={severityColor}
                  strokeWidth="4"
                  fill="none"
                  strokeLinecap="round"
                  strokeDasharray="270"
                  strokeDashoffset={270 * (1 - arrowProgress)}
                  filter="url(#splineGlow)"
                />
                <path
                  d="M 252 221 L 266 230 L 252 239"
                  stroke={severityColor}
                  strokeWidth="3.5"
                  fill="none"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  opacity={arrowProgress > 0.85 ? 1 : 0}
                  filter="url(#splineGlow)"
                />
              </>
            )}

            {/* Case 2: Dual Causes (Converging from y=148 and y=312 to y=230) */}
            {causeCount === 2 && (
              <>
                <path
                  d="M 0 148 C 60 148, 100 230, 140 230"
                  stroke={severityColor}
                  strokeWidth="3.5"
                  fill="none"
                  strokeLinecap="round"
                  strokeDasharray="280"
                  strokeDashoffset={280 * (1 - arrowProgress)}
                  filter="url(#splineGlow)"
                />
                <path
                  d="M 0 312 C 60 312, 100 230, 140 230"
                  stroke={severityColor}
                  strokeWidth="3.5"
                  fill="none"
                  strokeLinecap="round"
                  strokeDasharray="280"
                  strokeDashoffset={280 * (1 - arrowProgress)}
                  filter="url(#splineGlow)"
                />
                <path
                  d="M 140 230 L 265 230"
                  stroke={severityColor}
                  strokeWidth="3.5"
                  fill="none"
                  strokeLinecap="round"
                  filter="url(#splineGlow)"
                  opacity={arrowProgress > 0.65 ? 1 : 0}
                />
                <path
                  d="M 252 221 L 266 230 L 252 239"
                  stroke={severityColor}
                  strokeWidth="3.5"
                  fill="none"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  opacity={arrowProgress > 0.85 ? 1 : 0}
                  filter="url(#splineGlow)"
                />
              </>
            )}

            {/* Case 3: Three Causes (Converging from y=106, y=230, y=354 to y=230) */}
            {causeCount === 3 && (
              <>
                <path
                  d="M 0 106 C 50 106, 95 230, 140 230"
                  stroke={severityColor}
                  strokeWidth="3"
                  fill="none"
                  strokeLinecap="round"
                  strokeDasharray="290"
                  strokeDashoffset={290 * (1 - arrowProgress)}
                  filter="url(#splineGlow)"
                />
                <path
                  d="M 0 230 L 140 230"
                  stroke={severityColor}
                  strokeWidth="3"
                  fill="none"
                  strokeLinecap="round"
                  strokeDasharray="150"
                  strokeDashoffset={150 * (1 - arrowProgress)}
                  filter="url(#splineGlow)"
                />
                <path
                  d="M 0 354 C 50 354, 95 230, 140 230"
                  stroke={severityColor}
                  strokeWidth="3"
                  fill="none"
                  strokeLinecap="round"
                  strokeDasharray="290"
                  strokeDashoffset={290 * (1 - arrowProgress)}
                  filter="url(#splineGlow)"
                />
                <path
                  d="M 140 230 L 265 230"
                  stroke={severityColor}
                  strokeWidth="3.5"
                  fill="none"
                  strokeLinecap="round"
                  filter="url(#splineGlow)"
                  opacity={arrowProgress > 0.65 ? 1 : 0}
                />
                <path
                  d="M 252 221 L 266 230 L 252 239"
                  stroke={severityColor}
                  strokeWidth="3.5"
                  fill="none"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  opacity={arrowProgress > 0.85 ? 1 : 0}
                  filter="url(#splineGlow)"
                />
              </>
            )}
          </svg>

          {/* Central floating connector badge pill */}
          <div
            style={{
              position: "absolute",
              left: "50%",
              top: "50%",
              transform: "translate(-50%, -50%)",
              padding: "6px 14px",
              borderRadius: "20px",
              backgroundColor: "rgba(15, 23, 42, 0.92)",
              border: `1px solid ${severityBorder}`,
              boxShadow: `0 4px 14px rgba(0, 0, 0, 0.5), 0 0 12px ${glowColor}`,
              fontSize: "12px",
              fontWeight: 700,
              textTransform: "uppercase",
              letterSpacing: "0.1em",
              color: tokens.text.primary,
              whiteSpace: "nowrap",
              opacity: pillOpacity,
              backdropFilter: "blur(8px)",
              zIndex: 2,
            }}
          >
            {connector}
          </div>
        </div>

        {/* ================================================================ */}
        {/* RIGHT: Dominant Outcome Card                                     */}
        {/* ================================================================ */}
        <div
          style={{
            position: "relative",
            width: "640px",
            minHeight: "460px",
            flexShrink: 0,
          }}
        >
          {/* Atmospheric halo aura glow behind outcome card */}
          <div
            style={{
              position: "absolute",
              inset: "-12px",
              borderRadius: "28px",
              background: `radial-gradient(ellipse at center, ${glowColor} 0%, rgba(0, 0, 0, 0) 70%)`,
              filter: "blur(28px)",
              opacity: outcomeOpacity,
              pointerEvents: "none",
              zIndex: 0,
            }}
          />

          {/* Outcome Card Container */}
          <div
            style={{
              position: "relative",
              opacity: outcomeOpacity,
              transform: `translateX(${outcomeX}px) scale(${outcomeScale})`,
              width: "100%",
              minHeight: "460px",
              backgroundColor: "rgba(15, 23, 42, 0.90)",
              borderRadius: "22px",
              border: `2px solid ${severityBorder}`,
              padding: "44px 44px",
              display: "flex",
              flexDirection: "column",
              justifyContent: "space-between",
              boxShadow: `0 25px 60px -12px rgba(0, 0, 0, 0.75), 0 0 35px ${glowColor}`,
              backdropFilter: "blur(16px)",
              boxSizing: "border-box",
              zIndex: 1,
            }}
          >
            {/* Top Eyebrow Badge & Titles */}
            <div>
              <div
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "8px",
                  padding: "6px 16px",
                  borderRadius: "20px",
                  backgroundColor: severityBg,
                  border: `1px solid ${severityBorder}`,
                  marginBottom: "20px",
                }}
              >
                <span
                  style={{
                    width: "8px",
                    height: "8px",
                    borderRadius: "50%",
                    backgroundColor: severityColor,
                    boxShadow: `0 0 8px ${severityColor}`,
                  }}
                />
                <span
                  style={{
                    fontSize: "13px",
                    fontWeight: 700,
                    textTransform: "uppercase",
                    letterSpacing: "0.08em",
                    color: severityColor,
                  }}
                >
                  {badgeText}
                </span>
              </div>

              {/* Primary Outcome Label */}
              <div
                style={{
                  fontSize: outcomeValue ? "36px" : "44px",
                  fontWeight: 800,
                  color: tokens.text.primary,
                  lineHeight: 1.2,
                  letterSpacing: "-0.01em",
                }}
              >
                {outcomeLabel}
              </div>

              {/* Dominant Outcome Value (if present) */}
              {outcomeValue && (
                <div
                  style={{
                    marginTop: "16px",
                    display: "flex",
                    alignItems: "baseline",
                    gap: "12px",
                  }}
                >
                  <div
                    style={{
                      fontSize: "56px",
                      fontWeight: 800,
                      color: severityColor,
                      letterSpacing: "-0.02em",
                      lineHeight: 1.1,
                      textShadow: `0 0 24px ${glowColor}`,
                    }}
                  >
                    {outcomeValue}
                  </div>
                </div>
              )}
            </div>

            {/* Bottom Mechanism Note / Explanation Chip (if present) */}
            {outcomeNote && (
              <div
                style={{
                  marginTop: "24px",
                  padding: "14px 20px",
                  borderRadius: "12px",
                  backgroundColor: "rgba(255, 255, 255, 0.04)",
                  border: "1px solid rgba(255, 255, 255, 0.08)",
                  borderLeft: `3px solid ${severityColor}`,
                  display: "flex",
                  alignItems: "center",
                  gap: "12px",
                }}
              >
                <span style={{ fontSize: "16px", opacity: 0.85 }}>⚡</span>
                <span
                  style={{
                    fontSize: "16px",
                    fontWeight: 500,
                    color: tokens.text.secondary,
                    lineHeight: 1.35,
                  }}
                >
                  {outcomeNote}
                </span>
              </div>
            )}
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
}
