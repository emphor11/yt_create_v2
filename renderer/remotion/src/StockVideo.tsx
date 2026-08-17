import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { type StockVideoRenderSpec } from "./types";
import { tokens } from "./design-tokens";

export function StockVideo(renderSpec: StockVideoRenderSpec) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const duration_frames = renderSpec.duration_frames || 180;
  const isClean = renderSpec.props.text !== undefined;
  const headlineText = isClean ? renderSpec.props.text : (renderSpec.props.left?.raw || renderSpec.props.left?.label || "");

  const scaleSpring = spring({
    frame,
    fps,
    config: { damping: 20, stiffness: 70 },
  });

  const pulse = Math.sin(frame * 0.05) * 0.04 + 1;

  return (
    <AbsoluteFill
      style={{
        background: tokens.bg.base,
        backdropFilter: "blur(2px)",
        color: tokens.text.primary,
        fontFamily: tokens.font.family,
        overflow: "hidden",
      }}
    >
      {/* Background ambient lighting circles */}
      <div
        style={{
          position: "absolute",
          top: "50%",
          left: "50%",
          width: "800px",
          height: "800px",
          borderRadius: "50%",
          background: "radial-gradient(circle, rgba(168,85,247,0.2) 0%, transparent 70%)",
          transform: `translate(-50%, -50%) scale(${pulse * scaleSpring})`,
        }}
      />

      <div
        style={{
          position: "absolute",
          inset: 0,
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          padding: tokens.spacing.padding,
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
            {renderSpec.props.headerLabel || "VISUAL FOOTAGE"}
          </div>
          {renderSpec.props.title && (
            <div style={{ fontSize: 54, fontWeight: 900, marginTop: 16, color: tokens.text.primary }}>
              {renderSpec.props.title}
            </div>
          )}
        </header>

        <main style={{ display: "flex", gap: "40px" }}>
          <div
            style={{
              background: "rgba(15, 23, 42, 0.80)",
              border: "1px solid rgba(168, 85, 247, 0.35)",
              borderRadius: "16px",
              padding: "44px",
              flex: 1,
              backdropFilter: "blur(12px)",
              transform: `translateY(${(1 - scaleSpring) * 20}px)`,
              opacity: scaleSpring,
              boxShadow: "0 20px 60px rgba(0, 0, 0, 0.5)",
            }}
          >
            <div style={{ fontSize: 60, fontWeight: 950, color: tokens.text.primary, lineHeight: 1.15 }}>
              {headlineText}
            </div>
          </div>
        </main>

        {renderSpec.props.footerLabel ? (
          <footer style={{ fontSize: 24, color: tokens.text.muted, fontWeight: 600 }}>
            {renderSpec.props.footerLabel}
          </footer>
        ) : null}
      </div>
    </AbsoluteFill>
  );
}
