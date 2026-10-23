import type { StoryPlan } from "./types.ts";
import inflationTimestamps from "../../public/inflation_story_timestamps.json" with { type: "json" };

/**
 * Story 2: Inflation Erosion with Real Trajectory Chart and Visual State Changes.
 *
 * Story:
 * "At 7% inflation, your ₹10 lakh savings loses half its purchasing power
 * in 10 years, shrinking to just ₹5.08 lakh in real value."
 *
 * Capabilities:
 * 1. Real audible narration track: 'inflation_narration.mp3' mounted via <Audio>
 * 2. Real Chart Primitive: 10-Year Purchasing Power Trajectory Area Curve with SVG gradients
 * 3. Visual State Changes:
 *    - Card nominal dims ('dimmed')
 *    - Inflation card displays 'warning' state with '7% DRAG' badge
 *    - Purchasing power card transforms to 'eroded' state with dashed border and 'CRITICAL DRAG' badge
 * 4. Factual mathematical provenance: compound inflation decay formula
 * 5. Camera context safety: all elements verified in viewport
 * 6. Pure atomic cards in 5-layout spatial model (zero children, zero relative layouts)
 */
export const inflationStoryPlan: StoryPlan = {
  id: "inflation_purchasing_power_story",
  fps: 30,
  durationInFrames: 380, // Matches 12.5s real narration
  width: 1920,
  height: 1080,
  safeMargin: 80,
  audioFileName: "inflation_narration.mp3",
  narration: {
    text: inflationTimestamps.full_text,
    audioFile: inflationTimestamps.audio_file,
    wordTimestamps: inflationTimestamps.word_timestamps,
  },
  objects: [
    {
      id: "card_nominal",
      type: "card",
      layout: "split_left",
      width: 400,
      height: 220,
      cardProps: {
        title: "Nominal Bank Balance",
        value: 1000000,
        format: "currency_inr",
        subtitle: "Fixed in your account",
        accentColor: "#38BDF8", // Cyan
      },
    },
    {
      id: "card_inflation",
      type: "card",
      layout: "split_right",
      width: 400,
      height: 220,
      cardProps: {
        title: "Annual Inflation",
        value: 7.0,
        format: "percentage",
        decimals: 1,
        subtitle: "10-Year Compounding Drag",
        accentColor: "#F59E0B", // Amber
      },
    },
    {
      id: "card_purchasing_power",
      type: "card",
      layout: "center",
      width: 380,
      height: 220,
      cardProps: {
        title: "Real Purchasing Power",
        value: 1000000,
        format: "currency_inr",
        subtitle: "Initial Equivalent Worth",
        accentColor: "#F43F5E", // Rose/Danger
      },
    },
    // Continuous Scene Chart Primitive: 10-Year Decay Area Curve
    {
      id: "chart_decay_curve",
      type: "chart",
      layout: "full_bottom",
      width: 1760,
      height: 240,
      chartProps: {
        chartType: "trajectory_area",
        title: "10-Year Wealth Decay Curve",
        subtitle: "Compound 7% Inflation Drag",
        accentColor: "#F43F5E",
        series: [
          {
            id: "inflation_curve",
            name: "Purchasing Power (Real INR)",
            color: "#F43F5E",
            points: [
              { xLabel: "Yr 0", yValue: 1000000 },
              { xLabel: "Yr 2", yValue: 873438 },
              { xLabel: "Yr 4", yValue: 762895 },
              { xLabel: "Yr 6", yValue: 666342 },
              { xLabel: "Yr 8", yValue: 582009 },
              { xLabel: "Yr 10", yValue: 508349 },
            ],
          },
        ],
      },
    },
    {
      id: "connector_inflation_to_power",
      type: "connector",
      connectorProps: {
        fromId: "card_inflation",
        toId: "card_purchasing_power",
        label: "Compounding Decay",
        style: "dashed",
        arrow: true,
      },
    },
  ],
  events: [
    // 1. Spoken Anchor: 'ten lakh' -> Initial savings balance appears
    {
      action: "enter",
      targetId: "card_nominal",
      anchor: "10 lakh",
      startFrame: 14,
      durationFrames: 25,
      style: "fade_slide_up",
    },
    // 2. Spoken Anchor: '7 percent' -> Inflation drag appears on right
    {
      action: "enter",
      targetId: "card_inflation",
      anchor: "7 percent",
      startFrame: 119,
      durationFrames: 25,
      style: "fade_slide_up",
    },
    // 3. Purchasing power enters at bottom left
    {
      action: "enter",
      targetId: "card_purchasing_power",
      startFrame: 135,
      durationFrames: 25,
      style: "fade_slide_up",
    },
    // 4. Trajectory Chart enters at bottom right
    {
      action: "enter",
      targetId: "chart_decay_curve",
      startFrame: 145,
      durationFrames: 30,
      style: "fade_slide_up",
    },
    // 5. Connector draws from inflation to real purchasing power
    {
      action: "connect",
      targetId: "connector_inflation_to_power",
      startFrame: 165,
      durationFrames: 25,
    },
    // 6. Visual State: Inflation card transitions to warning
    {
      action: "change_visual_state",
      targetId: "card_inflation",
      startFrame: 175,
      durationFrames: 15,
      state: "warning",
      badge: "7% DRAG",
    },
    // 7. Purchasing power begins decaying: ₹10,00,000 -> ₹5,08,349 (Verified Provenance)
    {
      action: "transform_number",
      targetId: "card_purchasing_power",
      anchor: "purchasing power",
      startFrame: 195,
      durationFrames: 45,
      toValue: 508349,
      provenance: {
        derived_from: {
          formula: "inflation_decay",
          inputs: { initial: 1000000, rate: 7.0, years: 10 },
        },
      },
    },
    // 8. Text changes to clarify the massive erosion
    {
      action: "transform_text",
      targetId: "card_purchasing_power",
      startFrame: 235,
      durationFrames: 15,
      toText: "-49.2% real wealth eroded",
      toColor: "#F43F5E",
    },
    // 9. Visual State Changes:
    //    - Nominal card dims out of focus
    //    - Purchasing power card transforms to 'eroded' state with dashed decaying border
    {
      action: "change_visual_state",
      targetId: "card_nominal",
      startFrame: 240,
      durationFrames: 20,
      state: "dimmed",
    },
    {
      action: "change_visual_state",
      targetId: "card_purchasing_power",
      startFrame: 255,
      durationFrames: 20,
      state: "eroded",
      badge: "CRITICAL LOSS",
    },
    // 10. Dramatic visual climax: background darkens, chart dominates
    {
      action: "emphasize",
      targetId: "chart_decay_curve",
      startFrame: 260,
      durationFrames: 30,
      darkenBackdrop: 0.5,
      dominant: true,
    },
    // 11. Camera push preserves safe view of all 4 context elements
    {
      action: "camera",
      startFrame: 275,
      durationFrames: 40,
      behavior: "push_in",
      zoom: 1.04,
      requiredContextIds: ["card_nominal", "card_inflation", "card_purchasing_power"],
    },
  ],
};
