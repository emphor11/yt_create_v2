import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { type TypographyProps } from "./types";
import { tokens } from "./design-tokens";
import { safeSpringDelay } from "./animation-safety";

/**
 * Helper to highlight a specific keyword or phrase within a text string
 */
function renderHighlightedText(
  fullText: string,
  highlightStr: string | undefined,
  accentColor: string,
  baseFontSize: number,
  highlightSpring: number
) {
  if (!highlightStr || !highlightStr.trim()) {
    return fullText;
  }

  const strToMatch = highlightStr.trim();
  const lowerFull = fullText.toLowerCase();
  const lowerMatch = strToMatch.toLowerCase();

  const matchIdx = lowerFull.indexOf(lowerMatch);
  if (matchIdx === -1) {
    return fullText;
  }

  const before = fullText.slice(0, matchIdx);
  const matchedText = fullText.slice(matchIdx, matchIdx + strToMatch.length);
  const after = fullText.slice(matchIdx + strToMatch.length);

  return (
    <>
      {before}
      <span
        style={{
          display: "inline-block",
          color: "#ffffff",
          background: `${accentColor}25`,
          border: `1.5px solid ${accentColor}88`,
          padding: "2px 14px",
          borderRadius: "12px",
          margin: "0 4px",
          boxShadow: `0 4px 15px ${accentColor}${Math.round(highlightSpring * 51).toString(16).padStart(2, "0")}`,
          transform: `scale(${0.96 + highlightSpring * 0.04})`,
        }}
      >
        {matchedText}
      </span>
      {after}
    </>
  );
}

