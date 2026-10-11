import React from "react";
import { spring } from "remotion";
import type { CompiledVisualInstance } from "../world/compiledWorld";
import type { ResolvedPrimitiveFrame } from "../world/runtime/types";
import type { WorldRuntime } from "../world/runtime";

export interface ComponentProps {
  runtime: WorldRuntime;
  instance: CompiledVisualInstance;
  resolved: ResolvedPrimitiveFrame;
  frame: number;
}

export interface WaterfallStep {
  label: string;
  value: number;
  display_value?: string;
  is_total?: boolean;
  intent?: "neutral" | "accent" | "danger" | "success" | "warning";
}

const colorStyles: Record<
  string,
  {
    barColor: string;
    glow: string;
    border: string;
    textColor: string;
  }
> = {
  success: {
    barColor: "linear-gradient(180deg, #10b981 0%, #059669 100%)",
    glow: "rgba(16, 185, 129, 0.4)",
    border: "rgba(52, 211, 153, 0.5)",
    textColor: "#34d399",
  },
  danger: {
    barColor: "linear-gradient(180deg, #f43f5e 0%, #be123c 100%)",
    glow: "rgba(244, 63, 94, 0.4)",
    border: "rgba(251, 113, 133, 0.5)",
    textColor: "#fb7185",
  },
  accent: {
    barColor: "linear-gradient(180deg, #38bdf8 0%, #0284c7 100%)",
    glow: "rgba(56, 189, 248, 0.4)",
    border: "rgba(56, 189, 248, 0.5)",
    textColor: "#38bdf8",
  },
  neutral: {
    barColor: "linear-gradient(180deg, #94a3b8 0%, #64748b 100%)",
    glow: "rgba(148, 163, 184, 0.3)",
    border: "rgba(203, 213, 225, 0.3)",
    textColor: "#cbd5e1",
  },
};

