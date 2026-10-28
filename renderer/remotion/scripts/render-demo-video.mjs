import { bundle } from "@remotion/bundler";
import { getCompositions, renderMedia } from "@remotion/renderer";
import { copyFile, mkdir } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { loanStoryPlan } from "../src/story_engine/loanStoryPlan.ts";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const rendererRoot = path.resolve(scriptDir, "..");
const repoRoot = path.resolve(rendererRoot, "../..");
const entryPoint = path.join(rendererRoot, "src/index.ts");
const outputVideoPath = path.join(repoRoot, "output/the_rate_trap_living_canvas.mp4");
const artifactVideoPath = "/Users/dakshyadav/.gemini/antigravity/brain/0ea3762c-60ae-40de-96c0-ce19c83dda9d/the_rate_trap_living_canvas.mp4";

await mkdir(path.dirname(outputVideoPath), { recursive: true });

console.log("==================================================");
console.log("RENDERING REAL VIDEO: Living Canvas 3.0 (Atmosphere + Stamp)");
console.log("==================================================");
console.log(`Plan ID: ${loanStoryPlan.id}`);
console.log(`Duration: ${loanStoryPlan.durationInFrames} frames (~${(loanStoryPlan.durationInFrames / 30).toFixed(1)}s)`);
console.log(`Atmosphere Preset: ${loanStoryPlan.atmosphere?.preset}`);
console.log(`Narration Track: ${loanStoryPlan.audioFileName}`);

console.log("\n[1/3] Bundling Remotion codebase...");
const serveUrl = await bundle({
  entryPoint,
  onProgress: () => undefined,
});

console.log("[2/3] Resolving StoryScene composition...");
const compositions = await getCompositions(serveUrl, {
  inputProps: { plan: loanStoryPlan },
});
const comp = compositions.find((c) => c.id === "StoryScene");
if (!comp) {
  throw new Error("StoryScene composition not found!");
}

console.log(`[3/3] Rendering full 1080p video with audio, springs & camera shake...`);
const startTime = Date.now();

await renderMedia({
  composition: comp,
  serveUrl,
  codec: "h264",
  outputLocation: outputVideoPath,
  inputProps: { plan: loanStoryPlan },
  logLevel: "warn",
  concurrency: 4,
  onProgress: ({ progress, renderedFrames }) => {
    const pct = (progress * 100).toFixed(1);
    process.stdout.write(`\r[Rendering Video] ${pct}% (${renderedFrames}/${loanStoryPlan.durationInFrames} frames)`);
  },
});

console.log("\n");
const durationSec = ((Date.now() - startTime) / 1000).toFixed(1);
console.log(`✓ Video successfully rendered in ${durationSec}s!`);
console.log(`✓ Output file: ${outputVideoPath}`);

console.log("\nCopying video to Antigravity artifact directory for immediate playback...");
await copyFile(outputVideoPath, artifactVideoPath);
console.log(`✓ Playback ready at: ${artifactVideoPath}`);
