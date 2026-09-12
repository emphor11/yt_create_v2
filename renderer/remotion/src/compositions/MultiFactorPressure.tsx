import React from 'react';
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { tokens } from '../design-tokens';
import { MultiFactorPressureProps, FactorItemProp } from '../types';
import { safeAnimationWindow, safeSpringDelay, safeKeyframeWindow } from '../animation-safety';

interface FactorGeometry {
  cardHeight: number;
  gap: number;
  marginTop: number;
  centersY: number[];
  labelFontSize: number;
  valueFontSize: number;
  badgeFontSize: number;
  padding: string;
}

function getFactorGeometry(count: number): FactorGeometry {
  if (count <= 2) {
    const cardHeight = 150;
    const gap = 36;
    const marginTop = 82; // (500 - (150*2 + 36)) / 2 = 82
    return {
      cardHeight,
      gap,
      marginTop,
      centersY: [
        marginTop + 75,
        marginTop + 150 + gap + 75,
      ],
      labelFontSize: 22,
      valueFontSize: 24,
      badgeFontSize: 13,
      padding: '22px 28px',
    };
  }
  if (count === 3) {
    const cardHeight = 116;
    const gap = 24;
    const marginTop = 52; // (500 - (116*3 + 24*2)) / 2 = 52
    return {
      cardHeight,
      gap,
      marginTop,
      centersY: [
        marginTop + 58,
        marginTop + 116 + gap + 58,
        marginTop + 2 * (116 + gap) + 58,
      ],
      labelFontSize: 20,
      valueFontSize: 22,
      badgeFontSize: 12,
      padding: '18px 24px',
    };
  }
  // 4 factors
  const cardHeight = 90;
  const gap = 16;
  const marginTop = 46; // (500 - (90*4 + 16*3)) / 2 = 46
  return {
    cardHeight,
    gap,
    marginTop,
    centersY: [
      marginTop + 45,
      marginTop + 90 + gap + 45,
      marginTop + 2 * (90 + gap) + 45,
      marginTop + 3 * (90 + gap) + 45,
    ],
    labelFontSize: 17,
    valueFontSize: 19,
    badgeFontSize: 11,
    padding: '14px 20px',
  };
}

function getFactorColors(severity?: string | null) {
  const sev = (severity || '').toLowerCase();
  if (sev === 'critical' || sev === 'high') {
    return {
      stroke: tokens.accent.rose,
      bg: 'rgba(244, 63, 94, 0.12)',
      border: 'rgba(244, 63, 94, 0.35)',
      badgeBg: 'rgba(244, 63, 94, 0.2)',
      text: tokens.accent.rose,
    };
  }
  if (sev === 'medium' || sev === 'warning') {
    return {
      stroke: tokens.accent.amber,
      bg: 'rgba(245, 158, 11, 0.12)',
      border: 'rgba(245, 158, 11, 0.35)',
      badgeBg: 'rgba(245, 158, 11, 0.2)',
      text: tokens.accent.amber,
    };
  }
  if (sev === 'low' || sev === 'positive' || sev === 'growth') {
    return {
      stroke: tokens.accent.emerald,
      bg: 'rgba(16, 185, 129, 0.12)',
      border: 'rgba(16, 185, 129, 0.35)',
      badgeBg: 'rgba(16, 185, 129, 0.2)',
      text: tokens.accent.emerald,
    };
  }
  return {
    stroke: tokens.accent.cyan,
    bg: 'rgba(6, 182, 212, 0.10)',
    border: 'rgba(6, 182, 212, 0.30)',
    badgeBg: 'rgba(6, 182, 212, 0.18)',
    text: tokens.accent.cyan,
  };
}

