import React from "react";
import { interpolate, spring, Easing } from "remotion";
import type { StampTone } from "../types.ts";

export interface ImpactStampProps {
  text: string;
  tone?: StampTone;
  color?: string;
  rotationDeg?: number;
  frame: number;
  startFrame: number;
  durationFrames?: number;
  fps?: number;
  scale?: number;
  style?: React.CSSProperties;
  targetRect?: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
}

const TONE_COLORS: Record<StampTone, { border: string; bg: string; text: string }> = {
  verdict: {
    border: "#DC2626", // bold crimson
    bg: "rgba(220, 38, 38, 0.08)",
    text: "#EF4444",
  },
  warning: {
    border: "#D97706", // vivid hazard amber
    bg: "rgba(217, 119, 6, 0.08)",
    text: "#F59E0B",
  },
  classified: {
    border: "#4B5563", // deep archival slate
    bg: "rgba(75, 85, 99, 0.12)",
    text: "#E2E8F0",
  },
  amount: {
    border: "#16A34A", // financial emerald
    bg: "rgba(22, 163, 74, 0.08)",
    text: "#22C55E",
  },
};

export const ImpactStamp: React.FC<ImpactStampProps> = ({
  text,
  tone = "verdict",
  color,
  rotationDeg = -6.5,
  frame,
  startFrame,
  durationFrames = 180,
  fps = 30,
  scale: baseScale = 1.0,
  style,
  targetRect,
}) => {
  if (frame < startFrame) {
    return null;
  }

  const relFrame = frame - startFrame;
  if (relFrame > durationFrames) {
    return null;
  }

  const toneConfig = TONE_COLORS[tone] ?? TONE_COLORS.verdict;
  const stampColor = color || toneConfig.text;
  const borderColor = color || toneConfig.border;

  // 1. Slam entrance: 0 to 6 frames aggressive drop (1.65x down to 1.0x)
  const slamScale = interpolate(relFrame, [0, 6], [1.65, 1.0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.in(Easing.cubic),
  });

  // 2. Overshoot angular settle: frame 6 onward settles into resting tilt
  const settleSpring = spring({
    fps,
    frame: Math.max(0, relFrame - 6),
    config: {
      stiffness: 240,
      damping: 14,
      mass: 0.8,
    },
  });

  const initialHitAngle = rotationDeg > 0 ? rotationDeg + 8 : rotationDeg - 8;
  const activeRotation = interpolate(settleSpring, [0, 1], [initialHitAngle, rotationDeg]);

  // 3. Shadow tightness (loosens during flight, slams tight on landing)
  const shadowBlur = interpolate(relFrame, [0, 6], [32, 5], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const shadowSpread = interpolate(relFrame, [0, 6], [16, 2], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // 4. Subtle Ink Bleed halo (faint duplicate expanding on impact)
  const inkBleedOpacity = interpolate(relFrame, [6, 12, 40], [0.4, 0.22, 0.12], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // 5. Exit fade (if near end of duration)
  const exitOpacity = interpolate(
    relFrame,
    [durationFrames - 15, durationFrames],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // Position calculation:
  // If targetRect is provided, position over the center of targetRect with slight offset
  // Otherwise, default to canvas center or caller style
  let containerPosition: React.CSSProperties = {
    position: "absolute",
    left: "50%",
    top: "50%",
    transform: "translate(-50%, -50%)",
    zIndex: 90,
  };

  if (targetRect) {
    containerPosition = {
      position: "absolute",
      left: targetRect.x + targetRect.width / 2,
      top: targetRect.y + targetRect.height / 2,
      transform: "translate(-50%, -50%)",
      zIndex: 90,
    };
  }

  return (
    <div
      style={{
        ...containerPosition,
        pointerEvents: "none",
        opacity: exitOpacity,
        ...style,
      }}
    >
      <div
        style={{
          transform: `scale(${slamScale * baseScale}) rotate(${activeRotation}deg)`,
          transformOrigin: "center center",
          display: "inline-flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          position: "relative",
        }}
      >
        {/* Ink Bleed Shadow Layer */}
        {relFrame >= 6 && (
          <div
            style={{
              position: "absolute",
              inset: -3,
              border: `4px solid ${borderColor}`,
              borderRadius: 8,
              opacity: inkBleedOpacity,
              filter: "blur(3px)",
              transform: "scale(1.02)",
            }}
          />
        )}

        {/* Primary Tactile Rubber Stamp Box */}
        <div
          style={{
            border: `4px solid ${borderColor}`,
            borderRadius: 7,
            padding: "8px 24px",
            backgroundColor: toneConfig.bg,
            boxShadow: `0 ${shadowSpread}px ${shadowBlur}px rgba(0, 0, 0, 0.45)`,
            display: "inline-flex",
            alignItems: "center",
            justifyContent: "center",
            gap: 12,
            position: "relative",
            backdropFilter: "blur(2px)",
          }}
        >
          {/* Inner Distressed Border Accent */}
          <div
            style={{
              position: "absolute",
              inset: 3,
              border: `1.5px solid ${borderColor}`,
              borderRadius: 4,
              opacity: 0.65,
              pointerEvents: "none",
            }}
          />

          {/* Stamp Typography */}
          <span
            style={{
              fontFamily: "'Courier New', Courier, monospace, 'Arial Black', sans-serif",
              fontSize: 26,
              fontWeight: 900,
              letterSpacing: "0.18em",
              textTransform: "uppercase",
              color: stampColor,
              whiteSpace: "nowrap",
              textShadow: `0 0 12px ${stampColor}44`,
            }}
          >
            {text}
          </span>
        </div>
      </div>
    </div>
  );
};
