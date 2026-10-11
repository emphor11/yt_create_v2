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

export const Badge: React.FC<ComponentProps> = ({
  instance,
  resolved,
}) => {
  const props = resolved.props;
  const text = (props.text as string) || "";
  const variant = (props.variant as string) || "filled";
  const intent = (props.intent as string) || "neutral";

  const themeConfig: Record<string, { bg: string; border: string; text: string; dot: string }> = {
    accent: {
      bg: variant === "outline" ? "transparent" : "rgba(6, 182, 212, 0.15)",
      border: "rgba(6, 182, 212, 0.45)",
      text: "#38bdf8",
      dot: "#38bdf8",
    },
    danger: {
      bg: variant === "outline" ? "transparent" : "rgba(244, 63, 94, 0.15)",
      border: "rgba(244, 63, 94, 0.45)",
      text: "#fb7185",
      dot: "#f43f5e",
    },
    negative: {
      bg: variant === "outline" ? "transparent" : "rgba(244, 63, 94, 0.15)",
      border: "rgba(244, 63, 94, 0.45)",
      text: "#fb7185",
      dot: "#f43f5e",
    },
    warning: {
      bg: variant === "outline" ? "transparent" : "rgba(245, 158, 11, 0.15)",
      border: "rgba(245, 158, 11, 0.45)",
      text: "#fde047",
      dot: "#fbbf24",
    },
    success: {
      bg: variant === "outline" ? "transparent" : "rgba(16, 185, 129, 0.15)",
      border: "rgba(16, 185, 129, 0.45)",
      text: "#34d399",
      dot: "#10b981",
    },
    positive: {
      bg: variant === "outline" ? "transparent" : "rgba(16, 185, 129, 0.15)",
      border: "rgba(16, 185, 129, 0.45)",
      text: "#34d399",
      dot: "#10b981",
    },
    neutral: {
      bg: variant === "outline" ? "transparent" : "rgba(255, 255, 255, 0.08)",
      border: "rgba(255, 255, 255, 0.15)",
      text: "#e2e8f0",
      dot: "#94a3b8",
    },
  };

  const theme = themeConfig[intent] || themeConfig.neutral;

  return (
    <div
      data-visual-component="Badge"
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
        display: "inline-flex",
        alignItems: "center",
        justifyContent: "center",
        gap: 6,
        padding: "0 14px",
        background: theme.bg,
        border: `1px solid ${theme.border}`,
        borderRadius: 9999,
        boxSizing: "border-box",
        fontFamily: "Inter, ui-sans-serif, system-ui, sans-serif",
      }}
    >
      <span
        style={{
          width: 6,
          height: 6,
          borderRadius: "50%",
          backgroundColor: theme.dot,
          boxShadow: `0 0 6px ${theme.dot}`,
        }}
      />
      <span
        style={{
          fontSize: 11,
          fontWeight: 700,
          letterSpacing: "0.09em",
          textTransform: "uppercase",
          color: theme.text,
          userSelect: "none",
        }}
      >
        {text}
      </span>
    </div>
  );
};
