import { bundle } from "@remotion/bundler";
import { getCompositions, renderStill } from "@remotion/renderer";
import path from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const rendererRoot = path.resolve(scriptDir, "..");

const testPlanDocument = {
  id: "test_document_scene",
  fps: 30,
  durationInFrames: 120,
  width: 1920,
  height: 1080,
  safeMargin: 80,
  autoLayout: true,
  atmosphere: { preset: "paper_clean" },
  objects: [
    {
      id: "doc_sebi_fii",
      type: "document",
      layout: "center",
      documentProps: {
        title: "SECURITIES AND EXCHANGE BOARD OF INDIA",
        serialNo: "CIRCULAR NO. SEBI/HO/MRD/2024/114",
        docReference: "CIRCULAR NO. SEBI/HO/MRD/2024/114",
        docBody: "Foreign Portfolio Investors recorded consecutive weekly capital flight, resulting in a cumulative net exit exceeding ₹1,14,000 Crore from domestic equity markets.",
        highlightPhrase: "exceeding ₹1,14,000 Crore",
        watermark: "OFFICIAL FILING",
        stampText: "REGULATORY NOTICE",
        statusBadge: "MANDATORY CIRCULAR",
        visualState: "danger",
      },
    },
  ],
  events: [
    {
      action: "enter",
      targetId: "doc_sebi_fii",
      startFrame: 0,
      durationFrames: 25,
      style: "fade_slide_up",
    },
  ],
};

const testPlanWaterfall = {
  id: "test_waterfall_scene",
  fps: 30,
  durationInFrames: 120,
  width: 1920,
  height: 1080,
  safeMargin: 80,
  autoLayout: true,
  atmosphere: { preset: "paper_clean" },
  objects: [
    {
      id: "wf_corporate_margin",
      type: "waterfall",
      layout: "center",
      waterfallProps: {
        title: "WHERE CORPORATE PROFITS EVAPORATE",
        initialLabel: "Gross Revenue",
        initialDisplayValue: "₹10,000 Cr",
        initialValue: 10000,
        steps: [
          {
            label: "Raw Material Inflation",
            displayValue: "-₹5,400 Cr",
            value: 5400,
            stepType: "deduction",
          },
          {
            label: "Rising Wage & Power Costs",
            displayValue: "-₹2,200 Cr",
            value: 2200,
            stepType: "deduction",
          },
          {
            label: "High Interest Debt Service",
            displayValue: "-₹1,200 Cr",
            value: 1200,
            stepType: "deduction",
          },
        ],
        finalLabel: "Net Surviving Profit",
        finalDisplayValue: "₹1,200 Cr",
        finalValue: 1200,
        badge: "12% NET MARGIN",
        visualState: "warning",
      },
    },
  ],
  events: [
    {
      action: "enter",
      targetId: "wf_corporate_margin",
      startFrame: 0,
      durationFrames: 25,
      style: "fade_slide_up",
    },
  ],
};

const testPlanCapitalFlow = {
  id: "test_capital_flow_scene",
  fps: 30,
  durationInFrames: 120,
  width: 1920,
  height: 1080,
  safeMargin: 80,
  autoLayout: true,
  atmosphere: { preset: "paper_clean" },
  objects: [
    {
      id: "flow_fii_flight",
      type: "capital_flow",
      layout: "center",
      capitalFlowProps: {
        title: "GLOBAL CAPITAL FLIGHT",
        sourceLabel: "MUMBAI // BSE",
        sourceSublabel: "Overvalued Indian Equities",
        targetLabel: "NEW YORK // WALL ST",
        targetSublabel: "Risk-Free US 10-Yr Treasuries (4.5%)",
        flowLabel: "Cumulative FII Drain",
        flowDisplayValue: "₹1,14,000 Crore",
        flowDirection: "left_to_right",
        badge: "HISTORIC DRAIN",
        visualState: "danger",
      },
    },
  ],
  events: [
    {
      action: "enter",
      targetId: "flow_fii_flight",
      startFrame: 0,
      durationFrames: 25,
      style: "fade_slide_up",
    },
  ],
};

async function main() {
  console.log("Bundling Remotion project...");
  const entryPoint = path.join(rendererRoot, "src/index.ts");
  const serveUrl = await bundle({
    entryPoint,
    onProgress: () => undefined,
  });

  const artifactsDir = "/Users/dakshyadav/.gemini/antigravity/brain/0ea3762c-60ae-40de-96c0-ce19c83dda9d";
  const docOut = path.join(artifactsDir, "verified_document_primitive_frame_045.png");
  const wfOut = path.join(artifactsDir, "verified_waterfall_primitive_frame_045.png");
  const cfOut = path.join(artifactsDir, "verified_capital_flow_primitive_frame_045.png");

  console.log("Rendering Document primitive frame 45...");
  const docComps = await getCompositions(serveUrl, {
    inputProps: { plan: testPlanDocument },
  });
  const docComp = docComps.find((c) => c.id === "FiveLayoutsDemoStoryScene");

  await renderStill({
    composition: docComp,
    serveUrl,
    output: docOut,
    inputProps: { plan: testPlanDocument },
    frame: 45,
    imageFormat: "png",
    logLevel: "warn",
  });
  console.log("Document frame rendered:", docOut);

  console.log("Rendering Waterfall primitive frame 45...");
  const wfComps = await getCompositions(serveUrl, {
    inputProps: { plan: testPlanWaterfall },
  });
  const wfComp = wfComps.find((c) => c.id === "FiveLayoutsDemoStoryScene");

  await renderStill({
    composition: wfComp,
    serveUrl,
    output: wfOut,
    inputProps: { plan: testPlanWaterfall },
    frame: 45,
    imageFormat: "png",
    logLevel: "warn",
  });
  console.log("Waterfall frame rendered:", wfOut);

  console.log("Rendering Capital Flow primitive frame 45...");
  const cfComps = await getCompositions(serveUrl, {
    inputProps: { plan: testPlanCapitalFlow },
  });
  const cfComp = cfComps.find((c) => c.id === "FiveLayoutsDemoStoryScene");

  await renderStill({
    composition: cfComp,
    serveUrl,
    output: cfOut,
    inputProps: { plan: testPlanCapitalFlow },
    frame: 45,
    imageFormat: "png",
    logLevel: "warn",
  });
  console.log("Capital Flow frame rendered:", cfOut);
}

main().catch((err) => {
  console.error("Render failed:", err);
  process.exit(1);
});
