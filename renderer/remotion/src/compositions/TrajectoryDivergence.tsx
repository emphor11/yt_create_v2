import React from 'react';
import { AbsoluteFill, interpolate, spring, useCurrentFrame } from 'remotion';
import { tokens } from '../design-tokens';
import { TrajectoryDivergenceProps } from '../types';
import { safeAnimationWindow, safeSpringDelay } from '../animation-safety';

export function TrajectoryDivergence(childProps: {
  scene_id: string;
  composition: string;
  fps: number;
  duration_frames: number;
  props: TrajectoryDivergenceProps;
  frame_spans?: any[];
}) {
  const { props, duration_frames, fps = 30 } = childProps;
  const frame = useCurrentFrame();

  const {
    headerLabel = 'WEALTH ACCUMULATION DIVERGENCE',
    timeHorizon = '10 Years',
    baselineLabel = 'Starting Point',
    pathA,
    pathB,
    divergenceGap,
    variant,
  } = props;

  // Scene fade-in (frames 0..8)
  const sceneOpacity = interpolate(
    frame,
    [0, Math.min(8, Math.max(1, duration_frames - 1))],
    [0, 1],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
  );

  // 1. Header entrance
  const headerDelay = safeSpringDelay(4, duration_frames);
  const headerSpring = spring({
    frame: Math.max(0, frame - headerDelay),
    fps,
    config: tokens.motion.reveal,
  });

  // 2. Baseline Row entrance
  const baselineDelay = safeSpringDelay(10, duration_frames);
  const baselineSpring = spring({
    frame: Math.max(0, frame - baselineDelay),
    fps,
    config: tokens.motion.reveal,
  });

  // 3. SVG Path Draw
  const [curveStart, curveEnd] = safeAnimationWindow(18, 80, duration_frames);
  const curveProgress = interpolate(
    frame,
    [curveStart, curveEnd],
    [0, 1],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
  );

  // 4. Path Cards Reveal
  const cardADelay = safeSpringDelay(55, duration_frames);
  const cardASpring = spring({
    frame: Math.max(0, frame - cardADelay),
    fps,
    config: tokens.motion.impact,
  });

  const cardBDelay = safeSpringDelay(55, duration_frames);
  const cardBSpring = spring({
    frame: Math.max(0, frame - cardBDelay),
    fps,
    config: tokens.motion.impact,
  });

  // 5. Gap Badge Reveal
  const gapDelay = safeSpringDelay(70, duration_frames);
  const gapSpring = spring({
    frame: Math.max(0, frame - gapDelay),
    fps,
    config: tokens.motion.impact,
  });

  const colorA = pathA.direction === 'up' || pathA.tone === 'positive' ? tokens.accent.emerald : tokens.accent.cyan;
  const colorB = pathB.direction === 'down' || pathB.tone === 'negative' ? tokens.accent.rose : tokens.accent.cyan;

  // SVG Geometry
  const svgWidth = 960;
  const svgHeight = 460;
  const cx = svgWidth / 2;
  const cy = svgHeight - 60; // origin point

  // Path A (Up)
  const axEnd = cx - 350;
  const ayEnd = 60;
  
  // Path B (Down)
  const bxEnd = cx + 350;
  const byEnd = svgHeight - 60;

  // Control points for nice curves
  const acp1x = cx;
  const acp1y = cy - 200;
  const acp2x = axEnd + 150;
  const acp2y = ayEnd;
  const dPathA = `M ${cx} ${cy} C ${acp1x} ${acp1y}, ${acp2x} ${acp2y}, ${axEnd} ${ayEnd}`;
  
  const bcp1x = cx;
  const bcp1y = cy;
  const bcp2x = bxEnd - 150;
  const bcp2y = byEnd;
  const dPathB = `M ${cx} ${cy} C ${bcp1x} ${bcp1y}, ${bcp2x} ${bcp2y}, ${bxEnd} ${byEnd}`;

  // Approximate path length (just use strokeDasharray large enough)
  const pathLength = 1200;
  const dashOffset = interpolate(curveProgress, [0, 1], [pathLength, 0]);

  return (
    <AbsoluteFill style={{ backgroundColor: tokens.bg.base, opacity: sceneOpacity, fontFamily: tokens.font.family }}>
      <div style={{ position: 'relative', width: '100%', height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
        
        {/* Header */}
        <div style={{
          position: 'absolute',
          top: 80,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          transform: `translateY(${interpolate(headerSpring, [0, 1], [-40, 0])}px)`,
          opacity: headerSpring
        }}>
          {timeHorizon && (
            <div style={{
              backgroundColor: tokens.bg.surface,
              color: tokens.accent.cyan,
              padding: '8px 24px',
              borderRadius: tokens.radius.pill,
              fontSize: tokens.font.eyebrow,
              fontWeight: 600,
              letterSpacing: '0.05em',
              textTransform: 'uppercase',
              marginBottom: 24,
              border: `1px solid ${tokens.bg.border}`
            }}>
              {timeHorizon}
            </div>
          )}
          <h1 style={{
            color: tokens.text.primary,
            fontSize: tokens.font.subheadline,
            fontWeight: 700,
            margin: 0,
            textTransform: 'uppercase',
            letterSpacing: '0.02em'
          }}>
            {headerLabel}
          </h1>
        </div>

        {/* SVG Paths */}
        <div style={{ position: 'absolute', top: 300, width: svgWidth, height: svgHeight }}>
          <svg width={svgWidth} height={svgHeight} style={{ overflow: 'visible' }}>
            <defs>
              <linearGradient id="gradA" x1="100%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stopColor={colorA} />
                <stop offset="100%" stopColor={colorA} stopOpacity={0.2} />
              </linearGradient>
              <linearGradient id="gradB" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor={colorB} stopOpacity={0.2} />
                <stop offset="100%" stopColor={colorB} />
              </linearGradient>
            </defs>
            
            <path
              d={dPathA}
              fill="none"
              stroke="url(#gradA)"
              strokeWidth={8}
              strokeLinecap="round"
              strokeDasharray={pathLength}
              strokeDashoffset={dashOffset}
            />
            
            <path
              d={dPathB}
              fill="none"
              stroke="url(#gradB)"
              strokeWidth={8}
              strokeLinecap="round"
              strokeDasharray={pathLength}
              strokeDashoffset={dashOffset}
            />

            {/* Origin Dot */}
            <circle
              cx={cx}
              cy={cy}
              r={12}
              fill={tokens.bg.base}
              stroke={tokens.text.primary}
              strokeWidth={4}
              opacity={baselineSpring}
            />
          </svg>

          {/* Baseline Row */}
          {baselineLabel && (
            <div style={{
              position: 'absolute',
              left: cx,
              top: cy + 40,
              transform: 'translateX(-50%)',
              opacity: baselineSpring,
              color: tokens.text.secondary,
              fontSize: tokens.font.body,
              fontWeight: 500,
              textAlign: 'center',
              whiteSpace: 'nowrap'
            }}>
              <div style={{ width: 2, height: 24, backgroundColor: tokens.bg.border, margin: '0 auto 12px' }} />
              {baselineLabel}
            </div>
          )}

          {/* Path A Card */}
          <div style={{
            position: 'absolute',
            left: axEnd,
            top: ayEnd - 20,
            transform: `translate(-100%, -100%) translateX(${interpolate(cardASpring, [0, 1], [-40, 0])}px)`,
            opacity: cardASpring,
            backgroundColor: tokens.bg.cardLeft,
            border: `2px solid ${colorA}`,
            borderRadius: tokens.radius.card,
            padding: '24px 32px',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'flex-end',
            boxShadow: `0 20px 40px -10px ${colorA}40`
          }}>
            <div style={{ color: tokens.text.secondary, fontSize: tokens.font.eyebrow, marginBottom: 8 }}>{pathA.label}</div>
            <div style={{ color: tokens.text.primary, fontSize: tokens.font.subheadline, fontWeight: 700, marginBottom: 12 }}>{pathA.endValue}</div>
            {pathA.rate && (
              <div style={{
                backgroundColor: `${colorA}20`,
                color: colorA,
                padding: '4px 12px',
                borderRadius: tokens.radius.pill,
                fontSize: tokens.font.caption,
                fontWeight: 600
              }}>
                {pathA.rate}
              </div>
            )}
          </div>

          {/* Path B Card */}
          <div style={{
            position: 'absolute',
            left: bxEnd,
            top: byEnd + 20,
            transform: `translate(0, 0) translateX(${interpolate(cardBSpring, [0, 1], [40, 0])}px)`,
            opacity: cardBSpring,
            backgroundColor: tokens.bg.cardRight,
            border: `2px solid ${colorB}`,
            borderRadius: tokens.radius.card,
            padding: '24px 32px',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'flex-start',
            boxShadow: `0 20px 40px -10px ${colorB}40`
          }}>
            <div style={{ color: tokens.text.secondary, fontSize: tokens.font.eyebrow, marginBottom: 8 }}>{pathB.label}</div>
            <div style={{ color: tokens.text.primary, fontSize: tokens.font.subheadline, fontWeight: 700, marginBottom: 12 }}>{pathB.endValue}</div>
            {pathB.rate && (
              <div style={{
                backgroundColor: `${colorB}20`,
                color: colorB,
                padding: '4px 12px',
                borderRadius: tokens.radius.pill,
                fontSize: tokens.font.caption,
                fontWeight: 600
              }}>
                {pathB.rate}
              </div>
            )}
          </div>
        </div>

        {/* Divergence Gap Badge */}
        {divergenceGap && (
          <div style={{
            position: 'absolute',
            bottom: 80,
            left: '50%',
            transform: `translateX(-50%) scale(${interpolate(gapSpring, [0, 1], [0.8, 1])})`,
            opacity: gapSpring,
            backgroundColor: tokens.bg.surface,
            border: `2px solid ${tokens.accent.amber}`,
            borderRadius: tokens.radius.card,
            padding: '24px 48px',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            boxShadow: `0 20px 40px -10px ${tokens.accent.amber}40`
          }}>
            <div style={{ color: tokens.accent.amber, fontSize: tokens.font.subheadline, fontWeight: 800 }}>
              {divergenceGap}
            </div>
          </div>
        )}

      </div>
    </AbsoluteFill>
  );
}
