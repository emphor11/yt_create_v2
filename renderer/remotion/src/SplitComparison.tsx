import React from "react";
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { type SplitComparisonProps } from "./types";
import { tokens } from "./design-tokens";
import { safeAnimationWindow, safeSpringDelay } from "./animation-safety";

/**
 * Smart Number Formatter & Interpolator for Split Comparisons
 */
function formatValue(rawVal: string | number | undefined, progress: number, unit?: string): string {
  if (rawVal === undefined || rawVal === null || rawVal === "") return "";
  const unitSuffix = unit ? ` ${unit}` : "";

  if (typeof rawVal === "number") {
    const isFloat = rawVal % 1 !== 0;
    const current = progress * rawVal;
    const formattedNum = isFloat ? current.toFixed(1) : Math.round(current).toString();
    return `${formattedNum}${unitSuffix}`;
  }

  const str = String(rawVal).trim();
  const match = str.match(/^([^\d\.-]*)([\d,]+(?:\.\d+)?)(.*)$/);
  if (!match) {
    return `${str}${unitSuffix}`;
  }

  const prefix = match[1] || "";
  const numStr = match[2].replace(/,/g, "");
  const suffix = match[3] || "";
  const targetNum = parseFloat(numStr);

  if (isNaN(targetNum)) {
    return `${str}${unitSuffix}`;
  }

  const currentNum = progress * targetNum;
  const hasDecimals = numStr.includes(".");
  const decimalPlaces = hasDecimals ? (numStr.split(".")[1]?.length || 1) : 0;
  const formattedNum = decimalPlaces > 0 ? currentNum.toFixed(decimalPlaces) : Math.round(currentNum).toLocaleString();

  return `${prefix}${formattedNum}${suffix}${unitSuffix}`;
}

