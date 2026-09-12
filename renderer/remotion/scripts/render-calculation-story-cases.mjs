import { bundle } from "@remotion/bundler";
import { getCompositions, renderStill } from "@remotion/renderer";
import { mkdir } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const rendererRoot = path.resolve(scriptDir, "..");
const outputDir = path.resolve(rendererRoot, "test-outputs/calculation_story");
await mkdir(outputDir, { recursive: true });

console.log("Bundling Remotion project...");
const entryPoint = path.join(rendererRoot, "src/index.ts");
const serveUrl = await bundle({
  entryPoint,
  onProgress: () => undefined,
});

const testCases = [
  {
    name: "01_multiplication",
    frame: 75,
    props: {
      scene_id: "calc_case_a_multiplication",
      composition: "CalculationStory",
      fps: 30,
      duration_frames: 180,
      props: {
        operationType: "multiplication",
        variant: "multiplication",
        inputValue: "₹50 lakh",
        inputLabel: "Starting Portfolio Base",
        operationLabel: "×",
        rateLabel: "4% Safe Withdrawal Rate",
        resultValue: "₹2 lakh",
        resultLabel: "Annual Passive Cash Flow",
        note: "CONSERVATIVE RETIREMENT RULE OF THUMB",
        polarity: "positive",
      },
    },
  },
  {
    name: "02_addition",
    frame: 75,
    props: {
      scene_id: "calc_case_b_addition",
      composition: "CalculationStory",
      fps: 30,
      duration_frames: 180,
      props: {
        operationType: "addition",
        variant: "addition",
        inputValue: "₹1,00,000",
        inputLabel: "Fixed Base Salary",
        secondaryValue: "₹10,000",
        secondaryLabel: "Quarterly Performance Bonus",
        operationLabel: "+",
        rateLabel: "Additive Compensation Stream",
        resultValue: "₹1,10,000",
        resultLabel: "Total Monthly Take-Home",
        note: "CONVERGING COMPENSATION PILLARS",
        polarity: "positive",
      },
    },
  },
  {
    name: "03_subtraction",
    frame: 75,
    props: {
      scene_id: "calc_case_c_subtraction",
      composition: "CalculationStory",
      fps: 30,
      duration_frames: 180,
      props: {
        operationType: "subtraction",
        variant: "subtraction",
        inputValue: "₹1,00,000",
        inputLabel: "Gross Invoice Billing",
        secondaryValue: "₹20,000",
        secondaryLabel: "Withholding Tax & TDS Drag",
        operationLabel: "-",
        rateLabel: "20% Statutory Deduction",
        resultValue: "₹80,000",
        resultLabel: "Net Retained Capital",
        note: "CAPITAL FRICTION DEDUCTION",
        polarity: "negative",
      },
    },
  },
  {
    name: "04_allocation",
    frame: 75,
    props: {
      scene_id: "calc_case_d_allocation",
      composition: "CalculationStory",
      fps: 30,
      duration_frames: 180,
      props: {
        operationType: "allocation",
        variant: "allocation",
        inputValue: "₹10 lakh",
        inputLabel: "Total Investable Surplus",
        operationLabel: "allocation",
        rateLabel: "40% Target Allocation",
        resultValue: "₹4 lakh",
        resultLabel: "Fixed-Income Debt Buffer",
        note: "PORTFOLIO RISK REBALANCING CARVE-OUT",
        polarity: "neutral",
      },
    },
  },
  {
    name: "05_growth",
    frame: 75,
    props: {
      scene_id: "calc_case_e_growth",
      composition: "CalculationStory",
      fps: 30,
      duration_frames: 180,
      props: {
        operationType: "growth",
        variant: "growth",
        inputValue: "₹10 lakh",
        inputLabel: "Initial Principal Investment",
        operationLabel: "grows to",
        rateLabel: "12% Compounding CAGR",
        timeframe: "20 Years",
        resultValue: "₹1 Crore",
        resultLabel: "Terminal Accumulated Wealth",
        note: "EXPONENTIAL COMPOUNDING JOURNEY",
        polarity: "positive",
      },
    },
  },
  {
    name: "06_neutral",
    frame: 75,
    props: {
      scene_id: "calc_case_f_neutral",
      composition: "CalculationStory",
      fps: 30,
      duration_frames: 180,
      props: {
        operationType: "neutral",
        variant: "neutral",
        inputValue: "₹50,000",
        inputLabel: "Current Starting Balance",
        operationLabel: "",
        rateLabel: "",
        resultValue: "₹1 Crore",
        resultLabel: "Projected Benchmark Target",
        note: "NON-ARITHMETIC DIRECTIONAL PROGRESSION",
      },
    },
  },
];

for (const tc of testCases) {
  const compositions = await getCompositions(serveUrl, { inputProps: tc.props });
  const composition = compositions.find((candidate) => candidate.id === "CalculationStory");
  if (!composition) {
    throw new Error("CalculationStory composition not found in Root.tsx");
  }

  const outputPath = path.join(outputDir, `${tc.name}.png`);
  console.log(`Rendering ${tc.name} at frame ${tc.frame}...`);
  await renderStill({
    composition,
    serveUrl,
    output: outputPath,
    inputProps: tc.props,
    frame: tc.frame,
    imageFormat: "png",
    logLevel: "warn",
  });
  console.log(`✓ Saved ${outputPath}`);
}

console.log("All CalculationStory visual cases successfully rendered!");
