import React from 'react';
import {
  AbsoluteFill,
  interpolate,
  useCurrentFrame,
  Img,
  OffthreadVideo,
  staticFile,
} from 'remotion';
import { BrollCaptionProps } from '../types';

/**
 * BrollCaption Composition:
 * Renders full-bleed, un-obscured B-roll footage (video or image) cleanly at 100% opacity.
 * Transparent container ensures zero dark background occlusion over underlying media in VideoAssembly.
 */
export function BrollCaption(props: BrollCaptionProps | any) {
  const frame = useCurrentFrame();

  const resolvedProps: BrollCaptionProps =
    props?.props && typeof props.props === 'object' && !Array.isArray(props.props)
      ? props.props
      : props || {};

  const duration_frames =
    props?.duration_frames ||
    props?.durationInFrames ||
    props?.props?.duration_frames ||
    180;

  const asset = resolvedProps.asset || props?.asset || null;

  // Subtle cinematic drift & slow zoom for standalone media presentation
  const bgScale = interpolate(frame, [0, duration_frames], [1.0, 1.04], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const bgDriftX = interpolate(frame, [0, duration_frames], [-8, 8], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const bgDriftY = interpolate(frame, [0, duration_frames], [-5, 5], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill
      style={{
        backgroundColor: 'transparent',
        overflow: 'hidden',
      }}
    >
      {/* If asset is passed directly in props (standalone rendering/preview), render full-screen media at full opacity */}
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
                opacity: 1.0,
                transform: `scale(${bgScale}) translate(${bgDriftX}px, ${bgDriftY}px)`,
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
                opacity: 1.0,
                transform: `scale(${bgScale}) translate(${bgDriftX}px, ${bgDriftY}px)`,
              }}
            />
          )}
        </div>
      ) : null}
    </AbsoluteFill>
  );
}
