import React from 'react';
import { AbsoluteFill, interpolate, spring, useCurrentFrame } from 'remotion';
import { tokens } from '../design-tokens';
import { CashFlowWaterfallProps } from '../types';
import { safeSpringDelay } from '../animation-safety';

export function CashFlowWaterfall(childProps: {
  scene_id: string;
  composition: string;
  fps: number;
  duration_frames: number;
  props: CashFlowWaterfallProps;
  frame_spans?: any[];
}) {
  const { props, duration_frames, fps = 30 } = childProps;
  const frame = useCurrentFrame();

  const {
    headerLabel = 'MONTHLY CASH FLOW',
    startingLabel,
    startingValue,
    steps = [],
    finalLabel,
    finalValue,
  } = props;

  // Scene fade-in
  const sceneOpacity = interpolate(
    frame,
    [0, Math.min(8, Math.max(1, duration_frames - 1))],
    [0, 1],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
  );

  const headerDelay = safeSpringDelay(4, duration_frames);
  const headerSpring = spring({
    frame: Math.max(0, frame - headerDelay),
    fps,
    config: tokens.motion.reveal,
  });

  const startingDelay = safeSpringDelay(10, duration_frames);
  const startingSpring = spring({
    frame: Math.max(0, frame - startingDelay),
    fps,
    config: tokens.motion.reveal,
  });

  const displaySteps = steps.slice(0, duration_frames < 90 ? 3 : 6);

  const finalDelay = safeSpringDelay(20 + displaySteps.length * 10 + 10, duration_frames);
  const finalSpring = spring({
    frame: Math.max(0, frame - finalDelay),
    fps,
    config: tokens.motion.impact,
  });

  return (
    <AbsoluteFill style={{ backgroundColor: tokens.bg.base, opacity: sceneOpacity, fontFamily: tokens.font.family }}>
      <div style={{ padding: '80px 120px', width: '100%', height: '100%', display: 'flex', flexDirection: 'column' }}>
        
        {/* Header */}
        <div style={{
          transform: `translateY(${interpolate(headerSpring, [0, 1], [-40, 0])}px)`,
          opacity: headerSpring,
          marginBottom: 60,
          textAlign: 'center'
        }}>
          <h1 style={{
            color: tokens.text.secondary,
            fontSize: tokens.font.eyebrow,
            fontWeight: 600,
            letterSpacing: '0.1em',
            textTransform: 'uppercase',
            margin: 0
          }}>
            {headerLabel}
          </h1>
        </div>

        {/* Starting Block */}
        <div style={{
          transform: `translateX(${interpolate(startingSpring, [0, 1], [-80, 0])}px)`,
          opacity: startingSpring,
          backgroundColor: tokens.bg.surface,
          border: `2px solid ${tokens.accent.emerald}`,
          borderRadius: tokens.radius.card,
          padding: '24px 32px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          boxShadow: `0 10px 30px -10px ${tokens.accent.emerald}40`
        }}>
          <div style={{ color: tokens.text.primary, fontSize: tokens.font.body, fontWeight: 600 }}>{startingLabel}</div>
          <div style={{ color: tokens.accent.emerald, fontSize: tokens.font.subheadline, fontWeight: 700 }}>{startingValue}</div>
        </div>

        {/* Steps */}
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', marginTop: 16, marginBottom: 16, flex: 1, justifyContent: 'center' }}>
          {displaySteps.map((step, i) => {
            const stepDelay = safeSpringDelay(20 + i * 10, duration_frames);
            const stepSpring = spring({
              frame: Math.max(0, frame - stepDelay),
              fps,
              config: tokens.motion.gentle,
            });

            const isSubtract = step.direction === 'subtract';
            const color = isSubtract ? tokens.accent.rose : tokens.accent.emerald;

            return (
              <React.Fragment key={i}>
                {/* Connector Arrow */}
                <div style={{
                  width: 4,
                  height: 32,
                  backgroundColor: tokens.bg.border,
                  opacity: stepSpring,
                  position: 'relative'
                }}>
                  <div style={{
                    position: 'absolute',
                    bottom: -4,
                    left: '50%',
                    transform: 'translateX(-50%)',
                    width: 0,
                    height: 0,
                    borderLeft: '6px solid transparent',
                    borderRight: '6px solid transparent',
                    borderTop: `6px solid ${tokens.bg.border}`
                  }} />
                </div>
                
                {/* Step Card */}
                <div style={{
                  width: '80%',
                  transform: `translateY(${interpolate(stepSpring, [0, 1], [-20, 0])}px)`,
                  opacity: stepSpring,
                  backgroundColor: tokens.bg.surface,
                  borderLeft: `4px solid ${color}`,
                  borderRadius: tokens.radius.chip,
                  padding: '20px 32px',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  marginTop: 8
                }}>
                  <div style={{ display: 'flex', flexDirection: 'column' }}>
                    <div style={{ color: tokens.text.primary, fontSize: tokens.font.caption, fontWeight: 500 }}>{step.label}</div>
                    {step.subtext && <div style={{ color: tokens.text.muted, fontSize: 18, marginTop: 4 }}>{step.subtext}</div>}
                  </div>
                  <div style={{ color: color, fontSize: tokens.font.body, fontWeight: 700 }}>{step.value}</div>
                </div>
              </React.Fragment>
            );
          })}
        </div>

        {/* Final Block */}
        {(finalLabel || finalValue) && (
          <div style={{
            transform: `translateY(${interpolate(finalSpring, [0, 1], [80, 0])}px)`,
            opacity: finalSpring,
            backgroundColor: tokens.bg.surface,
            border: `2px solid ${tokens.accent.amber}`,
            borderRadius: tokens.radius.card,
            padding: '32px 48px',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            boxShadow: `0 20px 40px -10px ${tokens.accent.amber}40`,
            marginTop: 'auto'
          }}>
            <div style={{ color: tokens.text.primary, fontSize: tokens.font.subheadline, fontWeight: 600 }}>{finalLabel}</div>
            <div style={{ color: tokens.accent.amber, fontSize: tokens.font.headline, fontWeight: 800 }}>{finalValue}</div>
          </div>
        )}

      </div>
    </AbsoluteFill>
  );
}
