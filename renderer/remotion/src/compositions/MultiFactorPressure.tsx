import React from 'react';
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { tokens } from '../design-tokens';
import { MultiFactorPressureProps } from '../types';

export function MultiFactorPressure(props: MultiFactorPressureProps | any) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const resolvedProps: MultiFactorPressureProps = (props as any).props || props;

  const factors = Array.isArray(resolvedProps.factors) && resolvedProps.factors.length > 0
    ? resolvedProps.factors.slice(0, 4)
    : [
        { label: "High Inflation", value: "7%", severity: "high" },
        { label: "Weak Returns", value: "3%", severity: "medium" },
      ];
  const combinedLabel = resolvedProps.combinedLabel || "Combined Vulnerability";
  const combinedSeverity = resolvedProps.combinedSeverity || "critical";
  const outcomeNote = resolvedProps.outcomeNote || null;

  // Severity styling
  let severityColor = tokens.accent.rose;
  let severityBg = "rgba(244, 63, 94, 0.12)";
  if (combinedSeverity === "medium") {
    severityColor = tokens.accent.amber;
    severityBg = "rgba(245, 158, 11, 0.12)";
  }

  // Scene fade
  const sceneOpacity = interpolate(frame, [0, 8], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Converging arrows draw progress
  const rayProgress = interpolate(frame, [32, 58], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Central node impact spring
  const coreSpring = spring({
    frame: Math.max(0, frame - 50),
    fps,
    config: { mass: 1.2, damping: 18, stiffness: 100 },
  });
  const coreScale = interpolate(coreSpring, [0, 1], [0.85, 1]);
  const coreOpacity = interpolate(coreSpring, [0, 1], [0, 1]);

  // Single border glow pulse [74, 88]
  const pulseOpacity = interpolate(
    frame,
    [74, 81, 88],
    [0.4, 1.0, 0.6],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

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
          maxWidth: "1600px",
          gap: "40px",
        }}
      >
        {/* Left Column: Factor Cards */}
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            gap: "18px",
            flex: 1,
            maxWidth: "480px",
          }}
        >
          {factors.map((factor, index) => {
            const factorSpring = spring({
              frame: Math.max(0, frame - (8 + index * 10)),
              fps,
              config: { damping: 15, stiffness: 115 },
            });
            const fX = interpolate(factorSpring, [0, 1], [-50, 0]);
            const fOpacity = interpolate(factorSpring, [0, 1], [0, 1]);

            let badgeColor = tokens.accent.rose;
            if (factor.severity === "low") badgeColor = tokens.accent.emerald;
            else if (factor.severity === "medium") badgeColor = tokens.accent.amber;

            return (
              <div
                key={index}
                style={{
                  opacity: fOpacity,
                  transform: `translateX(${fX}px)`,
                  backgroundColor: tokens.bg.cardLeft,
                  borderRadius: tokens.radius.card,
                  border: `1px solid ${tokens.bg.border}`,
                  padding: "20px 26px",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  boxShadow: "0 10px 25px -8px rgba(0, 0, 0, 0.4)",
                  borderLeft: `4px solid ${badgeColor}`,
                }}
              >
                <div>
                  <div style={{ fontSize: "22px", fontWeight: 600, color: tokens.text.primary }}>
                    {factor.label}
                  </div>
                  {factor.value && (
                    <div style={{ fontSize: "20px", fontWeight: 700, color: tokens.accent.cyan, marginTop: "4px" }}>
                      {factor.value}
                    </div>
                  )}
                </div>

                {factor.severity && (
                  <div
                    style={{
                      fontSize: "14px",
                      fontWeight: 700,
                      textTransform: "uppercase",
                      letterSpacing: "0.06em",
                      color: badgeColor,
                      backgroundColor: "rgba(0,0,0,0.3)",
                      padding: "6px 12px",
                      borderRadius: tokens.radius.chip,
                    }}
                  >
                    {factor.severity}
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Center: Inward Converging Rays */}
        <div style={{ width: "160px", display: "flex", alignItems: "center", justifyContent: "center" }}>
          <svg width="160" height="200" viewBox="0 0 160 200" style={{ overflow: "visible" }}>
            <path
              d="M 0 40 C 70 40, 90 100, 150 100"
              stroke={severityColor}
              strokeWidth="3.5"
              fill="none"
              strokeLinecap="round"
              strokeDasharray="200"
              strokeDashoffset={200 * (1 - rayProgress)}
            />
            <path
              d="M 0 100 L 150 100"
              stroke={severityColor}
              strokeWidth="3.5"
              fill="none"
              strokeLinecap="round"
              strokeDasharray="160"
              strokeDashoffset={160 * (1 - rayProgress)}
            />
            <path
              d="M 0 160 C 70 160, 90 100, 150 100"
              stroke={severityColor}
              strokeWidth="3.5"
              fill="none"
              strokeLinecap="round"
              strokeDasharray="200"
              strokeDashoffset={200 * (1 - rayProgress)}
            />
            <path
              d="M 135 90 L 150 100 L 135 110"
              stroke={severityColor}
              strokeWidth="4"
              fill="none"
              strokeLinecap="round"
              strokeLinejoin="round"
              opacity={rayProgress > 0.8 ? 1 : 0}
            />
          </svg>
        </div>

        {/* Right: Central Vulnerability Core */}
        <div
          style={{
            opacity: coreOpacity,
            transform: `scale(${coreScale})`,
            flex: 1.2,
            maxWidth: "580px",
            minHeight: "360px",
            backgroundColor: tokens.bg.surface,
            borderRadius: tokens.radius.card,
            border: `2px solid rgba(244, 63, 94, ${pulseOpacity})`,
            padding: "44px 40px",
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
            boxShadow: `0 25px 60px -15px rgba(0,0,0,0.7), 0 0 40px rgba(244, 63, 94, 0.25)`,
          }}
        >
          <div
            style={{
              display: "inline-flex",
              alignSelf: "flex-start",
              padding: "6px 14px",
              borderRadius: tokens.radius.chip,
              backgroundColor: severityBg,
              color: severityColor,
              fontSize: "16px",
              fontWeight: 800,
              textTransform: "uppercase",
              letterSpacing: "0.08em",
              marginBottom: "16px",
            }}
          >
            {combinedSeverity} Threat
          </div>
          <div
            style={{
              fontSize: "36px",
              fontWeight: 800,
              color: tokens.text.primary,
              lineHeight: 1.2,
              marginBottom: outcomeNote ? "16px" : "0",
            }}
          >
            {combinedLabel}
          </div>
          {outcomeNote && (
            <div
              style={{
                fontSize: "20px",
                fontWeight: 500,
                color: tokens.text.secondary,
                lineHeight: 1.4,
              }}
            >
              {outcomeNote}
            </div>
          )}
        </div>
      </div>
    </AbsoluteFill>
  );
};
