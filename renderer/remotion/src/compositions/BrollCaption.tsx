import React from 'react';
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig, Img, OffthreadVideo, staticFile } from 'remotion';
import { tokens } from '../design-tokens';
import { BrollCaptionProps } from '../types';
import { safeAnimationWindow, safeSpringDelay, safeKeyframeWindow } from '../animation-safety';

export function BrollCaption(props: BrollCaptionProps | any) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const resolvedProps: BrollCaptionProps =
    props?.props && typeof props.props === 'object' && !Array.isArray(props.props)
      ? props.props
      : props || {};
  const duration_frames =
    props?.duration_frames || props?.props?.duration_frames || 180;

  const caption = resolvedProps.caption || 'Essential Strategic Perspective';
  const emphasisPhrase = resolvedProps.emphasisPhrase || null;
  const author = resolvedProps.author || null;
  const sourceContext = resolvedProps.sourceContext || null;
  const headerLabel = resolvedProps.headerLabel || null;
  const rawVariant = (resolvedProps.variant || '').toLowerCase();
  const polarity = (resolvedProps.polarity || 'neutral').toLowerCase();
  const asset = resolvedProps.asset || null;

  // Determine variant
  let variant: 'statement' | 'quote' | 'ambient_broll' = 'statement';
  if (rawVariant === 'quote' || author) {
    variant = 'quote';
  } else if (rawVariant === 'ambient_broll' || (asset && rawVariant !== 'statement')) {
    variant = 'ambient_broll';
  } else {
    variant = 'statement';
  }

  // Theme colors
  const isPositive = polarity === 'positive' || polarity === 'low';
  const isCritical = polarity === 'critical' || polarity === 'high';
  const isWarning = polarity === 'medium' || polarity === 'warning';

  let accentColor = tokens.accent.cyan;
  let glowColor = 'rgba(6, 182, 212, 0.35)';
  let bgTint = 'rgba(6, 182, 212, 0.08)';
  let defaultEyebrow = 'CORE PRINCIPLE // STRATEGIC INSIGHT';

  if (isCritical) {
    accentColor = tokens.accent.rose;
    glowColor = 'rgba(244, 63, 94, 0.35)';
    bgTint = 'rgba(244, 63, 94, 0.08)';
    defaultEyebrow = 'CRITICAL WARNING // CORE PRINCIPLE';
  } else if (isPositive) {
    accentColor = tokens.accent.emerald;
    glowColor = 'rgba(16, 185, 129, 0.35)';
    bgTint = 'rgba(16, 185, 129, 0.08)';
    defaultEyebrow = 'PROVEN RULE // WEALTH GENERATION';
  } else if (isWarning) {
    accentColor = tokens.accent.amber;
    glowColor = 'rgba(245, 158, 11, 0.35)';
    bgTint = 'rgba(245, 158, 11, 0.08)';
    defaultEyebrow = 'KEY PRINCIPLE // SYSTEMIC';
  }

  if (variant === 'quote') {
    defaultEyebrow = 'NOTABLE PERSPECTIVE // WISDOM';
  } else if (variant === 'ambient_broll') {
    defaultEyebrow = 'CONTEXTUAL OVERVIEW';
  }

  // Scene fade
  const sceneOpacity = interpolate(
    frame,
    [0, Math.min(10, Math.max(1, duration_frames - 1))],
    [0, 1],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
  );

  // Background slow atmospheric drift
  const bgDriftX = interpolate(frame, [0, duration_frames], [-15, 15]);
  const bgDriftY = interpolate(frame, [0, duration_frames], [-10, 10]);

  // Duration-safe text reveal calculation
  const words = caption.split(' ');
  const [textStart, textEnd] = safeAnimationWindow(10, Math.min(48, 14 + words.length * 2.2), duration_frames);
  const framesPerWord = Math.max(0.8, (textEnd - textStart) / Math.max(1, words.length));

  // Emphasis box motion
  const boxDelay = safeSpringDelay(32, duration_frames, 0.55);
  const boxSpring = spring({
    frame: Math.max(0, frame - boxDelay),
    fps,
    config: { damping: 14, stiffness: 110 },
  });
  const boxY = interpolate(boxSpring, [0, 1], [24, 0]);
  const boxOpacity = interpolate(boxSpring, [0, 1], [0, 1]);

  // Author / attribution entrance
  const authorDelay = safeSpringDelay(42, duration_frames, 0.65);
  const authorSpring = spring({
    frame: Math.max(0, frame - authorDelay),
    fps,
    config: { damping: 14, stiffness: 110 },
  });
  const authorY = interpolate(authorSpring, [0, 1], [20, 0]);
  const authorOpacity = interpolate(authorSpring, [0, 1], [0, 1]);

  // Pulse keyframes
  const pulseFrames = safeKeyframeWindow([60, 68, 78], duration_frames);
  const pulseGlow = interpolate(frame, pulseFrames, [0.4, 1.0, 0.6], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // Calculate font size dynamically based on caption length
  const isLongCaption = caption.length > 130;
  const captionFontSize = isLongCaption ? (variant === 'quote' ? '34px' : '38px') : (variant === 'quote' ? '42px' : '48px');

  return (
    <AbsoluteFill
      style={{
        backgroundColor: tokens.bg.base,
        fontFamily: tokens.font.family,
        opacity: sceneOpacity,
        overflow: 'hidden',
      }}
    >
      {/* Layer 1: Background Media Asset OR Cinematic No-Asset Atmospheric Canvas */}
      {asset && asset.local_path ? (
        <div style={{ position: 'absolute', inset: 0, overflow: 'hidden' }}>
          {asset.asset_type === 'video' ? (
            <OffthreadVideo
              src={asset.local_path.startsWith('http') ? asset.local_path : staticFile(asset.local_path)}
              style={{
                position: 'absolute',
                inset: 0,
                width: '100%',
                height: '100%',
                objectFit: 'cover',
                transform: `scale(1.04) translate(${bgDriftX}px, ${bgDriftY}px)`,
                filter: 'brightness(0.65) contrast(1.1)',
              }}
              muted
            />
          ) : (
            <Img
              src={asset.local_path.startsWith('http') ? asset.local_path : staticFile(asset.local_path)}
              style={{
                position: 'absolute',
                inset: 0,
                width: '100%',
                height: '100%',
                objectFit: 'cover',
                transform: `scale(1.05) translate(${bgDriftX}px, ${bgDriftY}px)`,
                filter: 'brightness(0.65) contrast(1.1)',
              }}
            />
          )}
          {/* Heavy cinematic wash over asset */}
          <div
            style={{
              position: 'absolute',
              inset: 0,
              background: `
                radial-gradient(ellipse at center, rgba(9, 9, 11, 0.40) 0%, rgba(9, 9, 11, 0.88) 85%),
                linear-gradient(180deg, rgba(9, 9, 11, 0.60) 0%, rgba(9, 9, 11, 0.30) 40%, rgba(9, 9, 11, 0.85) 100%)
              `,
              pointerEvents: 'none',
            }}
          />
        </div>
      ) : (
        /* Rich No-Asset Atmospheric Canvas (never a blank slide) */
        <div style={{ position: 'absolute', inset: 0, overflow: 'hidden' }}>
          {/* Deep space radial glow */}
          <div
            style={{
              position: 'absolute',
              inset: -100,
              background: `
                radial-gradient(circle at 50% 35%, ${bgTint} 0%, transparent 65%),
                radial-gradient(circle at 80% 70%, rgba(99, 102, 241, 0.08) 0%, transparent 55%),
                radial-gradient(circle at 20% 80%, ${bgTint} 0%, transparent 50%),
                linear-gradient(180deg, #0f172a 0%, #09090b 100%)
              `,
              transform: `translate(${bgDriftX * 0.5}px, ${bgDriftY * 0.5}px)`,
            }}
          />

          {/* Isometric Micro-grid overlay */}
          <div
            style={{
              position: 'absolute',
              inset: 0,
              backgroundImage: `
                linear-gradient(to right, rgba(255, 255, 255, 0.025) 1px, transparent 1px),
                linear-gradient(to bottom, rgba(255, 255, 255, 0.025) 1px, transparent 1px)
              `,
              backgroundSize: '56px 56px',
              opacity: 0.6,
              pointerEvents: 'none',
            }}
          />

          {/* Central Atmospheric Halo Flare */}
          <div
            style={{
              position: 'absolute',
              width: '800px',
              height: '800px',
              borderRadius: '50%',
              background: `radial-gradient(circle, ${glowColor} 0%, transparent 70%)`,
              opacity: 0.35 * pulseGlow,
              left: '50%',
              top: '48%',
              transform: 'translate(-50%, -50%)',
              pointerEvents: 'none',
            }}
          />
        </div>
      )}

      {/* Layer 2: Top and Bottom Cinematic Hairline Framing */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: '24px',
          backgroundColor: '#000000',
          borderBottom: '1px solid rgba(255, 255, 255, 0.06)',
          zIndex: 10,
        }}
      />
      <div
        style={{
          position: 'absolute',
          bottom: 0,
          left: 0,
          right: 0,
          height: '24px',
          backgroundColor: '#000000',
          borderTop: '1px solid rgba(255, 255, 255, 0.06)',
          zIndex: 10,
        }}
      />

      {/* Layer 3: Main Foreground Content by Variant */}
      <div
        style={{
          position: 'relative',
          width: '100%',
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '60px 120px',
          zIndex: 5,
        }}
      >
        {/* ======================================================== */}
        {/* VARIANT 1: STATEMENT (Thesis / Key Rule / Principle)     */}
        {/* ======================================================== */}
        {variant === 'statement' && (
          <div
            style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              textAlign: 'center',
              maxWidth: '1420px',
            }}
          >
            {/* Eyebrow Chip */}
            <div
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '8px',
                padding: '8px 18px',
                borderRadius: tokens.radius.chip,
                backgroundColor: 'rgba(15, 23, 42, 0.85)',
                border: `1px solid ${accentColor}60`,
                boxShadow: `0 0 16px ${glowColor}`,
                marginBottom: '36px',
              }}
            >
              <div
                style={{
                  width: '7px',
                  height: '7px',
                  borderRadius: '50%',
                  backgroundColor: accentColor,
                  boxShadow: `0 0 8px ${accentColor}`,
                }}
              />
              <span
                style={{
                  fontSize: '13px',
                  fontWeight: 800,
                  textTransform: 'uppercase',
                  letterSpacing: '0.12em',
                  color: accentColor,
                }}
              >
                {headerLabel || defaultEyebrow}
              </span>
            </div>

            {/* Main Statement Text with Word-by-Word Reveal */}
            <div
              style={{
                fontSize: captionFontSize,
                fontWeight: 800,
                color: tokens.text.primary,
                lineHeight: 1.32,
                letterSpacing: '-0.025em',
                display: 'flex',
                flexWrap: 'wrap',
                justifyContent: 'center',
                gap: '12px 14px',
                maxWidth: '1320px',
                marginBottom: emphasisPhrase ? '36px' : '0',
                textShadow: '0 4px 24px rgba(0,0,0,0.85)',
              }}
            >
              {words.map((word, i) => {
                const wStart = textStart + i * framesPerWord;
                const wOpacity = interpolate(frame, [wStart, wStart + 3], [0, 1], {
                  extrapolateLeft: 'clamp',
                  extrapolateRight: 'clamp',
                });
                const wY = interpolate(frame, [wStart, wStart + 3], [10, 0], {
                  extrapolateLeft: 'clamp',
                  extrapolateRight: 'clamp',
                });

                return (
                  <span
                    key={i}
                    style={{
                      opacity: wOpacity,
                      transform: `translateY(${wY}px)`,
                      display: 'inline-block',
                    }}
                  >
                    {word}
                  </span>
                );
              })}
            </div>

            {/* Emphasis Highlight Box */}
            {emphasisPhrase && (
              <div
                style={{
                  opacity: boxOpacity,
                  transform: `translateY(${boxY}px)`,
                  backgroundColor: 'rgba(15, 23, 42, 0.90)',
                  backdropFilter: 'blur(16px)',
                  borderRadius: '16px',
                  border: `1px solid ${tokens.bg.border}`,
                  borderLeft: `5px solid ${accentColor}`,
                  padding: '20px 36px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '16px',
                  boxShadow: `0 20px 45px -10px rgba(0,0,0,0.8), 0 0 ${25 * pulseGlow}px ${glowColor}`,
                  maxWidth: '1000px',
                }}
              >
                <span
                  style={{
                    fontSize: '12px',
                    fontWeight: 800,
                    textTransform: 'uppercase',
                    letterSpacing: '0.1em',
                    color: accentColor,
                    whiteSpace: 'nowrap',
                  }}
                >
                  KEY PRINCIPLE //
                </span>
                <span
                  style={{
                    fontSize: '26px',
                    fontWeight: 700,
                    color: tokens.text.primary,
                    letterSpacing: '-0.01em',
                  }}
                >
                  {emphasisPhrase}
                </span>
              </div>
            )}
          </div>
        )}

        {/* ======================================================== */}
        {/* VARIANT 2: QUOTE (Editorial Wisdom & Luminary Thoughts)  */}
        {/* ======================================================== */}
        {variant === 'quote' && (
          <div
            style={{
              position: 'relative',
              maxWidth: '1360px',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              textAlign: 'center',
              padding: '0 40px',
            }}
          >
            {/* Top Eyebrow */}
            <div
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '8px',
                padding: '6px 16px',
                borderRadius: tokens.radius.chip,
                backgroundColor: 'rgba(99, 102, 241, 0.15)',
                border: '1px solid rgba(99, 102, 241, 0.40)',
                marginBottom: '28px',
              }}
            >
              <span
                style={{
                  fontSize: '12px',
                  fontWeight: 800,
                  textTransform: 'uppercase',
                  letterSpacing: '0.12em',
                  color: tokens.accent.primary,
                }}
              >
                {headerLabel || defaultEyebrow}
              </span>
            </div>

            {/* Stylized Giant Quotation Glyphs */}
            <div
              style={{
                position: 'relative',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                marginBottom: '36px',
              }}
            >
              <div
                style={{
                  position: 'absolute',
                  top: '-70px',
                  left: '-40px',
                  fontSize: '140px',
                  fontFamily: 'Georgia, serif',
                  color: accentColor,
                  opacity: 0.22,
                  lineHeight: 1,
                  userSelect: 'none',
                  pointerEvents: 'none',
                }}
              >
                “
              </div>

              {/* Main Quote Content */}
              <div
                style={{
                  fontSize: captionFontSize,
                  fontWeight: 600,
                  fontStyle: 'italic',
                  color: tokens.text.primary,
                  lineHeight: 1.45,
                  letterSpacing: '-0.01em',
                  display: 'flex',
                  flexWrap: 'wrap',
                  justifyContent: 'center',
                  gap: '10px 12px',
                  maxWidth: '1240px',
                  textShadow: '0 4px 20px rgba(0,0,0,0.85)',
                  position: 'relative',
                  zIndex: 2,
                }}
              >
                {words.map((word, i) => {
                  const wStart = textStart + i * framesPerWord;
                  const wOpacity = interpolate(frame, [wStart, wStart + 3], [0, 1], {
                    extrapolateLeft: 'clamp',
                    extrapolateRight: 'clamp',
                  });
                  const wY = interpolate(frame, [wStart, wStart + 3], [8, 0], {
                    extrapolateLeft: 'clamp',
                    extrapolateRight: 'clamp',
                  });

                  return (
                    <span
                      key={i}
                      style={{
                        opacity: wOpacity,
                        transform: `translateY(${wY}px)`,
                        display: 'inline-block',
                      }}
                    >
                      {word}
                    </span>
                  );
                })}
              </div>
            </div>

            {/* Author Attribution Card */}
            {(author || sourceContext) && (
              <div
                style={{
                  opacity: authorOpacity,
                  transform: `translateY(${authorY}px)`,
                  display: 'flex',
                  alignItems: 'center',
                  gap: '16px',
                  padding: '14px 28px',
                  borderRadius: '9999px',
                  backgroundColor: 'rgba(15, 23, 42, 0.85)',
                  border: `1px solid ${tokens.bg.border}`,
                  boxShadow: '0 12px 30px -8px rgba(0,0,0,0.7)',
                }}
              >
                {/* Author Monogram / Icon Avatar */}
                <div
                  style={{
                    width: '36px',
                    height: '36px',
                    borderRadius: '50%',
                    backgroundColor: 'rgba(99, 102, 241, 0.25)',
                    border: `1px solid ${tokens.accent.primary}`,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '14px',
                    fontWeight: 800,
                    color: tokens.accent.primary,
                  }}
                >
                  {author ? author.charAt(0) : '“'}
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', textAlign: 'left' }}>
                  {author && (
                    <div style={{ fontSize: '20px', fontWeight: 700, color: tokens.text.primary }}>
                      {author}
                    </div>
                  )}
                  {sourceContext && (
                    <div style={{ fontSize: '14px', fontWeight: 500, color: tokens.text.secondary }}>
                      {sourceContext}
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        )}

        {/* ======================================================== */}
        {/* VARIANT 3: AMBIENT B-ROLL (Cinematic Glass Card Overlay) */}
        {/* ======================================================== */}
        {variant === 'ambient_broll' && (
          <div
            style={{
              position: 'relative',
              width: '100%',
              maxWidth: '1360px',
              backgroundColor: 'rgba(15, 23, 42, 0.76)',
              backdropFilter: 'blur(20px)',
              borderRadius: '24px',
              border: '1px solid rgba(255, 255, 255, 0.14)',
              boxShadow: '0 30px 80px -15px rgba(0, 0, 0, 0.85)',
              padding: '48px 60px',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              textAlign: 'center',
            }}
          >
            {/* Viewfinder Corner Accents */}
            <div style={{ position: 'absolute', top: '16px', left: '16px', width: '12px', height: '12px', borderTop: '2px solid rgba(255,255,255,0.3)', borderLeft: '2px solid rgba(255,255,255,0.3)' }} />
            <div style={{ position: 'absolute', top: '16px', right: '16px', width: '12px', height: '12px', borderTop: '2px solid rgba(255,255,255,0.3)', borderRight: '2px solid rgba(255,255,255,0.3)' }} />
            <div style={{ position: 'absolute', bottom: '16px', left: '16px', width: '12px', height: '12px', borderBottom: '2px solid rgba(255,255,255,0.3)', borderLeft: '2px solid rgba(255,255,255,0.3)' }} />
            <div style={{ position: 'absolute', bottom: '16px', right: '16px', width: '12px', height: '12px', borderBottom: '2px solid rgba(255,255,255,0.3)', borderRight: '2px solid rgba(255,255,255,0.3)' }} />

            {/* Top Category Tag */}
            <div
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '8px',
                padding: '6px 14px',
                borderRadius: tokens.radius.chip,
                backgroundColor: 'rgba(255, 255, 255, 0.08)',
                marginBottom: '24px',
              }}
            >
              <span
                style={{
                  fontSize: '12px',
                  fontWeight: 800,
                  textTransform: 'uppercase',
                  letterSpacing: '0.1em',
                  color: tokens.text.secondary,
                }}
              >
                {headerLabel || defaultEyebrow}
              </span>
            </div>

            {/* Caption in Glass Card */}
            <div
              style={{
                fontSize: captionFontSize,
                fontWeight: 700,
                color: tokens.text.primary,
                lineHeight: 1.36,
                letterSpacing: '-0.02em',
                display: 'flex',
                flexWrap: 'wrap',
                justifyContent: 'center',
                gap: '12px',
                maxWidth: '1200px',
                marginBottom: emphasisPhrase ? '28px' : '0',
              }}
            >
              {words.map((word, i) => {
                const wStart = textStart + i * framesPerWord;
                const wOpacity = interpolate(frame, [wStart, wStart + 3], [0, 1], {
                  extrapolateLeft: 'clamp',
                  extrapolateRight: 'clamp',
                });

                return (
                  <span key={i} style={{ opacity: wOpacity, display: 'inline-block' }}>
                    {word}
                  </span>
                );
              })}
            </div>

            {/* Emphasis Phrase */}
            {emphasisPhrase && (
              <div
                style={{
                  opacity: boxOpacity,
                  transform: `translateY(${boxY}px)`,
                  backgroundColor: 'rgba(255, 255, 255, 0.08)',
                  borderRadius: tokens.radius.chip,
                  border: `1px solid ${accentColor}50`,
                  padding: '14px 28px',
                  color: accentColor,
                  fontSize: '22px',
                  fontWeight: 700,
                }}
              >
                {emphasisPhrase}
              </div>
            )}
          </div>
        )}
      </div>
    </AbsoluteFill>
  );
}
