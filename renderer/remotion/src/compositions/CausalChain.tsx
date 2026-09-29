import React from 'react';
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { tokens } from '../design-tokens';
import { CausalChainProps, CausalStepProp } from '../types';
import { safeSpringDelay } from '../animation-safety';

function EditorialBackdrop({ glowColor = '#38bdf8', glowOpacity = 0.10 }: { glowColor?: string; glowOpacity?: number }) {
  return (
    <AbsoluteFill style={{ backgroundColor: '#060911', overflow: 'hidden', pointerEvents: 'none', zIndex: 0 }}>
      <div style={{ position: 'absolute', inset: 0, background: 'radial-gradient(ellipse 95% 75% at 50% 46%, #0b1222 0%, #060913 65%, #020408 100%)' }} />
      <div style={{ position: 'absolute', width: '900px', height: '600px', left: '50%', top: '50%', transform: 'translate(-50%,-50%)', borderRadius: '50%', background: `radial-gradient(ellipse at center, ${glowColor} 0%, transparent 68%)`, filter: 'blur(48px)', opacity: glowOpacity }} />
    </AbsoluteFill>
  );
}

const POLARITY_COLORS: Record<string, string> = {
  positive: '#10b981',
  negative: '#f43f5e',
  warning: '#f59e0b',
  neutral: '#38bdf8',
};

