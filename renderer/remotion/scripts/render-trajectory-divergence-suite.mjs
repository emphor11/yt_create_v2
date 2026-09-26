import { bundle } from "@remotion/bundler";
import { getCompositions, renderStill, renderMedia } from "@remotion/renderer";
import { mkdir } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const rendererRoot = path.resolve(scriptDir, "..");
const outputDir = "/Users/dakshyadav/.gemini/antigravity/brain/6d419c6d-aa14-47ab-a0a4-e305e6158af7/scratch/trajectory_divergence_test";

await mkdir(outputDir, { recursive: true });

console.log("Bundling Remotion project...");
const entryPoint = path.join(rendererRoot, "src/index.ts");
const serveUrl = await bundle({
  entryPoint,
  onProgress: () => undefined,
});

// ---------------------------------------------------------------------------
// Test Cases
// ---------------------------------------------------------------------------

// 1. Positive vs Negative Divergence
const case1_pos_neg = {
  headerLabel: "WEALTH ACCUMULATION DIVERGENCE",
  timeHorizon: "10 Years",
  baselineLabel: "₹30,000 Monthly Commitment",
  pathA: {
    label: "Investor (Equity SIP)",
    endValue: "₹38 Lakh",
    rate: "12% CAGR",
    direction: "up",
    tone: "positive",
  },
  pathB: {
    label: "Spender (Car EMI)",
    endValue: "₹6 Lakh Resale",
    rate: "15% Depreciation",
    direction: "down",
    tone: "negative",
  },
  divergenceGap: "₹32 Lakh Wealth Gap",
  variant: "wealth_gap",
};

// 2. Positive vs Positive Comparison (Index Fund vs Regular Fund)
const case2_pos_pos = {
  headerLabel: "DIRECT VS REGULAR FUND DIVERGENCE",
  timeHorizon: "15 Years",
  baselineLabel: "₹20,000 Monthly SIP",
  pathA: {
    label: "Direct Low-Cost Index",
    endValue: "₹52 Lakh",
    rate: "13.5% CAGR",
    direction: "up",
    tone: "positive",
  },
  pathB: {
    label: "High-Expense Active Fund",
    endValue: "₹36 Lakh",
    rate: "10.8% CAGR",
    direction: "up",
    tone: "positive",
  },
  divergenceGap: "₹16 Lakh Fee Drag Gap",
  variant: "cost_opportunity",
};

// 3. Qualitative Endpoints (Accelerated Wealth vs Survival Limits)
const case3_qualitative = {
  headerLabel: "CAREER LEVERAGE DIVERGENCE",
  timeHorizon: "20 Years",
  baselineLabel: "Identical 40 Hr Workweek",
  pathA: {
    label: "Equity Ownership Path",
    endValue: "Accelerated Wealth",
    direction: "up",
    tone: "positive",
  },
  pathB: {
    label: "Fixed Hourly Wage Path",
    endValue: "Survival Limits",
    direction: "down",
    tone: "negative",
  },
  divergenceGap: "Structural Divide",
  variant: "standard",
};

// 4. Negative vs Negative Comparison (Moderate vs Severe Erosion)
const case4_neg_neg = {
  headerLabel: "PURCHASING POWER EROSION",
  timeHorizon: "15 Years",
  baselineLabel: "₹1 Crore Uninvested Cash",
  pathA: {
    label: "Moderate Inflation (6%)",
    endValue: "-42% Real Value",
    rate: "6% Annual Drag",
    direction: "down",
    tone: "negative",
  },
  pathB: {
    label: "Stagflation Shock (12%)",
    endValue: "-82% Real Value",
    rate: "12% Hyper Drag",
    direction: "down",
    tone: "negative",
  },
  divergenceGap: "40% Additional Loss",
  variant: "standard",
};

// 5. Missing Optional Props (No baseline, no timeHorizon, no rates, no gap)
const case5_minimal = {
  headerLabel: "OUTCOME SEPARATION",
  pathA: {
    label: "Disciplined Strategy",
    endValue: "High Capital",
    direction: "up",
    tone: "positive",
  },
  pathB: {
    label: "Unhedged Exposure",
    endValue: "Depleted Capital",
    direction: "down",
    tone: "negative",
  },
};

// 6. Long Labels & Large Values
const case6_long_labels = {
  headerLabel: "GENERATIONAL CAPITAL COMPOUNDING",
  timeHorizon: "25 Years",
  baselineLabel: "₹50,000 Monthly Systematic Investment",
  pathA: {
    label: "Aggressive Multi-Asset Portfolio",
    endValue: "₹2,45,00,000",
    rate: "14.2% Annualized",
    direction: "up",
    tone: "positive",
  },
  pathB: {
    label: "Conservative Fixed Deposit Ladder",
    endValue: "₹98,50,000",
    rate: "6.5% Pre-Tax",
    direction: "neutral",
    tone: "neutral",
  },
  divergenceGap: "₹1.465 Crore Wealth Gap",
  variant: "wealth_gap",
};

async function renderCaseStill(name, data, frame = 60, duration_frames = 180) {
  const inputProps = { props: data, duration_frames };
  const compositions = await getCompositions(serveUrl, { inputProps });
  const composition = compositions.find((candidate) => candidate.id === "TrajectoryDivergence");
  const outputPath = path.join(outputDir, `${name}.png`);
  console.log(`Rendering ${name} at frame ${frame}...`);
  await renderStill({
    composition,
    serveUrl,
    output: outputPath,
    inputProps,
    frame,
    imageFormat: "png",
    logLevel: "warn",
  });
  console.log(`✓ Saved ${outputPath}`);
}

// 1. Render Variant Stills
console.log("--- RENDERING VARIANT STILLS ---");
await renderCaseStill("case1_pos_neg_f60", case1_pos_neg, 60);
await renderCaseStill("case2_pos_pos_f60", case2_pos_pos, 60);
await renderCaseStill("case3_qualitative_f60", case3_qualitative, 60);
await renderCaseStill("case4_neg_neg_f60", case4_neg_neg, 60);
await renderCaseStill("case5_minimal_f60", case5_minimal, 60);
await renderCaseStill("case6_long_labels_f60", case6_long_labels, 60);

// 2. Render Progression Frames for Case 1
console.log("--- RENDERING CHOREOGRAPHY PROGRESSION FRAMES ---");
const progressionFrames = [1, 10, 20, 35, 60, 90];
for (const f of progressionFrames) {
  await renderCaseStill(`progression_case1_f${f}`, case1_pos_neg, f);
}

// 3. Render 3-second MP4 Video Clip
console.log("--- RENDERING SHORT MP4 VIDEO CLIP (90 frames / 3 sec) ---");
const inputPropsVideo = { props: case1_pos_neg, duration_frames: 90 };
const compositions = await getCompositions(serveUrl, { inputProps: inputPropsVideo });
const compositionVideo = compositions.find((c) => c.id === "TrajectoryDivergence");
const videoOutputPath = path.join(outputDir, "trajectory_divergence_gap_3s.mp4");

await renderMedia({
  composition: { ...compositionVideo, durationInFrames: 90 },
  serveUrl,
  codec: "h264",
  outputLocation: videoOutputPath,
  inputProps: inputPropsVideo,
  logLevel: "warn",
});
console.log(`✓ Saved video: ${videoOutputPath}`);
console.log("ALL RENDERS COMPLETED SUCCESSFULLY!");
