import { bundle } from "@remotion/bundler";
import { getCompositions, renderMedia } from "@remotion/renderer";
import { mkdir, readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const rendererRoot = path.resolve(scriptDir, "..");
const requestPath = process.argv[2];

if (!requestPath) {
  throw new Error("Missing render request JSON path.");
}

const request = JSON.parse(await readFile(requestPath, "utf8"));
const world = request.world;
const outputPath = request.outputPath;

if (!world || !outputPath) {
  throw new Error("Render request requires world and outputPath.");
}

console.log("[render-world-spec] Step 1: Request loaded for world:", world.world_id, "frames:", world.total_duration_frames);

const entryPoint = path.join(rendererRoot, "src/index.ts");
console.log("[render-world-spec] Step 2: Bundling webpack entryPoint:", entryPoint);
const tBundle = Date.now();
const serveUrl = await bundle({
  entryPoint,
  onProgress: (p) => {
    if (p % 25 === 0) console.log(`[render-world-spec] Bundle progress: ${p}%`);
  },
});
console.log(`[render-world-spec] Step 2: Bundled successfully in ${((Date.now() - tBundle)/1000).toFixed(1)}s! serveUrl:`, serveUrl);

console.log("[render-world-spec] Step 3: Getting compositions from serveUrl...");
const compositions = await getCompositions(serveUrl, {
  inputProps: { world },
});
const composition = compositions.find((candidate) => candidate.id === "WorldComposition");

if (!composition) {
  throw new Error("Composition 'WorldComposition' not found in Root.tsx.");
}

composition.durationInFrames = world.total_duration_frames;
composition.fps = world.canvas_config.fps;
composition.width = world.canvas_config.width;
composition.height = world.canvas_config.height;

console.log(`[render-world-spec] Step 4: WorldComposition ready (${composition.width}x${composition.height}, ${composition.fps}fps, ${composition.durationInFrames} frames)`);
console.log("[render-world-spec] Step 5: Starting renderMedia with concurrency 2 to:", outputPath);

await mkdir(path.dirname(outputPath), { recursive: true });
await renderMedia({
  composition,
  serveUrl,
  codec: "h264",
  outputLocation: outputPath,
  inputProps: { world },
  overwrite: true,
  muted: false,
  concurrency: 2,
  logLevel: "warn",
  onProgress: ({ renderedFrames, encodedFrames }) => {
    if (renderedFrames % 150 === 0 || renderedFrames === world.total_duration_frames) {
      const pct = Math.round((renderedFrames / world.total_duration_frames) * 100);
      console.log(`[Remotion Progress] Rendered: ${renderedFrames}/${world.total_duration_frames} (${pct}%), Encoded: ${encodedFrames}`);
    }
  },
});

console.log("[render-world-spec] Step 6: renderMedia completed successfully!");

console.log(JSON.stringify({ outputPath, contentType: "video/mp4" }));
