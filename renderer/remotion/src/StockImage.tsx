import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { type StockImageRenderSpec } from "./types";
import { tokens } from "./design-tokens";
import { safeSpringDelay } from "./animation-safety";

export function StockImage(renderSpec: StockImageRenderSpec | any) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const props = renderSpec?.props ? renderSpec.props : renderSpec || {};
  const duration_frames: number =
    renderSpec?.duration_frames ||
    renderSpec?.durationInFrames ||
    renderSpec?.props?.duration_frames ||
    240;

  const headerLabel = props.headerLabel || "";
  const text = props.text || props.title || props.label || "";
  const subtitle = props.subtitle || "";

  // ─────────────────────────────────────────────────────────────────────────
  // PHASE 1 — HEADER EYEBROW ENTRANCE (0 → ~10% D)
  // Establishes scene context while viewer registers the underlying image.
  // ─────────────────────────────────────────────────────────────────────────
  const headerDelay = safeSpringDelay(0, duration_frames, 0.08);
  const headerSpring = spring({
    frame: Math.max(0, frame - headerDelay),
    fps,
    config: { damping: 16, stiffness: 110 },
  });

  // ─────────────────────────────────────────────────────────────────────────
  // PHASE 2 — EDITORIAL CAPTION CARD ENTRANCE (10% D → ~35% D)
  // Brief hold allows visual recognition before text slides up smoothly.
  // ─────────────────────────────────────────────────────────────────────────
  const captionNominal = Math.floor(duration_frames * 0.10);
  const captionDelay = safeSpringDelay(captionNominal, duration_frames, 0.25);
  const captionSpring = spring({
    frame: Math.max(0, frame - captionDelay),
    fps,
    config: { damping: 18, stiffness: 85 },
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
            background:
              "linear-gradient(180deg, rgba(0,0,0,0.35) 0%, rgba(0,0,0,0.05) 45%, rgba(0,0,0,0.80) 100%)",
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
          <header
            style={{
              opacity: headerSpring,
              transform: `translateY(${(1 - headerSpring) * -12}px)`,
            }}
          >
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
              transform: `translateY(${(1 - captionSpring) * 24}px)`,
              opacity: captionSpring,
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
              <div
                style={{
                  fontSize: 52,
                  fontWeight: 950,
                  color: tokens.text.primary,
                  lineHeight: 1.2,
                }}
              >
                {text}
              </div>
              {subtitle ? (
                <div
                  style={{
                    fontSize: 24,
                    color: tokens.text.secondary,
                    marginTop: 12,
                    fontWeight: 500,
                  }}
                >
                  {subtitle}
                </div>
              ) : null}
            </div>
          </footer>
        ) : null}
      </div>
    </AbsoluteFill>
  );
}
