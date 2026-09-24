import React from 'react';
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { tokens } from '../design-tokens';
import { TimeDecayProps } from '../types';
import { safeAnimationWindow, safeSpringDelay } from '../animation-safety';

// Helper to extract numeric values from currency/quantity strings (e.g. "₹50,000" -> 50000, "₹10 lakh" -> 1000000)
function extractNumericAmount(val: string): number | null {
  if (!val) return null;
  const clean = val.toLowerCase().replace(/,/g, '').trim();

  // Check for lakh / lac
  const lakhMatch = clean.match(/([\d.]+)\s*(?:lakh|lac)/);
  if (lakhMatch) {
    const n = parseFloat(lakhMatch[1]);
    if (!isNaN(n)) return n * 100000;
  }
  const crMatch = clean.match(/([\d.]+)\s*(?:crore|cr)/);
  if (crMatch) {
    const n = parseFloat(crMatch[1]);
    if (!isNaN(n)) return n * 10000000;
  }
  const kMatch = clean.match(/([\d.]+)\s*k/);
  if (kMatch) {
    const n = parseFloat(kMatch[1]);
    if (!isNaN(n)) return n * 1000;
  }
  const rawNumMatch = clean.match(/([\d.]+)/);
  if (rawNumMatch) {
    const n = parseFloat(rawNumMatch[1]);
    if (!isNaN(n)) return n;
  }
  return null;
}

interface DeclineProfile {
  ratio: number; // 0.15 (mild) to 0.82 (catastrophic)
  dropPercentStr: string; // e.g. "-18%", "-74%"
  severityLevel: "mild" | "moderate" | "severe";
  endDisplayValue: string;
}

function resolveDeclineProfile(
  fixedAmount: string,
  endValue?: string | null,
  dropRate?: string | null,
  annotation?: string | null,
  severity?: string | null,
  variant?: string | null,
  decayType?: string | null
): DeclineProfile {
  const isSinglePeriod = decayType === "single_period" || variant === "single_period_drop";
  const startNum = extractNumericAmount(fixedAmount);
  const endNum = endValue ? extractNumericAmount(endValue) : null;

  // 1. Single-period drop handling (e.g. 15% first-year depreciation - not compounded)
  if (isSinglePeriod) {
    const rateSource = dropRate || annotation || endValue || "";
    const pctMatch = rateSource.match(/(\d+(?:\.\d+)?)\s*%/);
    const parsedPct = pctMatch ? parseFloat(pctMatch[1]) : (dropRate && !isNaN(parseFloat(dropRate)) ? parseFloat(dropRate) : 15);
    const validPct = !isNaN(parsedPct) && parsedPct > 0 ? parsedPct : 15;
    const ratio = Math.min(0.82, Math.max(0.10, validPct / 100));
    const level: "mild" | "moderate" | "severe" =
      severity === "mild" ? "mild" : severity === "severe" ? "severe" : validPct <= 20 ? "mild" : validPct >= 45 ? "severe" : "moderate";
    const endVal =
      endValue ||
      (startNum ? `₹${Math.round(startNum * (1 - ratio)).toLocaleString('en-IN')}` : `${Math.round(100 - validPct)}% Value`);
    return { ratio, dropPercentStr: `-${Math.round(validPct)}%`, severityLevel: level, endDisplayValue: endVal };
  }

  // 2. Exact numeric comparison if both fixedAmount and endValue are present
  if (startNum && endNum && startNum > 0 && endNum < startNum) {
    const rawRatio = (startNum - endNum) / startNum;
    const ratio = Math.min(0.82, Math.max(0.15, rawRatio));
    const pct = Math.round(rawRatio * 100);
    const level: "mild" | "moderate" | "severe" =
      severity === "mild" ? "mild" : severity === "severe" ? "severe" : pct <= 25 ? "mild" : pct >= 55 ? "severe" : "moderate";
    return { ratio, dropPercentStr: `-${pct}%`, severityLevel: level, endDisplayValue: endValue! };
  }

  // 3. Explicit dropRate or percentage in annotation
  const rateSource = dropRate || annotation || "";
  const pctMatch = rateSource.match(/(\d+(?:\.\d+)?)\s*%/);
  if (pctMatch) {
    const pct = parseFloat(pctMatch[1]);
    if (!isNaN(pct) && pct > 0) {
      const ratio = Math.min(0.82, Math.max(0.15, pct / 100));
      const level: "mild" | "moderate" | "severe" =
        severity === "mild" ? "mild" : severity === "severe" ? "severe" : pct <= 25 ? "mild" : pct >= 55 ? "severe" : "moderate";
      const endVal =
        endValue ||
        (startNum ? `₹${Math.round(startNum * (1 - ratio)).toLocaleString('en-IN')}` : `${Math.round(100 - pct)}% Value`);
      return { ratio, dropPercentStr: `-${Math.round(pct)}%`, severityLevel: level, endDisplayValue: endVal };
    }
  }

  // 4. Explicit variant / severity presets
  if (variant === "mild_decay" || severity === "mild") {
    const endVal =
      endValue ||
      (startNum ? `₹${Math.round(startNum * 0.82).toLocaleString('en-IN')}` : "82% Value");
    return { ratio: 0.18, dropPercentStr: "-18%", severityLevel: "mild", endDisplayValue: endVal };
  }
  if (variant === "severe_decay" || severity === "severe" || severity === "catastrophic") {
    const endVal =
      endValue ||
      (startNum ? `₹${Math.round(startNum * 0.26).toLocaleString('en-IN')}` : "26% Value");
    return { ratio: 0.74, dropPercentStr: "-74%", severityLevel: "severe", endDisplayValue: endVal };
  }

  // 5. Default standard erosion (~48% purchasing power decay)
  const fallbackEnd =
    endValue ||
    (startNum ? `₹${Math.round(startNum * 0.52).toLocaleString('en-IN')}` : "52% Value");
  return { ratio: 0.48, dropPercentStr: "-48%", severityLevel: "moderate", endDisplayValue: fallbackEnd };
}

