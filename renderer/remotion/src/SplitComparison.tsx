import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { type SplitComparisonProps } from "./types";
import { tokens } from "./design-tokens";

/**
 * Smart Number Formatter & Interpolator for Split Comparisons
 */
function formatValue(rawVal: string | number | undefined, progress: number, unit?: string): string {
  if (rawVal === undefined || rawVal === null) return "";
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
  const duration_frames = (props as any).duration_frames || 180;

  const headerLabel = resolvedProps.headerLabel || "";
  const comparisonLabel = (resolvedProps as any).comparison_label || resolvedProps.comparisonLabel || "";
  const tone = resolvedProps.tone || "neutral";
  const delta = resolvedProps.delta || "";
  const winner = resolvedProps.winner || null;

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
  let leftColor = "#3b82f6";
  let rightColor = "#06b6d4";

  if (tone === "positive_negative") {
    leftColor = "#ef4444";  // Bear/Loss Red
    rightColor = "#10b981"; // Bull/Profit Green
  } else if (tone === "before_after") {
    leftColor = "#f59e0b";  // Before Amber
    rightColor = "#10b981"; // After Emerald Green
  }

  // Animation Springs & Timings
  // Frame 0..20: Left & Right Cards enter from sides
  const leftSpring = spring({
    frame,
    fps,
    config: { damping: 14, stiffness: 90 },
  });

  const rightSpring = spring({
    frame,
    fps,
    config: { damping: 14, stiffness: 90 },
  });

  // Frame 15..30: Central VS Badge pops in
  const vsSpring = spring({
    frame: Math.max(0, frame - 15),
    fps,
    config: { damping: 12, stiffness: 120 },
  });

  // Frame 25..55: Number Count-Up Progress
  const countProgress = interpolate(
    frame,
    [25, 55],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // Frame 40..60: Delta / Winner callout lands
  const deltaSpring = spring({
    frame: Math.max(0, frame - 40),
    fps,
    config: { damping: 14, stiffness: 100 },
  });

  const leftFormattedVal = formatValue(leftValRaw, countProgress, leftUnit);
  const rightFormattedVal = formatValue(rightValRaw, countProgress, rightUnit);

  const isLeftWinner = winner === "left";
  const isRightWinner = winner === "right";

  return (
    <AbsoluteFill
      style={{
        background: tokens.bg.base,
        color: tokens.text.primary,
        fontFamily: tokens.font.family,
        overflow: "hidden",
        padding: tokens.spacing.padding,
      }}
    >
      <div
        style={{
          position: "relative",
          display: "flex",
          flexDirection: "column",
          height: "100%",
          justifyContent: "space-between",
        }}
      >
        {/* Header Eyebrow & Optional Comparison Metric Topic */}
        <header style={{ textAlign: "center" }}>
          {headerLabel ? (
            <div
              style={{
                color: tokens.accent.blue,
                fontSize: tokens.font.eyebrow,
                fontWeight: 800,
                textTransform: "uppercase",
                letterSpacing: 2,
                marginBottom: comparisonLabel ? 4 : 0,
              }}
            >
              {headerLabel}
            </div>
          ) : null}

          {comparisonLabel ? (
            <div
              style={{
                fontSize: 28,
                fontWeight: 900,
                letterSpacing: 2,
                textTransform: "uppercase",
                color: "#ffffff",
                background: "rgba(255, 255, 255, 0.05)",
                display: "inline-block",
                padding: "6px 20px",
                borderRadius: "20px",
                border: "1px solid rgba(255, 255, 255, 0.15)",
              }}
            >
              {comparisonLabel}
            </div>
          ) : null}
        </header>

        {/* Main Side-by-Side Comparison Layout with Central VS Badge */}
        <main
          style={{
            position: "relative",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: "24px",
            flex: 1,
            margin: "20px 0",
          }}
        >
          {/* LEFT COMPARISON CARD */}
          <div
            style={{
              flex: 1,
              position: "relative",
              background: isLeftWinner
                ? "linear-gradient(135deg, rgba(30, 41, 59, 0.95) 0%, rgba(15, 23, 42, 0.95) 100%)"
                : "rgba(15, 23, 42, 0.75)",
              border: `2px solid ${isLeftWinner ? "#f59e0b" : `${leftColor}55`}`,
              borderTop: `4px solid ${isLeftWinner ? "#f59e0b" : leftColor}`,
              borderRadius: "18px",
              padding: "36px 28px",
              textAlign: "center",
              boxShadow: isLeftWinner
                ? "0 10px 30px rgba(245, 158, 11, 0.3)"
                : "0 8px 25px rgba(0, 0, 0, 0.25)",
              opacity: leftSpring,
              transform: `translateX(${(1 - leftSpring) * -60}px)`,
            }}
          >
            {/* Winner Badge */}
            {isLeftWinner ? (
              <div
                style={{
                  position: "absolute",
                  top: "-14px",
                  left: "50%",
                  transform: "translateX(-50%)",
                  background: "#f59e0b",
                  color: "#000000",
                  fontSize: 12,
                  fontWeight: 900,
                  padding: "2px 12px",
                  borderRadius: "12px",
                  letterSpacing: 1,
                }}
              >
                WINNER 👑
              </div>
            ) : null}

            {/* Left Subject Name */}
            <div
              style={{
                fontSize: 24,
                fontWeight: 900,
                textTransform: "uppercase",
                letterSpacing: 1.5,
                color: leftColor,
                marginBottom: 6,
              }}
            >
              {leftRole}
            </div>

            {leftLabel ? (
              <div style={{ fontSize: 16, color: tokens.text.muted, fontWeight: 600, marginBottom: 16 }}>
                {leftLabel}
              </div>
            ) : (
              <div style={{ height: 16 }} />
            )}

            {/* Left Hero Value */}
            <div
              style={{
                fontSize: 64,
                fontWeight: 900,
                color: "#ffffff",
                lineHeight: 1,
                letterSpacing: -1,
              }}
            >
              {leftFormattedVal}
            </div>
          </div>

          {/* CENTRAL PROMINENT "VS" BADGE */}
          <div
            style={{
              position: "relative",
              zIndex: 10,
              opacity: vsSpring,
              transform: `scale(${vsSpring})`,
              flexShrink: 0,
            }}
          >
            <div
              style={{
                width: "64px",
                height: "64px",
                borderRadius: "50%",
                background: "linear-gradient(135deg, #1e293b 0%, #0f172a 100%)",
                border: "3px solid tokens.accent.blue",
                borderColor: tokens.accent.blue,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: 22,
                fontWeight: 900,
                color: "#ffffff",
                letterSpacing: 1,
                boxShadow: "0 0 20px rgba(59, 130, 246, 0.5), inset 0 0 10px rgba(255,255,255,0.1)",
              }}
            >
              VS
            </div>
          </div>

          {/* RIGHT COMPARISON CARD */}
          <div
            style={{
              flex: 1,
              position: "relative",
              background: isRightWinner
                ? "linear-gradient(135deg, rgba(30, 41, 59, 0.95) 0%, rgba(15, 23, 42, 0.95) 100%)"
                : "rgba(15, 23, 42, 0.75)",
              border: `2px solid ${isRightWinner ? "#f59e0b" : `${rightColor}55`}`,
              borderTop: `4px solid ${isRightWinner ? "#f59e0b" : rightColor}`,
              borderRadius: "18px",
              padding: "36px 28px",
              textAlign: "center",
              boxShadow: isRightWinner
                ? "0 10px 30px rgba(245, 158, 11, 0.3)"
                : "0 8px 25px rgba(0, 0, 0, 0.25)",
              opacity: rightSpring,
              transform: `translateX(${(1 - rightSpring) * 60}px)`,
            }}
          >
            {/* Winner Badge */}
            {isRightWinner ? (
              <div
                style={{
                  position: "absolute",
                  top: "-14px",
                  left: "50%",
                  transform: "translateX(-50%)",
                  background: "#f59e0b",
                  color: "#000000",
                  fontSize: 12,
                  fontWeight: 900,
                  padding: "2px 12px",
                  borderRadius: "12px",
                  letterSpacing: 1,
                }}
              >
                WINNER 👑
              </div>
            ) : null}

            {/* Right Subject Name */}
            <div
              style={{
                fontSize: 24,
                fontWeight: 900,
                textTransform: "uppercase",
                letterSpacing: 1.5,
                color: rightColor,
                marginBottom: 6,
              }}
            >
              {rightRole}
            </div>

            {rightLabel ? (
              <div style={{ fontSize: 16, color: tokens.text.muted, fontWeight: 600, marginBottom: 16 }}>
                {rightLabel}
              </div>
            ) : (
              <div style={{ height: 16 }} />
            )}

            {/* Right Hero Value */}
            <div
              style={{
                fontSize: 64,
                fontWeight: 900,
                color: "#ffffff",
                lineHeight: 1,
                letterSpacing: -1,
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
              transform: `translateY(${(1 - deltaSpring) * 15}px)`,
              marginBottom: 10,
            }}
          >
            <div
              style={{
                display: "inline-block",
                fontSize: 20,
                fontWeight: 900,
                color: "#10b981",
                background: "rgba(16, 185, 129, 0.15)",
                border: "1px solid #10b981",
                padding: "6px 20px",
                borderRadius: "20px",
                letterSpacing: 1,
              }}
            >
              {delta} DIFFERENCE
            </div>
          </div>
        ) : null}

        {/* Footer */}
        {footerLabel ? (
          <footer style={{ textAlign: "center", fontSize: 20, color: tokens.text.muted, fontWeight: 600 }}>
            {footerLabel}
          </footer>
        ) : null}
      </div>
    </AbsoluteFill>
  );
}