export const WaterfallBridge: React.FC<ComponentProps> = ({
  runtime,
  instance,
  resolved,
  frame,
}) => {
  const props = resolved.props;
  const header = (props.header as string) || (props.title as string) || "FINANCIAL WATERFALL BRIDGE";
  const subtext = props.subtext as string | undefined;

  // Parse steps
  let rawSteps: WaterfallStep[] = [];
  if (Array.isArray(props.steps)) {
    rawSteps = props.steps.map((s: any) => {
      const numVal = typeof s?.value === "number" ? s.value : parseFloat(String(s?.value || 0)) || 0;
      return {
        label: String(s?.label ?? "Step"),
        value: numVal,
        display_value: s?.display_value ? String(s.display_value) : undefined,
        is_total: Boolean(s?.is_total),
        intent: s?.intent,
      };
    });
  }

  // Fallback if empty
  if (rawSteps.length === 0) {
    rawSteps = [
      { label: "Gross Revenue", value: 100, is_total: true, display_value: "₹100 Cr" },
      { label: "COGS & Direct", value: -40, is_total: false, display_value: "-₹40 Cr" },
      { label: "OpEx & SG&A", value: -25, is_total: false, display_value: "-₹25 Cr" },
      { label: "Taxes & Cess", value: -10, is_total: false, display_value: "-₹10 Cr" },
      { label: "Net Profit", value: 25, is_total: true, display_value: "₹25 Cr" },
    ];
  }

  // Entrance timing
  const enterFrame = runtime.getEntranceFrame(instance.object_id);
  const localFrame = Math.max(0, frame - enterFrame);

  // Card geometry
  const cardWidth = resolved.geometry.width || 860;
  const cardHeight = resolved.geometry.height || 400;

  // Calculate cumulative heights for waterfall positioning
  let runningTotal = 0;
  interface ComputedStep extends WaterfallStep {
    start: number;
    end: number;
    display_value: string;
    style: (typeof colorStyles)["accent"];
  }

  const computedSteps: ComputedStep[] = rawSteps.map((step, idx) => {
    let start = 0;
    let end = 0;

    if (step.is_total || idx === 0) {
      start = 0;
      end = step.value;
      runningTotal = step.value;
    } else {
      start = runningTotal;
      end = runningTotal + step.value;
      runningTotal = end;
    }

    // Default intent derivation
    let intentKey = step.intent;
    if (!intentKey) {
      if (step.is_total || idx === 0) {
        intentKey = "accent";
      } else if (step.value < 0) {
        intentKey = "danger";
      } else {
        intentKey = "success";
      }
    }
    const style = colorStyles[intentKey] || colorStyles.neutral;

    const formattedValue =
      step.display_value ||
      (step.value > 0 && !step.is_total ? `+${step.value}` : String(step.value));

    return {
      ...step,
      start,
      end,
      display_value: formattedValue,
      style,
    };
  });

  // Calculate Y-scale bounds
  const allLevels = computedSteps.flatMap((s) => [s.start, s.end, 0]);
  const minVal = Math.min(0, ...allLevels);
  const maxVal = Math.max(1, ...allLevels);
  const range = maxVal - minVal || 1;

  // Plot area dimensions
  const plotTop = 75;
  const plotBottom = cardHeight - 70;
  const plotHeight = plotBottom - plotTop;

  const getY = (val: number) => {
    const norm = (val - minVal) / range;
    return plotBottom - norm * plotHeight;
  };

  const zeroY = getY(0);

  return (
    <div
      data-visual-component="WaterfallBridge"
      data-object-id={instance.object_id}
      style={{
        position: "absolute",
        left: resolved.geometry.x,
        top: resolved.geometry.y,
        width: cardWidth,
        height: cardHeight,
        opacity: resolved.opacity,
        transform: resolved.transform,
        transformOrigin: "center center",
        background: "linear-gradient(180deg, #131722 0%, #0d111a 100%)",
        border: "1px solid rgba(255, 255, 255, 0.10)",
        borderRadius: 16,
        boxShadow: "0 24px 48px -12px rgba(0, 0, 0, 0.8), 0 0 0 1px rgba(255, 255, 255, 0.04) inset",
        boxSizing: "border-box",
        overflow: "hidden",
        display: "flex",
        flexDirection: "column",
        justifyContent: "space-between",
        padding: "24px 28px",
        fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
      }}
    >
      {/* Header bar */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "flex-start",
          marginBottom: 8,
        }}
      >
        <div>
          <div
            style={{
              fontSize: 11,
              fontWeight: 800,
              letterSpacing: "0.14em",
              color: "#64748b",
              textTransform: "uppercase",
              marginBottom: 4,
            }}
          >
            VALUE BRIDGE & TRANSITION
          </div>
          <div
            style={{
              fontSize: 20,
              fontWeight: 700,
              letterSpacing: "-0.01em",
              color: "#f8fafc",
            }}
          >
            {header}
          </div>
        </div>

        {subtext && (
          <div
            style={{
              fontSize: 12,
              fontWeight: 500,
              color: "#94a3b8",
              backgroundColor: "rgba(255, 255, 255, 0.04)",
              border: "1px solid rgba(255, 255, 255, 0.08)",
              padding: "4px 10px",
              borderRadius: 6,
              maxWidth: 320,
              textAlign: "right",
            }}
          >
            {subtext}
          </div>
        )}
      </div>

      {/* Waterfall Graphic Area */}
      <div
        style={{
          position: "relative",
          width: "100%",
          height: plotHeight + 50,
          marginTop: 10,
        }}
      >
        {/* Zero baseline */}
        <div
          style={{
            position: "absolute",
            left: 0,
            right: 0,
            top: zeroY - plotTop,
            height: 1,
            backgroundColor: "rgba(255, 255, 255, 0.15)",
            zIndex: 1,
          }}
        />

        {/* Columns */}
        <div
          style={{
            position: "absolute",
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            display: "flex",
            justifyContent: "space-between",
            alignItems: "stretch",
          }}
        >
          {computedSteps.map((step, idx) => {
            const stepAnim = spring({
              frame: Math.max(0, localFrame - idx * 4),
              fps: 30,
              config: { damping: 16, stiffness: 100 },
            });

            // Heights
            const yStart = getY(step.start) - plotTop;
            const yEnd = getY(step.end) - plotTop;
            const topY = Math.min(yStart, yEnd);
            const rawBarH = Math.max(4, Math.abs(yStart - yEnd));
            const barH = rawBarH * stepAnim;

            // Bridge connector line to next step
            const nextStep = computedSteps[idx + 1];
            const hasNext = Boolean(nextStep);

            return (
              <div
                key={idx}
                style={{
                  flex: 1,
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "center",
                  position: "relative",
                  margin: "0 6px",
                }}
              >
                {/* Connector dashed line to the next bar */}
                {hasNext && (
                  <div
                    style={{
                      position: "absolute",
                      top: yEnd,
                      left: "50%",
                      width: "100%",
                      height: 1,
                      borderTop: "1px dashed rgba(255, 255, 255, 0.25)",
                      zIndex: 2,
                      opacity: stepAnim,
                    }}
                  />
                )}

                {/* Floating Waterfall Bar */}
                <div
                  style={{
                    position: "absolute",
                    top: step.value < 0 ? yStart : yStart - barH,
                    width: "70%",
                    maxWidth: 72,
                    height: Math.max(4, barH),
                    background: step.style.barColor,
                    border: `1px solid ${step.style.border}`,
                    borderRadius: 6,
                    boxShadow: `0 4px 16px ${step.style.glow}`,
                    zIndex: 3,
                    opacity: stepAnim,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                  }}
                />

                {/* Top/Bottom display value pill */}
                <div
                  style={{
                    position: "absolute",
                    top: (step.value < 0 ? yStart : yStart - barH) - 24,
                    fontSize: 12,
                    fontWeight: 700,
                    color: step.style.textColor,
                    letterSpacing: "-0.01em",
                    whiteSpace: "nowrap",
                    opacity: stepAnim,
                    zIndex: 4,
                  }}
                >
                  {step.display_value}
                </div>

                {/* Bottom Step Label */}
                <div
                  style={{
                    position: "absolute",
                    bottom: 0,
                    width: "100%",
                    textAlign: "center",
                    fontSize: 11,
                    fontWeight: step.is_total ? 700 : 500,
                    color: step.is_total ? "#f8fafc" : "#94a3b8",
                    lineHeight: 1.2,
                    textTransform: "uppercase",
                    letterSpacing: "0.02em",
                  }}
                >
                  {step.label}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
