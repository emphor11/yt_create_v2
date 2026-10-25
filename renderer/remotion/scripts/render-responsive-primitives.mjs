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
    { frame: 360, name: "responsive_card_012s_early_window.png" },
    { frame: 700, name: "responsive_card_023s_emi_breakdown.png" },
    { frame: 1140, name: "responsive_hero_chart_038s_amortization.png" },
    { frame: 2500, name: "responsive_number_083s_tenure_slash.png" },
    { frame: 3300, name: "responsive_split_110s_rbi_image_card.png" },
    { frame: 3570, name: "responsive_hero_chart_119s_return_comparison.png" },
    { frame: 3900, name: "responsive_number_130s_total_savings.png" },
  ];

  console.log("[3/3] Rendering responsive primitive verification frames...");
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
  console.log("SUCCESS: All responsive primitive test frames rendered!");
}

main().catch((err) => {
  console.error("FATAL ERROR:", err);
  process.exit(1);
});
