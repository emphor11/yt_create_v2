import React from 'react';
import { AbsoluteFill, interpolate, spring, useCurrentFrame } from 'remotion';
import { tokens } from '../design-tokens';
import { DebtAmortizationScheduleProps } from '../types';
import { safeSpringDelay } from '../animation-safety';

export function DebtAmortizationSchedule(childProps: {
  scene_id: string;
  composition: string;
  fps: number;
  duration_frames: number;
  props: DebtAmortizationScheduleProps;
  frame_spans?: any[];
}) {
  const { props, duration_frames, fps = 30 } = childProps;
  const frame = useCurrentFrame();

  const {
    headerLabel = 'LOAN AMORTIZATION SCHEDULE',
    loanAmount,
    loanLabel = 'Original Principal',
    interestRate,
    tenure,
    paymentAmount,
    totalInterest,
    periods = [],
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

  // Overview bar entrance
  const overviewDelay = safeSpringDelay(10, duration_frames, 0.2);
  const overviewSpring = spring({
    frame: Math.max(0, frame - overviewDelay),
    fps,
    config: tokens.motion.reveal,
  });

  // Center visual entrance
  const centerDelay = safeSpringDelay(18, duration_frames, 0.35);
  const centerSpring = spring({
    frame: Math.max(0, frame - centerDelay),
    fps,
    config: tokens.motion.impact,
  });

  // Annotation entrance
  const annotationDelay = safeSpringDelay(32, duration_frames, 0.7);
  const annotationSpring = spring({
    frame: Math.max(0, frame - annotationDelay),
    fps,
    config: tokens.motion.gentle,
  });

  const displayPeriods = periods.length > 0 ? periods.slice(0, 3) : null;

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
      {/* 1. Header Eyebrow */}
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

      {/* 2. Top Loan Metrics Bar */}
      <div
        style={{
          transform: `translateY(${interpolate(overviewSpring, [0, 1], [-20, 0])}px)`,
          opacity: overviewSpring,
          display: 'grid',
          gridTemplateColumns: 'repeat(4, 1fr)',
          gap: 16,
          marginTop: 14,
        }}
      >
        {/* Principal */}
        <div
          style={{
            backgroundColor: tokens.bg.surface,
            border: `1px solid ${tokens.accent.emerald}60`,
            borderRadius: tokens.radius.chip,
            padding: '16px 20px',
          }}
        >
          <div style={{ color: tokens.text.secondary, fontSize: 18, fontWeight: 500 }}>{loanLabel}</div>
          <div style={{ color: tokens.accent.emerald, fontSize: 32, fontWeight: 800, marginTop: 4 }}>{loanAmount}</div>
        </div>

        {/* Tenure */}
        <div
          style={{
            backgroundColor: tokens.bg.surface,
            border: `1px solid ${tokens.bg.border}`,
            borderRadius: tokens.radius.chip,
            padding: '16px 20px',
          }}
        >
          <div style={{ color: tokens.text.secondary, fontSize: 18, fontWeight: 500 }}>Tenure</div>
          <div style={{ color: tokens.text.primary, fontSize: 32, fontWeight: 800, marginTop: 4 }}>{tenure || 'Loan Horizon'}</div>
        </div>

        {/* Interest Rate */}
        <div
          style={{
            backgroundColor: tokens.bg.surface,
            border: `1px solid ${tokens.bg.border}`,
            borderRadius: tokens.radius.chip,
            padding: '16px 20px',
          }}
        >
          <div style={{ color: tokens.text.secondary, fontSize: 18, fontWeight: 500 }}>Interest Rate</div>
          <div style={{ color: tokens.accent.amber, fontSize: 32, fontWeight: 800, marginTop: 4 }}>{interestRate || 'Base Rate'}</div>
        </div>

        {/* Monthly Payment */}
        <div
          style={{
            backgroundColor: tokens.bg.surface,
            border: `1px solid ${tokens.accent.rose}60`,
            borderRadius: tokens.radius.chip,
            padding: '16px 20px',
          }}
        >
          <div style={{ color: tokens.text.secondary, fontSize: 18, fontWeight: 500 }}>Monthly EMI</div>
          <div style={{ color: tokens.accent.rose, fontSize: 32, fontWeight: 800, marginTop: 4 }}>{paymentAmount || 'Monthly Pay'}</div>
        </div>
      </div>

      {/* 3. Central Amortization Dynamics Visualization */}
      <div
        style={{
          transform: `scale(${interpolate(centerSpring, [0, 1], [0.96, 1])})`,
          opacity: centerSpring,
          backgroundColor: tokens.bg.surface,
          borderRadius: tokens.radius.card,
          border: `1px solid ${tokens.bg.border}`,
          padding: '28px 40px',
          margin: '16px 0',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          gap: 20,
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span style={{ color: tokens.text.primary, fontSize: 22, fontWeight: 700 }}>
            {displayPeriods ? 'Payment Decomposition Across Loan Timeline' : 'Lifetime Loan Cost: Principal vs Interest Drag'}
          </span>
          <div style={{ display: 'flex', gap: 24, alignItems: 'center' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <div style={{ width: 12, height: 12, borderRadius: 3, backgroundColor: tokens.accent.rose }} />
              <span style={{ color: tokens.text.secondary, fontSize: 16 }}>Interest Cost</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <div style={{ width: 12, height: 12, borderRadius: 3, backgroundColor: tokens.accent.emerald }} />
              <span style={{ color: tokens.text.secondary, fontSize: 16 }}>Principal Reduction</span>
            </div>
          </div>
        </div>

        {displayPeriods ? (
          /* Render multi-period breakdown */
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            {displayPeriods.map((period, idx) => {
              const pDelay = safeSpringDelay(20 + idx * 8, duration_frames, 0.5);
              const pSpring = spring({ frame: Math.max(0, frame - pDelay), fps, config: tokens.motion.gentle });

              const pNum = period.principalNumeric || 30;
              const iNum = period.interestNumeric || 70;
              const sum = pNum + iNum;
              const principalPct = (pNum / sum) * 100 * pSpring;
              const interestPct = (iNum / sum) * 100 * pSpring;

              return (
                <div key={idx} style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 18 }}>
                    <span style={{ color: tokens.text.primary, fontWeight: 600 }}>{period.periodLabel}</span>
                    <span style={{ color: tokens.text.muted }}>
                      Principal: <strong style={{ color: tokens.accent.emerald }}>{period.principalShare}</strong> | Interest: <strong style={{ color: tokens.accent.rose }}>{period.interestShare}</strong>
                      {period.remainingBalance && ` | Bal: ${period.remainingBalance}`}
                    </span>
                  </div>
                  <div style={{ height: 20, width: '100%', backgroundColor: 'rgba(255,255,255,0.06)', borderRadius: tokens.radius.pill, overflow: 'hidden', display: 'flex' }}>
                    <div style={{ height: '100%', width: `${interestPct}%`, backgroundColor: tokens.accent.rose }} />
                    <div style={{ height: '100%', width: `${principalPct}%`, backgroundColor: tokens.accent.emerald }} />
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          /* Default 2-Phase Lifetime comparison */
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            {/* Early Phase */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 18 }}>
                <span style={{ color: tokens.text.primary, fontWeight: 600 }}>Early Phase (First 5–7 Years)</span>
                <span style={{ color: tokens.accent.rose, fontWeight: 700 }}>~70% Interest / 30% Principal</span>
              </div>
              <div style={{ height: 22, width: '100%', backgroundColor: 'rgba(255,255,255,0.06)', borderRadius: tokens.radius.pill, overflow: 'hidden', display: 'flex' }}>
                <div style={{ height: '100%', width: `${70 * centerSpring}%`, backgroundColor: tokens.accent.rose }} />
                <div style={{ height: '100%', width: `${30 * centerSpring}%`, backgroundColor: tokens.accent.emerald }} />
              </div>
            </div>

            {/* Late Phase */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 18 }}>
                <span style={{ color: tokens.text.primary, fontWeight: 600 }}>Late Phase (Final Years)</span>
                <span style={{ color: tokens.accent.emerald, fontWeight: 700 }}>~20% Interest / 80% Principal</span>
              </div>
              <div style={{ height: 22, width: '100%', backgroundColor: 'rgba(255,255,255,0.06)', borderRadius: tokens.radius.pill, overflow: 'hidden', display: 'flex' }}>
                <div style={{ height: '100%', width: `${20 * centerSpring}%`, backgroundColor: tokens.accent.rose }} />
                <div style={{ height: '100%', width: `${80 * centerSpring}%`, backgroundColor: tokens.accent.emerald }} />
              </div>
            </div>

            {totalInterest && (
              <div style={{ marginTop: 8, padding: '10px 16px', backgroundColor: 'rgba(244, 63, 94, 0.10)', border: `1px solid ${tokens.accent.rose}40`, borderRadius: tokens.radius.chip, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ color: tokens.text.secondary, fontSize: 18 }}>Total Lifetime Interest Outflow:</span>
                <span style={{ color: tokens.accent.rose, fontSize: 24, fontWeight: 800 }}>{totalInterest}</span>
              </div>
            )}
          </div>
        )}
      </div>

      {/* 4. Bottom Annotation */}
      {annotation ? (
        <div
          style={{
            transform: `translateY(${interpolate(annotationSpring, [0, 1], [20, 0])}px)`,
            opacity: annotationSpring,
            backgroundColor: 'rgba(24, 24, 27, 0.70)',
            borderLeft: `4px solid ${tokens.accent.amber}`,
            borderRadius: tokens.radius.chip,
            padding: '16px 24px',
            display: 'flex',
            alignItems: 'center',
            gap: 12,
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
