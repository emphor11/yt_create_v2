import { interpolate, spring, Easing } from "remotion";
import { type PrimitiveAnimation } from "./types";

/**
 * Computes an animated value for a target property at currentFrame.
 */
export function evaluateAnimatedProperty<T = any>(
  propertyName: string,
  baseValue: T,
  animations: PrimitiveAnimation[] | undefined,
  currentFrame: number,
  fps: number = 30
): T {
  if (!animations || animations.length === 0) {
    return baseValue;
  }

  // Filter animations targeting this property, sorted by trigger_frame
  const relevant = animations
    .filter((a) => a.target_property === propertyName)
    .sort((a, b) => a.trigger_frame - b.trigger_frame);

  if (relevant.length === 0) {
    return baseValue;
  }

  let currentValue = baseValue;

  for (const anim of relevant) {
    if (currentFrame < anim.trigger_frame) {
      continue;
    }

    const duration = anim.duration_frames || 30;
    const fromVal = anim.from_value !== undefined ? anim.from_value : currentValue;
    const toVal = anim.to_value;

    let progress = 0;
    if (anim.easing === "spring") {
      const springVal = spring({
        frame: currentFrame - anim.trigger_frame,
        fps,
        config: anim.spring_config || { damping: 14, stiffness: 100 },
      });
      progress = springVal;
    } else if (anim.easing === "ease-out") {
      progress = interpolate(
        currentFrame,
        [anim.trigger_frame, anim.trigger_frame + duration],
        [0, 1],
        {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
          easing: Easing.out(Easing.cubic),
        }
      );
    } else if (anim.easing === "bezier") {
      progress = interpolate(
        currentFrame,
        [anim.trigger_frame, anim.trigger_frame + duration],
        [0, 1],
        {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
          easing: Easing.bezier(0.16, 1, 0.3, 1),
        }
      );
    } else {
      // linear
      progress = interpolate(
        currentFrame,
        [anim.trigger_frame, anim.trigger_frame + duration],
        [0, 1],
        {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        }
      );
    }

    // Interpolate numeric, color, or snap
    if (typeof fromVal === "number" && typeof toVal === "number") {
      let val = fromVal + (toVal - fromVal) * progress;
      if (propertyName === "opacity" || propertyName.endsWith("opacity")) {
        val = Math.min(1, Math.max(0, val));
      }
      currentValue = val as unknown as T;
    } else if (progress >= 1) {
      currentValue = toVal;
    } else if (progress <= 0) {
      currentValue = fromVal;
    } else {
      currentValue = toVal;
    }
  }

  return currentValue;
}

/**
 * Calculates entrance spring scale and opacity for a primitive based on enter_frame.
 */
export function evaluatePrimitiveEntrance(
  enterFrame: number = 0,
  currentFrame: number,
  fps: number = 30
): { opacity: number; scale: number } {
  if (currentFrame < enterFrame) {
    return { opacity: 0, scale: 0.8 };
  }

  const s = spring({
    frame: currentFrame - enterFrame,
    fps,
    config: { damping: 16, stiffness: 120 },
  });

  return {
    opacity: interpolate(s, [0, 1], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
    scale: interpolate(s, [0, 1], [0.85, 1.0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
  };
}
