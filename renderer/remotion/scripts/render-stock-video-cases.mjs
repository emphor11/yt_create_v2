/**
 * StockVideo render cases — validates duration-safe video overlay springs and visual hold
 * Tests: 30f, 45f, 90f, 150f, 300f + realistic narrative example
 *
 * Usage: node scripts/render-stock-video-cases.mjs
 */
import { bundle } from "@remotion/bundler";
import { getCompositions, renderStill } from "@remotion/renderer";
import { mkdir } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const rendererRoot = path.resolve(scriptDir, "..");
const outputBase = path.resolve(scriptDir, "../test-renders/stock-video");

await mkdir(outputBase, { recursive: true });

// ── Shared example props ─────────────────────────────────────────────────
const standardCaption = {
  headerLabel: "KINETIC MARKET FORCES",
  text: "High-frequency algorithmic trading triggers cascading market flash events",
  subtitle: "Microsecond order books amplify structural volatility during liquidity shocks",
};

const shortCaption = {
  headerLabel: "LIQUIDITY DYNAMICS",
  text: "Sovereign debt rollovers require constant primary dealer absorption",
};

const longCaption = {
  headerLabel: "INSTITUTIONAL EXECUTION",
  text: "Dark pool matching systems internalize cross-asset volume away from exchanges",
  subtitle: "Price discovery fragments as off-exchange block trades dominate retail flow",
};

// ── Test cases ───────────────────────────────────────────────────────────
const cases = [
  // Duration stress tests
  { label: "30f-short", durationFrames: 30, props: shortCaption },
  { label: "45f-short", durationFrames: 45, props: shortCaption },
  { label: "90f-short", durationFrames: 90, props: standardCaption },

  // Medium duration
  { label: "150f-medium", durationFrames: 150, props: standardCaption },

  // Long duration
  { label: "300f-long", durationFrames: 300, props: longCaption },

  // Realistic narrative: 180f (6s at 30fps) with full video overlay
  { label: "180f-realistic", durationFrames: 180, props: standardCaption },

  // Phase 1 verification: render at frame 6 (header visible, caption card held back)
  { label: "150f-phase1-hold", durationFrames: 150, props: standardCaption, frameOverride: 6 },

  // Phase 2 verification: render at frame 28 (caption card actively translating in)
  { label: "150f-phase2-entering", durationFrames: 150, props: standardCaption, frameOverride: 28 },
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
    composition: "StockVideo",
    fps,
    duration_frames: tc.durationFrames,
    durationInFrames: tc.durationFrames,
    props: tc.props,
  };

  try {
    const compositions = await getCompositions(serveUrl, { inputProps });
    const comp = compositions.find((candidate) => candidate.id === "StockVideo");
    if (!comp) {
      throw new Error("StockVideo composition not found in Root.tsx");
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
