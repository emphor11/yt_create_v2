import {
  AbsoluteFill,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { type QuoteCalloutProps } from "./types";
import { tokens } from "./design-tokens";

export function QuoteCallout(props: any) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const resolvedProps: QuoteCalloutProps = props.props ? props.props : props;

  const headerLabel = resolvedProps.headerLabel || "";
  const quoteText = resolvedProps.quote || resolvedProps.title || "The best investment you can make is in your own abilities.";
  const authorName = resolvedProps.author || "Industry Expert";
  const authorRole = resolvedProps.role || "";
  const avatarSymbol = resolvedProps.avatar || "💬";
  const footerLabel = resolvedProps.footerLabel || "";

  // Springs for staggered entrance
  const cardSpring = spring({
    frame,
    fps,
    config: { damping: 14, stiffness: 90 },
  });

  const authorSpring = spring({
    frame: Math.max(0, frame - 15),
    fps,
    config: { damping: 15, stiffness: 100 },
  });

  const quoteFontSize = quoteText.length > 100 ? 32 : quoteText.length > 60 ? 38 : 46;

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
          position: "relative",
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
                color: tokens.accent.blue,
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
            position: "relative",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            flex: 1,
            margin: "24px 0",
          }}
        >
          {/* Main Quote Card */}
          <div
            style={{
              position: "relative",
              width: "100%",
              maxWidth: "1400px",
              background: "linear-gradient(135deg, rgba(30, 41, 59, 0.95) 0%, rgba(15, 23, 42, 0.9) 100%)",
              border: `2px solid ${tokens.accent.blue}`,
              borderRadius: "24px",
              padding: "48px 56px",
              boxShadow: "0 20px 50px rgba(59, 130, 246, 0.2)",
              backdropFilter: "blur(12px)",
              overflow: "hidden",
              opacity: cardSpring,
              transform: `scale(${0.92 + cardSpring * 0.08}) translateY(${(1 - cardSpring) * 30}px)`,
            }}
          >
            {/* Watermark Quote Icon */}
            <div
              style={{
                position: "absolute",
                top: "-30px",
                right: "30px",
                fontSize: "220px",
                fontWeight: 900,
                color: tokens.accent.blue,
                opacity: 0.08,
                lineHeight: 1,
                userSelect: "none",
                pointerEvents: "none",
              }}
            >
              “
            </div>

            {/* Quote Body Text */}
            <div
              style={{
                position: "relative",
                fontSize: quoteFontSize,
                fontWeight: 800,
                color: "#ffffff",
                lineHeight: 1.3,
                letterSpacing: -0.5,
                fontStyle: "italic",
                marginBottom: 32,
              }}
            >
              “{quoteText}”
            </div>

            {/* Author Meta Row */}
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: "20px",
                borderTop: "1px solid rgba(255, 255, 255, 0.1)",
                paddingTop: 24,
                opacity: authorSpring,
                transform: `translateY(${(1 - authorSpring) * 15}px)`,
              }}
            >
              {/* Avatar Emoji Circle */}
              <div
                style={{
                  width: "56px",
                  height: "56px",
                  borderRadius: "50%",
                  background: "rgba(59, 130, 246, 0.2)",
                  border: `2px solid ${tokens.accent.blue}`,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: 26,
                  flexShrink: 0,
                }}
              >
                {avatarSymbol}
              </div>

              {/* Author & Role */}
              <div>
                <div style={{ fontSize: 24, fontWeight: 900, color: tokens.text.primary }}>
                  {authorName}
                </div>
                {authorRole ? (
                  <div style={{ fontSize: 18, color: tokens.text.secondary, fontWeight: 500, marginTop: 2 }}>
                    {authorRole}
                  </div>
                ) : null}
              </div>
            </div>
          </div>
        </main>

        {footerLabel ? (
          <footer style={{ textAlign: "center", fontSize: 22, color: tokens.text.muted, fontWeight: 600 }}>
            {footerLabel}
          </footer>
        ) : null}
      </div>
    </AbsoluteFill>
  );
}
