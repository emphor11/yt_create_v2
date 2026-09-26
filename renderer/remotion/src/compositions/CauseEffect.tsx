import React from 'react';
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { tokens } from '../design-tokens';
import { CauseEffectProps } from '../types';
import { safeAnimationWindow, safeSpringDelay } from '../animation-safety';

// ---------------------------------------------------------------------------
// Atmospheric Backdrop Component (Clean Editorial Style)
// ---------------------------------------------------------------------------

interface EditorialBackdropProps {
  glowColor: string;
  glowOpacity?: number;
}

function EditorialBackdrop({ glowColor, glowOpacity = 0.12 }: EditorialBackdropProps) {
  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#060911",
        overflow: "hidden",
        pointerEvents: "none",
        zIndex: 0,
      }}
    >
      {/* Deep Multi-stop Cinematic Vignette */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: "radial-gradient(ellipse 95% 75% at 50% 46%, #0b1222 0%, #060913 65%, #020408 100%)",
        }}
      />

      {/* Atmospheric Soft Aura behind the outcome destination */}
      <div
        style={{
          position: "absolute",
          width: "980px",
          height: "680px",
          right: "100px",
          top: "48%",
          transform: "translateY(-50%)",
          borderRadius: "50%",
          background: `radial-gradient(ellipse at center, ${glowColor} 0%, transparent 68%)`,
          filter: "blur(44px)",
          opacity: glowOpacity,
        }}
      />

      {/* Ultra-faint Editorial Datum Lines (<= 0.035 opacity) */}
      <div
        style={{
          position: "absolute",
          top: "84px",
          left: "140px",
          right: "140px",
          height: "1px",
          background: "linear-gradient(90deg, transparent 0%, rgba(255, 255, 255, 0.035) 15%, rgba(255, 255, 255, 0.035) 85%, transparent 100%)",
        }}
      />
      <div
        style={{
          position: "absolute",
          bottom: "84px",
          left: "140px",
          right: "140px",
          height: "1px",
          background: "linear-gradient(90deg, transparent 0%, rgba(255, 255, 255, 0.035) 15%, rgba(255, 255, 255, 0.035) 85%, transparent 100%)",
        }}
      />
    </AbsoluteFill>
  );
}

// ---------------------------------------------------------------------------
// Main CauseEffect Component
// ---------------------------------------------------------------------------

