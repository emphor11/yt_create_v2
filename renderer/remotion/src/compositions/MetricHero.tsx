import React from 'react';
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { tokens } from '../design-tokens';
import { MetricHeroProps } from '../types';

export function MetricHero(props: MetricHeroProps | any) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const resolvedProps: MetricHeroProps = (props as any).props || props;
  const duration_frames = (props as any).duration_frames || 180;

  const value = resolvedProps.value || "0";
  const label = resolvedProps.label || "";
  const context = resolvedProps.context || null;
  const isHero = resolvedProps.emphasis === "hero" || resolvedProps.variant === "hero" || resolvedProps.emphasis !== "supporting";

  // Scene fade in
  const sceneOpacity = interpolate(frame, [0, 8], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Context badge animation
  const badgeSpring = spring({
    frame: Math.max(0, frame - 6),
    fps,
    config: { damping: 16, stiffness: 120 },
  });
  const badgeY = interpolate(badgeSpring, [0, 1], [18, 0]);
  const badgeOpacity = interpolate(badgeSpring, [0, 1], [0, 1]);

  // Value animation
  const valueSpring = spring({
    frame: Math.max(0, frame - 12),
    fps,
    config: { damping: 14, stiffness: 110 },
  });
  const valueScale = interpolate(valueSpring, [0, 1], [0.88, 1]);
  const valueOpacity = interpolate(valueSpring, [0, 1], [0, 1]);

  // Label animation
  const labelSpring = spring({
    frame: Math.max(0, frame - 18),
    fps,
    config: { damping: 15, stiffness: 100 },
  });
  const labelY = interpolate(labelSpring, [0, 1], [24, 0]);
  const labelOpacity = interpolate(labelSpring, [0, 1], [0, 1]);

  // Radial glow bloom
  const glowBloom = interpolate(
    frame,
    [duration_frames * 0.45, duration_frames * 0.65],
    [0, 0.18],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  return (
    <AbsoluteFill
      style={{
        backgroundColor: tokens.bg.base,
        fontFamily: tokens.font.family,
        opacity: sceneOpacity,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        padding: "60px 100px",
        overflow: "hidden",
      }}
    >
      {/* Background radial glow */}
      {isHero && (
        <div
          style={{
            position: "absolute",
            width: "600px",
            height: "600px",
            borderRadius: "50%",
            background: `radial-gradient(circle, rgba(59, 130, 246, ${glowBloom}) 0%, transparent 70%)`,
            pointerEvents: "none",
            zIndex: 0,
          }}
        />
      )}

      {/* Context Badge */}
      {context && (
        <div
          style={{
            opacity: badgeOpacity,
            transform: `translateY(${badgeY}px)`,
            marginBottom: "28px",
            padding: "8px 20px",
            borderRadius: tokens.radius.pill,
            backgroundColor: "rgba(30, 41, 59, 0.7)",
            border: `1px solid ${tokens.bg.border}`,
            color: tokens.accent.cyan,
            fontSize: "18px",
            fontWeight: 600,
            letterSpacing: "0.06em",
            textTransform: "uppercase",
            zIndex: 1,
          }}
        >
          {context}
        </div>
      )}

      {/* Main Metric Value */}
      <div
        style={{
          opacity: valueOpacity,
          transform: `scale(${valueScale})`,
          fontSize: isHero ? "112px" : "68px",
          fontWeight: 800,
          letterSpacing: "-0.03em",
          lineHeight: 1.05,
          color: tokens.text.primary,
          textAlign: "center",
          maxWidth: "1400px",
          zIndex: 1,
        }}
      >
        {value}
      </div>

      {/* Semantic Label */}
      <div
        style={{
          opacity: labelOpacity,
          transform: `translateY(${labelY}px)`,
          marginTop: "24px",
          fontSize: isHero ? "36px" : "28px",
          fontWeight: 600,
          lineHeight: 1.3,
          color: tokens.text.secondary,
          textAlign: "center",
          maxWidth: "1100px",
          zIndex: 1,
        }}
      >
        {label}
      </div>
    </AbsoluteFill>
  );
};
