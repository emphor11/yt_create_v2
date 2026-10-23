import type { StoryPlan } from "./types.ts";
import salaryTimestamps from "../../public/salary_split_story_timestamps.json" with { type: "json" };

/**
 * Story 3: Executive Salary Memo with True Split Transformation and Visual States.
 *
 * Story:
 * "A ₹50 lakh executive salary is not what hits your bank account.
 * ₹15 lakh goes to income taxes, and ₹10 lakh covers living expenses,
 * leaving you with exactly ₹25 lakh in real net savings."
 *
 * Capabilities:
 * 1. True Split Transformation:
 *    - 3 daughter cards physically emerge from inside the Executive Compensation Document
 *    - Cards scale up and travel from document center to target positions with division pulse
 * 2. Visual State Changes Beyond Numbers:
 *    - Official Document receives a green 'SANCTIONED' rubber ink stamp
 *    - Tax card transforms to 'danger' state with '30% SURCHARGE' badge
 *    - Living card transforms to 'warning' state with '20% LIVING' badge
 *    - Savings card transforms to 'success' state with '50% NET CORPUS' badge
 *    - Non-focused deduction cards smoothly 'dimmed' during climax
 * 3. Real audible narration track: 'salary_split_narration.mp3' mounted via <Audio>
 * 4. Factual mathematical provenance: salary_tax_split verifies gross == tax + living + savings
 * 5. Pure atomic cards in 5-layout spatial model (zero children, zero relative layouts)
 */
