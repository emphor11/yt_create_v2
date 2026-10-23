import { bundle } from "@remotion/bundler";
import { getCompositions, renderMedia, renderStill } from "@remotion/renderer";
import { mkdir } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { stockVideoStoryPlan } from "../src/story_engine/stockVideoStoryPlan.ts";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const rendererRoot = path.resolve(scriptDir, "..");
const entryPoint = path.join(rendererRoot, "src/index.ts");
const outDir = path.resolve(rendererRoot, "../../output");

console.log("Bundling Remotion entry point for StockVideo vertical-slice test...");
const serveUrl = await bundle({
  entryPoint,
  onProgress: () => undefined,
});

const compositions = await getCompositions(serveUrl);
const comp = compositions.find((c) => c.id === "StockVideoStoryScene");
if (!comp) {
  throw new Error("Could not find StockVideoStoryScene composition");
}

await mkdir(outDir, { recursive: true });

const outVideo = path.join(outDir, "stock_video_story.mp4");
console.log(`\nRendering Stock-Video vertical-slice MP4 to ${outVideo}...`);
await renderMedia({
  composition: comp,
  serveUrl,
  codec: "h264",
  outputLocation: outVideo,
  inputProps: { plan: stockVideoStoryPlan },
  logLevel: "warn",
});
console.log(`✓ Rendered Stock-Video MP4: ${outVideo}`);

// Keyframes requested:
// 1. enter frame - 1 (Frame 171)
// 2. enter frame (Frame 172)
// 3. middle of stock video (Frame 251)
// 4. exit frame - 1 (Frame 329)
// 5. exit frame (Frame 330)
// 6. next visual frame (Frame 355)

const keyframes = [
  { frame: 171, name: "stock_video_f171_enter_minus_1.png", desc: "enter frame - 1 (Card 1 before stock video)" },
  { frame: 172, name: "stock_video_f172_enter_frame.png", desc: "enter frame (Hard Cut in: stock video full screen)" },
  { frame: 251, name: "stock_video_f251_middle.png", desc: "middle of stock video (B-roll footage playing full screen)" },
  { frame: 329, name: "stock_video_f329_exit_minus_1.png", desc: "exit frame - 1 (Stock video final frame)" },
  { frame: 330, name: "stock_video_f330_exit_frame.png", desc: "exit frame (Hard Cut out: video cuts away, Card 2 enters)" },
  { frame: 355, name: "stock_video_f355_next_visual.png", desc: "next visual frame (Card 2 settled)" },
];

for (const kf of keyframes) {
  const dest = path.join(outDir, kf.name);
  console.log(`Rendering frame ${kf.frame} (${kf.desc}) to ${dest}...`);
  await renderStill({
    composition: comp,
    serveUrl,
    output: dest,
    frame: kf.frame,
    inputProps: { plan: stockVideoStoryPlan },
  });
  console.log(`✓ Rendered frame ${kf.frame}: ${dest}`);
}

console.log("\n==================================================");
console.log("STOCK-VIDEO VERTICAL-SLICE RENDER COMPLETE!");
console.log("==================================================");
