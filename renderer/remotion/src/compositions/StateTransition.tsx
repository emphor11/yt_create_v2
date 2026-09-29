import React from 'react';
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { tokens } from '../design-tokens';
import { StateTransitionProps, StateNodeProp } from '../types';
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

function StateCard({ node, accent, delay, frame, fps, isOutcome }: {
  node: StateNodeProp; accent: string; delay: number; frame: number; fps: number; isOutcome: boolean;
}) {
  const sp = spring({ frame: Math.max(0, frame - delay), fps, config: { damping: 18, stiffness: 100, mass: 0.95 } });
  const opacity = sp;
  const y = interpolate(sp, [0, 1], [24, 0]);

  return (
    <div style={{
      opacity,
      transform: `translateY(${y}px)`,
      flex: 1,
      minWidth: 220,
      maxWidth: 280,
      minHeight: 140,
      background: isOutcome
        ? `linear-gradient(135deg, ${accent}28 0%, ${accent}10 100%)`
        : 'rgba(255,255,255,0.04)',
      border: `1.5px solid ${isOutcome ? accent : 'rgba(255,255,255,0.12)'}`,
      borderRadius: 16,
      padding: '24px 22px',
      display: 'flex',
      flexDirection: 'column',
      gap: 8,
      boxShadow: isOutcome ? `0 0 32px ${accent}28` : 'none',
    }}>
      <div style={{ fontFamily: "Inter, ui-sans-serif, system-ui, sans-serif", fontSize: '10px', fontWeight: 700, letterSpacing: '0.18em', color: isOutcome ? accent : 'rgba(255,255,255,0.4)', textTransform: 'uppercase' }}>
        {isOutcome ? 'AFTER' : 'BEFORE'}
      </div>
      <div style={{ fontFamily: "Inter, ui-sans-serif, system-ui, sans-serif", fontSize: '22px', fontWeight: 800, color: isOutcome ? accent : 'rgba(255,255,255,0.9)', lineHeight: 1.2 }}>
        {node.label}
      </div>
      {node.value && (
        <div style={{ fontFamily: "Inter, ui-sans-serif, system-ui, sans-serif", fontSize: '26px', fontWeight: 900, color: accent }}>
          {node.value}
        </div>
      )}
      {node.description && (
        <div style={{ fontFamily: "Inter, ui-sans-serif, system-ui, sans-serif", fontSize: '13px', color: 'rgba(255,255,255,0.55)', lineHeight: 1.5 }}>
          {node.description}
        </div>
      )}
    </div>
  );
}

