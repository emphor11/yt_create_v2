import React from "react";
import type { CompiledVisualInstance } from "../world/compiledWorld";
import type { ResolvedPrimitiveFrame } from "../world/runtime/types";
import type { WorldRuntime } from "../world/runtime";

export interface ComponentProps {
  runtime: WorldRuntime;
  instance: CompiledVisualInstance;
  resolved: ResolvedPrimitiveFrame;
  frame: number;
  renderChild?: (childId: string) => React.ReactNode;
}

export const SurfaceCard: React.FC<ComponentProps> = ({
  instance,
  resolved,
  renderChild,
}) => {
  const props = resolved.props;
  const variant = (props.variant as string) || "elevated";
  const intent = (props.intent as string) || "neutral";
  const headerLabel = props.header_label as string | undefined;

  // Professional color themes based on intent
  const intentBorders: Record<string, string> = {
    neutral: "rgba(255, 255, 255, 0.08)",
    accent: "rgba(56, 189, 248, 0.4)",
    danger: "rgba(244, 63, 94, 0.4)",
    warning: "rgba(251, 191, 36, 0.4)",
    success: "rgba(52, 211, 153, 0.4)",
  };

  const intentAccentBars: Record<string, string> = {
    neutral: "#94a3b8",
    accent: "#38bdf8",
    danger: "#f43f5e",
    warning: "#fbbf24",
    success: "#34d399",
  };

  const borderColor = intentBorders[intent] || intentBorders.neutral;
  const accentBarColor = intentAccentBars[intent] || intentAccentBars.neutral;
  const showAccentTop = variant === "accent_top" || intent === "accent" || intent === "danger";

  return (
    <div
      data-visual-component="SurfaceCard"
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
        border: `1px solid ${borderColor}`,
        borderRadius: 16,
        boxShadow: "0 24px 48px -12px rgba(0, 0, 0, 0.8), 0 0 0 1px rgba(255, 255, 255, 0.03) inset",
        boxSizing: "border-box",
        overflow: "hidden",
      }}
    >
      {/* Top Accent Strip */}
      {showAccentTop && (
        <div
          style={{
            position: "absolute",
            top: 0,
            left: 0,
            right: 0,
            height: 3,
            background: accentBarColor,
            boxShadow: `0 0 10px ${accentBarColor}`,
          }}
        />
      )}

      {/* Header Label */}
      {headerLabel && (
        <div
          style={{
            position: "absolute",
            top: 14,
            left: 24,
            right: 24,
            fontSize: 11,
            fontWeight: 700,
            letterSpacing: "0.12em",
            textTransform: "uppercase",
            color: "#64748b",
            fontFamily: "Inter, ui-sans-serif, system-ui, sans-serif",
            userSelect: "none",
          }}
        >
          {headerLabel}
        </div>
      )}

      {/* Child Elements (Positioned deterministically in parent-local space) */}
      {instance.child_object_ids.map((childId) => renderChild?.(childId))}
    </div>
  );
};
