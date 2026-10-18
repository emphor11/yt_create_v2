import { bundle } from "@remotion/bundler";
import { getCompositions, renderMedia } from "@remotion/renderer";
import { mkdir } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { loanStoryPlan } from "../src/story_engine/loanStoryPlan.ts";
import { inflationStoryPlan } from "../src/story_engine/inflationStoryPlan.ts";
import { salarySplitStoryPlan } from "../src/story_engine/salarySplitStoryPlan.ts";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const rendererRoot = path.resolve(scriptDir, "..");
const entryPoint = path.join(rendererRoot, "src/index.ts");
const outDir = path.resolve(rendererRoot, "../../output");

console.log("Bundling Remotion entry point:", entryPoint);
const serveUrl = await bundle({
  entryPoint,
  onProgress: () => undefined,
});

const compositions = await getCompositions(serveUrl);
const comp1 = compositions.find((c) => c.id === "StoryScene");
const comp2 = compositions.find((c) => c.id === "InflationStoryScene");
const comp3 = compositions.find((c) => c.id === "SalarySplitStoryScene");

await mkdir(outDir, { recursive: true });

// Render Story 1
const path1 = path.join(outDir, "loan_story_continuous.mp4");
console.log(`\nRendering Story 1 MP4 with real audio narration to ${path1}...`);
await renderMedia({
  composition: comp1,
  serveUrl,
  codec: "h264",
  outputLocation: path1,
  inputProps: { plan: loanStoryPlan },
  logLevel: "warn",
});
console.log(`✓ Rendered Story 1: ${path1}`);

// Render Story 2
const path2 = path.join(outDir, "inflation_story_continuous.mp4");
console.log(`\nRendering Story 2 MP4 with real audio narration to ${path2}...`);
await renderMedia({
  composition: comp2,
  serveUrl,
  codec: "h264",
  outputLocation: path2,
  inputProps: { plan: inflationStoryPlan },
  logLevel: "warn",
});
console.log(`✓ Rendered Story 2: ${path2}`);

// Render Story 3
const path3 = path.join(outDir, "salary_split_story_continuous.mp4");
console.log(`\nRendering Story 3 MP4 with real audio narration to ${path3}...`);
await renderMedia({
  composition: comp3,
  serveUrl,
  codec: "h264",
  outputLocation: path3,
  inputProps: { plan: salarySplitStoryPlan },
  logLevel: "warn",
});
console.log(`✓ Rendered Story 3: ${path3}`);
