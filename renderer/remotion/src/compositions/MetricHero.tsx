import React from 'react';
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { tokens } from '../design-tokens';
import { MetricHeroProps } from '../types';
import { safeAnimationWindow, safeSpringDelay } from '../animation-safety';

// ---------------------------------------------------------------------------
// Typography & Optical Formatting Helpers
// ---------------------------------------------------------------------------

function getDynamicFontSize(valueStr: string, baseMax: number = 176, baseMin: number = 92): number {
  const len = (valueStr || "").trim().length;
  if (len <= 4) return baseMax;                     // e.g. "45%", "3x" (~176px)
  if (len <= 7) return Math.round(baseMax * 0.88);  // e.g. "₹75,000", "$120k" (~155px)
  if (len <= 11) return Math.round(baseMax * 0.74); // e.g. "₹1.5 Crore" (~130px)
  if (len <= 15) return Math.round(baseMax * 0.62); // e.g. "50/30/20 Rule" (~109px)
  return Math.max(baseMin, Math.round(baseMax * 0.54));
}

function renderFormattedValue(value: string, fontSize: number, color: string) {
  const trimmed = (value || "0").trim();
  // Match currency prefix (₹, $, €, £, ¥)
  const currencyMatch = trimmed.match(/^([₹$€£¥])\s*(.*)$/);
  if (currencyMatch) {
    const symbol = currencyMatch[1];
    const rest = currencyMatch[2];
    return (
      <span
        style={{
          fontVariantNumeric: "tabular-nums lining-nums",
          letterSpacing: "-0.035em",
          color,
          display: "inline-flex",
          alignItems: "baseline",
          justifyContent: "center",
        }}
      >
        <span
          style={{
            fontSize: `${Math.round(fontSize * 0.82)}px`,
            opacity: 0.86,
            marginRight: "6px",
            fontWeight: 700,
          }}
        >
          {symbol}
        </span>
        <span style={{ fontWeight: 800 }}>{rest}</span>
      </span>
    );
  }

  return (
    <span
      style={{
        fontVariantNumeric: "tabular-nums lining-nums",
        letterSpacing: "-0.035em",
        fontWeight: 800,
        color,
      }}
    >
      {trimmed}
    </span>
  );
}

// ---------------------------------------------------------------------------
// Subtle Editorial Background Component
// ---------------------------------------------------------------------------

interface EditorialBackdropProps {
  glowColor: string;
  glowOpacity?: number;
}

