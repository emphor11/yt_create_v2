import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

import { type SplitComparisonRenderSpec } from "./types";
import { tokens } from "./design-tokens";

export function SplitComparison(renderSpec: SplitComparisonRenderSpec) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const props = renderSpec.props as any;

  // Extract exact component properties
  const headerLabel = props.headerLabel || "";
  const leftRole = props.leftRole || "";
  const leftLabel = props.leftLabel || "";
  const leftRawVal = props.leftValue !== undefined ? String(props.leftValue) : "0";
  const leftUnit = props.leftUnit || "";

  const rightRole = props.rightRole || "";
  const rightLabel = props.rightLabel || "";
  const rightRawVal = props.rightValue !== undefined ? String(props.rightValue) : "0";
  const rightUnit = props.rightUnit || "";

  // Synchronized entrance animation for both cards simultaneously
  const entranceSpring = spring({
    frame,
    fps,
    config: { damping: 18, stiffness: 110 },
  });
  const entranceOpacity = interpolate(frame, [0, 15], [0, 1], {
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill
      style={{
        background: tokens.bg.base,
        backdropFilter: "blur(4px)",
        color: tokens.text.primary,
        fontFamily: tokens.font.family,
        overflow: "hidden",
      }}
    >
      {/* Background Grid Accent */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background:
            "linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px), linear-gradient(0deg, rgba(255,255,255,0.02) 1px, transparent 1px)",
          backgroundSize: "96px 96px",
        }}
      />
      <div
        style={{
          position: "relative",
          display: "grid",
          gridTemplateRows: "auto 1fr auto",
          height: "100%",
          padding: tokens.spacing.padding,
        }}
      >
        {headerLabel ? (
          <header>
            <div
              style={{
                color: tokens.accent.cyan,
                fontSize: tokens.font.eyebrow,
                fontWeight: 800,
                letterSpacing: 2,
                textTransform: "uppercase",
              }}
            >
              {headerLabel}
            </div>
          </header>
        ) : null}

        <main
          style={{
            alignItems: "center",
            display: "grid",
            gap: 40,
            gridTemplateColumns: "1fr 1fr",
            marginTop: headerLabel ? 32 : 0,
          }}
        >
          {/* Left Panel - Dark Glass Red Accent */}
          <section
            style={{
              border: "2px solid rgba(244, 63, 94, 0.35)",
              borderRadius: 16,
              background: tokens.bg.cardLeft,
              boxShadow: "0 24px 70px rgba(0, 0, 0, 0.5)",
              minHeight: 420,
              opacity: entranceOpacity,
              padding: 44,
              display: "flex",
              flexDirection: "column",
              justifyContent: "space-between",
              transform: `translateY(${(1 - entranceSpring) * 40}px)`,
              backdropFilter: "blur(8px)",
            }}
          >
            <div>
              {leftRole ? (
                <div
                  style={{
                    color: tokens.accent.rose,
                    fontSize: 28,
                    fontWeight: 900,
                    textTransform: "uppercase",
                    letterSpacing: 1.5,
                  }}
                >
                  {leftRole}
                </div>
              ) : null}
              {leftLabel ? (
                <div style={{ color: tokens.text.secondary, fontSize: 22, marginTop: 6, fontWeight: 600 }}>
                  {leftLabel}
                </div>
              ) : null}
            </div>
            <div
              style={{
                color: tokens.accent.rose,
                fontSize: 104,
                fontWeight: 950,
                lineHeight: 1,
                marginTop: 36,
                textShadow: "0 0 30px rgba(244, 63, 94, 0.3)",
              }}
            >
              {leftRawVal}
              {leftUnit ? (
                <span style={{ fontSize: 44, marginLeft: 10, color: tokens.text.secondary }}>
                  {leftUnit}
                </span>
              ) : null}
            </div>
          </section>

          {/* Right Panel - Dark Glass Emerald Accent */}
          <section
            style={{
              border: "2px solid rgba(16, 185, 129, 0.35)",
              borderRadius: 16,
              background: tokens.bg.cardRight,
              boxShadow: "0 24px 70px rgba(0, 0, 0, 0.5)",
              minHeight: 420,
              opacity: entranceOpacity,
              padding: 44,
              display: "flex",
              flexDirection: "column",
              justifyContent: "space-between",
              transform: `translateY(${(1 - entranceSpring) * 40}px)`,
              backdropFilter: "blur(8px)",
            }}
          >
            <div>
              {rightRole ? (
                <div
                  style={{
                    color: tokens.accent.emerald,
                    fontSize: 28,
                    fontWeight: 900,
                    textTransform: "uppercase",
                    letterSpacing: 1.5,
                  }}
                >
                  {rightRole}
                </div>
              ) : null}
              {rightLabel ? (
                <div style={{ color: tokens.text.secondary, fontSize: 22, marginTop: 6, fontWeight: 600 }}>
                  {rightLabel}
                </div>
              ) : null}
            </div>
            <div
              style={{
                color: tokens.accent.emerald,
                fontSize: 104,
                fontWeight: 950,
                lineHeight: 1,
                marginTop: 36,
                textShadow: "0 0 30px rgba(16, 185, 129, 0.3)",
              }}
            >
              {rightRawVal}
              {rightUnit ? (
                <span style={{ fontSize: 44, marginLeft: 10, color: tokens.text.secondary }}>
                  {rightUnit}
                </span>
              ) : null}
            </div>
          </section>
        </main>

        {renderSpec.props.footerLabel ? (
          <footer
            style={{
              alignItems: "center",
              color: tokens.text.muted,
              display: "flex",
              fontSize: 26,
              fontWeight: 700,
              justifyContent: "center",
            }}
          >
            <span>{renderSpec.props.footerLabel}</span>
          </footer>
        ) : null}
      </div>
    </AbsoluteFill>
  );
}
