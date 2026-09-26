import { bundle } from "@remotion/bundler";
import { getCompositions, renderStill, renderMedia } from "@remotion/renderer";
import { mkdir } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const rendererRoot = path.resolve(scriptDir, "..");
const outputDir = "/Users/dakshyadav/.gemini/antigravity/brain/6d419c6d-aa14-47ab-a0a4-e305e6158af7/scratch/growth_trajectory_test";

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

// 1. ₹15 Lakh → ₹95 Lakh (compounding_snowball)
const case1_compounding = {
  headerLabel: "WEALTH COMPOUNDING ENGINE",
  startValue: "₹15 Lakh",
  startLabel: "Initial Principal Base",
  endValue: "₹95 Lakh",
  endLabel: "Terminal Freedom Corpus",
  timeHorizon: "25 Years",
  growthRate: "12% CAGR",
  growthType: "compound",
  milestoneValue: "Tipping Point (Yr 14)",
  milestoneLabel: "Returns exceed total annual savings",
  annotation: "After year 14, compound interest generated per year surpasses cumulative principal contributed.",
  variant: "compounding_snowball",
};

// 2. Qualitative labels: Flat Curve → Later Decades
const case2_qualitative = {
  headerLabel: "EXPONENTIAL HOCKEY STICK",
  startValue: "Flat Curve",
  startLabel: "Early Foundation",
  endValue: "Later Decades",
  endLabel: "Hyperbolic Payoff",
  timeHorizon: "Decades",
  growthType: "compound",
  milestoneValue: "Patience Inflection",
  milestoneLabel: "Invisible progress turns visible",
  annotation: "90% of total wealth accumulation happens in the final 20% of the holding period.",
  variant: "compounding_snowball",
};

// 3. Base Salary → Scaled Wealth Corpus (accelerating_growth)
const case3_accelerating = {
  headerLabel: "CAREER EQUITY TRAJECTORY",
  startValue: "Base Salary",
  startLabel: "Linear Labor",
  endValue: "Scaled Corpus",
  endLabel: "Leveraged Equity",
  timeHorizon: "15 Years",
  growthRate: "+24% p.a.",
  growthType: "accelerating",
  milestoneValue: "Equity Inflection",
  milestoneLabel: "Transition from wages to equity",
  annotation: "Shifting compensation from fixed salary to enterprise equity creates dramatic convex upside.",
  variant: "accelerating_growth",
};

// 4. Positive growth linear accumulation
const case4_linear = {
  headerLabel: "DISCIPLINED CAPITAL ACCUMULATION",
  startValue: "₹5,000 / mo",
  startLabel: "Monthly SIP",
  endValue: "₹38 Lakh",
  endLabel: "Accumulated Principal",
  timeHorizon: "10 Years",
  growthRate: "Steady Linear",
  growthType: "linear",
  variant: "linear_accumulation",
};

// 5. Declining trajectory (downside risk / erosion)
const case5_declining = {
  headerLabel: "PURCHASING POWER EROSION",
  startValue: "₹1.2 Crore",
  startLabel: "Uninvested Cash",
  endValue: "₹48 Lakh",
  endLabel: "Real Value",
  timeHorizon: "20 Years",
  growthRate: "-7.2% Inflation",
  annotation: "Persistent real inflation silently halves purchasing power over two decades of idle holding.",
  variant: "declining_trajectory",
};

// 6. Long value string (₹1.5 Crore)
const case6_long_val = {
  headerLabel: "SUPER-COMPOUNDING PORTFOLIO",
  startValue: "₹25,00,000",
  startLabel: "Seed Capital",
  endValue: "₹1,50,00,000",
  endLabel: "Generational Wealth Target",
  timeHorizon: "30 Years",
  growthRate: "14.5% CAGR",
  growthType: "compound",
  milestoneValue: "Milestone: ₹50 Lakh",
  milestoneLabel: "First crore comes 4x faster",
  annotation: "The first 50 lakh takes 12 years; the next crore takes less than 8 years.",
  variant: "compounding_snowball",
};

// 7. Minimal missing optional values
const case7_minimal = {
  startValue: "₹10,000",
  endValue: "₹1,00,000",
};

async function renderCaseStill(name, data, frame = 60, duration_frames = 180) {
  const inputProps = { props: data, duration_frames };
  const compositions = await getCompositions(serveUrl, { inputProps });
  const composition = compositions.find((candidate) => candidate.id === "GrowthTrajectory");
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
await renderCaseStill("case1_compounding_f60", case1_compounding, 60);
await renderCaseStill("case2_qualitative_f60", case2_qualitative, 60);
await renderCaseStill("case3_accelerating_f60", case3_accelerating, 60);
await renderCaseStill("case4_linear_f60", case4_linear, 60);
await renderCaseStill("case5_declining_f60", case5_declining, 60);
await renderCaseStill("case6_long_val_f60", case6_long_val, 60);
await renderCaseStill("case7_minimal_f60", case7_minimal, 60);

// 2. Render Progression Frames for Case 1
console.log("--- RENDERING CHOREOGRAPHY PROGRESSION FRAMES ---");
const progressionFrames = [1, 10, 20, 35, 60, 90];
for (const f of progressionFrames) {
  await renderCaseStill(`progression_case1_f${f}`, case1_compounding, f);
}

// 3. Render 3-second MP4 Video Clip
console.log("--- RENDERING SHORT MP4 VIDEO CLIP (90 frames / 3 sec) ---");
const inputPropsVideo = { props: case1_compounding, duration_frames: 90 };
const compositions = await getCompositions(serveUrl, { inputProps: inputPropsVideo });
const compositionVideo = compositions.find((c) => c.id === "GrowthTrajectory");
const videoOutputPath = path.join(outputDir, "growth_trajectory_snowball_3s.mp4");

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
