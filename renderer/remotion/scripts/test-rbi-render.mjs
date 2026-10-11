import { bundle } from "@remotion/bundler";
import { getCompositions, renderMedia } from "@remotion/renderer";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const rendererRoot = path.resolve(scriptDir, "..");
const entryPoint = path.join(rendererRoot, "src/index.ts");

console.log("Reading test world JSON...");
const world = JSON.parse(fs.readFileSync("/tmp/test_rbi_world.json", "utf8"));
console.log(`World loaded: ${world.world_id}, duration: ${world.total_duration_frames} frames`);

console.log("Bundling Remotion project...");
const t0 = Date.now();
const serveUrl = await bundle({
  entryPoint,
  onProgress: (p) => {
    if (p % 25 === 0) console.log(`Bundle progress: ${p}%`);
  },
});
console.log(`Bundled in ${((Date.now() - t0) / 1000).toFixed(1)}s!`);

const compositions = await getCompositions(serveUrl, {
  inputProps: { world },
});
const comp = compositions.find((c) => c.id === "WorldComposition");
if (!comp) throw new Error("WorldComposition not found");

comp.durationInFrames = 90; // Render only first 90 frames (3 seconds) for test
comp.fps = world.canvas_config.fps;
comp.width = world.canvas_config.width;
comp.height = world.canvas_config.height;

console.log("Starting renderMedia for 90 frames with concurrency 2...");
const tStart = Date.now();
await renderMedia({
  composition: comp,
  serveUrl,
  codec: "h264",
  outputLocation: "/tmp/test_rbi_90frames.mp4",
  inputProps: { world },
  concurrency: 2,
  overwrite: true,
  logLevel: "warn",
  onProgress: ({ renderedFrames, encodedFrames }) => {
    console.log(`Render progress: ${renderedFrames}/90 frames rendered, ${encodedFrames} encoded`);
  },
});

console.log(`Finished in ${((Date.now() - tStart) / 1000).toFixed(1)}s! File exists: ${fs.existsSync("/tmp/test_rbi_90frames.mp4")}`);
