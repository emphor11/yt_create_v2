import { bundle } from "@remotion/bundler";
import { getCompositions, renderStill } from "@remotion/renderer";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const rendererRoot = path.resolve(scriptDir, "..");
const entryPoint = path.join(rendererRoot, "src/index.ts");

const worldPath = path.join(rendererRoot, "test-renders/salary_compiled_world.json");
const world = JSON.parse(fs.readFileSync(worldPath, "utf8"));

console.log("Bundling Remotion entry point...");
const serveUrl = await bundle({
  entryPoint,
  onProgress: (p) => {
    if (p % 25 === 0) console.log(`Bundle progress: ${p}%`);
  },
});

console.log("Fetching WorldComposition...");
const compositions = await getCompositions(serveUrl, {
  inputProps: { world },
});
const comp = compositions.find((c) => c.id === "WorldComposition");
if (!comp) {
  throw new Error("WorldComposition not found in Root.tsx");
}

comp.durationInFrames = world.total_duration_frames;
comp.fps = world.canvas_config.fps;
comp.width = world.canvas_config.width;
comp.height = world.canvas_config.height;

console.log(`WorldComposition configured: ${comp.width}x${comp.height}, ${comp.fps}fps, ${comp.durationInFrames} frames`);

const testFrames = [
  { frame: 10, name: "frame_0010_beat01_beginning.png", desc: "beat_01 beginning" },
  { frame: 65, name: "frame_0065_beat01_raise_action.png", desc: "first raise action" },
  { frame: 950, name: "frame_0950_beat02_salary_comparison.png", desc: "beat_02 salary comparison" },
  { frame: 2600, name: "frame_2600_beat03_fixed_costs.png", desc: "beat_03 fixed-cost section" },
  { frame: 3400, name: "frame_3400_beat04_rent.png", desc: "beat_04 rent section" },
  { frame: 4000, name: "frame_4000_beat05_inflation.png", desc: "beat_05 inflation section" },
  { frame: 5200, name: "frame_5200_beat06_taxation.png", desc: "beat_06 taxation section" },
  { frame: 6500, name: "frame_6500_beat07_savings.png", desc: "beat_07 savings section" },
  { frame: 7920, name: "frame_7920_beat08_conclusion.png", desc: "beat_08 conclusion" },
  { frame: 8003, name: "frame_8003_terminal_hold.png", desc: "terminal hold" },
];

const outDir = path.join(rendererRoot, "test-renders/smoke_stills");
fs.mkdirSync(outDir, { recursive: true });

for (const tf of testFrames) {
  const outPath = path.join(outDir, tf.name);
  console.log(`Rendering frame ${tf.frame} (${tf.desc}) -> ${tf.name}...`);
  const start = Date.now();
  await renderStill({
    composition: comp,
    serveUrl,
    output: outPath,
    frame: tf.frame,
    inputProps: { world },
    imageFormat: "png",
    logLevel: "warn",
  });
  console.log(`  Rendered in ${Date.now() - start}ms: ${outPath}`);
}

console.log("SMOKE TEST STILLS COMPLETE!");
