import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { type TypographyRenderSpec } from "./types";
import { tokens } from "./design-tokens";

export function Typography(renderSpec: TypographyRenderSpec) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const duration_frames = renderSpec.duration_frames || 180;
  const props = renderSpec.props as any;

  // Extract exact component properties
  const headerLabel = props.headerLabel || "";
  const text = props.text || "";
  const subtitle = props.subtitle || "";
  const footerLabel = props.footerLabel || "";

  const titleSpring = spring({
    frame,
    fps,
    config: { damping: 14, stiffness: 120 },
  });

  // Living motion pulse for long scene holds
  const pulse = 1 + Math.sin((frame / duration_frames) * Math.PI * 2) * 0.015;

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
        {headerLabel ? (
          <header>
            <div
              style={{
                color: tokens.accent.rose,
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
            alignItems: "flex-start",
            justifyContent: "center",
            flex: 1,
          }}
        >
          <div
            style={{
              fontSize: 84,
              fontWeight: 950,
              lineHeight: 1.1,
              letterSpacing: -2,
              transform: `scale(${interpolate(titleSpring, [0, 1], [0.92, 1]) * pulse})`,
              opacity: titleSpring,
            }}
          >
            {text}
          </div>
          {subtitle && (
            <div
              style={{
                fontSize: 34,
                fontWeight: 500,
                color: tokens.text.secondary,
                marginTop: 24,
                lineHeight: 1.35,
                maxWidth: "1200px",
                opacity: titleSpring,
              }}
            >
              {subtitle}
            </div>
          )}
        </main>

        {footerLabel ? (
          <footer style={{ fontSize: 24, color: "#71717a", fontWeight: 600 }}>
            {footerLabel}
          </footer>
        ) : null}
      </div>
    </AbsoluteFill>
  );
}
