import React from "react";
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { type SplitComparisonProps, type ComparisonSplitProps } from "./types";
import { tokens } from "./design-tokens";
import { safeAnimationWindow, safeSpringDelay } from "./animation-safety";

export type { SplitComparisonProps, ComparisonSplitProps };

// ---------------------------------------------------------------------------
// Dynamic Typography & Optical Value Formatting
// ---------------------------------------------------------------------------

interface FormattedValueParts {
  formatted: string;
  prefix: string;
  numberPart: string;
  suffix: string;
}

function getDynamicFontSize(valueStr: string, baseMax: number = 88, baseMin: number = 52): number {
  const len = (valueStr || "").trim().length;
  if (len <= 4) return baseMax;                     // e.g. "1×", "2×", "12%" (~88px)
  if (len <= 7) return Math.round(baseMax * 0.92);  // e.g. "6.5%", "$40k" (~81px)
  if (len <= 11) return Math.round(baseMax * 0.82); // e.g. "₹80,000", "10 YEARS" (~72px)
  if (len <= 15) return Math.round(baseMax * 0.70); // e.g. "₹1,50,000" (~62px)
  return Math.max(baseMin, Math.round(baseMax * 0.58));
}

function formatValue(rawVal: string | number | undefined, progress: number, unit?: string): FormattedValueParts {
  const unitSuffix = unit ? ` ${unit}` : "";
  if (rawVal === undefined || rawVal === null || rawVal === "") {
    return { formatted: "", prefix: "", numberPart: "", suffix: unitSuffix };
  }

  if (typeof rawVal === "number") {
    const isFloat = rawVal % 1 !== 0;
    // Don't roll up small integers from 0 (e.g. 1 or 2)
    const current = (rawVal <= 5 && !isFloat) ? rawVal : progress * rawVal;
    const formattedNum = isFloat ? current.toFixed(1) : Math.round(current).toString();
    return {
      formatted: `${formattedNum}${unitSuffix}`,
      prefix: "",
      numberPart: formattedNum,
      suffix: unitSuffix,
    };
  }

  const str = String(rawVal).trim();
  const match = str.match(/^([^\d\.-]*)([\d,]+(?:\.\d+)?)(.*)$/);
  if (!match) {
    return {
      formatted: `${str}${unitSuffix}`,
      prefix: "",
      numberPart: str,
      suffix: unitSuffix,
    };
  }

  const prefix = match[1] || "";
  const numStr = match[2].replace(/,/g, "");
  const suffix = (match[3] || "") + unitSuffix;
  const targetNum = parseFloat(numStr);

  if (isNaN(targetNum)) {
    return {
      formatted: `${str}${unitSuffix}`,
      prefix: "",
      numberPart: str,
      suffix: unitSuffix,
    };
  }

  const isFloat = numStr.includes(".");
  // For small multiplier integers like 1 or 2 (e.g. "1×", "2×"), avoid awkward 0x display
  const isSmallInt = targetNum <= 5 && !isFloat;
  const currentNum = isSmallInt ? targetNum : progress * targetNum;
  const decimalPlaces = isFloat ? (numStr.split(".")[1]?.length || 1) : 0;
  const formattedNum = decimalPlaces > 0 ? currentNum.toFixed(decimalPlaces) : Math.round(currentNum).toLocaleString();

  return {
    formatted: `${prefix}${formattedNum}${suffix}`,
    prefix,
    numberPart: formattedNum,
    suffix,
  };
}

function renderValue(
  valueObj: FormattedValueParts,
  fontSize: number,
  textColor: string,
  isWinner: boolean,
  accentColor: string,
  accentRgb: string
) {
  const { prefix, numberPart, suffix, formatted } = valueObj;

  if (!numberPart) {
    return (
      <span
        style={{
          fontFamily: tokens.font.family,
          fontSize: `${fontSize}px`,
          fontWeight: 800,
          color: textColor,
          letterSpacing: "-0.03em",
          lineHeight: 1,
          filter: isWinner ? `drop-shadow(0 0 30px rgba(${accentRgb}, 0.35))` : "none",
        }}
      >
        {formatted}
      </span>
    );
  }

  const isMathSuffix = suffix.includes("%") || suffix.includes("×") || suffix.includes("x");

  return (
    <span
      style={{
        fontFamily: tokens.font.family,
        fontSize: `${fontSize}px`,
        fontVariantNumeric: "tabular-nums lining-nums",
        letterSpacing: "-0.035em",
        color: textColor,
        display: "inline-flex",
        alignItems: "baseline",
        lineHeight: 1,
        filter: isWinner ? `drop-shadow(0 0 35px rgba(${accentRgb}, 0.40))` : "none",
      }}
    >
      {prefix && (
        <span
          style={{
            fontSize: `${Math.round(fontSize * 0.78)}px`,
            opacity: 0.84,
            marginRight: "4px",
            fontWeight: 700,
          }}
        >
          {prefix}
        </span>
      )}
      <span style={{ fontSize: `${fontSize}px`, fontWeight: 800 }}>{numberPart}</span>
      {suffix && (
        <span
          style={{
            fontSize: isMathSuffix ? `${Math.round(fontSize * 0.80)}px` : `${Math.round(fontSize * 0.45)}px`,
            opacity: 0.84,
            marginLeft: isMathSuffix ? "3px" : "8px",
            fontWeight: 700,
          }}
        >
          {suffix}
        </span>
      )}
    </span>
  );
}

