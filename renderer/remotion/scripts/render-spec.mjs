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
const inputProps = renderSpec.composition === "StoryScene"
  ? (renderSpec.plan ? { plan: renderSpec.plan } : (renderSpec.props?.plan ? renderSpec.props : renderSpec))
  : renderSpec;

const compositions = await getCompositions(serveUrl, {
  inputProps,
});
const composition = compositions.find((candidate) => candidate.id === renderSpec.composition);

if (!composition) {
  throw new Error(`Composition not found: ${renderSpec.composition}.`);
}

// Override composition settings dynamically to match the render spec
if (renderSpec.duration_frames) {
  composition.durationInFrames = renderSpec.duration_frames;
}
if (renderSpec.fps) {
  composition.fps = renderSpec.fps;
}

await mkdir(path.dirname(outputPath), { recursive: true });

// Print timing report before rendering
const storyPlan = renderSpec.plan || renderSpec.props?.plan;
if (storyPlan && storyPlan.objects && storyPlan.events) {
  const fps = storyPlan.fps || composition.fps || 30;
  const durationFrames = storyPlan.durationInFrames || composition.durationInFrames || 380;
  for (const obj of storyPlan.objects) {
    const enterEv = storyPlan.events.find(
      (e) => (e.action === "enter" || e.action === "connect") && e.targetId === obj.id
    );
    const exitEv = storyPlan.events.find(
      (e) => e.action === "exit" && e.targetId === obj.id
    );
    if (enterEv) {
      const anchor = enterEv.anchor || "";
      const startFrame = enterEv.startFrame || 0;
      const matchedTs = `${(startFrame / fps).toFixed(2)}s`;
      const enterStatus = "present";
      const endTs = exitEv
        ? `${((exitEv.startFrame || durationFrames) / fps).toFixed(2)}s`
        : `${(durationFrames / fps).toFixed(2)}s`;
      console.log(`Object: ${obj.id}`);
      console.log(`Anchor: "${anchor}"`);
      console.log(`Matched timestamp: ${matchedTs}`);
      console.log(`Start frame: ${startFrame}`);
      console.log(`Enter event: ${enterStatus}`);
      console.log(`Visible interval: ${matchedTs} – ${endTs}\n`);
    } else {
      console.log(`Object: ${obj.id}`);
      console.log(`Anchor: ""`);
      console.log(`Matched timestamp: N/A`);
      console.log(`Start frame: N/A`);
      console.log(`Enter event: missing`);
      console.log(`Visible interval: N/A (invisible)\n`);
    }
  }
}

await renderMedia({
  composition,
  serveUrl,
  codec: "h264",
  outputLocation: outputPath,
  inputProps,
  overwrite: true,
  muted: false,
  concurrency: 2,
  logLevel: "warn",
});

console.log(JSON.stringify({ outputPath, contentType: "video/mp4" }));
