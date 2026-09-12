import { interpolate, spring } from "remotion";
import { safeAnimationWindow, safeSpringDelay, safeKeyframeWindow } from "../src/animation-safety.ts";

console.log("==================================================");
console.log("TEST SUITE: DURATION-SAFE ANIMATION ROBUSTNESS");
console.log("==================================================");

// 1. UNIT TESTS: Mathematical Guarantees
console.log("\n--- TEST 1: safeAnimationWindow Guarantees ---");
const testDurations = [1, 2, 3, 5, 10, 15, 24, 34, 45, 60, 120, 180, 300, 600];

for (const d of testDurations) {
  const [s, e] = safeAnimationWindow(24, 80, d);
  if (s >= e) {
    throw new Error(`FAIL: start >= end for duration ${d}: [${s}, ${e}]`);
  }
  if (s < 0) {
    throw new Error(`FAIL: start < 0 for duration ${d}: [${s}, ${e}]`);
  }
  if (e > Math.max(1, d)) {
    throw new Error(`FAIL: end > duration for duration ${d}: [${s}, ${e}]`);
  }
  // Verify with actual remotion interpolate
  for (let f = 0; f <= d; f++) {
    const val = interpolate(f, [s, e], [0, 1], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });
    if (isNaN(val) || typeof val !== "number") {
      throw new Error(`FAIL: NaN or non-number interpolate result at frame ${f} in [${s}, ${e}]`);
    }
  }
  console.log(`✓ duration ${d.toString().padStart(3)} frames -> window [${s.toString().padStart(2)}, ${e.toString().padStart(2)}] strictly increasing and valid`);
}

// 2. UNIT TESTS: safeSpringDelay
console.log("\n--- TEST 2: safeSpringDelay Guarantees ---");
for (const d of testDurations) {
  const dAnchor = safeSpringDelay(8, d, 0.2);
  const dDot = safeSpringDelay(20, d, 0.35);
  const dEnd = safeSpringDelay(65, d, 0.7);
  const dAnnot = safeSpringDelay(72, d, 0.8);

  if (dAnchor < 0 || dDot < 0 || dEnd < 0 || dAnnot < 0) {
    throw new Error(`FAIL: Negative delay on duration ${d}`);
  }
  if (dEnd > d || dAnnot > d) {
    throw new Error(`FAIL: Delay exceeded duration on duration ${d}`);
  }
  console.log(`✓ duration ${d.toString().padStart(3)} frames -> delays: anchor=${dAnchor}, dot=${dDot}, endDot=${dEnd}, annot=${dAnnot}`);
}

// 3. UNIT TESTS: safeKeyframeWindow
console.log("\n--- TEST 3: safeKeyframeWindow Guarantees ---");
for (const d of testDurations) {
  const kfs = safeKeyframeWindow([74, 81, 88], d);
  for (let i = 1; i < kfs.length; i++) {
    if (kfs[i] <= kfs[i - 1]) {
      throw new Error(`FAIL: Keyframes not strictly increasing on d=${d}: ${kfs}`);
    }
  }
  for (let f = 0; f <= d; f++) {
    interpolate(f, kfs, [0.4, 1.0, 0.6], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });
  }
  console.log(`✓ duration ${d.toString().padStart(3)} frames -> keyframes [${kfs.join(", ")}] strictly increasing and valid`);
}

// 4. INTEGRATION TESTS: Frame-by-frame execution of all 6 composition animation models
console.log("\n--- TEST 4: Frame-by-Frame Simulation Across All Six Compositions ---");

