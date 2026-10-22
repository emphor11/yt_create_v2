import { bundle } from "@remotion/bundler";
import { getCompositions, renderMedia, renderStill } from "@remotion/renderer";
import { mkdir } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { splitScreenStoryPlan } from "../src/story_engine/splitScreenStoryPlan.ts";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const rendererRoot = path.resolve(scriptDir, "..");
const entryPoint = path.join(rendererRoot, "src/index.ts");
const outDir = path.resolve(rendererRoot, "../../output");

console.log("Bundling Remotion entry point for SplitScreen visual test...");
const serveUrl = await bundle({
  entryPoint,
  onProgress: () => undefined,
});

const compositions = await getCompositions(serveUrl);
const comp = compositions.find((c) => c.id === "SplitScreenStoryScene");
if (!comp) {
  throw new Error("Could not find SplitScreenStoryScene composition");
}

await mkdir(outDir, { recursive: true });

const outVideo = path.join(outDir, "split_screen_story.mp4");
console.log(`\nRendering Split-Screen visual test MP4 to ${outVideo}...`);
await renderMedia({
  composition: comp,
  serveUrl,
  codec: "h264",
  outputLocation: outVideo,
  inputProps: { plan: splitScreenStoryPlan },
  logLevel: "warn",
});
console.log(`✓ Rendered Split-Screen video: ${outVideo}`);

// Render Keyframe Stills
const still1 = path.join(outDir, "split_screen_frame_50.png");
console.log(`Rendering frame 50 still (bank image in split_left) to ${still1}...`);
await renderStill({
  composition: comp,
  serveUrl,
  output: still1,
  frame: 50,
  inputProps: { plan: splitScreenStoryPlan },
});
console.log(`✓ Rendered frame 50: ${still1}`);

const still2 = path.join(outDir, "split_screen_frame_250.png");
console.log(`Rendering frame 250 still (bank image + interest card + debug divider) to ${still2}...`);
await renderStill({
  composition: comp,
  serveUrl,
  output: still2,
  frame: 250,
  inputProps: { plan: splitScreenStoryPlan },
});
console.log(`✓ Rendered frame 250: ${still2}`);

console.log("\n==================================================");
console.log("SPLIT-SCREEN VISUAL TEST RENDER COMPLETE!");
console.log("==================================================");
