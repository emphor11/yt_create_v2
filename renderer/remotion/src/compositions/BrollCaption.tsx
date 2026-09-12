import React from 'react';
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { tokens } from '../design-tokens';
import { BrollCaptionProps } from '../types';

export function BrollCaption(props: BrollCaptionProps | any) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const resolvedProps: BrollCaptionProps = (props as any).props || props;

  const caption = resolvedProps.caption || "";
  const emphasisPhrase = resolvedProps.emphasisPhrase || null;
  const author = resolvedProps.author || null;

  // Scene fade
  const sceneOpacity = interpolate(frame, [0, 12], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Word-by-word reveal calculation
  const words = caption.split(" ");
  const baseStart = 10;
  const framesPerWord = 2.5;

  // Emphasis box motion
  const boxSpring = spring({
    frame: Math.max(0, frame - 32),
    fps,
    config: { damping: 15, stiffness: 105 },
  });
  const boxY = interpolate(boxSpring, [0, 1], [20, 0]);
  const boxOpacity = interpolate(boxSpring, [0, 1], [0, 1]);

  // Author motion
  const authorOpacity = interpolate(frame, [44, 60], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill
      style={{
        backgroundColor: "rgba(9, 9, 11, 0.75)",
        fontFamily: tokens.font.family,
        opacity: sceneOpacity,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        padding: "60px 140px",
        overflow: "hidden",
        textAlign: "center",
      }}
    >
      {/* Vignette Gradient Overlay */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: "radial-gradient(ellipse at center, transparent 40%, rgba(9,9,11,0.95) 100%)",
          pointerEvents: "none",
        }}
      />

      {/* Main Caption (Word-by-word reveal) */}
      <div
        style={{
          fontSize: "42px",
          fontWeight: 600,
          color: tokens.text.primary,
          lineHeight: 1.4,
          maxWidth: "1350px",
          display: "flex",
          flexWrap: "wrap",
          justifyContent: "center",
          gap: "12px",
          zIndex: 1,
          marginBottom: emphasisPhrase ? "36px" : "0",
        }}
      >
        {words.map((word, i) => {
          const wordStart = baseStart + i * framesPerWord;
          const wordOpacity = interpolate(frame, [wordStart, wordStart + 4], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          });
          const wordY = interpolate(frame, [wordStart, wordStart + 4], [8, 0], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          });

          return (
            <span
              key={i}
              style={{
                opacity: wordOpacity,
                transform: `translateY(${wordY}px)`,
                display: "inline-block",
              }}
            >
              {word}
            </span>
          );
        })}
      </div>

      {/* Emphasis Phrase Box */}
      {emphasisPhrase && (
        <div
          style={{
            opacity: boxOpacity,
            transform: `translateY(${boxY}px)`,
            backgroundColor: "rgba(15, 23, 42, 0.8)",
            borderRadius: tokens.radius.chip,
            border: `1px solid ${tokens.bg.border}`,
            borderLeft: `4px solid ${tokens.accent.primary}`,
            padding: "16px 28px",
            color: tokens.accent.cyan,
            fontSize: "24px",
            fontWeight: 600,
            maxWidth: "900px",
            boxShadow: "0 15px 35px -10px rgba(0,0,0,0.6)",
            zIndex: 1,
            marginBottom: author ? "24px" : "0",
          }}
        >
          {emphasisPhrase}
        </div>
      )}

      {/* Author Attribution */}
      {author && (
        <div
          style={{
            opacity: authorOpacity,
            fontSize: "22px",
            fontStyle: "italic",
            color: tokens.text.secondary,
            zIndex: 1,
          }}
        >
          — {author}
        </div>
      )}
    </AbsoluteFill>
  );
};
