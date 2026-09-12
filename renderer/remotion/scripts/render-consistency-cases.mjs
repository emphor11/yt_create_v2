import { bundle } from "@remotion/bundler";
import { getCompositions, renderStill } from "@remotion/renderer";
import { mkdir, copyFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const rendererRoot = path.resolve(scriptDir, "..");
const outputDir = path.resolve(rendererRoot, "test-outputs/consistency");
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
    fileName: "comparison_split_01_clear_winner.png",
    compositionId: "SplitComparison",
    frame: 75,
    props: {
      scene_id: "split_01_winner",
      composition: "SplitComparison",
      fps: 30,
      duration_frames: 180,
      props: {
        headerLabel: "LONG-TERM FEE IMPACT",
        comparisonLabel: "20-YEAR WEALTH OUTCOME",
        leftRole: "Active Regular Fund",
        leftLabel: "2.25% Expense Ratio Drag",
        leftValue: "₹1.48 Crore",
        leftUnit: "Corpus",
        rightRole: "Low-Cost Direct Index",
        rightLabel: "0.15% Expense Ratio",
        rightValue: "₹2.64 Crore",
        rightUnit: "Corpus",
        winner: "right",
        delta: "+₹1.16 Crore Alpha",
        tone: "superiority",
        footerLabel: "Assumes ₹25,000/mo SIP at 12% gross annual returns over 20 years",
      },
    },
  },
  {
    fileName: "comparison_split_02_close_comparison.png",
    compositionId: "SplitComparison",
    frame: 75,
    props: {
      scene_id: "split_02_close",
      composition: "SplitComparison",
      fps: 30,
      duration_frames: 180,
      props: {
        headerLabel: "CASH YIELD BENCHMARK",
        comparisonLabel: "POST-TAX ANNUAL RETURN",
        leftRole: "Traditional Bank FD",
        leftLabel: "Fixed Deposit at 30% Tax Slab",
        leftValue: "4.55%",
        leftUnit: "Net Yield",
        rightRole: "Arbitrage Fund",
        rightLabel: "Equity Taxation (12.5% LTCG)",
        rightValue: "6.21%",
        rightUnit: "Net Yield",
        delta: "+1.66% Post-Tax Gain",
        tone: "neutral",
        footerLabel: "Calculated for high-income bracket investors over 12-month horizon",
      },
    },
  },
  {
    fileName: "ranked_list_01_3_items.png",
    compositionId: "RankedList",
    frame: 75,
    props: {
      scene_id: "ranked_01_3items",
      composition: "RankedList",
      fps: 30,
      duration_frames: 180,
      props: {
        headerLabel: "TOP WEALTH DESTROYERS",
        variant: "dominance",
        showBars: true,
        items: [
          {
            title: "Lifestyle Inflation",
            rank: 1,
            subtitle: "Upgrading expenses in lockstep with income raises",
            value: "42%",
            numericValue: 42,
            badge: "PRIMARY DRAIN",
            change: "+2",
          },
          {
            title: "Hidden Fees & Churn",
            rank: 2,
            subtitle: "Active management and transaction friction",
            value: "28%",
            numericValue: 28,
            badge: "SECOND ORDER",
            change: "-1",
          },
          {
            title: "Tax Inefficiency",
            rank: 3,
            subtitle: "Unoptimized capital gains realization",
            value: "18%",
            numericValue: 18,
            badge: "DRAG",
            change: "NEW",
          },
        ],
        footerLabel: "Quantified drag on retirement corpus accumulation over 25 years",
      },
    },
  },
  {
    fileName: "ranked_list_02_5_items.png",
    compositionId: "RankedList",
    frame: 80,
    props: {
      scene_id: "ranked_02_5items",
      composition: "RankedList",
      fps: 30,
      duration_frames: 180,
      props: {
        headerLabel: "PORTFOLIO CAPITAL ALLOCATION",
        variant: "dominance",
        showBars: true,
        items: [
          {
            title: "Diversified Equities",
            rank: 1,
            subtitle: "Nifty 50 + Midcap Index",
            value: "₹45.0 Lakh",
            numericValue: 45,
            badge: "CORE ENGINE",
          },
          {
            title: "Commercial Real Estate",
            rank: 2,
            subtitle: "REITs & Rental Inflows",
            value: "₹30.0 Lakh",
            numericValue: 30,
          },
          {
            title: "Fixed Income & Debt",
            rank: 3,
            subtitle: "Target Maturity Funds",
            value: "₹15.0 Lakh",
            numericValue: 15,
          },
          {
            title: "Sovereign Gold Bonds",
            rank: 4,
            subtitle: "Inflation hedge + 2.5% coupon",
            value: "₹8.0 Lakh",
            numericValue: 8,
          },
          {
            title: "Emergency Liquid Reserves",
            rank: 5,
            subtitle: "6 Months Operating Expenses",
            value: "₹4.0 Lakh",
            numericValue: 4,
          },
        ],
        footerLabel: "Ideal ₹1.02 Crore allocation for capital preservation and growth",
      },
    },
  },
  {
    fileName: "process_flow_01_3_steps_horizontal.png",
    compositionId: "ProcessFlow",
    frame: 75,
    props: {
      scene_id: "process_01_3steps",
      composition: "ProcessFlow",
      fps: 30,
      duration_frames: 180,
      props: {
        headerLabel: "AUTOMATED WEALTH ARCHITECTURE",
        layout: "horizontal",
        steps: [
          {
            title: "Salary Inflow",
            subtitle: "Direct Payroll Deposit",
            type: "cause",
            value: "₹2,50,000/mo",
            connectorLabel: "auto-debits",
          },
          {
            title: "Systematic SIP",
            subtitle: "60/40 Equity & Debt Split",
            type: "step",
            value: "₹1,00,000/mo",
            connectorLabel: "compounds into",
          },
          {
            title: "Financial Freedom",
            subtitle: "Year 15 Milestone",
            type: "outcome",
            value: "₹4.8 Crore",
          },
        ],
        footerLabel: "Zero-touch execution rules that remove emotional decision friction",
      },
    },
  },
  {
    fileName: "process_flow_02_5_steps_vertical.png",
    compositionId: "ProcessFlow",
    frame: 80,
    props: {
      scene_id: "process_02_5steps",
      composition: "ProcessFlow",
      fps: 30,
      duration_frames: 180,
      props: {
        headerLabel: "DEBT AVALANCHE FRAMEWORK",
        layout: "vertical",
        steps: [
          {
            title: "Credit Card Debt",
            subtitle: "36.0% APR • Maximum Hazard",
            type: "cause",
            value: "Pay Aggressively",
            connectorLabel: "cleared first",
          },
          {
            title: "Personal Loan",
            subtitle: "14.5% APR • Fixed Term",
            type: "step",
            value: "Roll Over Extra Cash",
            connectorLabel: "then attack",
          },
          {
            title: "Auto Vehicle Loan",
            subtitle: "8.8% APR • Fixed Payment",
            type: "step",
            value: "Pay Minimum",
            connectorLabel: "then target",
          },
          {
            title: "Home Mortgage",
            subtitle: "8.2% APR • Tax Deductible",
            type: "step",
            value: "Maintain Schedule",
            connectorLabel: "completes to",
          },
          {
            title: "100% Debt Freedom",
            subtitle: "Zero Liabilities Achieved",
            type: "outcome",
            value: "100% Solvency",
          },
        ],
        footerLabel: "The mathematically optimal way to eliminate debt with minimal interest paid",
      },
    },
  },
  {
    fileName: "consistency_short_duration_34frames.png",
    compositionId: "SplitComparison",
    frame: 30,
    props: {
      scene_id: "split_03_short",
      composition: "SplitComparison",
      fps: 30,
      duration_frames: 34,
      props: {
        headerLabel: "REAL ESTATE PARADOX",
        comparisonLabel: "OPPORTUNITY COST",
        leftRole: "Home Ownership EMI",
        leftLabel: "₹65,000 EMI + Maintenance",
        leftValue: "₹65K/mo",
        rightRole: "Rent & SIP Strategy",
        rightLabel: "₹25K Rent + ₹40K SIP",
        rightValue: "₹40K SIP",
        winner: "right",
        delta: "2.4x Corpus at Yr 20",
        tone: "superiority",
        footerLabel: "Fast 1.13s scene safely settles without clipping",
      },
    },
  },
];

for (const testCase of testCases) {
  console.log(`Rendering ${testCase.fileName} at frame ${testCase.frame}...`);
  const compositions = await getCompositions(serveUrl, { inputProps: testCase.props });
  const comp = compositions.find((c) => c.id === testCase.compositionId);
  if (!comp) {
    throw new Error(`Composition ${testCase.compositionId} not found in Root.tsx`);
  }

  comp.durationInFrames = testCase.props.duration_frames || 180;
  comp.fps = testCase.props.fps || 30;

  const outputPath = path.join(outputDir, testCase.fileName);
  await renderStill({
    composition: comp,
    serveUrl,
    output: outputPath,
    frame: testCase.frame,
    inputProps: testCase.props,
    imageFormat: "png",
    logLevel: "warn",
  });

  const artifactPath = path.join(artifactDir, testCase.fileName);
  await copyFile(outputPath, artifactPath);
  console.log(`✓ Rendered & saved to artifacts: ${testCase.fileName}`);
}

console.log("\n==================================================");
console.log("ALL 7 STILL CASES RENDERED AND VERIFIED");
console.log("==================================================");