const compositionModels = [
  {
    name: "TimeDecay",
    durations: [10, 15, 24, 34, 45, 60, 120, 180, 300],
    simulateFrame: (frame, duration_frames) => {
      const sceneOpacity = interpolate(frame, [0, Math.min(8, Math.max(1, duration_frames - 1))], [0, 1], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      });
      const anchorDelay = safeSpringDelay(8, duration_frames, 0.2);
      const anchorSpring = spring({ frame: Math.max(0, frame - anchorDelay), fps: 30, config: { damping: 15, stiffness: 105 } });
      const anchorY = interpolate(anchorSpring, [0, 1], [30, 0]);
      const anchorOpacity = interpolate(anchorSpring, [0, 1], [0, 1]);

      const [curveStart, curveEnd] = safeAnimationWindow(24, 80, duration_frames);
      const curveProgress = interpolate(frame, [curveStart, curveEnd], [0, 1], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      });

      const startDotDelay = safeSpringDelay(20, duration_frames, 0.35);
      const startDotSpring = spring({ frame: Math.max(0, frame - startDotDelay), fps: 30, config: { damping: 12, stiffness: 140 } });

      const endDotDelay = safeSpringDelay(65, duration_frames, 0.7);
      const endDotSpring = spring({ frame: Math.max(0, frame - endDotDelay), fps: 30, config: { damping: 12, stiffness: 130 } });

      const annotDelay = safeSpringDelay(72, duration_frames, 0.8);
      const annotSpring = spring({ frame: Math.max(0, frame - annotDelay), fps: 30, config: { damping: 14, stiffness: 110 } });
      const annotY = interpolate(annotSpring, [0, 1], [24, 0]);
      const annotOpacity = interpolate(annotSpring, [0, 1], [0, 1]);

      return { sceneOpacity, anchorY, anchorOpacity, curveProgress, startDotSpring, endDotSpring, annotY, annotOpacity };
    },
  },
  {
    name: "CalculationStory",
    durations: [10, 15, 24, 34, 45, 60, 120, 180, 300],
    simulateFrame: (frame, duration_frames) => {
      const sceneOpacity = interpolate(frame, [0, Math.min(8, Math.max(1, duration_frames - 1))], [0, 1], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      });
      const inputDelay = safeSpringDelay(8, duration_frames, 0.2);
      const inputSpring = spring({ frame: Math.max(0, frame - inputDelay), fps: 30, config: { damping: 15, stiffness: 110 } });
      const inputX = interpolate(inputSpring, [0, 1], [-60, 0]);

      const opDelay = safeSpringDelay(20, duration_frames, 0.35);
      const opSpring = spring({ frame: Math.max(0, frame - opDelay), fps: 30, config: { damping: 12, stiffness: 130 } });
      const opScale = interpolate(opSpring, [0, 1], [0.5, 1]);

      const [arrowStart, arrowEnd] = safeAnimationWindow(26, 48, duration_frames);
      const arrowProgress = interpolate(frame, [arrowStart, arrowEnd], [0, 1], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      });

      const resultDelay = safeSpringDelay(42, duration_frames, 0.6);
      const resultSpring = spring({ frame: Math.max(0, frame - resultDelay), fps: 30, config: { damping: 14, stiffness: 100 } });
      const resultX = interpolate(resultSpring, [0, 1], [60, 0]);

      const noteDelay = safeSpringDelay(54, duration_frames, 0.75);
      const noteSpring = spring({ frame: Math.max(0, frame - noteDelay), fps: 30, config: { damping: 16, stiffness: 120 } });
      const noteOpacity = interpolate(noteSpring, [0, 1], [0, 1]);

      return { sceneOpacity, inputX, opScale, arrowProgress, resultX, noteOpacity };
    },
  },
  {
    name: "CauseEffect",
    durations: [10, 15, 24, 34, 45, 60, 120, 180, 300],
    simulateFrame: (frame, duration_frames) => {
      const sceneOpacity = interpolate(frame, [0, Math.min(8, Math.max(1, duration_frames - 1))], [0, 1], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      });
      const [arrowStart, arrowEnd] = safeAnimationWindow(30, 54, duration_frames);
      const arrowProgress = interpolate(frame, [arrowStart, arrowEnd], [0, 1], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      });
      const outcomeDelay = safeSpringDelay(46, duration_frames, 0.65);
      const outcomeSpring = spring({ frame: Math.max(0, frame - outcomeDelay), fps: 30, config: { damping: 14, stiffness: 105 } });
      const outcomeX = interpolate(outcomeSpring, [0, 1], [60, 0]);

      for (let idx = 0; idx < 3; idx++) {
        const causeDelay = safeSpringDelay(8 + idx * 12, duration_frames, 0.4);
        const causeSpring = spring({ frame: Math.max(0, frame - causeDelay), fps: 30, config: { damping: 15, stiffness: 110 } });
        interpolate(causeSpring, [0, 1], [-50, 0]);
      }
      return { sceneOpacity, arrowProgress, outcomeX };
    },
  },
  {
    name: "MultiFactorPressure",
    durations: [10, 15, 24, 34, 45, 60, 120, 180, 300],
    simulateFrame: (frame, duration_frames) => {
      const sceneOpacity = interpolate(frame, [0, Math.min(8, Math.max(1, duration_frames - 1))], [0, 1], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      });
      const [rayStart, rayEnd] = safeAnimationWindow(32, 58, duration_frames);
      const rayProgress = interpolate(frame, [rayStart, rayEnd], [0, 1], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      });
      const coreDelay = safeSpringDelay(50, duration_frames, 0.65);
      const coreSpring = spring({ frame: Math.max(0, frame - coreDelay), fps: 30, config: { mass: 1.2, damping: 18, stiffness: 100 } });
      const coreScale = interpolate(coreSpring, [0, 1], [0.85, 1]);

      const pulseFrames = safeKeyframeWindow([74, 81, 88], duration_frames);
      const pulseOpacity = interpolate(frame, pulseFrames, [0.4, 1.0, 0.6], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      });

      for (let idx = 0; idx < 4; idx++) {
        const factorDelay = safeSpringDelay(8 + idx * 10, duration_frames, 0.4);
        const factorSpring = spring({ frame: Math.max(0, frame - factorDelay), fps: 30, config: { damping: 15, stiffness: 115 } });
        interpolate(factorSpring, [0, 1], [-50, 0]);
      }
      return { sceneOpacity, rayProgress, coreScale, pulseOpacity };
    },
  },
  {
    name: "MetricHero",
    durations: [10, 15, 24, 34, 45, 60, 120, 180, 300],
    simulateFrame: (frame, duration_frames) => {
      const sceneOpacity = interpolate(frame, [0, Math.min(8, Math.max(1, duration_frames - 1))], [0, 1], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      });
      const badgeDelay = safeSpringDelay(6, duration_frames, 0.2);
      const badgeSpring = spring({ frame: Math.max(0, frame - badgeDelay), fps: 30, config: { damping: 16, stiffness: 120 } });
      const badgeY = interpolate(badgeSpring, [0, 1], [18, 0]);

      const valueDelay = safeSpringDelay(12, duration_frames, 0.35);
      const valueSpring = spring({ frame: Math.max(0, frame - valueDelay), fps: 30, config: { damping: 14, stiffness: 110 } });
      const valueScale = interpolate(valueSpring, [0, 1], [0.88, 1]);

      const labelDelay = safeSpringDelay(18, duration_frames, 0.5);
      const labelSpring = spring({ frame: Math.max(0, frame - labelDelay), fps: 30, config: { damping: 15, stiffness: 100 } });
      const labelY = interpolate(labelSpring, [0, 1], [24, 0]);

      const [glowStart, glowEnd] = safeAnimationWindow(
        Math.round(duration_frames * 0.45),
        Math.round(duration_frames * 0.65),
        duration_frames
      );
      const glowBloom = interpolate(frame, [glowStart, glowEnd], [0, 0.18], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      });

      return { sceneOpacity, badgeY, valueScale, labelY, glowBloom };
    },
  },
  {
    name: "BrollCaption",
    durations: [10, 15, 24, 34, 45, 60, 120, 180, 300],
    simulateFrame: (frame, duration_frames) => {
      const sceneOpacity = interpolate(frame, [0, Math.min(12, Math.max(1, duration_frames - 1))], [0, 1], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      });
      const baseStart = Math.min(10, Math.floor(duration_frames * 0.15));
      const availableFrames = Math.max(1, duration_frames - baseStart - 6);
      const framesPerWord = Math.min(2.5, availableFrames / 10);

      for (let i = 0; i < 10; i++) {
        const wordStart = baseStart + i * framesPerWord;
        interpolate(frame, [wordStart, wordStart + 4], [0, 1], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        });
      }

      const boxDelay = safeSpringDelay(32, duration_frames, 0.6);
      const boxSpring = spring({ frame: Math.max(0, frame - boxDelay), fps: 30, config: { damping: 15, stiffness: 105 } });
      const boxY = interpolate(boxSpring, [0, 1], [20, 0]);

      const [authorStart, authorEnd] = safeAnimationWindow(44, 60, duration_frames);
      const authorOpacity = interpolate(frame, [authorStart, authorEnd], [0, 1], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      });

      return { sceneOpacity, boxY, authorOpacity };
    },
  },
];

for (const comp of compositionModels) {
  for (const d of comp.durations) {
    for (let f = 0; f < d; f++) {
      try {
        comp.simulateFrame(f, d);
      } catch (err) {
        throw new Error(`FAIL: ${comp.name} threw error at frame ${f}/${d}: ${err.message}`);
      }
    }
  }
  console.log(`✓ ${comp.name.padEnd(20)} verified across all frames for durations: [${comp.durations.join(", ")}]`);
}

console.log("\n==================================================");
console.log("SUCCESS: ALL REGRESSION TESTS PASSED (0 ERRORS)");
console.log("==================================================");
