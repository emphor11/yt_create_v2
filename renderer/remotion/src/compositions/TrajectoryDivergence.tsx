import React from 'react';
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { tokens } from '../design-tokens';
import { TrajectoryDivergenceProps, TrajectoryPathProp } from '../types';
import { safeAnimationWindow, safeSpringDelay } from '../animation-safety';

// ---------------------------------------------------------------------------
// Atmospheric Editorial Backdrop (Cardless Full-Bleed 16:9)
// ---------------------------------------------------------------------------

function EditorialBackdrop() {
  return (
    <AbsoluteFill
      style={{
        backgroundColor: '#060911',
        overflow: 'hidden',
        pointerEvents: 'none',
        zIndex: 0,
      }}
    >
      {/* Deep Multi-stop Obsidian Vignette */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          background: 'radial-gradient(ellipse 95% 75% at 50% 50%, #0b1222 0%, #060913 65%, #020408 100%)',
        }}
      />

      {/* Subtle Horizontal Datum Gridlines */}
      <div
        style={{
          position: 'absolute',
          top: '84px',
          left: '120px',
          right: '120px',
          height: '1px',
          background: 'linear-gradient(90deg, transparent 0%, rgba(255, 255, 255, 0.04) 15%, rgba(255, 255, 255, 0.04) 85%, transparent 100%)',
        }}
      />
      <div
        style={{
          position: 'absolute',
          top: '540px',
          left: '120px',
          right: '120px',
          height: '1px',
          background: 'linear-gradient(90deg, transparent 0%, rgba(255, 255, 255, 0.025) 15%, rgba(255, 255, 255, 0.025) 85%, transparent 100%)',
        }}
      />
      <div
        style={{
          position: 'absolute',
          bottom: '84px',
          left: '120px',
          right: '120px',
          height: '1px',
          background: 'linear-gradient(90deg, transparent 0%, rgba(255, 255, 255, 0.035) 15%, rgba(255, 255, 255, 0.035) 85%, transparent 100%)',
        }}
      />
    </AbsoluteFill>
  );
}

// ---------------------------------------------------------------------------
// Analytical Cubic Bezier Position Calculator
// ---------------------------------------------------------------------------

function getCubicBezierPoint(
  t: number,
  p0: [number, number],
  p1: [number, number],
  p2: [number, number],
  p3: [number, number]
): [number, number] {
  const clampedT = Math.max(0, Math.min(1, t));
  const u = 1 - clampedT;
  const tt = clampedT * clampedT;
  const uu = u * u;
  const uuu = uu * u;
  const ttt = tt * clampedT;

  const x = uuu * p0[0] + 3 * uu * clampedT * p1[0] + 3 * u * tt * p2[0] + ttt * p3[0];
  const y = uuu * p0[1] + 3 * uu * clampedT * p1[1] + 3 * u * tt * p2[1] + ttt * p3[1];
  return [x, y];
}

// ---------------------------------------------------------------------------
// Path Geometry & Color Resolution
// ---------------------------------------------------------------------------

function resolvePathColors(
  path: TrajectoryPathProp | undefined,
  fallbackIndex: number
): { accentColor: string; glowRgb: string } {
  const tone = path?.tone?.toLowerCase();
  const dir = path?.direction?.toLowerCase();

  if (tone === 'positive') {
    return { accentColor: tokens.accent.emerald || '#10b981', glowRgb: '16, 185, 129' };
  }
  if (tone === 'negative') {
    return { accentColor: tokens.accent.rose || '#f43f5e', glowRgb: '244, 63, 94' };
  }
  if (tone === 'neutral') {
    return fallbackIndex === 0
      ? { accentColor: tokens.accent.cyan || '#38bdf8', glowRgb: '56, 189, 248' }
      : { accentColor: '#94a3b8', glowRgb: '148, 163, 184' };
  }

  // Infer from direction if tone is unspecified
  if (dir === 'up') {
    return { accentColor: tokens.accent.emerald || '#10b981', glowRgb: '16, 185, 129' };
  }
  if (dir === 'down') {
    return { accentColor: tokens.accent.rose || '#f43f5e', glowRgb: '244, 63, 94' };
  }

  // Fallbacks
  if (fallbackIndex === 0) {
    return { accentColor: tokens.accent.cyan || '#38bdf8', glowRgb: '56, 189, 248' };
  }
  return { accentColor: tokens.accent.amber || '#f59e0b', glowRgb: '245, 158, 11' };
}

