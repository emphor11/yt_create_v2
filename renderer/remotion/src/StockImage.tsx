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

  const props = renderSpec.props as any;
  const headerLabel = props.headerLabel || "";
  const text = props.text || "";

  const imgSpring = spring({
    frame,
    fps,
    config: { damping: 24, stiffness: 60 },
  });

  return (
    <AbsoluteFill
      style={{
        background: "transparent",
        color: tokens.text.primary,
        fontFamily: tokens.font.family,
        overflow: "hidden",
      }}
    >
      {/* Subtle bottom gradient if text is present */}
      {text ? (
        <div
          style={{
            position: "absolute",
            inset: 0,
            background: "linear-gradient(180deg, rgba(0,0,0,0.35) 0%, rgba(0,0,0,0.05) 45%, rgba(0,0,0,0.75) 100%)",
            pointerEvents: "none",
          }}
        />
      ) : null}

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
        {headerLabel ? (
          <header>
            <div
              style={{
                display: "inline-block",
                background: "rgba(0, 0, 0, 0.65)",
                border: "1px solid rgba(6, 182, 212, 0.4)",
                borderRadius: "9999px",
                padding: "8px 18px",
                color: tokens.accent.cyan,
                fontSize: tokens.font.eyebrow,
                fontWeight: 800,
                textTransform: "uppercase",
                letterSpacing: 2,
                backdropFilter: "blur(8px)",
              }}
            >
              {headerLabel}
            </div>
          </header>
        ) : null}

        {text ? (
          <footer
            style={{
              transform: `translateY(${(1 - imgSpring) * 20}px)`,
              opacity: imgSpring,
            }}
          >
            <div
              style={{
                background: "rgba(15, 23, 42, 0.85)",
                border: "1px solid rgba(6, 182, 212, 0.4)",
                borderRadius: "16px",
                padding: "24px 36px",
                backdropFilter: "blur(12px)",
                boxShadow: "0 20px 50px rgba(0, 0, 0, 0.6)",
                maxWidth: "92%",
              }}
            >
              <div style={{ fontSize: 52, fontWeight: 950, color: tokens.text.primary, lineHeight: 1.2 }}>
                {text}
              </div>
            </div>
          </footer>
        ) : null}
      </div>
    </AbsoluteFill>
  );
}
