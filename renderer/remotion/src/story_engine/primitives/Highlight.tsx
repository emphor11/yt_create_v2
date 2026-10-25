import React from "react";
import { handDrawn } from "../hand-drawn-theme.ts";

export interface HighlightWrapperProps {
  intensity: number; // 0 (no highlight) to 1 (full intensity)
  progress?: number; // 0 to 1 (animated marker stroke draw progress)
  color?: string;
  variant?: "marker" | "pulse" | "glow" | "border";
  strokePosition?: "bottom" | "middle" | "top";
  children: React.ReactNode;
  style?: React.CSSProperties;
}

export const Highlight: React.FC<HighlightWrapperProps> = ({
  intensity,
  progress = 0,
  color,
  strokePosition = "bottom",
  children,
  style,
}) => {
  const activeIntensity = Math.max(0, intensity);
  const activeProgress = Math.max(0, Math.min(1.0, progress > 0 ? progress : (activeIntensity > 0 ? 1.0 : 0)));

  if (activeIntensity <= 0 && activeProgress <= 0) {
    return <div style={style}>{children}</div>;
  }

  // Authentic documentary fluorescent yellow by default, or electric cyan/coral
  const markerColor = color || "#FACC15";
  const scale = 1 + 0.02 * activeIntensity;
  const shadowSpread = 8 * activeIntensity;

  // Determine vertical position of highlighter stroke
  let strokeBottom = "14%";
  let strokeHeight = 28;
  if (strokePosition === "middle") {
    strokeBottom = "45%";
    strokeHeight = 32;
  } else if (strokePosition === "top") {
    strokeBottom = "75%";
    strokeHeight = 28;
  }

  return (
    <div
      style={{
        position: "relative",
        transform: `scale(${scale})`,
        boxShadow: activeIntensity > 0 ? `0 0 ${shadowSpread}px 2px ${markerColor}44` : undefined,
        borderRadius: handDrawn.radius.card,
        transition: "transform 0.1s ease-out, box-shadow 0.1s ease-out",
        ...style,
      }}
    >
      {children}

      {/* Animated Investigative Highlighter Marker Pen Stroke */}
      {activeProgress > 0 && (
        <div
          style={{
            position: "absolute",
            bottom: strokeBottom,
            left: "4%",
            right: "4%",
            height: strokeHeight,
            pointerEvents: "none",
            zIndex: 15,
            overflow: "hidden",
            mixBlendMode: "multiply",
          }}
        >
          <svg
            width="100%"
            height="100%"
            preserveAspectRatio="none"
            viewBox="0 0 100 24"
            style={{
              width: "100%",
              height: "100%",
              display: "block",
              clipPath: `inset(0 ${(1 - activeProgress) * 100}% 0 0 round 3px)`,
            }}
          >
            {/* Organic, slightly wavy hand-drawn chisel marker path */}
            <path
              d="M 0,4 Q 25,1 50,3.5 T 100,2.5 L 99.5,21.5 Q 75,23.5 50,21 T 0.5,22.5 Z"
              fill={markerColor}
              opacity={0.78}
            />
          </svg>
        </div>
      )}
    </div>
  );
};
