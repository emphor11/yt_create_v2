import type { StoryPlan } from "./types.ts";
import loanTimestamps from "../../public/loan_story_timestamps.json" with { type: "json" };

/**
 * Visual Plan for the ₹50 Lakh Loan Story (Atomic 5-Layout Spatial Model).
 *
 * Story:
 * "A ₹50 lakh loan starts at 8.5% interest. When the rate rises to 10.5%, the EMI increases."
 *
 * Fully addresses audit points:
 * 1. Real audible narration track: 'loan_narration.mp3' mounted via <Audio>
 * 2. Word-level timestamps from actual spoken audio
 * 3. Fixed factually misleading text: EMI subtitle is initially 'Base Monthly Payment' and only
 *    transforms to '+ ₹6,528 / month burden' when the rate hike takes effect!
 * 4. Factual mathematical provenance: EMI has verifiable derivation from principal, rate, tenure
 * 5. Camera viewport context: retains visibility of loan and rate context cards
 * 6. Pure atomic cards in 5-layout spatial model (zero children, zero relative layouts)
 */
export const loanStoryPlan: StoryPlan = {
  id: "loan_rate_hike_story",
  fps: 30,
  durationInFrames: 505, // Matches 16.8s real narration (Chunks 1-4)
  width: 1920,
  height: 1080,
  safeMargin: 80,
  audioFileName: "loan_narration.mp3",
  narration: {
    text: loanTimestamps.full_text,
    audioFile: loanTimestamps.audio_file,
    wordTimestamps: loanTimestamps.word_timestamps,
  },
  objects: [
    {
      id: "card_loan",
      type: "card",
      layout: "center",
      width: 380,
      height: 230,
      cardProps: {
        title: "Home Loan Principal",
        value: 5000000,
        format: "currency_inr",
        subtitle: "20 Year Tenure",
        accentColor: "#3B82F6", // Blue
      },
    },
    {
      id: "card_rate",
      type: "card",
      layout: "split_right",
      width: 380,
      height: 230,
      cardProps: {
        title: "Interest Rate",
        value: 8.5,
        format: "percentage",
        decimals: 1,
        subtitle: "Annual Floating",
        accentColor: "#F59E0B", // Amber
      },
    },
    {
      id: "card_emi",
      type: "card",
      layout: "center",
      width: 380,
      height: 230,
      cardProps: {
        title: "Monthly EMI",
        value: 43391,
        format: "currency_inr",
        subtitle: "Base Monthly Payment",
        accentColor: "#EF4444", // Red/Warning
        provenance: {
          derived_from: {
            formula: "loan_emi",
            inputs: { principal: 5000000, rate: 8.5, tenure_months: 240 },
          },
        },
      },
    },
    {
      id: "connector_rate_to_emi",
      type: "connector",
      connectorProps: {
        fromId: "card_rate",
        toId: "card_emi",
        label: "Drives payment",
        arrow: true,
      },
    },
  ],
  events: [
    // 1. Spoken Anchor: 'fifty lakh' -> Loan card appears centered
    {
      action: "enter",
      targetId: "card_loan",
      anchor: "50 lakh",
      startFrame: 15,
      durationFrames: 25,
      style: "fade_slide_up",
    },
    // 2. Spatial Movement: Loan card moves to split_left
    {
      action: "move",
      targetId: "card_loan",
      startFrame: 65,
      durationFrames: 30,
      to: "split_left",
    },
    // 3. Spoken Anchor: 'starts at 8.5' -> Rate card appears at split_right
    {
      action: "enter",
      targetId: "card_rate",
      anchor: "starts at",
      startFrame: 95,
      durationFrames: 25,
      style: "fade_slide_up",
    },
    // 4. Baseline EMI card appears at center
    {
      action: "enter",
      targetId: "card_emi",
      startFrame: 130,
      durationFrames: 25,
      style: "fade_slide_up",
    },
    // 5. Connector unrolls between Rate and EMI
    {
      action: "connect",
      targetId: "connector_rate_to_emi",
      startFrame: 160,
      durationFrames: 25,
    },
    // 6. Camera pushes in gently
    {
      action: "camera",
      startFrame: 180,
      durationFrames: 35,
      behavior: "push_in",
      zoom: 1.05,
      requiredContextIds: ["card_loan", "card_rate"],
    },
    // 7. Spoken Anchor: 'rate rises to 10.5' -> Rate changes to 10.5%
    {
      action: "transform_number",
      targetId: "card_rate",
      anchor: "rises to 10.5",
      startFrame: 195,
      durationFrames: 30,
      toValue: 10.5,
    },
    // 8. Visual State: Rate card transitions to warning with hike badge
    {
      action: "change_visual_state",
      targetId: "card_rate",
      startFrame: 220,
      durationFrames: 20,
      state: "warning",
      badge: "+2.0% HIKE",
    },
    {
      action: "emphasize",
      targetId: "card_rate",
      startFrame: 230,
      durationFrames: 20,
      dominant: true,
    },
    // 9. Spoken Anchor: 'EMI surges' -> EMI transforms to ₹49,919 with verified mathematical provenance
    {
      action: "transform_number",
      targetId: "card_emi",
      anchor: "monthly EMI",
      startFrame: 250,
      durationFrames: 30,
      toValue: 49919,
      provenance: {
        derived_from: {
          formula: "loan_emi",
          inputs: { principal: 5000000, rate: 10.5, tenure_months: 240 },
        },
      },
    },
    // 10. Reveal burden subtitle at the EXACT moment EMI increases!
    {
      action: "transform_text",
      targetId: "card_emi",
      startFrame: 265,
      durationFrames: 15,
      toText: "+ ₹6,528 / month burden",
      toColor: "#F87171",
    },
    // 11. Visual State: EMI card enters danger state, Loan card dims
    {
      action: "change_visual_state",
      targetId: "card_emi",
      startFrame: 265,
      durationFrames: 20,
      state: "danger",
      badge: "BURDEN SURGE",
    },
    {
      action: "change_visual_state",
      targetId: "card_loan",
      startFrame: 270,
      durationFrames: 20,
      state: "dimmed",
    },
    // 11. Dramatic climax: background darkens, connector turns heavy crimson, EMI card grows
    {
      action: "emphasize",
      targetId: "card_emi",
      startFrame: 275,
      durationFrames: 35,
      grow: 1.12,
      darkenBackdrop: 0.6,
      connectorIntensity: 2.2,
      dominant: true,
    },
    // 12. Camera focuses with controlled zoom that preserves context
    {
      action: "camera",
      startFrame: 280,
      durationFrames: 35,
      behavior: "focus",
      targetId: "card_emi",
      zoom: 1.08,
      requiredContextIds: ["card_loan", "card_rate"],
    },
    // 13. Highlight pulse on expanded EMI
    {
      action: "highlight",
      targetId: "card_emi",
      startFrame: 295,
      durationFrames: 35,
      color: "#EF4444",
    },
  ],
};
