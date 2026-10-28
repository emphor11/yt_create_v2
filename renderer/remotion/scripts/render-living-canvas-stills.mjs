import { bundle } from "@remotion/bundler";
import { getCompositions, renderStill } from "@remotion/renderer";
import { readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const rendererRoot = path.resolve(scriptDir, "..");
const repoRoot = path.resolve(rendererRoot, "../..");
const entryPoint = path.join(rendererRoot, "src/index.ts");
const planPath = path.join(repoRoot, "output/mutual_fund_plan.json");
const outDir = path.resolve("/Users/dakshyadav/.gemini/antigravity/brain/0ea3762c-60ae-40de-96c0-ce19c83dda9d");

console.log("Reading continuous_story_plan from JSON file:", planPath);
const planRaw = await readFile(planPath, "utf-8");
const plan = JSON.parse(planRaw);
plan.autoLayout = true; // Ensure Living Canvas dynamic auto-layout is active!

console.log(`Plan loaded: ${plan.id}, Duration: ${plan.durationInFrames} frames`);

console.log("Bundling Remotion...");
const serveUrl = await bundle({
  entryPoint,
  onProgress: () => undefined,
});

const compositions = await getCompositions(serveUrl, { inputProps: { plan } });
const comp = compositions.find((c) => c.id === "StoryScene");
if (!comp) {
  throw new Error("StoryScene composition not found!");
}

const frames = [
  { frame: 180, name: "living_canvas_006s_hero.png", label: "006s: Solitary Hero Title Scale" },
  { frame: 900, name: "living_canvas_030s_plate_and_card.png", label: "030s: Inward Dual Split Photo & Card" },
  { frame: 2760, name: "living_canvas_092s_regulatory.png", label: "092s: SEBI Regulatory Documentary Framing" },
  { frame: 3450, name: "living_canvas_115s_climax_number.png", label: "115s: ₹45 Lakhs Dominant Focal Hero" },
  { frame: 3750, name: "living_canvas_125s_chart_compression.png", label: "125s: 3-Column + Chart Vertical Floor Compression" },
  { frame: 4260, name: "living_canvas_142s_split_comparison.png", label: "142s: Dual Inward Balanced Split" },
];

for (const { frame, name, label } of frames) {
  const outputPath = path.join(outDir, name);
  console.log(`Rendering ${label} at frame ${frame} -> ${name}...`);
  await renderStill({
    composition: comp,
    serveUrl,
    output: outputPath,
    frame,
    inputProps: { plan },
    logLevel: "warn",
  });
  console.log(`✓ Saved ${name}`);
}

console.log("\nAll living canvas keyframes rendered successfully!");