export function StateTransition(props: StateTransitionProps | any) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const resolvedProps: StateTransitionProps = (props as any).props || props;
  const duration_frames: number = (props as any).duration_frames || 180;

  const initial = resolvedProps.initial_state ?? { label: 'Initial State' };
  const trigger = resolvedProps.transition ?? { label: 'Trigger Event' };
  const final = resolvedProps.final_state ?? { label: 'New State' };
  const consequence = resolvedProps.consequence || null;
  const polarity = resolvedProps.polarity || 'neutral';
  const headerLabel = resolvedProps.header_label || 'STATE TRANSITION';

  const accentColor = POLARITY_COLORS[polarity] ?? '#38bdf8';

  const sceneOpacity = interpolate(frame, [0, Math.min(8, duration_frames - 1)], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });

  // Staggered timing
  const initialDelay = 8;
  const triggerDelay = safeSpringDelay(30, duration_frames, 0.5);
  const finalDelay = safeSpringDelay(55, duration_frames, 0.45);
  const consequenceDelay = safeSpringDelay(75, duration_frames, 0.4);

  // Trigger card spring
  const triggerSp = spring({ frame: Math.max(0, frame - triggerDelay), fps, config: { damping: 20, stiffness: 120, mass: 0.85 } });
  const triggerOpacity = triggerSp;
  const triggerScale = interpolate(triggerSp, [0, 1], [0.88, 1]);

  // Arrow animations
  const arrow1Opacity = interpolate(frame, [triggerDelay, triggerDelay + 14], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const arrow2Opacity = interpolate(frame, [finalDelay - 10, finalDelay + 4], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });

  // Consequence
  const consequenceSp = spring({ frame: Math.max(0, frame - consequenceDelay), fps, config: { damping: 18, stiffness: 100 } });

  return (
    <AbsoluteFill style={{ opacity: sceneOpacity }}>
      <EditorialBackdrop glowColor={accentColor} glowOpacity={0.09} />

      <AbsoluteFill style={{ zIndex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '80px 80px 60px' }}>

        {/* Header */}
        <div style={{ position: 'absolute', top: '56px', left: '100px', fontFamily: "Inter, ui-sans-serif, system-ui, sans-serif", fontSize: '11px', fontWeight: 700, letterSpacing: '0.22em', color: accentColor, textTransform: 'uppercase', opacity: 0.7 }}>
          {headerLabel}
        </div>

        {/* Main three-panel layout */}
        <div style={{ display: 'flex', flexDirection: 'row', alignItems: 'stretch', gap: 0, width: '100%', maxWidth: 1000 }}>

          {/* Initial state */}
          <StateCard node={initial} accent="rgba(255,255,255,0.4)" delay={initialDelay} frame={frame} fps={fps} isOutcome={false} />

          {/* Arrow 1 */}
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', width: 60, opacity: arrow1Opacity, flexShrink: 0 }}>
            <div style={{ color: 'rgba(255,255,255,0.3)', fontSize: '24px' }}>→</div>
          </div>

          {/* Trigger card */}
          <div style={{
            opacity: triggerOpacity,
            transform: `scale(${triggerScale})`,
            flex: 1,
            minWidth: 200,
            maxWidth: 240,
            background: `rgba(255,255,255,0.06)`,
            border: `1.5px solid rgba(255,255,255,0.18)`,
            borderRadius: 16,
            padding: '20px 18px',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            gap: 8,
            textAlign: 'center',
          }}>
            <div style={{ fontFamily: "Inter, ui-sans-serif, system-ui, sans-serif", fontSize: '10px', fontWeight: 700, letterSpacing: '0.18em', color: accentColor, opacity: 0.7 }}>
              TRIGGER
            </div>
            <div style={{ fontFamily: "Inter, ui-sans-serif, system-ui, sans-serif", fontSize: '17px', fontWeight: 700, color: 'rgba(255,255,255,0.85)', lineHeight: 1.3 }}>
              {trigger.label}
            </div>
            {trigger.value && (
              <div style={{ fontFamily: "Inter, ui-sans-serif, system-ui, sans-serif", fontSize: '22px', fontWeight: 900, color: accentColor }}>
                {trigger.value}
              </div>
            )}
          </div>

          {/* Arrow 2 */}
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', width: 60, opacity: arrow2Opacity, flexShrink: 0 }}>
            <div style={{ color: accentColor, fontSize: '24px' }}>→</div>
          </div>

          {/* Final state */}
          <StateCard node={final} accent={accentColor} delay={finalDelay} frame={frame} fps={fps} isOutcome={true} />
        </div>

        {/* Consequence */}
        {consequence && (
          <div style={{
            marginTop: 36,
            opacity: consequenceSp,
            transform: `translateY(${interpolate(consequenceSp, [0, 1], [12, 0])}px)`,
            background: `${accentColor}14`,
            border: `1px solid ${accentColor}40`,
            borderRadius: 10,
            padding: '12px 28px',
            fontFamily: "Inter, ui-sans-serif, system-ui, sans-serif",
            fontSize: '15px',
            color: 'rgba(255,255,255,0.65)',
            textAlign: 'center',
          }}>
            {consequence}
          </div>
        )}
      </AbsoluteFill>
    </AbsoluteFill>
  );
}
