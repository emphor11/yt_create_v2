import {
  AbsoluteFill,
  Easing,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { type NumberCounterRenderSpec } from "./types";
import { tokens } from "./design-tokens";

export function NumberCounter(renderSpec: NumberCounterRenderSpec) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const duration_frames = renderSpec.duration_frames || 180;
  const isClean = renderSpec.props.startValue !== undefined;
  const startValue = isClean ? renderSpec.props.startValue! : (renderSpec.props.left?.value || 0);
  const endValue = isClean ? renderSpec.props.endValue! : (renderSpec.props.right?.value || 100);
  const label = isClean ? (renderSpec.props.label || "Metric") : `${renderSpec.props.left?.label || ""} ➔ ${renderSpec.props.right?.label || ""}`;
  const unit = renderSpec.props.unit || (renderSpec.props.left?.unit || "");

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

  const currentValue = Math.round(interpolate(countProgress, [0, 1], [startValue, endValue]));

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
            {renderSpec.props.headerLabel || "KEY METRIC"}
          </div>
          {renderSpec.props.title && (
            <div
              style={{
                fontSize: 54,
                fontWeight: 900,
                marginTop: 16,
              }}
            >
              {renderSpec.props.title}
            </div>
          )}
        </header>

        <main
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <div style={{ color: tokens.text.secondary, fontSize: 26, fontWeight: 800, textTransform: "uppercase", letterSpacing: 1.5 }}>
            {label}
          </div>
          <div
            style={{
              display: "flex",
              alignItems: "baseline",
              justifyContent: "center",
              marginTop: 20,
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

        {renderSpec.props.footerLabel ? (
          <footer style={{ fontSize: 26, color: "#9ca3af", fontWeight: 600 }}>
            {renderSpec.props.footerLabel}
          </footer>
        ) : null}
      </div>
    </AbsoluteFill>
  );
}
