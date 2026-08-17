import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { type StockImageRenderSpec } from "./types";
import { tokens } from "./design-tokens";

export function StockImage(renderSpec: StockImageRenderSpec) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const duration_frames = renderSpec.duration_frames || 180;
  const isClean = renderSpec.props.text !== undefined;
  const headlineText = isClean ? renderSpec.props.text : (renderSpec.props.left?.raw || renderSpec.props.left?.label || "");

  const imgSpring = spring({
    frame,
    fps,
    config: { damping: 24, stiffness: 60 },
  });

  // Ken Burns zoom effect across scene duration (1.0 -> 1.08 scale)
  const kenBurnsScale = interpolate(frame, [0, duration_frames], [1.0, 1.08], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

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
      {/* Background Image with Ken Burns zoom effect */}
      <img
        src="https://images.unsplash.com/photo-1560518883-ce09059eeffa?auto=format&fit=crop&w=1920&q=80"
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
          opacity: 0.35 * imgSpring,
          transform: `scale(${kenBurnsScale})`,
        }}
        alt="Stock background"
      />

      {/* Radial vignette overlay */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: "radial-gradient(circle, transparent 40%, rgba(9,9,11,0.85) 100%)",
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
              color: tokens.accent.cyan,
              fontSize: tokens.font.eyebrow,
              fontWeight: 800,
              textTransform: "uppercase",
              letterSpacing: 2,
            }}
          >
            {renderSpec.props.headerLabel || "VISUAL CONTEXT"}
          </div>
          {renderSpec.props.title && (
            <div style={{ fontSize: 54, fontWeight: 900, marginTop: 16, color: tokens.text.primary }}>
              {renderSpec.props.title}
            </div>
          )}
        </header>

        <main style={{ display: "flex", gap: "40px", marginTop: "40px" }}>
          <div
            style={{
              background: "rgba(15, 23, 42, 0.80)",
              border: "1px solid rgba(6, 182, 212, 0.3)",
              borderRadius: "16px",
              padding: "44px",
              flex: 1,
              backdropFilter: "blur(12px)",
              transform: `translateY(${(1 - imgSpring) * 30}px)`,
              opacity: imgSpring,
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