export function SplitComparison(props: SplitComparisonProps | any) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Normalize boundary props wrapper
  const resolvedProps: SplitComparisonProps = props.props ? props.props : props;
  const duration_frames = (props as any).duration_frames || (props as any).durationInFrames || 180;

  const headerLabel = resolvedProps.headerLabel || "";
  const rawCompLabel = (resolvedProps as any).comparison_label || resolvedProps.comparisonLabel || "";
  // Disambiguate so we don't duplicate identical text in both eyebrow and badge
  const comparisonLabel =
    rawCompLabel.trim().toLowerCase() === headerLabel.trim().toLowerCase()
      ? ""
      : rawCompLabel;

  const tone = (resolvedProps.tone || "neutral").toLowerCase();
  const delta = resolvedProps.delta || "";
  const winner = (resolvedProps.winner || "").toLowerCase().trim();
  const isLeftWinner = winner === "left" || winner === "a";
  const isRightWinner = winner === "right" || winner === "b";
  const hasWinner = isLeftWinner || isRightWinner;

  // Extract Left Side Data
  const leftRole =
    resolvedProps.leftRole ||
    resolvedProps.left?.role ||
    resolvedProps.left?.label ||
    "Option A";
  const leftLabel = resolvedProps.leftLabel || resolvedProps.left?.label || "";
  const leftValRaw =
    resolvedProps.leftValue !== undefined
      ? resolvedProps.leftValue
      : resolvedProps.left?.value !== undefined
      ? resolvedProps.left?.value
      : resolvedProps.left?.raw;
  const leftUnit = resolvedProps.leftUnit || resolvedProps.left?.unit || "";

  // Extract Right Side Data
  const rightRole =
    resolvedProps.rightRole ||
    resolvedProps.right?.role ||
    resolvedProps.right?.label ||
    "Option B";
  const rightLabel = resolvedProps.rightLabel || resolvedProps.right?.label || "";
  const rightValRaw =
    resolvedProps.rightValue !== undefined
      ? resolvedProps.rightValue
      : resolvedProps.right?.value !== undefined
      ? resolvedProps.right?.value
      : resolvedProps.right?.raw;
  const rightUnit = resolvedProps.rightUnit || resolvedProps.right?.unit || "";

  const footerLabel = resolvedProps.footerLabel || "";

  // Tone-Based Color Schemes
  let leftColor = tokens.accent.cyan;
  let rightColor = tokens.accent.blue;

  if (tone === "positive_negative") {
    leftColor = isLeftWinner ? tokens.accent.emerald : tokens.accent.rose;
    rightColor = isRightWinner ? tokens.accent.emerald : tokens.accent.rose;
  } else if (tone === "before_after") {
    leftColor = tokens.accent.amber;   // Before Baseline
    rightColor = tokens.accent.emerald; // After Strategy
  } else if (tone === "superiority") {
    leftColor = isLeftWinner ? tokens.accent.amber : "#94a3b8";
    rightColor = isRightWinner ? tokens.accent.amber : "#94a3b8";
  }

  // Duration-Safe Animation Timings
  // Header entrance
  const headerDelay = safeSpringDelay(0, duration_frames, 0.2);
  const headerSpring = spring({
    frame: Math.max(0, frame - headerDelay),
    fps,
    config: tokens.motion.reveal,
  });

  // Cards entrance
  const leftDelay = safeSpringDelay(4, duration_frames, 0.25);
  const leftSpring = spring({
    frame: Math.max(0, frame - leftDelay),
    fps,
    config: tokens.motion.reveal,
  });

  const rightDelay = safeSpringDelay(8, duration_frames, 0.3);
  const rightSpring = spring({
    frame: Math.max(0, frame - rightDelay),
    fps,
    config: tokens.motion.reveal,
  });

  // Central Divider / VS Chip
  const vsDelay = safeSpringDelay(12, duration_frames, 0.35);
  const vsSpring = spring({
    frame: Math.max(0, frame - vsDelay),
    fps,
    config: { damping: 14, stiffness: 120 },
  });

  // Number Count-Up Progress (guaranteed safe window)
  const [countStart, countEnd] = safeAnimationWindow(14, 46, duration_frames, 2);
  const countProgress = interpolate(
    frame,
    [countStart, countEnd],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // Delta callout entrance
  const deltaDelay = safeSpringDelay(24, duration_frames, 0.55);
  const deltaSpring = spring({
    frame: Math.max(0, frame - deltaDelay),
    fps,
    config: tokens.motion.impact,
  });

  const leftFormattedVal = formatValue(leftValRaw, countProgress, leftUnit);
  const rightFormattedVal = formatValue(rightValRaw, countProgress, rightUnit);

  return (
    <AbsoluteFill
      style={{
        background: "radial-gradient(ellipse 90% 70% at 50% 40%, rgba(15, 23, 42, 0.96) 0%, rgba(5, 7, 10, 0.99) 100%)",
        color: tokens.text.primary,
        fontFamily: tokens.font.family,
        overflow: "hidden",
        padding: "50px 80px",
      }}
    >
      {/* Cinematic Top and Bottom Subtle Letterbox Hairlines */}
      <div
        style={{
          position: "absolute",
          top: 24,
          left: 80,
          right: 80,
          height: "1px",
          background: "linear-gradient(90deg, transparent 0%, rgba(255, 255, 255, 0.12) 30%, rgba(255, 255, 255, 0.12) 70%, transparent 100%)",
        }}
      />
      <div
        style={{
          position: "absolute",
          bottom: 24,
          left: 80,
          right: 80,
          height: "1px",
          background: "linear-gradient(90deg, transparent 0%, rgba(255, 255, 255, 0.12) 30%, rgba(255, 255, 255, 0.12) 70%, transparent 100%)",
        }}
      />

      {/* Atmospheric Ambient Glow behind Winner */}
      {hasWinner && (
        <div
          style={{
            position: "absolute",
            top: "50%",
            left: isLeftWinner ? "30%" : "70%",
            transform: "translate(-50%, -50%)",
            width: "600px",
            height: "600px",
            borderRadius: "50%",
            background: isLeftWinner
              ? `radial-gradient(circle, ${leftColor}22 0%, transparent 70%)`
              : `radial-gradient(circle, ${rightColor}22 0%, transparent 70%)`,
            filter: "blur(60px)",
            pointerEvents: "none",
            zIndex: 0,
          }}
        />
      )}

      <div
        style={{
          position: "relative",
          display: "flex",
          flexDirection: "column",
          height: "100%",
          justifyContent: "space-between",
          zIndex: 1,
        }}
      >
        {/* Header Eyebrow & Optional Headline */}
        <header
          style={{
            textAlign: "center",
            opacity: headerSpring,
            transform: `translateY(${(1 - headerSpring) * -16}px)`,
          }}
        >
          {headerLabel ? (
            <div
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: 8,
                padding: "6px 18px",
                borderRadius: tokens.radius.pill,
                background: "rgba(255, 255, 255, 0.05)",
                border: "1px solid rgba(255, 255, 255, 0.12)",
                color: tokens.accent.cyan,
                fontSize: 13,
                fontWeight: 800,
                textTransform: "uppercase",
                letterSpacing: 2,
                boxShadow: "0 2px 10px rgba(0, 0, 0, 0.2)",
              }}
            >
              <span
                style={{
                  width: 6,
                  height: 6,
                  borderRadius: "50%",
                  backgroundColor: tokens.accent.cyan,
                  boxShadow: `0 0 8px ${tokens.accent.cyan}`,
                }}
              />
              {headerLabel}
            </div>
          ) : null}

          {comparisonLabel ? (
            <div
              style={{
                marginTop: 10,
                fontSize: 28,
                fontWeight: 900,
                letterSpacing: 1.5,
                textTransform: "uppercase",
                color: "#ffffff",
              }}
            >
              {comparisonLabel}
            </div>
          ) : null}
        </header>

        {/* Main Editorial Side-by-Side Cards with Matchup Divider */}
        <main
          style={{
            position: "relative",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: "36px",
            flex: 1,
            margin: "24px 0",
          }}
        >
          {/* LEFT COMPARISON CARD */}
          <div
            style={{
              flex: isLeftWinner ? 1.06 : hasWinner ? 0.94 : 1,
              position: "relative",
              background: isLeftWinner
                ? `linear-gradient(145deg, rgba(30, 41, 59, 0.92) 0%, rgba(15, 23, 42, 0.96) 100%)`
                : "rgba(15, 23, 42, 0.72)",
              border: isLeftWinner
                ? `2px solid ${leftColor}`
                : "1px solid rgba(255, 255, 255, 0.09)",
              borderRadius: "20px",
              padding: isLeftWinner ? "42px 34px" : "36px 30px",
              textAlign: "center",
              boxShadow: isLeftWinner
                ? `0 16px 40px ${leftColor}28, 0 0 20px ${leftColor}18`
                : "0 8px 30px rgba(0, 0, 0, 0.35)",
              backdropFilter: "blur(16px)",
              opacity: hasWinner && !isLeftWinner ? leftSpring * 0.82 : leftSpring,
              transform: `translateX(${(1 - leftSpring) * -40}px) scale(${isLeftWinner ? 1.02 : 1})`,
              transition: "transform 0.3s ease",
            }}
          >
            {/* Winner Pill Badge */}
            {isLeftWinner ? (
              <div
                style={{
                  position: "absolute",
                  top: "-15px",
                  left: "50%",
                  transform: "translateX(-50%)",
                  background: leftColor,
                  color: "#05070a",
                  fontSize: 11,
                  fontWeight: 900,
                  padding: "4px 16px",
                  borderRadius: tokens.radius.pill,
                  letterSpacing: 1.5,
                  textTransform: "uppercase",
                  boxShadow: `0 4px 14px ${leftColor}66`,
                  display: "flex",
                  alignItems: "center",
                  gap: 6,
                }}
              >
                <span>★</span> PRIMARY ADVANTAGE
              </div>
            ) : null}

            {/* Left Subject Name */}
            <div
              style={{
                fontSize: 22,
                fontWeight: 900,
                textTransform: "uppercase",
                letterSpacing: 1.8,
                color: leftColor,
                marginBottom: 8,
              }}
            >
              {leftRole}
            </div>

            {leftLabel ? (
              <div
                style={{
                  fontSize: 15,
                  color: tokens.text.secondary,
                  fontWeight: 600,
                  marginBottom: 20,
                  minHeight: "22px",
                }}
              >
                {leftLabel}
              </div>
            ) : (
              <div style={{ height: 22, marginBottom: 20 }} />
            )}

            {/* Left Hero Value */}
            <div
              style={{
                fontSize: isLeftWinner ? 74 : 64,
                fontWeight: 900,
                color: "#ffffff",
                lineHeight: 1,
                letterSpacing: -1.5,
                fontVariantNumeric: "tabular-nums",
                textShadow: isLeftWinner ? `0 0 30px ${leftColor}44` : "none",
              }}
            >
              {leftFormattedVal}
            </div>
          </div>

          {/* CENTRAL SLEEK MATCHUP DIVIDER */}
          <div
            style={{
              position: "relative",
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              height: "70%",
              opacity: vsSpring,
              transform: `scale(${vsSpring})`,
              flexShrink: 0,
              zIndex: 10,
            }}
          >
            {/* Top Hairline */}
            <div
              style={{
                width: "1px",
                flex: 1,
                background: "linear-gradient(180deg, transparent 0%, rgba(255, 255, 255, 0.2) 100%)",
              }}
            />

            {/* Central VS Chip */}
            <div
              style={{
                margin: "12px 0",
                padding: "8px 14px",
                borderRadius: "14px",
                background: "rgba(15, 23, 42, 0.95)",
                border: "1px solid rgba(255, 255, 255, 0.18)",
                fontSize: 13,
                fontWeight: 900,
                color: tokens.text.secondary,
                letterSpacing: 2,
                boxShadow: "0 6px 20px rgba(0, 0, 0, 0.5)",
              }}
            >
              VS
            </div>

            {/* Bottom Hairline */}
            <div
              style={{
                width: "1px",
                flex: 1,
                background: "linear-gradient(180deg, rgba(255, 255, 255, 0.2) 0%, transparent 100%)",
              }}
            />
          </div>

          {/* RIGHT COMPARISON CARD */}
          <div
            style={{
              flex: isRightWinner ? 1.06 : hasWinner ? 0.94 : 1,
              position: "relative",
              background: isRightWinner
                ? `linear-gradient(145deg, rgba(30, 41, 59, 0.92) 0%, rgba(15, 23, 42, 0.96) 100%)`
                : "rgba(15, 23, 42, 0.72)",
              border: isRightWinner
                ? `2px solid ${rightColor}`
                : "1px solid rgba(255, 255, 255, 0.09)",
              borderRadius: "20px",
              padding: isRightWinner ? "42px 34px" : "36px 30px",
              textAlign: "center",
              boxShadow: isRightWinner
                ? `0 16px 40px ${rightColor}28, 0 0 20px ${rightColor}18`
                : "0 8px 30px rgba(0, 0, 0, 0.35)",
              backdropFilter: "blur(16px)",
              opacity: hasWinner && !isRightWinner ? rightSpring * 0.82 : rightSpring,
              transform: `translateX(${(1 - rightSpring) * 40}px) scale(${isRightWinner ? 1.02 : 1})`,
              transition: "transform 0.3s ease",
            }}
          >
            {/* Winner Pill Badge */}
            {isRightWinner ? (
              <div
                style={{
                  position: "absolute",
                  top: "-15px",
                  left: "50%",
                  transform: "translateX(-50%)",
                  background: rightColor,
                  color: "#05070a",
                  fontSize: 11,
                  fontWeight: 900,
                  padding: "4px 16px",
                  borderRadius: tokens.radius.pill,
                  letterSpacing: 1.5,
                  textTransform: "uppercase",
                  boxShadow: `0 4px 14px ${rightColor}66`,
                  display: "flex",
                  alignItems: "center",
                  gap: 6,
                }}
              >
                <span>★</span> PRIMARY ADVANTAGE
              </div>
            ) : null}

            {/* Right Subject Name */}
            <div
              style={{
                fontSize: 22,
                fontWeight: 900,
                textTransform: "uppercase",
                letterSpacing: 1.8,
                color: rightColor,
                marginBottom: 8,
              }}
            >
              {rightRole}
            </div>

            {rightLabel ? (
              <div
                style={{
                  fontSize: 15,
                  color: tokens.text.secondary,
                  fontWeight: 600,
                  marginBottom: 20,
                  minHeight: "22px",
                }}
              >
                {rightLabel}
              </div>
            ) : (
              <div style={{ height: 22, marginBottom: 20 }} />
            )}

            {/* Right Hero Value */}
            <div
              style={{
                fontSize: isRightWinner ? 74 : 64,
                fontWeight: 900,
                color: "#ffffff",
                lineHeight: 1,
                letterSpacing: -1.5,
                fontVariantNumeric: "tabular-nums",
                textShadow: isRightWinner ? `0 0 30px ${rightColor}44` : "none",
              }}
            >
              {rightFormattedVal}
            </div>
          </div>
        </main>

        {/* Bottom Delta Callout Emphasis */}
        {delta ? (
          <div
            style={{
              textAlign: "center",
              opacity: deltaSpring,
              transform: `translateY(${(1 - deltaSpring) * 14}px)`,
              marginBottom: 8,
            }}
          >
            <div
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: 8,
                fontSize: 18,
                fontWeight: 900,
                color: hasWinner
                  ? isLeftWinner
                    ? leftColor
                    : rightColor
                  : tokens.accent.emerald,
                background: hasWinner
                  ? isLeftWinner
                    ? `${leftColor}18`
                    : `${rightColor}18`
                  : "rgba(16, 185, 129, 0.14)",
                border: `1px solid ${
                  hasWinner
                    ? isLeftWinner
                      ? `${leftColor}55`
                      : `${rightColor}55`
                    : "rgba(16, 185, 129, 0.4)"
                }`,
                padding: "8px 24px",
                borderRadius: tokens.radius.pill,
                letterSpacing: 1.5,
                textTransform: "uppercase",
                boxShadow: "0 6px 20px rgba(0, 0, 0, 0.3)",
              }}
            >
              <span style={{ fontSize: 16 }}>⚡</span>
              <span>{delta.toUpperCase().includes("DIFF") || delta.toUpperCase().includes("GAP") || delta.toUpperCase().includes("ADVANTAGE") ? delta : `${delta} NET SPREAD`}</span>
            </div>
          </div>
        ) : null}

        {/* Footer */}
        {footerLabel ? (
          <footer
            style={{
              textAlign: "center",
              fontSize: 16,
              color: tokens.text.muted,
              fontWeight: 600,
              letterSpacing: 0.5,
            }}
          >
            {footerLabel}
          </footer>
        ) : null}
      </div>
    </AbsoluteFill>
  );
}
