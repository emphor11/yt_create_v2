import { bundle } from "@remotion/bundler";
import { getCompositions, renderStill } from "@remotion/renderer";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const rendererRoot = path.resolve(scriptDir, "..");

async function main() {
  console.log("[1/4] Reading /tmp/test_plan.json...");
  const plan = JSON.parse(fs.readFileSync("/tmp/test_plan.json", "utf8"));
  
  console.log("[2/4] Bundling entry point...");
  const entryPoint = path.join(rendererRoot, "src/index.ts");
  const serveUrl = await bundle({ entryPoint });
  console.log("      Bundle URL:", serveUrl);

  console.log("[3/4] Resolving composition...");
  const compositions = await getCompositions(serveUrl, { inputProps: { plan } });
  const comp = compositions.find((c) => c.id === "StoryScene");
  if (!comp) throw new Error("Composition StoryScene not found");

  const outDir = "/Users/dakshyadav/.gemini/antigravity/brain/0ea3762c-60ae-40de-96c0-ce19c83dda9d";
  const framesToTest = [
    { frame: 780, name: "step1_frame_026s.png" },
    { frame: 2160, name: "step1_frame_072s.png" },
    { frame: 2640, name: "step1_frame_088s.png" },
    { frame: 3960, name: "step1_frame_132s.png" },
  ];

  console.log("[4/4] Rendering frames...");
  for (const item of framesToTest) {
    const outPath = path.join(outDir, item.name);
    console.log(`      Rendering frame ${item.frame} -> ${item.name}...`);
    await renderStill({
      composition: comp,
      serveUrl,
      output: outPath,
      inputProps: { plan },
      frame: item.frame,
      logLevel: "warn",
    });
    console.log(`      Done: ${item.name} (${fs.statSync(outPath).size} bytes)`);
  }
  console.log("ALL TEST FRAMES RENDERED SUCCESSFULLY!");
}

main().catch((err) => {
  console.error("FATAL ERROR:", err);
  process.exit(1);
});