export function CausalChain(props: CausalChainProps | any) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const resolvedProps: CausalChainProps = (props as any).props || props;
  const duration_frames: number = (props as any).duration_frames || 180;

  const rawSteps = Array.isArray(resolvedProps.steps) && resolvedProps.steps.length >= 3
    ? resolvedProps.steps.slice(0, 6)
    : [{ label: 'Cause' }, { label: 'Effect' }, { label: 'Outcome' }];

  const connectors: string[] = Array.isArray(resolvedProps.connectors) ? resolvedProps.connectors : [];
  const polarity = resolvedProps.polarity || 'neutral';
  const headline = resolvedProps.headline || null;
  const headerLabel = resolvedProps.header_label || 'CAUSAL MECHANISM';
  const stepCount = rawSteps.length;

  const accentColor = POLARITY_COLORS[polarity] ?? '#38bdf8';

  const sceneOpacity = interpolate(frame, [0, Math.min(8, duration_frames - 1)], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });

  // Each step appears with a staggered spring
  const stepDelay = Math.max(12, Math.round(duration_frames / (stepCount + 2)));

  const stepAnimations = rawSteps.map((_, i) => {
    const delay = safeSpringDelay(i * stepDelay, duration_frames, 0.6);
    const sp = spring({ frame: Math.max(0, frame - delay), fps, config: { damping: 20, stiffness: 110, mass: 0.9 } });
    return { opacity: sp, x: interpolate(sp, [0, 1], [24, 0]) };
  });

  // Connector arrows appear after their left step
  const connectorAnimations = rawSteps.slice(0, -1).map((_, i) => {
    const delay = safeSpringDelay((i + 1) * stepDelay + 4, duration_frames, 0.6);
    return interpolate(frame, [delay, delay + 12], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  });

  // Layout: if ≤ 3 steps, go horizontal; if 4–6, stack in 2 rows
  const useVertical = stepCount >= 4;
  const stepsPerRow = useVertical ? Math.ceil(stepCount / 2) : stepCount;
  const rows: CausalStepProp[][] = useVertical
    ? [rawSteps.slice(0, stepsPerRow), rawSteps.slice(stepsPerRow)]
    : [rawSteps];

  const cardWidth = useVertical ? 200 : Math.min(220, Math.floor(920 / stepCount) - 10);
  const cardHeight = 80;

  return (
    <AbsoluteFill style={{ opacity: sceneOpacity }}>
      <EditorialBackdrop glowColor={accentColor} glowOpacity={0.08} />

      <AbsoluteFill style={{ zIndex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '80px 100px' }}>

        {/* Header */}
        <div style={{ position: 'absolute', top: '56px', left: '100px', fontFamily: "Inter, ui-sans-serif, system-ui, sans-serif", fontSize: '11px', fontWeight: 700, letterSpacing: '0.22em', color: accentColor, textTransform: 'uppercase', opacity: 0.7 }}>
          {headerLabel}
        </div>

        {/* Steps */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 24, alignItems: 'center', marginTop: 20 }}>
          {rows.map((rowSteps, ri) => {
            const rowStart = ri * stepsPerRow;
            return (
              <div key={ri} style={{ display: 'flex', flexDirection: 'row', alignItems: 'center', gap: 0 }}>
                {rowSteps.map((step, si) => {
                  const globalIdx = rowStart + si;
                  const anim = stepAnimations[globalIdx] ?? { opacity: 1, x: 0 };
                  const connectorIdx = globalIdx;
                  const connectorLabel = connectors[connectorIdx] || '→';
                  const isLast = globalIdx === rawSteps.length - 1;

                  return (
                    <React.Fragment key={si}>
                      {/* Step card */}
                      <div style={{
                        opacity: anim.opacity,
                        transform: `translateX(${anim.x}px)`,
                        width: cardWidth,
                        minHeight: cardHeight,
                        background: globalIdx === rawSteps.length - 1
                          ? `linear-gradient(135deg, ${accentColor}22 0%, ${accentColor}10 100%)`
                          : 'rgba(255,255,255,0.04)',
                        border: `1.5px solid ${globalIdx === rawSteps.length - 1 ? accentColor : 'rgba(255,255,255,0.12)'}`,
                        borderRadius: 12,
                        padding: '14px 18px',
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'flex-start',
                        gap: 4,
                        boxShadow: globalIdx === rawSteps.length - 1 ? `0 0 24px ${accentColor}28` : 'none',
                      }}>
                        {/* Step number */}
                        <div style={{ fontFamily: "Inter, ui-sans-serif, system-ui, sans-serif", fontSize: '10px', fontWeight: 700, color: accentColor, opacity: 0.6, letterSpacing: '0.12em' }}>
                          STEP {globalIdx + 1}
                        </div>
                        <div style={{ fontFamily: "Inter, ui-sans-serif, system-ui, sans-serif", fontSize: '15px', fontWeight: 600, color: 'rgba(255,255,255,0.9)', lineHeight: 1.3 }}>
                          {step.label}
                        </div>
                        {step.value && (
                          <div style={{ fontFamily: "Inter, ui-sans-serif, system-ui, sans-serif", fontSize: '18px', fontWeight: 800, color: accentColor, marginTop: 2 }}>
                            {step.value}
                          </div>
                        )}
                      </div>

                      {/* Connector arrow */}
                      {!isLast && (
                        <div style={{
                          opacity: connectorAnimations[connectorIdx] ?? 0,
                          display: 'flex',
                          flexDirection: 'column',
                          alignItems: 'center',
                          justifyContent: 'center',
                          width: 52,
                          flexShrink: 0,
                        }}>
                          <div style={{ fontFamily: "Inter, ui-sans-serif, system-ui, sans-serif", fontSize: '9px', fontWeight: 600, color: 'rgba(255,255,255,0.4)', letterSpacing: '0.08em', textAlign: 'center', marginBottom: 3 }}>
                            {connectorLabel !== '→' ? connectorLabel : ''}
                          </div>
                          <div style={{ color: accentColor, fontSize: '18px', opacity: 0.7 }}>→</div>
                        </div>
                      )}
                    </React.Fragment>
                  );
                })}
              </div>
            );
          })}
        </div>

        {/* Headline */}
        {headline && (
          <div style={{
            marginTop: 36,
            fontFamily: "Inter, ui-sans-serif, system-ui, sans-serif",
            fontSize: '20px',
            fontWeight: 600,
            color: 'rgba(255,255,255,0.6)',
            textAlign: 'center',
            opacity: stepAnimations[rawSteps.length - 1]?.opacity ?? 0,
          }}>
            {headline}
          </div>
        )}
      </AbsoluteFill>
    </AbsoluteFill>
  );
}
