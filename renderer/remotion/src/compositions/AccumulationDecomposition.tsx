import React from 'react';
import { AbsoluteFill, interpolate, spring, useCurrentFrame } from 'remotion';
import { tokens } from '../design-tokens';
import { AccumulationDecompositionProps } from '../types';
import { safeSpringDelay } from '../animation-safety';

export function AccumulationDecomposition(childProps: {
  scene_id: string;
  composition: string;
  fps: number;
  duration_frames: number;
  props: AccumulationDecompositionProps;
  frame_spans?: any[];
}) {
  const { props, duration_frames, fps = 30 } = childProps;
  const frame = useCurrentFrame();

  const {
    headerLabel = 'WEALTH ACCUMULATION',
    totalValue,
    totalLabel = 'Total Accumulated Corpus',
    timeHorizon,
    streams = [],
    annotation,
  } = props;

  // Scene fade-in
  const sceneOpacity = interpolate(
    frame,
    [0, Math.min(8, Math.max(1, duration_frames - 1))],
    [0, 1],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
  );

  // Header entrance
  const headerDelay = safeSpringDelay(4, duration_frames, 0.1);
  const headerSpring = spring({
    frame: Math.max(0, frame - headerDelay),
    fps,
    config: tokens.motion.reveal,
  });

  // Hero Card entrance
  const heroDelay = safeSpringDelay(10, duration_frames, 0.2);
  const heroSpring = spring({
    frame: Math.max(0, frame - heroDelay),
    fps,
    config: tokens.motion.reveal,
  });

  // Calculate stream proportional widths
  const displayStreams = streams.slice(0, 4);
  const totalNumeric = displayStreams.reduce((acc, s) => acc + (s.numericAmount || 1), 0);

  // Annotation entrance
  const annotationDelay = safeSpringDelay(20 + displayStreams.length * 10, duration_frames, 0.7);
  const annotationSpring = spring({
    frame: Math.max(0, frame - annotationDelay),
    fps,
    config: tokens.motion.gentle,
  });

  // Color mapping helper
  const getColor = (colorToken?: string | null, index: number = 0) => {
    if (colorToken === 'emerald') return tokens.accent.emerald;
    if (colorToken === 'cyan') return tokens.accent.cyan;
    if (colorToken === 'amber') return tokens.accent.amber;
    if (colorToken === 'purple') return tokens.accent.purple;
    const palette = [tokens.accent.emerald, tokens.accent.cyan, tokens.accent.amber, tokens.accent.purple];
    return palette[index % palette.length];
  };

  return (
    <AbsoluteFill
      style={{
        backgroundColor: tokens.bg.base,
        opacity: sceneOpacity,
        fontFamily: tokens.font.family,
        padding: '70px 100px',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
        boxSizing: 'border-box',
      }}
    >
      {/* 1. Top Header Eyebrow */}
      <div
        style={{
          transform: `translateY(${interpolate(headerSpring, [0, 1], [-30, 0])}px)`,
          opacity: headerSpring,
          textAlign: 'center',
        }}
      >
        <span
          style={{
            color: tokens.text.secondary,
            fontSize: tokens.font.eyebrow,
            fontWeight: 600,
            letterSpacing: '0.12em',
            textTransform: 'uppercase',
          }}
        >
          {headerLabel}
        </span>
      </div>

      {/* 2. Hero Total Corpus Card */}
      <div
        style={{
          transform: `translateY(${interpolate(heroSpring, [0, 1], [-20, 0])}px)`,
          opacity: heroSpring,
          backgroundColor: tokens.bg.surface,
          border: `2px solid ${tokens.accent.cyan}`,
          borderRadius: tokens.radius.card,
          padding: '28px 44px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          boxShadow: `0 14px 40px -12px ${tokens.accent.cyan}35`,
          marginTop: 16,
        }}
      >
        <div style={{ display: 'flex', flexDirection: 'column' }}>
          <span style={{ color: tokens.text.secondary, fontSize: tokens.font.caption, fontWeight: 500, letterSpacing: '0.04em' }}>
            {totalLabel}
          </span>
          <span style={{ color: tokens.accent.cyan, fontSize: tokens.font.headline, fontWeight: 800, marginTop: 4, letterSpacing: '-0.02em' }}>
            {totalValue}
          </span>
        </div>

        {timeHorizon && (
          <div
            style={{
              backgroundColor: 'rgba(56, 189, 248, 0.12)',
              border: `1px solid ${tokens.accent.cyan}60`,
              borderRadius: tokens.radius.pill,
              padding: '10px 24px',
              display: 'flex',
              alignItems: 'center',
              gap: 8,
            }}
          >
            <span style={{ color: tokens.accent.cyan, fontSize: tokens.font.caption, fontWeight: 700 }}>
              ⏱ {timeHorizon}
            </span>
          </div>
        )}
      </div>

      {/* 3. Stacked Composite Bar */}
      {displayStreams.length > 0 && (
        <div style={{ margin: '20px 0', display: 'flex', flexDirection: 'column', gap: 10 }}>
          <div
            style={{
              height: 24,
              width: '100%',
              backgroundColor: tokens.bg.surface,
              borderRadius: tokens.radius.pill,
              overflow: 'hidden',
              display: 'flex',
              border: `1px solid ${tokens.bg.border}`,
            }}
          >
            {displayStreams.map((stream, idx) => {
              const streamDelay = safeSpringDelay(14 + idx * 8, duration_frames, 0.4);
              const barSpring = spring({
                frame: Math.max(0, frame - streamDelay),
                fps,
                config: tokens.motion.reveal,
              });

              const fraction = (stream.numericAmount || 1) / totalNumeric;
              const barWidth = fraction * 100 * barSpring;
              const color = getColor(stream.colorToken, idx);

              return (
                <div
                  key={idx}
                  style={{
                    height: '100%',
                    width: `${barWidth}%`,
                    backgroundColor: color,
                    transition: 'width 0.1s ease',
                  }}
                />
              );
            })}
          </div>
        </div>
      )}

      {/* 4. Stream Cards Breakdown */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: `repeat(${Math.max(1, displayStreams.length)}, 1fr)`,
          gap: 20,
          margin: '10px 0',
        }}
      >
        {displayStreams.map((stream, idx) => {
          const streamDelay = safeSpringDelay(16 + idx * 10, duration_frames, 0.5);
          const streamSpring = spring({
            frame: Math.max(0, frame - streamDelay),
            fps,
            config: tokens.motion.reveal,
          });

          const color = getColor(stream.colorToken, idx);

          return (
            <div
              key={idx}
              style={{
                transform: `translateY(${interpolate(streamSpring, [0, 1], [30, 0])}px)`,
                opacity: streamSpring,
                backgroundColor: tokens.bg.surface,
                borderLeft: `5px solid ${color}`,
                borderTop: `1px solid ${tokens.bg.border}`,
                borderRight: `1px solid ${tokens.bg.border}`,
                borderBottom: `1px solid ${tokens.bg.border}`,
                borderRadius: tokens.radius.card,
                padding: '24px 28px',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
              }}
            >
              <div>
                <div style={{ color: tokens.text.secondary, fontSize: 20, fontWeight: 500 }}>
                  {stream.label}
                </div>
                <div style={{ color: color, fontSize: 40, fontWeight: 700, marginTop: 8 }}>
                  {stream.value}
                </div>
              </div>

              {stream.rate && (
                <div style={{ marginTop: 12 }}>
                  <span
                    style={{
                      display: 'inline-block',
                      backgroundColor: `${color}18`,
                      color: color,
                      fontSize: 18,
                      fontWeight: 600,
                      padding: '4px 12px',
                      borderRadius: tokens.radius.pill,
                    }}
                  >
                    {stream.rate}
                  </span>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* 5. Bottom Key Insight Annotation */}
      {annotation ? (
        <div
          style={{
            transform: `translateY(${interpolate(annotationSpring, [0, 1], [20, 0])}px)`,
            opacity: annotationSpring,
            backgroundColor: 'rgba(24, 24, 27, 0.70)',
            borderLeft: `4px solid ${tokens.accent.emerald}`,
            borderRadius: tokens.radius.chip,
            padding: '16px 24px',
            display: 'flex',
            alignItems: 'center',
            gap: 12,
            marginTop: 10,
          }}
        >
          <span style={{ fontSize: 22 }}>💡</span>
          <span style={{ color: tokens.text.primary, fontSize: 22, fontWeight: 500, lineHeight: 1.4 }}>
            {annotation}
          </span>
        </div>
      ) : (
        <div style={{ height: 20 }} />
      )}
    </AbsoluteFill>
  );
}
