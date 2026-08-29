import {
  AbsoluteFill,
  Easing,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { type NumberCounterRenderSpec } from "./types";
import { tokens } from "./design-tokens";

export function NumberCounter(renderSpec: NumberCounterRenderSpec) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const duration_frames = renderSpec.duration_frames || 180;
  const props = renderSpec.props as any;

  // Extract exact component properties
  const headerLabel = props.headerLabel || "";
  const label = props.label || "";
  const startValue = typeof props.startValue === "number" ? props.startValue : (parseFloat(String(props.startValue || 0)) || 0);
  const endValue = typeof props.endValue === "number" ? props.endValue : (parseFloat(String(props.endValue || 100)) || 100);
  const unit = props.unit || "";
  const footerLabel = props.footerLabel || "";

  // Counter animation scales dynamically across 75% of scene duration
  const countProgress = interpolate(
    frame,
    [0, Math.round(duration_frames * 0.75)],
    [0, 1],
    {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
      easing: Easing.bezier(0.16, 1, 0.3, 1), // ease-out-expo
    }
  );

  const currentValue = Math.round(startValue + (endValue - startValue) * countProgress);

  // Living motion: subtle breathing pulse to keep long scene holds dynamic
  const pulse = 1 + Math.sin((frame / duration_frames) * Math.PI * 4) * 0.02;

  return (
    <AbsoluteFill
      style={{
        background: `linear-gradient(135deg, ${tokens.bg.cardLeft} 0%, ${tokens.bg.cardRight} 100%)`,
        backdropFilter: "blur(4px)",
        color: tokens.text.primary,
        fontFamily: tokens.font.family,
        overflow: "hidden",
        padding: tokens.spacing.padding,
      }}
    >
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          height: "100%",
          justifyContent: "space-between",
          alignItems: "center",
          textAlign: "center",
        }}
      >
        {headerLabel ? (
          <header>
            <div
              style={{
                color: tokens.accent.purple,
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

        <main
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            flex: 1,
          }}
        >
          {label ? (
            <div style={{ color: tokens.text.secondary, fontSize: 26, fontWeight: 800, textTransform: "uppercase", letterSpacing: 1.5 }}>
              {label}
            </div>
          ) : null}
          <div
            style={{
              display: "flex",
              alignItems: "baseline",
              justifyContent: "center",
              marginTop: label ? 20 : 0,
              transform: `scale(${pulse})`,
            }}
          >
            {/* Currency Prefix if INR or USD */}
            {unit === "INR" || unit === "₹" ? (
              <span style={{ fontSize: 72, fontWeight: 900, color: tokens.accent.purple, marginRight: 8 }}>₹</span>
            ) : unit === "USD" || unit === "$" ? (
              <span style={{ fontSize: 72, fontWeight: 900, color: tokens.accent.purple, marginRight: 8 }}>$</span>
            ) : null}

            {/* Main Numeric Counter */}
            <span
              style={{
                fontSize: 144,
                fontWeight: 950,
                color: tokens.accent.purple,
                lineHeight: 1,
                textShadow: "0 0 40px rgba(168, 85, 247, 0.4)",
              }}
            >
              {currentValue.toLocaleString()}
            </span>

            {/* Unit Suffix for non-currency units (e.g. months, years, %, GB) */}
            {unit && unit !== "INR" && unit !== "₹" && unit !== "USD" && unit !== "$" ? (
              <span
                style={{
                  fontSize: 54,
                  fontWeight: 800,
                  color: tokens.text.secondary,
                  marginLeft: 16,
                  textTransform: "lowercase",
                }}
              >
                {unit}
              </span>
            ) : null}
          </div>
        </main>

        {footerLabel ? (
          <footer style={{ fontSize: 26, color: "#9ca3af", fontWeight: 600 }}>
            {footerLabel}
          </footer>
        ) : null}
      </div>
    </AbsoluteFill>
  );
}
