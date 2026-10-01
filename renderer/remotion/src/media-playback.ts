/**
 * Return the number of renderer frames needed for one complete media pass.
 * A null result means the asset has no usable duration metadata, so callers
 * should preserve their existing non-looping fallback behavior.
 */
export function getMediaLoopDurationInFrames(
  durationSeconds: number | null | undefined,
  fps: number,
): number | null {
  if (durationSeconds == null || !Number.isFinite(durationSeconds) || durationSeconds <= 0) {
    return null;
  }
  if (!Number.isFinite(fps) || fps <= 0) {
    return null;
  }
  return Math.max(1, Math.ceil(durationSeconds * fps));
}