// ---------------------------------------------------------------------------
// Atmospheric Editorial Backdrop
// ---------------------------------------------------------------------------

interface EditorialBackdropProps {
  hasWinner: boolean;
  isLeftWinner: boolean;
  isRightWinner: boolean;
  winnerRgb: string;
  glowOpacity: number;
}

function EditorialBackdrop({ hasWinner, isLeftWinner, isRightWinner, winnerRgb, glowOpacity }: EditorialBackdropProps) {
  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#060911",
        overflow: "hidden",
        pointerEvents: "none",
      }}
    >
      {/* Asymmetric Radial Glow centered behind the Winner territory */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          opacity: glowOpacity,
          background: hasWinner
            ? `
              radial-gradient(circle at ${isLeftWinner ? "26%" : "74%"} 50%, rgba(${winnerRgb}, 0.16) 0%, rgba(${winnerRgb}, 0.05) 45%, transparent 72%),
              radial-gradient(circle at ${isLeftWinner ? "74%" : "26%"} 50%, rgba(255, 255, 255, 0.015) 0%, transparent 55%),
              radial-gradient(ellipse at 50% 50%, transparent 40%, rgba(3, 5, 10, 0.8) 100%)
            `
            : `
              radial-gradient(circle at 50% 50%, rgba(56, 189, 248, 0.08) 0%, rgba(56, 189, 248, 0.02) 50%, transparent 75%),
              radial-gradient(ellipse at 50% 50%, transparent 40%, rgba(3, 5, 10, 0.8) 100%)
            `,
        }}
      />

      {/* Precision Technical Datum Grid Pattern */}
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
// Main SplitComparison / ComparisonSplit Component
// ---------------------------------------------------------------------------

