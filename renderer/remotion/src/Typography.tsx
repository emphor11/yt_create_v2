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
  const text = renderSpec.props.text || renderSpec.props.left?.raw || renderSpec.props.left?.label || "";
  const subtitle = renderSpec.props.subtitle || renderSpec.props.right?.raw || "";

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
            {renderSpec.props.headerLabel || "KEY INSIGHT"}
          </div>
        </header>

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
              fontSize: 90,
              fontWeight: 950,
              lineHeight: 1.1,
              letterSpacing: -2,
              transform: `scale(${interpolate(titleSpring, [0, 1], [0.92, 1]) * pulse})`,
              opacity: titleSpring,
            }}
          >
            {text}
          </div>
        </main>

        {renderSpec.props.footerLabel ? (
          <footer style={{ fontSize: 24, color: "#71717a", fontWeight: 600 }}>
            {renderSpec.props.footerLabel}
          </footer>
        ) : null}
      </div>
    </AbsoluteFill>
  );
}
