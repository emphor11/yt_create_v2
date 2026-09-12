import React from 'react';
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { tokens } from '../design-tokens';
import { MetricHeroProps } from '../types';
import { safeAnimationWindow, safeSpringDelay } from '../animation-safety';

export function MetricHero(props: MetricHeroProps | any) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const resolvedProps: MetricHeroProps = (props as any).props || props;
  const duration_frames = (props as any).duration_frames || 180;

  const value = resolvedProps.value || "0";
  const label = resolvedProps.label || "";
  const context = resolvedProps.context || null;
  const polarity = resolvedProps.polarity || null;
  const direction = resolvedProps.direction || null;
  const baselineValue = resolvedProps.baselineValue || null;
  const baselineLabel = resolvedProps.baselineLabel || "Baseline";
  const delta = resolvedProps.delta || null;

  // Variant & treatment resolution (eliminates the old boolean hero trap)
  const explicitVariant = resolvedProps.variant || (resolvedProps as any).treatment;

  let treatment: "hero_milestone" | "supporting_metric" | "warning_metric" | "before_after_metric";

  if (
    explicitVariant === "warning_metric" ||
    polarity === "negative" ||
    polarity === "warning" ||
    resolvedProps.emphasis === "highlight_risk"
  ) {
    treatment = "warning_metric";
  } else if (
    explicitVariant === "before_after_metric" ||
    (baselineValue && baselineValue !== value) ||
    (delta && explicitVariant !== "supporting" && explicitVariant !== "supporting_metric")
  ) {
    treatment = "before_after_metric";
  } else if (
    explicitVariant === "supporting_metric" ||
    explicitVariant === "supporting" ||
    resolvedProps.emphasis === "supporting"
  ) {
    treatment = "supporting_metric";
  } else {
    treatment = "hero_milestone";
  }

  // Scene entrance fade
  const sceneOpacity = interpolate(
    frame,
    [0, Math.min(8, Math.max(1, duration_frames - 1))],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // -------------------------------------------------------------------------
  // Treatment 1: HERO MILESTONE
  // -------------------------------------------------------------------------
  if (treatment === "hero_milestone") {
    const badgeDelay = safeSpringDelay(6, duration_frames, 0.2);
    const badgeSpring = spring({
      frame: Math.max(0, frame - badgeDelay),
      fps,
      config: tokens.motion.reveal,
    });
    const badgeY = interpolate(badgeSpring, [0, 1], [18, 0]);

    const valueDelay = safeSpringDelay(12, duration_frames, 0.35);
    const valueSpring = spring({
      frame: Math.max(0, frame - valueDelay),
      fps,
      config: tokens.motion.reveal,
    });

    // Direction-aware motion offset
    const dirOffset = direction === "up" ? 30 : direction === "down" ? -30 : 0;
    const valueY = interpolate(valueSpring, [0, 1], [dirOffset, 0]);
    const valueScale = interpolate(valueSpring, [0, 1], [0.9, 1]);

    const labelDelay = safeSpringDelay(18, duration_frames, 0.5);
    const labelSpring = spring({
      frame: Math.max(0, frame - labelDelay),
      fps,
      config: tokens.motion.settle,
    });
    const labelY = interpolate(labelSpring, [0, 1], [24, 0]);

    // Ambient radial glow bloom
    const [glowStart, glowEnd] = safeAnimationWindow(
      Math.round(duration_frames * 0.4),
      Math.round(duration_frames * 0.65),
      duration_frames
    );
    const glowBloom = interpolate(
      frame,
      [glowStart, glowEnd],
      [0.08, 0.22],
      { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
    );

    const glowColor = polarity === "positive" ? "16, 185, 129" : "6, 182, 212";

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
        {/* Atmospheric Radial Glow */}
        <div
          style={{
            position: "absolute",
            width: "800px",
            height: "800px",
            borderRadius: "50%",
            background: `radial-gradient(circle, rgba(${glowColor}, ${glowBloom}) 0%, transparent 70%)`,
            pointerEvents: "none",
            zIndex: 0,
          }}
        />

        {/* Ambient Outer Halo Ring */}
        <div
          style={{
            position: "absolute",
            width: "1200px",
            height: "480px",
            borderRadius: "40px",
            border: "1px solid rgba(255, 255, 255, 0.04)",
            background: "radial-gradient(ellipse at center, rgba(15, 23, 42, 0.5) 0%, transparent 80%)",
            pointerEvents: "none",
            zIndex: 0,
          }}
        />

        {/* Context Badge */}
        {context && (
          <div
            style={{
              opacity: badgeSpring,
              transform: `translateY(${badgeY}px)`,
              marginBottom: "28px",
              padding: "10px 24px",
              borderRadius: tokens.radius.pill,
              backgroundColor: "rgba(15, 23, 42, 0.85)",
              border: `1px solid rgba(56, 189, 248, 0.35)`,
              color: tokens.accent.cyan,
              fontSize: "19px",
              fontWeight: 700,
              letterSpacing: "0.08em",
              textTransform: "uppercase",
              boxShadow: "0 4px 20px -2px rgba(6, 182, 212, 0.2)",
              zIndex: 1,
            }}
          >
            {context}
          </div>
        )}

        {/* Main Hero Metric Value */}
        <div
          style={{
            opacity: valueSpring,
            transform: `translateY(${valueY}px) scale(${valueScale})`,
            fontSize: "124px",
            fontWeight: 800,
            letterSpacing: "-0.035em",
            lineHeight: 1.02,
            color: polarity === "positive" ? "#34d399" : tokens.text.primary,
            textAlign: "center",
            maxWidth: "1400px",
            textShadow: `0 0 40px rgba(${glowColor}, 0.25)`,
            zIndex: 1,
          }}
        >
          {value}
        </div>

        {/* Semantic Label */}
        <div
          style={{
            opacity: labelSpring,
            transform: `translateY(${labelY}px)`,
            marginTop: "26px",
            fontSize: "36px",
            fontWeight: 600,
            lineHeight: 1.35,
            color: tokens.text.secondary,
            textAlign: "center",
            maxWidth: "1150px",
            zIndex: 1,
          }}
        >
          {label}
        </div>
      </AbsoluteFill>
    );
  }

  // -------------------------------------------------------------------------
  // Treatment 2: SUPPORTING METRIC (Asymmetric Editorial Plaque Layout)
  // -------------------------------------------------------------------------
  if (treatment === "supporting_metric") {
    const cardDelay = safeSpringDelay(8, duration_frames, 0.25);
    const cardSpring = spring({
      frame: Math.max(0, frame - cardDelay),
      fps,
      config: tokens.motion.reveal,
    });
    const cardX = interpolate(cardSpring, [0, 1], [-40, 0]);

    const valueDelay = safeSpringDelay(14, duration_frames, 0.4);
    const valueSpring = spring({
      frame: Math.max(0, frame - valueDelay),
      fps,
      config: tokens.motion.settle,
    });

    return (
      <AbsoluteFill
        style={{
          backgroundColor: tokens.bg.base,
          fontFamily: tokens.font.family,
          opacity: sceneOpacity,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          padding: "60px 120px",
          overflow: "hidden",
        }}
      >
        <div
          style={{
            opacity: cardSpring,
            transform: `translateX(${cardX}px)`,
            width: "100%",
            maxWidth: "1100px",
            backgroundColor: tokens.bg.surface,
            borderRadius: tokens.radius.card,
            border: `1px solid ${tokens.bg.border}`,
            borderLeft: `6px solid ${tokens.accent.cyan}`,
            padding: "54px 64px",
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
            boxShadow: "0 25px 50px -12px rgba(0, 0, 0, 0.6)",
            position: "relative",
          }}
        >
          {/* Supporting Eyebrow Tag */}
          <div
            style={{
              fontSize: "18px",
              fontWeight: 700,
              letterSpacing: "0.1em",
              textTransform: "uppercase",
              color: tokens.accent.cyan,
              marginBottom: "18px",
              display: "flex",
              alignItems: "center",
              gap: "10px",
            }}
          >
            <span
              style={{
                display: "inline-block",
                width: "8px",
                height: "8px",
                borderRadius: "50%",
                backgroundColor: tokens.accent.cyan,
              }}
            />
            {context || "SUPPORTING METRIC"}
          </div>

          {/* Metric Value */}
          <div
            style={{
              opacity: valueSpring,
              fontSize: "76px",
              fontWeight: 800,
              letterSpacing: "-0.025em",
              color: tokens.text.primary,
              lineHeight: 1.1,
              marginBottom: "18px",
            }}
          >
            {value}
          </div>

          {/* Metric Label */}
          <div
            style={{
              fontSize: "30px",
              fontWeight: 500,
              lineHeight: 1.35,
              color: tokens.text.secondary,
              maxWidth: "920px",
            }}
          >
            {label}
          </div>
        </div>
      </AbsoluteFill>
    );
  }

  // -------------------------------------------------------------------------
  // Treatment 3: WARNING METRIC (Tension, Risk, Rose Severity Glow)
  // -------------------------------------------------------------------------
  if (treatment === "warning_metric") {
    const badgeDelay = safeSpringDelay(6, duration_frames, 0.2);
    const badgeSpring = spring({
      frame: Math.max(0, frame - badgeDelay),
      fps,
      config: tokens.motion.reveal,
    });

    const valueDelay = safeSpringDelay(10, duration_frames, 0.35);
    const valueSpring = spring({
      frame: Math.max(0, frame - valueDelay),
      fps,
      config: tokens.motion.impact,
    });
    // Downward impact motion for warning/decline
    const valueY = interpolate(valueSpring, [0, 1], [-30, 0]);

    const labelDelay = safeSpringDelay(18, duration_frames, 0.5);
    const labelSpring = spring({
      frame: Math.max(0, frame - labelDelay),
      fps,
      config: tokens.motion.settle,
    });

    const [glowStart, glowEnd] = safeAnimationWindow(
      Math.round(duration_frames * 0.35),
      Math.round(duration_frames * 0.65),
      duration_frames
    );
    const alertGlow = interpolate(
      frame,
      [glowStart, glowEnd],
      [0.1, 0.25],
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
        {/* Warning Radial Aura */}
        <div
          style={{
            position: "absolute",
            width: "750px",
            height: "750px",
            borderRadius: "50%",
            background: `radial-gradient(circle, rgba(244, 63, 94, ${alertGlow}) 0%, transparent 70%)`,
            pointerEvents: "none",
            zIndex: 0,
          }}
        />

        {/* Warning Badge */}
        <div
          style={{
            opacity: badgeSpring,
            transform: `scale(${interpolate(badgeSpring, [0, 1], [0.85, 1])})`,
            marginBottom: "26px",
            padding: "10px 24px",
            borderRadius: tokens.radius.pill,
            backgroundColor: "rgba(244, 63, 94, 0.15)",
            border: "1px solid rgba(244, 63, 94, 0.45)",
            color: tokens.accent.rose,
            fontSize: "18px",
            fontWeight: 800,
            letterSpacing: "0.08em",
            textTransform: "uppercase",
            display: "flex",
            alignItems: "center",
            gap: "8px",
            zIndex: 1,
          }}
        >
          <span>⚠</span>
          <span>{context || "CRITICAL VULNERABILITY"}</span>
        </div>

        {/* Warning Metric Value */}
        <div
          style={{
            opacity: valueSpring,
            transform: `translateY(${valueY}px)`,
            fontSize: "116px",
            fontWeight: 800,
            letterSpacing: "-0.035em",
            lineHeight: 1.05,
            color: tokens.accent.rose,
            textAlign: "center",
            maxWidth: "1400px",
            textShadow: "0 0 45px rgba(244, 63, 94, 0.35)",
            zIndex: 1,
          }}
        >
          {value}
        </div>

        {/* Warning Label */}
        <div
          style={{
            opacity: labelSpring,
            transform: `translateY(${interpolate(labelSpring, [0, 1], [20, 0])}px)`,
            marginTop: "24px",
            fontSize: "34px",
            fontWeight: 600,
            lineHeight: 1.35,
            color: "#fecdd3",
            textAlign: "center",
            maxWidth: "1100px",
            zIndex: 1,
          }}
        >
          {label}
        </div>
      </AbsoluteFill>
    );
  }

  // -------------------------------------------------------------------------
  // Treatment 4: BEFORE / AFTER TRANSFORMATION METRIC
  // -------------------------------------------------------------------------
  const leftDelay = safeSpringDelay(8, duration_frames, 0.25);
  const leftSpring = spring({
    frame: Math.max(0, frame - leftDelay),
    fps,
    config: tokens.motion.reveal,
  });

  const [arrowStart, arrowEnd] = safeAnimationWindow(18, 42, duration_frames);
  const arrowProgress = interpolate(
    frame,
    [arrowStart, arrowEnd],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  const rightDelay = safeSpringDelay(32, duration_frames, 0.55);
  const rightSpring = spring({
    frame: Math.max(0, frame - rightDelay),
    fps,
    config: tokens.motion.impact,
  });

  const labelDelay = safeSpringDelay(42, duration_frames, 0.7);
  const labelSpring = spring({
    frame: Math.max(0, frame - labelDelay),
    fps,
    config: tokens.motion.settle,
  });

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
      {/* Transformation Row */}
      <div
        style={{
          display: "flex",
          flexDirection: "row",
          alignItems: "center",
          justifyContent: "center",
          width: "100%",
          maxWidth: "1550px",
          gap: "40px",
          marginBottom: "36px",
        }}
      >
        {/* Baseline Card */}
        <div
          style={{
            opacity: leftSpring,
            transform: `translateX(${interpolate(leftSpring, [0, 1], [-40, 0])}px)`,
            flex: 1,
            maxWidth: "440px",
            backgroundColor: tokens.bg.cardLeft,
            borderRadius: tokens.radius.card,
            border: `1px solid ${tokens.bg.border}`,
            padding: "36px 40px",
            display: "flex",
            flexDirection: "column",
            boxShadow: "0 15px 35px -10px rgba(0, 0, 0, 0.5)",
          }}
        >
          <div
            style={{
              fontSize: "17px",
              fontWeight: 700,
              textTransform: "uppercase",
              letterSpacing: "0.08em",
              color: tokens.text.muted,
              marginBottom: "14px",
            }}
          >
            {baselineLabel}
          </div>
          <div
            style={{
              fontSize: "52px",
              fontWeight: 700,
              color: tokens.text.secondary,
              lineHeight: 1.1,
            }}
          >
            {baselineValue || "Initial"}
          </div>
        </div>

        {/* Transition Vector Arrow */}
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            width: "180px",
          }}
        >
          <svg
            width="180"
            height="40"
            viewBox="0 0 180 40"
            style={{ overflow: "visible", marginBottom: "8px" }}
          >
            <path
              d="M 0 20 L 170 20 M 155 10 L 170 20 L 155 30"
              stroke={tokens.accent.cyan}
              strokeWidth="3.5"
              fill="none"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeDasharray="200"
              strokeDashoffset={200 * (1 - arrowProgress)}
            />
          </svg>
          {delta && (
            <div
              style={{
                fontSize: "16px",
                fontWeight: 700,
                color: tokens.accent.cyan,
                backgroundColor: "rgba(6, 182, 212, 0.12)",
                padding: "6px 14px",
                borderRadius: tokens.radius.chip,
                border: "1px solid rgba(6, 182, 212, 0.25)",
              }}
            >
              {delta}
            </div>
          )}
        </div>

        {/* Resulting Hero Card */}
        <div
          style={{
            opacity: rightSpring,
            transform: `scale(${interpolate(rightSpring, [0, 1], [0.9, 1])})`,
            flex: 1.2,
            maxWidth: "540px",
            backgroundColor: tokens.bg.surface,
            borderRadius: tokens.radius.card,
            border: `2px solid ${tokens.accent.cyan}`,
            padding: "40px 44px",
            display: "flex",
            flexDirection: "column",
            boxShadow: "0 25px 60px -15px rgba(6, 182, 212, 0.2), 0 20px 40px -10px rgba(0, 0, 0, 0.7)",
          }}
        >
          <div
            style={{
              fontSize: "18px",
              fontWeight: 700,
              textTransform: "uppercase",
              letterSpacing: "0.08em",
              color: tokens.accent.cyan,
              marginBottom: "14px",
            }}
          >
            {context || "RESULT"}
          </div>
          <div
            style={{
              fontSize: "84px",
              fontWeight: 800,
              color: tokens.text.primary,
              lineHeight: 1.05,
            }}
          >
            {value}
          </div>
        </div>
      </div>

      {/* Semantic Label */}
      <div
        style={{
          opacity: labelSpring,
          fontSize: "32px",
          fontWeight: 600,
          lineHeight: 1.35,
          color: tokens.text.secondary,
          textAlign: "center",
          maxWidth: "1150px",
        }}
      >
        {label}
      </div>
    </AbsoluteFill>
  );
}
