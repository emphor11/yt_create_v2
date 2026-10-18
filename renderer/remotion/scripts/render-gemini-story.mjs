import { bundle } from "@remotion/bundler";
import { getCompositions, renderMedia, renderStill } from "@remotion/renderer";
import { readFile, mkdir, stat } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const rendererRoot = path.resolve(scriptDir, "..");
const repoRoot = path.resolve(rendererRoot, "../..");
const entryPoint = path.join(rendererRoot, "src/index.ts");
const planPath = path.join(repoRoot, "output/gemini_compiled_loan_plan.json");
const outDir = path.join(repoRoot, "output");
const stillsDir = path.join(outDir, "gemini_story_stills");

console.log("=================================================================");
console.log("RENDERING GEMINI-GENERATED CONTINUOUS STORY");
console.log("=================================================================");

// 1. Load compiled plan
console.log(`[1/4] Loading compiled plan: ${path.relative(repoRoot, planPath)}`);
const planRaw = await readFile(planPath, "utf-8");
const plan = JSON.parse(planRaw);
console.log(`      Story ID: ${plan.id}, Duration: ${plan.durationInFrames} frames (${(plan.durationInFrames / plan.fps).toFixed(1)}s), Objects: ${plan.objects.length}, Events: ${plan.events.length}`);

// 2. Bundle Remotion
console.log(`[2/4] Bundling Remotion project...`);
const serveUrl = await bundle({
  entryPoint,
  onProgress: () => undefined,
});

const compositions = await getCompositions(serveUrl, { inputProps: { plan } });
const comp = compositions.find((c) => c.id === "StoryScene");
if (!comp) {
  throw new Error("StoryScene composition not found in Root.tsx!");
}

await mkdir(stillsDir, { recursive: true });

// 3. Render Keyframe Stills
console.log(`[3/4] Rendering 10 keyframe stills across all 3 visual beats...`);
const keyframes = [
  { frame: 30, name: "gemini_kf_01_loan_entered.png", label: "Beat 1: Loan card entered at center_left (₹50 Lakh)" },
  { frame: 90, name: "gemini_kf_02_emi_and_link.png", label: "Beat 1: EMI card entered at center_right (₹43,391) + rate link connected" },
  { frame: 185, name: "gemini_kf_03_loan_rate_warning.png", label: "Beat 2: Loan card warning state (10.5% Rate badge)" },
  { frame: 250, name: "gemini_kf_04_emi_transforming.png", label: "Beat 2: EMI value transforming towards ₹49,919" },
  { frame: 285, name: "gemini_kf_05_emi_danger_climax.png", label: "Beat 2 climax: EMI card in danger state (Surged badge, ₹49,919)" },
  { frame: 340, name: "gemini_kf_06_extra_burden_entered.png", label: "Beat 3: Extra burden card entered at bottom_center (₹15.66 Lakh)" },
  { frame: 400, name: "gemini_kf_07_extra_burden_eroded.png", label: "Beat 3: Extra burden card eroded state (Severe Burden badge)" },
  { frame: 490, name: "gemini_kf_08_final_composition.png", label: "Final story climax: 3 atomic cards across 12-zone spatial canvas with zero overlap" },
];

for (const kf of keyframes) {
  const outputPath = path.join(stillsDir, kf.name);
  console.log(`      Rendering frame ${kf.frame} -> ${kf.name} (${kf.label})...`);
  await renderStill({
    composition: comp,
    serveUrl,
    output: outputPath,
    inputProps: { plan },
    frame: kf.frame,
    imageFormat: "png",
    logLevel: "warn",
  });
  const fileStat = await stat(outputPath);
  console.log(`      ✓ Rendered ${kf.name} (${(fileStat.size / 1024).toFixed(1)} KB)`);
}

// 4. Render Full MP4 Video
const videoPath = path.join(outDir, "gemini_loan_story.mp4");
console.log(`[4/4] Rendering full MP4 video with real audio narration...`);
console.log(`      Output target: ${path.relative(repoRoot, videoPath)}`);

await renderMedia({
  composition: comp,
  serveUrl,
  codec: "h264",
  outputLocation: videoPath,
  inputProps: { plan },
  logLevel: "warn",
});

const videoStat = await stat(videoPath);
console.log(`      ✓ Rendered MP4 successfully! Size: ${(videoStat.size / (1024 * 1024)).toFixed(2)} MB`);

console.log("\n=================================================================");
console.log("RENDER COMPLETE!");
console.log("=================================================================");
console.log(`Video:  ${path.relative(repoRoot, videoPath)}`);
console.log(`Stills: ${path.relative(repoRoot, stillsDir)}/`);
