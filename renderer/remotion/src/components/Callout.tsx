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

export const Callout: React.FC<ComponentProps> = ({
  instance,
  resolved,
}) => {
  const props = resolved.props;
  const text = (props.text as string) || "";
  const attribution = props.attribution as string | undefined;
  const intent = (props.intent as string) || "insight";

  const accentColors: Record<string, { border: string; glow: string; text: string }> = {
    insight: { border: "#38bdf8", glow: "rgba(56, 189, 248, 0.2)", text: "#f8fafc" },
    takeaway: { border: "#a855f7", glow: "rgba(168, 85, 247, 0.2)", text: "#f8fafc" },
    positive: { border: "#10b981", glow: "rgba(16, 185, 129, 0.2)", text: "#f8fafc" },
    warning: { border: "#fbbf24", glow: "rgba(251, 191, 36, 0.2)", text: "#f8fafc" },
    danger: { border: "#f43f5e", glow: "rgba(244, 63, 94, 0.2)", text: "#f8fafc" },
  };

  const accent = accentColors[intent] || accentColors.insight;

  return (
    <div
      data-visual-component="Callout"
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
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        padding: "16px 24px",
        background: "linear-gradient(90deg, rgba(17, 24, 39, 0.95) 0%, rgba(15, 23, 42, 0.85) 100%)",
        borderLeft: `4px solid ${accent.border}`,
        borderTop: "1px solid rgba(255, 255, 255, 0.08)",
        borderRight: "1px solid rgba(255, 255, 255, 0.08)",
        borderBottom: "1px solid rgba(255, 255, 255, 0.08)",
        borderRadius: "0 12px 12px 0",
        boxShadow: `0 16px 32px -8px rgba(0, 0, 0, 0.7), 0 0 20px -5px ${accent.glow}`,
        boxSizing: "border-box",
        fontFamily: "Inter, ui-sans-serif, system-ui, sans-serif",
      }}
    >
      <div
        style={{
          fontSize: 16,
          fontWeight: 600,
          lineHeight: 1.45,
          color: accent.text,
          letterSpacing: "-0.01em",
        }}
      >
        {text}
      </div>

      {attribution && (
        <div
          style={{
            fontSize: 11,
            fontWeight: 700,
            textTransform: "uppercase",
            letterSpacing: "0.08em",
            color: "#64748b",
            marginTop: 6,
            userSelect: "none",
          }}
        >
          {attribution}
        </div>
      )}
    </div>
  );
};
