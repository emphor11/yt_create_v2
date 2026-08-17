import {
  AbsoluteFill,
  Easing,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { type ChartsRenderSpec } from "./types";
import { tokens } from "./design-tokens";

export function Charts(renderSpec: ChartsRenderSpec) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const duration_frames = renderSpec.duration_frames || 180;
  const unit = renderSpec.props.unit || "";

  // Extract labels and values cleanly (support N bars)
  const isClean = renderSpec.props.labels !== undefined || renderSpec.props.x !== undefined;
  const labels: string[] = isClean
    ? renderSpec.props.labels || renderSpec.props.x || []
    : [renderSpec.props.left?.label || "Left", renderSpec.props.right?.label || "Right"];

  const rawValues: number[] = isClean
    ? renderSpec.props.values || renderSpec.props.y || []
    : [renderSpec.props.left?.value || 0, renderSpec.props.right?.value || 0];

  // If labels or values are empty, fallback safely
  const barLabels = labels.length > 0 ? labels : ["Before", "After"];
  const barValues = rawValues.length > 0 ? rawValues : [50, 100];
  const barCount = Math.max(barLabels.length, barValues.length);

  const maxVal = Math.max(...barValues, 1);

  const barColors = [
    { main: tokens.accent.emerald, glow: "rgba(16, 185, 129, 0.4)", gradient: "linear-gradient(0deg, #047857 0%, #10b981 100%)" },
    { main: tokens.accent.cyan, glow: "rgba(6, 182, 212, 0.4)", gradient: "linear-gradient(0deg, #0e7490 0%, #06b6d4 100%)" },
    { main: tokens.accent.blue, glow: "rgba(59, 130, 246, 0.4)", gradient: "linear-gradient(0deg, #1d4ed8 0%, #3b82f6 100%)" },
    { main: tokens.accent.purple, glow: "rgba(168, 85, 247, 0.4)", gradient: "linear-gradient(0deg, #7e22ce 0%, #a855f7 100%)" },
  ];

  return (
    <AbsoluteFill
      style={{
        background: tokens.bg.base,
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
        }}
      >
        <header>
          <div
            style={{
              color: tokens.accent.emerald,
              fontSize: tokens.font.eyebrow,
              fontWeight: 800,
              textTransform: "uppercase",
              letterSpacing: 2,
            }}
          >
            {renderSpec.props.headerLabel || "DATA BREAKDOWN"}
          </div>
          {renderSpec.props.title && (
            <div
              style={{
                fontSize: 54,
                fontWeight: 900,
                marginTop: 16,
                lineHeight: 1.1,
              }}
            >
              {renderSpec.props.title}
            </div>
          )}
        </header>

        <main
          style={{
            display: "flex",
            justifyContent: "center",
            alignItems: "flex-end",
            flex: 1,
            gap: barCount > 2 ? "60px" : "120px",
            borderBottom: "3px solid rgba(255, 255, 255, 0.15)",
            paddingBottom: "30px",
            margin: "40px 0 20px",
          }}
        >
          {Array.from({ length: barCount }).map((_, idx) => {
            const val = barValues[idx] ?? 0;
            const label = barLabels[idx] ?? `Item ${idx + 1}`;
            const targetHeightPct = (val / maxVal) * 80;

            const delay = Math.round((duration_frames * 0.3 * idx) / Math.max(1, barCount - 1));
            const barSpring = interpolate(
              frame,
              [delay, delay + Math.round(duration_frames * 0.4)],
              [0, 1],
              { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.bezier(0.16, 1, 0.3, 1) }
            );

            const colorTheme = barColors[idx % barColors.length];

            return (
              <div
                key={idx}
                style={{
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "center",
                  width: barCount > 3 ? "140px" : "180px",
                  height: "100%",
                  justifyContent: "flex-end",
                }}
              >
                {/* Numeric Value Label above bar */}
                <div
                  style={{
                    fontSize: 36,
                    fontWeight: 950,
                    color: colorTheme.main,
                    marginBottom: 16,
                    opacity: barSpring,
                  }}
                >
                  {val.toLocaleString()} {unit}
                </div>

                {/* Animated Growing Bar */}
                <div
                  style={{
                    width: "100%",
                    height: `${targetHeightPct * barSpring}%`,
                    minHeight: "8px",
                    background: colorTheme.gradient,
                    borderRadius: "12px 12px 0 0",
                    boxShadow: `0 0 30px ${colorTheme.glow}`,
                  }}
                />

                {/* Category X-Axis Label */}
                <div
                  style={{
                    marginTop: 20,
                    fontSize: 22,
                    fontWeight: 800,
                    color: tokens.text.secondary,
                    textAlign: "center",
                    textTransform: "uppercase",
                    letterSpacing: 1,
                  }}
                >
                  {label}
                </div>
              </div>
            );
          })}
        </main>

        {renderSpec.props.footerLabel ? (
          <footer style={{ textAlign: "center", fontSize: 24, color: tokens.text.muted, fontWeight: 600 }}>
            {renderSpec.props.footerLabel}
          </footer>
        ) : null}
      </div>
    </AbsoluteFill>
  );
}
