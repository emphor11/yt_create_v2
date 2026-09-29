import React from 'react';
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { tokens } from '../design-tokens';
import { TimelineMilestoneProps, TimelineMilestoneEventProp } from '../types';
import { safeSpringDelay } from '../animation-safety';

function EditorialBackdrop({ glowColor = '#38bdf8', glowOpacity = 0.08 }: { glowColor?: string; glowOpacity?: number }) {
  return (
    <AbsoluteFill style={{ backgroundColor: '#060911', overflow: 'hidden', pointerEvents: 'none', zIndex: 0 }}>
      <div style={{ position: 'absolute', inset: 0, background: 'radial-gradient(ellipse 95% 75% at 50% 46%, #0b1222 0%, #060913 65%, #020408 100%)' }} />
      <div style={{ position: 'absolute', width: '900px', height: '500px', left: '50%', top: '50%', transform: 'translate(-50%,-50%)', borderRadius: '50%', background: `radial-gradient(ellipse at center, ${glowColor} 0%, transparent 68%)`, filter: 'blur(60px)', opacity: glowOpacity }} />
    </AbsoluteFill>
  );
}

const POLARITY_COLORS: Record<string, string> = {
  positive: '#10b981',
  negative: '#f43f5e',
  warning: '#f59e0b',
  neutral: '#38bdf8',
};

function eventColor(polarity?: string | null): string {
  return POLARITY_COLORS[polarity ?? 'neutral'] ?? '#38bdf8';
}

export function TimelineMilestone(props: TimelineMilestoneProps | any) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const resolvedProps: TimelineMilestoneProps = (props as any).props || props;
  const duration_frames: number = (props as any).duration_frames || 180;

  const events: TimelineMilestoneEventProp[] = Array.isArray(resolvedProps.events) && resolvedProps.events.length >= 2
    ? resolvedProps.events.slice(0, 7)
    : [{ date: 'Start', label: 'Event A' }, { date: 'End', label: 'Event B' }];

  const title = resolvedProps.title || null;
  const headerLabel = resolvedProps.header_label || 'TIMELINE';
  const timeSpan = resolvedProps.time_span || null;
  const metricLabel = resolvedProps.metric_label || null;

  // Global accent = color of last event (or overall dominant polarity)
  const lastPolarity = events[events.length - 1]?.polarity ?? 'neutral';
  const accentColor = eventColor(lastPolarity);

  const sceneOpacity = interpolate(frame, [0, Math.min(8, duration_frames - 1)], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });

  const eventCount = events.length;
  const timelineBarDelay = 10;
  const barFill = interpolate(frame, [timelineBarDelay, timelineBarDelay + 50], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });

  // Each event appears along the timeline with stagger
  const eventDelayStep = Math.max(12, Math.round(40 / eventCount));
  const eventAnimations = events.map((_, i) => {
    const delay = safeSpringDelay(timelineBarDelay + i * eventDelayStep, duration_frames, 0.55);
    const sp = spring({ frame: Math.max(0, frame - delay), fps, config: { damping: 18, stiffness: 110, mass: 0.9 } });
    return { opacity: sp, y: interpolate(sp, [0, 1], [20, 0]) };
  });

  // Layout
  const TIMELINE_WIDTH = 980;
  const dotSize = 14;

  return (
    <AbsoluteFill style={{ opacity: sceneOpacity }}>
      <EditorialBackdrop glowColor={accentColor} glowOpacity={0.07} />

      <AbsoluteFill style={{ zIndex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '80px 80px 60px' }}>

        {/* Header row */}
        <div style={{ position: 'absolute', top: '56px', left: '100px', right: '100px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ fontFamily: "Inter, ui-sans-serif, system-ui, sans-serif", fontSize: '11px', fontWeight: 700, letterSpacing: '0.22em', color: accentColor, textTransform: 'uppercase', opacity: 0.7 }}>
            {headerLabel}
          </div>
          {timeSpan && (
            <div style={{ fontFamily: "Inter, ui-sans-serif, system-ui, sans-serif", fontSize: '10px', fontWeight: 600, color: 'rgba(255,255,255,0.35)', letterSpacing: '0.12em' }}>
              {timeSpan}
            </div>
          )}
        </div>

        {/* Title */}
        {title && (
          <div style={{ marginBottom: 48, fontFamily: "Inter, ui-sans-serif, system-ui, sans-serif", fontSize: '24px', fontWeight: 700, color: 'rgba(255,255,255,0.8)', textAlign: 'center' }}>
            {title}
          </div>
        )}

        {/* Metric label */}
        {metricLabel && (
          <div style={{ marginBottom: 16, fontFamily: "Inter, ui-sans-serif, system-ui, sans-serif", fontSize: '11px', fontWeight: 700, color: accentColor, letterSpacing: '0.16em', opacity: 0.7 }}>
            {metricLabel}
          </div>
        )}

        {/* Timeline bar + dots */}
        <div style={{ position: 'relative', width: TIMELINE_WIDTH, height: 80 }}>
          {/* Base track */}
          <div style={{ position: 'absolute', top: 38, left: 0, right: 0, height: 2, background: 'rgba(255,255,255,0.08)', borderRadius: 1 }} />
          {/* Animated fill */}
          <div style={{ position: 'absolute', top: 38, left: 0, height: 2, width: `${barFill * 100}%`, background: `linear-gradient(90deg, rgba(255,255,255,0.2) 0%, ${accentColor} 100%)`, borderRadius: 1, boxShadow: `0 0 8px ${accentColor}60` }} />

          {/* Event dots + tick marks */}
          {events.map((ev, i) => {
            const xPct = eventCount === 1 ? 50 : (i / (eventCount - 1)) * 100;
            const x = (xPct / 100) * TIMELINE_WIDTH;
            const color = eventColor(ev.polarity);
            const anim = eventAnimations[i];
            const aboveRow = i % 2 === 0;

            return (
              <div key={i} style={{ position: 'absolute', left: x, top: 0, transform: 'translateX(-50%)' }}>
                {/* Dot */}
                <div style={{
                  position: 'absolute',
                  top: 32,
                  left: -dotSize / 2,
                  width: dotSize,
                  height: dotSize,
                  borderRadius: '50%',
                  background: color,
                  boxShadow: `0 0 10px ${color}80`,
                  opacity: anim.opacity,
                }} />

                {/* Label card — alternates above/below */}
                <div style={{
                  position: 'absolute',
                  top: aboveRow ? undefined : 60,
                  bottom: aboveRow ? 52 : undefined,
                  left: -60,
                  width: 120,
                  opacity: anim.opacity,
                  transform: `translateY(${anim.y}px)`,
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  gap: 3,
                  textAlign: 'center',
                }}>
                  <div style={{ fontFamily: "Inter, ui-sans-serif, system-ui, sans-serif", fontSize: '10px', fontWeight: 700, color, letterSpacing: '0.10em' }}>
                    {ev.date}
                  </div>
                  {ev.value && (
                    <div style={{ fontFamily: "Inter, ui-sans-serif, system-ui, sans-serif", fontSize: '18px', fontWeight: 900, color, lineHeight: 1 }}>
                      {ev.value}
                    </div>
                  )}
                  <div style={{ fontFamily: "Inter, ui-sans-serif, system-ui, sans-serif", fontSize: '11px', color: 'rgba(255,255,255,0.6)', lineHeight: 1.3 }}>
                    {ev.label}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
}