export function TimeDecay(props: TimeDecayProps | any) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const resolvedProps: TimeDecayProps = (props as any).props || props;
  const duration_frames = (props as any).duration_frames || 180;

  const fixedAmount = resolvedProps.fixedAmount || "Original Value";
  const amountLabel = resolvedProps.amountLabel || "Fixed Income";
  const timePeriod = resolvedProps.timePeriod || "15 Years";
  const emphasis = resolvedProps.emphasis || "value_erosion";
  const annotation = resolvedProps.annotation || null;
  const showChart = resolvedProps.showChart !== false;
  const endValue = resolvedProps.endValue || null;
  const endLabel = resolvedProps.endLabel || null;
  const dropRate = resolvedProps.dropRate || null;
  const severity = resolvedProps.severity || null;
  const variant = resolvedProps.variant || null;
  const rateLabel = resolvedProps.rateLabel || null;
  const decayType = resolvedProps.decayType || (variant === "single_period_drop" || emphasis === "single_period_drop" ? "single_period" : "standard");

  // Resolve decline dynamics
  const decline = resolveDeclineProfile(
    fixedAmount,
    endValue,
    dropRate,
    annotation,
    severity,
    variant,
    decayType
  );

  // Scene entrance fade
  const sceneOpacity = interpolate(
    frame,
    [0, Math.min(8, Math.max(1, duration_frames - 1))],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // Left anchor motion
  const anchorDelay = safeSpringDelay(4, duration_frames, 0.12);
  const anchorSpring = spring({
    frame: Math.max(0, frame - anchorDelay),
    fps,
    config: tokens.motion.reveal,
  });

  // Curve draw animation window
  const [curveStart, curveEnd] = safeAnimationWindow(12, 58, duration_frames);
  const curveProgress = interpolate(
    frame,
    [curveStart, curveEnd],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // Start dot spring
  const startDotDelay = safeSpringDelay(8, duration_frames, 0.18);
  const startDotSpring = spring({
    frame: Math.max(0, frame - startDotDelay),
    fps,
    config: tokens.motion.reveal,
  });

  // End ring / dot spring
  const endDotDelay = safeSpringDelay(32, duration_frames, 0.45);
  const endDotSpring = spring({
    frame: Math.max(0, frame - endDotDelay),
    fps,
    config: tokens.motion.impact,
  });

  // Terminal callout badge spring
  const calloutDelay = safeSpringDelay(38, duration_frames, 0.55);
  const calloutSpring = spring({
    frame: Math.max(0, frame - calloutDelay),
    fps,
    config: tokens.motion.settle,
  });

  // Annotation editorial spring
  const annotDelay = safeSpringDelay(46, duration_frames, 0.68);
  const annotSpring = spring({
    frame: Math.max(0, frame - annotDelay),
    fps,
    config: tokens.motion.gentle,
  });

  // SVG Chart Geometry
  const svgWidth = 840;
  const svgHeight = 310;
  const xStart = 60;
  const yStart = 50; // 100% baseline level
  const xEnd = 770;
  const yMin = 50;
  const yMax = 250; // Max decline level (approx 85% drop)

  const isSinglePeriod = decayType === "single_period" || variant === "single_period_drop";

  // Dynamic end point based on decline ratio
  const yEnd = Math.round(yMin + (yMax - yMin) * (decline.ratio / 0.82));

  // Bezier curve: front-loaded descent for single-period depreciation, or compounding descent for inflation
  const cp1x = isSinglePeriod ? Math.round(xStart + (xEnd - xStart) * 0.25) : Math.round(xStart + (xEnd - xStart) * 0.32);
  const cp1y = isSinglePeriod ? Math.round(yStart + (yEnd - yStart) * 0.65) : Math.round(yStart + (yEnd - yStart) * 0.12);
  const cp2x = isSinglePeriod ? Math.round(xStart + (xEnd - xStart) * 0.70) : Math.round(xStart + (xEnd - xStart) * 0.68);
  const cp2y = isSinglePeriod ? Math.round(yEnd) : Math.round(yEnd - (yEnd - yStart) * 0.04);

  const pathData = `M ${xStart} ${yStart} C ${cp1x} ${cp1y}, ${cp2x} ${cp2y}, ${xEnd} ${yEnd}`;
  const areaFillData = `${pathData} L ${xEnd} 280 L ${xStart} 280 Z`;

  // Color Palette by Severity
  let startColor = tokens.accent.emerald;
  let midColor = tokens.accent.amber;
  let endColor = tokens.accent.rose;
  let severityBadgeBg = "rgba(244, 63, 94, 0.15)";
  let severityBadgeBorder = "rgba(244, 63, 94, 0.4)";
  let severityBadgeText = tokens.accent.rose;

  if (decline.severityLevel === "mild") {
    startColor = tokens.accent.emerald;
    midColor = "#34d399";
    endColor = tokens.accent.amber;
    severityBadgeBg = "rgba(245, 158, 11, 0.15)";
    severityBadgeBorder = "rgba(245, 158, 11, 0.4)";
    severityBadgeText = tokens.accent.amber;
  } else if (decline.severityLevel === "severe") {
    startColor = tokens.accent.emerald;
    midColor = tokens.accent.rose;
    endColor = "#e11d48"; // Crimson alert
    severityBadgeBg = "rgba(225, 29, 72, 0.2)";
    severityBadgeBorder = "rgba(225, 29, 72, 0.55)";
    severityBadgeText = "#fb7185";
  }

  // Terminal Badge vertical positioning (if low, badge sits above; if high, badge sits below)
  const badgeAbove = yEnd >= 140;
  const badgeTopPx = badgeAbove ? Math.max(10, yEnd - 108) : yEnd + 18;
  const badgeLeftPx = Math.min(xEnd - 260, 520);

  return (
    <AbsoluteFill
      style={{
        backgroundColor: tokens.bg.base,
        fontFamily: tokens.font.family,
        opacity: sceneOpacity,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "60px 80px",
        overflow: "hidden",
      }}
    >
      <div
        style={{
          display: "flex",
          flexDirection: "row",
          alignItems: "center",
          justifyContent: "space-between",
          width: "100%",
          maxWidth: "1680px",
          gap: "50px",
        }}
      >
        {/* Left: Fixed Nominal Anchor Card */}
        <div
          style={{
            opacity: anchorSpring,
            transform: `translateX(${interpolate(anchorSpring, [0, 1], [-40, 0])}px)`,
            flex: 0.85,
            maxWidth: "460px",
            minHeight: "420px",
            backgroundColor: tokens.bg.cardLeft,
            borderRadius: tokens.radius.card,
            border: `1px solid ${tokens.bg.border}`,
            borderLeft: `4px solid ${tokens.accent.cyan}`,
            padding: "44px 40px",
            display: "flex",
            flexDirection: "column",
            justifyContent: "space-between",
            boxShadow: "0 20px 45px -15px rgba(0, 0, 0, 0.55)",
          }}
        >
          <div>
            <div
              style={{
                fontSize: "17px",
                fontWeight: 600,
                textTransform: "uppercase",
                letterSpacing: "0.08em",
                color: tokens.text.secondary,
                marginBottom: "14px",
              }}
            >
              {amountLabel}
            </div>
            <div
              style={{
                fontSize: fixedAmount.length > 9 ? "46px" : "68px",
                fontWeight: 800,
                color: tokens.text.primary,
                lineHeight: 1.08,
                marginBottom: "10px",
              }}
            >
              {fixedAmount}
            </div>
            <div
              style={{
                fontSize: "16px",
                fontWeight: 500,
                color: tokens.text.muted,
                marginBottom: "28px",
              }}
            >
              {isSinglePeriod ? "Initial Baseline (Before Drop)" : "Nominal Baseline (Day 1 Constant)"}
            </div>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
            {/* Horizon Chip */}
            <div
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: "8px",
                fontSize: "17px",
                fontWeight: 700,
                color: tokens.accent.cyan,
                backgroundColor: "rgba(56, 189, 248, 0.12)",
                padding: "8px 18px",
                borderRadius: tokens.radius.chip,
                border: `1px solid rgba(56, 189, 248, 0.3)`,
                alignSelf: "flex-start",
                letterSpacing: "0.04em",
                textTransform: "uppercase",
              }}
            >
              <span>⏱</span>
              <span>{timePeriod}</span>
            </div>

            {/* Inflation / Rate Context */}
            {rateLabel && (
              <div
                style={{
                  fontSize: "15px",
                  fontWeight: 600,
                  color: tokens.text.secondary,
                  letterSpacing: "0.02em",
                }}
              >
                {rateLabel}
              </div>
            )}
          </div>
        </div>

        {/* Right: Dynamic Decay Trajectory Panel */}
        <div
          style={{
            flex: 1.35,
            minHeight: "440px",
            backgroundColor: tokens.bg.surface,
            borderRadius: tokens.radius.card,
            border: `1px solid ${tokens.bg.border}`,
            padding: "36px 44px",
            display: "flex",
            flexDirection: "column",
            justifyContent: "space-between",
            boxShadow: "0 25px 50px -15px rgba(0, 0, 0, 0.65)",
            position: "relative",
          }}
        >
          {/* Timeline Axis Top Header */}
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: "8px",
              fontSize: "15px",
              fontWeight: 700,
              textTransform: "uppercase",
              letterSpacing: "0.08em",
              color: tokens.text.muted,
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <div
                style={{
                  width: "10px",
                  height: "10px",
                  borderRadius: "50%",
                  backgroundColor: tokens.accent.emerald,
                }}
              />
              <span>Starting Baseline (100% Value)</span>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <span>{isSinglePeriod ? `Period: ${timePeriod}` : `Time Horizon: ${timePeriod}`}</span>
              <div
                style={{
                  width: "10px",
                  height: "10px",
                  borderRadius: "50%",
                  backgroundColor: endColor,
                }}
              />
            </div>
          </div>

          {/* SVG Trajectory Chart Container */}
          {showChart ? (
            <div
              style={{
                position: "relative",
                width: `${svgWidth}px`,
                height: `${svgHeight}px`,
                margin: "0 auto",
              }}
            >
              <svg width={svgWidth} height={svgHeight} viewBox={`0 0 ${svgWidth} ${svgHeight}`}>
                <defs>
                  {/* Dynamic Decay Gradient along curve */}
                  <linearGradient id="decayPathGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" stopColor={startColor} />
                    <stop offset="55%" stopColor={midColor} />
                    <stop offset="100%" stopColor={endColor} />
                  </linearGradient>

                  {/* Fading area gradient under curve */}
                  <linearGradient id="decayAreaGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" stopColor={endColor} stopOpacity="0.18" />
                    <stop offset="100%" stopColor={endColor} stopOpacity="0.0" />
                  </linearGradient>
                </defs>

                {/* Horizontal Reference Guidelines & Percentage Labels */}
                <line
                  x1={xStart}
                  y1={yStart}
                  x2={xEnd}
                  y2={yStart}
                  stroke="rgba(255, 255, 255, 0.09)"
                  strokeDasharray="4 4"
                  strokeWidth="1.5"
                />
                <text
                  x={xStart - 10}
                  y={yStart + 4}
                  fill={tokens.text.muted}
                  fontSize="13"
                  fontWeight="600"
                  textAnchor="end"
                >
                  100%
                </text>

                <line
                  x1={xStart}
                  y1={150}
                  x2={xEnd}
                  y2={150}
                  stroke="rgba(255, 255, 255, 0.06)"
                  strokeDasharray="4 4"
                  strokeWidth="1.5"
                />
                <text
                  x={xStart - 10}
                  y={154}
                  fill={tokens.text.muted}
                  fontSize="13"
                  fontWeight="600"
                  textAnchor="end"
                >
                  50%
                </text>

                <line
                  x1={xStart}
                  y1={yMax}
                  x2={xEnd}
                  y2={yMax}
                  stroke="rgba(255, 255, 255, 0.05)"
                  strokeDasharray="4 4"
                  strokeWidth="1.5"
                />
                <text
                  x={xStart - 10}
                  y={yMax + 4}
                  fill={tokens.text.muted}
                  fontSize="13"
                  fontWeight="600"
                  textAnchor="end"
                >
                  0%
                </text>

                {/* Subtle area fill under curve */}
                <path
                  d={areaFillData}
                  fill="url(#decayAreaGrad)"
                  opacity={curveProgress}
                />

                {/* Animated Dynamic Decay Bezier Curve */}
                <path
                  d={pathData}
                  stroke="url(#decayPathGrad)"
                  strokeWidth="5.5"
                  fill="none"
                  strokeLinecap="round"
                  strokeDasharray="1100"
                  strokeDashoffset={1100 * (1 - curveProgress)}
                />

                {/* Origin start marker (100% Value Day 1) */}
                <circle
                  cx={xStart}
                  cy={yStart}
                  r={8 * startDotSpring}
                  fill={tokens.accent.emerald}
                  stroke="#ffffff"
                  strokeWidth="2.5"
                />

                {/* Terminal endpoint marker with pulse aura */}
                <circle
                  cx={xEnd}
                  cy={yEnd}
                  r={18 * endDotSpring}
                  fill="none"
                  stroke={endColor}
                  strokeWidth="2"
                  opacity={0.35 * endDotSpring}
                />
                <circle
                  cx={xEnd}
                  cy={yEnd}
                  r={9 * endDotSpring}
                  fill={endColor}
                  stroke="#ffffff"
                  strokeWidth="2.5"
                />
              </svg>

              {/* High-Impact Terminal Endpoint Callout Badge */}
              <div
                style={{
                  position: "absolute",
                  top: `${badgeTopPx}px`,
                  left: `${badgeLeftPx}px`,
                  opacity: calloutSpring,
                  transform: `scale(${interpolate(calloutSpring, [0, 1], [0.85, 1])})`,
                  backgroundColor: "rgba(15, 23, 42, 0.95)",
                  border: `2px solid ${endColor}`,
                  borderRadius: tokens.radius.card,
                  padding: "16px 24px",
                  display: "flex",
                  flexDirection: "column",
                  boxShadow: `0 15px 35px -10px ${endColor}44, 0 10px 20px -5px rgba(0, 0, 0, 0.8)`,
                  zIndex: 10,
                  maxWidth: "280px",
                }}
              >
                <div
                  style={{
                    fontSize: "13px",
                    fontWeight: 800,
                    textTransform: "uppercase",
                    letterSpacing: "0.08em",
                    color: tokens.text.secondary,
                    marginBottom: "4px",
                  }}
                >
                  {endLabel || (isSinglePeriod || decline.severityLevel === "mild" ? "RESIDUAL VALUE" : "REAL PURCHASING POWER")}
                </div>
                <div
                  style={{
                    fontSize: "36px",
                    fontWeight: 800,
                    color: endColor,
                    lineHeight: 1.1,
                    marginBottom: "8px",
                  }}
                >
                  {decline.endDisplayValue}
                </div>
                <div
                  style={{
                    display: "inline-flex",
                    alignItems: "center",
                    gap: "6px",
                    fontSize: "13px",
                    fontWeight: 800,
                    color: severityBadgeText,
                    backgroundColor: severityBadgeBg,
                    border: `1px solid ${severityBadgeBorder}`,
                    padding: "4px 10px",
                    borderRadius: tokens.radius.chip,
                    letterSpacing: "0.04em",
                    textTransform: "uppercase",
                    alignSelf: "flex-start",
                  }}
                >
                  <span>📉</span>
                  <span>{decline.dropPercentStr} {isSinglePeriod ? "DROP" : "EROSION"}</span>
                </div>
              </div>
            </div>
          ) : (
            <div
              style={{
                height: "220px",
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "center",
                gap: "14px",
              }}
            >
              <div style={{ fontSize: "36px", fontWeight: 800, color: endColor }}>
                {decline.dropPercentStr} {isSinglePeriod ? "Value Decline" : "Purchasing Power Loss"}
              </div>
              <div style={{ fontSize: "20px", color: tokens.text.secondary }}>
                Terminal {isSinglePeriod ? "Value" : "Real Value"}: {decline.endDisplayValue}
              </div>
            </div>
          )}

          {/* Bottom Editorial Callout (if annotation exists) */}
          {annotation && (
            <div
              style={{
                opacity: annotSpring,
                transform: `translateY(${interpolate(annotSpring, [0, 1], [16, 0])}px)`,
                marginTop: "14px",
                padding: "14px 22px",
                borderRadius: tokens.radius.chip,
                backgroundColor: severityBadgeBg,
                border: `1px solid ${severityBadgeBorder}`,
                borderLeft: `5px solid ${endColor}`,
                color: tokens.text.primary,
                fontSize: "18px",
                fontWeight: 600,
                display: "flex",
                alignItems: "center",
                gap: "10px",
              }}
            >
              <span>⚠</span>
              <span>{annotation}</span>
            </div>
          )}
        </div>
      </div>
    </AbsoluteFill>
  );
}
