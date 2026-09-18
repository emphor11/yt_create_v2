import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { type IconAnimationRenderSpec } from "./types";
import { tokens } from "./design-tokens";
import { safeSpringDelay } from "./animation-safety";

export function IconAnimation(renderSpec: IconAnimationRenderSpec | any) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const props = renderSpec?.props ? renderSpec.props : renderSpec || {};
  const duration_frames: number =
    renderSpec?.duration_frames ||
    renderSpec?.durationInFrames ||
    renderSpec?.props?.duration_frames ||
    240;

  // Extract exact component properties with backward-compatible fallbacks
  const headerLabel = props.headerLabel || "";
  const icon = props.icon || "💡";
  const label = props.label || props.text || props.title || "";
  const footerLabel = props.footerLabel || "";

  // ─────────────────────────────────────────────────────────────────────────
  // PHASE 1 — ICON ENTRANCE (0 → ~20% D)
  // Clean spring entrance with subtle scale & fade.
  // ─────────────────────────────────────────────────────────────────────────
  const iconDelay = safeSpringDelay(0, duration_frames, 0.08);
  const iconSpring = spring({
    frame: Math.max(0, frame - iconDelay),
    fps,
    config: { damping: 14, stiffness: 120 },
  });

  const headerDelay = safeSpringDelay(0, duration_frames, 0.08);
  const headerSpring = spring({
    frame: Math.max(0, frame - headerDelay),
    fps,
    config: { damping: 16, stiffness: 110 },
  });

  // ─────────────────────────────────────────────────────────────────────────
  // PHASE 2 — ONE-SHOT IMPACT GLOW BLOOM (18% D → 40% D)
  // Single expansion bloom that settles into resting glow (NO infinite oscillation).
  // ─────────────────────────────────────────────────────────────────────────
  const glowDelay = safeSpringDelay(
    Math.floor(duration_frames * 0.18),
    duration_frames,
    0.3
  );
  const glowSpring = spring({
    frame: Math.max(0, frame - glowDelay),
    fps,
    config: { damping: 14, stiffness: 90 },
  });

  const glowScale = interpolate(glowSpring, [0, 0.7, 1], [0.8, 1.25, 1.08], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const glowOpacity = interpolate(glowSpring, [0, 0.5, 1], [0, 0.35, 0.22], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // ─────────────────────────────────────────────────────────────────────────
  // PHASE 3 — CONCEPT LABEL REVEAL (35% D → 60% D)
  // Text label slides up and fades in after icon is anchored.
  // ─────────────────────────────────────────────────────────────────────────
  const labelDelay = safeSpringDelay(
    Math.floor(duration_frames * 0.35),
    duration_frames,
    0.55
  );
  const labelSpring = spring({
    frame: Math.max(0, frame - labelDelay),
    fps,
    config: { damping: 16, stiffness: 100 },
  });

  const footerDelay = safeSpringDelay(
    Math.floor(duration_frames * 0.55),
    duration_frames,
    0.75
  );
  const footerSpring = spring({
    frame: Math.max(0, frame - footerDelay),
    fps,
    config: { damping: 18, stiffness: 90 },
  });

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
          <header
            style={{
              opacity: headerSpring,
              transform: `translateY(${(1 - headerSpring) * -10}px)`,
            }}
          >
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
              transform: `scale(${0.85 + iconSpring * 0.15})`,
              opacity: iconSpring,
            }}
          >
            {/* Outer Glow Ring — One-shot bloom, settles cleanly */}
            <div
              style={{
                position: "absolute",
                top: 0,
                left: "50%",
                transform: `translateX(-50%) scale(${glowScale})`,
                width: "200px",
                height: "200px",
                borderRadius: "44px",
                background: "rgba(168, 85, 247, 0.25)",
                filter: "blur(16px)",
                opacity: glowOpacity,
                zIndex: 0,
              }}
            />

            {/* Core Icon Box */}
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
                boxShadow: `0 0 50px rgba(168, 85, 247, ${0.25 + glowSpring * 0.2})`,
                backdropFilter: "blur(12px)",
                zIndex: 1,
              }}
            >
              {icon}
            </div>

            {/* Phase 3: Concept Label */}
            {label ? (
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
                  opacity: labelSpring,
                  transform: `translateY(${(1 - labelSpring) * 16}px)`,
                }}
              >
                {label}
              </div>
            ) : null}
          </div>
        </main>

        {footerLabel ? (
          <footer
            style={{
              textAlign: "center",
              fontSize: 24,
              color: tokens.text.muted,
              fontWeight: 600,
              opacity: footerSpring,
            }}
          >
            {footerLabel}
          </footer>
        ) : null}
      </div>
    </AbsoluteFill>
  );
}