function resolvePathEndpoints(
  pathA: TrajectoryPathProp | undefined,
  pathB: TrajectoryPathProp | undefined
): { yEndA: number; yEndB: number } {
  const dirA = pathA?.direction?.toLowerCase() || (pathA?.tone === 'negative' ? 'down' : 'up');
  const dirB = pathB?.direction?.toLowerCase() || (pathB?.tone === 'negative' ? 'down' : pathB?.tone === 'positive' ? 'up' : 'neutral');

  const baselineY = 540;

  // Case 1: Opposing directions (one up, one down)
  if (dirA === 'up' && dirB === 'down') {
    return { yEndA: 330, yEndB: 750 };
  }
  if (dirA === 'down' && dirB === 'up') {
    return { yEndA: 750, yEndB: 330 };
  }

  // Case 2: Both UP (e.g. Index Fund vs Active Fund)
  if (dirA === 'up' && dirB === 'up') {
    return { yEndA: 260, yEndB: 440 };
  }

  // Case 3: Both DOWN (e.g. Moderate vs Severe Decline)
  if (dirA === 'down' && dirB === 'down') {
    return { yEndA: 640, yEndB: 820 };
  }

  // Case 4: One UP, one Neutral/Flat
  if (dirA === 'up' && (dirB === 'neutral' || !dirB)) {
    return { yEndA: 330, yEndB: baselineY };
  }
  if ((dirA === 'neutral' || !dirA) && dirB === 'up') {
    return { yEndA: baselineY, yEndB: 330 };
  }

  // Case 5: One DOWN, one Neutral/Flat
  if (dirA === 'down' && (dirB === 'neutral' || !dirB)) {
    return { yEndA: 750, yEndB: baselineY };
  }
  if ((dirA === 'neutral' || !dirA) && dirB === 'down') {
    return { yEndA: baselineY, yEndB: 750 };
  }

  // Default: balanced separation
  return { yEndA: 360, yEndB: 720 };
}

// ---------------------------------------------------------------------------
// Main TrajectoryDivergence Component
// ---------------------------------------------------------------------------

