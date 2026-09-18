/**
 * ProgressiveList render cases — validates duration-safe progressive item reveal & consolidation hold
 * Tests: 30f, 45f, 90f, 150f, 300f + realistic narrative example
 *
 * Usage: node scripts/render-progressive-list-cases.mjs
 */
import { bundle } from "@remotion/bundler";
import { getCompositions, renderStill } from "@remotion/renderer";
import { mkdir } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const rendererRoot = path.resolve(scriptDir, "..");
const outputBase = path.resolve(scriptDir, "../test-renders/progressive-list");

await mkdir(outputBase, { recursive: true });

// ── Shared example props ─────────────────────────────────────────────────
const standardList = {
  headerLabel: "WEALTH DESTRUCTION PATHWAYS",
  items: [
    {
      title: "Negative Real Yields",
      subtitle: "Fixed deposits trailing consumer inflation erode purchasing power",
      value: "-2.4%",
    },
    {
      title: "Excessive Management Fees",
      subtitle: "Compounded 2% expense ratios consume 40% of terminal corpus",
      value: "40% Drag",
    },
    {
      title: "Taxes on Nominal Gains",
      subtitle: "Paying capital gains tax on phantom inflation-driven price increases",
      value: "12.5% LTCG",
    },
    {
      title: "Premature Liquidation",
      subtitle: "Panic selling during bear market drawdowns locks in paper losses",
      value: "Irreversible",
    },
  ],
  footerLabel: "FOUR STRUCTURAL RETIREMENT HEADWINDS",
};

const shortList = {
  headerLabel: "PORTFOLIO RULES",
  items: [
    { title: "Preserve capital principal above all else" },
    { title: "Diversify across uncorrelated risk premiums" },
    { title: "Minimize friction, turnover, and transaction fees" },
  ],
};

// ── Test cases ───────────────────────────────────────────────────────────
const cases = [
  // Duration stress tests
  { label: "30f-short", durationFrames: 30, props: shortList },
  { label: "45f-short", durationFrames: 45, props: shortList },
  { label: "90f-short", durationFrames: 90, props: standardList },

  // Medium duration
  { label: "150f-medium", durationFrames: 150, props: standardList },

  // Long duration
  { label: "300f-long", durationFrames: 300, props: standardList },

  // Realistic narrative: 180f (6s at 30fps) with full 4-item list + subtitle + values
  { label: "180f-realistic", durationFrames: 180, props: standardList },

  // Phase 1 / early item 1 verification
  { label: "180f-item1-entrance", durationFrames: 180, props: standardList, frameOverride: 25 },

  // Phase 2 / item 2 spotlight verification
  { label: "180f-item2-spotlight", durationFrames: 180, props: standardList, frameOverride: 65 },

  // Phase 2 / item 3 spotlight verification
  { label: "180f-item3-spotlight", durationFrames: 180, props: standardList, frameOverride: 105 },

  // Phase 3 / consolidation hold verification (frame 155 on 180f)
  { label: "180f-consolidation-hold", durationFrames: 180, props: standardList, frameOverride: 155 },
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
    composition: "ProgressiveList",
    fps,
    duration_frames: tc.durationFrames,
    durationInFrames: tc.durationFrames,
    props: tc.props,
  };

  try {
    const compositions = await getCompositions(serveUrl, { inputProps });
    const comp = compositions.find((candidate) => candidate.id === "ProgressiveList");
    if (!comp) {
      throw new Error("ProgressiveList composition not found in Root.tsx");
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
      `✓ ${tc.label.padEnd(26)} frame=${String(frame).padStart(3)}/${tc.durationFrames} → ${path.basename(outputPath)}`
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
