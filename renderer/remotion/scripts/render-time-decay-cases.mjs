import { bundle } from "@remotion/bundler";
import { getCompositions, renderStill } from "@remotion/renderer";
import { mkdir } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const rendererRoot = path.resolve(scriptDir, "..");
const outputDir = path.resolve(rendererRoot, "test-outputs/time_decay");
await mkdir(outputDir, { recursive: true });

console.log("Bundling Remotion project...");
const entryPoint = path.join(rendererRoot, "src/index.ts");
const serveUrl = await bundle({
  entryPoint,
  onProgress: () => undefined,
});

const testCases = [
  {
    name: "01_mild_decline",
    frame: 75,
    props: {
      scene_id: "decay_case_a_mild",
      composition: "TimeDecay",
      fps: 30,
      duration_frames: 180,
      props: {
        fixedAmount: "₹1,00,000",
        amountLabel: "Fixed-Yield Debt Corpus",
        timePeriod: "5 Years",
        severity: "mild",
        variant: "mild_decay",
        endValue: "₹82,000",
        endLabel: "Residual Purchasing Power",
        dropRate: "18%",
        rateLabel: "3.8% Annual Inflation Drag",
        annotation: "Short-term horizon limits total inflation drag to mild real-value erosion",
      },
    },
  },
  {
    name: "02_severe_catastrophic_decline",
    frame: 75,
    props: {
      scene_id: "decay_case_b_severe",
      composition: "TimeDecay",
      fps: 30,
      duration_frames: 180,
      props: {
        fixedAmount: "₹50,000",
        amountLabel: "Monthly Fixed Pension",
        timePeriod: "25 Years",
        severity: "severe",
        variant: "severe_decay",
        endValue: "₹13,000",
        endLabel: "Real Purchasing Power",
        dropRate: "74%",
        rateLabel: "7.0% Compounding Annual Inflation",
        annotation: "Unhedged fixed income loses 74% of real living purchasing power over 25 years",
      },
    },
  },
  {
    name: "03_long_horizon_30yr",
    frame: 75,
    props: {
      scene_id: "decay_case_c_horizon",
      composition: "TimeDecay",
      fps: 30,
      duration_frames: 180,
      props: {
        fixedAmount: "₹1 Crore",
        amountLabel: "Idle Bank Deposit Balance",
        timePeriod: "30 Years",
        severity: "severe",
        variant: "severe_decay",
        endValue: "₹35 lakh",
        endLabel: "Real Terminal Value",
        dropRate: "65%",
        rateLabel: "6.5% Long-Term Inflation Baseline",
        annotation: "Holding cash long-term guarantees 65% loss of purchasing power over three decades",
      },
    },
  },
  {
    name: "04_short_duration_34frames",
    frame: 28,
    props: {
      scene_id: "decay_case_d_short_duration",
      composition: "TimeDecay",
      fps: 30,
      duration_frames: 34,
      props: {
        fixedAmount: "₹20,000",
        amountLabel: "Monthly Cash Buffer",
        timePeriod: "10 Years",
        severity: "moderate",
        variant: "standard",
        endValue: "₹12,000",
        endLabel: "Real Purchasing Power",
        dropRate: "40%",
        rateLabel: "6.0% Inflation Rate",
        annotation: "Purchasing power erosion verified on 34-frame fast-paced scene",
      },
    },
  },
];

for (const tc of testCases) {
  const compositions = await getCompositions(serveUrl, { inputProps: tc.props });
  const composition = compositions.find((candidate) => candidate.id === "TimeDecay");
  if (!composition) {
    throw new Error("TimeDecay composition not found in Root.tsx");
  }

  const outputPath = path.join(outputDir, `${tc.name}.png`);
  console.log(`Rendering ${tc.name} at frame ${tc.frame} (duration ${tc.props.duration_frames})...`);
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

console.log("All 4 TimeDecay visual cases successfully rendered!");
