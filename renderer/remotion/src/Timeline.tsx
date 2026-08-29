import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { type TimelineRenderSpec } from "./types";
import { tokens } from "./design-tokens";

export function Timeline(renderSpec: TimelineRenderSpec) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const duration_frames = renderSpec.duration_frames || 180;
  const props = renderSpec.props as any;
  
  // Extract exact component properties
  const headerLabel = props.headerLabel || "";
  const stepsList: string[] = Array.isArray(props.steps) ? props.steps : [];
  const footerLabel = props.footerLabel || "";

  const stepCount = stepsList.length;

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
            justifyContent: "center",
            gap: "28px",
            flex: 1,
            margin: "32px 0",
          }}
        >
          {stepsList.map((stepText, idx) => {
            // Sequential stagger delay for each step
            const delay = Math.round((duration_frames * 0.45 * idx) / Math.max(1, stepCount - 1));
            const stepSpring = spring({
              frame: Math.max(0, frame - delay),
              fps,
              config: { damping: 16, stiffness: 110 },
            });

            return (
              <div
                key={idx}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "24px",
                  opacity: stepSpring,
                  transform: `translateX(${(1 - stepSpring) * -40}px)`,
                }}
              >
                {/* Node Badge */}
                <div
                  style={{
                    width: "48px",
                    height: "48px",
                    borderRadius: "50%",
                    background: idx === stepCount - 1 ? tokens.accent.blue : "rgba(59, 130, 246, 0.2)",
                    border: `3px solid ${tokens.accent.blue}`,
                    boxShadow: "0 0 16px rgba(59, 130, 246, 0.4)",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontSize: 20,
                    fontWeight: 900,
                    color: "#ffffff",
                    flexShrink: 0,
                  }}
                >
                  {idx + 1}
                </div>

                {/* Step Card */}
                <div
                  style={{
                    background: "rgba(15, 23, 42, 0.75)",
                    border: "1px solid rgba(59, 130, 246, 0.3)",
                    borderRadius: "12px",
                    padding: "18px 28px",
                    flex: 1,
                    boxShadow: "0 10px 30px rgba(0, 0, 0, 0.3)",
                    backdropFilter: "blur(6px)",
                  }}
                >
                  <div style={{ fontSize: 18, color: tokens.accent.blue, fontWeight: 800, textTransform: "uppercase", letterSpacing: 1 }}>
                    Step {idx + 1}
                  </div>
                  <div style={{ fontSize: 36, fontWeight: 900, color: tokens.text.primary, marginTop: 4, lineHeight: 1.2 }}>
                    {stepText}
                  </div>
                </div>
              </div>
            );
          })}
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