export const salarySplitStoryPlan: StoryPlan = {
  id: "salary_tax_split_story",
  fps: 30,
  durationInFrames: 380, // Matches 12.5s real narration
  width: 1920,
  height: 1080,
  safeMargin: 80,
  audioFileName: "salary_split_narration.mp3",
  narration: {
    text: salaryTimestamps.full_text,
    audioFile: salaryTimestamps.audio_file,
    wordTimestamps: salaryTimestamps.word_timestamps,
  },
  objects: [
    // 1. Non-Card Primitive: Official Salary Statement Document
    {
      id: "doc_salary",
      type: "document",
      layout: "split_left",
      width: 420,
      height: 300,
      documentProps: {
        title: "Executive Compensation Memo",
        serialNo: "REF: FY26-CORP-EXEC-0941",
        issuer: "Board of Directors & Payroll",
        date: "Fiscal Year 2026-27",
        statusBadge: "APPROVED SANCTION",
        watermark: "OFFICIAL",
        accentColor: "#38BDF8", // Cyan
        items: [
          { label: "Designation", value: "Senior Director" },
          { label: "Pay Grade", value: "Level 8 Executive" },
          { label: "Compensation Basis", value: "Annual Guaranteed CTC" },
        ],
        value: 5000000,
        provenance: {
          derived_from: {
            formula: "salary_tax_split",
            inputs: { gross: 5000000, tax: 1500000, living: 1000000, savings: 2500000 },
          },
        },
      },
    },

    // 2. Split Daughter 1: Income Tax & Surcharge (Split Right)
    {
      id: "card_tax",
      type: "card",
      layout: "split_right",
      width: 400,
      height: 180,
      cardProps: {
        title: "Income Tax & Cess",
        value: 1500000,
        format: "currency_inr",
        subtitle: "30% Effective Surcharge",
        accentColor: "#EF4444", // Red
      },
    },

    // 3. Split Daughter 2: Fixed Living Costs (Center)
    {
      id: "card_living",
      type: "card",
      layout: "center",
      width: 360,
      height: 180,
      cardProps: {
        title: "Living Expenses & Rent",
        value: 1000000,
        format: "currency_inr",
        subtitle: "20% Essential Sustenance",
        accentColor: "#F59E0B", // Amber
      },
    },

    // 4. Split Daughter 3: Net Liquid Savings (Full Bottom)
    {
      id: "card_savings",
      type: "card",
      layout: "full_bottom",
      width: 1760,
      height: 200,
      cardProps: {
        title: "Net Retained Savings",
        value: 2500000,
        format: "currency_inr",
        subtitle: "50% Real Wealth Corpus",
        accentColor: "#10B981", // Emerald Green
      },
    },

    // Split Connectors Branching Out from Document
    {
      id: "conn_split_tax",
      type: "connector",
      connectorProps: {
        fromId: "doc_salary",
        toId: "card_tax",
        label: "Deduction 1",
        arrow: true,
      },
    },
    {
      id: "conn_split_living",
      type: "connector",
      connectorProps: {
        fromId: "doc_salary",
        toId: "card_living",
        label: "Deduction 2",
        arrow: true,
      },
    },
    {
      id: "conn_split_savings",
      type: "connector",
      connectorProps: {
        fromId: "doc_salary",
        toId: "card_savings",
        label: "Net Balance",
        arrow: true,
      },
    },
  ],
  events: [
    // 1. Spoken Anchor: 'executive salary' -> Salary Document enters
    {
      action: "enter",
      targetId: "doc_salary",
      anchor: "executive salary",
      startFrame: 15,
      durationFrames: 25,
      style: "fade_slide_up",
    },
    // 2. Official Rubber Stamp slams onto the document
    {
      action: "change_visual_state",
      targetId: "doc_salary",
      startFrame: 50,
      durationFrames: 20,
      state: "stamped",
      stamp: {
        text: "SANCTIONED",
        color: "#10B981",
        angle: -14,
      },
    },
    // 3. Camera pushes in gently to establish document
    {
      action: "camera",
      startFrame: 60,
      durationFrames: 30,
      behavior: "push_in",
      zoom: 1.04,
      requiredContextIds: ["doc_salary"],
    },
    // 4. TRUE SPLIT TRANSFORMATION:
    //    All 3 daughter cards physically emerge from inside the Executive Compensation Document!
    {
      action: "split",
      sourceId: "doc_salary",
      targetIds: ["card_tax", "card_living", "card_savings"],
      startFrame: 90,
      durationFrames: 30,
      staggerFrames: 35, // Staggered to sync with narration cues!
    },
    // 5. Connectors branch out as cards emerge
    {
      action: "connect",
      targetId: "conn_split_tax",
      startFrame: 105,
      durationFrames: 20,
    },
    {
      action: "change_visual_state",
      targetId: "card_tax",
      startFrame: 120,
      durationFrames: 15,
      state: "danger",
      badge: "30% SURCHARGE",
    },
    {
      action: "connect",
      targetId: "conn_split_living",
      startFrame: 145,
      durationFrames: 20,
    },
    {
      action: "change_visual_state",
      targetId: "card_living",
      startFrame: 155,
      durationFrames: 15,
      state: "warning",
      badge: "20% LIVING",
    },
    {
      action: "connect",
      targetId: "conn_split_savings",
      startFrame: 180,
      durationFrames: 20,
    },
    {
      action: "change_visual_state",
      targetId: "card_savings",
      startFrame: 195,
      durationFrames: 15,
      state: "success",
      badge: "50% NET CORPUS",
    },
    // 6. Camera shifts to reveal complete split while preserving all cards in view
    {
      action: "camera",
      startFrame: 235,
      durationFrames: 30,
      behavior: "push_in",
      zoom: 1.04,
      requiredContextIds: ["doc_salary", "card_tax", "card_living"],
    },
    // 7. Visual State: Dim secondary deduction cards to make savings pop heroically
    {
      action: "change_visual_state",
      targetId: "card_tax",
      startFrame: 250,
      durationFrames: 20,
      state: "dimmed",
    },
    {
      action: "change_visual_state",
      targetId: "card_living",
      startFrame: 250,
      durationFrames: 20,
      state: "dimmed",
    },
    // 8. Dramatic Climax: Highlight final retained net savings
    {
      action: "emphasize",
      targetId: "card_savings",
      startFrame: 260,
      durationFrames: 35,
      grow: 1.08,
      darkenBackdrop: 0.55,
      connectorIntensity: 2.0,
      dominant: true,
    },
    {
      action: "highlight",
      targetId: "card_savings",
      startFrame: 275,
      durationFrames: 35,
      color: "#10B981",
    },
  ],
};
