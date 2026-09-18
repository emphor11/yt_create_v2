/**
 * IconAnimation render cases — validates 3-phase one-shot bloom upgrade
 * Tests: 30f, 45f, 90f, 150f, 300f + realistic narrative example
 *
 * Usage: node scripts/render-icon-animation-cases.mjs
 */
import { bundle } from "@remotion/bundler";
import { getCompositions, renderStill } from "@remotion/renderer";
import { mkdir } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const rendererRoot = path.resolve(scriptDir, "..");
const outputBase = path.resolve(scriptDir, "../test-renders/icon-animation");

await mkdir(outputBase, { recursive: true });

// ── Shared example props ─────────────────────────────────────────────────
const standardWarning = {
  headerLabel: "KEY VULNERABILITY",
  icon: "⚠️",
  label: "Inflation silently erodes purchasing power over time",
  footerLabel: "CORE RETIREMENT RISK",
};

const financialInsight = {
  headerLabel: "WEALTH PRINCIPLE",
  icon: "💡",
  label: "Assets must compound faster than the rate of money supply growth",
  footerLabel: "PORTFOLIO TARGET",
};

const marketShield = {
  headerLabel: "CAPITAL DEFENSE",
  icon: "🛡️",
  label: "Hedging downside volatility protects terminal portfolio wealth",
  footerLabel: "RISK ALLOCATION",
};

// ── Test cases ───────────────────────────────────────────────────────────
const cases = [
  // Duration stress tests
  { label: "30f-short", durationFrames: 30, props: standardWarning },
  { label: "45f-short", durationFrames: 45, props: standardWarning },
  { label: "90f-short", durationFrames: 90, props: financialInsight },

  // Medium duration
  { label: "150f-medium", durationFrames: 150, props: financialInsight },

  // Long duration
  { label: "300f-long", durationFrames: 300, props: marketShield },

  // Realistic narrative: 180f (6s at 30fps) with full concept
  { label: "180f-realistic", durationFrames: 180, props: standardWarning },

  // Phase 1 verification: render at early frame (frame 15 on 150f) to see icon arriving before bloom
  { label: "150f-icon-entrance", durationFrames: 150, props: financialInsight, frameOverride: 15 },

  // Phase 2 verification: render at bloom peak (frame 38 on 150f)
  { label: "150f-bloom-peak", durationFrames: 150, props: financialInsight, frameOverride: 38 },

  // Phase 3 verification: render at label reveal (frame 70 on 150f)
  { label: "150f-label-reveal", durationFrames: 150, props: financialInsight, frameOverride: 70 },
];

console.log("Bundling Remotion...");
const entryPoint = path.join(rendererRoot, "src/index.ts");
const serveUrl = await bundle({
  entryPoint,
  onProgress: () => undefined,
});

let passed = 0;
let failed = 0;

for (const tc of cases) {
  const fps = 30;
  const frame =
    tc.frameOverride !== undefined
      ? tc.frameOverride
      : Math.floor(tc.durationFrames * 0.85); // default: near end (settled payoff)

  const outputPath = path.join(outputBase, `${tc.label}-frame${frame}.png`);

  const inputProps = {
    scene_id: `scene_${tc.label}`,
    composition: "IconAnimation",
    fps,
    duration_frames: tc.durationFrames,
    durationInFrames: tc.durationFrames,
    props: tc.props,
  };

  try {
    const compositions = await getCompositions(serveUrl, { inputProps });
    const comp = compositions.find((candidate) => candidate.id === "IconAnimation");
    if (!comp) {
      throw new Error("IconAnimation composition not found in Root.tsx");
    }

    await renderStill({
      composition: {
        ...comp,
        durationInFrames: tc.durationFrames,
      },
      serveUrl,
      output: outputPath,
      inputProps,
      frame,
      imageFormat: "png",
      logLevel: "error",
    });
    console.log(
      `✓ ${tc.label.padEnd(24)} frame=${String(frame).padStart(3)}/${tc.durationFrames} → ${path.basename(outputPath)}`
    );
    passed++;
  } catch (err) {
    console.error(`✗ ${tc.label} FAILED: ${err.message}`);
    failed++;
  }
}

console.log(`\nRender cases: ${passed} passed, ${failed} failed`);
console.log(`Output: ${outputBase}`);
if (failed > 0) process.exit(1);
