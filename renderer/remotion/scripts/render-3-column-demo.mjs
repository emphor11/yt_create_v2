import { bundle } from "@remotion/bundler";
import { getCompositions, renderStill } from "@remotion/renderer";
import path from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const rendererRoot = path.resolve(scriptDir, "..");
const repoRoot = path.resolve(rendererRoot, "../..");
const entryPoint = path.join(rendererRoot, "src/index.ts");
const outDir = path.resolve("/Users/dakshyadav/.gemini/antigravity/brain/0ea3762c-60ae-40de-96c0-ce19c83dda9d");

const livingCanvasPlan = {
  id: "living_canvas_demo",
  fps: 30,
  durationInFrames: 250,
  width: 1920,
  height: 1080,
  safeMargin: 80,
  autoLayout: true,
  objects: [
    {
      id: "hero_card",
      type: "card",
      layout: "center",
      cardProps: {
        title: "Mutual Fund Commission",
        subtitle: "1% annual expense ratio",
        displayValue: "₹45 Lakhs",
        accentColor: "#EF4444",
        badge: "WEALTH DRAIN",
      },
    },
    {
      id: "left_img",
      type: "image",
      layout: "split_left",
      imageProps: {
        assetId: "assets/img_macro_close-up_of_signed_mortgage_agreement_contract_documen.jpg",
        caption: "SEBI Mandate (Jan 2013)",
        badge: "REGULATION",
      },
    },
    {
      id: "right_img",
      type: "image",
      layout: "split_right",
      imageProps: {
        assetId: "assets/img_cinematic_macro_photography_of_modern_financial_stock_exchan.jpg",
        caption: "Equal Market Returns",
        badge: "INDEX DATA",
      },
    },
  ],
  events: [
    { action: "enter", targetId: "hero_card", startFrame: 0, durationFrames: 10 },
    { action: "enter", targetId: "left_img", startFrame: 30, durationFrames: 15 },
    { action: "enter", targetId: "right_img", startFrame: 30, durationFrames: 15 },
  ],
};

console.log("Bundling Remotion for 3-Column Demo...");
const serveUrl = await bundle({
  entryPoint,
  onProgress: () => undefined,
});

const compositions = await getCompositions(serveUrl, { inputProps: { plan: livingCanvasPlan } });
const comp = compositions.find((c) => c.id === "StoryScene");

const outPath = path.join(outDir, "living_canvas_3_column_symphony.png");
console.log("Rendering 3-Column Symphony at Frame 60...");
await renderStill({
  composition: comp,
  serveUrl,
  output: outPath,
  frame: 60,
  inputProps: { plan: livingCanvasPlan },
  logLevel: "warn",
});
console.log("✓ Saved 3-Column Symphony demo to:", outPath);
