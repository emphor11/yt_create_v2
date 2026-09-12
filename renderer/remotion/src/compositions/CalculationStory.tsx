import React from 'react';
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { tokens } from '../design-tokens';
import { CalculationStoryProps } from '../types';

export function CalculationStory(props: CalculationStoryProps | any) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const resolvedProps: CalculationStoryProps = (props as any).props || props;

  const inputLabel = resolvedProps.inputLabel || "Input";
  const inputValue = resolvedProps.inputValue || "0";
  const operationLabel = resolvedProps.operationLabel || "×";
  const rateLabel = resolvedProps.rateLabel || "";
  const resultLabel = resolvedProps.resultLabel || "Result";
  const resultValue = resolvedProps.resultValue || "0";
  const note = resolvedProps.note || null;

  // Scene fade
  const sceneOpacity = interpolate(frame, [0, 8], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Input Card motion
  const inputSpring = spring({
    frame: Math.max(0, frame - 8),
    fps,
    config: { damping: 15, stiffness: 110 },
  });
  const inputX = interpolate(inputSpring, [0, 1], [-60, 0]);
  const inputOpacity = interpolate(inputSpring, [0, 1], [0, 1]);

  // Operator Badge motion
  const opSpring = spring({
    frame: Math.max(0, frame - 20),
    fps,
    config: { damping: 12, stiffness: 130 },
  });
  const opScale = interpolate(opSpring, [0, 1], [0.5, 1]);
  const opOpacity = interpolate(opSpring, [0, 1], [0, 1]);

  // Arrow dash draw (0 to 1)
  const arrowProgress = interpolate(frame, [26, 48], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Result Card motion
  const resultSpring = spring({
    frame: Math.max(0, frame - 42),
    fps,
    config: { damping: 14, stiffness: 100 },
  });
  const resultX = interpolate(resultSpring, [0, 1], [60, 0]);
  const resultOpacity = interpolate(resultSpring, [0, 1], [0, 1]);

  // Note motion
  const noteSpring = spring({
    frame: Math.max(0, frame - 54),
    fps,
    config: { damping: 16, stiffness: 120 },
  });
  const noteOpacity = interpolate(noteSpring, [0, 1], [0, 1]);

  return (
    <AbsoluteFill
      style={{
        backgroundColor: tokens.bg.base,
        fontFamily: tokens.font.family,
        opacity: sceneOpacity,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "60px 100px",
        overflow: "hidden",
      }}
    >
      <div
        style={{
          display: "flex",
          flexDirection: "row",
          alignItems: "center",
          justifyContent: "center",
          gap: "40px",
          width: "100%",
          maxWidth: "1600px",
        }}
      >
        {/* Input Card */}
        <div
          style={{
            opacity: inputOpacity,
            transform: `translateX(${inputX}px)`,
            flex: 1,
            maxWidth: "460px",
            minHeight: "340px",
            backgroundColor: tokens.bg.cardLeft,
            borderRadius: tokens.radius.card,
            border: `1px solid ${tokens.bg.border}`,
            padding: "40px 36px",
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
            boxShadow: "0 20px 40px -15px rgba(0, 0, 0, 0.5)",
          }}
        >
          <div
            style={{
              fontSize: "18px",
              fontWeight: 600,
              textTransform: "uppercase",
              letterSpacing: "0.06em",
              color: tokens.text.secondary,
              marginBottom: "16px",
            }}
          >
            {inputLabel}
          </div>
          <div
            style={{
              fontSize: "48px",
              fontWeight: 800,
              color: tokens.text.primary,
              lineHeight: 1.1,
            }}
          >
            {inputValue}
          </div>
        </div>

        {/* Center Operator Section */}
        <div
          style={{
            opacity: opOpacity,
            transform: `scale(${opScale})`,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            width: "180px",
            position: "relative",
          }}
        >
          {/* Connector Arrow SVG */}
          <svg
            width="180"
            height="40"
            viewBox="0 0 180 40"
            style={{ overflow: "visible", marginBottom: "8px" }}
          >
            <path
              d="M 0 20 L 170 20 M 155 10 L 170 20 L 155 30"
              stroke={tokens.accent.primary}
              strokeWidth="3.5"
              fill="none"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeDasharray="200"
              strokeDashoffset={200 * (1 - arrowProgress)}
            />
          </svg>

          {/* Operator Badge */}
          <div
            style={{
              width: "72px",
              height: "72px",
              borderRadius: "50%",
              backgroundColor: "rgba(15, 23, 42, 0.9)",
              border: `2px solid ${tokens.accent.primary}`,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: "36px",
              fontWeight: 800,
              color: tokens.accent.cyan,
              boxShadow: `0 0 20px rgba(59, 130, 246, 0.3)`,
              marginBottom: "10px",
            }}
          >
            {operationLabel}
          </div>

          {/* Rate Label */}
          {rateLabel && (
            <div
              style={{
                fontSize: "18px",
                fontWeight: 600,
                color: tokens.text.secondary,
                textAlign: "center",
                lineHeight: 1.2,
              }}
            >
              {rateLabel}
            </div>
          )}
        </div>

        {/* Result Card */}
        <div
          style={{
            opacity: resultOpacity,
            transform: `translateX(${resultX}px)`,
            flex: 1.2,
            maxWidth: "560px",
            minHeight: "360px",
            backgroundColor: tokens.bg.surface,
            borderRadius: tokens.radius.card,
            border: `2px solid rgba(59, 130, 246, 0.4)`,
            padding: "44px 40px",
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
            boxShadow: "0 25px 50px -12px rgba(59, 130, 246, 0.15), 0 20px 40px -15px rgba(0, 0, 0, 0.7)",
            position: "relative",
          }}
        >
          <div
            style={{
              fontSize: "20px",
              fontWeight: 600,
              textTransform: "uppercase",
              letterSpacing: "0.06em",
              color: tokens.text.primary,
              marginBottom: "16px",
            }}
          >
            {resultLabel}
          </div>
          <div
            style={{
              fontSize: "64px",
              fontWeight: 800,
              color: tokens.accent.cyan,
              lineHeight: 1.1,
              marginBottom: note ? "20px" : "0",
            }}
          >
            {resultValue}
          </div>

          {note && (
            <div
              style={{
                opacity: noteOpacity,
                display: "inline-flex",
                alignSelf: "flex-start",
                padding: "8px 16px",
                borderRadius: tokens.radius.chip,
                backgroundColor: "rgba(16, 185, 129, 0.12)",
                border: `1px solid rgba(16, 185, 129, 0.3)`,
                color: tokens.accent.emerald,
                fontSize: "16px",
                fontWeight: 600,
              }}
            >
              {note}
            </div>
          )}
        </div>
      </div>
    </AbsoluteFill>
  );
};
