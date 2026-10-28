import { bundle } from "@remotion/bundler";
import { getCompositions, renderStill } from "@remotion/renderer";
import { mkdir, readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const rendererRoot = path.resolve(scriptDir, "..");

const planPath = process.argv[2];
const framesArg = process.argv[3]; // comma-separated frame numbers or label:frame
const outputDir = process.argv[4];

if (!planPath || !framesArg || !outputDir) {
  console.error("Usage: node render-frames-batch.mjs <plan.json> <frame1,frame2,...> <outputDir>");
  process.exit(1);
}

const plan = JSON.parse(await readFile(planPath, "utf8"));
await mkdir(outputDir, { recursive: true });

const entryPoint = path.join(rendererRoot, "src/index.ts");
console.log("Bundling Remotion project...");
const serveUrl = await bundle({
  entryPoint,
  onProgress: () => undefined,
});

const inputProps = { plan };
const compositions = await getCompositions(serveUrl, { inputProps });
const composition = compositions.find((c) => c.id === "StoryScene");

if (!composition) {
  throw new Error("StoryScene composition not found");
}

const frameSpecs = framesArg.split(",").map((s) => {
  const parts = s.trim().split(":");
  if (parts.length === 2) {
    return { label: parts[0], frame: parseInt(parts[1], 10) };
  }
  return { label: `frame_${parts[0]}`, frame: parseInt(parts[0], 10) };
});

for (const spec of frameSpecs) {
  const outPath = path.join(outputDir, `${spec.label}.png`);
  console.log(`Rendering ${spec.label} at frame ${spec.frame} -> ${outPath}...`);
  await renderStill({
    composition,
    serveUrl,
    output: outPath,
    inputProps,
    frame: spec.frame,
    imageFormat: "png",
    logLevel: "warn",
  });
  console.log(`✓ Rendered ${spec.label}`);
}

console.log("All requested frames rendered successfully!");
