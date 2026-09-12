import { bundle } from "@remotion/bundler";
import { getCompositions, renderStill } from "@remotion/renderer";
import { mkdir, copyFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const rendererRoot = path.resolve(scriptDir, "..");
const outputDir = path.resolve(rendererRoot, "test-outputs/broll_caption");
const artifactDir = "/Users/dakshyadav/.gemini/antigravity/brain/a538aef0-5101-46ba-a3b4-7c766d4b9a56";
await mkdir(outputDir, { recursive: true });

console.log("Bundling Remotion project...");
const entryPoint = path.join(rendererRoot, "src/index.ts");
const serveUrl = await bundle({
  entryPoint,
  onProgress: () => undefined,
});

const testCases = [
  {
    name: "01_statement_thesis",
    frame: 75,
    props: {
      scene_id: "broll_01_statement",
      composition: "BrollCaption",
      fps: 30,
      duration_frames: 180,
      props: {
        headerLabel: "CORE INVESTMENT THESIS",
        caption: "The true cost of inflation is not what you spend today, but the compound wealth you never generate.",
        emphasisPhrase: "the compound wealth you never generate",
        variant: "statement",
        polarity: "critical",
      },
    },
  },
  {
    name: "02_quote_luminary",
    frame: 75,
    props: {
      scene_id: "broll_02_quote",
      composition: "BrollCaption",
      fps: 30,
      duration_frames: 180,
      props: {
        headerLabel: "NOTABLE PERSPECTIVE // WISDOM",
        caption: "The big money is not in the buying and the selling, but in the waiting.",
        author: "Charlie Munger",
        sourceContext: "Vice Chairman, Berkshire Hathaway",
        variant: "quote",
        polarity: "positive",
      },
    },
  },
  {
    name: "03_ambient_broll_asset_backed",
    frame: 75,
    props: {
      scene_id: "broll_03_ambient_asset",
      composition: "BrollCaption",
      fps: 30,
      duration_frames: 180,
      props: {
        headerLabel: "GLOBAL MACRO CONTEXT",
        caption: "Supply bottlenecks and shifting sovereign yields redefine modern cross-border liquidity flows.",
        emphasisPhrase: "redefine modern cross-border liquidity",
        variant: "ambient_broll",
        polarity: "neutral",
        asset: {
          asset_type: "video",
          local_path: "run_037fbcb7ba2e4471a87f6687bb2c5b05_scene_002_asset_hook_0_1_beat_02.mp4",
        },
      },
    },
  },
  {
    name: "04_no_asset_fallback",
    frame: 75,
    props: {
      scene_id: "broll_04_no_asset",
      composition: "BrollCaption",
      fps: 30,
      duration_frames: 180,
      props: {
        headerLabel: "AUTOMATION MAXIM",
        caption: "Disciplined systematic contribution consistently outperforms tactical speculation over 30-year horizons.",
        emphasisPhrase: "systematic contribution consistently outperforms speculation",
        variant: "statement",
        polarity: "positive",
        asset: null,
      },
    },
  },
  {
    name: "05_long_caption",
    frame: 75,
    props: {
      scene_id: "broll_05_long_caption",
      composition: "BrollCaption",
      fps: 30,
      duration_frames: 180,
      props: {
        headerLabel: "SEQUENCE RISK AUDIT",
        caption: "When early retirement liquidations coincide with severe multi-year equity drawdowns, permanent wealth destruction accelerates exponentially, exhausting solvent capital decades ahead of actuarial life expectancy.",
        emphasisPhrase: "permanent wealth destruction accelerates exponentially",
        variant: "statement",
        polarity: "critical",
      },
    },
  },
  {
    name: "06_short_duration_34frames",
    frame: 26,
    props: {
      scene_id: "broll_06_short_duration",
      composition: "BrollCaption",
      fps: 30,
      duration_frames: 34,
      props: {
        headerLabel: "PURCHASING POWER REALITY",
        caption: "Cash feels safe for 30 days, but guarantees permanent loss over 30 years.",
        emphasisPhrase: "guarantees permanent loss over 30 years",
        variant: "statement",
        polarity: "critical",
      },
    },
  },
];

console.log(`Rendering ${testCases.length} visual test cases for BrollCaption...`);
for (const tc of testCases) {
  const compositions = await getCompositions(serveUrl, { inputProps: tc.props });
  const composition = compositions.find((candidate) => candidate.id === "BrollCaption");
  if (!composition) {
    throw new Error("BrollCaption composition not found in Root.tsx");
  }

  const outputFileName = `broll_caption_${tc.name}.png`;
  const outputPath = path.join(outputDir, outputFileName);
  const artifactPath = path.join(artifactDir, outputFileName);

  console.log(`Rendering ${tc.name} at frame ${tc.frame} (duration: ${tc.props.duration_frames})...`);
  await renderStill({
    composition,
    serveUrl,
    output: outputPath,
    inputProps: tc.props,
    frame: tc.frame,
    imageFormat: "png",
    logLevel: "warn",
  });

  await copyFile(outputPath, artifactPath);
  console.log(`Saved: ${artifactPath}`);
}

console.log("All BrollCaption test cases rendered and copied to artifacts successfully.");