export function CauseEffect(props: CauseEffectProps | any) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const resolvedProps: CauseEffectProps = (props as any).props || props;
  const duration_frames = (props as any).duration_frames || 180;

  const rawCauses = Array.isArray(resolvedProps.causes) && resolvedProps.causes.length > 0
    ? resolvedProps.causes
    : [{ label: "Contributing Cause", value: null }];
  const causes = rawCauses.slice(0, 3);
  const causeCount = causes.length;

  const connector = (resolvedProps.connector || "leads to").trim();
  const outcomeLabel = resolvedProps.outcomeLabel || "Outcome";
  const outcomeValue = resolvedProps.outcomeValue || null;
  const outcomeSeverity = resolvedProps.outcomeSeverity || "neutral";
  const outcomeHeaderLabel = resolvedProps.outcomeHeaderLabel || null;
  const outcomeNote = resolvedProps.outcomeNote || null;
  const polarity = resolvedProps.polarity || outcomeSeverity;
  const headerLabel = resolvedProps.headerLabel || null;

  // Determine editorial color scheme
  const effectivePolarity = (polarity || outcomeSeverity || "neutral").toLowerCase();

  let accentColor = tokens.accent.cyan || "#38bdf8";
  let glowColorRgb = "56, 189, 248";
  let badgeText = "RESULTING OUTCOME";

  if (effectivePolarity === "positive") {
    accentColor = tokens.accent.emerald || "#10b981";
    glowColorRgb = "16, 185, 129";
    badgeText = "POSITIVE PAYOFF";
  } else if (effectivePolarity === "negative" || effectivePolarity === "critical") {
    accentColor = tokens.accent.rose || "#f43f5e";
    glowColorRgb = "244, 63, 94";
    badgeText = effectivePolarity === "critical" ? "CRITICAL OUTCOME" : "SYSTEMIC RISK";
  } else if (effectivePolarity === "warning") {
    accentColor = tokens.accent.amber || "#f59e0b";
    glowColorRgb = "245, 158, 11";
    badgeText = "DOWNSIDE EXPOSURE";
  }

  if (outcomeHeaderLabel) {
    badgeText = outcomeHeaderLabel;
  }

  // Duration-safe scene fade
  const sceneOpacity = interpolate(
    frame,
    [0, Math.min(8, Math.max(1, duration_frames - 1))],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // Sub-threshold camera motion: remains below noticeable threshold (1.000 -> 1.006)
  const cameraScale = interpolate(
    frame,
    [0, Math.max(1, duration_frames)],
    [1.000, 1.006],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // -------------------------------------------------------------------------
  // Duration-Adaptive Choreography Windows (Target ratios scaled to duration)
  // -------------------------------------------------------------------------
  const [conduitStart, conduitEnd] = safeAnimationWindow(
    Math.round(14 * Math.min(1, duration_frames / 120)),
    Math.round(36 * Math.min(1, duration_frames / 120)),
    duration_frames
  );
  const conduitProgress = interpolate(frame, [conduitStart, conduitEnd], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Subtle pulse transmission along the conduit
  const [pulseStart, pulseEnd] = safeAnimationWindow(
    Math.round(18 * Math.min(1, duration_frames / 120)),
    Math.round(42 * Math.min(1, duration_frames / 120)),
    duration_frames
  );
  const pulseProgress = interpolate(frame, [pulseStart, pulseEnd], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Pulse opacity: smooth fade in, high visibility during transit, gentle fade out at destination
  const pulseOpacity = interpolate(
    pulseProgress,
    [0, 0.12, 0.88, 1],
    [0, 0.85, 0.85, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // Connector verb label resolution
  const [verbStart, verbEnd] = safeAnimationWindow(
    Math.round(20 * Math.min(1, duration_frames / 120)),
    Math.round(38 * Math.min(1, duration_frames / 120)),
    duration_frames
  );
  const verbOpacity = interpolate(frame, [verbStart, verbEnd], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Outcome activation (spring triggers as pulse approaches destination)
  const outcomeDelay = safeSpringDelay(
    Math.round(28 * Math.min(1, duration_frames / 120)),
    duration_frames,
    0.50
  );
  const outcomeSpring = spring({
    frame: Math.max(0, frame - outcomeDelay),
    fps,
    config: { damping: 18, stiffness: 120, mass: 0.95 },
  });
  const outcomeX = interpolate(outcomeSpring, [0, 1], [22, 0]);
  const outcomeOpacity = interpolate(outcomeSpring, [0, 1], [0, 1]);

  // Dynamic vertical metrics for causes column
  const stageHeight = 500;
  let causeRowPositions: number[] = [250]; // Y center coordinate
  let causeCardHeight = 110;
  let causeCardGap = 0;

  if (causeCount === 2) {
    causeRowPositions = [165, 335];
    causeCardHeight = 110;
    causeCardGap = 30;
  } else if (causeCount === 3) {
    causeRowPositions = [115, 250, 385];
    causeCardHeight = 90;
    causeCardGap = 20;
  }

  // Calculate pulse position along the conduit
  // Conduit width is 270px (from 0 to 250), merging at x=135, y=250
  const pulsePositions = causes.map((_, idx) => {
    const startY = causeRowPositions[idx];
    if (causeCount === 1) {
      return { x: pulseProgress * 248, y: 250 };
    }
    if (pulseProgress <= 0.5) {
      const t = pulseProgress / 0.5;
      const x = t * 135;
      const y = startY + (250 - startY) * (t * t * (3 - 2 * t));
      return { x, y };
    } else {
      const t = (pulseProgress - 0.5) / 0.5;
      const x = 135 + t * 113;
      return { x, y: 250 };
    }
  });

  return (
    <AbsoluteFill
      style={{
        fontFamily: tokens.font.family,
        opacity: sceneOpacity,
        transform: `scale(${cameraScale})`,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "60px 120px",
        overflow: "hidden",
      }}
    >
      <EditorialBackdrop glowColor={`rgba(${glowColorRgb}, 0.16)`} glowOpacity={0.6 + outcomeOpacity * 0.4} />

      {/* Top Editorial Eyebrow / Scene Header */}
      {headerLabel && (
        <div
          style={{
            position: "absolute",
            top: "84px",
            left: "140px",
            display: "flex",
            alignItems: "center",
            gap: "10px",
            zIndex: 2,
          }}
        >
          <div
            style={{
              fontSize: "15px",
              fontWeight: 700,
              textTransform: "uppercase",
              letterSpacing: "0.14em",
              color: "#64748b",
            }}
          >
            {headerLabel}
          </div>
        </div>
      )}

      {/* Main Causal Editorial Stage (16:9 Balanced) */}
      <div
        style={{
          position: "relative",
          zIndex: 1,
          display: "flex",
          flexDirection: "row",
          alignItems: "center",
          justifyContent: "space-between",
          width: "100%",
          maxWidth: "1540px",
          height: `${stageHeight}px`,
        }}
      >
        {/* ================================================================ */}
        {/* LEFT WING: Editorial Input Plaques (Causes)                      */}
        {/* ================================================================ */}
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
            gap: `${causeCardGap}px`,
            width: "480px",
            height: `${stageHeight}px`,
            flexShrink: 0,
          }}
        >
          {causes.map((cause, index) => {
            const causeDelay = safeSpringDelay(
              Math.round((6 + index * 9) * Math.min(1, duration_frames / 120)),
              duration_frames,
              0.35
            );
            const causeSpring = spring({
              frame: Math.max(0, frame - causeDelay),
              fps,
              config: { damping: 18, stiffness: 120, mass: 0.95 },
            });
            const cX = interpolate(causeSpring, [0, 1], [-24, 0]);
            const cOpacity = interpolate(causeSpring, [0, 1], [0, 1]);

            return (
              <div
                key={index}
                style={{
                  opacity: cOpacity,
                  transform: `translateX(${cX}px)`,
                  minHeight: `${causeCardHeight}px`,
                  backgroundColor: "rgba(15, 23, 42, 0.65)",
                  borderRadius: "10px",
                  border: "1px solid rgba(255, 255, 255, 0.08)",
                  borderLeft: `4px solid ${accentColor}`,
                  padding: causeCount === 3 ? "14px 22px" : "18px 26px",
                  display: "flex",
                  alignItems: "center",
                  boxShadow: "0 8px 24px rgba(0, 0, 0, 0.45)",
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
                  {/* Subtle Datum / Index Marker */}
                  <div
                    style={{
                      width: "34px",
                      height: "34px",
                      borderRadius: "6px",
                      backgroundColor: "rgba(255, 255, 255, 0.05)",
                      border: "1px solid rgba(255, 255, 255, 0.10)",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      fontSize: "14px",
                      fontWeight: 700,
                      color: "#94a3b8",
                      fontVariantNumeric: "tabular-nums lining-nums",
                      flexShrink: 0,
                    }}
                  >
                    {cause.icon && cause.icon.length <= 2 ? cause.icon : `0${index + 1}`}
                  </div>

                  {/* Input Typography */}
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div
                      style={{
                        fontSize: causeCount === 3 ? "20px" : "23px",
                        fontWeight: 600,
                        color: "#f1f5f9",
                        lineHeight: 1.25,
                        letterSpacing: "-0.01em",
                      }}
                    >
                      {cause.label}
                    </div>
                    {cause.value && (
                      <div
                        style={{
                          fontSize: causeCount === 3 ? "16px" : "18px",
                          fontWeight: 700,
                          color: accentColor,
                          marginTop: "4px",
                          fontVariantNumeric: "tabular-nums lining-nums",
                          letterSpacing: "-0.02em",
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
        {/* CENTER: Dynamic Kinetic Conduit & Mechanism                      */}
        {/* ================================================================ */}
        <div
          style={{
            width: "270px",
            height: `${stageHeight}px`,
            position: "relative",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            flexShrink: 0,
          }}
        >
          {/* Dynamic Splines SVG */}
          <svg
            width="270"
            height={stageHeight}
            viewBox={`0 0 270 ${stageHeight}`}
            style={{ overflow: "visible", position: "absolute", inset: 0 }}
          >
            {/* Guide tracks (subtle background path) */}
            {causeCount === 1 && (
              <line
                x1="0"
                y1="250"
                x2="248"
                y2="250"
                stroke="rgba(255, 255, 255, 0.08)"
                strokeWidth="2"
              />
            )}
            {causeCount === 2 && (
              <>
                <path
                  d="M 0 165 C 65 165, 95 250, 135 250"
                  stroke="rgba(255, 255, 255, 0.08)"
                  strokeWidth="2"
                  fill="none"
                />
                <path
                  d="M 0 335 C 65 335, 95 250, 135 250"
                  stroke="rgba(255, 255, 255, 0.08)"
                  strokeWidth="2"
                  fill="none"
                />
                <line
                  x1="135"
                  y1="250"
                  x2="248"
                  y2="250"
                  stroke="rgba(255, 255, 255, 0.08)"
                  strokeWidth="2"
                />
              </>
            )}
            {causeCount === 3 && (
              <>
                <path
                  d="M 0 115 C 65 115, 95 250, 135 250"
                  stroke="rgba(255, 255, 255, 0.08)"
                  strokeWidth="2"
                  fill="none"
                />
                <line
                  x1="0"
                  y1="250"
                  x2="135"
                  y2="250"
                  stroke="rgba(255, 255, 255, 0.08)"
                  strokeWidth="2"
                />
                <path
                  d="M 0 385 C 65 385, 95 250, 135 250"
                  stroke="rgba(255, 255, 255, 0.08)"
                  strokeWidth="2"
                  fill="none"
                />
                <line
                  x1="135"
                  y1="250"
                  x2="248"
                  y2="250"
                  stroke="rgba(255, 255, 255, 0.08)"
                  strokeWidth="2"
                />
              </>
            )}

            {/* Active Drawing Paths */}
            {causeCount === 1 && (
              <>
                <line
                  x1="0"
                  y1="250"
                  x2="248"
                  y2="250"
                  stroke={accentColor}
                  strokeWidth="2.5"
                  strokeDasharray="248"
                  strokeDashoffset={248 * (1 - conduitProgress)}
                />
                <path
                  d="M 238 243 L 248 250 L 238 257"
                  stroke={accentColor}
                  strokeWidth="2.5"
                  fill="none"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  opacity={conduitProgress > 0.85 ? 1 : 0}
                />
              </>
            )}
            {causeCount === 2 && (
              <>
                <path
                  d="M 0 165 C 65 165, 95 250, 135 250"
                  stroke={accentColor}
                  strokeWidth="2.5"
                  fill="none"
                  strokeLinecap="round"
                  strokeDasharray="280"
                  strokeDashoffset={280 * (1 - conduitProgress)}
                />
                <path
                  d="M 0 335 C 65 335, 95 250, 135 250"
                  stroke={accentColor}
                  strokeWidth="2.5"
                  fill="none"
                  strokeLinecap="round"
                  strokeDasharray="280"
                  strokeDashoffset={280 * (1 - conduitProgress)}
                />
                <line
                  x1="135"
                  y1="250"
                  x2="248"
                  y2="250"
                  stroke={accentColor}
                  strokeWidth="2.5"
                  opacity={conduitProgress > 0.6 ? 1 : 0}
                />
                <path
                  d="M 238 243 L 248 250 L 238 257"
                  stroke={accentColor}
                  strokeWidth="2.5"
                  fill="none"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  opacity={conduitProgress > 0.85 ? 1 : 0}
                />
              </>
            )}
            {causeCount === 3 && (
              <>
                <path
                  d="M 0 115 C 65 115, 95 250, 135 250"
                  stroke={accentColor}
                  strokeWidth="2"
                  fill="none"
                  strokeLinecap="round"
                  strokeDasharray="290"
                  strokeDashoffset={290 * (1 - conduitProgress)}
                />
                <line
                  x1="0"
                  y1="250"
                  x2="135"
                  y2="250"
                  stroke={accentColor}
                  strokeWidth="2"
                  strokeDasharray="135"
                  strokeDashoffset={135 * (1 - conduitProgress)}
                />
                <path
                  d="M 0 385 C 65 385, 95 250, 135 250"
                  stroke={accentColor}
                  strokeWidth="2"
                  fill="none"
                  strokeLinecap="round"
                  strokeDasharray="290"
                  strokeDashoffset={290 * (1 - conduitProgress)}
                />
                <line
                  x1="135"
                  y1="250"
                  x2="248"
                  y2="250"
                  stroke={accentColor}
                  strokeWidth="2.5"
                  opacity={conduitProgress > 0.6 ? 1 : 0}
                />
                <path
                  d="M 238 243 L 248 250 L 238 257"
                  stroke={accentColor}
                  strokeWidth="2.5"
                  fill="none"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  opacity={conduitProgress > 0.85 ? 1 : 0}
                />
              </>
            )}

            {/* Traveling Restrained Editorial Pulse Dots */}
            {pulsePositions.map((pos, pIdx) => (
              <circle
                key={pIdx}
                cx={pos.x}
                cy={pos.y}
                r="3.5"
                fill={accentColor}
                opacity={pulseOpacity}
                style={{
                  filter: `drop-shadow(0 0 5px ${accentColor})`,
                }}
              />
            ))}
          </svg>

          {/* Central Connector Verb Label */}
          <div
            style={{
              position: "absolute",
              left: "48%",
              top: "50%",
              transform: "translate(-50%, -50%)",
              padding: "5px 14px",
              borderRadius: "6px",
              backgroundColor: "rgba(11, 18, 34, 0.94)",
              border: `1px solid rgba(255, 255, 255, 0.12)`,
              boxShadow: "0 4px 16px rgba(0, 0, 0, 0.6)",
              fontSize: "12px",
              fontWeight: 700,
              textTransform: "uppercase",
              letterSpacing: "0.12em",
              color: "#cbd5e1",
              whiteSpace: "nowrap",
              opacity: verbOpacity,
              zIndex: 2,
            }}
          >
            {connector}
          </div>
        </div>

        {/* ================================================================ */}
        {/* RIGHT WING: The Consequence Destination (Cardless Architecture)  */}
        {/* ================================================================ */}
        <div
          style={{
            position: "relative",
            width: "660px",
            minHeight: "420px",
            display: "flex",
            flexDirection: "row",
            alignItems: "center",
            opacity: outcomeOpacity,
            transform: `translateX(${outcomeX}px)`,
            flexShrink: 0,
          }}
        >
          {/* Subtle Vertical Editorial Gradient Divider */}
          <div
            style={{
              width: "2px",
              height: "280px",
              background: `linear-gradient(180deg, transparent 0%, rgba(255, 255, 255, 0.18) 20%, rgba(255, 255, 255, 0.18) 80%, transparent 100%)`,
              marginRight: "40px",
              flexShrink: 0,
            }}
          />

          {/* Destination Content */}
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              justifyContent: "center",
              flex: 1,
            }}
          >
            {/* Eyebrow Datum */}
            <div
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: "8px",
                marginBottom: "20px",
              }}
            >
              <span
                style={{
                  width: "7px",
                  height: "7px",
                  borderRadius: "50%",
                  backgroundColor: accentColor,
                  boxShadow: `0 0 10px ${accentColor}`,
                }}
              />
              <span
                style={{
                  fontSize: "15px",
                  fontWeight: 700,
                  textTransform: "uppercase",
                  letterSpacing: "0.12em",
                  color: accentColor,
                }}
              >
                {badgeText}
              </span>
            </div>

            {/* Primary Outcome Statement */}
            <div
              style={{
                fontSize: outcomeValue ? "42px" : "48px",
                fontWeight: 800,
                color: "#f8fafc",
                lineHeight: 1.18,
                letterSpacing: "-0.02em",
                marginBottom: outcomeValue ? "18px" : "0",
              }}
            >
              {outcomeLabel}
            </div>

            {/* Dominant Resulting Value (if present and meaningful) */}
            {outcomeValue && (
              <div
                style={{
                  fontSize: "58px",
                  fontWeight: 800,
                  color: accentColor,
                  lineHeight: 1.05,
                  letterSpacing: "-0.03em",
                  fontVariantNumeric: "tabular-nums lining-nums",
                  textShadow: `0 6px 28px rgba(0, 0, 0, 0.7), 0 0 45px rgba(${glowColorRgb}, 0.3)`,
                  marginBottom: outcomeNote ? "22px" : "0",
                }}
              >
                {outcomeValue}
              </div>
            )}

            {/* Editorial Outcome Note / Footnote (if present) */}
            {outcomeNote && (
              <div
                style={{
                  fontSize: "17px",
                  fontWeight: 500,
                  color: "#94a3b8",
                  lineHeight: 1.45,
                  maxWidth: "580px",
                  letterSpacing: "-0.01em",
                  paddingTop: "14px",
                  borderTop: "1px solid rgba(255, 255, 255, 0.08)",
                }}
              >
                {outcomeNote}
              </div>
            )}
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
}
