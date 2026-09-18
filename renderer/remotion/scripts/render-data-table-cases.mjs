/**
 * DataTable render cases — validates duration-safe staged row disclosure, frame-driven spotlight, and annotation payoff
 * Tests: 30f, 45f, 90f, 150f, 300f + realistic financial narrative example + progression frames
 *
 * Usage: node scripts/render-data-table-cases.mjs
 */
import { bundle } from "@remotion/bundler";
import { getCompositions, renderStill } from "@remotion/renderer";
import { mkdir } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const rendererRoot = path.resolve(scriptDir, "..");
const outputBase = path.resolve(scriptDir, "../test-renders/data-table");

await mkdir(outputBase, { recursive: true });

// ── Shared example props ─────────────────────────────────────────────────
const realisticTechTable = {
  headerLabel: "BIG TECH CAPITAL EFFICIENCY",
  title: "Operating Margin Comparison (FY2023)",
  columns: ["Company", "Revenue", "Operating Income", "Margin"],
  rows: [
    ["Microsoft", "$211.9B", "$88.5B", "+41.8%"],
    ["Apple", "$383.3B", "$114.3B", "+29.8%"],
    ["Alphabet", "$307.4B", "$84.3B", "+27.4%"],
    ["Amazon", "$574.8B", "$36.9B", "+6.4%"],
  ],
  highlightRow: 0,
  annotation: "Microsoft leads Big Tech with 41.8% margin efficiency",
  footerLabel: "SEC FORM 10-K FILINGS // GAAP OPERATING RESULTS",
};

const shortTable = {
  headerLabel: "ASSET VALUATION",
  columns: ["Asset Class", "Yield", "Real Return"],
  rows: [
    ["US Equities", "1.6%", "+7.2%"],
    ["10Y Treasuries", "4.3%", "+1.5%"],
    ["Cash Equivalents", "5.1%", "-0.2%"],
  ],
  highlightRow: 0,
  annotation: "Equities remain highest real yielding asset",
  footerLabel: "FEDERAL RESERVE ECONOMIC DATA (FRED)",
};

// ── Test cases ───────────────────────────────────────────────────────────
const cases = [
  // Duration stress tests
  { label: "30f-short", durationFrames: 30, props: shortTable },
  { label: "45f-short", durationFrames: 45, props: shortTable },
  { label: "90f-short", durationFrames: 90, props: realisticTechTable },

  // Medium duration
  { label: "150f-medium", durationFrames: 150, props: realisticTechTable },

  // Long duration
  { label: "300f-long", durationFrames: 300, props: realisticTechTable },

  // Realistic narrative: 180f (6s at 30fps) settled
  { label: "180f-realistic-settled", durationFrames: 180, props: realisticTechTable },

  // Progression frames on 180f
  // Phase 1: Header and columns entrance (frame 15)
  { label: "180f-phase1-columns", durationFrames: 180, props: realisticTechTable, frameOverride: 15 },

  // Phase 2: Rows midway revealing (frame 60)
  { label: "180f-phase2-rows-reveal", durationFrames: 180, props: realisticTechTable, frameOverride: 60 },

  // Phase 3: Spotlight focus & annotation payoff (frame 145)
  { label: "180f-phase3-spotlight-payoff", durationFrames: 180, props: realisticTechTable, frameOverride: 145 },
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
    composition: "DataTable",
    fps,
    duration_frames: tc.durationFrames,
    durationInFrames: tc.durationFrames,
    props: tc.props,
  };

  try {
    const compositions = await getCompositions(serveUrl, { inputProps });
    const comp = compositions.find((candidate) => candidate.id === "DataTable");
    if (!comp) {
      throw new Error("DataTable composition not found in Root.tsx");
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
