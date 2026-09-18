/**
 * Typography render cases — validates duration-safe progressive springs & multi-variant staging
 * Tests: 30f, 45f, 90f, 150f, 300f + realistic narrative example + variants
 *
 * Usage: node scripts/render-typography-cases.mjs
 */
import { bundle } from "@remotion/bundler";
import { getCompositions, renderStill } from "@remotion/renderer";
import { mkdir } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const rendererRoot = path.resolve(scriptDir, "..");
const outputBase = path.resolve(scriptDir, "../test-renders/typography");

await mkdir(outputBase, { recursive: true });

// ── Shared example props ─────────────────────────────────────────────────
const standardHeadline = {
  headerLabel: "MACROECONOMIC SHIFT",
  text: "The greatest risk to capital is not volatility, but permanent loss.",
  highlight: "permanent loss",
  subtitle: "Understanding drawdowns versus short-term price fluctuations",
  footerLabel: "PORTFOLIO PRESERVATION DOCTRINE",
};

const metricExample = {
  headerLabel: "INFLATION RUN-RATE",
  value: "7.4%",
  text: "Real purchasing power degradation per annum across key consumption baskets",
  subtitle: "Source: Ministry of Statistics and Programme Implementation",
  footerLabel: "HISTORICAL 10-YEAR AVERAGE",
};

const questionExample = {
  headerLabel: "CAPITAL ALLOCATION",
  text: "Are you paying for past performance or future cash flows?",
  highlight: "future cash flows",
  subtitle: "How retail investors repeatedly buy peak cycle narratives",
};

const quoteExample = {
  headerLabel: "INVESTING WISDOM",
  text: '"Price is what you pay. Value is what you get."',
  author: "Warren Buffett",
  footerLabel: "BERKSHIRE HATHAWAY ANNUAL LETTER",
};

// ── Test cases ───────────────────────────────────────────────────────────
const cases = [
  // Duration stress tests
  { label: "30f-short", durationFrames: 30, props: standardHeadline },
  { label: "45f-short", durationFrames: 45, props: standardHeadline },
  { label: "90f-short", durationFrames: 90, props: standardHeadline },

  // Medium duration (question variant)
  { label: "150f-question", durationFrames: 150, props: questionExample },

  // Long duration (quote variant)
  { label: "300f-long", durationFrames: 300, props: quoteExample },

  // Realistic narrative: 180f (6s at 30fps) with headline + highlight + subtitle + footer
  { label: "180f-realistic", durationFrames: 180, props: standardHeadline },

  // Metric variant verification: 180f
  { label: "180f-metric-variant", durationFrames: 180, props: metricExample },

  // Phase 1 verification on metric: render at frame 15 (number established, text entering)
  { label: "180f-metric-phase1", durationFrames: 180, props: metricExample, frameOverride: 15 },

  // Phase 2 verification: render at highlight emphasis moment (frame 45 on 180f)
  { label: "180f-highlight-phase", durationFrames: 180, props: standardHeadline, frameOverride: 45 },
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
    composition: "Typography",
    fps,
    duration_frames: tc.durationFrames,
    durationInFrames: tc.durationFrames,
    props: tc.props,
  };

  try {
    const compositions = await getCompositions(serveUrl, { inputProps });
    const comp = compositions.find((candidate) => candidate.id === "Typography");
    if (!comp) {
      throw new Error("Typography composition not found in Root.tsx");
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
