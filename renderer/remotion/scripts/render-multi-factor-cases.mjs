import { bundle } from "@remotion/bundler";
import { getCompositions, renderStill } from "@remotion/renderer";
import { mkdir, copyFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const rendererRoot = path.resolve(scriptDir, "..");
const outputDir = path.resolve(rendererRoot, "test-outputs/multi_factor_pressure");
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
    name: "01_dual_factor_critical",
    frame: 75,
    props: {
      scene_id: "mf_01_dual_critical",
      composition: "MultiFactorPressure",
      fps: 30,
      duration_frames: 180,
      props: {
        headerLabel: "INFLATION & YIELD SQUEEZE",
        factors: [
          { label: "Headline Inflation Surge", value: "7.2% p.a.", severity: "critical" },
          { label: "Fixed Deposit Yield Gap", value: "2.4% Net", severity: "medium" },
        ],
        combinedLabel: "Purchasing Power Collapse",
        outcomeValue: "-42% Real Capital",
        combinedSeverity: "critical",
        outcomeHeaderLabel: "CRITICAL THREAT // CONVERGENCE",
        outcomeNote: "Negative real yields compound annually, exhausting purchasing power in 10 years",
        variant: "dual_factor",
        polarity: "critical",
      },
    },
  },
  {
    name: "02_tri_factor_systemic",
    frame: 75,
    props: {
      scene_id: "mf_02_tri_systemic",
      composition: "MultiFactorPressure",
      fps: 30,
      duration_frames: 180,
      props: {
        headerLabel: "SYSTEMIC MACRO CONVERGENCE",
        factors: [
          { label: "Aggressive Rate Hikes", value: "+250 bps", severity: "high" },
          { label: "Currency Depreciation", value: "-8.4%", severity: "critical" },
          { label: "Import Supply Shock", value: "+18%", severity: "medium" },
        ],
        combinedLabel: "Severe Operating Margin Squeeze",
        outcomeValue: "-31% Free Cash Flow",
        combinedSeverity: "high",
        outcomeHeaderLabel: "HIGH RISK // SYSTEMIC",
        outcomeNote: "Simultaneous input cost inflation and surging debt service crush margins",
        variant: "tri_factor",
        polarity: "high",
      },
    },
  },
  {
    name: "03_quad_factor_retirement_squeeze",
    frame: 75,
    props: {
      scene_id: "mf_03_quad_retirement",
      composition: "MultiFactorPressure",
      fps: 30,
      duration_frames: 180,
      props: {
        headerLabel: "RETIREMENT SOLVENCY AUDIT",
        factors: [
          { label: "Market Sequence Drawdown", value: "-22%", severity: "critical" },
          { label: "Medical Inflation Surge", value: "+14% p.a.", severity: "high" },
          { label: "Active Mutual Fund Drag", value: "2.25%", severity: "medium" },
          { label: "Longevity Horizon Extension", value: "+7 Years", severity: "low" },
        ],
        combinedLabel: "Premature Portfolio Depletion",
        outcomeValue: "Year 13 Failure",
        combinedSeverity: "critical",
        outcomeHeaderLabel: "CRITICAL SYSTEMIC CONVERGENCE",
        outcomeNote: "Four independent financial forces converge to exhaust liquid wealth 12 years early",
        variant: "quad_factor",
        polarity: "critical",
      },
    },
  },
  {
    name: "04_dual_factor_positive_synergy",
    frame: 75,
    props: {
      scene_id: "mf_04_dual_positive",
      composition: "MultiFactorPressure",
      fps: 30,
      duration_frames: 180,
      props: {
        headerLabel: "WEALTH ACCELERATION STRATEGY",
        factors: [
          { label: "Automated Equity SIP", value: "₹50,000 / mo", severity: "low" },
          { label: "Systematic Tax Harvesting", value: "+1.8% Alpha", severity: "low" },
        ],
        combinedLabel: "Accelerated Corpus Compounding",
        outcomeValue: "₹3.8 Crore",
        combinedSeverity: "low",
        outcomeHeaderLabel: "POSITIVE SYNERGY // ACCELERATION",
        outcomeNote: "Continuous disciplined accumulation combined with tax efficiency maximizes net worth",
        variant: "dual_factor",
        polarity: "positive",
      },
    },
  },
  {
    name: "05_short_duration_34frames",
    frame: 28,
    props: {
      scene_id: "mf_05_short_duration",
      composition: "MultiFactorPressure",
      fps: 30,
      duration_frames: 34,
      props: {
        headerLabel: "RAPID VALUATION CONTRACTION",
        factors: [
          { label: "Peak Valuation Multiples", value: "35x P/E", severity: "high" },
          { label: "Central Bank Liquidity Drain", value: "-$1.2T", severity: "critical" },
          { label: "Corporate Margin Squeeze", value: "-450 bps", severity: "medium" },
        ],
        combinedLabel: "Multiple Re-Rating Shock",
        outcomeValue: "-28% Multiple",
        combinedSeverity: "critical",
        outcomeHeaderLabel: "CRITICAL THREAT // RAPID DOWNSIDE",
        outcomeNote: "Tightening financial conditions force rapid multiple compression across equities",
        variant: "tri_factor",
        polarity: "critical",
      },
    },
  },
];

console.log(`Rendering ${testCases.length} visual test cases for MultiFactorPressure...`);
for (const tc of testCases) {
  const compositions = await getCompositions(serveUrl, { inputProps: tc.props });
  const composition = compositions.find((candidate) => candidate.id === "MultiFactorPressure");
  if (!composition) {
    throw new Error("MultiFactorPressure composition not found in Root.tsx");
  }

  const outputFileName = `multi_factor_${tc.name}.png`;
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

console.log("All MultiFactorPressure test cases rendered and copied to artifacts successfully.");
