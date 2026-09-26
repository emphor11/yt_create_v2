import { bundle } from "@remotion/bundler";
import { getCompositions, renderStill } from "@remotion/renderer";
import { mkdir } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const rendererRoot = path.resolve(scriptDir, "..");
const outputDir = "/Users/dakshyadav/.gemini/antigravity/brain/6d419c6d-aa14-47ab-a0a4-e305e6158af7/scratch/comparison_split_test";
await mkdir(outputDir, { recursive: true });

console.log("Bundling Remotion project...");
const entryPoint = path.join(rendererRoot, "src/index.ts");
const serveUrl = await bundle({
  entryPoint,
  onProgress: () => undefined,
});

const testCases = [
  // Case 1: START TODAY 1x vs WAIT 10 YEARS 2x
  {
    name: "case1_multiplier_choice",
    frame: 140,
    props: {
      scene_id: "case1",
      composition: "SplitComparison",
      fps: 30,
      duration_frames: 180,
      props: {
        headerLabel: "TIME HORIZON COMPARISON",
        comparisonLabel: "OPPORTUNITY COST",
        leftRole: "START TODAY",
        leftValue: "1×",
        leftLabel: "Immediate Capital Compounding",
        rightRole: "WAIT 10 YEARS",
        rightValue: "2×",
        rightLabel: "Required Multiplier to Catch Up",
        delta: "+100% Capital Burden",
        winner: "left",
        tone: "positive_negative",
        footerLabel: "DELAY DOUBLES THE CAPITAL REQUIREMENT",
      },
    },
  },
  // Case 2: Traditional FD 6.5% vs Nifty 50 Index 12.2%
  {
    name: "case2_rate_benchmark",
    frame: 140,
    props: {
      scene_id: "case2",
      composition: "SplitComparison",
      fps: 30,
      duration_frames: 180,
      props: {
        headerLabel: "STRATEGY BENCHMARK",
        comparisonLabel: "20-YEAR WEALTH OUTCOME",
        leftRole: "Traditional FD",
        leftValue: "6.5%",
        leftLabel: "Fixed Deposit Baseline",
        leftUnit: "p.a.",
        rightRole: "Nifty 50 Index",
        rightValue: "12.2%",
        rightLabel: "Index Fund SIP Strategy",
        rightUnit: "CAGR",
        delta: "+5.7% Real Alpha",
        winner: "right",
        tone: "superiority",
        footerLabel: "COMPOUNDING SPREAD DRIVES DIVERGENCE",
      },
    },
  },
  // Case 3: ₹50,000 vs ₹75,000 Quantity Comparison
  {
    name: "case3_quantity_spread",
    frame: 140,
    props: {
      scene_id: "case3",
      composition: "SplitComparison",
      fps: 30,
      duration_frames: 180,
      props: {
        headerLabel: "COMPENSATION BENCHMARK",
        leftRole: "Entry Level",
        leftValue: "₹50,000",
        leftLabel: "Fixed Monthly Retainer",
        rightRole: "Senior Specialist",
        rightValue: "₹75,000",
        rightLabel: "Market Discretionary Rate",
        delta: "₹25,000 Spread",
        winner: "right",
        tone: "before_after",
      },
    },
  },
  // Case 4: Pure structural comparison without delta
  {
    name: "case4_no_delta_structural",
    frame: 140,
    props: {
      scene_id: "case4",
      composition: "SplitComparison",
      fps: 30,
      duration_frames: 180,
      props: {
        headerLabel: "HEAD-TO-HEAD COMPARISON",
        leftRole: "Option A",
        leftValue: "₹10,000",
        leftLabel: "Initial Baseline",
        rightRole: "Option B",
        rightValue: "₹25,000",
        rightLabel: "Target Strategy",
      },
    },
  },
];

console.log("Rendering comparison cases...");
for (const tc of testCases) {
  const compositions = await getCompositions(serveUrl, { inputProps: tc.props });
  const comp = compositions.find((c) => c.id === "SplitComparison");
  const fileName = `${tc.name}_f${tc.frame}.png`;
  const outPath = path.join(outputDir, fileName);
  console.log(`Rendering ${tc.name} at frame ${tc.frame} -> ${fileName}...`);
  await renderStill({
    composition: comp,
    serveUrl,
    output: outPath,
    inputProps: tc.props,
    frame: tc.frame,
  });
  console.log(`Saved ${fileName}`);
}

// Kinetic progression frames for case1 (frames 1, 15, 30, 45, 75, 140)
const progressionFrames = [1, 15, 30, 45, 75, 140];
console.log("\nRendering choreography progression for case 1...");
for (const f of progressionFrames) {
  const compositions = await getCompositions(serveUrl, { inputProps: testCases[0].props });
  const comp = compositions.find((c) => c.id === "SplitComparison");
  const fileName = `progression_case1_f${f}.png`;
  const outPath = path.join(outputDir, fileName);
  console.log(`Rendering progression frame ${f} -> ${fileName}...`);
  await renderStill({
    composition: comp,
    serveUrl,
    output: outPath,
    inputProps: testCases[0].props,
    frame: f,
  });
  console.log(`Saved ${fileName}`);
}

console.log("\nAll ComparisonSplit renders complete!");
