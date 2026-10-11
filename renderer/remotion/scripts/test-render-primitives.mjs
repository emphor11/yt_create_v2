import { bundle } from "@remotion/bundler";
import { getCompositions, renderStill } from "@remotion/renderer";
import path from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const rendererRoot = path.resolve(scriptDir, "..");
const entryPoint = path.join(rendererRoot, "src/index.ts");

console.log("Bundling Remotion entry point...");
const serveUrl = await bundle({
  entryPoint,
  onProgress: (p) => {
    if (p % 25 === 0) console.log(`Bundle progress: ${p}%`);
  },
});

console.log("Fetching compositions...");
const compositions = await getCompositions(serveUrl);
console.log(`Found ${compositions.length} compositions.`);
const comp = compositions.find((c) => c.id === "PrimitiveDemo");
if (!comp) {
  throw new Error("PrimitiveDemo composition not found in Root.tsx!");
}
console.log(`Found composition: ${comp.id} (${comp.width}x${comp.height}, ${comp.fps}fps)`);

console.log("Rendering frame 60 of PrimitiveDemo...");
const outputLocation = path.join(rendererRoot, "primitive_demo_rendered.png");
await renderStill({
  composition: comp,
  serveUrl,
  output: outputLocation,
  frame: 60,
  logLevel: "info",
});

console.log("SUCCESS! Rendered frame saved to:", outputLocation);
