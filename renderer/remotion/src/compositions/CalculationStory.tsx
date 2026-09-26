import React from 'react';
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { tokens } from '../design-tokens';
import { CalculationStoryProps } from '../types';
import { safeAnimationWindow, safeSpringDelay, getCalculationPhases, CalculationPhases } from '../animation-safety';

export { getCalculationPhases };
export type { CalculationPhases };

// ---------------------------------------------------------------------------
// Dynamic Typography & Optical Currency Formatting
// ---------------------------------------------------------------------------

function getDynamicFontSize(valueStr: string, baseMax: number = 88, baseMin: number = 50): number {
  const len = (valueStr || "").trim().length;
  if (len <= 5) return baseMax;                     // e.g. "₹50k", "50%" (~88px)
  if (len <= 8) return Math.round(baseMax * 0.92);  // e.g. "₹50,000", "₹10 lakh" (~81px)
  if (len <= 12) return Math.round(baseMax * 0.82); // e.g. "₹1,00,000", "₹1.47 Crore" (~72px)
  if (len <= 16) return Math.round(baseMax * 0.72); // e.g. "₹1,00,00,000" (~63px)
  return Math.max(baseMin, Math.round(baseMax * 0.60));
}

function renderFormattedValue(value: string, fontSize: number, color: string) {
  const trimmed = (value || "0").trim();
  const currencyMatch = trimmed.match(/^([₹$€£¥])\s*(.*)$/);
  if (currencyMatch) {
    const symbol = currencyMatch[1];
    const rest = currencyMatch[2];
    return (
      <span
        style={{
          fontFamily: tokens.font.family,
          fontSize: `${fontSize}px`,
          fontVariantNumeric: "tabular-nums lining-nums",
          letterSpacing: "-0.035em",
          color,
          display: "inline-flex",
          alignItems: "baseline",
        }}
      >
        <span
          style={{
            fontSize: `${Math.round(fontSize * 0.78)}px`,
            opacity: 0.84,
            marginRight: "6px",
            fontWeight: 700,
          }}
        >
          {symbol}
        </span>
        <span style={{ fontSize: `${fontSize}px`, fontWeight: 800 }}>{rest}</span>
      </span>
    );
  }

  return (
    <span
      style={{
        fontFamily: tokens.font.family,
        fontSize: `${fontSize}px`,
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

function renderRateContent(rateLabel: string, accentColor: string, isNegative: boolean) {
  const trimmed = (rateLabel || "").trim();
  // Match prefix rates like "50% Target Savings Rate" or "12% Compounding CAGR"
  const match = trimmed.match(/^([+-]?\d+(?:\.\d+)?%|[+-]?\d+(?:\.\d+)?x|\d+\s*Years?)\s*(.*)$/i);
  if (match) {
    const rateVal = match[1];
    const rateDesc = match[2];
    return (
      <div style={{ display: "flex", flexDirection: "column", gap: "2px" }}>
        <div
          style={{
            fontSize: "28px",
            fontWeight: 800,
            letterSpacing: "-0.02em",
            fontVariantNumeric: "tabular-nums lining-nums",
            color: accentColor,
            lineHeight: 1.1,
          }}
        >
          {rateVal}
        </div>
        {rateDesc && (
          <div
            style={{
              fontSize: "14px",
              fontWeight: 500,
              color: "#94a3b8",
              lineHeight: 1.25,
              maxWidth: "260px",
            }}
          >
            {rateDesc}
          </div>
        )}
      </div>
    );
  }

  return (
    <div
      style={{
        fontSize: "18px",
        fontWeight: 700,
        letterSpacing: "-0.01em",
        color: accentColor,
        lineHeight: 1.25,
        maxWidth: "260px",
      }}
    >
      {trimmed}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Atmospheric Editorial Backdrop (Zero Dashboard Clutter)
// ---------------------------------------------------------------------------

interface EditorialBackdropProps {
  accentRgb: string;
}

function EditorialBackdrop({ accentRgb }: EditorialBackdropProps) {
  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#060911",
        overflow: "hidden",
        pointerEvents: "none",
      }}
    >
      {/* Editorial Vignette & Asymmetric Radial Glow centered behind the Result */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: `
            radial-gradient(circle at 76% 50%, rgba(${accentRgb}, 0.16) 0%, rgba(${accentRgb}, 0.05) 42%, transparent 72%),
            radial-gradient(circle at 20% 50%, rgba(255, 255, 255, 0.02) 0%, transparent 60%),
            radial-gradient(ellipse at 50% 50%, transparent 40%, rgba(3, 5, 10, 0.75) 100%)
          `,
        }}
      />

      {/* Subtle Precision Technical Grid Pattern */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          opacity: 0.035,
          backgroundImage: `
            linear-gradient(to right, rgba(255, 255, 255, 0.15) 1px, transparent 1px),
            linear-gradient(to bottom, rgba(255, 255, 255, 0.15) 1px, transparent 1px)
          `,
          backgroundSize: "64px 64px",
        }}
      />

      {/* Top and Bottom Datum Hairline Guides */}
      <div
        style={{
          position: "absolute",
          top: "84px",
          left: "120px",
          right: "120px",
          height: "1px",
          background: "linear-gradient(90deg, transparent 0%, rgba(255, 255, 255, 0.06) 15%, rgba(255, 255, 255, 0.06) 85%, transparent 100%)",
        }}
      />
      <div
        style={{
          position: "absolute",
          bottom: "84px",
          left: "120px",
          right: "120px",
          height: "1px",
          background: "linear-gradient(90deg, transparent 0%, rgba(255, 255, 255, 0.05) 15%, rgba(255, 255, 255, 0.05) 85%, transparent 100%)",
        }}
      />
    </AbsoluteFill>
  );
}

// ---------------------------------------------------------------------------
// Main CalculationStory Component
// ---------------------------------------------------------------------------

export function CalculationStory(props: CalculationStoryProps | any) {
  const frame = useCurrentFrame();
  const videoConfig = useVideoConfig();

  // Robust prop unwrapping supporting VideoAssembly wrapper and direct calls
  const resolvedProps: CalculationStoryProps = (props as any)?.props || props || {};
  const duration_frames = (props as any)?.duration_frames || (props as any)?.durationInFrames || videoConfig?.durationInFrames || 180;
  const fps = (props as any)?.fps || videoConfig?.fps || 30;

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

  // Derive explicit semantic operation type
  const explicitType: string =
    resolvedProps.operationType ||
    resolvedProps.variant ||
    (operationLabel === "+" ? "addition" :
     operationLabel === "−" || operationLabel === "-" ? "subtraction" :
     operationLabel === "×" || operationLabel === "*" ? "multiplication" :
     operationLabel === "→" ? "growth" :
     operationLabel.includes("%") ? "allocation" : "growth");

  // Determine standard mathematical operator glyph
  let operatorSymbol = operationLabel ? operationLabel.trim() : "";
  if (!operatorSymbol) {
    if (explicitType === "addition") operatorSymbol = "+";
    else if (explicitType === "subtraction") operatorSymbol = "−";
    else if (explicitType === "multiplication") operatorSymbol = "×";
    else if (explicitType === "growth") operatorSymbol = "→";
    else if (explicitType === "allocation") operatorSymbol = "%";
    else operatorSymbol = "→";
  } else if (operatorSymbol === "-") {
    operatorSymbol = "−";
  } else if (operatorSymbol === "*") {
    operatorSymbol = "×";
  }

  // Determine color staging based on polarity / arithmetic nature
  const isNegative = polarity === "negative" || explicitType === "subtraction";
  const isPositive = polarity === "positive";
  const isWarning = polarity === "warning";

  let accentColor = tokens.accent.cyan || "#38bdf8";
  let accentRgb = "56, 189, 248";
  if (isPositive) {
    accentColor = tokens.accent.emerald || "#10b981";
    accentRgb = "16, 185, 129";
  } else if (isNegative) {
    accentColor = tokens.accent.rose || "#f43f5e";
    accentRgb = "244, 63, 94";
  } else if (isWarning) {
    accentColor = tokens.accent.amber || "#f59e0b";
    accentRgb = "245, 158, 11";
  }

  const resultTextColor = isPositive ? "#34d399" : isNegative ? "#fb7185" : "#ffffff";

  // -------------------------------------------------------------------------
  // Duration-Adaptive Choreography Windows
  // -------------------------------------------------------------------------

  // Scene entrance fade (frames 0..8)
  const sceneOpacity = interpolate(
    frame,
    [0, Math.min(8, Math.max(1, duration_frames - 1))],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // Sub-threshold camera motion: subtle atmospheric zoom (1.000 -> 1.006)
  const cameraScale = interpolate(
    frame,
    [0, Math.max(1, duration_frames)],
    [1.000, 1.006],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // Keyframe phase coordinator guaranteed duration-safe
  const phases = getCalculationPhases(duration_frames);

  // Phase 1: Establish Input (Input reveals on left)
  const inputSpring = spring({
    frame: Math.max(0, frame - phases.inputDelay),
    fps,
    config: tokens.motion.reveal,
  });
  const inputX = interpolate(inputSpring, [0, 1], [-32, 0]);

  // Phase 2: Introduce Operation (Operator token scales in)
  const opSpring = spring({
    frame: Math.max(0, frame - phases.operatorDelay),
    fps,
    config: tokens.motion.impact,
  });
  const opScale = interpolate(opSpring, [0, 1], [0.4, 1]);

  // Phase 3: Factor / Rate reveals
  const driverSpring = spring({
    frame: Math.max(0, frame - phases.driverDelay),
    fps,
    config: tokens.motion.reveal,
  });
  const driverY = interpolate(driverSpring, [0, 1], [16, 0]);

  // Phase 4: Vector conduit draws across
  const arrowProgress = interpolate(
    frame,
    [phases.vectorStart, phases.vectorEnd],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // Pulse along the conduit
  const pulseOpacity = interpolate(
    arrowProgress,
    [0, 0.15, 0.85, 1],
    [0, 0.9, 0.9, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // Phase 5: Payoff / Result reveal (Climax moment)
  const resultSpring = spring({
    frame: Math.max(0, frame - phases.resultDelay),
    fps,
    config: tokens.motion.impact,
  });
  const resultX = interpolate(resultSpring, [0, 1], [32, 0]);
  const resultScale = interpolate(resultSpring, [0, 1], [0.95, 1]);

  // Phase 6: Note & context settle
  const noteSpring = spring({
    frame: Math.max(0, frame - phases.noteDelay),
    fps,
    config: tokens.motion.gentle,
  });
  const noteY = interpolate(noteSpring, [0, 1], [10, 0]);

  // Dynamic font sizing
  const hasSecondaryOperand = Boolean(secondaryValue);
  const inputFontSize = getDynamicFontSize(inputValue, hasSecondaryOperand ? 68 : 80, 48);
  const secondaryFontSize = hasSecondaryOperand ? getDynamicFontSize(secondaryValue || "", 54, 40) : 44;
  const resultFontSize = getDynamicFontSize(resultValue, hasSecondaryOperand ? 88 : 104, 60);

  return (
    <AbsoluteFill
      style={{
        fontFamily: tokens.font.family,
        opacity: sceneOpacity,
        transform: `scale(${cameraScale})`,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "0 120px",
        overflow: "hidden",
      }}
    >
      <EditorialBackdrop accentRgb={accentRgb} />

      {/* Top Editorial Eyebrow / Scene Header */}
      <div
        style={{
          position: "absolute",
          top: "84px",
          left: "120px",
          right: "120px",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          zIndex: 10,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <div
            style={{
              width: "7px",
              height: "7px",
              borderRadius: "50%",
              backgroundColor: accentColor,
              boxShadow: `0 0 8px ${accentColor}`,
            }}
          />
          <div
            style={{
              fontSize: "14px",
              fontWeight: 700,
              textTransform: "uppercase",
              letterSpacing: "0.14em",
              color: "#94a3b8",
            }}
          >
            {headerLabel || "FINANCIAL CALCULATION"}
          </div>
        </div>

        {timeframe && (
          <div
            style={{
              fontSize: "13px",
              fontWeight: 700,
              textTransform: "uppercase",
              letterSpacing: "0.12em",
              color: "#94a3b8",
              backgroundColor: "rgba(255, 255, 255, 0.04)",
              border: "1px solid rgba(255, 255, 255, 0.08)",
              padding: "4px 12px",
              borderRadius: tokens.radius.chip,
            }}
          >
            HORIZON: <span style={{ color: "#f8fafc" }}>{timeframe}</span>
          </div>
        )}
      </div>

      {/* Main Calculation Stage (Expansive Horizontal Equation Flow) */}
      <div
        style={{
          position: "relative",
          zIndex: 2,
          display: "flex",
          flexDirection: "row",
          alignItems: "center",
          justifyContent: "space-between",
          width: "100%",
          maxWidth: "1680px",
          minHeight: "360px",
        }}
      >
        {/* ================================================================ */}
        {/* STAGE 1: Left Input Anchor                                      */}
        {/* ================================================================ */}
        <div
          style={{
            flex: "1",
            maxWidth: hasSecondaryOperand ? "400px" : "460px",
            opacity: inputSpring,
            transform: `translateX(${inputX}px)`,
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
          }}
        >
          {/* Eyebrow Label */}
          <div
            style={{
              fontSize: "13px",
              fontWeight: 700,
              textTransform: "uppercase",
              letterSpacing: "0.14em",
              color: "#64748b",
              marginBottom: "12px",
              display: "flex",
              alignItems: "center",
              gap: "8px",
            }}
          >
            <span style={{ width: "6px", height: "6px", borderRadius: "50%", backgroundColor: "#64748b" }} />
            BASE INPUT
          </div>

          {/* Hero Value */}
          <div style={{ lineHeight: 1.05, marginBottom: "14px" }}>
            {renderFormattedValue(inputValue, inputFontSize, "#f8fafc")}
          </div>

          {/* Subtitle / Semantic Role */}
          <div
            style={{
              fontSize: "19px",
              fontWeight: 500,
              color: "#94a3b8",
              lineHeight: 1.35,
              maxWidth: "380px",
            }}
          >
            {inputLabel}
          </div>
        </div>

        {/* ================================================================ */}
        {/* STAGE 2: Transformation Conduit & Operations                    */}
        {/* ================================================================ */}
        <div
          style={{
            flex: hasSecondaryOperand ? "1.6" : "1.4",
            display: "flex",
            flexDirection: "row",
            alignItems: "center",
            justifyContent: "center",
            position: "relative",
            padding: "0 28px",
            gap: "20px",
          }}
        >
          {/* Connecting Kinetic Vector Line (Drawn behind the opaque nodes) */}
          <svg
            style={{
              position: "absolute",
              left: 0,
              right: 0,
              top: "50%",
              transform: "translateY(-50%)",
              width: "100%",
              height: "40px",
              pointerEvents: "none",
              zIndex: 1,
              overflow: "visible",
            }}
          >
            {/* Subtle Datum Guideline */}
            <line
              x1="0"
              y1="20"
              x2="100%"
              y2="20"
              stroke="rgba(255, 255, 255, 0.07)"
              strokeWidth="1.5"
              strokeDasharray="4 4"
            />
            {/* Active Drawing Conduit */}
            <line
              x1="0"
              y1="20"
              x2={`${Math.round(arrowProgress * 100)}%`}
              y2="20"
              stroke={accentColor}
              strokeWidth="2.5"
              strokeLinecap="round"
            />
            {/* Traveling Pulse Bead */}
            {arrowProgress > 0 && arrowProgress < 1 && (
              <circle
                cx={`${Math.round(arrowProgress * 100)}%`}
                cy="20"
                r="4"
                fill="#ffffff"
                opacity={pulseOpacity}
                filter={`drop-shadow(0 0 6px ${accentColor})`}
              />
            )}
          </svg>

          {/* Operator Token Badge */}
          <div
            style={{
              position: "relative",
              zIndex: 3,
              opacity: opSpring,
              transform: `scale(${opScale})`,
              width: "58px",
              height: "58px",
              borderRadius: "50%",
              backgroundColor: "#080d1a",
              border: `2px solid ${accentColor}`,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: "28px",
              fontWeight: 800,
              color: accentColor,
              boxShadow: `0 0 24px rgba(${accentRgb}, 0.35), 0 4px 16px rgba(0, 0, 0, 0.5)`,
              flexShrink: 0,
            }}
          >
            {operatorSymbol}
          </div>

          {/* Case A: Secondary Numerical Operand Plaque (e.g. Addition / Subtraction) */}
          {hasSecondaryOperand && (
            <div
              style={{
                position: "relative",
                zIndex: 3,
                opacity: driverSpring,
                transform: `translateY(${driverY}px)`,
                backgroundColor: "#090e1c",
                border: `1px solid ${isNegative ? "rgba(244, 63, 94, 0.35)" : "rgba(" + accentRgb + ", 0.35)"}`,
                borderRadius: "16px",
                padding: "16px 22px",
                boxShadow: "0 10px 30px rgba(0, 0, 0, 0.5)",
                display: "flex",
                flexDirection: "column",
                gap: "4px",
                minWidth: "220px",
                maxWidth: "280px",
              }}
            >
              <div
                style={{
                  fontSize: "12px",
                  fontWeight: 700,
                  textTransform: "uppercase",
                  letterSpacing: "0.12em",
                  color: isNegative ? "#f43f5e" : accentColor,
                  display: "flex",
                  alignItems: "center",
                  gap: "6px",
                }}
              >
                <span style={{ width: "5px", height: "5px", borderRadius: "50%", backgroundColor: isNegative ? "#f43f5e" : accentColor }} />
                {isNegative ? "DEDUCTION" : "FACTOR"}
              </div>
              <div style={{ lineHeight: 1.05 }}>
                {renderFormattedValue(secondaryValue || "0", secondaryFontSize, isNegative ? "#fb7185" : "#f8fafc")}
              </div>
              {secondaryLabel && (
                <div
                  style={{
                    fontSize: "14px",
                    fontWeight: 500,
                    color: "#94a3b8",
                    lineHeight: 1.3,
                  }}
                >
                  {secondaryLabel}
                </div>
              )}
              {rateLabel && (
                <div
                  style={{
                    marginTop: "4px",
                    fontSize: "12px",
                    fontWeight: 600,
                    color: isNegative ? "#f87171" : accentColor,
                    backgroundColor: isNegative ? "rgba(244, 63, 94, 0.12)" : `rgba(${accentRgb}, 0.12)`,
                    padding: "3px 8px",
                    borderRadius: "6px",
                    alignSelf: "flex-start",
                  }}
                >
                  {rateLabel}
                </div>
              )}
            </div>
          )}

          {/* Case B: Single Operand Rate / Driver Capsule */}
          {!hasSecondaryOperand && rateLabel && (
            <div
              style={{
                position: "relative",
                zIndex: 3,
                opacity: driverSpring,
                transform: `translateY(${driverY}px)`,
                backgroundColor: "#090e1c",
                border: `1px solid rgba(${accentRgb}, 0.35)`,
                borderRadius: "16px",
                padding: "16px 24px",
                boxShadow: `0 10px 30px rgba(0, 0, 0, 0.5), 0 0 20px rgba(${accentRgb}, 0.12)`,
                display: "flex",
                flexDirection: "column",
                gap: "4px",
                minWidth: "180px",
                maxWidth: "320px",
              }}
            >
              <div
                style={{
                  fontSize: "11px",
                  fontWeight: 700,
                  textTransform: "uppercase",
                  letterSpacing: "0.14em",
                  color: accentColor,
                  display: "flex",
                  alignItems: "center",
                  gap: "6px",
                }}
              >
                <span style={{ width: "5px", height: "5px", borderRadius: "50%", backgroundColor: accentColor }} />
                {explicitType === "allocation" ? "ALLOCATION" : explicitType === "growth" ? "COMPOUNDING RATE" : "RATE / FACTOR"}
              </div>
              {renderRateContent(rateLabel, accentColor, isNegative)}
            </div>
          )}

          {/* Transformation Arrow into Result */}
          <div
            style={{
              position: "relative",
              zIndex: 2,
              opacity: interpolate(arrowProgress, [0.75, 1], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
              fontSize: "26px",
              fontWeight: 700,
              color: accentColor,
              flexShrink: 0,
            }}
          >
            →
          </div>
        </div>

        {/* ================================================================ */}
        {/* STAGE 3: Final Result (Visual Climax)                            */}
        {/* ================================================================ */}
        <div
          style={{
            flex: "1.3",
            maxWidth: "560px",
            opacity: resultSpring,
            transform: `translateX(${resultX}px) scale(${resultScale})`,
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
            paddingLeft: "48px",
            position: "relative",
          }}
        >
          {/* Vertical Datum Accent Guideline */}
          <div
            style={{
              position: "absolute",
              left: 0,
              top: "5%",
              bottom: "5%",
              width: "3px",
              background: `linear-gradient(180deg, transparent 0%, ${accentColor} 30%, ${accentColor} 70%, transparent 100%)`,
              borderRadius: "2px",
              boxShadow: `0 0 16px rgba(${accentRgb}, 0.55)`,
            }}
          />

          {/* Eyebrow Label */}
          <div
            style={{
              fontSize: "14px",
              fontWeight: 700,
              textTransform: "uppercase",
              letterSpacing: "0.14em",
              color: accentColor,
              marginBottom: "12px",
              display: "flex",
              alignItems: "center",
              gap: "8px",
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
            {resultLabel.toUpperCase() || "FINAL RESULT"}
          </div>

          {/* Climax Hero Value */}
          <div
            style={{
              lineHeight: 1.02,
              marginBottom: "14px",
              filter: `drop-shadow(0 0 35px rgba(${accentRgb}, 0.35))`,
            }}
          >
            {renderFormattedValue(resultValue, resultFontSize, resultTextColor)}
          </div>

          {/* Subtitle */}
          <div
            style={{
              fontSize: "20px",
              fontWeight: 500,
              color: "#cbd5e1",
              lineHeight: 1.35,
              marginBottom: note ? "18px" : "0",
            }}
          >
            {resultLabel}
          </div>

          {/* Optional Contextual Note Pill */}
          {note && (
            <div
              style={{
                opacity: noteSpring,
                transform: `translateY(${noteY}px)`,
                display: "inline-flex",
                alignItems: "center",
                gap: "8px",
                alignSelf: "flex-start",
                padding: "8px 18px",
                borderRadius: tokens.radius.chip,
                backgroundColor: "rgba(255, 255, 255, 0.04)",
                border: "1px solid rgba(255, 255, 255, 0.12)",
                color: "#e2e8f0",
                fontSize: "14px",
                fontWeight: 600,
                letterSpacing: "0.03em",
                lineHeight: 1.2,
                boxShadow: "0 4px 16px rgba(0, 0, 0, 0.35)",
              }}
            >
              <span style={{ color: accentColor, fontSize: "15px" }}>✦</span>
              <span>{note}</span>
            </div>
          )}
        </div>
      </div>
    </AbsoluteFill>
  );
}
