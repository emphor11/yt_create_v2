import React from 'react';
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { tokens } from '../design-tokens';
import { CalculationStoryProps } from '../types';
import { safeAnimationWindow, safeSpringDelay } from '../animation-safety';

function parsePercent(str: string): number {
  const match = str.match(/(\d+(?:\.\d+)?)\s*%/);
  if (match) {
    const val = parseFloat(match[1]);
    if (!isNaN(val) && val > 0 && val <= 100) return val;
  }
  return 40; // Default illustrative 40%
}

export function CalculationStory(props: CalculationStoryProps | any) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const resolvedProps: CalculationStoryProps = (props as any).props || props;
  const duration_frames = (props as any).duration_frames || 180;

  const inputLabel = resolvedProps.inputLabel || "Input";
  const inputValue = resolvedProps.inputValue || "0";
  const operationLabel = resolvedProps.operationLabel || "";
  const rateLabel = resolvedProps.rateLabel || "";
  const resultLabel = resolvedProps.resultLabel || "Result";
  const resultValue = resolvedProps.resultValue || "0";
  const note = resolvedProps.note || null;
  const polarity = resolvedProps.polarity || null;
  const timeframe = resolvedProps.timeframe || null;
  const secondaryLabel = resolvedProps.secondaryLabel || null;
  const secondaryValue = resolvedProps.secondaryValue || null;

  // Semantic treatment resolution
  const explicitType = (
    resolvedProps.operationType ||
    resolvedProps.variant ||
    (resolvedProps as any).treatment
  );

  const op = operationLabel.trim().toLowerCase();
  const rate = rateLabel.trim().toLowerCase();

  let treatment: "multiplication" | "addition" | "subtraction" | "allocation" | "growth" | "neutral";

  if (
    explicitType === "addition" ||
    op === "+" ||
    op === "plus" ||
    op === "add" ||
    op === "and"
  ) {
    treatment = "addition";
  } else if (
    explicitType === "subtraction" ||
    op === "-" ||
    op === "minus" ||
    op === "subtract" ||
    op === "drag" ||
    op === "fee" ||
    op === "tax" ||
    op === "deduction"
  ) {
    treatment = "subtraction";
  } else if (
    explicitType === "allocation" ||
    op === "allocation" ||
    op === "allocated" ||
    op === "portion" ||
    op === "%" ||
    (rate.includes("%") && (op.includes("portion") || op.includes("allocation") || op.includes("of") || op.includes("carve")))
  ) {
    treatment = "allocation";
  } else if (
    explicitType === "growth" ||
    op === "growth" ||
    op === "grows to" ||
    op === "becomes" ||
    op === "→" ||
    Boolean(timeframe)
  ) {
    treatment = "growth";
  } else if (explicitType === "neutral" || (!op && !rate)) {
    treatment = "neutral";
  } else if (
    explicitType === "multiplication" ||
    op === "×" ||
    op === "*" ||
    op === "times" ||
    op === "multiplied" ||
    rate.includes("%") ||
    rate.includes("rate")
  ) {
    treatment = "multiplication";
  } else {
    treatment = "neutral";
  }

  // Scene entrance fade
  const sceneOpacity = interpolate(
    frame,
    [0, Math.min(8, Math.max(1, duration_frames - 1))],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // -------------------------------------------------------------------------
  // Treatment 1: MULTIPLICATION (Base × Rate Modifier → Result)
  // -------------------------------------------------------------------------
  if (treatment === "multiplication") {
    const inputDelay = safeSpringDelay(8, duration_frames, 0.2);
    const inputSpring = spring({
      frame: Math.max(0, frame - inputDelay),
      fps,
      config: tokens.motion.reveal,
    });

    const opDelay = safeSpringDelay(18, duration_frames, 0.35);
    const opSpring = spring({
      frame: Math.max(0, frame - opDelay),
      fps,
      config: tokens.motion.impact,
    });

    const [arrowStart, arrowEnd] = safeAnimationWindow(24, 46, duration_frames);
    const arrowProgress = interpolate(
      frame,
      [arrowStart, arrowEnd],
      [0, 1],
      { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
    );

    const resultDelay = safeSpringDelay(38, duration_frames, 0.58);
    const resultSpring = spring({
      frame: Math.max(0, frame - resultDelay),
      fps,
      config: tokens.motion.settle,
    });

    const noteDelay = safeSpringDelay(48, duration_frames, 0.72);
    const noteSpring = spring({
      frame: Math.max(0, frame - noteDelay),
      fps,
      config: tokens.motion.gentle,
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
            gap: "36px",
            width: "100%",
            maxWidth: "1600px",
          }}
        >
          {/* Base Input Card */}
          <div
            style={{
              opacity: inputSpring,
              transform: `translateX(${interpolate(inputSpring, [0, 1], [-40, 0])}px)`,
              flex: 1,
              maxWidth: "440px",
              minHeight: "320px",
              backgroundColor: tokens.bg.cardLeft,
              borderRadius: tokens.radius.card,
              border: `1px solid ${tokens.bg.border}`,
              padding: "40px 36px",
              display: "flex",
              flexDirection: "column",
              justifyContent: "center",
              boxShadow: "0 20px 40px -15px rgba(0, 0, 0, 0.5)",
            }}
          >
            <div
              style={{
                fontSize: "18px",
                fontWeight: 600,
                textTransform: "uppercase",
                letterSpacing: "0.08em",
                color: tokens.text.secondary,
                marginBottom: "16px",
              }}
            >
              {inputLabel}
            </div>
            <div
              style={{
                fontSize: "52px",
                fontWeight: 800,
                color: tokens.text.primary,
                lineHeight: 1.1,
              }}
            >
              {inputValue}
            </div>
          </div>

          {/* Center Multiplier Connector */}
          <div
            style={{
              opacity: opSpring,
              transform: `scale(${interpolate(opSpring, [0, 1], [0.6, 1])})`,
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

            {/* Operator Badge */}
            <div
              style={{
                width: "68px",
                height: "68px",
                borderRadius: "50%",
                backgroundColor: "rgba(15, 23, 42, 0.9)",
                border: `2px solid ${tokens.accent.cyan}`,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: "36px",
                fontWeight: 800,
                color: tokens.accent.cyan,
                boxShadow: `0 0 20px rgba(6, 182, 212, 0.3)`,
                marginBottom: "10px",
              }}
            >
              {operationLabel || "×"}
            </div>

            {/* Rate Modifier Pill */}
            {rateLabel && (
              <div
                style={{
                  fontSize: "17px",
                  fontWeight: 600,
                  color: tokens.accent.cyan,
                  backgroundColor: "rgba(6, 182, 212, 0.12)",
                  border: "1px solid rgba(6, 182, 212, 0.25)",
                  padding: "4px 12px",
                  borderRadius: tokens.radius.chip,
                  textAlign: "center",
                  lineHeight: 1.2,
                }}
              >
                {rateLabel}
              </div>
            )}
          </div>

          {/* Dominant Result Card */}
          <div
            style={{
              opacity: resultSpring,
              transform: `translateX(${interpolate(resultSpring, [0, 1], [40, 0])}px)`,
              flex: 1.3,
              maxWidth: "580px",
              minHeight: "360px",
              backgroundColor: tokens.bg.surface,
              borderRadius: tokens.radius.card,
              border: `2px solid rgba(6, 182, 212, 0.45)`,
              padding: "44px 40px",
              display: "flex",
              flexDirection: "column",
              justifyContent: "center",
              boxShadow: "0 25px 60px -15px rgba(6, 182, 212, 0.2), 0 20px 40px -15px rgba(0, 0, 0, 0.7)",
              position: "relative",
            }}
          >
            <div
              style={{
                fontSize: "20px",
                fontWeight: 700,
                textTransform: "uppercase",
                letterSpacing: "0.08em",
                color: tokens.accent.cyan,
                marginBottom: "16px",
              }}
            >
              {resultLabel}
            </div>
            <div
              style={{
                fontSize: "72px",
                fontWeight: 800,
                color: tokens.text.primary,
                lineHeight: 1.05,
                marginBottom: note ? "20px" : "0",
              }}
            >
              {resultValue}
            </div>

            {note && (
              <div
                style={{
                  opacity: noteSpring,
                  display: "inline-flex",
                  alignSelf: "flex-start",
                  padding: "8px 16px",
                  borderRadius: tokens.radius.chip,
                  backgroundColor: "rgba(16, 185, 129, 0.12)",
                  border: `1px solid rgba(16, 185, 129, 0.3)`,
                  color: tokens.accent.emerald,
                  fontSize: "16px",
                  fontWeight: 600,
                }}
              >
                {note}
              </div>
            )}
          </div>
        </div>
      </AbsoluteFill>
    );
  }

  // -------------------------------------------------------------------------
  // Treatment 2: ADDITION (Input A + Input B ↘ Converging Sum)
  // -------------------------------------------------------------------------
  if (treatment === "addition") {
    const cardADelay = safeSpringDelay(8, duration_frames, 0.2);
    const cardASpring = spring({
      frame: Math.max(0, frame - cardADelay),
      fps,
      config: tokens.motion.reveal,
    });

    const cardBDelay = safeSpringDelay(16, duration_frames, 0.35);
    const cardBSpring = spring({
      frame: Math.max(0, frame - cardBDelay),
      fps,
      config: tokens.motion.reveal,
    });

    const [splineStart, splineEnd] = safeAnimationWindow(24, 48, duration_frames);
    const splineProgress = interpolate(
      frame,
      [splineStart, splineEnd],
      [0, 1],
      { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
    );

    const sumDelay = safeSpringDelay(42, duration_frames, 0.6);
    const sumSpring = spring({
      frame: Math.max(0, frame - sumDelay),
      fps,
      config: tokens.motion.impact,
    });

    const secLabel = secondaryLabel || rateLabel || "Additional Input";
    const secVal = secondaryValue || rateLabel || "";

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
            gap: "36px",
            width: "100%",
            maxWidth: "1600px",
          }}
        >
          {/* Left Column: Stacked Inputs with Plus Operator */}
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              gap: "18px",
              flex: 1,
              maxWidth: "460px",
              position: "relative",
            }}
          >
            {/* Input Card A */}
            <div
              style={{
                opacity: cardASpring,
                transform: `translateX(${interpolate(cardASpring, [0, 1], [-40, 0])}px)`,
                backgroundColor: tokens.bg.cardLeft,
                borderRadius: tokens.radius.card,
                border: `1px solid ${tokens.bg.border}`,
                borderLeft: `4px solid ${tokens.accent.cyan}`,
                padding: "24px 30px",
                boxShadow: "0 10px 30px -10px rgba(0, 0, 0, 0.4)",
              }}
            >
              <div
                style={{
                  fontSize: "16px",
                  fontWeight: 600,
                  textTransform: "uppercase",
                  letterSpacing: "0.08em",
                  color: tokens.text.secondary,
                  marginBottom: "8px",
                }}
              >
                {inputLabel}
              </div>
              <div
                style={{
                  fontSize: "42px",
                  fontWeight: 800,
                  color: tokens.text.primary,
                  lineHeight: 1.1,
                }}
              >
                {inputValue}
              </div>
            </div>

            {/* Centered Addition Badge */}
            <div
              style={{
                position: "absolute",
                left: "50%",
                top: "50%",
                transform: "translate(-50%, -50%)",
                width: "40px",
                height: "40px",
                borderRadius: "50%",
                backgroundColor: "rgba(15, 23, 42, 0.95)",
                border: `2px solid ${tokens.accent.emerald}`,
                color: tokens.accent.emerald,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: "24px",
                fontWeight: 800,
                zIndex: 2,
                boxShadow: "0 0 16px rgba(16, 185, 129, 0.4)",
              }}
            >
              +
            </div>

            {/* Input Card B */}
            <div
              style={{
                opacity: cardBSpring,
                transform: `translateX(${interpolate(cardBSpring, [0, 1], [-40, 0])}px)`,
                backgroundColor: tokens.bg.cardLeft,
                borderRadius: tokens.radius.card,
                border: `1px solid ${tokens.bg.border}`,
                borderLeft: `4px solid ${tokens.accent.emerald}`,
                padding: "24px 30px",
                boxShadow: "0 10px 30px -10px rgba(0, 0, 0, 0.4)",
              }}
            >
              <div
                style={{
                  fontSize: "16px",
                  fontWeight: 600,
                  textTransform: "uppercase",
                  letterSpacing: "0.08em",
                  color: tokens.text.secondary,
                  marginBottom: "8px",
                }}
              >
                {secLabel}
              </div>
              <div
                style={{
                  fontSize: "42px",
                  fontWeight: 800,
                  color: tokens.accent.emerald,
                  lineHeight: 1.1,
                }}
              >
                {secVal}
              </div>
            </div>
          </div>

          {/* Center: Converging Dual Splines */}
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              width: "160px",
            }}
          >
            <svg
              width="160"
              height="180"
              viewBox="0 0 160 180"
              style={{ overflow: "visible" }}
            >
              {/* Top spline from Card A */}
              <path
                d="M 0 45 C 80 45, 90 90, 150 90"
                stroke={tokens.accent.emerald}
                strokeWidth="3.5"
                fill="none"
                strokeLinecap="round"
                strokeDasharray="220"
                strokeDashoffset={220 * (1 - splineProgress)}
              />
              {/* Bottom spline from Card B */}
              <path
                d="M 0 135 C 80 135, 90 90, 150 90"
                stroke={tokens.accent.emerald}
                strokeWidth="3.5"
                fill="none"
                strokeLinecap="round"
                strokeDasharray="220"
                strokeDashoffset={220 * (1 - splineProgress)}
              />
              {/* Converged Arrowhead */}
              <path
                d="M 135 80 L 150 90 L 135 100"
                stroke={tokens.accent.emerald}
                strokeWidth="4"
                fill="none"
                strokeLinecap="round"
                strokeLinejoin="round"
                opacity={splineProgress > 0.8 ? 1 : 0}
              />
            </svg>
          </div>

          {/* Right: Combined Sum Card */}
          <div
            style={{
              opacity: sumSpring,
              transform: `scale(${interpolate(sumSpring, [0, 1], [0.88, 1])})`,
              flex: 1.3,
              maxWidth: "580px",
              minHeight: "360px",
              backgroundColor: tokens.bg.surface,
              borderRadius: tokens.radius.card,
              border: `2px solid rgba(16, 185, 129, 0.6)`,
              padding: "44px 40px",
              display: "flex",
              flexDirection: "column",
              justifyContent: "center",
              boxShadow: "0 25px 60px -15px rgba(16, 185, 129, 0.25), 0 20px 40px -15px rgba(0, 0, 0, 0.7)",
            }}
          >
            <div
              style={{
                fontSize: "18px",
                fontWeight: 700,
                textTransform: "uppercase",
                letterSpacing: "0.08em",
                color: tokens.accent.emerald,
                marginBottom: "14px",
              }}
            >
              {resultLabel || "COMBINED TOTAL"}
            </div>
            <div
              style={{
                fontSize: "76px",
                fontWeight: 800,
                color: "#34d399",
                lineHeight: 1.05,
                marginBottom: note ? "18px" : "0",
              }}
            >
              {resultValue}
            </div>
            {note && (
              <div
                style={{
                  fontSize: "18px",
                  fontWeight: 500,
                  color: tokens.text.secondary,
                }}
              >
                {note}
              </div>
            )}
          </div>
        </div>
      </AbsoluteFill>
    );
  }

  // -------------------------------------------------------------------------
  // Treatment 3: SUBTRACTION / DEDUCTION (Starting - Deduction → Net Retained)
  // -------------------------------------------------------------------------
  if (treatment === "subtraction") {
    const grossDelay = safeSpringDelay(8, duration_frames, 0.2);
    const grossSpring = spring({
      frame: Math.max(0, frame - grossDelay),
      fps,
      config: tokens.motion.reveal,
    });

    const deductDelay = safeSpringDelay(20, duration_frames, 0.38);
    const deductSpring = spring({
      frame: Math.max(0, frame - deductDelay),
      fps,
      config: tokens.motion.impact,
    });

    const [arrowStart, arrowEnd] = safeAnimationWindow(28, 50, duration_frames);
    const arrowProgress = interpolate(
      frame,
      [arrowStart, arrowEnd],
      [0, 1],
      { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
    );

    const netDelay = safeSpringDelay(42, duration_frames, 0.62);
    const netSpring = spring({
      frame: Math.max(0, frame - netDelay),
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
            gap: "32px",
            width: "100%",
            maxWidth: "1650px",
          }}
        >
          {/* Starting Gross Corpus */}
          <div
            style={{
              opacity: grossSpring,
              transform: `translateX(${interpolate(grossSpring, [0, 1], [-40, 0])}px)`,
              flex: 1,
              maxWidth: "420px",
              minHeight: "320px",
              backgroundColor: tokens.bg.cardLeft,
              borderRadius: tokens.radius.card,
              border: `1px solid ${tokens.bg.border}`,
              padding: "36px 36px",
              display: "flex",
              flexDirection: "column",
              justifyContent: "center",
              boxShadow: "0 15px 35px -10px rgba(0, 0, 0, 0.5)",
            }}
          >
            <div
              style={{
                fontSize: "17px",
                fontWeight: 600,
                textTransform: "uppercase",
                letterSpacing: "0.08em",
                color: tokens.text.muted,
                marginBottom: "14px",
              }}
            >
              {inputLabel || "GROSS AMOUNT"}
            </div>
            <div
              style={{
                fontSize: "48px",
                fontWeight: 800,
                color: tokens.text.primary,
                lineHeight: 1.1,
              }}
            >
              {inputValue}
            </div>
          </div>

          {/* Deduction Component (Distinct Rose Alert) */}
          <div
            style={{
              opacity: deductSpring,
              transform: `scale(${interpolate(deductSpring, [0, 1], [0.8, 1])})`,
              flex: 0.9,
              maxWidth: "340px",
              minHeight: "260px",
              backgroundColor: "rgba(244, 63, 94, 0.12)",
              borderRadius: tokens.radius.card,
              border: `2px solid rgba(244, 63, 94, 0.45)`,
              padding: "28px 30px",
              display: "flex",
              flexDirection: "column",
              justifyContent: "center",
              position: "relative",
              boxShadow: "0 15px 40px -10px rgba(244, 63, 94, 0.25)",
            }}
          >
            <div
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: "6px",
                fontSize: "15px",
                fontWeight: 800,
                textTransform: "uppercase",
                letterSpacing: "0.08em",
                color: tokens.accent.rose,
                marginBottom: "10px",
              }}
            >
              <span>−</span>
              <span>{secondaryLabel || (operationLabel && operationLabel !== "-" && operationLabel !== "−" ? operationLabel : "DEDUCTION / DRAG")}</span>
            </div>
            <div
              style={{
                fontSize: "38px",
                fontWeight: 800,
                color: tokens.accent.rose,
                lineHeight: 1.1,
              }}
            >
              {secondaryValue || rateLabel || "− Tax / Fee"}
            </div>
            {secondaryValue && rateLabel && rateLabel !== secondaryValue && (
              <div
                style={{
                  fontSize: "14px",
                  fontWeight: 600,
                  color: "rgba(244, 63, 94, 0.85)",
                  marginTop: "8px",
                }}
              >
                {rateLabel}
              </div>
            )}
          </div>

          {/* Subtraction Vector Arrow */}
          <div style={{ width: "80px", display: "flex", alignItems: "center", justifyContent: "center" }}>
            <svg width="80" height="30" viewBox="0 0 80 30">
              <path
                d="M 0 15 L 70 15 M 55 5 L 70 15 L 55 25"
                stroke={tokens.accent.cyan}
                strokeWidth="3.5"
                fill="none"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeDasharray="100"
                strokeDashoffset={100 * (1 - arrowProgress)}
              />
            </svg>
          </div>

          {/* Net Remaining Card */}
          <div
            style={{
              opacity: netSpring,
              transform: `translateX(${interpolate(netSpring, [0, 1], [40, 0])}px)`,
              flex: 1.2,
              maxWidth: "520px",
              minHeight: "340px",
              backgroundColor: tokens.bg.surface,
              borderRadius: tokens.radius.card,
              border: `2px solid rgba(56, 189, 248, 0.4)`,
              padding: "40px 38px",
              display: "flex",
              flexDirection: "column",
              justifyContent: "center",
              boxShadow: "0 25px 50px -15px rgba(0, 0, 0, 0.7)",
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
              {resultLabel || "NET REMAINING"}
            </div>
            <div
              style={{
                fontSize: "68px",
                fontWeight: 800,
                color: "#f8fafc",
                lineHeight: 1.05,
                marginBottom: note ? "16px" : "0",
              }}
            >
              {resultValue}
            </div>
            {note && (
              <div
                style={{
                  fontSize: "17px",
                  fontWeight: 600,
                  color: tokens.text.secondary,
                }}
              >
                {note}
              </div>
            )}
          </div>
        </div>
      </AbsoluteFill>
    );
  }

  // -------------------------------------------------------------------------
  // Treatment 4: PERCENTAGE ALLOCATION (Total → Proportional Bar Segment → Carved Portion)
  // -------------------------------------------------------------------------
  if (treatment === "allocation") {
    const totalDelay = safeSpringDelay(8, duration_frames, 0.2);
    const totalSpring = spring({
      frame: Math.max(0, frame - totalDelay),
      fps,
      config: tokens.motion.reveal,
    });

    const allocPercent = parsePercent(rateLabel || "40%");

    const [barStart, barEnd] = safeAnimationWindow(20, 48, duration_frames);
    const barProgress = interpolate(
      frame,
      [barStart, barEnd],
      [0, 1],
      { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
    );

    const allocDelay = safeSpringDelay(40, duration_frames, 0.6);
    const allocSpring = spring({
      frame: Math.max(0, frame - allocDelay),
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
        <div
          style={{
            display: "flex",
            flexDirection: "row",
            alignItems: "center",
            justifyContent: "center",
            gap: "40px",
            width: "100%",
            maxWidth: "1600px",
            marginBottom: "32px",
          }}
        >
          {/* Total Corpus Source Card */}
          <div
            style={{
              opacity: totalSpring,
              transform: `translateX(${interpolate(totalSpring, [0, 1], [-40, 0])}px)`,
              flex: 1,
              maxWidth: "460px",
              minHeight: "320px",
              backgroundColor: tokens.bg.cardLeft,
              borderRadius: tokens.radius.card,
              border: `1px solid ${tokens.bg.border}`,
              padding: "40px 38px",
              display: "flex",
              flexDirection: "column",
              justifyContent: "center",
              boxShadow: "0 20px 40px -15px rgba(0, 0, 0, 0.5)",
            }}
          >
            <div
              style={{
                fontSize: "18px",
                fontWeight: 600,
                textTransform: "uppercase",
                letterSpacing: "0.08em",
                color: tokens.text.secondary,
                marginBottom: "14px",
              }}
            >
              {inputLabel || "TOTAL PORTFOLIO"}
            </div>
            <div
              style={{
                fontSize: "52px",
                fontWeight: 800,
                color: tokens.text.primary,
                lineHeight: 1.1,
              }}
            >
              {inputValue}
            </div>
          </div>

          {/* Center: Visual Proportional Carve-Out Bar */}
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              width: "380px",
            }}
          >
            <div
              style={{
                fontSize: "17px",
                fontWeight: 700,
                color: tokens.accent.cyan,
                textTransform: "uppercase",
                letterSpacing: "0.08em",
                marginBottom: "12px",
              }}
            >
              {rateLabel || `${allocPercent}% ALLOCATION`}
            </div>

            {/* Proportional Segment Bar */}
            <div
              style={{
                width: "100%",
                height: "36px",
                borderRadius: tokens.radius.chip,
                backgroundColor: "rgba(255, 255, 255, 0.08)",
                border: `1px solid ${tokens.bg.border}`,
                overflow: "hidden",
                position: "relative",
                marginBottom: "14px",
              }}
            >
              <div
                style={{
                  width: `${barProgress * allocPercent}%`,
                  height: "100%",
                  background: "linear-gradient(90deg, #06b6d4 0%, #3b82f6 100%)",
                  borderRadius: tokens.radius.chip,
                  boxShadow: "0 0 16px rgba(6, 182, 212, 0.5)",
                }}
              />
            </div>

            {/* Arrow indicating carved-out portion */}
            <svg width="240" height="24" viewBox="0 0 240 24">
              <path
                d="M 0 12 L 230 12 M 215 4 L 230 12 L 215 20"
                stroke={tokens.accent.cyan}
                strokeWidth="3"
                fill="none"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </div>

          {/* Allocated Portion Result Card */}
          <div
            style={{
              opacity: allocSpring,
              transform: `scale(${interpolate(allocSpring, [0, 1], [0.9, 1])})`,
              flex: 1.2,
              maxWidth: "540px",
              minHeight: "340px",
              backgroundColor: tokens.bg.surface,
              borderRadius: tokens.radius.card,
              border: `2px solid ${tokens.accent.cyan}`,
              padding: "44px 40px",
              display: "flex",
              flexDirection: "column",
              justifyContent: "center",
              boxShadow: "0 25px 60px -15px rgba(6, 182, 212, 0.25), 0 20px 40px -15px rgba(0, 0, 0, 0.7)",
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
              {resultLabel || "ALLOCATED PORTION"}
            </div>
            <div
              style={{
                fontSize: "72px",
                fontWeight: 800,
                color: "#f8fafc",
                lineHeight: 1.05,
              }}
            >
              {resultValue}
            </div>
          </div>
        </div>

        {note && (
          <div
            style={{
              fontSize: "20px",
              fontWeight: 500,
              color: tokens.text.secondary,
              textAlign: "center",
            }}
          >
            {note}
          </div>
        )}
      </AbsoluteFill>
    );
  }

  // -------------------------------------------------------------------------
  // Treatment 5: GROWTH / TRANSFORMATION (Starting → Growth Vector → Future Result)
  // -------------------------------------------------------------------------
  if (treatment === "growth") {
    const startDelay = safeSpringDelay(8, duration_frames, 0.2);
    const startSpring = spring({
      frame: Math.max(0, frame - startDelay),
      fps,
      config: tokens.motion.reveal,
    });

    const [journeyStart, journeyEnd] = safeAnimationWindow(20, 50, duration_frames);
    const journeyProgress = interpolate(
      frame,
      [journeyStart, journeyEnd],
      [0, 1],
      { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
    );

    const futureDelay = safeSpringDelay(40, duration_frames, 0.6);
    const futureSpring = spring({
      frame: Math.max(0, frame - futureDelay),
      fps,
      config: tokens.motion.impact,
    });

    const [glowStart, glowEnd] = safeAnimationWindow(
      Math.round(duration_frames * 0.4),
      Math.round(duration_frames * 0.7),
      duration_frames
    );
    const glowBloom = interpolate(
      frame,
      [glowStart, glowEnd],
      [0.08, 0.25],
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
        {/* Future Growth Radiant Aura */}
        <div
          style={{
            position: "absolute",
            right: "15%",
            width: "700px",
            height: "700px",
            borderRadius: "50%",
            background: `radial-gradient(circle, rgba(16, 185, 129, ${glowBloom}) 0%, transparent 70%)`,
            pointerEvents: "none",
            zIndex: 0,
          }}
        />

        <div
          style={{
            display: "flex",
            flexDirection: "row",
            alignItems: "center",
            justifyContent: "center",
            gap: "36px",
            width: "100%",
            maxWidth: "1650px",
            zIndex: 1,
          }}
        >
          {/* Starting Corpus Card */}
          <div
            style={{
              opacity: startSpring,
              transform: `translateX(${interpolate(startSpring, [0, 1], [-40, 0])}px)`,
              flex: 1,
              maxWidth: "420px",
              minHeight: "320px",
              backgroundColor: tokens.bg.cardLeft,
              borderRadius: tokens.radius.card,
              border: `1px solid ${tokens.bg.border}`,
              padding: "36px 36px",
              display: "flex",
              flexDirection: "column",
              justifyContent: "center",
              boxShadow: "0 15px 35px -10px rgba(0, 0, 0, 0.5)",
            }}
          >
            <div
              style={{
                fontSize: "17px",
                fontWeight: 600,
                textTransform: "uppercase",
                letterSpacing: "0.08em",
                color: tokens.text.muted,
                marginBottom: "14px",
              }}
            >
              {inputLabel || "INITIAL INVESTMENT"}
            </div>
            <div
              style={{
                fontSize: "52px",
                fontWeight: 800,
                color: tokens.text.secondary,
                lineHeight: 1.1,
              }}
            >
              {inputValue}
            </div>
          </div>

          {/* Growth Journey Vector */}
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              width: "240px",
            }}
          >
            {/* Timeline Horizon Chip */}
            <div
              style={{
                fontSize: "16px",
                fontWeight: 700,
                color: tokens.accent.emerald,
                backgroundColor: "rgba(16, 185, 129, 0.12)",
                border: "1px solid rgba(16, 185, 129, 0.3)",
                padding: "6px 16px",
                borderRadius: tokens.radius.pill,
                textTransform: "uppercase",
                letterSpacing: "0.08em",
                marginBottom: "10px",
                textAlign: "center",
              }}
            >
              {timeframe || "COMPOUNDING JOURNEY"}
            </div>

            {/* Gradient Vector Beam */}
            <svg
              width="240"
              height="36"
              viewBox="0 0 240 36"
              style={{ overflow: "visible" }}
            >
              <defs>
                <linearGradient id="growthGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stopColor={tokens.accent.cyan} />
                  <stop offset="100%" stopColor={tokens.accent.emerald} />
                </linearGradient>
              </defs>
              <path
                d="M 0 18 L 225 18 M 210 8 L 225 18 L 210 28"
                stroke="url(#growthGrad)"
                strokeWidth="4"
                fill="none"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeDasharray="260"
                strokeDashoffset={260 * (1 - journeyProgress)}
              />
            </svg>

            {/* Compounding Rate / Driver Subtitle */}
            {rateLabel && (
              <div
                style={{
                  fontSize: "15px",
                  fontWeight: 600,
                  color: tokens.text.secondary,
                  marginTop: "10px",
                  textAlign: "center",
                  letterSpacing: "0.04em",
                }}
              >
                {rateLabel}
              </div>
            )}
          </div>

          {/* Future Expanded Result Card */}
          <div
            style={{
              opacity: futureSpring,
              transform: `scale(${interpolate(futureSpring, [0, 1], [0.88, 1])})`,
              flex: 1.4,
              maxWidth: "600px",
              minHeight: "380px",
              backgroundColor: tokens.bg.surface,
              borderRadius: tokens.radius.card,
              border: `2px solid rgba(16, 185, 129, 0.6)`,
              padding: "48px 44px",
              display: "flex",
              flexDirection: "column",
              justifyContent: "center",
              boxShadow: "0 25px 60px -15px rgba(16, 185, 129, 0.3), 0 20px 40px -15px rgba(0, 0, 0, 0.8)",
              position: "relative",
            }}
          >
            <div
              style={{
                fontSize: "19px",
                fontWeight: 700,
                textTransform: "uppercase",
                letterSpacing: "0.08em",
                color: tokens.accent.emerald,
                marginBottom: "16px",
              }}
            >
              {resultLabel || "ACCUMULATED WEALTH"}
            </div>
            <div
              style={{
                fontSize: "84px",
                fontWeight: 800,
                color: "#34d399",
                lineHeight: 1.02,
                marginBottom: note ? "18px" : "0",
              }}
            >
              {resultValue}
            </div>
            {note && (
              <div
                style={{
                  display: "inline-flex",
                  alignSelf: "flex-start",
                  padding: "8px 16px",
                  borderRadius: tokens.radius.chip,
                  backgroundColor: "rgba(16, 185, 129, 0.12)",
                  border: `1px solid rgba(16, 185, 129, 0.3)`,
                  color: tokens.accent.emerald,
                  fontSize: "16px",
                  fontWeight: 600,
                }}
              >
                {note}
              </div>
            )}
          </div>
        </div>
      </AbsoluteFill>
    );
  }

  // -------------------------------------------------------------------------
  // Treatment 6: NEUTRAL / FALLBACK TRANSFORMATION
  // -------------------------------------------------------------------------
  const inDelay = safeSpringDelay(8, duration_frames, 0.2);
  const inSpring = spring({
    frame: Math.max(0, frame - inDelay),
    fps,
    config: tokens.motion.reveal,
  });

  const [arrStart, arrEnd] = safeAnimationWindow(20, 44, duration_frames);
  const arrProgress = interpolate(
    frame,
    [arrStart, arrEnd],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  const outDelay = safeSpringDelay(36, duration_frames, 0.58);
  const outSpring = spring({
    frame: Math.max(0, frame - outDelay),
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
          gap: "40px",
          width: "100%",
          maxWidth: "1600px",
        }}
      >
        {/* Input Card */}
        <div
          style={{
            opacity: inSpring,
            transform: `translateX(${interpolate(inSpring, [0, 1], [-40, 0])}px)`,
            flex: 1,
            maxWidth: "460px",
            minHeight: "320px",
            backgroundColor: tokens.bg.cardLeft,
            borderRadius: tokens.radius.card,
            border: `1px solid ${tokens.bg.border}`,
            padding: "40px 38px",
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
            boxShadow: "0 20px 40px -15px rgba(0, 0, 0, 0.5)",
          }}
        >
          <div
            style={{
              fontSize: "18px",
              fontWeight: 600,
              textTransform: "uppercase",
              letterSpacing: "0.08em",
              color: tokens.text.secondary,
              marginBottom: "16px",
            }}
          >
            {inputLabel}
          </div>
          <div
            style={{
              fontSize: "52px",
              fontWeight: 800,
              color: tokens.text.primary,
              lineHeight: 1.1,
            }}
          >
            {inputValue}
          </div>
        </div>

        {/* Center Neutral Arrow (No invented operator symbol) */}
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            width: "180px",
          }}
        >
          <svg width="180" height="36" viewBox="0 0 180 36">
            <path
              d="M 0 18 L 170 18 M 155 10 L 170 18 L 155 26"
              stroke={tokens.accent.cyan}
              strokeWidth="3.5"
              fill="none"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeDasharray="200"
              strokeDashoffset={200 * (1 - arrProgress)}
            />
          </svg>
          {rateLabel && (
            <div
              style={{
                fontSize: "17px",
                fontWeight: 600,
                color: tokens.text.secondary,
                textAlign: "center",
                marginTop: "8px",
              }}
            >
              {rateLabel}
            </div>
          )}
        </div>

        {/* Result Card */}
        <div
          style={{
            opacity: outSpring,
            transform: `translateX(${interpolate(outSpring, [0, 1], [40, 0])}px)`,
            flex: 1.2,
            maxWidth: "560px",
            minHeight: "340px",
            backgroundColor: tokens.bg.surface,
            borderRadius: tokens.radius.card,
            border: `2px solid rgba(56, 189, 248, 0.4)`,
            padding: "44px 40px",
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
            boxShadow: "0 25px 60px -15px rgba(0, 0, 0, 0.7)",
          }}
        >
          <div
            style={{
              fontSize: "20px",
              fontWeight: 700,
              textTransform: "uppercase",
              letterSpacing: "0.08em",
              color: tokens.accent.cyan,
              marginBottom: "16px",
            }}
          >
            {resultLabel}
          </div>
          <div
            style={{
              fontSize: "68px",
              fontWeight: 800,
              color: tokens.text.primary,
              lineHeight: 1.05,
              marginBottom: note ? "18px" : "0",
            }}
          >
            {resultValue}
          </div>
          {note && (
            <div
              style={{
                fontSize: "18px",
                fontWeight: 500,
                color: tokens.text.secondary,
              }}
            >
              {note}
            </div>
          )}
        </div>
      </div>
    </AbsoluteFill>
  );
}
