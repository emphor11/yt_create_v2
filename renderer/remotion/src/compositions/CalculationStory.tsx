import React from 'react';
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { tokens } from '../design-tokens';
import { CalculationStoryProps } from '../types';
import { safeAnimationWindow, getCalculationPhases, CalculationPhases } from '../animation-safety';
export { getCalculationPhases };
export type { CalculationPhases };


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

  const headerLabel = resolvedProps.headerLabel || null;
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

  // Normalized, duration-aware phase keyframe coordinator
  const phases = getCalculationPhases(duration_frames);

  // -------------------------------------------------------------------------
  // Treatment 1: MULTIPLICATION (Base × Rate Modifier → Result)
  // -------------------------------------------------------------------------
  if (treatment === "multiplication") {
    // Phase 1: ESTABLISH (Input enters alone)
    const inputSpring = spring({
      frame: Math.max(0, frame - phases.inputDelay),
      fps,
      config: tokens.motion.reveal,
    });

    // Phase 2: BUILD (Rate / Driver enters)
    const driverSpring = spring({
      frame: Math.max(0, frame - phases.driverDelay),
      fps,
      config: tokens.motion.reveal,
    });

    // Phase 3: TRANSFORM (Operator badge pops in & vector arrow draws across)
    const opSpring = spring({
      frame: Math.max(0, frame - phases.operatorDelay),
      fps,
      config: tokens.motion.impact,
    });
    const arrowProgress = interpolate(
      frame,
      [phases.vectorStart, phases.vectorEnd],
      [0, 1],
      { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
    );
    const arrowOpacity = interpolate(arrowProgress, [0, 0.12], [0, 1], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });

    // Phase 4: PAYOFF (Result Card impacts in)
    const resultSpring = spring({
      frame: Math.max(0, frame - phases.resultDelay),
      fps,
      config: tokens.motion.impact,
    });

    // Phase 5: RESOLVE (Note pill settles in; full equation holds)
    const noteSpring = spring({
      frame: Math.max(0, frame - phases.noteDelay),
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
        {/* Optional Eyebrow Header */}
        {headerLabel && (
          <div
            style={{
              position: "absolute",
              top: "50px",
              left: "100px",
              display: "flex",
              alignItems: "center",
              gap: "10px",
              zIndex: 10,
            }}
          >
            <div
              style={{
                fontSize: "15px",
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
          {/* Phase 1: ESTABLISH - Base Input Card */}
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

          {/* Phases 2 & 3: BUILD & TRANSFORM - Multiplier Connector & Vector */}
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              width: "200px",
              position: "relative",
            }}
          >
            {/* Phase 3: Dynamic Vector Arrow */}
            <svg
              width="200"
              height="40"
              viewBox="0 0 200 40"
              style={{
                overflow: "visible",
                marginBottom: "8px",
                opacity: arrowOpacity,
              }}
            >
              <path
                d="M 0 20 L 190 20 M 175 10 L 190 20 L 175 30"
                stroke={tokens.accent.cyan}
                strokeWidth="3.5"
                fill="none"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeDasharray="220"
                strokeDashoffset={220 * (1 - arrowProgress)}
              />
            </svg>

            {/* Phase 3: Operator Badge */}
            <div
              style={{
                opacity: opSpring,
                transform: `scale(${interpolate(opSpring, [0, 1], [0.4, 1])})`,
                width: "68px",
                height: "68px",
                borderRadius: "50%",
                backgroundColor: "rgba(15, 23, 42, 0.95)",
                border: `2px solid ${tokens.accent.cyan}`,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: "36px",
                fontWeight: 800,
                color: tokens.accent.cyan,
                boxShadow: `0 0 24px rgba(6, 182, 212, 0.35)`,
                marginBottom: "12px",
              }}
            >
              {operationLabel || "×"}
            </div>

            {/* Phase 2: Rate Modifier Pill / Driver */}
            {rateLabel && (
              <div
                style={{
                  opacity: driverSpring,
                  transform: `translateY(${interpolate(driverSpring, [0, 1], [14, 0])}px) scale(${interpolate(driverSpring, [0, 1], [0.9, 1])})`,
                  fontSize: "17px",
                  fontWeight: 600,
                  color: tokens.accent.cyan,
                  backgroundColor: "rgba(6, 182, 212, 0.12)",
                  border: "1px solid rgba(6, 182, 212, 0.28)",
                  padding: "6px 14px",
                  borderRadius: tokens.radius.chip,
                  textAlign: "center",
                  lineHeight: 1.2,
                }}
              >
                {rateLabel}
              </div>
            )}
          </div>

          {/* Phase 4: PAYOFF - Dominant Result Card */}
          <div
            style={{
              opacity: resultSpring,
              transform: `translateX(${interpolate(resultSpring, [0, 1], [40, 0])}px) scale(${interpolate(resultSpring, [0, 1], [0.94, 1])})`,
              flex: 1.3,
              maxWidth: "580px",
              minHeight: "360px",
              backgroundColor: tokens.bg.surface,
              borderRadius: tokens.radius.card,
              border: `2px solid rgba(6, 182, 212, 0.55)`,
              padding: "44px 40px",
              display: "flex",
              flexDirection: "column",
              justifyContent: "center",
              boxShadow: "0 25px 60px -15px rgba(6, 182, 212, 0.25), 0 20px 40px -15px rgba(0, 0, 0, 0.7)",
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

            {/* Phase 5: RESOLVE - Contextual Note Badge */}
            {note && (
              <div
                style={{
                  opacity: noteSpring,
                  transform: `translateY(${interpolate(noteSpring, [0, 1], [8, 0])}px)`,
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
    // Phase 1: ESTABLISH (Card A enters alone)
    const cardASpring = spring({
      frame: Math.max(0, frame - phases.inputDelay),
      fps,
      config: tokens.motion.reveal,
    });

    // Phase 2: BUILD (Card B enters below Card A)
    const cardBSpring = spring({
      frame: Math.max(0, frame - phases.driverDelay),
      fps,
      config: tokens.motion.reveal,
    });

    // Phase 3: TRANSFORM (+ operator badge pops in & converging splines draw across)
    const opSpring = spring({
      frame: Math.max(0, frame - phases.operatorDelay),
      fps,
      config: tokens.motion.impact,
    });
    const splineProgress = interpolate(
      frame,
      [phases.vectorStart, phases.vectorEnd],
      [0, 1],
      { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
    );
    const splineOpacity = interpolate(splineProgress, [0, 0.12], [0, 1], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });

    // Phase 4: PAYOFF (Combined Sum Card reveals with emerald bloom)
    const sumSpring = spring({
      frame: Math.max(0, frame - phases.resultDelay),
      fps,
      config: tokens.motion.impact,
    });

    // Phase 5: RESOLVE (Explanatory Note settles in; hold for comprehension)
    const noteSpring = spring({
      frame: Math.max(0, frame - phases.noteDelay),
      fps,
      config: tokens.motion.gentle,
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
        {/* Optional Eyebrow Header */}
        {headerLabel && (
          <div
            style={{
              position: "absolute",
              top: "50px",
              left: "100px",
              display: "flex",
              alignItems: "center",
              gap: "10px",
              zIndex: 10,
            }}
          >
            <div
              style={{
                fontSize: "15px",
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
            {/* Phase 1: ESTABLISH - Input Card A */}
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

            {/* Phase 3: TRANSFORM - Centered Addition Badge */}
            <div
              style={{
                position: "absolute",
                left: "50%",
                top: "50%",
                transform: `translate(-50%, -50%) scale(${interpolate(opSpring, [0, 1], [0.4, 1])})`,
                opacity: opSpring,
                width: "42px",
                height: "42px",
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
                boxShadow: "0 0 20px rgba(16, 185, 129, 0.5)",
              }}
            >
              +
            </div>

            {/* Phase 2: BUILD - Input Card B */}
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

          {/* Phase 3: TRANSFORM - Converging Dual Splines */}
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
              style={{ overflow: "visible", opacity: splineOpacity }}
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
                opacity={splineProgress > 0.75 ? 1 : 0}
              />
            </svg>
          </div>

          {/* Phase 4: PAYOFF - Combined Sum Card */}
          <div
            style={{
              opacity: sumSpring,
              transform: `scale(${interpolate(sumSpring, [0, 1], [0.88, 1])})`,
              flex: 1.3,
              maxWidth: "580px",
              minHeight: "360px",
              backgroundColor: tokens.bg.surface,
              borderRadius: tokens.radius.card,
              border: `2px solid rgba(16, 185, 129, 0.65)`,
              padding: "44px 40px",
              display: "flex",
              flexDirection: "column",
              justifyContent: "center",
              boxShadow: "0 25px 60px -15px rgba(16, 185, 129, 0.28), 0 20px 40px -15px rgba(0, 0, 0, 0.7)",
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

            {/* Phase 5: RESOLVE - Explanatory Note */}
            {note && (
              <div
                style={{
                  opacity: noteSpring,
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
    // Phase 1: ESTABLISH (Gross Corpus enters alone)
    const grossSpring = spring({
      frame: Math.max(0, frame - phases.inputDelay),
      fps,
      config: tokens.motion.reveal,
    });

    // Phase 2: BUILD (Deduction component reveals with rose alert styling)
    const deductSpring = spring({
      frame: Math.max(0, frame - phases.driverDelay),
      fps,
      config: tokens.motion.impact,
    });

    // Phase 3: TRANSFORM (Subtraction vector arrow cuts across)
    const arrowProgress = interpolate(
      frame,
      [phases.vectorStart, phases.vectorEnd],
      [0, 1],
      { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
    );
    const arrowOpacity = interpolate(arrowProgress, [0, 0.12], [0, 1], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });

    // Phase 4: PAYOFF (Net Remaining Card reveals)
    const netSpring = spring({
      frame: Math.max(0, frame - phases.resultDelay),
      fps,
      config: tokens.motion.settle,
    });

    // Phase 5: RESOLVE (Takeaway Note settles in; hold for comprehension)
    const noteSpring = spring({
      frame: Math.max(0, frame - phases.noteDelay),
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
        {/* Optional Eyebrow Header */}
        {headerLabel && (
          <div
            style={{
              position: "absolute",
              top: "50px",
              left: "100px",
              display: "flex",
              alignItems: "center",
              gap: "10px",
              zIndex: 10,
            }}
          >
            <div
              style={{
                fontSize: "15px",
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
          {/* Phase 1: ESTABLISH - Starting Gross Corpus */}
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

          {/* Phase 2: BUILD - Deduction Component (Distinct Rose Alert) */}
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

          {/* Phase 3: TRANSFORM - Subtraction Vector Arrow */}
          <div style={{ width: "80px", display: "flex", alignItems: "center", justifyContent: "center" }}>
            <svg width="80" height="30" viewBox="0 0 80 30" style={{ opacity: arrowOpacity }}>
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

          {/* Phase 4: PAYOFF - Net Remaining Card */}
          <div
            style={{
              opacity: netSpring,
              transform: `translateX(${interpolate(netSpring, [0, 1], [40, 0])}px) scale(${interpolate(netSpring, [0, 1], [0.95, 1])})`,
              flex: 1.2,
              maxWidth: "520px",
              minHeight: "340px",
              backgroundColor: tokens.bg.surface,
              borderRadius: tokens.radius.card,
              border: `2px solid rgba(56, 189, 248, 0.45)`,
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

            {/* Phase 5: RESOLVE - Takeaway Note */}
            {note && (
              <div
                style={{
                  opacity: noteSpring,
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
    // Phase 1: ESTABLISH (Total Corpus Source Card enters alone)
    const totalSpring = spring({
      frame: Math.max(0, frame - phases.inputDelay),
      fps,
      config: tokens.motion.reveal,
    });

    const allocPercent = parsePercent(rateLabel || "40%");

    // Phase 2: BUILD (Allocation Chip reveals)
    const driverSpring = spring({
      frame: Math.max(0, frame - phases.driverDelay),
      fps,
      config: tokens.motion.reveal,
    });

    // Phase 3: TRANSFORM (Dynamic Bar Fill & Carve-Out Arrow)
    const barProgress = interpolate(
      frame,
      [phases.vectorStart, phases.vectorEnd],
      [0, 1],
      { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
    );
    const arrowProgress = interpolate(
      frame,
      [phases.vectorStart, phases.vectorEnd],
      [0, 1],
      { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
    );
    const arrowOpacity = interpolate(arrowProgress, [0, 0.12], [0, 1], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });

    // Phase 4: PAYOFF (Allocated Portion Result Card reveals)
    const allocSpring = spring({
      frame: Math.max(0, frame - phases.resultDelay),
      fps,
      config: tokens.motion.settle,
    });

    // Phase 5: RESOLVE (Allocation Note settles in; hold for comprehension)
    const noteSpring = spring({
      frame: Math.max(0, frame - phases.noteDelay),
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
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          padding: "60px 100px",
          overflow: "hidden",
        }}
      >
        {/* Optional Eyebrow Header */}
        {headerLabel && (
          <div
            style={{
              position: "absolute",
              top: "50px",
              left: "100px",
              display: "flex",
              alignItems: "center",
              gap: "10px",
              zIndex: 10,
            }}
          >
            <div
              style={{
                fontSize: "15px",
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
          {/* Phase 1: ESTABLISH - Total Corpus Source Card */}
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

          {/* Phases 2 & 3: BUILD & TRANSFORM - Proportional Carve-Out Bar */}
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              width: "380px",
            }}
          >
            {/* Phase 2: Allocation Percentage Chip */}
            <div
              style={{
                opacity: driverSpring,
                transform: `translateY(${interpolate(driverSpring, [0, 1], [14, 0])}px)`,
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

            {/* Phase 3: Dynamic Proportional Segment Bar */}
            <div
              style={{
                opacity: driverSpring,
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

            {/* Phase 3: Dynamic Carve-Out Arrow */}
            <svg width="240" height="24" viewBox="0 0 240 24" style={{ opacity: arrowOpacity }}>
              <path
                d="M 0 12 L 230 12 M 215 4 L 230 12 L 215 20"
                stroke={tokens.accent.cyan}
                strokeWidth="3"
                fill="none"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeDasharray="240"
                strokeDashoffset={240 * (1 - arrowProgress)}
              />
            </svg>
          </div>

          {/* Phase 4: PAYOFF - Allocated Portion Result Card */}
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

        {/* Phase 5: RESOLVE - Allocation Note */}
        {note && (
          <div
            style={{
              opacity: noteSpring,
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
    // Phase 1: ESTABLISH (Initial Principal Investment Card enters alone)
    const startSpring = spring({
      frame: Math.max(0, frame - phases.inputDelay),
      fps,
      config: tokens.motion.reveal,
    });

    // Phase 2: BUILD (Timeline Horizon Chip & Compounding Rate reveal)
    const driverSpring = spring({
      frame: Math.max(0, frame - phases.driverDelay),
      fps,
      config: tokens.motion.reveal,
    });

    // Phase 3: TRANSFORM (Compounding Trajectory Beam & Radiant Aura Expansion)
    const journeyProgress = interpolate(
      frame,
      [phases.vectorStart, phases.vectorEnd],
      [0, 1],
      { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
    );
    const journeyOpacity = interpolate(journeyProgress, [0, 0.12], [0, 1], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });

    const glowBloom = interpolate(
      frame,
      [phases.vectorStart, phases.resultDelay],
      [0.05, 0.28],
      { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
    );

    // Phase 4: PAYOFF (Future Expanded Result Card reveals with emerald bloom)
    const futureSpring = spring({
      frame: Math.max(0, frame - phases.resultDelay),
      fps,
      config: tokens.motion.impact,
    });

    // Phase 5: RESOLVE (Compounding Note settles in; hold for comprehension)
    const noteSpring = spring({
      frame: Math.max(0, frame - phases.noteDelay),
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
        {/* Optional Eyebrow Header */}
        {headerLabel && (
          <div
            style={{
              position: "absolute",
              top: "50px",
              left: "100px",
              display: "flex",
              alignItems: "center",
              gap: "10px",
              zIndex: 10,
            }}
          >
            <div
              style={{
                fontSize: "15px",
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

        {/* Phase 3 & 4: Future Growth Radiant Aura Bloom */}
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
          {/* Phase 1: ESTABLISH - Starting Corpus Card */}
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

          {/* Phases 2 & 3: BUILD & TRANSFORM - Growth Journey Vector */}
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              width: "240px",
            }}
          >
            {/* Phase 2: Timeline Horizon Chip */}
            <div
              style={{
                opacity: driverSpring,
                transform: `translateY(${interpolate(driverSpring, [0, 1], [14, 0])}px)`,
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

            {/* Phase 3: Gradient Vector Beam */}
            <svg
              width="240"
              height="36"
              viewBox="0 0 240 36"
              style={{ overflow: "visible", opacity: journeyOpacity }}
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

            {/* Phase 2: Compounding Rate / Driver Subtitle */}
            {rateLabel && (
              <div
                style={{
                  opacity: driverSpring,
                  transform: `translateY(${interpolate(driverSpring, [0, 1], [8, 0])}px)`,
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

          {/* Phase 4: PAYOFF - Future Expanded Result Card */}
          <div
            style={{
              opacity: futureSpring,
              transform: `scale(${interpolate(futureSpring, [0, 1], [0.88, 1])})`,
              flex: 1.4,
              maxWidth: "600px",
              minHeight: "380px",
              backgroundColor: tokens.bg.surface,
              borderRadius: tokens.radius.card,
              border: `2px solid rgba(16, 185, 129, 0.65)`,
              padding: "48px 44px",
              display: "flex",
              flexDirection: "column",
              justifyContent: "center",
              boxShadow: "0 25px 60px -15px rgba(16, 185, 129, 0.35), 0 20px 40px -15px rgba(0, 0, 0, 0.8)",
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

            {/* Phase 5: RESOLVE - Compounding Note Badge */}
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
  // Treatment 6: NEUTRAL / FALLBACK TRANSFORMATION
  // -------------------------------------------------------------------------
  // Phase 1: ESTABLISH (Input Card enters alone)
  const inSpring = spring({
    frame: Math.max(0, frame - phases.inputDelay),
    fps,
    config: tokens.motion.reveal,
  });

  // Phase 2: BUILD (Transition Subtitle / Driver reveals)
  const driverSpring = spring({
    frame: Math.max(0, frame - phases.driverDelay),
    fps,
    config: tokens.motion.reveal,
  });

  // Phase 3: TRANSFORM (Directional connection vector draws across)
  const arrProgress = interpolate(
    frame,
    [phases.vectorStart, phases.vectorEnd],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );
  const arrOpacity = interpolate(arrProgress, [0, 0.12], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Phase 4: PAYOFF (Destination Result Card arrives)
  const outSpring = spring({
    frame: Math.max(0, frame - phases.resultDelay),
    fps,
    config: tokens.motion.settle,
  });

  // Phase 5: RESOLVE (Note settles in; hold for comprehension)
  const noteSpring = spring({
    frame: Math.max(0, frame - phases.noteDelay),
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
      {/* Optional Eyebrow Header */}
      {headerLabel && (
        <div
          style={{
            position: "absolute",
            top: "50px",
            left: "100px",
            display: "flex",
            alignItems: "center",
            gap: "10px",
            zIndex: 10,
          }}
        >
          <div
            style={{
              fontSize: "15px",
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
        {/* Phase 1: ESTABLISH - Input Card */}
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

        {/* Phases 2 & 3: BUILD & TRANSFORM - Neutral Directional Arrow */}
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            width: "180px",
          }}
        >
          {/* Phase 3: Directional Vector Arrow */}
          <svg width="180" height="36" viewBox="0 0 180 36" style={{ opacity: arrOpacity }}>
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

          {/* Phase 2: Rate / Transition Driver Subtitle */}
          {rateLabel && (
            <div
              style={{
                opacity: driverSpring,
                transform: `translateY(${interpolate(driverSpring, [0, 1], [10, 0])}px)`,
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

        {/* Phase 4: PAYOFF - Result Card */}
        <div
          style={{
            opacity: outSpring,
            transform: `translateX(${interpolate(outSpring, [0, 1], [40, 0])}px)`,
            flex: 1.2,
            maxWidth: "560px",
            minHeight: "340px",
            backgroundColor: tokens.bg.surface,
            borderRadius: tokens.radius.card,
            border: `2px solid rgba(56, 189, 248, 0.45)`,
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

          {/* Phase 5: RESOLVE - Contextual Note */}
          {note && (
            <div
              style={{
                opacity: noteSpring,
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