export function SplitComparison(props: SplitComparisonProps | any) {
  const frame = useCurrentFrame();
  const videoConfig = useVideoConfig();
  const fps = videoConfig?.fps || 30;

  // Normalize boundary props wrapper
  const resolvedProps: SplitComparisonProps = props.props ? props.props : props;
  const duration_frames = (props as any).duration_frames || (props as any).durationInFrames || videoConfig?.durationInFrames || 180;
  const frame_spans = (props as any).frame_spans || [];

  const headerLabel = resolvedProps.headerLabel || "";
  const rawCompLabel = (resolvedProps as any).comparison_label || resolvedProps.comparisonLabel || "";
  // Disambiguate so we don't duplicate identical text in both eyebrow and subtitle
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
  let leftColor = tokens.accent.cyan || "#38bdf8";
  let leftRgb = "56, 189, 248";
  let rightColor = tokens.accent.cyan || "#38bdf8";
  let rightRgb = "56, 189, 248";
  let deltaColor = tokens.accent.emerald || "#10b981";
  let deltaRgb = "16, 185, 129";

  if (tone === "positive_negative") {
    leftColor = isLeftWinner ? (tokens.accent.emerald || "#10b981") : (tokens.accent.rose || "#f43f5e");
    leftRgb = isLeftWinner ? "16, 185, 129" : "244, 63, 94";
    rightColor = isRightWinner ? (tokens.accent.emerald || "#10b981") : (tokens.accent.rose || "#f43f5e");
    rightRgb = isRightWinner ? "16, 185, 129" : "244, 63, 94";
    deltaColor = hasWinner ? (tokens.accent.emerald || "#10b981") : (tokens.accent.cyan || "#38bdf8");
    deltaRgb = hasWinner ? "16, 185, 129" : "56, 189, 248";
  } else if (tone === "before_after") {
    leftColor = tokens.accent.amber || "#f59e0b";     // Before Baseline
    leftRgb = "245, 158, 11";
    rightColor = tokens.accent.emerald || "#10b981";  // After Strategy
    rightRgb = "16, 185, 129";
    deltaColor = tokens.accent.emerald || "#10b981";
    deltaRgb = "16, 185, 129";
  } else if (tone === "superiority") {
    leftColor = isLeftWinner ? (tokens.accent.emerald || "#10b981") : "#94a3b8";
    leftRgb = isLeftWinner ? "16, 185, 129" : "148, 163, 184";
    rightColor = isRightWinner ? (tokens.accent.emerald || "#10b981") : "#94a3b8";
    rightRgb = isRightWinner ? "16, 185, 129" : "148, 163, 184";
    deltaColor = tokens.accent.emerald || "#10b981";
    deltaRgb = "16, 185, 129";
  } else {
    if (isLeftWinner) {
      leftColor = tokens.accent.emerald || "#10b981";
      leftRgb = "16, 185, 129";
      rightColor = "#94a3b8";
      rightRgb = "148, 163, 184";
      deltaColor = leftColor;
      deltaRgb = leftRgb;
    } else if (isRightWinner) {
      rightColor = tokens.accent.emerald || "#10b981";
      rightRgb = "16, 185, 129";
      leftColor = "#94a3b8";
      leftRgb = "148, 163, 184";
      deltaColor = rightColor;
      deltaRgb = rightRgb;
    } else {
      leftColor = tokens.accent.cyan || "#38bdf8";
      leftRgb = "56, 189, 248";
      rightColor = tokens.accent.cyan || "#38bdf8";
      rightRgb = "56, 189, 248";
      deltaColor = tokens.accent.emerald || "#10b981";
      deltaRgb = "16, 185, 129";
    }
  }

  const winnerRgb = isLeftWinner ? leftRgb : rightRgb;

  // -------------------------------------------------------------------------
  // Staged Duration-Aware Choreography
  // -------------------------------------------------------------------------

  // Scene entrance fade (frames 0..8)
  const sceneOpacity = interpolate(
    frame,
    [0, Math.min(8, Math.max(1, duration_frames - 1))],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // Sub-threshold camera motion (1.000 -> 1.006)
  const cameraScale = interpolate(
    frame,
    [0, Math.max(1, duration_frames)],
    [1.000, 1.006],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // Phase 1: Header / Context entrance
  const headerDelay = safeSpringDelay(0, duration_frames, 0.15);
  const headerSpring = spring({
    frame: Math.max(0, frame - headerDelay),
    fps,
    config: tokens.motion.reveal,
  });

  // Phase 2: Option A (Left territory) entrance
  const leftDelay = safeSpringDelay(8, duration_frames, 0.22);
  const leftSpring = spring({
    frame: Math.max(0, frame - leftDelay),
    fps,
    config: tokens.motion.reveal,
  });

  // Phase 3: Option B (Right territory) entrance
  const rightDelay = safeSpringDelay(24, duration_frames, 0.38);
  const rightSpring = spring({
    frame: Math.max(0, frame - rightDelay),
    fps,
    config: tokens.motion.reveal,
  });

  // Phase 4: Central Axis & Horizontal Measurement bracket
  const vsDelay = safeSpringDelay(42, duration_frames, 0.50);
  const vsSpring = spring({
    frame: Math.max(0, frame - vsDelay),
    fps,
    config: { damping: 14, stiffness: 120 },
  });

  // Number Count-Up Progress (guaranteed safe window)
  const [countStart, countEnd] = safeAnimationWindow(14, 55, duration_frames, 2);
  const countProgress = interpolate(
    frame,
    [countStart, countEnd],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // Phase 5: Delta callout & Advantage illumination
  const deltaDelay = safeSpringDelay(64, duration_frames, 0.65);
  const deltaSpring = spring({
    frame: Math.max(0, frame - deltaDelay),
    fps,
    config: tokens.motion.impact,
  });

  // Phase 6: Footer note entrance
  const footerDelay = safeSpringDelay(84, duration_frames, 0.78);
  const footerSpring = spring({
    frame: Math.max(0, frame - footerDelay),
    fps,
    config: tokens.motion.gentle,
  });

  // Value formatting with live count-up
  const leftValueObj = formatValue(leftValRaw, countProgress, leftUnit);
  const rightValueObj = formatValue(rightValRaw, countProgress, rightUnit);

  // Dynamic font sizing
  const leftFontSize = getDynamicFontSize(String(leftValRaw || ""), 88, 54);
  const rightFontSize = getDynamicFontSize(String(rightValRaw || ""), 88, 54);

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
      <EditorialBackdrop
        hasWinner={hasWinner}
        isLeftWinner={isLeftWinner}
        isRightWinner={isRightWinner}
        winnerRgb={winnerRgb}
        glowOpacity={deltaSpring}
      />

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
          opacity: headerSpring,
          transform: `translateY(${interpolate(headerSpring, [0, 1], [-12, 0])}px)`,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <div
            style={{
              width: "7px",
              height: "7px",
              borderRadius: "50%",
              backgroundColor: deltaColor,
              boxShadow: `0 0 8px ${deltaColor}`,
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
            {headerLabel || "STRATEGY BENCHMARK"}
          </div>
        </div>

        {comparisonLabel && (
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
            {comparisonLabel}
          </div>
        )}
      </div>

      {/* Main Analytical Comparison Field */}
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
          minHeight: "380px",
        }}
      >
        {/* ================================================================ */}
        {/* OPTION A: Left Territory                                        */}
        {/* ================================================================ */}
        <div
          style={{
            flex: "1",
            maxWidth: "580px",
            opacity: leftSpring,
            transform: `translateX(${interpolate(leftSpring, [0, 1], [-32, 0])}px)`,
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
            paddingLeft: isLeftWinner ? "24px" : "0",
            position: "relative",
          }}
        >
          {/* Winner Vertical Datum Accent Guideline */}
          {isLeftWinner && (
            <div
              style={{
                position: "absolute",
                left: 0,
                top: "8%",
                bottom: "8%",
                width: "3px",
                opacity: deltaSpring,
                background: `linear-gradient(180deg, transparent 0%, ${leftColor} 30%, ${leftColor} 70%, transparent 100%)`,
                borderRadius: "2px",
                boxShadow: `0 0 16px rgba(${leftRgb}, 0.6)`,
              }}
            />
          )}

          {/* Eyebrow Label / Role */}
          <div
            style={{
              fontSize: "13px",
              fontWeight: 700,
              textTransform: "uppercase",
              letterSpacing: "0.14em",
              color: isLeftWinner ? leftColor : "#64748b",
              marginBottom: "12px",
              display: "flex",
              alignItems: "center",
              gap: "8px",
            }}
          >
            <span
              style={{
                width: "6px",
                height: "6px",
                borderRadius: "50%",
                backgroundColor: isLeftWinner ? leftColor : "#64748b",
                boxShadow: isLeftWinner ? `0 0 8px ${leftColor}` : "none",
              }}
            />
            {leftRole.toUpperCase()}
          </div>

          {/* Hero Tabular Value */}
          <div style={{ lineHeight: 1.05, marginBottom: "14px" }}>
            {renderValue(
              leftValueObj,
              leftFontSize,
              isLeftWinner ? "#f8fafc" : "#e2e8f0",
              isLeftWinner && deltaSpring > 0.5,
              leftColor,
              leftRgb
            )}
          </div>

          {/* Supporting Role / Label */}
          {leftLabel ? (
            <div
              style={{
                fontSize: "19px",
                fontWeight: 500,
                color: "#94a3b8",
                lineHeight: 1.35,
                maxWidth: "460px",
                marginBottom: isLeftWinner ? "16px" : "0",
              }}
            >
              {leftLabel}
            </div>
          ) : null}

          {/* Winner Primary Advantage Badge */}
          {isLeftWinner && (
            <div
              style={{
                opacity: deltaSpring,
                transform: `translateY(${interpolate(deltaSpring, [0, 1], [8, 0])}px)`,
                display: "inline-flex",
                alignItems: "center",
                gap: "6px",
                alignSelf: "flex-start",
                padding: "6px 14px",
                borderRadius: tokens.radius.chip,
                backgroundColor: `rgba(${leftRgb}, 0.12)`,
                border: `1px solid rgba(${leftRgb}, 0.35)`,
                color: leftColor,
                fontSize: "12px",
                fontWeight: 700,
                letterSpacing: "0.08em",
                textTransform: "uppercase",
                boxShadow: `0 4px 14px rgba(0, 0, 0, 0.3)`,
              }}
            >
              <span>✦</span> PRIMARY ADVANTAGE
            </div>
          )}
        </div>

        {/* ================================================================ */}
        {/* CENTRAL MEASUREMENT AXIS & DELTA CONSEQUENCE                   */}
        {/* ================================================================ */}
        <div
          style={{
            position: "relative",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            width: "320px",
            flexShrink: 0,
            zIndex: 5,
          }}
        >
          {/* Vertical Axis Hairline */}
          <div
            style={{
              position: "absolute",
              top: "-140px",
              bottom: "-140px",
              width: "1px",
              background: "linear-gradient(180deg, transparent 0%, rgba(255, 255, 255, 0.04) 15%, rgba(255, 255, 255, 0.14) 35%, rgba(255, 255, 255, 0.14) 65%, rgba(255, 255, 255, 0.04) 85%, transparent 100%)",
              opacity: vsSpring,
            }}
          />

          {/* Top and Bottom Technical Crosshairs */}
          <div
            style={{
              position: "absolute",
              top: "-140px",
              fontSize: "10px",
              color: "rgba(255, 255, 255, 0.25)",
              opacity: vsSpring,
              transform: "translateY(-50%)",
            }}
          >
            +
          </div>
          <div
            style={{
              position: "absolute",
              bottom: "-140px",
              fontSize: "10px",
              color: "rgba(255, 255, 255, 0.25)",
              opacity: vsSpring,
              transform: "translateY(50%)",
            }}
          >
            +
          </div>

          {/* Connecting Horizontal Measurement Vector Line across Center */}
          <svg
            style={{
              position: "absolute",
              left: "-80px",
              right: "-80px",
              top: "50%",
              transform: "translateY(-50%)",
              width: "calc(100% + 160px)",
              height: "40px",
              pointerEvents: "none",
              zIndex: 1,
              overflow: "visible",
            }}
          >
            <line
              x1="0"
              y1="20"
              x2="100%"
              y2="20"
              stroke="rgba(255, 255, 255, 0.07)"
              strokeWidth="1.5"
              strokeDasharray="4 4"
            />
            <line
              x1={`${50 - 50 * vsSpring}%`}
              y1="20"
              x2={`${50 + 50 * vsSpring}%`}
              y2="20"
              stroke={deltaColor}
              strokeWidth="1.5"
              strokeOpacity={0.65}
            />
          </svg>

          {/* Consequence / Delta Plaque (revealed when delta is supplied) */}
          {delta ? (
            <div
              style={{
                position: "relative",
                zIndex: 10,
                opacity: deltaSpring,
                transform: `scale(${interpolate(deltaSpring, [0, 1], [0.9, 1])}) translateY(${interpolate(deltaSpring, [0, 1], [14, 0])}px)`,
                backgroundColor: "#090e1c",
                border: `1px solid rgba(${deltaRgb}, 0.35)`,
                borderRadius: "16px",
                padding: "16px 24px",
                boxShadow: `0 12px 36px rgba(0, 0, 0, 0.6), 0 0 24px rgba(${deltaRgb}, 0.16)`,
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                gap: "4px",
                textAlign: "center",
              }}
            >
              <div
                style={{
                  fontSize: "11px",
                  fontWeight: 700,
                  textTransform: "uppercase",
                  letterSpacing: "0.14em",
                  color: deltaColor,
                  display: "flex",
                  alignItems: "center",
                  gap: "6px",
                }}
              >
                <span style={{ width: "5px", height: "5px", borderRadius: "50%", backgroundColor: deltaColor }} />
                MEASURED SPREAD
              </div>
              <div
                style={{
                  fontSize: "30px",
                  fontWeight: 800,
                  fontVariantNumeric: "tabular-nums lining-nums",
                  letterSpacing: "-0.025em",
                  color: deltaColor,
                  lineHeight: 1.1,
                  textShadow: `0 0 20px rgba(${deltaRgb}, 0.4)`,
                }}
              >
                {delta}
              </div>
            </div>
          ) : (
            /* Clean Precision Datum Medallion when no delta is provided */
            <div
              style={{
                position: "relative",
                zIndex: 10,
                opacity: vsSpring,
                transform: `scale(${interpolate(vsSpring, [0, 1], [0.8, 1])})`,
                width: "48px",
                height: "48px",
                borderRadius: "50%",
                backgroundColor: "#090e1c",
                border: "1px solid rgba(255, 255, 255, 0.18)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: "12px",
                fontWeight: 800,
                letterSpacing: "0.12em",
                color: "#94a3b8",
                boxShadow: "0 8px 24px rgba(0, 0, 0, 0.5)",
              }}
            >
              VS
            </div>
          )}
        </div>

        {/* ================================================================ */}
        {/* OPTION B: Right Territory                                       */}
        {/* ================================================================ */}
        <div
          style={{
            flex: "1",
            maxWidth: "580px",
            opacity: rightSpring,
            transform: `translateX(${interpolate(rightSpring, [0, 1], [32, 0])}px)`,
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
            alignItems: "flex-end",
            textAlign: "right",
            paddingRight: isRightWinner ? "24px" : "0",
            position: "relative",
          }}
        >
          {/* Winner Vertical Datum Accent Guideline */}
          {isRightWinner && (
            <div
              style={{
                position: "absolute",
                right: 0,
                top: "8%",
                bottom: "8%",
                width: "3px",
                opacity: deltaSpring,
                background: `linear-gradient(180deg, transparent 0%, ${rightColor} 30%, ${rightColor} 70%, transparent 100%)`,
                borderRadius: "2px",
                boxShadow: `0 0 16px rgba(${rightRgb}, 0.6)`,
              }}
            />
          )}

          {/* Eyebrow Label / Role */}
          <div
            style={{
              fontSize: "13px",
              fontWeight: 700,
              textTransform: "uppercase",
              letterSpacing: "0.14em",
              color: isRightWinner ? rightColor : "#64748b",
              marginBottom: "12px",
              display: "flex",
              alignItems: "center",
              gap: "8px",
            }}
          >
            {rightRole.toUpperCase()}
            <span
              style={{
                width: "6px",
                height: "6px",
                borderRadius: "50%",
                backgroundColor: isRightWinner ? rightColor : "#64748b",
                boxShadow: isRightWinner ? `0 0 8px ${rightColor}` : "none",
              }}
            />
          </div>

          {/* Hero Tabular Value */}
          <div style={{ lineHeight: 1.05, marginBottom: "14px" }}>
            {renderValue(
              rightValueObj,
              rightFontSize,
              isRightWinner ? "#f8fafc" : "#e2e8f0",
              isRightWinner && deltaSpring > 0.5,
              rightColor,
              rightRgb
            )}
          </div>

          {/* Supporting Role / Label */}
          {rightLabel ? (
            <div
              style={{
                fontSize: "19px",
                fontWeight: 500,
                color: "#94a3b8",
                lineHeight: 1.35,
                maxWidth: "460px",
                marginBottom: isRightWinner ? "16px" : "0",
              }}
            >
              {rightLabel}
            </div>
          ) : null}

          {/* Winner Primary Advantage Badge */}
          {isRightWinner && (
            <div
              style={{
                opacity: deltaSpring,
                transform: `translateY(${interpolate(deltaSpring, [0, 1], [8, 0])}px)`,
                display: "inline-flex",
                alignItems: "center",
                gap: "6px",
                alignSelf: "flex-end",
                padding: "6px 14px",
                borderRadius: tokens.radius.chip,
                backgroundColor: `rgba(${rightRgb}, 0.12)`,
                border: `1px solid rgba(${rightRgb}, 0.35)`,
                color: rightColor,
                fontSize: "12px",
                fontWeight: 700,
                letterSpacing: "0.08em",
                textTransform: "uppercase",
                boxShadow: `0 4px 14px rgba(0, 0, 0, 0.3)`,
              }}
            >
              <span>✦</span> PRIMARY ADVANTAGE
            </div>
          )}
        </div>
      </div>

      {/* Optional Contextual Footer Note */}
      {footerLabel && (
        <div
          style={{
            position: "absolute",
            bottom: "84px",
            opacity: footerSpring,
            transform: `translateY(${interpolate(footerSpring, [0, 1], [10, 0])}px)`,
            display: "inline-flex",
            alignItems: "center",
            gap: "8px",
            padding: "8px 18px",
            borderRadius: tokens.radius.chip,
            backgroundColor: "rgba(255, 255, 255, 0.04)",
            border: "1px solid rgba(255, 255, 255, 0.10)",
            color: "#cbd5e1",
            fontSize: "14px",
            fontWeight: 600,
            letterSpacing: "0.03em",
            lineHeight: 1.2,
            boxShadow: "0 4px 16px rgba(0, 0, 0, 0.35)",
            zIndex: 10,
          }}
        >
          <span style={{ color: deltaColor, fontSize: "15px" }}>✦</span>
          <span>{footerLabel}</span>
        </div>
      )}
    </AbsoluteFill>
  );
}

// Architectural alias preserving both naming conventions
export const ComparisonSplit = SplitComparison;
