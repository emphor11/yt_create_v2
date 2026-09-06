import { bundle } from "@remotion/bundler";
import { getCompositions, renderStill } from "@remotion/renderer";
import { mkdir, readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const rendererRoot = path.resolve(scriptDir, "..");
const requestPath = process.argv[2];

if (!requestPath) {
  throw new Error("Missing render still request JSON path.");
}

const request = JSON.parse(await readFile(requestPath, "utf8"));
const compositionId = request.composition;
const inputProps = request.inputProps || {};
const outputPath = request.outputPath;

if (!compositionId || !outputPath) {
  throw new Error("Render still request requires composition and outputPath.");
}

const entryPoint = path.join(rendererRoot, "src/index.ts");
const serveUrl = await bundle({
  entryPoint,
  onProgress: () => undefined,
});

const compositions = await getCompositions(serveUrl, {
  inputProps,
});
const composition = compositions.find((candidate) => candidate.id === compositionId);

if (!composition) {
  throw new Error(`Composition not found: ${compositionId}.`);
}

await mkdir(path.dirname(outputPath), { recursive: true });
await renderStill({
  composition,
  serveUrl,
  output: outputPath,
  inputProps,
  imageFormat: "png",
  logLevel: "warn",
});

console.log(JSON.stringify({ outputPath, contentType: "image/png" }));
