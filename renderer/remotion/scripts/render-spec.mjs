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
const renderSpec = request.renderSpec;
const outputPath = request.outputPath;

if (!renderSpec || !outputPath) {
  throw new Error("Render request requires renderSpec and outputPath.");
}

const entryPoint = path.join(rendererRoot, "src/index.ts");
const serveUrl = await bundle({
  entryPoint,
  onProgress: () => undefined,
});
const compositions = await getCompositions(serveUrl, {
  inputProps: renderSpec,
});
const composition = compositions.find((candidate) => candidate.id === renderSpec.composition);

if (!composition) {
  throw new Error(`Composition not found: ${renderSpec.composition}.`);
}

await mkdir(path.dirname(outputPath), { recursive: true });
await renderMedia({
  composition,
  serveUrl,
  codec: "h264",
  outputLocation: outputPath,
  inputProps: renderSpec,
  overwrite: true,
  muted: true,
  concurrency: 2,
  logLevel: "warn",
});

console.log(JSON.stringify({ outputPath, contentType: "video/mp4" }));
