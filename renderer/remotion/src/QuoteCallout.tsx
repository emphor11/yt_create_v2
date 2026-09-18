import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { type QuoteCalloutProps } from "./types";
import { tokens } from "./design-tokens";
import { safeAnimationWindow, safeSpringDelay } from "./animation-safety";

export function QuoteCallout(props: any) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const resolvedProps: QuoteCalloutProps = props.props ? props.props : props;
  // Read duration_frames from the outer wrapper (standard convention)
  const duration_frames: number =
    (props as any).duration_frames || (props as any).durationInFrames || 180;

  const headerLabel = resolvedProps.headerLabel || "";
  const quoteText =
    resolvedProps.quote ||
    resolvedProps.title ||
    "The best investment you can make is in your own abilities.";
  const authorName = resolvedProps.author || "Industry Expert";
  const authorRole = resolvedProps.role || "";
  const avatarSymbol = resolvedProps.avatar || "💬";
  const footerLabel = resolvedProps.footerLabel || "";

  // ─────────────────────────────────────────────────────────────────────────
  // PHASE 1 — CARD FRAME (0 → ~12% D)
  // Card border + background scales in. The quote area is empty at this point
  // because words haven't started revealing yet.
  // ─────────────────────────────────────────────────────────────────────────
  const cardDelay = safeSpringDelay(0, duration_frames, 0.08);
  const cardSpring = spring({
    frame: Math.max(0, frame - cardDelay),
    fps,
    config: { damping: 14, stiffness: 90 },
  });

  // ─────────────────────────────────────────────────────────────────────────
  // PHASE 2 — QUOTE WORD-BY-WORD REVEAL (10% D → 58% D)
  // Each word fades+lifts in sequentially. The reveal window is
  // duration-safe via safeAnimationWindow. The viewer reads the quote
  // as it builds, not all at once.
  // ─────────────────────────────────────────────────────────────────────────
  const words = quoteText.trim().split(/\s+/);
  const wordCount = Math.max(1, words.length);

  // Text reveal window: starts at ~10% D, ends at ~58% D (duration-safe)
  const textRevealStart = Math.max(
    safeSpringDelay(4, duration_frames, 0.08), // never before card starts settling
    Math.floor(duration_frames * 0.10)
  );
  const textRevealEnd = Math.min(
    Math.floor(duration_frames * 0.58),
    duration_frames - 2
  );

  // Clamp so window is always strictly increasing
  const [safeTextStart, safeTextEnd] = safeAnimationWindow(
    textRevealStart,
    Math.max(textRevealStart + wordCount, textRevealEnd),
    duration_frames,
    wordCount
  );

  const framesPerWord = Math.max(
    0.5,
    (safeTextEnd - safeTextStart) / wordCount
  );

  // ─────────────────────────────────────────────────────────────────────────
  // PHASE 3 — AUTHOR / ATTRIBUTION (65% D)
  // Author row slides up after the quote has been fully revealed.
  // Duration-safe delay.
  // ─────────────────────────────────────────────────────────────────────────
  const authorDelay = safeSpringDelay(
    Math.floor(duration_frames * 0.65),
    duration_frames,
    0.78
  );
  const authorSpring = spring({
    frame: Math.max(0, frame - authorDelay),
    fps,
    config: { damping: 15, stiffness: 100 },
  });

  // Font size based on quote length (unchanged from original)
  const quoteFontSize =
    quoteText.length > 100 ? 32 : quoteText.length > 60 ? 38 : 46;

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
        {/* Header Eyebrow (unchanged) */}
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
          {/* ── PHASE 1 + 2: Main Quote Card ─────────────────────────────── */}
          <div
            style={{
              position: "relative",
              width: "100%",
              maxWidth: "1400px",
              background:
                "linear-gradient(135deg, rgba(30, 41, 59, 0.95) 0%, rgba(15, 23, 42, 0.9) 100%)",
              border: `2px solid ${tokens.accent.blue}`,
              borderRadius: "24px",
              padding: "48px 56px",
              boxShadow: "0 20px 50px rgba(59, 130, 246, 0.2)",
              backdropFilter: "blur(12px)",
              overflow: "hidden",
              // Card frame entrance (Phase 1)
              opacity: cardSpring,
              transform: `scale(${0.92 + cardSpring * 0.08}) translateY(${
                (1 - cardSpring) * 30
              }px)`,
            }}
          >
            {/* Watermark Quote Icon (unchanged, purely decorative) */}
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
              "
            </div>

            {/* ── PHASE 2: Word-by-Word Quote Reveal ───────────────────── */}
            <div
              style={{
                position: "relative",
                fontSize: quoteFontSize,
                fontWeight: 800,
                color: "#ffffff",
                lineHeight: 1.4,
                letterSpacing: -0.5,
                fontStyle: "italic",
                marginBottom: 32,
                // Wrap words so they flow naturally
                display: "flex",
                flexWrap: "wrap",
                gap: "0.28em",
                alignItems: "baseline",
              }}
            >
              {/* Opening quote mark — appears with first word */}
              <span
                style={{
                  opacity: interpolate(
                    frame,
                    [safeTextStart, safeTextStart + 3],
                    [0, 1],
                    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
                  ),
                }}
              >
                "
              </span>

              {words.map((word, idx) => {
                const wordStart = safeTextStart + idx * framesPerWord;
                const wordEnd = wordStart + Math.min(3, framesPerWord);
                const wordOpacity = interpolate(
                  frame,
                  [wordStart, Math.max(wordStart + 0.5, wordEnd)],
                  [0, 1],
                  { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
                );
                const wordY = interpolate(
                  frame,
                  [wordStart, Math.max(wordStart + 0.5, wordEnd)],
                  [8, 0],
                  { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
                );
                return (
                  <span
                    key={idx}
                    style={{
                      display: "inline-block",
                      opacity: wordOpacity,
                      transform: `translateY(${wordY}px)`,
                    }}
                  >
                    {word}
                  </span>
                );
              })}

              {/* Closing quote mark — appears with last word */}
              <span
                style={{
                  opacity: interpolate(
                    frame,
                    [
                      safeTextStart + (wordCount - 1) * framesPerWord,
                      Math.min(
                        safeTextStart + (wordCount - 1) * framesPerWord + 3,
                        duration_frames - 1
                      ),
                    ],
                    [0, 1],
                    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
                  ),
                }}
              >
                "
              </span>
            </div>

            {/* ── PHASE 3: Author Meta Row ──────────────────────────────── */}
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
              {/* Avatar Emoji Circle (unchanged) */}
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

              {/* Author & Role (unchanged) */}
              <div>
                <div
                  style={{
                    fontSize: 24,
                    fontWeight: 900,
                    color: tokens.text.primary,
                  }}
                >
                  {authorName}
                </div>
                {authorRole ? (
                  <div
                    style={{
                      fontSize: 18,
                      color: tokens.text.secondary,
                      fontWeight: 500,
                      marginTop: 2,
                    }}
                  >
                    {authorRole}
                  </div>
                ) : null}
              </div>
            </div>
          </div>
        </main>

        {footerLabel ? (
          <footer
            style={{
              textAlign: "center",
              fontSize: 22,
              color: tokens.text.muted,
              fontWeight: 600,
            }}
          >
            {footerLabel}
          </footer>
        ) : null}
      </div>
    </AbsoluteFill>
  );
}
