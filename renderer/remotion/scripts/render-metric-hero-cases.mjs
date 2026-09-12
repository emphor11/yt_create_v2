import { bundle } from "@remotion/bundler";
import { getCompositions, renderStill } from "@remotion/renderer";
import { mkdir } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const rendererRoot = path.resolve(scriptDir, "..");
const outputDir = path.resolve(rendererRoot, "test-outputs/metric_hero");
await mkdir(outputDir, { recursive: true });

console.log("Bundling Remotion project...");
const entryPoint = path.join(rendererRoot, "src/index.ts");
const serveUrl = await bundle({
  entryPoint,
  onProgress: () => undefined,
});

const testCases = [
  {
    name: "01_hero_milestone",
    frame: 75,
    props: {
      scene_id: "hero_case",
      composition: "MetricHero",
      fps: 30,
      duration_frames: 180,
      props: {
        value: "₹50 lakh",
        label: "Starting Retirement Portfolio",
        context: "BASELINE 2024",
        variant: "hero_milestone",
        polarity: "positive",
        direction: "up",
      },
    },
  },
  {
    name: "02_supporting_metric",
    frame: 75,
    props: {
      scene_id: "supporting_case",
      composition: "MetricHero",
      fps: 30,
      duration_frames: 180,
      props: {
        value: "6.8%",
        label: "Average Annual Inflation Rate in Tier-1 Cities",
        context: "HISTORICAL BENCHMARK",
        variant: "supporting_metric",
      },
    },
  },
  {
    name: "03_warning_metric",
    frame: 75,
    props: {
      scene_id: "warning_case",
      composition: "MetricHero",
      fps: 30,
      duration_frames: 180,
      props: {
        value: "₹26 lakh",
        label: "Projected Shortfall from Unhedged Inflation Drag",
        context: "CRITICAL VULNERABILITY",
        variant: "warning_metric",
        polarity: "negative",
        direction: "down",
      },
    },
  },
  {
    name: "04_before_after_metric",
    frame: 75,
    props: {
      scene_id: "before_after_case",
      composition: "MetricHero",
      fps: 30,
      duration_frames: 180,
      props: {
        baselineValue: "₹50,000",
        baselineLabel: "Starting Monthly Salary",
        value: "₹1.2 Cr",
        label: "Total Lifetime Purchasing Power Gap Over 15 Years",
        context: "AFTER 15 YEARS",
        delta: "+24x Spread",
        variant: "before_after_metric",
      },
    },
  },
];

for (const tc of testCases) {
  const compositions = await getCompositions(serveUrl, { inputProps: tc.props });
  const composition = compositions.find((candidate) => candidate.id === "MetricHero");
  if (!composition) {
    throw new Error("MetricHero composition not found in Root.tsx");
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

console.log("All 4 MetricHero visual cases successfully rendered!");
