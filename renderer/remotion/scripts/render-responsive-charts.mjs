import { bundle } from "@remotion/bundler";
import { getCompositions, renderStill } from "@remotion/renderer";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const rendererRoot = path.resolve(scriptDir, "..");

async function main() {
  console.log("[1/3] Reading /tmp/home_loan_plan.json...");
  const plan = JSON.parse(fs.readFileSync("/tmp/home_loan_plan.json", "utf8"));

  console.log("[2/3] Bundling Remotion...");
  const entryPoint = path.join(rendererRoot, "src/index.ts");
  const serveUrl = await bundle({ entryPoint });

  const compositions = await getCompositions(serveUrl, { inputProps: { plan } });
  const comp = compositions.find((c) => c.id === "StoryScene");
  if (!comp) throw new Error("StoryScene composition not found");

  const outDir = "/Users/dakshyadav/.gemini/antigravity/brain/0ea3762c-60ae-40de-96c0-ce19c83dda9d";
  const frames = [
    { frame: 1140, name: "responsive_chart_038s_amortization.png" },
    { frame: 3570, name: "responsive_chart_119s_return_comparison.png" },
    { frame: 4050, name: "responsive_chart_135s_savings_trajectory.png" },
  ];

  console.log("[3/3] Rendering responsive chart frames...");
  for (const item of frames) {
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
  console.log("SUCCESS: All responsive chart test frames rendered!");
}

main().catch((err) => {
  console.error("FATAL ERROR:", err);
  process.exit(1);
});
