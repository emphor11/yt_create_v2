import { interpolate, spring } from "remotion";
import { safeAnimationWindow, safeSpringDelay, safeKeyframeWindow, getCalculationPhases } from "../src/animation-safety.ts";

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

// 3b. UNIT TESTS: getCalculationPhases Guarantees (5-Phase Storytelling Sequence)
console.log("\n--- TEST 3b: getCalculationPhases Guarantees ---");
for (const d of testDurations) {
  const phases = getCalculationPhases(d);
  if (phases.inputDelay < 0 || phases.driverDelay < 0 || phases.operatorDelay < 0 || phases.resultDelay < 0 || phases.noteDelay < 0) {
    throw new Error(`FAIL: Negative delay in getCalculationPhases on duration ${d}: ${JSON.stringify(phases)}`);
  }
  if (phases.vectorStart >= phases.vectorEnd) {
    throw new Error(`FAIL: vectorStart >= vectorEnd on duration ${d}: [${phases.vectorStart}, ${phases.vectorEnd}]`);
  }
  if (phases.vectorEnd > Math.max(1, d)) {
    throw new Error(`FAIL: vectorEnd > duration on duration ${d}: ${phases.vectorEnd} > ${d}`);
  }
  console.log(`✓ duration ${d.toString().padStart(3)} frames -> phases: in=${phases.inputDelay.toString().padStart(2)}, drv=${phases.driverDelay.toString().padStart(2)}, op=${phases.operatorDelay.toString().padStart(2)}, vec=[${phases.vectorStart.toString().padStart(2)},${phases.vectorEnd.toString().padStart(2)}], res=${phases.resultDelay.toString().padStart(2)}, note=${phases.noteDelay.toString().padStart(2)}`);
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
      const phases = getCalculationPhases(duration_frames);

      // Phase 1: Establish (Input)
      const inputSpring = spring({ frame: Math.max(0, frame - phases.inputDelay), fps: 30, config: { damping: 15, stiffness: 110 } });
      const inputX = interpolate(inputSpring, [0, 1], [-40, 0]);

      // Phase 2: Build (Driver / Rate)
      const driverSpring = spring({ frame: Math.max(0, frame - phases.driverDelay), fps: 30, config: { damping: 15, stiffness: 110 } });
      const driverY = interpolate(driverSpring, [0, 1], [14, 0]);

      // Phase 3: Transform (Operator & Vector)
      const opSpring = spring({ frame: Math.max(0, frame - phases.operatorDelay), fps: 30, config: { damping: 12, stiffness: 140 } });
      const opScale = interpolate(opSpring, [0, 1], [0.4, 1]);

      const arrowProgress = interpolate(frame, [phases.vectorStart, phases.vectorEnd], [0, 1], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      });

      // Phase 4: Payoff (Result)
      const resultSpring = spring({ frame: Math.max(0, frame - phases.resultDelay), fps: 30, config: { damping: 12, stiffness: 140 } });
      const resultX = interpolate(resultSpring, [0, 1], [40, 0]);

      // Phase 5: Resolve (Note)
      const noteSpring = spring({ frame: Math.max(0, frame - phases.noteDelay), fps: 30, config: { damping: 16, stiffness: 120 } });
      const noteOpacity = interpolate(noteSpring, [0, 1], [0, 1]);

      return { sceneOpacity, inputX, driverY, opScale, arrowProgress, resultX, noteOpacity };
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
  {
    name: "SplitComparison",
    durations: [10, 15, 24, 34, 45, 60, 120, 180, 300],
    simulateFrame: (frame, duration_frames) => {
      const headerDelay = safeSpringDelay(0, duration_frames, 0.2);
      const headerSpring = spring({ frame: Math.max(0, frame - headerDelay), fps: 30 });
      const leftDelay = safeSpringDelay(4, duration_frames, 0.25);
      const leftSpring = spring({ frame: Math.max(0, frame - leftDelay), fps: 30 });
      const rightDelay = safeSpringDelay(8, duration_frames, 0.3);
      const rightSpring = spring({ frame: Math.max(0, frame - rightDelay), fps: 30 });
      const vsDelay = safeSpringDelay(12, duration_frames, 0.35);
      const vsSpring = spring({ frame: Math.max(0, frame - vsDelay), fps: 30 });

      const [countStart, countEnd] = safeAnimationWindow(14, 46, duration_frames, 2);
      const countProgress = interpolate(frame, [countStart, countEnd], [0, 1], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      });

      const deltaDelay = safeSpringDelay(24, duration_frames, 0.55);
      const deltaSpring = spring({ frame: Math.max(0, frame - deltaDelay), fps: 30 });

      return { headerSpring, leftSpring, rightSpring, vsSpring, countProgress, deltaSpring };
    },
  },
  {
    name: "RankedList",
    durations: [10, 15, 24, 34, 45, 60, 120, 180, 300],
    simulateFrame: (frame, duration_frames) => {
      const itemCount = 5;
      const totalBuildDuration = Math.max(1, Math.floor(duration_frames * 0.70));
      const timePerItem = Math.max(1, Math.floor(totalBuildDuration / itemCount));

      const headerDelay = safeSpringDelay(0, duration_frames, 0.15);
      const headerSpring = spring({ frame: Math.max(0, frame - headerDelay), fps: 30 });

      const results = [];
      for (let i = 0; i < itemCount; i++) {
        const itemDelay = safeSpringDelay(i * timePerItem, duration_frames, 0.65);
        const rowSpring = spring({ frame: Math.max(0, frame - itemDelay), fps: 30 });

        const [barStart, barEnd] = safeAnimationWindow(
          itemDelay + 2,
          itemDelay + Math.max(4, timePerItem),
          duration_frames,
          2
        );
        const barProgress = interpolate(frame, [barStart, barEnd], [0, 1], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        });
        results.push({ rowSpring, barProgress });
      }
      return { headerSpring, results };
    },
  },
  {
    name: "ProcessFlow",
    durations: [10, 15, 24, 34, 45, 60, 120, 180, 300],
    simulateFrame: (frame, duration_frames) => {
      const stepCount = 5;
      const totalBuildDuration = Math.max(1, Math.floor(duration_frames * 0.72));
      const timePerStep = Math.max(1, Math.floor(totalBuildDuration / stepCount));

      const headerDelay = safeSpringDelay(0, duration_frames, 0.15);
      const headerSpring = spring({ frame: Math.max(0, frame - headerDelay), fps: 30 });

      const results = [];
      for (let i = 0; i < stepCount; i++) {
        const stepDelay = safeSpringDelay(i * timePerStep, duration_frames, 0.65);
        const stepSpring = spring({ frame: Math.max(0, frame - stepDelay), fps: 30 });

        const [connStart, connEnd] = safeAnimationWindow(
          stepDelay + 2,
          stepDelay + Math.max(4, timePerStep),
          duration_frames,
          2
        );
        const connectorProgress = interpolate(frame, [connStart, connEnd], [0, 1], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        });
        results.push({ stepSpring, connectorProgress });
      }
      return { headerSpring, results };
    },
  },
  // ─── QuoteCallout — 3-phase word reveal model ──────────────────────────
  {
    name: "QuoteCallout",
    durations: [10, 15, 24, 34, 45, 60, 120, 180, 300],
    simulateFrame: (frame, duration_frames) => {
      // Phase 1 — card frame spring (safe delay at 0)
      const cardDelay = safeSpringDelay(0, duration_frames, 0.08);
      const cardSpring = spring({
        frame: Math.max(0, frame - cardDelay),
        fps: 30,
        config: { damping: 14, stiffness: 90 },
      });

      // Phase 2 — word-by-word reveal window (10% D → 58% D)
      // Simulate with a 12-word quote
      const wordCount = 12;
      const textRevealStart = Math.max(
        safeSpringDelay(4, duration_frames, 0.08),
        Math.floor(duration_frames * 0.10)
      );
      const textRevealEnd = Math.min(
        Math.floor(duration_frames * 0.58),
        duration_frames - 2
      );
      const [safeTextStart, safeTextEnd] = safeAnimationWindow(
        textRevealStart,
        Math.max(textRevealStart + wordCount, textRevealEnd),
        duration_frames,
        wordCount
      );
      const framesPerWord = Math.max(0.5, (safeTextEnd - safeTextStart) / wordCount);

      // Verify each word interpolate is valid
      for (let idx = 0; idx < wordCount; idx++) {
        const wordStart = safeTextStart + idx * framesPerWord;
        const wordEnd = Math.max(wordStart + 0.5, wordStart + Math.min(3, framesPerWord));
        const wordOpacity = interpolate(frame, [wordStart, wordEnd], [0, 1], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        });
        if (isNaN(wordOpacity) || typeof wordOpacity !== "number") {
          throw new Error(`QuoteCallout word ${idx} produced NaN at frame ${frame}/${duration_frames}`);
        }
      }

      // Closing quote mark uses last word timing
      const lastWordStart = safeTextStart + (wordCount - 1) * framesPerWord;
      const closingEnd = Math.min(lastWordStart + 3, duration_frames - 1);
      interpolate(frame, [lastWordStart, Math.max(lastWordStart + 0.5, closingEnd)], [0, 1], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      });

      // Phase 3 — author spring (65% D with safe cap at 78%)
      const authorDelay = safeSpringDelay(
        Math.floor(duration_frames * 0.65),
        duration_frames,
        0.78
      );
      const authorSpring = spring({
        frame: Math.max(0, frame - authorDelay),
        fps: 30,
        config: { damping: 15, stiffness: 100 },
      });

      return { cardSpring, safeTextStart, safeTextEnd, framesPerWord, authorSpring };
    },
  },
  // ─── IconAnimation — 3-phase one-shot bloom model ──────────────────────
  {
    name: "IconAnimation",
    durations: [10, 15, 24, 34, 45, 60, 120, 180, 300],
    simulateFrame: (frame, duration_frames) => {
      // Phase 1: Icon spring
      const iconDelay = safeSpringDelay(0, duration_frames, 0.08);
      const iconSpring = spring({
        frame: Math.max(0, frame - iconDelay),
        fps: 30,
        config: { damping: 14, stiffness: 120 },
      });

      // Phase 2: One-shot glow bloom
      const glowDelay = safeSpringDelay(
        Math.floor(duration_frames * 0.18),
        duration_frames,
        0.3
      );
      const glowSpring = spring({
        frame: Math.max(0, frame - glowDelay),
        fps: 30,
        config: { damping: 14, stiffness: 90 },
      });
      const glowScale = interpolate(glowSpring, [0, 0.7, 1], [0.8, 1.25, 1.08], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      });
      const glowOpacity = interpolate(glowSpring, [0, 0.5, 1], [0, 0.35, 0.22], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      });

      // Phase 3: Concept label
      const labelDelay = safeSpringDelay(
        Math.floor(duration_frames * 0.35),
        duration_frames,
        0.55
      );
      const labelSpring = spring({
        frame: Math.max(0, frame - labelDelay),
        fps: 30,
        config: { damping: 16, stiffness: 100 },
      });

      return { iconSpring, glowScale, glowOpacity, labelSpring };
    },
  },
  // ─── Typography — duration-safe staged text model ─────────────────────
  {
    name: "Typography",
    durations: [10, 15, 24, 34, 45, 60, 120, 180, 300],
    simulateFrame: (frame, duration_frames) => {
      // Header
      const headerDelay = safeSpringDelay(0, duration_frames, 0.08);
      const headerSpring = spring({ frame: Math.max(0, frame - headerDelay), fps: 30, config: { damping: 15, stiffness: 100 } });

      // Metric number
      const metricDelay = safeSpringDelay(0, duration_frames, 0.08);
      const metricSpring = spring({ frame: Math.max(0, frame - metricDelay), fps: 30, config: { damping: 14, stiffness: 120 } });

      // Main editorial text (tested for both standard and metric variants)
      const mainDelayStd = safeSpringDelay(8, duration_frames, 0.18);
      const mainSpringStd = spring({ frame: Math.max(0, frame - mainDelayStd), fps: 30, config: { damping: 14, stiffness: 95 } });

      const mainDelayMetric = safeSpringDelay(Math.floor(duration_frames * 0.20), duration_frames, 0.35);
      const mainSpringMetric = spring({ frame: Math.max(0, frame - mainDelayMetric), fps: 30, config: { damping: 14, stiffness: 95 } });

      // Highlight emphasis
      const highlightDelay = safeSpringDelay(8 + Math.max(6, Math.floor(duration_frames * 0.12)), duration_frames, 0.45);
      const highlightSpring = spring({ frame: Math.max(0, frame - highlightDelay), fps: 30, config: { damping: 12, stiffness: 110 } });

      // Subtitle / Author
      const subtitleDelay = safeSpringDelay(Math.floor(duration_frames * 0.45), duration_frames, 0.70);
      const subtitleSpring = spring({ frame: Math.max(0, frame - subtitleDelay), fps: 30, config: { damping: 15, stiffness: 90 } });

      // Footer
      const footerDelay = safeSpringDelay(Math.floor(duration_frames * 0.60), duration_frames, 0.80);
      const footerSpring = spring({ frame: Math.max(0, frame - footerDelay), fps: 30, config: { damping: 16, stiffness: 85 } });

      return { headerSpring, metricSpring, mainSpringStd, mainSpringMetric, highlightSpring, subtitleSpring, footerSpring };
    },
  },
  // ─── StockImage — duration-safe media overlay model ───────────────────
  {
    name: "StockImage",
    durations: [10, 15, 24, 34, 45, 60, 120, 180, 300],
    simulateFrame: (frame, duration_frames) => {
      const headerDelay = safeSpringDelay(0, duration_frames, 0.08);
      const headerSpring = spring({ frame: Math.max(0, frame - headerDelay), fps: 30, config: { damping: 16, stiffness: 110 } });

      const captionDelay = safeSpringDelay(Math.floor(duration_frames * 0.10), duration_frames, 0.25);
      const captionSpring = spring({ frame: Math.max(0, frame - captionDelay), fps: 30, config: { damping: 18, stiffness: 85 } });

      return { headerSpring, captionSpring };
    },
  },
  // ─── StockVideo — duration-safe video overlay model ───────────────────
  {
    name: "StockVideo",
    durations: [10, 15, 24, 34, 45, 60, 120, 180, 300],
    simulateFrame: (frame, duration_frames) => {
      const headerDelay = safeSpringDelay(0, duration_frames, 0.08);
      const headerSpring = spring({ frame: Math.max(0, frame - headerDelay), fps: 30, config: { damping: 16, stiffness: 110 } });

      const captionDelay = safeSpringDelay(Math.floor(duration_frames * 0.12), duration_frames, 0.28);
      const captionSpring = spring({ frame: Math.max(0, frame - captionDelay), fps: 30, config: { damping: 18, stiffness: 85 } });

      return { headerSpring, captionSpring };
    },
  },
  // ─── ProgressiveList — duration-safe sequential list model ────────────
  {
    name: "ProgressiveList",
    durations: [10, 15, 24, 34, 45, 60, 120, 180, 300],
    simulateFrame: (frame, duration_frames) => {
      const itemCount = 4;
      const headerDelay = safeSpringDelay(0, duration_frames, 0.08);
      const headerSpring = spring({ frame: Math.max(0, frame - headerDelay), fps: 30, config: { damping: 16, stiffness: 110 } });

      const guideProgress = interpolate(frame, [0, Math.max(2, Math.floor(duration_frames * 0.22))], [0, 1], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      });

      const buildStart = Math.floor(duration_frames * 0.08);
      const totalBuildDuration = Math.max(1, Math.floor(duration_frames * 0.72) - buildStart);
      const timePerItem = Math.max(1, Math.floor(totalBuildDuration / itemCount));
      const isHoldPhase = frame >= Math.floor(duration_frames * 0.72);

      const items = [];
      for (let idx = 0; idx < itemCount; idx++) {
        const nominalItemStart = buildStart + idx * timePerItem;
        const itemDelay = safeSpringDelay(nominalItemStart, duration_frames, 0.72);
        const itemSpring = spring({ frame: Math.max(0, frame - itemDelay), fps: 30, config: { damping: 15, stiffness: 100 } });
        const isRevealed = frame >= itemDelay;
        const baseOpacity = isHoldPhase ? 1.0 : 0.72;
        const currentOpacity = isRevealed ? baseOpacity * itemSpring : 0;
        items.push({ itemSpring, currentOpacity });
      }

      const footerDelay = safeSpringDelay(Math.floor(duration_frames * 0.72), duration_frames, 0.85);
      const footerSpring = spring({ frame: Math.max(0, frame - footerDelay), fps: 30, config: { damping: 16, stiffness: 90 } });

      return { headerSpring, guideProgress, items, footerSpring };
    },
  },
  // ─── BrollCaption — duration-safe broll caption model ─────────────────
  {
    name: "BrollCaption",
    durations: [10, 15, 24, 34, 45, 60, 120, 180, 300],
    simulateFrame: (frame, duration_frames) => {
      const sceneOpacity = interpolate(
        frame,
        [0, Math.min(8, Math.max(1, duration_frames - 1))],
        [0, 1],
        { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
      );
      const headerDelay = safeSpringDelay(0, duration_frames, 0.08);
      const headerSpring = spring({
        frame: Math.max(0, frame - headerDelay),
        fps: 30,
        config: { damping: 16, stiffness: 110 },
      });
      const cardSpring = spring({
        frame: Math.max(0, frame - headerDelay),
        fps: 30,
        config: { damping: 18, stiffness: 90 },
      });

      const words = ["Essential", "Strategic", "Perspective", "For", "Long", "Term", "Compounding"];
      const nominalTextStart = Math.floor(duration_frames * 0.08);
      const nominalTextEnd = Math.min(
        Math.floor(duration_frames * 0.55),
        nominalTextStart + Math.max(10, Math.round(words.length * 2.2))
      );
      const [textStart, textEnd] = safeAnimationWindow(nominalTextStart, nominalTextEnd, duration_frames);
      const framesPerWord = Math.max(0.6, (textEnd - textStart) / Math.max(1, words.length));

      const wordOpacities = words.map((_, i) => {
        const wStart = textStart + i * framesPerWord;
        return interpolate(frame, [wStart, wStart + 3], [0, 1], {
          extrapolateLeft: 'clamp',
          extrapolateRight: 'clamp',
        });
      });

      const payoffNominal = textEnd + 3;
      const boxDelay = safeSpringDelay(payoffNominal, duration_frames, 0.72);
      const boxSpring = spring({
        frame: Math.max(0, frame - boxDelay),
        fps: 30,
        config: { damping: 14, stiffness: 115 },
      });

      const authorDelay = safeSpringDelay(payoffNominal, duration_frames, 0.72);
      const authorSpring = spring({
        frame: Math.max(0, frame - authorDelay),
        fps: 30,
        config: { damping: 15, stiffness: 110 },
      });

      const pulseGlow = interpolate(boxSpring, [0, 0.7, 1], [0.4, 1.0, 0.65], {
        extrapolateLeft: 'clamp',
        extrapolateRight: 'clamp',
      });

      return { sceneOpacity, headerSpring, cardSpring, wordOpacities, boxSpring, authorSpring, pulseGlow };
    },
  },
  // ─── DataTable — duration-safe editorial financial table model ────────
  {
    name: "DataTable",
    durations: [10, 15, 24, 34, 45, 60, 120, 180, 300],
    simulateFrame: (frame, duration_frames) => {
      const rowCount = 4;
      const targetRowIdx = 1;

      const sceneOpacity = interpolate(
        frame,
        [0, Math.min(8, Math.max(1, duration_frames - 1))],
        [0, 1],
        { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
      );

      const headerDelay = safeSpringDelay(0, duration_frames, 0.08);
      const headerSpring = spring({
        frame: Math.max(0, frame - headerDelay),
        fps: 30,
        config: { damping: 16, stiffness: 110 },
      });

      const colDelay = safeSpringDelay(Math.floor(duration_frames * 0.03), duration_frames, 0.10);
      const colSpring = spring({
        frame: Math.max(0, frame - colDelay),
        fps: 30,
        config: { damping: 16, stiffness: 105 },
      });

      const buildStart = Math.floor(duration_frames * 0.08);
      const buildEnd = Math.floor(duration_frames * 0.65);
      const totalBuildDuration = Math.max(1, buildEnd - buildStart);
      const timePerRow = Math.max(1, Math.floor(totalBuildDuration / Math.max(1, rowCount)));

      const nominalSpotlightStart = Math.max(
        buildStart + timePerRow * Math.min(rowCount, 2),
        Math.floor(duration_frames * 0.60)
      );
      const spotlightDelay = safeSpringDelay(nominalSpotlightStart, duration_frames, 0.72);
      const spotlightSpring = spring({
        frame: Math.max(0, frame - spotlightDelay),
        fps: 30,
        config: { damping: 14, stiffness: 100 },
      });

      const footerDelay = safeSpringDelay(Math.floor(duration_frames * 0.72), duration_frames, 0.85);
      const footerSpring = spring({
        frame: Math.max(0, frame - footerDelay),
        fps: 30,
        config: { damping: 16, stiffness: 90 },
      });

      const rows = [];
      for (let rIdx = 0; rIdx < rowCount; rIdx++) {
        const nominalRowStart = buildStart + rIdx * timePerRow;
        const rowDelay = safeSpringDelay(nominalRowStart, duration_frames, 0.68);
        const rowSpring = spring({
          frame: Math.max(0, frame - rowDelay),
          fps: 30,
          config: { damping: 15, stiffness: 95 },
        });

        const isTargetRow = targetRowIdx === rIdx;
        const unselectedDim = interpolate(spotlightSpring, [0, 1], [0.92, 0.40], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        });
        const rowOpacity = (isTargetRow ? 1.0 : unselectedDim) * rowSpring;
        const rowScale = isTargetRow
          ? interpolate(spotlightSpring, [0, 1], [1.0, 1.018], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            })
          : 1.0;

        rows.push({ rowSpring, rowOpacity, rowScale });
      }

      return { sceneOpacity, headerSpring, colSpring, spotlightSpring, footerSpring, rows };
    },
  },
  // ─── GrowthTrajectory — 5-phase growth trajectory model ─────────────
  {
    name: "GrowthTrajectory",
    durations: [10, 15, 24, 34, 45, 60, 120, 180, 300],
    simulateFrame: (frame, duration_frames) => {
      const sceneOpacity = interpolate(
        frame,
        [0, Math.min(8, Math.max(1, duration_frames - 1))],
        [0, 1],
        { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
      );

      const headerDelay = safeSpringDelay(4, duration_frames, 0.1);
      const headerSpring = spring({
        frame: Math.max(0, frame - headerDelay),
        fps: 30,
      });

      const startCardDelay = safeSpringDelay(8, duration_frames, 0.18);
      const startCardSpring = spring({
        frame: Math.max(0, frame - startCardDelay),
        fps: 30,
      });

      const [curveStart, curveEnd] = safeAnimationWindow(18, 75, duration_frames);
      const curveProgress = interpolate(
        frame,
        [curveStart, curveEnd],
        [0, 1],
        { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
      );

      const milestoneDelay = safeSpringDelay(38, duration_frames, 0.48);
      const milestoneSpring = spring({
        frame: Math.max(0, frame - milestoneDelay),
        fps: 30,
      });

      const payoffDelay = safeSpringDelay(56, duration_frames, 0.68);
      const payoffSpring = spring({
        frame: Math.max(0, frame - payoffDelay),
        fps: 30,
      });

      const currentLeadX = interpolate(curveProgress, [0, 1], [80, 880]);
      const currentLeadY = interpolate(curveProgress, [0, 0.5, 1], [290, 227, 65]);
      const areaOpacity = interpolate(curveProgress, [0, 0.3], [0, 1], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      });

      return {
        sceneOpacity,
        headerSpring,
        startCardSpring,
        curveProgress,
        milestoneSpring,
        payoffSpring,
        currentLeadX,
        currentLeadY,
        areaOpacity,
      };
    },
  },
  {
    name: 'TrajectoryDivergence',
    durations: [30, 60, 90, 120, 150, 180, 240, 300, 360],
    props: {
      headerLabel: 'WEALTH ACCUMULATION DIVERGENCE',
      timeHorizon: '10 Years',
      baselineLabel: '₹30,000 Monthly Commitment',
      pathA: {
        label: 'Investor (Equity SIP)',
        endValue: '₹38 Lakh',
        rate: '12% CAGR',
        direction: 'up',
        tone: 'positive',
      },
      pathB: {
        label: 'Spender (Car EMI)',
        startValue: '₹15 Lakh Car',
        endValue: '₹6 Lakh Resale',
        rate: '15% Depreciation',
        direction: 'down',
        tone: 'negative',
      },
      divergenceGap: '₹32 Lakh Wealth Gap',
      variant: 'wealth_gap',
    },
    simulateFrame: (frame, duration_frames) => {
      const sceneOpacity = interpolate(
        frame,
        [0, Math.min(8, Math.max(1, duration_frames - 1))],
        [0, 1],
        { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
      );
      const headerDelay = safeSpringDelay(4, duration_frames);
      const headerSpring = spring({ frame: Math.max(0, frame - headerDelay), fps: 30 });
      
      const baselineDelay = safeSpringDelay(10, duration_frames);
      const baselineSpring = spring({ frame: Math.max(0, frame - baselineDelay), fps: 30 });

      const [pathStart, pathEnd] = safeAnimationWindow(18, 80, duration_frames);
      const pathProgress = interpolate(frame, [pathStart, pathEnd], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });

      const cardADelay = safeSpringDelay(55, duration_frames);
      const cardASpring = spring({ frame: Math.max(0, frame - cardADelay), fps: 30 });
      
      const cardBDelay = safeSpringDelay(55, duration_frames);
      const cardBSpring = spring({ frame: Math.max(0, frame - cardBDelay), fps: 30 });

      const gapDelay = safeSpringDelay(70, duration_frames);
      const gapSpring = spring({ frame: Math.max(0, frame - gapDelay), fps: 30 });

      return { sceneOpacity, headerSpring, baselineSpring, pathProgress, cardASpring, cardBSpring, gapSpring };
    },
  },
  {
    name: 'CashFlowWaterfall',
    durations: [30, 60, 90, 120, 150, 180, 240, 300, 360],
    props: {
      headerLabel: 'MONTHLY CASH FLOW',
      startingLabel: 'Gross Monthly Salary',
      startingValue: '₹5,00,000',
      steps: [
        { label: 'Taxes', value: '-₹1,50,000', direction: 'subtract', subtext: 'Direct Tax Code' },
        { label: 'EMI Obligations', value: '-₹1,20,000', direction: 'subtract', subtext: 'Car & Personal Loans' },
        { label: 'Living Expenses', value: '-₹1,50,000', direction: 'subtract' },
      ],
      finalLabel: 'Investable Surplus',
      finalValue: '₹80,000',
      variant: 'standard',
    },
    simulateFrame: (frame, duration_frames) => {
      const sceneOpacity = interpolate(
        frame,
        [0, Math.min(8, Math.max(1, duration_frames - 1))],
        [0, 1],
        { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
      );
      
      const headerDelay = safeSpringDelay(4, duration_frames);
      const headerSpring = spring({ frame: Math.max(0, frame - headerDelay), fps: 30 });
      
      const startingDelay = safeSpringDelay(10, duration_frames);
      const startingSpring = spring({ frame: Math.max(0, frame - startingDelay), fps: 30 });
      
      // Simulate max 3 steps for safety limits check
      const stepsCount = duration_frames < 90 ? Math.min(3, 3) : 3;
      for (let i = 0; i < stepsCount; i++) {
        const stepDelay = safeSpringDelay(20 + i * 10, duration_frames);
        const stepSpring = spring({ frame: Math.max(0, frame - stepDelay), fps: 30 });
      }
      
      const finalDelay = safeSpringDelay(20 + stepsCount * 10 + 10, duration_frames);
      const finalSpring = spring({ frame: Math.max(0, frame - finalDelay), fps: 30 });
      
      return { sceneOpacity, headerSpring, startingSpring, finalSpring };
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
