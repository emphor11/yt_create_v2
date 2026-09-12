/**
 * Animation Safety Utilities for Remotion Compositions
 *
 * Guarantees that all animation windows and spring delays adapt safely
 * to arbitrary scene durations (from ultra-short 10-frame beats to long 600-frame scenes)
 * without triggering Remotion's strict monotonic increase error:
 * "inputRange must be strictly monotonically increasing".
 */

/**
 * Calculates a strictly monotonically increasing animation window [start, end]
 * guaranteed to fit within the actual scene duration.
 *
 * Guarantees:
 * - safeStart < safeEnd
 * - 0 <= safeStart
 * - safeEnd <= durationFrames (for durationFrames >= 1)
 * - On normal/long scenes where nominal window fits with margins, preserves exact nominal timing.
 * - On short scenes, proportionally compresses window within available duration.
 */
export function safeAnimationWindow(
  startFrame: number,
  desiredEndFrame: number,
  durationFrames: number,
  minWindow: number = 1
): [number, number] {
  const d = Math.max(1, durationFrames);
  const refDuration = Math.max(desiredEndFrame, 120);

  // If nominal window fits comfortably within scene duration, preserve nominal timing
  if (desiredEndFrame > startFrame && desiredEndFrame <= d && startFrame <= d - minWindow) {
    return [Math.max(0, startFrame), Math.min(d, desiredEndFrame)];
  }

  // Otherwise scale proportionally to scene duration
  const startFrac = Math.max(0, Math.min(startFrame / refDuration, 0.4));
  const endFrac = Math.min(Math.max(desiredEndFrame / refDuration, startFrac + 0.15), 0.95);

  let safeStart = Math.floor(d * startFrac);
  let safeEnd = Math.floor(d * endFrac);

  if (safeEnd <= safeStart) {
    safeEnd = safeStart + minWindow;
  }
  if (safeEnd > d) {
    safeEnd = d;
    safeStart = Math.max(0, safeEnd - minWindow);
  }

  // Absolute fallback for ultra-small durations (e.g. d = 1)
  if (safeStart >= safeEnd) {
    safeStart = 0;
    safeEnd = Math.max(1, safeStart + minWindow);
  }

  return [safeStart, safeEnd];
}

/**
 * Calculates a spring delay offset that adapts gracefully to scene duration.
 *
 * On normal scenes, returns nominalDelay.
 * On short scenes, scales delay so the spring triggers well before the scene ends.
 */
export function safeSpringDelay(
  nominalDelay: number,
  durationFrames: number,
  maxFraction: number = 0.65
): number {
  const d = Math.max(1, durationFrames);
  const maxDelay = Math.max(0, Math.floor(d * maxFraction));
  return Math.min(Math.max(0, nominalDelay), maxDelay);
}

/**
 * Scales a multi-point keyframe array (e.g. [74, 81, 88]) safely within duration.
 */
export function safeKeyframeWindow(
  nominalFrames: number[],
  durationFrames: number
): number[] {
  if (!nominalFrames || nominalFrames.length === 0) {
    return [0, 1];
  }
  const d = Math.max(nominalFrames.length, durationFrames);
  const maxNominal = Math.max(...nominalFrames);

  // If nominal frames fit within scene duration, keep them
  if (maxNominal <= d) {
    return nominalFrames;
  }

  // Scale keyframes proportionally into the latter half of the scene [0.5 * d, 0.95 * d]
  const count = nominalFrames.length;
  const start = Math.floor(d * 0.5);
  const span = Math.max(count, Math.floor(d * 0.45));
  const step = span / (count - 1 || 1);

  const result: number[] = [];
  for (let i = 0; i < count; i++) {
    const val = Math.floor(start + i * step);
    if (i > 0 && val <= result[i - 1]) {
      result.push(result[i - 1] + 1);
    } else {
      result.push(val);
    }
  }

  // Final check: strictly increasing
  for (let i = 1; i < result.length; i++) {
    if (result[i] <= result[i - 1]) {
      result[i] = result[i - 1] + 1;
    }
  }

  return result;
}
