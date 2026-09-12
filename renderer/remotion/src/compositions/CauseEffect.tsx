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

  const causes = Array.isArray(resolvedProps.causes) && resolvedProps.causes.length > 0
    ? resolvedProps.causes.slice(0, 3)
    : [{ label: "Contributing Cause", value: null }];
  const connector = resolvedProps.connector || "leads to";
  const outcomeLabel = resolvedProps.outcomeLabel || "Outcome";
  const outcomeValue = resolvedProps.outcomeValue || null;
  const outcomeSeverity = resolvedProps.outcomeSeverity || "neutral";

  // Determine severity color
  let severityColor = tokens.accent.primary;
  if (outcomeSeverity === "negative" || outcomeSeverity === "critical") {
    severityColor = tokens.accent.rose;
  } else if (outcomeSeverity === "positive") {
    severityColor = tokens.accent.emerald;
  } else if (outcomeSeverity === "warning") {
    severityColor = tokens.accent.amber;
  }

  // Scene fade
  const sceneOpacity = interpolate(frame, [0, Math.min(8, Math.max(1, duration_frames - 1))], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Arrows progress
  const [arrowStart, arrowEnd] = safeAnimationWindow(30, 54, duration_frames);
  const arrowProgress = interpolate(frame, [arrowStart, arrowEnd], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Outcome card motion
  const outcomeDelay = safeSpringDelay(46, duration_frames, 0.65);
  const outcomeSpring = spring({
    frame: Math.max(0, frame - outcomeDelay),
    fps,
    config: { damping: 14, stiffness: 105 },
  });
  const outcomeX = interpolate(outcomeSpring, [0, 1], [60, 0]);
  const outcomeOpacity = interpolate(outcomeSpring, [0, 1], [0, 1]);

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
          justifyContent: "center",
          width: "100%",
          maxWidth: "1550px",
          gap: "36px",
        }}
      >
        {/* Left: Causes Column */}
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            gap: "20px",
            flex: 1,
            maxWidth: "460px",
          }}
        >
          {causes.map((cause, index) => {
            const causeDelay = safeSpringDelay(8 + index * 12, duration_frames, 0.4);
            const causeSpring = spring({
              frame: Math.max(0, frame - causeDelay),
              fps,
              config: { damping: 15, stiffness: 110 },
            });
            const cX = interpolate(causeSpring, [0, 1], [-50, 0]);
            const cOpacity = interpolate(causeSpring, [0, 1], [0, 1]);

            return (
              <div
                key={index}
                style={{
                  opacity: cOpacity,
                  transform: `translateX(${cX}px)`,
                  backgroundColor: tokens.bg.cardLeft,
                  borderRadius: tokens.radius.card,
                  border: `1px solid ${tokens.bg.border}`,
                  padding: "24px 30px",
                  display: "flex",
                  flexDirection: "column",
                  justifyContent: "center",
                  boxShadow: "0 10px 30px -10px rgba(0, 0, 0, 0.4)",
                  borderLeft: `4px solid ${tokens.accent.primary}`,
                }}
              >
                <div
                  style={{
                    fontSize: "24px",
                    fontWeight: 600,
                    color: tokens.text.primary,
                    lineHeight: 1.25,
                  }}
                >
                  {cause.label}
                </div>
                {cause.value && (
                  <div
                    style={{
                      fontSize: "20px",
                      fontWeight: 700,
                      color: tokens.accent.cyan,
                      marginTop: "8px",
                    }}
                  >
                    {cause.value}
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Center: Connector Section with Splines */}
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            width: "180px",
            position: "relative",
          }}
        >
          <svg
            width="180"
            height="180"
            viewBox="0 0 180 180"
            style={{ overflow: "visible" }}
          >
            {/* If single cause: straight line */}
            {causes.length === 1 && (
              <path
                d="M 0 90 L 170 90 M 155 80 L 170 90 L 155 100"
                stroke={severityColor}
                strokeWidth="3.5"
                fill="none"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeDasharray="200"
                strokeDashoffset={200 * (1 - arrowProgress)}
              />
            )}

            {/* If 2 causes: 2 converging splines */}
            {causes.length === 2 && (
              <>
                <path
                  d="M 0 45 C 80 45, 110 90, 170 90"
                  stroke={severityColor}
                  strokeWidth="3"
                  fill="none"
                  strokeLinecap="round"
                  strokeDasharray="240"
                  strokeDashoffset={240 * (1 - arrowProgress)}
                />
                <path
                  d="M 0 135 C 80 135, 110 90, 170 90"
                  stroke={severityColor}
                  strokeWidth="3"
                  fill="none"
                  strokeLinecap="round"
                  strokeDasharray="240"
                  strokeDashoffset={240 * (1 - arrowProgress)}
                />
                <path
                  d="M 155 80 L 170 90 L 155 100"
                  stroke={severityColor}
                  strokeWidth="3.5"
                  fill="none"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  opacity={arrowProgress > 0.8 ? 1 : 0}
                />
              </>
            )}

            {/* If 3 causes: 3 converging splines */}
            {causes.length === 3 && (
              <>
                <path
                  d="M 0 25 C 80 25, 110 90, 170 90"
                  stroke={severityColor}
                  strokeWidth="3"
                  fill="none"
                  strokeLinecap="round"
                  strokeDasharray="250"
                  strokeDashoffset={250 * (1 - arrowProgress)}
                />
                <path
                  d="M 0 90 L 170 90"
                  stroke={severityColor}
                  strokeWidth="3"
                  fill="none"
                  strokeLinecap="round"
                  strokeDasharray="180"
                  strokeDashoffset={180 * (1 - arrowProgress)}
                />
                <path
                  d="M 0 155 C 80 155, 110 90, 170 90"
                  stroke={severityColor}
                  strokeWidth="3"
                  fill="none"
                  strokeLinecap="round"
                  strokeDasharray="250"
                  strokeDashoffset={250 * (1 - arrowProgress)}
                />
                <path
                  d="M 155 80 L 170 90 L 155 100"
                  stroke={severityColor}
                  strokeWidth="3.5"
                  fill="none"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  opacity={arrowProgress > 0.8 ? 1 : 0}
                />
              </>
            )}
          </svg>

          {/* Connector Label */}
          <div
            style={{
              marginTop: "8px",
              fontSize: "16px",
              fontWeight: 600,
              textTransform: "uppercase",
              letterSpacing: "0.08em",
              color: tokens.text.secondary,
              textAlign: "center",
              lineHeight: 1.2,
            }}
          >
            {connector}
          </div>
        </div>

        {/* Right: Outcome Card */}
        <div
          style={{
            opacity: outcomeOpacity,
            transform: `translateX(${outcomeX}px)`,
            flex: 1.1,
            maxWidth: "520px",
            minHeight: "340px",
            backgroundColor: tokens.bg.surface,
            borderRadius: tokens.radius.card,
            border: `2px solid ${severityColor}`,
            padding: "44px 38px",
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
            boxShadow: `0 20px 50px -10px rgba(0, 0, 0, 0.6), 0 0 30px ${severityColor}22`,
          }}
        >
          <div
            style={{
              fontSize: "18px",
              fontWeight: 600,
              textTransform: "uppercase",
              letterSpacing: "0.06em",
              color: severityColor,
              marginBottom: "14px",
            }}
          >
            Resulting Outcome
          </div>
          <div
            style={{
              fontSize: "36px",
              fontWeight: 800,
              color: tokens.text.primary,
              lineHeight: 1.2,
              marginBottom: outcomeValue ? "18px" : "0",
            }}
          >
            {outcomeLabel}
          </div>
          {outcomeValue && (
            <div
              style={{
                fontSize: "28px",
                fontWeight: 700,
                color: severityColor,
              }}
            >
              {outcomeValue}
            </div>
          )}
        </div>
      </div>
    </AbsoluteFill>
  );
};
