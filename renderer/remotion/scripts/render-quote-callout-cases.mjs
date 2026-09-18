/**
 * QuoteCallout render cases — validates 3-phase word-reveal upgrade
 * Tests: 30f, 45f, 90f, 150f, 300f + realistic narrative example
 *
 * Usage: node scripts/render-quote-callout-cases.mjs
 */
import { bundle } from "@remotion/bundler";
import { getCompositions, renderStill } from "@remotion/renderer";
import { mkdir, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const rendererRoot = path.resolve(scriptDir, "..");
const outputBase = path.resolve(scriptDir, "../test-renders/quote-callout");

await mkdir(outputBase, { recursive: true });

// ── Shared example props ─────────────────────────────────────────────────
const shortQuote = {
  quote: "Compounding is the eighth wonder of the world.",
  author: "Warren Buffett",
  role: "CEO, Berkshire Hathaway",
  avatar: "💡",
};

const longQuote = {
  quote:
    "The four most dangerous words in investing are: this time it's different. Markets cycle, fundamentals endure, and patience is the only durable edge.",
  author: "John Templeton",
  role: "Founder, Templeton Growth Fund",
  avatar: "📈",
  headerLabel: "INVESTING WISDOM",
};

const mediumQuote = {
  quote: "Risk comes from not knowing what you're doing. Know your circle of competence.",
  author: "Charlie Munger",
  role: "Vice Chairman, Berkshire Hathaway",
  avatar: "🧠",
};

// ── Test cases ───────────────────────────────────────────────────────────
const cases = [
  // Duration stress tests (short quote — most word-reveal stress)
  { label: "30f-short",  durationFrames: 30,  props: shortQuote },
  { label: "45f-short",  durationFrames: 45,  props: shortQuote },
  { label: "90f-short",  durationFrames: 90,  props: shortQuote },

  // Medium duration — verify word pacing is readable
  { label: "150f-medium", durationFrames: 150, props: mediumQuote },

  // Long duration — verify all 3 phases are well-spaced
  { label: "300f-long",  durationFrames: 300, props: longQuote },

  // Realistic narrative: 180f (6s at 30fps) with long quote + header
  { label: "180f-realistic", durationFrames: 180, props: longQuote },

  // Mid-word frame checks: render at frame that is mid-word-reveal (~40% D)
  { label: "150f-mid-reveal", durationFrames: 150, props: mediumQuote, frameOverride: 60 },

  // Author-phase check: render at ~70% D to verify author is visible
  { label: "180f-author-phase", durationFrames: 180, props: longQuote, frameOverride: 130 },
];

console.log("Bundling Remotion...");
const entryPoint = path.join(rendererRoot, "src/index.ts");
const serveUrl = await bundle({
  entryPoint,
  onProgress: () => undefined,
});

const allComps = await getCompositions(serveUrl, { inputProps: {} });
const comp = allComps.find((c) => c.id === "QuoteCallout");
if (!comp) {
  throw new Error("QuoteCallout composition not found in Root.tsx");
}

let passed = 0;
let failed = 0;

for (const tc of cases) {
  const fps = 30;
  const frame = tc.frameOverride !== undefined
    ? tc.frameOverride
    : Math.floor(tc.durationFrames * 0.85); // default: render near end (payoff held)

  const outputPath = path.join(outputBase, `${tc.label}-frame${frame}.png`);

  const inputProps = {
    duration_frames: tc.durationFrames,
    durationInFrames: tc.durationFrames,
    fps,
    props: tc.props,
  };

  try {
    await renderStill({
      composition: {
        ...comp,
        durationInFrames: tc.durationFrames,
        fps,
      },
      serveUrl,
      output: outputPath,
      inputProps,
      frame,
      imageFormat: "png",
      logLevel: "error",
    });
    console.log(`✓ ${tc.label.padEnd(22)} frame=${String(frame).padStart(3)}/${tc.durationFrames} → ${path.basename(outputPath)}`);
    passed++;
  } catch (err) {
    console.error(`✗ ${tc.label} FAILED: ${err.message}`);
    failed++;
  }
}

console.log(`\nRender cases: ${passed} passed, ${failed} failed`);
console.log(`Output: ${outputBase}`);
if (failed > 0) process.exit(1);
