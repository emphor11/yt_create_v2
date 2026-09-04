import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { type BeforeAfterProps } from "./types";
import { tokens } from "./design-tokens";

export function BeforeAfter(props: BeforeAfterProps | any) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Normalize boundary props wrapper
  const resolvedProps: BeforeAfterProps = props.props ? props.props : props;
  const duration_frames = (props as any).duration_frames || 180;

  const headerLabel = resolvedProps.headerLabel || "";
  const beforeState = resolvedProps.before || {
    label: "2020",
    title: "Market Cap",
    value: "$50B",
    subtitle: "Niche EV Maker",
  };
  const afterState = resolvedProps.after || {
    label: "2021",
    title: "Market Cap",
    value: "$1.0T",
    subtitle: "Global Mass-Market",
  };

  const delta = resolvedProps.delta || "";
  const deltaLabel = resolvedProps.deltaLabel || "";
  const tone = resolvedProps.tone || "neutral";
  const variant = resolvedProps.variant || (beforeState.value || afterState.value ? "numeric" : "visual");
  const footerLabel = resolvedProps.footerLabel || "";

  // Accent tone colors
  const accentColor =
    tone === "positive"
      ? "#10b981"
      : tone === "negative"
      ? "#ef4444"
      : tokens.accent.blue;

  const deltaColor = tone === "negative" ? "#ef4444" : "#f59e0b";

  // Staggered Sequential Reveal Timeline
  const beforeSpring = spring({
    frame,
    fps,
    config: { damping: 15, stiffness: 100 },
  });

  // Connector draws across 15% -> 45%
  const connectorProgress = interpolate(
    frame,
    [Math.round(duration_frames * 0.15), Math.round(duration_frames * 0.45)],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // AFTER state lands at 45%
  const afterSpring = spring({
    frame: Math.max(0, frame - Math.round(duration_frames * 0.45)),
    fps,
    config: { damping: 14, stiffness: 95 },
  });

  // Delta takeaway reveals at 65%
  const deltaSpring = spring({
    frame: Math.max(0, frame - Math.round(duration_frames * 0.65)),
    fps,
    config: { damping: 12, stiffness: 110 },
  });

  // Visual focus shift: BEFORE state dims softly to 0.55 after transition
  const beforeOpacity = interpolate(
    frame,
    [Math.round(duration_frames * 0.45), Math.round(duration_frames * 0.6)],
    [1, 0.55],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

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
        {/* Header */}
        {headerLabel ? (
          <header>
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

        {/* Main Visible Transformation Track */}
        <main
          style={{
            position: "relative",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            gap: "30px",
            flex: 1,
            margin: "20px 0",
          }}
        >
          {/* BEFORE STATE (Initial Entity Anchor) */}
          <div
            style={{
              flex: 1,
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              textAlign: "center",
              opacity: beforeSpring * beforeOpacity,
              transform: `translateY(${(1 - beforeSpring) * 20}px)`,
              transition: "opacity 0.3s",
            }}
          >
            <div
              style={{
                fontSize: 18,
                fontWeight: 800,
                color: tokens.text.muted,
                textTransform: "uppercase",
                letterSpacing: 1.5,
                marginBottom: 12,
              }}
            >
              {beforeState.label || "BEFORE"}
            </div>

            {beforeState.image ? (
              <div
                style={{
                  width: "100%",
                  height: "220px",
                  borderRadius: "16px",
                  overflow: "hidden",
                  marginBottom: 16,
                  border: "1px solid rgba(255, 255, 255, 0.15)",
                }}
              >
                <img
                  src={beforeState.image}
                  alt={beforeState.title}
                  style={{ width: "100%", height: "100%", objectFit: "cover" }}
                />
              </div>
            ) : null}

            {/* Value / Number */}
            {beforeState.value ? (
              <div
                style={{
                  fontSize: variant === "numeric" ? 72 : 48,
                  fontWeight: 950,
                  color: "#ffffff",
                  lineHeight: 1.1,
                  letterSpacing: -1.5,
                  marginBottom: 8,
                }}
              >
                {beforeState.value}
              </div>
            ) : null}

            <div
              style={{
                fontSize: 26,
                fontWeight: 800,
                color: tokens.text.primary,
                marginBottom: 6,
              }}
            >
              {beforeState.title}
            </div>

            {beforeState.subtitle ? (
              <div style={{ fontSize: 20, fontWeight: 500, color: tokens.text.secondary }}>
                {beforeState.subtitle}
              </div>
            ) : null}
          </div>

          {/* CENTRAL DIRECTIONAL CONNECTOR TRACK */}
          <div
            style={{
              width: "280px",
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            {/* Horizontal Arrow Line */}
            <div
              style={{
                position: "relative",
                width: "100%",
                height: "4px",
                background: "rgba(255, 255, 255, 0.15)",
                borderRadius: "2px",
                overflow: "visible",
                marginBottom: 16,
              }}
            >
              {/* Animated Progress Fill */}
              <div
                style={{
                  width: `${connectorProgress * 100}%`,
                  height: "100%",
                  background: accentColor,
                  borderRadius: "2px",
                  boxShadow: `0 0 10px ${accentColor}`,
                }}
              />

              {/* Arrow Head Indicator */}
              <div
                style={{
                  position: "absolute",
                  right: "-2px",
                  top: "-6px",
                  width: "0",
                  height: "0",
                  borderTop: "8px solid transparent",
                  borderBottom: "8px solid transparent",
                  borderLeft: `12px solid ${connectorProgress > 0.9 ? accentColor : "rgba(255,255,255,0.3)"}`,
                  opacity: connectorProgress,
                  transition: "opacity 0.2s",
                }}
              />
            </div>

            {/* Floating Transformation Delta Badge */}
            {delta ? (
              <div
                style={{
                  opacity: deltaSpring,
                  transform: `translateY(${(1 - deltaSpring) * 10}px) scale(${
                    0.9 + deltaSpring * 0.1
                  })`,
                  textAlign: "center",
                }}
              >
                <div
                  style={{
                    display: "inline-block",
                    fontSize: 22,
                    fontWeight: 900,
                    color: deltaColor,
                    background: `${deltaColor}20`,
                    border: `1.5px solid ${deltaColor}`,
                    padding: "4px 18px",
                    borderRadius: "16px",
                    letterSpacing: 1,
                  }}
                >
                  {delta}
                </div>
                {deltaLabel ? (
                  <div style={{ fontSize: 14, color: tokens.text.muted, fontWeight: 700, marginTop: 4 }}>
                    {deltaLabel}
                  </div>
                ) : null}
              </div>
            ) : null}
          </div>

          {/* AFTER STATE (Transformed Entity Outcome) */}
          <div
            style={{
              flex: 1,
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              textAlign: "center",
              opacity: afterSpring,
              transform: `translateY(${(1 - afterSpring) * 20}px) scale(${0.96 + afterSpring * 0.04})`,
            }}
          >
            <div
              style={{
                fontSize: 18,
                fontWeight: 800,
                color: accentColor,
                textTransform: "uppercase",
                letterSpacing: 1.5,
                marginBottom: 12,
              }}
            >
              {afterState.label || "AFTER"}
            </div>

            {afterState.image ? (
              <div
                style={{
                  width: "100%",
                  height: "220px",
                  borderRadius: "16px",
                  overflow: "hidden",
                  marginBottom: 16,
                  border: `2px solid ${accentColor}`,
                  boxShadow: `0 0 20px ${accentColor}44`,
                }}
              >
                <img
                  src={afterState.image}
                  alt={afterState.title}
                  style={{ width: "100%", height: "100%", objectFit: "cover" }}
                />
              </div>
            ) : null}

            {/* Transformed Value / Number */}
            {afterState.value ? (
              <div
                style={{
                  fontSize: variant === "numeric" ? 80 : 48,
                  fontWeight: 950,
                  color: "#ffffff",
                  lineHeight: 1.1,
                  letterSpacing: -1.5,
                  marginBottom: 8,
                }}
              >
                {afterState.value}
              </div>
            ) : null}

            <div
              style={{
                fontSize: 26,
                fontWeight: 900,
                color: "#ffffff",
                marginBottom: 6,
              }}
            >
              {afterState.title}
            </div>

            {afterState.subtitle ? (
              <div style={{ fontSize: 20, fontWeight: 600, color: tokens.text.secondary }}>
                {afterState.subtitle}
              </div>
            ) : null}
          </div>
        </main>

        {/* Footer */}
        {footerLabel ? (
          <footer style={{ textAlign: "center", fontSize: 20, color: tokens.text.muted, fontWeight: 600 }}>
            {footerLabel}
          </footer>
        ) : null}
      </div>
    </AbsoluteFill>
  );
}
