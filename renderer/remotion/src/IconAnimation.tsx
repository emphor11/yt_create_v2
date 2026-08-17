import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { type IconAnimationRenderSpec } from "./types";
import { tokens } from "./design-tokens";

export function IconAnimation(renderSpec: IconAnimationRenderSpec) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const isClean = renderSpec.props.text !== undefined;
  const headlineText = isClean ? renderSpec.props.text : (renderSpec.props.left?.raw || renderSpec.props.left?.label || "");

  const iconSpring = spring({
    frame,
    fps,
    config: { damping: 12, stiffness: 130 },
  });

  const glowPulse = Math.sin(frame * 0.08) * 0.08 + 1;

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
              color: tokens.accent.purple,
              fontSize: tokens.font.eyebrow,
              fontWeight: 800,
              textTransform: "uppercase",
              letterSpacing: 2,
            }}
          >
            {renderSpec.props.headerLabel || "ICON CONCEPT"}
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
            flexDirection: "column",
            justifyContent: "center",
            alignItems: "center",
            flex: 1,
          }}
        >
          {/* Main Icon Block with radiating glow ring */}
          <div
            style={{
              position: "relative",
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              transform: `scale(${iconSpring})`,
              opacity: iconSpring,
            }}
          >
            {/* Outer Glow Ring */}
            <div
              style={{
                position: "absolute",
                top: 0,
                left: "50%",
                transform: `translateX(-50%) scale(${glowPulse * 1.18})`,
                width: "200px",
                height: "200px",
                borderRadius: "44px",
                background: "rgba(168, 85, 247, 0.25)",
                filter: "blur(16px)",
                zIndex: 0,
              }}
            />

            <div
              style={{
                position: "relative",
                width: "200px",
                height: "200px",
                borderRadius: "40px",
                background: "rgba(15, 23, 42, 0.85)",
                border: "2px solid rgba(168, 85, 247, 0.6)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: 90,
                boxShadow: "0 0 50px rgba(168, 85, 247, 0.4)",
                backdropFilter: "blur(12px)",
                zIndex: 1,
              }}
            >
              {renderSpec.props.icon || "💡"}
            </div>

            <div
              style={{
                marginTop: 36,
                fontSize: 48,
                fontWeight: 950,
                color: tokens.text.primary,
                textAlign: "center",
                maxWidth: "900px",
                lineHeight: 1.2,
                zIndex: 1,
              }}
            >
              {headlineText}
            </div>
          </div>
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