export function Typography(props: TypographyProps | any) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Normalize boundary props wrapper
  const resolvedProps: TypographyProps = props.props
    ? props.props
    : props.text
    ? props
    : (props as any).renderSpec?.props || props;

  const duration_frames: number =
    (props as any).duration_frames ||
    (props as any).durationInFrames ||
    (props as any).renderSpec?.duration_frames ||
    180;

  const headerLabel = resolvedProps.headerLabel || "";
  const text = resolvedProps.text || resolvedProps.title || "";
  const subtitle = resolvedProps.subtitle || "";
  const footerLabel = resolvedProps.footerLabel || "";
  const highlight = resolvedProps.highlight || "";
  const val = resolvedProps.value || "";
  const author = resolvedProps.author || "";

  // Variant & Align Auto-Detection
  let variant = resolvedProps.variant || "headline";
  if (!resolvedProps.variant) {
    if (text.trim().endsWith("?")) variant = "question";
    else if (text.trim().startsWith('"') || text.trim().startsWith("'")) variant = "quote";
    else if (val) variant = "metric";
  }

  const isCentered =
    resolvedProps.align === "center" ||
    (!resolvedProps.align && (variant === "question" || variant === "metric"));

  // ─────────────────────────────────────────────────────────────────────────
  // DURATION-SAFE PROGRESSIVE SPRINGS
  // ─────────────────────────────────────────────────────────────────────────

  // Phase 1: Header eyebrow (0% D)
  const headerDelay = safeSpringDelay(0, duration_frames, 0.08);
  const headerSpring = spring({
    frame: Math.max(0, frame - headerDelay),
    fps,
    config: { damping: 15, stiffness: 100 },
  });

  // Phase 1 (for metric): giant number enters first
  const metricDelay = safeSpringDelay(0, duration_frames, 0.08);
  const metricSpring = spring({
    frame: Math.max(0, frame - metricDelay),
    fps,
    config: { damping: 14, stiffness: 120 },
  });

  // Phase 2: Main editorial text
  // For standard headline: starts near beginning (~8% D)
  // For metric variant: enters as explanatory context after the number is established (~20% D)
  const mainNominal = variant === "metric" && val ? Math.floor(duration_frames * 0.20) : 8;
  const mainDelay = safeSpringDelay(
    mainNominal,
    duration_frames,
    variant === "metric" ? 0.35 : 0.18
  );
  const mainSpring = spring({
    frame: Math.max(0, frame - mainDelay),
    fps,
    config: { damping: 14, stiffness: 95 },
  });

  // Phase 2b: Highlight emphasis (activates after text has entered)
  const highlightNominal = mainNominal + Math.max(6, Math.floor(duration_frames * 0.12));
  const highlightDelay = safeSpringDelay(highlightNominal, duration_frames, 0.45);
  const highlightSpring = spring({
    frame: Math.max(0, frame - highlightDelay),
    fps,
    config: { damping: 12, stiffness: 110 },
  });

  // Phase 3: Subtitle / Author Attribution (~45% D)
  const subtitleDelay = safeSpringDelay(
    Math.floor(duration_frames * 0.45),
    duration_frames,
    0.70
  );
  const subtitleSpring = spring({
    frame: Math.max(0, frame - subtitleDelay),
    fps,
    config: { damping: 15, stiffness: 90 },
  });

  // Phase 3b: Footer attribution / source (~60% D)
  const footerDelay = safeSpringDelay(
    Math.floor(duration_frames * 0.60),
    duration_frames,
    0.80
  );
  const footerSpring = spring({
    frame: Math.max(0, frame - footerDelay),
    fps,
    config: { damping: 16, stiffness: 85 },
  });

  // Variant Accent Color
  const accentColor =
    variant === "question"
      ? "#06b6d4"
      : variant === "quote"
      ? "#f59e0b"
      : variant === "metric"
      ? "#10b981"
      : tokens.accent.blue;

  const baseFontSize =
    variant === "question"
      ? 76
      : variant === "metric"
      ? 64
      : variant === "quote"
      ? 60
      : 78;

  return (
    <AbsoluteFill
      style={{
        background: tokens.bg.base,
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
        {/* Header Eyebrow / Category Badge */}
        {headerLabel ? (
          <header
            style={{
              textAlign: isCentered ? "center" : "left",
              opacity: headerSpring,
              transform: `translateY(${(1 - headerSpring) * -15}px)`,
            }}
          >
            <div
              style={{
                color: accentColor,
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

        {/* Main Editorial Text Body */}
        <main
          style={{
            position: "relative",
            display: "flex",
            flexDirection: "column",
            alignItems: isCentered ? "center" : "flex-start",
            justifyContent: "center",
            textAlign: isCentered ? "center" : "left",
            flex: 1,
            margin: "20px 0",
          }}
        >
          {/* METRIC VARIANT: Giant Number Callout */}
          {variant === "metric" && val ? (
            <div
              style={{
                fontSize: 96,
                fontWeight: 950,
                color: "#ffffff",
                lineHeight: 1,
                letterSpacing: -2,
                marginBottom: 12,
                opacity: metricSpring,
                transform: `scale(${0.92 + metricSpring * 0.08})`,
              }}
            >
              <span
                style={{
                  background: "linear-gradient(135deg, #ffffff 0%, #60a5fa 100%)",
                  WebkitBackgroundClip: "text",
                  WebkitTextFillColor: "transparent",
                }}
              >
                {val}
              </span>
            </div>
          ) : null}

          {/* QUOTE VARIANT: Quotation Mark Watermark */}
          {variant === "quote" ? (
            <div
              style={{
                position: "absolute",
                top: "10%",
                left: isCentered ? "50%" : "0%",
                transform: isCentered ? "translateX(-50%)" : "none",
                fontSize: 140,
                fontFamily: "Georgia, serif",
                color: "rgba(245, 158, 11, 0.12)",
                lineHeight: 0,
                pointerEvents: "none",
              }}
            >
              “
            </div>
          ) : null}

          {/* MAIN HEADLINE / QUESTION / STATEMENT BODY */}
          <div
            style={{
              fontSize: baseFontSize,
              fontWeight: 900,
              lineHeight: 1.15,
              letterSpacing: -1.5,
              color: "#ffffff",
              maxWidth: "1350px",
              opacity: mainSpring,
              transform: `translateY(${(1 - mainSpring) * 20}px)`,
            }}
          >
            {renderHighlightedText(text, highlight, accentColor, baseFontSize, highlightSpring)}
          </div>

          {/* SUBTITLE OR AUTHOR ATTRIBUTION */}
          {subtitle || author ? (
            <div
              style={{
                fontSize: 28,
                fontWeight: 500,
                color: variant === "quote" ? "#f59e0b" : tokens.text.secondary,
                marginTop: 20,
                lineHeight: 1.35,
                maxWidth: "1100px",
                opacity: subtitleSpring,
                transform: `translateY(${(1 - subtitleSpring) * 15}px)`,
              }}
            >
              {author ? `— ${author}` : subtitle}
            </div>
          ) : null}
        </main>

        {/* Footer Attribution / Source */}
        {footerLabel ? (
          <footer
            style={{
              textAlign: isCentered ? "center" : "left",
              fontSize: 18,
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
