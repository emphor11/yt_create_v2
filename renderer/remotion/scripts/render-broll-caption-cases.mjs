/**
 * BrollCaption render cases — validates duration-safe staged reveal, word progression, and emphasis payoff
 * Tests: 30f, 45f, 90f, 150f, 300f + statement, quote, ambient_broll variants + progression frames
 *
 * Usage: node scripts/render-broll-caption-cases.mjs
 */
import { bundle } from "@remotion/bundler";
import { getCompositions, renderStill } from "@remotion/renderer";
import { mkdir } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const rendererRoot = path.resolve(scriptDir, "..");
const outputBase = path.resolve(scriptDir, "../test-renders/broll-caption");

await mkdir(outputBase, { recursive: true });

// ── Shared example props ─────────────────────────────────────────────────
const statementProps = {
  headerLabel: "CORE FINANCIAL LAW // ASSET ALLOCATION",
  caption: "The stock market is a device for transferring money from the impatient to the patient.",
  emphasisPhrase: "PATIENCE GENERATES COMPOUNDING",
  polarity: "positive",
  variant: "statement",
};

const quoteProps = {
  headerLabel: "LUMINARY WISDOM // VALUE INVESTING",
  caption: "Price is what you pay. Value is what you get.",
  author: "Warren Buffett",
  sourceContext: "Chairman & CEO, Berkshire Hathaway",
  variant: "quote",
};

const ambientProps = {
  headerLabel: "MACROECONOMIC CONTEXT // LIQUIDITY CYCLE",
  caption: "Central banks control the cost of money, dictating asset prices across every global exchange.",
  emphasisPhrase: "LIQUIDITY EXPANSION PHASE",
  polarity: "critical",
  variant: "ambient_broll",
};

// ── Test cases ───────────────────────────────────────────────────────────
const cases = [
  // Duration stress tests
  { label: "30f-short-statement", durationFrames: 30, props: statementProps },
  { label: "45f-short-statement", durationFrames: 45, props: statementProps },
  { label: "90f-short-quote", durationFrames: 90, props: quoteProps },

  // Medium duration
  { label: "150f-medium-ambient", durationFrames: 150, props: ambientProps },

  // Long duration
  { label: "300f-long-statement", durationFrames: 300, props: statementProps },

  // Realistic narrative (180f): Statement settled
  { label: "180f-statement-settled", durationFrames: 180, props: statementProps },

  // Realistic narrative (180f): Quote settled
  { label: "180f-quote-settled", durationFrames: 180, props: quoteProps },

  // Realistic narrative (180f): Ambient settled
  { label: "180f-ambient-settled", durationFrames: 180, props: ambientProps },

  // Phase progression frames on 180f statement
  // Phase 1: Header / card entrance (frame 15)
  { label: "180f-phase1-entrance", durationFrames: 180, props: statementProps, frameOverride: 15 },

  // Phase 2: Word-by-word reveal in progress (frame 50)
  { label: "180f-phase2-word-reveal", durationFrames: 180, props: statementProps, frameOverride: 50 },

  // Phase 3: Emphasis payoff bloom & settled state (frame 140)
  { label: "180f-phase3-payoff-bloom", durationFrames: 180, props: statementProps, frameOverride: 140 },
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
    composition: "BrollCaption",
    fps,
    duration_frames: tc.durationFrames,
    durationInFrames: tc.durationFrames,
    props: tc.props,
  };

  try {
    const compositions = await getCompositions(serveUrl, { inputProps });
    const comp = compositions.find((candidate) => candidate.id === "BrollCaption");
    if (!comp) {
      throw new Error("BrollCaption composition not found in Root.tsx");
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
      `✓ ${tc.label.padEnd(28)} frame=${String(frame).padStart(3)}/${tc.durationFrames} → ${path.basename(outputPath)}`
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
