import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { type ProcessFlowProps, type ProcessStep } from "./types";
import { tokens } from "./design-tokens";

export function ProcessFlow(props: ProcessFlowProps | any) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Normalize boundary props wrapper
  const resolvedProps: ProcessFlowProps = props.props ? props.props : props;
  const duration_frames = (props as any).duration_frames || 180;

  const headerLabel = resolvedProps.headerLabel || "";
  const stepList: ProcessStep[] = Array.isArray(resolvedProps.steps) ? resolvedProps.steps : [];
  const footerLabel = resolvedProps.footerLabel || "";

  const stepCount = stepList.length;

  // Auto-determine layout: 2 or 3 steps -> horizontal, 4 or 5 steps -> vertical
  const preferredLayout = resolvedProps.layout || "auto";
  const isHorizontal =
    preferredLayout === "horizontal" ||
    (preferredLayout === "auto" && stepCount <= 3);

  // Staggered Timing Construction Logic
  // Allocate 75% of total scene duration for chain construction, hold remaining 25%
  const totalBuildDuration = Math.round(duration_frames * 0.75);
  const timePerStep = Math.round(totalBuildDuration / Math.max(1, stepCount));

  // Determine current active step for reading focus
  const currentActiveIndex = Math.min(
    stepCount - 1,
    Math.floor(frame / timePerStep)
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
        {/* Header Eyebrow */}
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

        {/* Main Causal Flow Chain */}
        <main
          style={{
            position: "relative",
            display: "flex",
            flexDirection: isHorizontal ? "row" : "column",
            alignItems: "center",
            justifyContent: "center",
            gap: isHorizontal ? "12px" : "10px",
            flex: 1,
            margin: "16px 0",
          }}
        >
          {stepList.map((step, idx) => {
            const stepFrameStart = idx * timePerStep;

            const stepSpring = spring({
              frame: Math.max(0, frame - stepFrameStart),
              fps,
              config: { damping: 14, stiffness: 95 },
            });

            // Active Reading Focus
            const isCurrentActive = idx === currentActiveIndex && frame < totalBuildDuration;
            const isRevealed = frame >= stepFrameStart;

            // Connector timing (draws after step appears)
            const connectorFrameStart = stepFrameStart + Math.round(timePerStep * 0.45);
            const connectorProgress = interpolate(
              frame,
              [connectorFrameStart, connectorFrameStart + Math.round(timePerStep * 0.45)],
              [0, 1],
              { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
            );

            // Node Role Styling
            const stepType = step.type || (idx === 0 ? "cause" : idx === stepCount - 1 ? "outcome" : "step");
            
            const roleBadgeText =
              stepType === "cause"
                ? "CAUSE"
                : stepType === "outcome"
                ? "OUTCOME"
                : "MECHANISM";

            const roleBadgeColor =
              stepType === "cause"
                ? "#f59e0b"
                : stepType === "outcome"
                ? "#10b981"
                : tokens.accent.blue;

            const cardBorderColor = isCurrentActive
              ? roleBadgeColor
              : isRevealed
              ? "rgba(59, 130, 246, 0.25)"
              : "transparent";

            const connectorText = step.connectorLabel || (idx < stepCount - 1 ? "leads to" : "");

            return (
              <div
                key={idx}
                style={{
                  display: "flex",
                  flexDirection: isHorizontal ? "row" : "column",
                  alignItems: "center",
                  flex: isHorizontal ? 1 : undefined,
                  width: isHorizontal ? undefined : "100%",
                  maxWidth: isHorizontal ? "440px" : "900px",
                }}
              >
                {/* CAUSAL STEP NODE CARD */}
                <div
                  style={{
                    position: "relative",
                    width: "100%",
                    background: isCurrentActive
                      ? "linear-gradient(135deg, rgba(30, 41, 59, 0.95) 0%, rgba(15, 23, 42, 0.95) 100%)"
                      : "rgba(15, 23, 42, 0.75)",
                    border: `2px solid ${cardBorderColor}`,
                    borderRadius: "16px",
                    padding: isHorizontal ? "24px 20px" : "18px 28px",
                    boxShadow: isCurrentActive
                      ? `0 10px 30px ${roleBadgeColor}33`
                      : "0 6px 20px rgba(0, 0, 0, 0.2)",
                    backdropFilter: "blur(6px)",
                    opacity: isRevealed ? (isCurrentActive ? 1 : 0.82) : 0,
                    transform: `scale(${isRevealed ? (isCurrentActive ? 1.04 : 1) : 0.92})`,
                    transition: "border 0.2s, opacity 0.2s, transform 0.2s",
                  }}
                >
                  {/* Role Tag & Icon */}
                  <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 8 }}>
                    <span
                      style={{
                        fontSize: 12,
                        fontWeight: 900,
                        letterSpacing: 1.5,
                        textTransform: "uppercase",
                        padding: "3px 10px",
                        borderRadius: "12px",
                        background: `${roleBadgeColor}22`,
                        color: roleBadgeColor,
                        border: `1px solid ${roleBadgeColor}66`,
                      }}
                    >
                      {roleBadgeText}
                    </span>
                    {step.icon ? <span style={{ fontSize: 20 }}>{step.icon}</span> : null}
                  </div>

                  {/* Title */}
                  <div
                    style={{
                      fontSize: isHorizontal ? 24 : 26,
                      fontWeight: 900,
                      color: "#ffffff",
                      lineHeight: 1.25,
                    }}
                  >
                    {step.title}
                  </div>

                  {/* Metric Value Callout */}
                  {step.value !== undefined && step.value !== null ? (
                    <div
                      style={{
                        fontSize: 22,
                        fontWeight: 900,
                        color: roleBadgeColor,
                        marginTop: 6,
                      }}
                    >
                      {step.value}
                    </div>
                  ) : null}

                  {/* Subtitle */}
                  {step.subtitle ? (
                    <div
                      style={{
                        fontSize: 15,
                        color: tokens.text.secondary,
                        marginTop: 4,
                        fontWeight: 500,
                      }}
                    >
                      {step.subtitle}
                    </div>
                  ) : null}
                </div>

                {/* CAUSAL CONNECTOR (Arrow + Relationship Label) */}
                {idx < stepCount - 1 ? (
                  <div
                    style={{
                      display: "flex",
                      flexDirection: isHorizontal ? "column" : "row",
                      alignItems: "center",
                      justifyContent: "center",
                      padding: isHorizontal ? "0 8px" : "6px 0",
                      opacity: connectorProgress,
                      transform: `scale(${connectorProgress})`,
                      flexShrink: 0,
                    }}
                  >
                    {/* Relationship Badge */}
                    {connectorText ? (
                      <span
                        style={{
                          fontSize: 13,
                          fontWeight: 800,
                          color: tokens.accent.blue,
                          background: "rgba(30, 41, 59, 0.9)",
                          border: `1px solid ${tokens.accent.blue}66`,
                          padding: "4px 10px",
                          borderRadius: "12px",
                          whiteSpace: "nowrap",
                          boxShadow: "0 4px 12px rgba(0,0,0,0.3)",
                          zIndex: 2,
                          marginBottom: isHorizontal ? 4 : 0,
                        }}
                      >
                        {connectorText}
                      </span>
                    ) : null}

                    {/* Arrow Indicator */}
                    <div
                      style={{
                        fontSize: 22,
                        fontWeight: 900,
                        color: tokens.accent.blue,
                        lineHeight: 1,
                      }}
                    >
                      {isHorizontal ? "➔" : "↓"}
                    </div>
                  </div>
                ) : null}
              </div>
            );
          })}
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
