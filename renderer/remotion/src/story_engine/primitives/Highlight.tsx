import React from "react";
import { tokens } from "../../design-tokens";

interface HighlightWrapperProps {
  intensity: number; // 0 (no highlight) to 1 (full intensity)
  color?: string;
  children: React.ReactNode;
  style?: React.CSSProperties;
}

export const Highlight: React.FC<HighlightWrapperProps> = ({
  intensity,
  color = tokens.accent.rose,
  children,
  style,
}) => {
  if (intensity <= 0) {
    return <div style={style}>{children}</div>;
  }

  const scale = 1 + 0.03 * intensity;
  const shadowSpread = 20 * intensity;

  return (
    <div
      style={{
        transform: `scale(${scale})`,
        boxShadow: `0 0 ${shadowSpread}px 4px ${color}66`,
        borderRadius: tokens.radius.card,
        transition: "transform 0.1s ease-out, box-shadow 0.1s ease-out",
        ...style,
      }}
    >
      {children}
    </div>
  );
};