export function TrajectoryDivergence(rawProps: TrajectoryDivergenceProps | any) {
  const frame = useCurrentFrame();
  const videoConfig = useVideoConfig();

  // Robust prop unwrapping supporting VideoAssembly wrapper and direct calls
  const resolvedProps: TrajectoryDivergenceProps = (rawProps as any)?.props || rawProps || {};
  const duration_frames = (rawProps as any)?.duration_frames || videoConfig?.durationInFrames || 180;
  const fps = (rawProps as any)?.fps || videoConfig?.fps || 30;

  const {
    headerLabel,
    timeHorizon,
    baselineLabel,
    pathA,
    pathB,
    divergenceGap,
    variant,
  } = resolvedProps;

  // Scene fade-in (frames 0..8)
  const sceneOpacity = interpolate(
    frame,
    [0, Math.min(8, Math.max(1, duration_frames - 1))],
    [0, 1],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
  );

  // Sub-threshold camera motion: subtle atmospheric zoom (1.000 -> 1.006)
  const cameraScale = interpolate(
    frame,
    [0, Math.max(1, duration_frames)],
    [1.000, 1.006],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
  );

  // -------------------------------------------------------------------------
  // Duration-Adaptive Choreography Windows
  // -------------------------------------------------------------------------
  const scaleRatio = Math.min(1, duration_frames / 120);

  // 1. Header & Baseline Origin Entrance
  const headerDelay = safeSpringDelay(Math.round(3 * scaleRatio), duration_frames, 0.08);
  const headerSpring = spring({
    frame: Math.max(0, frame - headerDelay),
    fps,
    config: tokens.motion.reveal,
  });

  const originDelay = safeSpringDelay(Math.round(6 * scaleRatio), duration_frames, 0.12);
  const originSpring = spring({
    frame: Math.max(0, frame - originDelay),
    fps,
    config: tokens.motion.reveal,
  });

  // 2. Trajectory Drawing Windows (Staggered kinetic start)
  const [curveAStart, curveAEnd] = safeAnimationWindow(
    Math.round(12 * scaleRatio),
    Math.round(52 * scaleRatio),
    duration_frames
  );
  const curveAProgress = interpolate(frame, [curveAStart, curveAEnd], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  const [curveBStart, curveBEnd] = safeAnimationWindow(
    Math.round(16 * scaleRatio),
    Math.round(56 * scaleRatio),
    duration_frames
  );
  const curveBProgress = interpolate(frame, [curveBStart, curveBEnd], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // 3. Endpoint Payoff Entrance (Precisely synchronized with path arrival)
  const endADelay = safeSpringDelay(Math.round(44 * scaleRatio), duration_frames, 0.58);
  const endASpring = spring({
    frame: Math.max(0, frame - endADelay),
    fps,
    config: tokens.motion.impact,
  });

  const endBDelay = safeSpringDelay(Math.round(48 * scaleRatio), duration_frames, 0.62);
  const endBSpring = spring({
    frame: Math.max(0, frame - endBDelay),
    fps,
    config: tokens.motion.impact,
  });

  // 4. Divergence Gap Bracket Reveal (Reveals after paths have separated)
  const gapDelay = safeSpringDelay(Math.round(56 * scaleRatio), duration_frames, 0.72);
  const gapSpring = spring({
    frame: Math.max(0, frame - gapDelay),
    fps,
    config: tokens.motion.impact,
  });

  // -------------------------------------------------------------------------
  // Geometric Coordinate Calculations (1920 x 1080 Viewport)
  // -------------------------------------------------------------------------
  const svgWidth = 1920;
  const svgHeight = 1080;

  // Shared origin coordinate on the left
  const xStart = 260;
  const yStart = 540; // baseline center

  // Terminal X coordinate for both trajectories (leaves 480px safe zone on right)
  const xEnd = 1380;
  const dx = xEnd - xStart;

  // Determine endpoints and colors based exclusively on props
  const { yEndA, yEndB } = resolvePathEndpoints(pathA, pathB);
  const colorConfigA = resolvePathColors(pathA, 0);
  const colorConfigB = resolvePathColors(pathB, 1);

  // Differentiate Path B cleanly if both paths share positive tone
  const finalColorA = colorConfigA.accentColor;
  let finalColorB = colorConfigB.accentColor;
  if (finalColorA === finalColorB && pathA?.tone === 'positive' && pathB?.tone === 'positive') {
    finalColorB = tokens.accent.cyan || '#38bdf8';
  }

  // Refined organic cubic Bezier control points:
  // Starts paired closely ($0 \to 30\%$), then visibly flares apart
  const dyA = yEndA - yStart;
  const cp1A: [number, number] = [xStart + dx * 0.30, yStart + dyA * 0.06];
  const cp2A: [number, number] = [xStart + dx * 0.68, yStart + dyA * 0.62];

  const dyB = yEndB - yStart;
  const cp1B: [number, number] = [xStart + dx * 0.30, yStart + dyB * 0.06];
  const cp2B: [number, number] = [xStart + dx * 0.68, yStart + dyB * 0.62];

  const p0: [number, number] = [xStart, yStart];
  const p3A: [number, number] = [xEnd, yEndA];
  const p3B: [number, number] = [xEnd, yEndB];

  const dPathA = `M ${p0[0]} ${p0[1]} C ${cp1A[0]} ${cp1A[1]}, ${cp2A[0]} ${cp2A[1]}, ${p3A[0]} ${p3A[1]}`;
  const dPathB = `M ${p0[0]} ${p0[1]} C ${cp1B[0]} ${cp1B[1]}, ${cp2B[0]} ${cp2B[1]}, ${p3B[0]} ${p3B[1]}`;

  const totalLength = 1450;
  const strokeOffsetA = totalLength * (1 - curveAProgress);
  const strokeOffsetB = totalLength * (1 - curveBProgress);

  // Exact lead marker coordinates along curves
  const [leadAX, leadAY] = getCubicBezierPoint(curveAProgress, p0, cp1A, cp2A, p3A);
  const [leadBX, leadBY] = getCubicBezierPoint(curveBProgress, p0, cp1B, cp2B, p3B);

  // Dynamic font sizing for endpoints to prevent overflow
  const endValAStr = pathA?.endValue || '';
  const endValBStr = pathB?.endValue || '';
  const fontSizeA = endValAStr.length > 14 ? 36 : endValAStr.length > 9 ? 46 : 58;
  const fontSizeB = endValBStr.length > 14 ? 36 : endValBStr.length > 9 ? 46 : 58;

  // Header display string
  const displayHeader = (headerLabel || 'TRAJECTORY DIVERGENCE').toUpperCase();

  // Gap geometry (midpoint between endpoints)
  const gapCenterY = (yEndA + yEndB) / 2;
  const hasDivergenceGap = Boolean(divergenceGap);
  const gapTopY = Math.min(yEndA, yEndB);
  const gapBottomY = Math.max(yEndA, yEndB);

  return (
    <AbsoluteFill
      style={{
        backgroundColor: '#060911',
        fontFamily: tokens.font.family,
        opacity: sceneOpacity,
        transform: `scale(${cameraScale})`,
        overflow: 'hidden',
      }}
    >
      <EditorialBackdrop />

      {/* ----------------------------------------------------------------- */}
      {/* 1. TOP EDITORIAL SAFE ZONE (Header & Temporal Horizon)           */}
      {/* ----------------------------------------------------------------- */}
      <div
        style={{
          position: 'absolute',
          top: '44px',
          left: '120px',
          right: '120px',
          height: '48px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          opacity: headerSpring,
          transform: `translateY(${interpolate(headerSpring, [0, 1], [-14, 0])}px)`,
          zIndex: 10,
        }}
      >
        {/* Left: Topic / Category Tag */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div
            style={{
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              backgroundColor: finalColorA,
              boxShadow: `0 0 10px ${finalColorA}`,
            }}
          />
          <span
            style={{
              fontSize: '14px',
              fontWeight: 700,
              textTransform: 'uppercase',
              letterSpacing: '0.16em',
              color: '#94a3b8',
            }}
          >
            {displayHeader}
          </span>
        </div>

        {/* Right: Time Horizon Chip */}
        {timeHorizon && (
          <div
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '7px',
              fontSize: '13px',
              fontWeight: 600,
              color: '#cbd5e1',
              backgroundColor: 'rgba(255, 255, 255, 0.04)',
              border: '1px solid rgba(255, 255, 255, 0.08)',
              padding: '6px 14px',
              borderRadius: tokens.radius.chip,
              letterSpacing: '0.06em',
              textTransform: 'uppercase',
            }}
          >
            <span style={{ color: '#64748b' }}>HORIZON</span>
            <span style={{ color: '#f8fafc', fontWeight: 700 }}>{timeHorizon}</span>
          </div>
        )}
      </div>

      {/* ----------------------------------------------------------------- */}
      {/* 2. SWEEPING FULL-CANVAS SVG TRAJECTORIES                          */}
      {/* ----------------------------------------------------------------- */}
      <svg
        viewBox={`0 0 ${svgWidth} ${svgHeight}`}
        style={{
          position: 'absolute',
          inset: 0,
          width: '100%',
          height: '100%',
          overflow: 'visible',
          zIndex: 5,
        }}
      >
        <defs>
          <filter id="divergenceGlow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="3.5" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
          </filter>

          {/* Chromatic progression gradients from shared origin to outcome colors */}
          <linearGradient id="gradPathA" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#64748b" stopOpacity="0.8" />
            <stop offset="35%" stopColor="#94a3b8" />
            <stop offset="100%" stopColor={finalColorA} />
          </linearGradient>

          <linearGradient id="gradPathB" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#64748b" stopOpacity="0.8" />
            <stop offset="35%" stopColor="#94a3b8" />
            <stop offset="100%" stopColor={finalColorB} />
          </linearGradient>
        </defs>

        {/* Baseline Horizontal Axis Guide */}
        <line
          x1={xStart - 30}
          y1={yStart}
          x2={xEnd + 30}
          y2={yStart}
          stroke="rgba(255, 255, 255, 0.04)"
          strokeWidth="1.5"
          strokeDasharray="6 6"
        />

        {/* Path A (Primary Trajectory Curve) */}
        <path
          d={dPathA}
          fill="none"
          stroke="url(#gradPathA)"
          strokeWidth="4.5"
          strokeLinecap="round"
          strokeDasharray={totalLength}
          strokeDashoffset={strokeOffsetA}
          filter="url(#divergenceGlow)"
        />

        {/* Path B (Secondary Trajectory Curve) */}
        <path
          d={dPathB}
          fill="none"
          stroke="url(#gradPathB)"
          strokeWidth="4.5"
          strokeLinecap="round"
          strokeDasharray={totalLength}
          strokeDashoffset={strokeOffsetB}
          filter="url(#divergenceGlow)"
        />

        {/* Shared Origin Indicator Node */}
        <g opacity={originSpring} transform={`scale(${originSpring})`} style={{ transformOrigin: `${p0[0]}px ${p0[1]}px` }}>
          <circle cx={p0[0]} cy={p0[1]} r="6" fill="#f8fafc" />
          <circle cx={p0[0]} cy={p0[1]} r="14" fill="none" stroke="#64748b" strokeWidth="1.5" opacity="0.45" />
        </g>

        {/* Kinetic Lead Point A */}
        {curveAProgress > 0.01 && curveAProgress < 0.99 && (
          <g>
            <circle
              cx={leadAX}
              cy={leadAY}
              r="4.5"
              fill="#ffffff"
              style={{ filter: 'drop-shadow(0 0 6px #ffffff)' }}
            />
            <circle
              cx={leadAX}
              cy={leadAY}
              r="10"
              fill="none"
              stroke={finalColorA}
              strokeWidth="1.5"
              opacity="0.65"
            />
          </g>
        )}

        {/* Kinetic Lead Point B */}
        {curveBProgress > 0.01 && curveBProgress < 0.99 && (
          <g>
            <circle
              cx={leadBX}
              cy={leadBY}
              r="4.5"
              fill="#ffffff"
              style={{ filter: 'drop-shadow(0 0 6px #ffffff)' }}
            />
            <circle
              cx={leadBX}
              cy={leadBY}
              r="10"
              fill="none"
              stroke={finalColorB}
              strokeWidth="1.5"
              opacity="0.65"
            />
          </g>
        )}

        {/* Path A Endpoint Node */}
        <g opacity={endASpring} transform={`scale(${endASpring})`} style={{ transformOrigin: `${p3A[0]}px ${p3A[1]}px` }}>
          <circle cx={p3A[0]} cy={p3A[1]} r="7" fill={finalColorA} />
          <circle cx={p3A[0]} cy={p3A[1]} r="16 * endASpring" fill="none" stroke={finalColorA} strokeWidth="1.5" opacity="0.35" />
        </g>

        {/* Path B Endpoint Node */}
        <g opacity={endBSpring} transform={`scale(${endBSpring})`} style={{ transformOrigin: `${p3B[0]}px ${p3B[1]}px` }}>
          <circle cx={p3B[0]} cy={p3B[1]} r="7" fill={finalColorB} />
          <circle cx={p3B[0]} cy={p3B[1]} r="16 * endBSpring" fill="none" stroke={finalColorB} strokeWidth="1.5" opacity="0.35" />
        </g>

        {/* Divergence Gap Vertical Bracket (Rendered ONLY if divergenceGap prop is provided) */}
        {hasDivergenceGap && (
          <g opacity={gapSpring}>
            <line
              x1={xEnd}
              y1={gapTopY + 12}
              x2={xEnd}
              y2={gapBottomY - 12}
              stroke="rgba(245, 158, 11, 0.45)"
              strokeWidth="1.5"
              strokeDasharray="4 4"
            />
            {/* Top Bracket Tick */}
            <line
              x1={xEnd - 7}
              y1={gapTopY + 12}
              x2={xEnd + 7}
              y2={gapTopY + 12}
              stroke="rgba(245, 158, 11, 0.75)"
              strokeWidth="1.5"
            />
            {/* Bottom Bracket Tick */}
            <line
              x1={xEnd - 7}
              y1={gapBottomY - 12}
              x2={xEnd + 7}
              y2={gapBottomY - 12}
              stroke="rgba(245, 158, 11, 0.75)"
              strokeWidth="1.5"
            />
          </g>
        )}
      </svg>

      {/* ----------------------------------------------------------------- */}
      {/* 3. SHARED BASELINE ORIGIN STACK (Left-Aligned to Margin)           */}
      {/* ----------------------------------------------------------------- */}
      {baselineLabel && (
        <div
          style={{
            position: 'absolute',
            right: `${svgWidth - xStart + 24}px`,
            top: `${yStart}px`,
            transform: `translateY(-50%) translateX(${interpolate(originSpring, [0, 1], [-12, 0])}px)`,
            width: '210px',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'flex-end',
            textAlign: 'right',
            opacity: originSpring,
            zIndex: 8,
            pointerEvents: 'none',
          }}
        >
          <div
            style={{
              fontSize: '11px',
              fontWeight: 700,
              textTransform: 'uppercase',
              letterSpacing: '0.14em',
              color: '#64748b',
              marginBottom: '3px',
            }}
          >
            SHARED BASELINE
          </div>
          <div
            style={{
              fontSize: '15px',
              fontWeight: 700,
              color: '#e2e8f0',
              lineHeight: 1.25,
            }}
          >
            {baselineLabel}
          </div>
        </div>
      )}

      {/* ----------------------------------------------------------------- */}
      {/* 4. DIVERGENCE GAP CALLOUT BADGE (Centered on bracket)              */}
      {/* ----------------------------------------------------------------- */}
      {hasDivergenceGap && (
        <div
          style={{
            position: 'absolute',
            left: `${xEnd}px`,
            top: `${gapCenterY}px`,
            transform: `translate(-50%, -50%) scale(${gapSpring})`,
            opacity: gapSpring,
            backgroundColor: 'rgba(11, 18, 34, 0.94)',
            border: '1px solid rgba(245, 158, 11, 0.45)',
            boxShadow: '0 12px 28px -6px rgba(0, 0, 0, 0.7)',
            backdropFilter: 'blur(8px)',
            borderRadius: '6px',
            padding: '6px 14px',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            zIndex: 9,
            pointerEvents: 'none',
            whiteSpace: 'nowrap',
          }}
        >
          <span
            style={{
              fontSize: '10px',
              fontWeight: 700,
              letterSpacing: '0.12em',
              textTransform: 'uppercase',
              color: '#f59e0b',
              marginBottom: '1px',
            }}
          >
            DIVERGENCE GAP
          </span>
          <span
            style={{
              fontSize: '14px',
              fontWeight: 800,
              color: '#f8fafc',
              letterSpacing: '0.02em',
            }}
          >
            {divergenceGap}
          </span>
        </div>
      )}

      {/* ----------------------------------------------------------------- */}
      {/* 5. DESTINATION ENDPOINT TYPOGRAPHY (Right 480px Safe Zone)        */}
      {/* ----------------------------------------------------------------- */}

      {/* Path A Endpoint Block */}
      {pathA && (
        <div
          style={{
            position: 'absolute',
            left: `${xEnd + 44}px`,
            top: `${yEndA}px`,
            transform: `translateY(-50%) translateY(${interpolate(endASpring, [0, 1], [14, 0])}px)`,
            width: '420px',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'flex-start',
            opacity: endASpring,
            zIndex: 8,
            pointerEvents: 'none',
          }}
        >
          {/* Label */}
          <div
            style={{
              fontSize: '12px',
              fontWeight: 700,
              textTransform: 'uppercase',
              letterSpacing: '0.14em',
              color: finalColorA,
              marginBottom: '3px',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
            }}
          >
            <span>●</span>
            <span>{pathA.label.toUpperCase()}</span>
          </div>

          {/* End Value */}
          {pathA.endValue && (
            <div
              style={{
                fontSize: `${fontSizeA}px`,
                fontWeight: 800,
                fontVariantNumeric: 'tabular-nums',
                color: '#f8fafc',
                lineHeight: 1.05,
                letterSpacing: '-0.02em',
                textShadow: `0 0 30px rgba(${colorConfigA.glowRgb}, 0.35)`,
              }}
            >
              {pathA.endValue}
            </div>
          )}

          {/* Rate Chip */}
          {pathA.rate && (
            <div
              style={{
                marginTop: '6px',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '6px',
                fontSize: '12px',
                fontWeight: 700,
                color: finalColorA,
                backgroundColor: `rgba(${colorConfigA.glowRgb}, 0.10)`,
                border: `1px solid rgba(${colorConfigA.glowRgb}, 0.32)`,
                padding: '3px 11px',
                borderRadius: tokens.radius.chip,
                letterSpacing: '0.04em',
                textTransform: 'uppercase',
              }}
            >
              <span>{pathA.direction === 'down' ? '▼' : '▲'}</span>
              <span>{pathA.rate}</span>
            </div>
          )}
        </div>
      )}

      {/* Path B Endpoint Block */}
      {pathB && (
        <div
          style={{
            position: 'absolute',
            left: `${xEnd + 44}px`,
            top: `${yEndB}px`,
            transform: `translateY(-50%) translateY(${interpolate(endBSpring, [0, 1], [14, 0])}px)`,
            width: '420px',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'flex-start',
            opacity: endBSpring,
            zIndex: 8,
            pointerEvents: 'none',
          }}
        >
          {/* Label */}
          <div
            style={{
              fontSize: '12px',
              fontWeight: 700,
              textTransform: 'uppercase',
              letterSpacing: '0.14em',
              color: finalColorB,
              marginBottom: '3px',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
            }}
          >
            <span>●</span>
            <span>{pathB.label.toUpperCase()}</span>
          </div>

          {/* End Value */}
          {pathB.endValue && (
            <div
              style={{
                fontSize: `${fontSizeB}px`,
                fontWeight: 800,
                fontVariantNumeric: 'tabular-nums',
                color: '#f8fafc',
                lineHeight: 1.05,
                letterSpacing: '-0.02em',
                textShadow: `0 0 30px rgba(${colorConfigB.glowRgb}, 0.35)`,
              }}
            >
              {pathB.endValue}
            </div>
          )}

          {/* Rate Chip */}
          {pathB.rate && (
            <div
              style={{
                marginTop: '6px',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '6px',
                fontSize: '12px',
                fontWeight: 700,
                color: finalColorB,
                backgroundColor: `rgba(${colorConfigB.glowRgb}, 0.10)`,
                border: `1px solid rgba(${colorConfigB.glowRgb}, 0.32)`,
                padding: '3px 11px',
                borderRadius: tokens.radius.chip,
                letterSpacing: '0.04em',
                textTransform: 'uppercase',
              }}
            >
              <span>{pathB.direction === 'down' ? '▼' : '▲'}</span>
              <span>{pathB.rate}</span>
            </div>
          )}
        </div>
      )}

      {/* ----------------------------------------------------------------- */}
      {/* 6. BASELINE HORIZONTAL TIMELINE LABELS (Bottom)                   */}
      {/* ----------------------------------------------------------------- */}
      <div
        style={{
          position: 'absolute',
          bottom: '56px',
          left: `${xStart}px`,
          right: `${svgWidth - xEnd}px`,
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          fontSize: '12px',
          fontWeight: 600,
          textTransform: 'uppercase',
          letterSpacing: '0.12em',
          color: '#475569',
          opacity: headerSpring,
          zIndex: 6,
          pointerEvents: 'none',
        }}
      >
        <span>T = 0 (SHARED START)</span>
        <span style={{ color: 'rgba(148, 163, 184, 0.65)' }}>WIDENING DIVERGENCE</span>
        <span>{timeHorizon ? `MATURITY (${timeHorizon})` : 'HORIZON TERMINUS'}</span>
      </div>
    </AbsoluteFill>
  );
}
