import { bundle } from "@remotion/bundler";
import { getCompositions, renderStill } from "@remotion/renderer";
import { mkdir } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const rendererRoot = path.resolve(scriptDir, "..");
const outputDir = "/Users/dakshyadav/.gemini/antigravity/brain/6d419c6d-aa14-47ab-a0a4-e305e6158af7/scratch/calculation_story_test";
await mkdir(outputDir, { recursive: true });

console.log("Bundling Remotion project...");
const entryPoint = path.join(rendererRoot, "src/index.ts");
const serveUrl = await bundle({
  entryPoint,
  onProgress: () => undefined,
});

const testCases = [
  // User Case 1: ₹1,00,000 × 50% = ₹50,000
  {
    name: "user_case1_percentage",
    frame: 140,
    props: {
      scene_id: "user_case1",
      composition: "CalculationStory",
      fps: 30,
      duration_frames: 180,
      props: {
        operationType: "multiplication",
        variant: "multiplication",
        inputValue: "₹1,00,000",
        inputLabel: "Monthly Gross Revenue",
        operationLabel: "×",
        rateLabel: "50% Target Savings Rate",
        resultValue: "₹50,000",
        resultLabel: "Investable Cash Flow",
        note: "50/30/20 ALLOCATION PRINCIPLE",
        polarity: "positive",
      },
    },
  },
  // User Case 2: ₹75,000 − ₹35,000 = ₹40,000
  {
    name: "user_case2_subtraction",
    frame: 140,
    props: {
      scene_id: "user_case2",
      composition: "CalculationStory",
      fps: 30,
      duration_frames: 180,
      props: {
        operationType: "subtraction",
        variant: "subtraction",
        inputValue: "₹75,000",
        inputLabel: "Fixed Monthly Inflow",
        secondaryValue: "₹35,000",
        secondaryLabel: "Household Operating Costs",
        operationLabel: "−",
        rateLabel: "Essential Overhead Drag",
        resultValue: "₹40,000",
        resultLabel: "Net Discretionary Margin",
        note: "RETAINED LIQUIDITY RESIDUAL",
        polarity: "negative",
      },
    },
  },
  // User Case 3: ₹10,000 × 12% = ₹1,200
  {
    name: "user_case3_yield",
    frame: 140,
    props: {
      scene_id: "user_case3",
      composition: "CalculationStory",
      fps: 30,
      duration_frames: 180,
      props: {
        operationType: "multiplication",
        variant: "multiplication",
        inputValue: "₹10,000",
        inputLabel: "Monthly Capital Commitment",
        operationLabel: "×",
        rateLabel: "12% Expected Annual Alpha",
        resultValue: "₹1,200",
        resultLabel: "First-Year Monthly Return",
        note: "PASSIVE COMPOUNDING ACCELERATOR",
        polarity: "positive",
      },
    },
  },
  // Variant Case 4: ₹50 lakh × 4% Safe Withdrawal = ₹2 lakh
  {
    name: "variant_case4_swr",
    frame: 140,
    props: {
      scene_id: "variant_case4",
      composition: "CalculationStory",
      fps: 30,
      duration_frames: 180,
      props: {
        operationType: "multiplication",
        variant: "multiplication",
        inputValue: "₹50 lakh",
        inputLabel: "Retirement Portfolio Corpus",
        operationLabel: "×",
        rateLabel: "4% Safe Withdrawal Rate",
        resultValue: "₹2 lakh",
        resultLabel: "Annual Passive Cash Flow",
        note: "TRINITY STUDY CONSERVATIVE FLOOR",
        polarity: "positive",
      },
    },
  },
  // Variant Case 5: ₹10 lakh → 12% CAGR (20 Years) = ₹1 Crore
  {
    name: "variant_case5_growth",
    frame: 140,
    props: {
      scene_id: "variant_case5",
      composition: "CalculationStory",
      fps: 30,
      duration_frames: 180,
      props: {
        operationType: "growth",
        variant: "growth",
        inputValue: "₹10 lakh",
        inputLabel: "Starting Principal Base",
        operationLabel: "→",
        rateLabel: "12% Compounding CAGR",
        timeframe: "20 Years",
        resultValue: "₹1 Crore",
        resultLabel: "Terminal Accumulated Wealth",
        note: "EXPONENTIAL TIME COMPOUNDING",
        polarity: "positive",
      },
    },
  },
  // Variant Case 6: ₹1,00,000 + ₹10,000 = ₹1,10,000 (Addition)
  {
    name: "variant_case6_addition",
    frame: 140,
    props: {
      scene_id: "variant_case6",
      composition: "CalculationStory",
      fps: 30,
      duration_frames: 180,
      props: {
        operationType: "addition",
        variant: "addition",
        inputValue: "₹1,00,000",
        inputLabel: "Fixed Base Pay",
        secondaryValue: "₹10,000",
        secondaryLabel: "Performance Incentive",
        operationLabel: "+",
        resultValue: "₹1,10,000",
        resultLabel: "Total Compensation",
        note: "CONVERGING INCOME STREAMS",
        polarity: "positive",
      },
    },
  },
];

console.log("Rendering calculation cases...");
for (const tc of testCases) {
  const compositions = await getCompositions(serveUrl, { inputProps: tc.props });
  const comp = compositions.find((c) => c.id === "CalculationStory");
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

// Kinetic progression frames for user_case1 (frames 1, 15, 35, 60, 90, 150)
const progressionFrames = [1, 15, 35, 60, 90, 150];
console.log("\nRendering choreography progression for user_case1...");
for (const f of progressionFrames) {
  const compositions = await getCompositions(serveUrl, { inputProps: testCases[0].props });
  const comp = compositions.find((c) => c.id === "CalculationStory");
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

console.log("\nAll CalculationStory renders complete!");
