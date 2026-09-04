import {
  AbsoluteFill,
  Easing,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { type NumberCounterProps } from "./types";
import { tokens } from "./design-tokens";

/**
 * Format float number preserving precision
 */
function formatNumberWithPrecision(val: number, precision?: number): string {
  if (precision !== undefined) {
    return val.toFixed(precision);
  }
  const isFloat = val % 1 !== 0;
  if (isFloat) {
    // Keep 1 or 2 decimals
    const str = val.toString();
    const decimalPlaces = str.split(".")[1]?.length || 1;
    return val.toFixed(Math.min(2, decimalPlaces));
  }
  return Math.round(val).toLocaleString();
}

export function NumberCounter(props: NumberCounterProps | any) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Normalize boundary props wrapper
  const resolvedProps: NumberCounterProps = props.props ? props.props : props;
  const duration_frames = (props as any).duration_frames || 180;

  const headerLabel = resolvedProps.headerLabel || "";
  const label = resolvedProps.label || "";
  const startValue = typeof resolvedProps.startValue === "number" ? resolvedProps.startValue : 0;
  const endValue = typeof resolvedProps.endValue === "number" ? resolvedProps.endValue : 100;

  const prefix = resolvedProps.prefix || "";
  const suffix = resolvedProps.suffix || resolvedProps.unit || "";
  const precision = resolvedProps.precision;
  const delta = resolvedProps.delta || "";
  const subtitle = resolvedProps.subtitle || "";

  // Auto-detect variant
  const variant = resolvedProps.variant || (startValue !== 0 ? "change" : "single");

  // Sequential Animation Timeline (NO CONTINUOUS PULSE!)
  const labelSpring = spring({
    frame,
    fps,
    config: { damping: 15, stiffness: 100 },
  });

  // Count-up progress over 60% of scene duration
  const countProgress = interpolate(
    frame,
    [Math.round(duration_frames * 0.15), Math.round(duration_frames * 0.65)],
    [0, 1],
    {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
      easing: Easing.bezier(0.16, 1, 0.3, 1),
    }
  );

  const currentRawVal = startValue + (endValue - startValue) * countProgress;
  const displayVal = formatNumberWithPrecision(currentRawVal, precision);

  // Subtle impact scale landing when counter completes (65% - 75%)
  const settleSpring = spring({
    frame: Math.max(0, frame - Math.round(duration_frames * 0.65)),
    fps,
    config: { damping: 12, stiffness: 120 },
  });

  // Delta takeaway & subtitle entrance (75%+)
  const deltaSpring = spring({
    frame: Math.max(0, frame - Math.round(duration_frames * 0.72)),
    fps,
    config: { damping: 14, stiffness: 100 },
  });

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
          alignItems: "center",
          textAlign: "center",
        }}
      >
        {/* Header Eyebrow */}
        {headerLabel ? (
          <header
            style={{
              opacity: labelSpring,
              transform: `translateY(${(1 - labelSpring) * -15}px)`,
            }}
          >
            <div
              style={{
                color: tokens.accent.blue,
                fontSize: tokens.font.eyebrow,
                fontWeight: 800,
                textTransform: "uppercase",
                letterSpacing: 2,
              }}
            >
              {headerLabel}
            </div>
          </header>
        ) : null}

        {/* Main Metric Hero Section */}
        <main
          style={{
            position: "relative",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            flex: 1,
            margin: "20px 0",
          }}
        >
          {/* Optional Metric Title / Category */}
          {label ? (
            <div
              style={{
                color: tokens.text.secondary,
                fontSize: 26,
                fontWeight: 800,
                textTransform: "uppercase",
                letterSpacing: 2,
                marginBottom: 16,
                opacity: labelSpring,
              }}
            >
              {label}
            </div>
          ) : null}

          {/* CHANGE VARIANT: Starting Point Indicator */}
          {variant === "change" && startValue !== 0 ? (
            <div
              style={{
                fontSize: 32,
                fontWeight: 700,
                color: tokens.text.muted,
                marginBottom: 8,
                opacity: labelSpring,
              }}
            >
              {prefix}
              {formatNumberWithPrecision(startValue, precision)}
              {suffix}
              <span style={{ margin: "0 12px", color: tokens.accent.blue }}>➔</span>
            </div>
          ) : null}

          {/* HERO COUNTING NUMBER */}
          <div
            style={{
              display: "flex",
              alignItems: "baseline",
              justifyContent: "center",
              transform: `scale(${0.96 + settleSpring * 0.04})`,
            }}
          >
            {prefix ? (
              <span
                style={{
                  fontSize: 84,
                  fontWeight: 900,
                  color: "#ffffff",
                  marginRight: 6,
                }}
              >
                {prefix}
              </span>
            ) : null}

            <span
              style={{
                fontSize: 120,
                fontWeight: 950,
                lineHeight: 1,
                letterSpacing: -3,
                color: "#ffffff",
                fontVariantNumeric: "tabular-nums",
              }}
            >
              {displayVal}
            </span>

            {suffix ? (
              <span
                style={{
                  fontSize: 76,
                  fontWeight: 900,
                  color: "#ffffff",
                  marginLeft: 8,
                }}
              >
                {suffix}
              </span>
            ) : null}
          </div>

          {/* DELTA TAKEAWAY BADGE */}
          {delta ? (
            <div
              style={{
                marginTop: 24,
                opacity: deltaSpring,
                transform: `translateY(${(1 - deltaSpring) * 15}px)`,
              }}
            >
              <div
                style={{
                  display: "inline-block",
                  fontSize: 24,
                  fontWeight: 900,
                  color: delta.startsWith("-") ? "#ef4444" : "#10b981",
                  background: delta.startsWith("-")
                    ? "rgba(239, 68, 68, 0.15)"
                    : "rgba(16, 185, 129, 0.15)",
                  border: `1.5px solid ${delta.startsWith("-") ? "#ef4444" : "#10b981"}`,
                  padding: "6px 24px",
                  borderRadius: "20px",
                  letterSpacing: 1,
                }}
              >
                {delta.startsWith("-") || delta.startsWith("+") ? "" : "▲ "}
                {delta}
              </div>
            </div>
          ) : null}

          {/* SUBTITLE / CONTEXT PERIOD */}
          {subtitle ? (
            <div
              style={{
                fontSize: 22,
                fontWeight: 600,
                color: tokens.text.secondary,
                marginTop: 16,
                opacity: deltaSpring,
              }}
            >
              {subtitle}
            </div>
          ) : null}
        </main>

        {/* Footer */}
        {resolvedProps.footerLabel ? (
          <footer style={{ textAlign: "center", fontSize: 20, color: tokens.text.muted, fontWeight: 600 }}>
            {resolvedProps.footerLabel}
          </footer>
        ) : null}
      </div>
    </AbsoluteFill>
  );
}
