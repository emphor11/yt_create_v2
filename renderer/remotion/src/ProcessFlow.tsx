import React from "react";
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { type ProcessFlowProps, type ProcessStep } from "./types";
import { tokens } from "./design-tokens";
import { safeAnimationWindow, safeSpringDelay } from "./animation-safety";

export function ProcessFlow(props: ProcessFlowProps | any) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Normalize boundary props wrapper
  const resolvedProps: ProcessFlowProps = props.props ? props.props : props;
  const duration_frames = (props as any).duration_frames || (props as any).durationInFrames || 180;

  const headerLabel = resolvedProps.headerLabel || "";
  const stepList: ProcessStep[] = Array.isArray(resolvedProps.steps) ? resolvedProps.steps : [];
  const footerLabel = resolvedProps.footerLabel || "";

  const stepCount = stepList.length;

  // Layout selection: 2 or 3 steps default to horizontal, 4 or 5 steps default to vertical
  const preferredLayout = (resolvedProps.layout || resolvedProps.variant || "auto").toLowerCase();
  const isHorizontal =
    preferredLayout === "horizontal" ||
    (preferredLayout === "auto" && stepCount <= 3);

  // Cascade Animation Timing: Brisk cascade so all steps and connectors settle early in the scene
  const totalBuildDuration = Math.min(36, Math.max(1, Math.floor(duration_frames * 0.40)));
  const timePerStep = Math.max(2, Math.floor(totalBuildDuration / Math.max(1, stepCount)));

  const headerDelay = safeSpringDelay(0, duration_frames, 0.15);
  const headerSpring = spring({
    frame: Math.max(0, frame - headerDelay),
    fps,
    config: tokens.motion.reveal,
  });

  return (
    <AbsoluteFill
      style={{
        background: "radial-gradient(ellipse 90% 70% at 50% 40%, rgba(15, 23, 42, 0.96) 0%, rgba(5, 7, 10, 0.99) 100%)",
        color: tokens.text.primary,
        fontFamily: tokens.font.family,
        overflow: "hidden",
        padding: "50px 80px",
      }}
    >
      {/* Cinematic Top and Bottom Subtle Letterbox Hairlines */}
      <div
        style={{
          position: "absolute",
          top: 24,
          left: 80,
          right: 80,
          height: "1px",
          background: "linear-gradient(90deg, transparent 0%, rgba(255, 255, 255, 0.12) 30%, rgba(255, 255, 255, 0.12) 70%, transparent 100%)",
        }}
      />
      <div
        style={{
          position: "absolute",
          bottom: 24,
          left: 80,
          right: 80,
          height: "1px",
          background: "linear-gradient(90deg, transparent 0%, rgba(255, 255, 255, 0.12) 30%, rgba(255, 255, 255, 0.12) 70%, transparent 100%)",
        }}
      />

      <div
        style={{
          position: "relative",
          display: "flex",
          flexDirection: "column",
          height: "100%",
          justifyContent: "space-between",
          zIndex: 1,
        }}
      >
        {/* Header Eyebrow */}
        <header
          style={{
            textAlign: "center",
            opacity: headerSpring,
            transform: `translateY(${(1 - headerSpring) * -14}px)`,
          }}
        >
          {headerLabel ? (
            <div
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: 8,
                padding: "6px 18px",
                borderRadius: tokens.radius.pill,
                background: "rgba(255, 255, 255, 0.05)",
                border: "1px solid rgba(255, 255, 255, 0.12)",
                color: tokens.accent.cyan,
                fontSize: 13,
                fontWeight: 800,
                textTransform: "uppercase",
                letterSpacing: 2,
                boxShadow: "0 2px 10px rgba(0, 0, 0, 0.2)",
              }}
            >
              <span
                style={{
                  width: 6,
                  height: 6,
                  borderRadius: "50%",
                  backgroundColor: tokens.accent.cyan,
                  boxShadow: `0 0 8px ${tokens.accent.cyan}`,
                }}
              />
              {headerLabel}
            </div>
          ) : null}
        </header>

        {/* Main Process Flow Journey Chain */}
        <main
          style={{
            position: "relative",
            display: "flex",
            flexDirection: isHorizontal ? "row" : "column",
            alignItems: "center",
            justifyContent: "center",
            gap: isHorizontal ? "12px" : "10px",
            flex: 1,
            margin: "20px 0",
            width: "100%",
          }}
        >
          {stepList.map((step, idx) => {
            const isFirst = idx === 0;
            const isLast = idx === stepCount - 1;
            const nominalDelay = idx * timePerStep;
            const stepDelay = safeSpringDelay(nominalDelay, duration_frames, 0.65);

            const stepSpring = spring({
              frame: Math.max(0, frame - stepDelay),
              fps,
              config: tokens.motion.reveal,
            });

            // Connector timing (strictly monotonic window)
            const [connStart, connEnd] = safeAnimationWindow(
              stepDelay + 2,
              stepDelay + Math.max(4, timePerStep),
              duration_frames,
              2
            );
            const connectorProgress = interpolate(
              frame,
              [connStart, connEnd],
              [0, 1],
              { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
            );

            // Node Role Styling
            const stepType = step.type || (isFirst ? "cause" : isLast ? "outcome" : "step");

            let roleBadgeText: string;
            let roleColor: string;

            if (stepType === "cause" || isFirst) {
              roleBadgeText = `STEP 01 // INITIATION`;
              roleColor = tokens.accent.cyan;
            } else if (stepType === "outcome" || isLast) {
              roleBadgeText = `FINAL STEP // PAYOFF`;
              roleColor = tokens.accent.emerald;
            } else {
              roleBadgeText = `STEP 0${idx + 1} // MECHANISM`;
              roleColor = tokens.accent.blue;
            }

            const connectorText = step.connectorLabel || (idx < stepCount - 1 ? "leads to" : "");

            return (
              <React.Fragment key={idx}>
                {/* CAUSAL STEP NODE CARD */}
                <div
                  style={{
                    position: "relative",
                    flex: isHorizontal ? (isLast ? 1.05 : 1) : undefined,
                    width: isHorizontal ? undefined : "100%",
                    maxWidth: isHorizontal ? `${Math.floor(1400 / Math.max(2, stepCount))}px` : "860px",
                    background: isLast
                      ? "linear-gradient(135deg, rgba(30, 41, 59, 0.90) 0%, rgba(15, 23, 42, 0.95) 100%)"
                      : "rgba(15, 23, 42, 0.70)",
                    border: isLast
                      ? `2px solid ${roleColor}`
                      : `1px solid rgba(255, 255, 255, 0.10)`,
                    borderRadius: "18px",
                    padding: isHorizontal
                      ? stepCount >= 4 ? "20px 16px" : "26px 22px"
                      : stepCount >= 5 ? "14px 22px" : "18px 26px",
                    boxShadow: isLast
                      ? `0 10px 30px ${roleColor}25, 0 0 16px ${roleColor}15`
                      : "0 6px 20px rgba(0, 0, 0, 0.25)",
                    backdropFilter: "blur(14px)",
                    opacity: stepSpring,
                    transform: isHorizontal
                      ? `translateY(${(1 - stepSpring) * 25}px) scale(${isLast ? 1.02 : 1})`
                      : `translateX(${(1 - stepSpring) * -25}px) scale(${isLast ? 1.02 : 1})`,
                    zIndex: isLast ? 2 : 1,
                    transition: "transform 0.25s ease",
                  }}
                >
                  {/* Role Tag & Icon */}
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between",
                      marginBottom: 10,
                    }}
                  >
                    <span
                      style={{
                        fontSize: 11,
                        fontWeight: 900,
                        letterSpacing: 1.5,
                        textTransform: "uppercase",
                        padding: "3px 10px",
                        borderRadius: tokens.radius.pill,
                        background: `${roleColor}18`,
                        color: roleColor,
                        border: `1px solid ${roleColor}55`,
                      }}
                    >
                      {roleBadgeText}
                    </span>
                    {step.icon ? <span style={{ fontSize: 20 }}>{step.icon}</span> : null}
                  </div>

                  {/* Title */}
                  <div
                    style={{
                      fontSize: isHorizontal ? (stepCount >= 4 ? 20 : 24) : stepCount >= 5 ? 20 : 23,
                      fontWeight: 900,
                      color: "#ffffff",
                      lineHeight: 1.25,
                      letterSpacing: -0.3,
                    }}
                  >
                    {step.title}
                  </div>

                  {/* Metric Value Callout */}
                  {step.value !== undefined && step.value !== null ? (
                    <div
                      style={{
                        fontSize: isLast ? (isHorizontal ? 26 : 24) : 20,
                        fontWeight: 900,
                        color: roleColor,
                        marginTop: 8,
                        fontVariantNumeric: "tabular-nums",
                        textShadow: isLast ? `0 0 16px ${roleColor}44` : "none",
                      }}
                    >
                      {step.value}
                    </div>
                  ) : null}

                  {/* Subtitle */}
                  {step.subtitle ? (
                    <div
                      style={{
                        fontSize: 14,
                        color: tokens.text.secondary,
                        marginTop: 6,
                        fontWeight: 500,
                        lineHeight: 1.35,
                      }}
                    >
                      {step.subtitle}
                    </div>
                  ) : null}
                </div>

                {/* CAUSAL CONNECTOR (Arrow + Relationship Label) */}
                {idx < stepCount - 1 && (
                  <div
                    style={{
                      display: "flex",
                      flexDirection: isHorizontal ? "column" : "row",
                      alignItems: "center",
                      justifyContent: "center",
                      padding: isHorizontal ? "0 4px" : "4px 0",
                      opacity: connectorProgress,
                      transform: `scale(${connectorProgress})`,
                      flexShrink: 0,
                      zIndex: 3,
                    }}
                  >
                    {/* Relationship Badge */}
                    {connectorText ? (
                      <span
                        style={{
                          fontSize: 11,
                          fontWeight: 800,
                          color: tokens.accent.cyan,
                          background: "rgba(15, 23, 42, 0.95)",
                          border: "1px solid rgba(6, 182, 212, 0.35)",
                          padding: "3px 8px",
                          borderRadius: tokens.radius.pill,
                          whiteSpace: "nowrap",
                          boxShadow: "0 4px 12px rgba(0, 0, 0, 0.4)",
                          marginBottom: isHorizontal ? 6 : 0,
                          marginRight: isHorizontal ? 0 : 8,
                          letterSpacing: 1,
                          textTransform: "uppercase",
                        }}
                      >
                        {connectorText}
                      </span>
                    ) : null}

                    {/* Modern SVG Directional Chevron Indicator */}
                    <div
                      style={{
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        width: isHorizontal ? 28 : 20,
                        height: isHorizontal ? 20 : 28,
                      }}
                    >
                      {isHorizontal ? (
                        <svg width="24" height="16" viewBox="0 0 24 16" fill="none">
                          <path
                            d="M2 8H20M20 8L14 2M20 8L14 14"
                            stroke={tokens.accent.cyan}
                            strokeWidth="2.5"
                            strokeLinecap="round"
                            strokeLinejoin="round"
                          />
                        </svg>
                      ) : (
                        <svg width="16" height="24" viewBox="0 0 16 24" fill="none">
                          <path
                            d="M8 2V20M8 20L2 14M8 20L14 14"
                            stroke={tokens.accent.cyan}
                            strokeWidth="2.5"
                            strokeLinecap="round"
                            strokeLinejoin="round"
                          />
                        </svg>
                      )}
                    </div>
                  </div>
                )}
              </React.Fragment>
            );
          })}
        </main>

        {/* Footer */}
        {footerLabel ? (
          <footer
            style={{
              textAlign: "center",
              fontSize: 16,
              color: tokens.text.muted,
              fontWeight: 600,
              letterSpacing: 0.5,
            }}
          >
            {footerLabel}
          </footer>
        ) : null}
      </div>
    </AbsoluteFill>
  );
}

