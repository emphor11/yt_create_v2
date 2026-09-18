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

/**
 * 5-Phase Duration-Aware Coordinator for CalculationStory
 *
 * Deconstructs the calculation narrative into 5 progressive phases:
 * Phase 1: ESTABLISH (0.00 -> 0.20 D) - Main input reveals alone
 * Phase 2: BUILD (0.20 -> 0.38 D) - Secondary input / rate / driver reveals
 * Phase 3: TRANSFORM (0.38 -> 0.58 D) - Operator badge & connecting vectors draw across
 * Phase 4: PAYOFF (0.58 -> 0.78 D) - Dominant result card impacts in
 * Phase 5: RESOLVE (0.78 -> 1.00 D) - Note pill settles in & hold for comprehension
 */
export interface CalculationPhases {
  inputDelay: number;
  driverDelay: number;
  operatorDelay: number;
  vectorStart: number;
  vectorEnd: number;
  resultDelay: number;
  noteDelay: number;
}

export function getCalculationPhases(durationFrames: number): CalculationPhases {
  const d = Math.max(1, durationFrames);

  if (d <= 6) {
    const [vs, ve] = safeAnimationWindow(0, 1, d, 1);
    return {
      inputDelay: 0,
      driverDelay: 0,
      operatorDelay: 0,
      vectorStart: vs,
      vectorEnd: ve,
      resultDelay: 0,
      noteDelay: 0,
    };
  }

  // Phase 1: ESTABLISH (0.00 -> 0.20 D)
  const inputDelay = Math.max(0, Math.floor(d * 0.04));

  // Phase 2: BUILD (0.20 -> 0.38 D)
  const driverDelay = Math.max(inputDelay + 1, Math.floor(d * 0.22));

  // Phase 3: TRANSFORM (0.38 -> 0.58 D)
  const operatorDelay = Math.max(driverDelay + 1, Math.floor(d * 0.38));
  const rawVecStart = Math.max(operatorDelay, Math.floor(d * 0.40));
  const rawVecEnd = Math.max(rawVecStart + 1, Math.floor(d * 0.56));
  const [vectorStart, vectorEnd] = safeAnimationWindow(rawVecStart, rawVecEnd, d, 1);

  // Phase 4: PAYOFF (0.58 -> 0.78 D)
  const rawResult = Math.max(vectorEnd, Math.floor(d * 0.60));
  const resultDelay = Math.min(d - 2, rawResult);

  // Phase 5: RESOLVE (0.78 -> 1.00 D)
  const noteDelay = Math.min(d - 1, Math.max(resultDelay + 1, Math.floor(d * 0.72)));

  return {
    inputDelay: Math.min(inputDelay, d - 1),
    driverDelay: Math.min(driverDelay, d - 1),
    operatorDelay: Math.min(operatorDelay, d - 1),
    vectorStart,
    vectorEnd,
    resultDelay: Math.max(0, resultDelay),
    noteDelay: Math.max(0, noteDelay),
  };
}

