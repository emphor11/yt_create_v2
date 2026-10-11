import { bundle } from "@remotion/bundler";
import { getCompositions, renderStill } from "@remotion/renderer";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const rendererRoot = path.resolve(scriptDir, "..");
const entryPoint = path.join(rendererRoot, "src/index.ts");

const world = JSON.parse(fs.readFileSync("/tmp/upi_compiled_world.json", "utf8"));
console.log(`Loaded UPI world: ${world.world_id}, ${world.total_duration_frames} frames`);

const serveUrl = await bundle({
  entryPoint,
  onProgress: (p) => {
    if (p % 25 === 0) console.log(`Bundle progress: ${p}%`);
  },
});

const compositions = await getCompositions(serveUrl, {
  inputProps: { world },
});
const comp = compositions.find((c) => c.id === "WorldComposition");
if (!comp) throw new Error("WorldComposition not found");

comp.durationInFrames = world.total_duration_frames;
comp.fps = world.canvas_config.fps;
comp.width = world.canvas_config.width;
comp.height = world.canvas_config.height;

const outDir = "/Users/dakshyadav/.gemini/antigravity/brain/5abf01a1-4fd5-44c8-9cee-9833da68fca4/video_frames";
fs.mkdirSync(outDir, { recursive: true });

const testFrames = [
  { frame: 50, name: "upi_beat1_frame50.png", desc: "Beat 1 Coffee QR HeroStat" },
  { frame: 400, name: "upi_beat1_frame400.png", desc: "Beat 1 HeroStat + Callout" },
  { frame: 1000, name: "upi_beat2_frame1000.png", desc: "Beat 2 News vs Reality ComparisonCard" },
  { frame: 5000, name: "upi_beat6_frame5000.png", desc: "Beat 6 Merchant Fee ProcessCard (3 steps)" },
  { frame: 6400, name: "upi_beat7_frame6400.png", desc: "Beat 7 Milestone Extension HeroStat + Callout" },
];

for (const tf of testFrames) {
  const outPath = path.join(outDir, tf.name);
  console.log(`Rendering frame ${tf.frame} (${tf.desc}) -> ${tf.name}...`);
  const t0 = Date.now();
  await renderStill({
    composition: comp,
    serveUrl,
    output: outPath,
    frame: tf.frame,
    inputProps: { world },
    imageFormat: "png",
    logLevel: "warn",
  });
  console.log(`  Rendered in ${Date.now() - t0}ms: ${outPath}`);
}

console.log("All UPI test stills rendered successfully!");