export function MultiFactorPressure(props: MultiFactorPressureProps | any) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const resolvedProps: MultiFactorPressureProps =
    props?.props && typeof props.props === 'object' && !Array.isArray(props.props)
      ? props.props
      : props || {};
  const duration_frames =
    props?.duration_frames || props?.props?.duration_frames || 180;

  const rawFactors: FactorItemProp[] =
    Array.isArray(resolvedProps.factors) && resolvedProps.factors.length > 0
      ? resolvedProps.factors.slice(0, 4)
      : [
          { label: 'High Inflation Rate', value: '7.2%', severity: 'critical' },
          { label: 'Weak Asset Yields', value: '2.5%', severity: 'medium' },
        ];

  const factorCount = Math.min(Math.max(rawFactors.length, 2), 4);
  const factors = rawFactors.slice(0, factorCount);
  const geometry = getFactorGeometry(factorCount);

  const combinedLabel = resolvedProps.combinedLabel || 'Severe Capital Depletion';
  const combinedSeverity = (resolvedProps.combinedSeverity || 'critical').toLowerCase();
  const outcomeNote = resolvedProps.outcomeNote || null;
  const outcomeValue = resolvedProps.outcomeValue || null;
  const outcomeHeaderLabel = resolvedProps.outcomeHeaderLabel || null;
  const headerLabel = resolvedProps.headerLabel || null;
  const polarity = (resolvedProps.polarity || combinedSeverity).toLowerCase();

  // Color theme for outcome core
  const isPositive = polarity === 'positive' || combinedSeverity === 'low';
  const isMedium = combinedSeverity === 'medium';
  
  let coreAccentColor = tokens.accent.rose;
  let coreGlowColor = 'rgba(244, 63, 94, 0.35)';
  let coreBgTint = 'rgba(244, 63, 94, 0.06)';
  let coreBadgeBg = 'rgba(244, 63, 94, 0.16)';
  let coreBadgeText = tokens.accent.rose;
  let defaultHeaderTag = 'CRITICAL THREAT // CONVERGENCE';

  if (isPositive) {
    coreAccentColor = tokens.accent.emerald;
    coreGlowColor = 'rgba(16, 185, 129, 0.35)';
    coreBgTint = 'rgba(16, 185, 129, 0.06)';
    coreBadgeBg = 'rgba(16, 185, 129, 0.16)';
    coreBadgeText = tokens.accent.emerald;
    defaultHeaderTag = 'POSITIVE SYNERGY // ACCELERATION';
  } else if (isMedium) {
    coreAccentColor = tokens.accent.amber;
    coreGlowColor = 'rgba(245, 158, 11, 0.35)';
    coreBgTint = 'rgba(245, 158, 11, 0.06)';
    coreBadgeBg = 'rgba(245, 158, 11, 0.16)';
    coreBadgeText = tokens.accent.amber;
    defaultHeaderTag = 'MODERATE PRESSURE // SYSTEMIC';
  }

  // Scene fade in
  const sceneOpacity = interpolate(
    frame,
    [0, Math.min(8, Math.max(1, duration_frames - 1))],
    [0, 1],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
  );

  // Ray progress
  const [rayStart, rayEnd] = safeAnimationWindow(18, 44, duration_frames);
  const rayProgress = interpolate(frame, [rayStart, rayEnd], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // Central Core Entrance Spring
  const coreDelay = safeSpringDelay(34, duration_frames, 0.5);
  const coreSpring = spring({
    frame: Math.max(0, frame - coreDelay),
    fps,
    config: { mass: 1.1, damping: 16, stiffness: 105 },
  });
  const coreScale = interpolate(coreSpring, [0, 1], [0.88, 1]);
  const coreOpacity = interpolate(coreSpring, [0, 1], [0, 1]);

  // Glow pulse keyframes on impact
  const pulseFrames = safeKeyframeWindow([62, 70, 80], duration_frames);
  const pulseOpacity = interpolate(
    frame,
    pulseFrames,
    [0.4, 1.0, 0.65],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
  );

  // Impact ripple at focal point
  const impactProgress = interpolate(frame, [rayEnd - 4, rayEnd + 14], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const rippleRadius = interpolate(impactProgress, [0, 1], [4, 28]);
  const rippleOpacity = interpolate(impactProgress, [0, 0.4, 1], [0, 0.8, 0]);

  // Geometry dimensions
  const stageHeight = 500;
  const connectorWidth = 260;
  const targetX = 245;
  const targetY = 250;

  return (
    <AbsoluteFill
      style={{
        backgroundColor: tokens.bg.base,
        fontFamily: tokens.font.family,
        opacity: sceneOpacity,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '50px 80px',
        overflow: 'hidden',
      }}
    >
      {/* Background radial gradient mesh */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          backgroundImage: `
            radial-gradient(circle at 75% 50%, ${coreBgTint} 0%, transparent 60%),
            radial-gradient(circle at 20% 30%, rgba(6, 182, 212, 0.04) 0%, transparent 50%)
          `,
          pointerEvents: 'none',
        }}
      />

      {/* Top Header Bar */}
      <div
        style={{
          width: '100%',
          maxWidth: '1440px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: '36px',
          borderBottom: `1px solid ${tokens.bg.border}`,
          paddingBottom: '16px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div
            style={{
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              backgroundColor: coreAccentColor,
              boxShadow: `0 0 10px ${coreAccentColor}`,
            }}
          />
          <span
            style={{
              fontSize: '13px',
              fontWeight: 800,
              textTransform: 'uppercase',
              letterSpacing: '0.12em',
              color: tokens.text.secondary,
            }}
          >
            {headerLabel || defaultHeaderTag}
          </span>
        </div>
        <span
          style={{
            fontSize: '12px',
            fontWeight: 700,
            textTransform: 'uppercase',
            letterSpacing: '0.1em',
            color: tokens.text.muted,
          }}
        >
          {factorCount} CONVERGING FORCES
        </span>
      </div>

      {/* Main Convergence Stage */}
      <div
        style={{
          display: 'flex',
          flexDirection: 'row',
          alignItems: 'center',
          justifyContent: 'center',
          width: '100%',
          maxWidth: '1440px',
          height: `${stageHeight}px`,
          position: 'relative',
        }}
      >
        {/* Left Column: Factor Cards Stack */}
        <div
          style={{
            width: '480px',
            height: `${stageHeight}px`,
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'flex-start',
            paddingTop: `${geometry.marginTop}px`,
            gap: `${geometry.gap}px`,
            zIndex: 2,
          }}
        >
          {factors.map((factor, index) => {
            const factorDelay = safeSpringDelay(6 + index * 8, duration_frames, 0.35);
            const factorSpring = spring({
              frame: Math.max(0, frame - factorDelay),
              fps,
              config: { damping: 14, stiffness: 120 },
            });
            const fX = interpolate(factorSpring, [0, 1], [-45, 0]);
            const fOpacity = interpolate(factorSpring, [0, 1], [0, 1]);

            const colors = getFactorColors(factor.severity);

            return (
              <div
                key={index}
                style={{
                  height: `${geometry.cardHeight}px`,
                  opacity: fOpacity,
                  transform: `translateX(${fX}px)`,
                  backgroundColor: tokens.bg.cardLeft,
                  borderRadius: tokens.radius.card,
                  border: `1px solid ${colors.border}`,
                  borderLeft: `5px solid ${colors.stroke}`,
                  padding: geometry.padding,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  boxShadow: `0 12px 28px -10px rgba(0, 0, 0, 0.5), 0 0 16px ${colors.bg}`,
                  position: 'relative',
                  overflow: 'hidden',
                }}
              >
                {/* Subtle internal gradient overlay */}
                <div
                  style={{
                    position: 'absolute',
                    inset: 0,
                    background: `linear-gradient(90deg, ${colors.bg} 0%, transparent 60%)`,
                    pointerEvents: 'none',
                  }}
                />

                <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', zIndex: 1 }}>
                  <div
                    style={{
                      fontSize: `${geometry.labelFontSize}px`,
                      fontWeight: 600,
                      color: tokens.text.primary,
                      lineHeight: 1.25,
                    }}
                  >
                    {factor.label}
                  </div>
                  {factor.value && (
                    <div
                      style={{
                        fontSize: `${geometry.valueFontSize}px`,
                        fontWeight: 800,
                        color: colors.stroke,
                        letterSpacing: '-0.02em',
                      }}
                    >
                      {factor.value}
                    </div>
                  )}
                </div>

                {factor.severity && (
                  <div
                    style={{
                      fontSize: `${geometry.badgeFontSize}px`,
                      fontWeight: 800,
                      textTransform: 'uppercase',
                      letterSpacing: '0.08em',
                      color: colors.text,
                      backgroundColor: colors.badgeBg,
                      border: `1px solid ${colors.border}`,
                      padding: factorCount >= 4 ? '4px 8px' : '6px 12px',
                      borderRadius: tokens.radius.chip,
                      zIndex: 1,
                      whiteSpace: 'nowrap',
                    }}
                  >
                    {factor.severity}
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Middle: Inward Converging SVG Connector */}
        <div
          style={{
            width: `${connectorWidth}px`,
            height: `${stageHeight}px`,
            position: 'relative',
            zIndex: 1,
          }}
        >
          <svg
            width={connectorWidth}
            height={stageHeight}
            viewBox={`0 0 ${connectorWidth} ${stageHeight}`}
            style={{ overflow: 'visible' }}
          >
            <defs>
              {/* User space filter to prevent 0-height clipping */}
              <filter
                id="rayGlow"
                filterUnits="userSpaceOnUse"
                x="-50"
                y="-50"
                width={connectorWidth + 100}
                height={stageHeight + 100}
              >
                <feGaussianBlur stdDeviation="3.5" result="blur" />
                <feMerge>
                  <feMergeNode in="blur" />
                  <feMergeNode in="SourceGraphic" />
                </feMerge>
              </filter>
            </defs>

            {/* Render converging bezier rays */}
            {geometry.centersY.map((yStart, idx) => {
              const factor = factors[idx];
              const colors = getFactorColors(factor?.severity);

              // Path geometry
              const isStraight = Math.abs(yStart - targetY) < 4;
              const pathD = isStraight
                ? `M 0 ${yStart} L ${targetX} ${targetY}`
                : `M 0 ${yStart} C 95 ${yStart}, 175 ${targetY}, ${targetX} ${targetY}`;

              const approxLen = isStraight ? targetX : 295;

              return (
                <g key={idx}>
                  {/* Subtle background track */}
                  <path
                    d={pathD}
                    stroke="rgba(255, 255, 255, 0.08)"
                    strokeWidth="2.5"
                    fill="none"
                    strokeLinecap="round"
                  />
                  {/* Dynamic laser ray */}
                  <path
                    d={pathD}
                    stroke={colors.stroke}
                    strokeWidth="3.5"
                    fill="none"
                    strokeLinecap="round"
                    strokeDasharray={approxLen}
                    strokeDashoffset={approxLen * (1 - rayProgress)}
                    filter="url(#rayGlow)"
                  />
                </g>
              );
            })}

            {/* Convergence Focal Target Shockwave Ripple */}
            {rayProgress > 0.85 && (
              <circle
                cx={targetX}
                cy={targetY}
                r={rippleRadius}
                fill="none"
                stroke={coreAccentColor}
                strokeWidth="2"
                opacity={rippleOpacity}
              />
            )}

            {/* Convergence Arrow Head */}
            <path
              d={`M ${targetX - 16} ${targetY - 11} L ${targetX} ${targetY} L ${targetX - 16} ${targetY + 11}`}
              stroke={coreAccentColor}
              strokeWidth="4"
              fill="none"
              strokeLinecap="round"
              strokeLinejoin="round"
              opacity={rayProgress > 0.8 ? 1 : 0}
            />
          </svg>
        </div>

        {/* Right Column: Central Outcome Core (~60% Dominance) */}
        <div
          style={{
            position: 'relative',
            width: '660px',
            height: `${stageHeight}px`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 2,
          }}
        >
          {/* Atmospheric Radial Glow Halo behind card */}
          <div
            style={{
              position: 'absolute',
              width: '600px',
              height: '600px',
              borderRadius: '50%',
              background: `radial-gradient(circle, ${coreGlowColor} 0%, rgba(0,0,0,0) 70%)`,
              opacity: coreOpacity * 0.5,
              transform: 'translate(-50%, -50%)',
              left: '50%',
              top: '50%',
              pointerEvents: 'none',
              zIndex: 0,
            }}
          />

          {/* Outcome Core Card */}
          <div
            style={{
              opacity: coreOpacity,
              transform: `scale(${coreScale})`,
              width: '100%',
              height: '100%',
              backgroundColor: tokens.bg.surface,
              borderRadius: tokens.radius.card,
              border: `2px solid ${coreAccentColor}`,
              boxShadow: `0 28px 70px -15px rgba(0,0,0,0.85), 0 0 ${45 * pulseOpacity}px ${coreGlowColor}`,
              padding: '40px 44px',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
              position: 'relative',
              overflow: 'hidden',
              zIndex: 1,
            }}
          >
            {/* Ambient internal card sheen */}
            <div
              style={{
                position: 'absolute',
                inset: 0,
                background: `linear-gradient(135deg, ${coreBgTint} 0%, transparent 60%)`,
                pointerEvents: 'none',
              }}
            />

            {/* Top Eyebrow Chip */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', zIndex: 1 }}>
              <div
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '8px',
                  padding: '7px 15px',
                  borderRadius: tokens.radius.chip,
                  backgroundColor: coreBadgeBg,
                  border: `1px solid ${coreAccentColor}50`,
                }}
              >
                <div
                  style={{
                    width: '7px',
                    height: '7px',
                    borderRadius: '50%',
                    backgroundColor: coreBadgeText,
                    boxShadow: `0 0 8px ${coreBadgeText}`,
                  }}
                />
                <span
                  style={{
                    color: coreBadgeText,
                    fontSize: '13px',
                    fontWeight: 800,
                    textTransform: 'uppercase',
                    letterSpacing: '0.08em',
                  }}
                >
                  {outcomeHeaderLabel || `${combinedSeverity.toUpperCase()} THREAT`}
                </span>
              </div>

              <div
                style={{
                  fontSize: '12px',
                  fontWeight: 700,
                  color: tokens.text.muted,
                  letterSpacing: '0.05em',
                  textTransform: 'uppercase',
                }}
              >
                NET IMPACT
              </div>
            </div>

            {/* Middle: Title & Optional Hero Outcome Value */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', zIndex: 1, margin: 'auto 0' }}>
              <div
                style={{
                  fontSize: outcomeValue ? (factorCount >= 4 ? '32px' : '36px') : '40px',
                  fontWeight: 800,
                  color: tokens.text.primary,
                  lineHeight: 1.18,
                  letterSpacing: '-0.02em',
                }}
              >
                {combinedLabel}
              </div>

              {outcomeValue && (
                <div style={{ display: 'flex', alignItems: 'baseline', gap: '14px', marginTop: '4px' }}>
                  <div
                    style={{
                      fontSize: '54px',
                      fontWeight: 900,
                      color: coreAccentColor,
                      letterSpacing: '-0.03em',
                      lineHeight: 1,
                      textShadow: `0 0 24px ${coreGlowColor}`,
                    }}
                  >
                    {outcomeValue}
                  </div>
                  <span
                    style={{
                      fontSize: '14px',
                      fontWeight: 700,
                      color: tokens.text.secondary,
                      textTransform: 'uppercase',
                      letterSpacing: '0.06em',
                    }}
                  >
                    {isPositive ? 'Net Acceleration' : 'Combined Deficit'}
                  </span>
                </div>
              )}
            </div>

            {/* Bottom: Mechanism Note & Convergence Footer */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', zIndex: 1 }}>
              {outcomeNote && (
                <div
                  style={{
                    backgroundColor: 'rgba(255, 255, 255, 0.04)',
                    border: `1px solid ${tokens.bg.border}`,
                    borderRadius: '12px',
                    padding: '14px 18px',
                    display: 'flex',
                    alignItems: 'flex-start',
                    gap: '10px',
                  }}
                >
                  <span
                    style={{
                      fontSize: '11px',
                      fontWeight: 800,
                      color: tokens.accent.cyan,
                      textTransform: 'uppercase',
                      letterSpacing: '0.08em',
                      marginTop: '2px',
                    }}
                  >
                    CAUSE:
                  </span>
                  <div
                    style={{
                      fontSize: '16px',
                      fontWeight: 500,
                      color: tokens.text.secondary,
                      lineHeight: 1.4,
                    }}
                  >
                    {outcomeNote}
                  </div>
                </div>
              )}

              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  paddingTop: '6px',
                  borderTop: `1px solid ${tokens.bg.border}`,
                  fontSize: '12px',
                  fontWeight: 600,
                  color: tokens.text.muted,
                }}
              >
                <span>STATUS: CONVERGENCE ACTIVE</span>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <div
                    style={{
                      width: '6px',
                      height: '6px',
                      borderRadius: '50%',
                      backgroundColor: coreAccentColor,
                      opacity: pulseOpacity,
                    }}
                  />
                  <span>REAL-TIME MULTI-FACTOR MODEL</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
}
