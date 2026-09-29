import React from 'react';
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { tokens } from '../design-tokens';
import { RangeThresholdProps } from '../types';
import { safeSpringDelay } from '../animation-safety';

function EditorialBackdrop({ glowColor = '#38bdf8', glowOpacity = 0.10 }: { glowColor?: string; glowOpacity?: number }) {
  return (
    <AbsoluteFill style={{ backgroundColor: '#060911', overflow: 'hidden', pointerEvents: 'none', zIndex: 0 }}>
      <div style={{ position: 'absolute', inset: 0, background: 'radial-gradient(ellipse 95% 75% at 50% 46%, #0b1222 0%, #060913 65%, #020408 100%)' }} />
      <div style={{ position: 'absolute', width: '900px', height: '600px', left: '50%', top: '50%', transform: 'translate(-50%,-50%)', borderRadius: '50%', background: `radial-gradient(ellipse at center, ${glowColor} 0%, transparent 68%)`, filter: 'blur(52px)', opacity: glowOpacity }} />
    </AbsoluteFill>
  );
}

const POLARITY_COLORS: Record<string, string> = {
  positive: '#10b981',
  negative: '#f43f5e',
  warning: '#f59e0b',
  neutral: '#38bdf8',
};

export function RangeThreshold(props: RangeThresholdProps | any) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const resolvedProps: RangeThresholdProps = (props as any).props || props;
  const duration_frames: number = (props as any).duration_frames || 180;

  const mode = resolvedProps.mode || 'target_vs_actual';
  const label = resolvedProps.label || 'Metric';
  const polarity = resolvedProps.polarity || 'neutral';
  const headerLabel = resolvedProps.header_label || 'RANGE & THRESHOLD';
  const accentColor = POLARITY_COLORS[polarity] ?? '#38bdf8';

  const sceneOpacity = interpolate(frame, [0, Math.min(8, duration_frames - 1)], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });

  // Shared animation springs
  const headerDelay = 6;
  const labelDelay = 14;
  const barDelay = safeSpringDelay(24, duration_frames, 0.55);
  const valueDelay = safeSpringDelay(40, duration_frames, 0.5);
  const consequenceDelay = safeSpringDelay(60, duration_frames, 0.45);

  const labelSp = spring({ frame: Math.max(0, frame - labelDelay), fps, config: { damping: 18, stiffness: 110 } });
  const barProgress = interpolate(frame, [barDelay, barDelay + 45], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const valueSp = spring({ frame: Math.max(0, frame - valueDelay), fps, config: { damping: 18, stiffness: 110 } });
  const consequenceSp = spring({ frame: Math.max(0, frame - consequenceDelay), fps, config: { damping: 18, stiffness: 100 } });

  const BAR_WIDTH = 720;
  const BAR_HEIGHT = 20;

  // --- Render modes ---

  const renderTargetVsActual = () => {
    const current = resolvedProps.current_value;
    const target = resolvedProps.target_value;
    const delta = resolvedProps.lower_bound ?? null;

    return (
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 32, width: '100%' }}>
        {/* Central metric pair */}
        <div style={{ display: 'flex', flexDirection: 'row', gap: 80, alignItems: 'flex-end' }}>
          {current && (
            <div style={{ opacity: valueSp, transform: `translateY(${interpolate(valueSp, [0, 1], [20, 0])}px)`, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 6 }}>
              <div style={{ fontFamily: "Inter, ui-sans-serif, system-ui, sans-serif", fontSize: '11px', fontWeight: 700, letterSpacing: '0.16em', color: accentColor, opacity: 0.7 }}>ACTUAL</div>
              <div style={{ fontFamily: "Inter, ui-sans-serif, system-ui, sans-serif", fontSize: '64px', fontWeight: 900, color: accentColor, lineHeight: 1 }}>{current}</div>
            </div>
          )}
          {target && (
            <div style={{ opacity: valueSp, transform: `translateY(${interpolate(valueSp, [0, 1], [20, 0])}px)`, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 6 }}>
              <div style={{ fontFamily: "Inter, ui-sans-serif, system-ui, sans-serif", fontSize: '11px', fontWeight: 700, letterSpacing: '0.16em', color: 'rgba(255,255,255,0.4)', opacity: 0.7 }}>TARGET</div>
              <div style={{ fontFamily: "Inter, ui-sans-serif, system-ui, sans-serif", fontSize: '48px', fontWeight: 700, color: 'rgba(255,255,255,0.5)', lineHeight: 1 }}>{target}</div>
            </div>
          )}
        </div>

        {/* Thin progress bar showing actual vs target */}
        {current && target && (
          <div style={{ position: 'relative', width: BAR_WIDTH, height: BAR_HEIGHT }}>
            <div style={{ position: 'absolute', inset: 0, background: 'rgba(255,255,255,0.07)', borderRadius: 999 }} />
            {/* Target marker */}
            <div style={{ position: 'absolute', left: '60%', top: -6, bottom: -6, width: 2, background: 'rgba(255,255,255,0.25)', borderRadius: 1 }} />
            <div style={{ position: 'absolute', left: '60%', top: -22, transform: 'translateX(-50%)', fontFamily: "Inter, ui-sans-serif, system-ui, sans-serif", fontSize: '10px', color: 'rgba(255,255,255,0.35)', fontWeight: 700 }}>TARGET</div>
            {/* Current fill */}
            <div style={{ position: 'absolute', left: 0, top: 0, bottom: 0, width: `${barProgress * 55}%`, background: accentColor, borderRadius: 999, boxShadow: `0 0 12px ${accentColor}60` }} />
          </div>
        )}
      </div>
    );
  };

  const renderRangeBand = () => {
    const lower = resolvedProps.lower_bound;
    const upper = resolvedProps.upper_bound;
    const current = resolvedProps.current_value;

    return (
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 28, width: '100%' }}>
        {/* Range bar */}
        <div style={{ position: 'relative', width: BAR_WIDTH, height: 36 }}>
          {/* Full bar background */}
          <div style={{ position: 'absolute', inset: 0, background: 'rgba(255,255,255,0.05)', borderRadius: 999 }} />
          {/* Safe zone highlight (30% to 75% of bar = the band) */}
          <div style={{ position: 'absolute', left: '25%', right: '20%', top: 0, bottom: 0, background: `${accentColor}25`, borderRadius: 999, border: `1px solid ${accentColor}50`, width: `${barProgress * 55}%` }} />
          {/* Current indicator dot */}
          {current && (
            <div style={{ position: 'absolute', left: `${42 * barProgress}%`, top: '50%', transform: 'translate(-50%,-50%)', width: 16, height: 16, borderRadius: '50%', background: accentColor, boxShadow: `0 0 16px ${accentColor}90` }} />
          )}
        </div>
        {/* Labels row */}
        <div style={{ display: 'flex', flexDirection: 'row', justifyContent: 'space-between', width: BAR_WIDTH, opacity: valueSp }}>
          {lower && <div style={{ fontFamily: "Inter, ui-sans-serif, system-ui, sans-serif", fontSize: '18px', fontWeight: 700, color: 'rgba(255,255,255,0.6)' }}>{lower}</div>}
          {current && <div style={{ fontFamily: "Inter, ui-sans-serif, system-ui, sans-serif", fontSize: '36px', fontWeight: 900, color: accentColor }}>{current}</div>}
          {upper && <div style={{ fontFamily: "Inter, ui-sans-serif, system-ui, sans-serif", fontSize: '18px', fontWeight: 700, color: 'rgba(255,255,255,0.6)' }}>{upper}</div>}
        </div>
      </div>
    );
  };

  const renderThreshold = () => {
    const threshold = resolvedProps.threshold;
    const condition = resolvedProps.condition || 'above';
    const consequence = resolvedProps.consequence;
    const current = resolvedProps.current_value;

    return (
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 28 }}>
        {/* Threshold value */}
        {threshold && (
          <div style={{ opacity: valueSp, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 6 }}>
            <div style={{ fontFamily: "Inter, ui-sans-serif, system-ui, sans-serif", fontSize: '11px', fontWeight: 700, letterSpacing: '0.16em', color: 'rgba(255,255,255,0.4)' }}>THRESHOLD</div>
            <div style={{ fontFamily: "Inter, ui-sans-serif, system-ui, sans-serif", fontSize: '56px', fontWeight: 900, color: 'rgba(255,255,255,0.7)', lineHeight: 1 }}>{threshold}</div>
          </div>
        )}
        {/* Condition badge */}
        <div style={{ opacity: barProgress, background: `${accentColor}20`, border: `1px solid ${accentColor}60`, borderRadius: 8, padding: '8px 20px' }}>
          <div style={{ fontFamily: "Inter, ui-sans-serif, system-ui, sans-serif", fontSize: '13px', fontWeight: 700, color: accentColor, letterSpacing: '0.12em', textTransform: 'uppercase' }}>
            {condition.toUpperCase()} THRESHOLD
          </div>
        </div>
      </div>
    );
  };

  const renderBody = () => {
    if (mode === 'range' || mode === 'band') return renderRangeBand();
    if (mode === 'threshold') return renderThreshold();
    return renderTargetVsActual();
  };

  return (
    <AbsoluteFill style={{ opacity: sceneOpacity }}>
      <EditorialBackdrop glowColor={accentColor} glowOpacity={0.09} />

      <AbsoluteFill style={{ zIndex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '80px 100px' }}>

        {/* Header */}
        <div style={{ position: 'absolute', top: '56px', left: '100px', fontFamily: "Inter, ui-sans-serif, system-ui, sans-serif", fontSize: '11px', fontWeight: 700, letterSpacing: '0.22em', color: accentColor, textTransform: 'uppercase', opacity: 0.7 }}>
          {headerLabel}
        </div>

        {/* Label */}
        <div style={{ opacity: labelSp, transform: `translateY(${interpolate(labelSp, [0, 1], [16, 0])}px)`, marginBottom: 36, fontFamily: "Inter, ui-sans-serif, system-ui, sans-serif", fontSize: '20px', fontWeight: 700, color: 'rgba(255,255,255,0.75)', textAlign: 'center', letterSpacing: '0.02em' }}>
          {label}
        </div>

        {/* Mode-specific body */}
        {renderBody()}

        {/* Consequence */}
        {resolvedProps.consequence && mode !== 'threshold' && (
          <div style={{
            marginTop: 36,
            opacity: consequenceSp,
            background: `${accentColor}12`,
            border: `1px solid ${accentColor}38`,
            borderRadius: 10,
            padding: '12px 28px',
            fontFamily: "Inter, ui-sans-serif, system-ui, sans-serif",
            fontSize: '15px',
            color: 'rgba(255,255,255,0.6)',
            textAlign: 'center',
          }}>
            {resolvedProps.consequence}
          </div>
        )}
      </AbsoluteFill>
    </AbsoluteFill>
  );
}
