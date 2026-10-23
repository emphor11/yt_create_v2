import { bundle } from "@remotion/bundler";
import { getCompositions, renderMedia, renderStill } from "@remotion/renderer";
import { mkdir } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { fiveLayoutsDemoStoryPlan } from "../src/story_engine/fiveLayoutsDemoStoryPlan.ts";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const rendererRoot = path.resolve(scriptDir, "..");
const entryPoint = path.join(rendererRoot, "src/index.ts");
const outDir = path.resolve(rendererRoot, "../../output");

console.log("Bundling Remotion entry point for 5-layout reduction test...");
const serveUrl = await bundle({
  entryPoint,
  onProgress: () => undefined,
});

const compositions = await getCompositions(serveUrl);
const comp = compositions.find((c) => c.id === "FiveLayoutsDemoStoryScene");
if (!comp) {
  throw new Error("Could not find FiveLayoutsDemoStoryScene composition");
}

await mkdir(outDir, { recursive: true });

const outVideo = path.join(outDir, "five_layouts_reduced_demo.mp4");
console.log(`\nRendering 5-Layout Reduced Story MP4 to ${outVideo}...`);
await renderMedia({
  composition: comp,
  serveUrl,
  codec: "h264",
  outputLocation: outVideo,
  inputProps: { plan: fiveLayoutsDemoStoryPlan },
  logLevel: "warn",
});
console.log(`✓ Rendered 5-Layout Story MP4: ${outVideo}`);

// Visual validation frames for each of the 5 layouts:
const keyframes = [
  {
    frame: 35,
    name: "layout_1_full_screen.png",
    desc: "1. full_screen: Real documentary B-Roll owns entire canvas",
  },
  {
    frame: 100,
    name: "layout_2_center.png",
    desc: "2. center: Hero Loan Metric card centered as single hero concept",
  },
  {
    frame: 210,
    name: "layout_3_4_split_left_right.png",
    desc: "3 & 4. split_left + split_right: Institution image on left, Rate hike card on right, divider respected",
  },
  {
    frame: 350,
    name: "layout_5_full_bottom.png",
    desc: "5. full_bottom: Trajectory area chart across bottom with subtitle clearance",
  },
];

for (const kf of keyframes) {
  const dest = path.join(outDir, kf.name);
  console.log(`Rendering frame ${kf.frame} (${kf.desc}) to ${dest}...`);
  await renderStill({
    composition: comp,
    serveUrl,
    output: dest,
    frame: kf.frame,
    inputProps: { plan: fiveLayoutsDemoStoryPlan },
  });
  console.log(`✓ Rendered frame ${kf.frame}: ${dest}`);
}

console.log("\n==================================================");
console.log("5-LAYOUT REDUCED VERTICAL-SLICE RENDER COMPLETE!");
console.log("==================================================");
