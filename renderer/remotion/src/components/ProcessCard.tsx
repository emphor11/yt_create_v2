import React from "react";
import type { CompiledVisualInstance } from "../world/compiledWorld";
import type { ResolvedPrimitiveFrame } from "../world/runtime/types";
import type { WorldRuntime } from "../world/runtime";

export interface ComponentProps {
  runtime: WorldRuntime;
  instance: CompiledVisualInstance;
  resolved: ResolvedPrimitiveFrame;
  frame: number;
}

interface StepItem {
  step: number;
  title: string;
  detail?: string;
}

export const ProcessCard: React.FC<ComponentProps> = ({
  runtime,
  instance,
  resolved,
  frame,
}) => {
  const props = resolved.props;
  const header = props.header as string | undefined;
  const title = (props.title as string) || "PROCESS";
  const rawSteps = (props.steps as unknown as StepItem[]) || [];
  const subtext = props.subtext as string | undefined;

  return (
    <div
      data-visual-component="ProcessCard"
      data-object-id={instance.object_id}
      style={{
        position: "absolute",
        left: resolved.geometry.x,
        top: resolved.geometry.y,
        width: resolved.geometry.width,
        height: resolved.geometry.height,
        opacity: resolved.opacity,
        transform: resolved.transform,
        transformOrigin: "center center",
        background: "linear-gradient(180deg, #131722 0%, #0d111a 100%)",
        border: "1px solid rgba(56, 189, 248, 0.3)",
        borderRadius: 16,
        boxShadow: "0 24px 48px -12px rgba(0, 0, 0, 0.8), 0 0 20px -6px rgba(56, 189, 248, 0.15)",
        boxSizing: "border-box",
        overflow: "hidden",
        display: "flex",
        flexDirection: "column",
        justifyContent: "space-between",
        padding: "20px 24px",
        fontFamily: "Inter, ui-sans-serif, system-ui, sans-serif",
      }}
    >
      {/* Top Header */}
      <div>
        {header && (
          <div
            style={{
              fontSize: 11,
              fontWeight: 700,
              letterSpacing: "0.12em",
              textTransform: "uppercase",
              color: "#64748b",
              marginBottom: 4,
              userSelect: "none",
            }}
          >
            {header}
          </div>
        )}
        <div
          style={{
            fontSize: 16,
            fontWeight: 700,
            color: "#f8fafc",
            letterSpacing: "-0.01em",
            marginBottom: 14,
          }}
        >
          {title}
        </div>
      </div>

      {/* Sequential Steps Row */}
      {(() => {
        const enterFrame = runtime.getEntranceFrame(instance.object_id);
        const intervals = runtime.prepared.visibility.get(instance.object_id) ?? [];
        const endFrame = intervals[0]?.end_frame ?? (enterFrame + 180);
        const totalLifespan = Math.max(30, endFrame - enterFrame);
        const numSteps = Math.max(1, rawSteps.length);
        const elapsed = Math.max(0, frame - enterFrame);
        const activeWindow = Math.max(1, totalLifespan - 15);
        const activeStepIdx = Math.min(
          numSteps - 1,
          Math.floor((Math.max(0, elapsed - 15) / activeWindow) * numSteps)
        );

        return (
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              gap: 12,
            }}
          >
            {rawSteps.map((step, idx) => {
              const isPast = idx < activeStepIdx;
              const isActive = idx === activeStepIdx;
              const isFuture = idx > activeStepIdx;

              const stepStaggerFrame = enterFrame + idx * 8;
              const stepProgress = Math.min(1, Math.max(0, (frame - stepStaggerFrame) / 12));
              const stepOpacity = (isFuture ? 0.45 : 1.0) * (0.2 + 0.8 * stepProgress);
              const stepTranslateY = (1 - stepProgress) * 8;

              let cardBg = "rgba(255, 255, 255, 0.03)";
              let cardBorder = "1px solid rgba(255, 255, 255, 0.07)";
              let cardShadow = "none";
              let badgeColor = "#94a3b8";
              let titleColor = "#cbd5e1";

              if (isActive) {
                cardBg = "linear-gradient(135deg, rgba(56, 189, 248, 0.16) 0%, rgba(14, 165, 233, 0.08) 100%)";
                cardBorder = "1.5px solid #38bdf8";
                cardShadow = "0 0 20px -3px rgba(56, 189, 248, 0.35)";
                badgeColor = "#38bdf8";
                titleColor = "#ffffff";
              } else if (isPast) {
                cardBg = "rgba(16, 185, 129, 0.06)";
                cardBorder = "1px solid rgba(16, 185, 129, 0.3)";
                badgeColor = "#34d399";
                titleColor = "#cbd5e1";
              }

              return (
                <React.Fragment key={idx}>
                  <div
                    style={{
                      flex: 1,
                      background: cardBg,
                      border: cardBorder,
                      borderRadius: 10,
                      padding: "12px 14px",
                      display: "flex",
                      flexDirection: "column",
                      gap: 4,
                      opacity: stepOpacity,
                      transform: `translateY(${stepTranslateY.toFixed(1)}px)`,
                      boxShadow: cardShadow,
                      transition: "all 0.2s ease",
                    }}
                  >
                    <div
                      style={{
                        fontSize: 10,
                        fontWeight: 800,
                        color: badgeColor,
                        textTransform: "uppercase",
                        letterSpacing: "0.06em",
                        display: "flex",
                        alignItems: "center",
                        gap: 4,
                      }}
                    >
                      {isPast ? "✓" : null} Step {step.step || idx + 1}
                    </div>
                    <div
                      style={{
                        fontSize: 13,
                        fontWeight: isActive ? 800 : 700,
                        color: titleColor,
                        lineHeight: 1.25,
                      }}
                    >
                      {step.title}
                    </div>
                    {step.detail && (
                      <div
                        style={{
                          fontSize: 10,
                          color: isActive ? "#cbd5e1" : "#64748b",
                          lineHeight: 1.2,
                        }}
                      >
                        {step.detail}
                      </div>
                    )}
                  </div>

                  {idx < rawSteps.length - 1 && (
                    <div
                      style={{
                        color: isPast ? "#10b981" : isActive ? "#38bdf8" : "#334155",
                        fontSize: 14,
                        fontWeight: 800,
                      }}
                    >
                      →
                    </div>
                  )}
                </React.Fragment>
              );
            })}
          </div>
        );
      })()}

      {/* Bottom Subtext */}
      {subtext ? (
        <div
          style={{
            fontSize: 11,
            color: "#64748b",
            marginTop: 10,
            lineHeight: 1.3,
            userSelect: "none",
          }}
        >
          {subtext}
        </div>
      ) : (
        <div style={{ height: 2 }} />
      )}
    </div>
  );
};
