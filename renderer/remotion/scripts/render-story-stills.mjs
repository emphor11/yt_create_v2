import { bundle } from "@remotion/bundler";
import { getCompositions, renderStill } from "@remotion/renderer";
import { mkdir } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { loanStoryPlan } from "../src/story_engine/loanStoryPlan.ts";
import { inflationStoryPlan } from "../src/story_engine/inflationStoryPlan.ts";
import { salarySplitStoryPlan } from "../src/story_engine/salarySplitStoryPlan.ts";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const rendererRoot = path.resolve(scriptDir, "..");
const entryPoint = path.join(rendererRoot, "src/index.ts");
const outDir = path.join(rendererRoot, "test-outputs/story_engine");

console.log("Bundling Remotion entry point:", entryPoint);
const serveUrl = await bundle({
  entryPoint,
  onProgress: () => undefined,
});

const compositions = await getCompositions(serveUrl);
const compLoan = compositions.find((c) => c.id === "StoryScene");
const compInflation = compositions.find((c) => c.id === "InflationStoryScene");
const compSalary = compositions.find((c) => c.id === "SalarySplitStoryScene");

if (!compLoan || !compInflation || !compSalary) {
  throw new Error("Compositions not found in Root.tsx!");
}

await mkdir(outDir, { recursive: true });

// 1. Story 1: Loan Rate Hike & Visual State Transformations
console.log("\n--- RENDERING STORY 1: LOAN RATE HIKE & VISUAL STATES ---");
const story1Frames = [
  { frame: 140, name: "story1_neutral_emi_initial.png", label: "Initial Neutral EMI (No Misleading Burden)" },
  { frame: 285, name: "story1_climax_visual_states.png", label: "Warning Hike Badge, Danger Burden Surge, and Dimmed Loan" },
];

for (const kf of story1Frames) {
  const outputPath = path.join(outDir, kf.name);
  console.log(`Rendering frame ${kf.frame} (${kf.label}) -> ${kf.name}...`);
  await renderStill({
    composition: compLoan,
    serveUrl,
    output: outputPath,
    inputProps: { plan: loanStoryPlan },
    frame: kf.frame,
    imageFormat: "png",
    logLevel: "warn",
  });
  console.log(`  ✓ Rendered ${kf.name}`);
}

// 2. Story 2: Inflation Purchasing Power with Chart Primitive & Erosion States
console.log("\n--- RENDERING STORY 2: INFLATION TRAJECTORY CHART & EROSION ---");
const story2Frames = [
  { frame: 180, name: "story2_eroding_connector.png", label: "Inflation Eroding Real Value" },
  { frame: 280, name: "story2_chart_and_erosion_climax.png", label: "Trajectory Area Chart + Eroded Real Power Card + Dimmed Balance" },
];

for (const kf of story2Frames) {
  const outputPath = path.join(outDir, kf.name);
  console.log(`Rendering frame ${kf.frame} (${kf.label}) -> ${kf.name}...`);
  await renderStill({
    composition: compInflation,
    serveUrl,
    output: outputPath,
    inputProps: { plan: inflationStoryPlan },
    frame: kf.frame,
    imageFormat: "png",
    logLevel: "warn",
  });
  console.log(`  ✓ Rendered ${kf.name}`);
}

// 3. Story 3: Salary Split Document with True Split & Official Rubber Stamp
console.log("\n--- RENDERING STORY 3: TRUE SPLIT & RUBBER STAMP ---");
const story3Frames = [
  { frame: 60, name: "story3_01_sanction_stamped.png", label: "Official Document with Green SANCTIONED Rubber Stamp" },
  { frame: 105, name: "story3_02_true_split_in_flight.png", label: "True Physical Emergence of Daughter Cards from Document Center" },
  { frame: 340, name: "story3_03_full_split_climax.png", label: "Complete 3-Way Split with Danger Surcharge, Warning Living, and Success Net Corpus" },
];

for (const kf of story3Frames) {
  const outputPath = path.join(outDir, kf.name);
  console.log(`Rendering frame ${kf.frame} (${kf.label}) -> ${kf.name}...`);
  await renderStill({
    composition: compSalary,
    serveUrl,
    output: outputPath,
    inputProps: { plan: salarySplitStoryPlan },
    frame: kf.frame,
    imageFormat: "png",
    logLevel: "warn",
  });
  console.log(`  ✓ Rendered ${kf.name}`);
}

console.log("\nAll stills rendered successfully into:", outDir);
