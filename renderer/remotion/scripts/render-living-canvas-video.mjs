import { bundle } from "@remotion/bundler";
import { getCompositions, renderMedia } from "@remotion/renderer";
import { readFile, copyFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const rendererRoot = path.resolve(scriptDir, "..");
const repoRoot = path.resolve(rendererRoot, "../..");
const entryPoint = path.join(rendererRoot, "src/index.ts");
const planPath = path.join(repoRoot, "output/mutual_fund_plan.json");
const outputVideoPath = path.join(repoRoot, "the_mutual_fund_living_canvas.mp4");
const artifactVideoPath = "/Users/dakshyadav/.gemini/antigravity/brain/0ea3762c-60ae-40de-96c0-ce19c83dda9d/the_mutual_fund_living_canvas.mp4";

console.log("Loading plan from:", planPath);
const planRaw = await readFile(planPath, "utf-8");
const plan = JSON.parse(planRaw);
plan.autoLayout = true;

console.log(`Plan loaded: ${plan.id}, Duration: ${plan.durationInFrames} frames (${(plan.durationInFrames / 30).toFixed(1)}s)`);

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

console.log("Starting full video render to:", outputVideoPath);
const startTime = Date.now();
await renderMedia({
  composition: comp,
  serveUrl,
  codec: "h264",
  outputLocation: outputVideoPath,
  inputProps: { plan },
  logLevel: "warn",
  concurrency: 4,
  onProgress: ({ progress, renderedFrames }) => {
    const pct = (progress * 100).toFixed(1);
    process.stdout.write(`\r[Rendering Living Canvas Video] ${pct}% (${renderedFrames}/${plan.durationInFrames} frames)`);
  },
});

console.log("\n");
const durationSec = ((Date.now() - startTime) / 1000).toFixed(1);
console.log(`✓ Full video rendered in ${durationSec}s!`);

console.log("Copying to artifact directory for user playback...");
await copyFile(outputVideoPath, artifactVideoPath);
console.log("✓ Copied to:", artifactVideoPath);