function EditorialBackdrop({ glowColor, glowOpacity = 0.14 }: EditorialBackdropProps) {
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

      {/* Atmospheric Soft Aura behind the metric (wide horizontal cinematic spread) */}
      <div
        style={{
          position: "absolute",
          width: "1300px",
          height: "720px",
          left: "50%",
          top: "46%",
          transform: "translate(-50%, -50%)",
          borderRadius: "50%",
          background: `radial-gradient(ellipse at center, rgba(${glowColor}, ${glowOpacity}) 0%, transparent 68%)`,
          filter: "blur(32px)",
        }}
      />

      {/* Ultra-faint Editorial Datum Lines (<= 0.035 opacity, disappears into background) */}
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
// Main MetricHero Component
// ---------------------------------------------------------------------------

export function MetricHero(props: MetricHeroProps | any) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const resolvedProps: MetricHeroProps = (props as any).props || props;
  const duration_frames = (props as any).duration_frames || 180;

  const value = resolvedProps.value || "0";
  const label = resolvedProps.label || "";
  const context = resolvedProps.context || resolvedProps.headerLabel || null;
  const polarity = resolvedProps.polarity || null;
  const direction = resolvedProps.direction || null;
  const baselineValue = resolvedProps.baselineValue || null;
  const baselineLabel = resolvedProps.baselineLabel || "Baseline";
  const delta = resolvedProps.delta || null;

  // Resolve treatment: explicit before_after takes precedence over simple negative polarity
  const explicitVariant = resolvedProps.variant || (resolvedProps as any).treatment;

  let treatment: "hero_milestone" | "supporting_metric" | "warning_metric" | "before_after_metric";

  if (
    explicitVariant === "before_after_metric" ||
    (baselineValue && baselineValue !== value)
  ) {
    treatment = "before_after_metric";
  } else if (
    explicitVariant === "warning_metric" ||
    polarity === "negative" ||
    polarity === "warning" ||
    resolvedProps.emphasis === "highlight_risk"
  ) {
    treatment = "warning_metric";
  } else if (
    explicitVariant === "supporting_metric" ||
    explicitVariant === "supporting" ||
    resolvedProps.emphasis === "supporting"
  ) {
    treatment = "supporting_metric";
  } else {
    treatment = "hero_milestone";
  }

  // Smooth entrance fade
  const sceneOpacity = interpolate(
    frame,
    [0, Math.min(8, Math.max(1, duration_frames - 1))],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // Sub-threshold camera motion: remains below noticeable threshold (1.000 -> 1.007 max)
  const cameraScale = interpolate(
    frame,
    [0, Math.max(1, duration_frames)],
    [1.000, 1.007],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // -------------------------------------------------------------------------
  // Treatment 1: HERO MILESTONE (Centered Editorial Authority)
  // -------------------------------------------------------------------------
  if (treatment === "hero_milestone") {
    const badgeDelay = safeSpringDelay(4, duration_frames, 0.15);
    const badgeSpring = spring({
      frame: Math.max(0, frame - badgeDelay),
      fps,
      config: tokens.motion.reveal,
    });
    const badgeY = interpolate(badgeSpring, [0, 1], [14, 0]);

    const valueDelay = safeSpringDelay(8, duration_frames, 0.28);
    const valueSpring = spring({
      frame: Math.max(0, frame - valueDelay),
      fps,
      config: { damping: 18, stiffness: 120, mass: 0.95 },
    });

    const dirOffset = direction === "up" ? 24 : direction === "down" ? -24 : 18;
    const valueY = interpolate(valueSpring, [0, 1], [dirOffset, 0]);

    const labelDelay = safeSpringDelay(16, duration_frames, 0.45);
    const labelSpring = spring({
      frame: Math.max(0, frame - labelDelay),
      fps,
      config: tokens.motion.settle,
    });
    const labelY = interpolate(labelSpring, [0, 1], [16, 0]);

    const isPositive = polarity === "positive";
    const glowColor = isPositive ? "16, 185, 129" : "56, 189, 248";
    const valueColor = isPositive ? "#34d399" : "#f8fafc";
    const fontSize = getDynamicFontSize(value, 176, 100);

    return (
      <AbsoluteFill
        style={{
          fontFamily: tokens.font.family,
          opacity: sceneOpacity,
          transform: `scale(${cameraScale})`,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          padding: "60px 140px",
          overflow: "hidden",
        }}
      >
        <EditorialBackdrop glowColor={glowColor} glowOpacity={0.15} />

        {/* Content Container (Full-bleed 16:9 editorial balance) */}
        <div
          style={{
            position: "relative",
            zIndex: 1,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            maxWidth: "1480px",
            width: "100%",
            textAlign: "center",
          }}
        >
          {/* Eyebrow Context Datum */}
          {context && (
            <div
              style={{
                opacity: badgeSpring,
                transform: `translateY(${badgeY}px)`,
                marginBottom: "28px",
                display: "inline-flex",
                alignItems: "center",
                gap: "8px",
                padding: "8px 22px",
                borderRadius: "6px",
                backgroundColor: "rgba(15, 23, 42, 0.75)",
                border: "1px solid rgba(56, 189, 248, 0.25)",
                boxShadow: "0 2px 14px rgba(0, 0, 0, 0.45)",
              }}
            >
              <span
                style={{
                  display: "inline-block",
                  width: "6px",
                  height: "6px",
                  borderRadius: "50%",
                  backgroundColor: isPositive ? "#34d399" : tokens.accent.cyan,
                  boxShadow: `0 0 8px ${isPositive ? "#34d399" : tokens.accent.cyan}`,
                }}
              />
              <span
                style={{
                  color: isPositive ? "#6ee7b7" : tokens.accent.cyan,
                  fontSize: "17px",
                  fontWeight: 700,
                  letterSpacing: "0.12em",
                  textTransform: "uppercase",
                }}
              >
                {context}
              </span>
            </div>
          )}

          {/* Primary Hero Metric Value */}
          <div
            style={{
              opacity: valueSpring,
              transform: `translateY(${valueY}px)`,
              fontSize: `${fontSize}px`,
              lineHeight: 1.02,
              marginBottom: "26px",
              textShadow: `0 8px 36px rgba(0, 0, 0, 0.7), 0 0 60px rgba(${glowColor}, 0.26)`,
            }}
          >
            {renderFormattedValue(value, fontSize, valueColor)}
          </div>

          {/* Semantic Editorial Label */}
          {label && (
            <div
              style={{
                opacity: labelSpring,
                transform: `translateY(${labelY}px)`,
                fontSize: "40px",
                fontWeight: 500,
                lineHeight: 1.36,
                color: "#cbd5e1",
                maxWidth: "1150px",
                letterSpacing: "-0.015em",
              }}
            >
              {label}
            </div>
          )}

          {/* Optional Delta or Baseline Chip */}
          {delta && (
            <div
              style={{
                opacity: labelSpring,
                marginTop: "24px",
                display: "inline-flex",
                alignItems: "center",
                gap: "6px",
                padding: "6px 18px",
                borderRadius: "6px",
                backgroundColor: isPositive ? "rgba(16, 185, 129, 0.14)" : "rgba(56, 189, 248, 0.14)",
                border: `1px solid ${isPositive ? "rgba(16, 185, 129, 0.35)" : "rgba(56, 189, 248, 0.35)"}`,
                color: isPositive ? "#34d399" : tokens.accent.cyan,
                fontSize: "17px",
                fontWeight: 700,
                letterSpacing: "0.04em",
              }}
            >
              <span>{direction === "up" ? "▲" : direction === "down" ? "▼" : "•"}</span>
              <span>{delta}</span>
            </div>
          )}
        </div>
      </AbsoluteFill>
    );
  }

  // -------------------------------------------------------------------------
  // Treatment 2: SUPPORTING METRIC (Asymmetric Editorial Two-Column Split)
  // -------------------------------------------------------------------------
  if (treatment === "supporting_metric") {
    const leftDelay = safeSpringDelay(6, duration_frames, 0.2);
    const leftSpring = spring({
      frame: Math.max(0, frame - leftDelay),
      fps,
      config: tokens.motion.reveal,
    });
    const leftX = interpolate(leftSpring, [0, 1], [-28, 0]);

    const rightDelay = safeSpringDelay(14, duration_frames, 0.38);
    const rightSpring = spring({
      frame: Math.max(0, frame - rightDelay),
      fps,
      config: tokens.motion.settle,
    });
    const rightX = interpolate(rightSpring, [0, 1], [24, 0]);

    const fontSize = getDynamicFontSize(value, 132, 84);

    return (
      <AbsoluteFill
        style={{
          fontFamily: tokens.font.family,
          opacity: sceneOpacity,
          transform: `scale(${cameraScale})`,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          padding: "80px 140px",
          overflow: "hidden",
        }}
      >
        <EditorialBackdrop glowColor="56, 189, 248" glowOpacity={0.11} />

        {/* Asymmetric Editorial Staging */}
        <div
          style={{
            position: "relative",
            zIndex: 1,
            display: "flex",
            flexDirection: "row",
            alignItems: "center",
            justifyContent: "space-between",
            width: "100%",
            maxWidth: "1520px",
            gap: "70px",
          }}
        >
          {/* Left Column: Metric Statement */}
          <div
            style={{
              opacity: leftSpring,
              transform: `translateX(${leftX}px)`,
              display: "flex",
              flexDirection: "column",
              alignItems: "flex-start",
              flex: "0 0 auto",
            }}
          >
            {context && (
              <div
                style={{
                  fontSize: "16px",
                  fontWeight: 700,
                  letterSpacing: "0.12em",
                  textTransform: "uppercase",
                  color: tokens.accent.cyan,
                  marginBottom: "16px",
                  display: "flex",
                  alignItems: "center",
                  gap: "8px",
                }}
              >
                <span
                  style={{
                    display: "inline-block",
                    width: "6px",
                    height: "6px",
                    borderRadius: "50%",
                    backgroundColor: tokens.accent.cyan,
                  }}
                />
                {context}
              </div>
            )}
            <div
              style={{
                fontSize: `${fontSize}px`,
                lineHeight: 1.04,
                textShadow: "0 8px 32px rgba(0, 0, 0, 0.65), 0 0 50px rgba(56, 189, 248, 0.2)",
              }}
            >
              {renderFormattedValue(value, fontSize, "#f8fafc")}
            </div>
          </div>

          {/* Delicate Vertical Editorial Divider */}
          <div
            style={{
              opacity: leftSpring,
              width: "1px",
              height: "160px",
              background: "linear-gradient(180deg, transparent 0%, rgba(255, 255, 255, 0.18) 25%, rgba(255, 255, 255, 0.18) 75%, transparent 100%)",
            }}
          />

          {/* Right Column: Editorial Explanation & Takeaway */}
          <div
            style={{
              opacity: rightSpring,
              transform: `translateX(${rightX}px)`,
              display: "flex",
              flexDirection: "column",
              justifyContent: "center",
              flex: "1 1 auto",
            }}
          >
            <div
              style={{
                fontSize: "38px",
                fontWeight: 500,
                lineHeight: 1.4,
                color: "#cbd5e1",
                maxWidth: "850px",
                letterSpacing: "-0.015em",
              }}
            >
              {label}
            </div>
            {delta && (
              <div
                style={{
                  marginTop: "20px",
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "6px",
                  fontSize: "18px",
                  fontWeight: 600,
                  color: tokens.accent.cyan,
                }}
              >
                <span>{direction === "up" ? "▲" : direction === "down" ? "▼" : "•"}</span>
                <span>{delta}</span>
              </div>
            )}
          </div>
        </div>
      </AbsoluteFill>
    );
  }

  // -------------------------------------------------------------------------
  // Treatment 3: WARNING METRIC (High-Tension Financial Risk & Deficit)
  // -------------------------------------------------------------------------
  if (treatment === "warning_metric") {
    const badgeDelay = safeSpringDelay(4, duration_frames, 0.15);
    const badgeSpring = spring({
      frame: Math.max(0, frame - badgeDelay),
      fps,
      config: tokens.motion.reveal,
    });

    const valueDelay = safeSpringDelay(8, duration_frames, 0.28);
    const valueSpring = spring({
      frame: Math.max(0, frame - valueDelay),
      fps,
      config: { damping: 18, stiffness: 130, mass: 1.0 },
    });
    // Downward impact reveal for warning
    const valueY = interpolate(valueSpring, [0, 1], [-24, 0]);

    const labelDelay = safeSpringDelay(16, duration_frames, 0.45);
    const labelSpring = spring({
      frame: Math.max(0, frame - labelDelay),
      fps,
      config: tokens.motion.settle,
    });
    const labelY = interpolate(labelSpring, [0, 1], [16, 0]);

    const fontSize = getDynamicFontSize(value, 176, 96);

    return (
      <AbsoluteFill
        style={{
          fontFamily: tokens.font.family,
          opacity: sceneOpacity,
          transform: `scale(${cameraScale})`,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          padding: "60px 140px",
          overflow: "hidden",
        }}
      >
        <EditorialBackdrop glowColor="244, 63, 94" glowOpacity={0.18} />

        <div
          style={{
            position: "relative",
            zIndex: 1,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            maxWidth: "1480px",
            width: "100%",
            textAlign: "center",
          }}
        >
          {/* Tension Warning Eyebrow */}
          <div
            style={{
              opacity: badgeSpring,
              transform: `scale(${interpolate(badgeSpring, [0, 1], [0.92, 1])})`,
              marginBottom: "28px",
              display: "inline-flex",
              alignItems: "center",
              gap: "8px",
              padding: "8px 22px",
              borderRadius: "6px",
              backgroundColor: "rgba(244, 63, 94, 0.16)",
              border: "1px solid rgba(244, 63, 94, 0.45)",
              boxShadow: "0 2px 16px rgba(244, 63, 94, 0.22)",
            }}
          >
            <span
              style={{
                display: "inline-block",
                width: "7px",
                height: "7px",
                borderRadius: "50%",
                backgroundColor: tokens.accent.rose,
                boxShadow: `0 0 10px ${tokens.accent.rose}`,
              }}
            />
            <span
              style={{
                color: "#fda4af",
                fontSize: "17px",
                fontWeight: 800,
                letterSpacing: "0.12em",
                textTransform: "uppercase",
              }}
            >
              {context || "CRITICAL VULNERABILITY"}
            </span>
          </div>

          {/* Warning Metric Value */}
          <div
            style={{
              opacity: valueSpring,
              transform: `translateY(${valueY}px)`,
              fontSize: `${fontSize}px`,
              lineHeight: 1.02,
              marginBottom: "26px",
              textShadow: "0 8px 36px rgba(0, 0, 0, 0.7), 0 0 65px rgba(244, 63, 94, 0.35)",
            }}
          >
            {renderFormattedValue(value, fontSize, tokens.accent.rose)}
          </div>

          {/* Warning Label */}
          {label && (
            <div
              style={{
                opacity: labelSpring,
                transform: `translateY(${labelY}px)`,
                fontSize: "40px",
                fontWeight: 500,
                lineHeight: 1.36,
                color: "#fecdd3",
                maxWidth: "1150px",
                letterSpacing: "-0.015em",
              }}
            >
              {label}
            </div>
          )}

          {/* Warning Delta */}
          {delta && (
            <div
              style={{
                opacity: labelSpring,
                marginTop: "24px",
                display: "inline-flex",
                alignItems: "center",
                gap: "6px",
                padding: "6px 18px",
                borderRadius: "6px",
                backgroundColor: "rgba(244, 63, 94, 0.16)",
                border: "1px solid rgba(244, 63, 94, 0.4)",
                color: "#fda4af",
                fontSize: "17px",
                fontWeight: 700,
              }}
            >
              <span>▼</span>
              <span>{delta}</span>
            </div>
          )}
        </div>
      </AbsoluteFill>
    );
  }

  // -------------------------------------------------------------------------
  // Treatment 4: BEFORE / AFTER METRIC (Financial Transition Bridge)
  // -------------------------------------------------------------------------
  const leftDelay = safeSpringDelay(6, duration_frames, 0.18);
  const leftSpring = spring({
    frame: Math.max(0, frame - leftDelay),
    fps,
    config: tokens.motion.reveal,
  });

  const [vectorStart, vectorEnd] = safeAnimationWindow(14, 34, duration_frames);
  const vectorProgress = interpolate(
    frame,
    [vectorStart, vectorEnd],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  const rightDelay = safeSpringDelay(26, duration_frames, 0.45);
  const rightSpring = spring({
    frame: Math.max(0, frame - rightDelay),
    fps,
    config: { damping: 18, stiffness: 120, mass: 0.95 },
  });

  const labelDelay = safeSpringDelay(34, duration_frames, 0.6);
  const labelSpring = spring({
    frame: Math.max(0, frame - labelDelay),
    fps,
    config: tokens.motion.settle,
  });

  const isPositive = polarity === "positive";
  const glowColor = isPositive ? "16, 185, 129" : polarity === "negative" ? "244, 63, 94" : "56, 189, 248";
  const rightValueColor = isPositive ? "#34d399" : polarity === "negative" ? tokens.accent.rose : "#f8fafc";
  const vectorColor = isPositive ? "#34d399" : polarity === "negative" ? tokens.accent.rose : tokens.accent.cyan;

  return (
    <AbsoluteFill
      style={{
        fontFamily: tokens.font.family,
        opacity: sceneOpacity,
        transform: `scale(${cameraScale})`,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        padding: "60px 120px",
        overflow: "hidden",
      }}
    >
      <EditorialBackdrop glowColor={glowColor} glowOpacity={0.14} />

      {/* Main Transition Bridge */}
      <div
        style={{
          position: "relative",
          zIndex: 1,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          width: "100%",
          maxWidth: "1520px",
        }}
      >
        {/* Row of Baseline -> Vector -> Result */}
        <div
          style={{
            display: "flex",
            flexDirection: "row",
            alignItems: "center",
            justifyContent: "center",
            width: "100%",
            gap: "50px",
            marginBottom: "36px",
          }}
        >
          {/* Baseline Plaque (Subdued anchor) */}
          <div
            style={{
              opacity: leftSpring,
              transform: `translateX(${interpolate(leftSpring, [0, 1], [-24, 0])}px)`,
              display: "flex",
              flexDirection: "column",
              alignItems: "flex-end",
              flex: "1 1 0",
              maxWidth: "460px",
            }}
          >
            <div
              style={{
                fontSize: "16px",
                fontWeight: 700,
                textTransform: "uppercase",
                letterSpacing: "0.12em",
                color: "#64748b",
                marginBottom: "12px",
              }}
            >
              {baselineLabel}
            </div>
            <div
              style={{
                fontSize: "68px",
                fontWeight: 700,
                color: "#94a3b8",
                lineHeight: 1.05,
                fontVariantNumeric: "tabular-nums lining-nums",
                letterSpacing: "-0.03em",
              }}
            >
              {baselineValue || "Initial"}
            </div>
          </div>

          {/* Directional Transition Vector & Delta Pill */}
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              width: "180px",
              flexShrink: 0,
            }}
          >
            <svg
              width="180"
              height="32"
              viewBox="0 0 180 32"
              style={{ overflow: "visible", marginBottom: "10px" }}
            >
              {/* Subtle background guide line */}
              <line
                x1="0"
                y1="16"
                x2="170"
                y2="16"
                stroke="rgba(255, 255, 255, 0.08)"
                strokeWidth="2"
              />
              {/* Animated active stroke */}
              <path
                d="M 0 16 L 165 16 M 152 7 L 165 16 L 152 25"
                stroke={vectorColor}
                strokeWidth="2.5"
                fill="none"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeDasharray="200"
                strokeDashoffset={200 * (1 - vectorProgress)}
              />
            </svg>

            {delta && (
              <div
                style={{
                  fontSize: "16px",
                  fontWeight: 700,
                  color: vectorColor,
                  backgroundColor: polarity === "negative" ? "rgba(244, 63, 94, 0.14)" : isPositive ? "rgba(16, 185, 129, 0.14)" : "rgba(56, 189, 248, 0.14)",
                  padding: "4px 14px",
                  borderRadius: "6px",
                  border: `1px solid ${polarity === "negative" ? "rgba(244, 63, 94, 0.35)" : isPositive ? "rgba(16, 185, 129, 0.35)" : "rgba(56, 189, 248, 0.35)"}`,
                }}
              >
                {delta}
              </div>
            )}
          </div>

          {/* Transformed Result Plaque (Heroic) */}
          <div
            style={{
              opacity: rightSpring,
              transform: `scale(${interpolate(rightSpring, [0, 1], [0.94, 1])})`,
              display: "flex",
              flexDirection: "column",
              alignItems: "flex-start",
              flex: "1.2 1 0",
              maxWidth: "540px",
            }}
          >
            <div
              style={{
                fontSize: "16px",
                fontWeight: 700,
                textTransform: "uppercase",
                letterSpacing: "0.12em",
                color: vectorColor,
                marginBottom: "12px",
              }}
            >
              {context || "RESULT"}
            </div>
            <div
              style={{
                fontSize: "96px",
                fontWeight: 800,
                lineHeight: 1.05,
                textShadow: `0 8px 32px rgba(0, 0, 0, 0.7), 0 0 55px rgba(${glowColor}, 0.25)`,
              }}
            >
              {renderFormattedValue(value, 96, rightValueColor)}
            </div>
          </div>
        </div>

        {/* Semantic Takeaway Label */}
        {label && (
          <div
            style={{
              opacity: labelSpring,
              fontSize: "36px",
              fontWeight: 500,
              lineHeight: 1.36,
              color: "#cbd5e1",
              textAlign: "center",
              maxWidth: "1150px",
              letterSpacing: "-0.015em",
            }}
          >
            {label}
          </div>
        )}
      </div>
    </AbsoluteFill>
  );
}
