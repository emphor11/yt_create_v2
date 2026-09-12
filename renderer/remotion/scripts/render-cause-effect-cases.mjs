import { bundle } from "@remotion/bundler";
import { getCompositions, renderStill } from "@remotion/renderer";
import { mkdir, copyFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const rendererRoot = path.resolve(scriptDir, "..");
const outputDir = path.resolve(rendererRoot, "test-outputs/cause_effect");
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
    name: "01_single_cause_negative",
    frame: 75,
    props: {
      scene_id: "cause_01_single_neg",
      composition: "CauseEffect",
      fps: 30,
      duration_frames: 180,
      props: {
        headerLabel: "INFLATION RISK PROFILE",
        causes: [
          { label: "Unhedged 7% Inflation", value: "-7.0% p.a.", icon: "📉" },
        ],
        connector: "leads to",
        outcomeLabel: "Real Wealth Erosion",
        outcomeValue: "60% Purchasing Power Loss",
        outcomeSeverity: "critical",
        outcomeHeaderLabel: "Systemic Downside",
        outcomeNote: "Fixed cash deposits lose over half their purchasing power in 10 years",
        variant: "single_cause",
        polarity: "critical",
      },
    },
  },
  {
    name: "02_single_cause_positive",
    frame: 75,
    props: {
      scene_id: "cause_02_single_pos",
      composition: "CauseEffect",
      fps: 30,
      duration_frames: 180,
      props: {
        headerLabel: "COMPOUNDING BLUEPRINT",
        causes: [
          { label: "Disciplined Monthly SIP", value: "₹25,000 / month", icon: "📈" },
        ],
        connector: "compounds to",
        outcomeLabel: "Retirement Freedom Corpus",
        outcomeValue: "₹2.4 Crore",
        outcomeSeverity: "positive",
        outcomeHeaderLabel: "Long-Term Payoff",
        outcomeNote: "12% CAGR equity growth over a 20-year unbroken investment horizon",
        variant: "single_cause",
        polarity: "positive",
      },
    },
  },
  {
    name: "03_dual_cause_negative",
    frame: 75,
    props: {
      scene_id: "cause_03_dual_neg",
      composition: "CauseEffect",
      fps: 30,
      duration_frames: 180,
      props: {
        headerLabel: "FRICTIONAL DRAG ANALYSIS",
        causes: [
          { label: "2.5% Active Fund Expense", value: "Annual Fee Drag", icon: "💸" },
          { label: "Taxes on Frequent Churn", value: "20% STCG Drag", icon: "⚖️" },
        ],
        connector: "combine to create",
        outcomeLabel: "Severe Portfolio Shortfall",
        outcomeValue: "₹42 Lakhs Lost",
        outcomeSeverity: "negative",
        outcomeHeaderLabel: "Frictional Wealth Loss",
        outcomeNote: "Hidden fees and transaction frictions quietly consume 35% of total terminal gains",
        variant: "dual_cause",
        polarity: "negative",
      },
    },
  },
  {
    name: "04_dual_cause_positive",
    frame: 75,
    props: {
      scene_id: "cause_04_dual_pos",
      composition: "CauseEffect",
      fps: 30,
      duration_frames: 180,
      props: {
        headerLabel: "STRATEGIC ACCUMULATION",
        causes: [
          { label: "Early Asset Allocation", value: "70% Equity / 30% Debt", icon: "🎯" },
          { label: "Annual Step-Up Contribution", value: "+10% Yearly", icon: "🚀" },
        ],
        connector: "converge to achieve",
        outcomeLabel: "Financial Independence (FIRE)",
        outcomeValue: "Corpus Reached at Age 48",
        outcomeSeverity: "positive",
        outcomeHeaderLabel: "Compounding Synergy",
        outcomeNote: "Step-up contributions shorten the accumulation phase by over 7 years",
        variant: "dual_cause",
        polarity: "positive",
      },
    },
  },
  {
    name: "05_tri_cause_systemic_risk",
    frame: 75,
    props: {
      scene_id: "cause_05_tri_risk",
      composition: "CauseEffect",
      fps: 30,
      duration_frames: 180,
      props: {
        headerLabel: "SEQUENCE-OF-RETURNS RISK",
        causes: [
          { label: "Severe Market Drawdown", value: "-35% Crash", icon: "💥" },
          { label: "Surging Core Inflation", value: "+8.2% Spike", icon: "🔥" },
          { label: "Emergency Liquidity Crunch", value: "Zero Buffer", icon: "⚠️" },
        ],
        connector: "converge to trigger",
        outcomeLabel: "Premature Capital Exhaustion",
        outcomeValue: "Depleted in Year 11",
        outcomeSeverity: "critical",
        outcomeHeaderLabel: "Triple Threat Sequence Risk",
        outcomeNote: "Forced asset sales in a down market permanently lock in irreversible capital loss",
        variant: "multi_cause",
        polarity: "critical",
      },
    },
  },
  {
    name: "06_short_duration_34frames",
    frame: 26,
    props: {
      scene_id: "cause_06_short_duration",
      composition: "CauseEffect",
      fps: 30,
      duration_frames: 34,
      props: {
        headerLabel: "RAPID CAUSAL BEAT",
        causes: [
          { label: "Hidden Fee Drag", value: "2.1%", icon: "💸" },
          { label: "Tax Friction", value: "15%", icon: "⚖️" },
        ],
        connector: "compounds to",
        outcomeLabel: "Portfolio Shortfall",
        outcomeValue: "₹18 Lakhs Lost",
        outcomeSeverity: "negative",
        outcomeHeaderLabel: "Frictional Erosion",
        outcomeNote: "Verified duration-safe on 34 frames",
        variant: "dual_cause",
        polarity: "negative",
      },
    },
  },
];

for (const tc of testCases) {
  const compositions = await getCompositions(serveUrl, { inputProps: tc.props });
  const composition = compositions.find((candidate) => candidate.id === "CauseEffect");
  if (!composition) {
    throw new Error("CauseEffect composition not found in Root.tsx");
  }

  const outputPath = path.join(outputDir, `${tc.name}.png`);
  console.log(`Rendering ${tc.name} at frame ${tc.frame} (duration ${tc.props.duration_frames})...`);
  await renderStill({
    composition,
    serveUrl,
    output: outputPath,
    inputProps: tc.props,
    frame: tc.frame,
    imageFormat: "png",
    logLevel: "warn",
  });
  console.log(`✓ Saved ${outputPath}`);

  // Also copy to artifact directory for presentation & embedding in walkthrough.md
  const artifactPath = path.join(artifactDir, `cause_effect_${tc.name}.png`);
  await copyFile(outputPath, artifactPath);
  console.log(`✓ Copied to artifact: ${artifactPath}`);
}

console.log("All 5 CauseEffect visual cases successfully rendered!");
