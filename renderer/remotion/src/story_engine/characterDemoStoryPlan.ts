import type { StoryPlan } from "./types.ts";
import characterTimestamps from "../../public/character_story_timestamps.json" with { type: "json" };

/**
 * Character Demo Story: Salaried Worker vs Inflation Wealth Deficit.
 *
 * Story:
 * "A salaried employee saves diligently every single month.
 * At first, a conservative fixed return feels completely safe...
 * ...until persistent inflation begins eroding real purchasing power.
 * ...leaving them facing a thirty lakh wealth deficit over time."
 *
 * Showcase Capabilities:
 * 1. Minimal Futuristic Character Primitive (SVG/React, zero external image assets):
 *    - Visor glow adapting to emotion (neutral -> focused -> concerned).
 *    - 15 skeletal joints smoothly interpolating between poses over 20 frames.
 *    - Clean floor pedestal and non-flipped role badge.
 * 2. Visual Narrative Arc:
 *    - Frame ~20: Character enters in idle pose facing right.
 *    - Frame ~150: Character points toward the initial savings deposit.
 *    - Frame ~290: Character switches to 'think' pose as inflation connector emerges.
 *    - Frame ~385: Character transforms to 'worried' pose as the 30L wealth deficit card hits.
 * 3. Real Audible Narration:
 *    - Mounted via <Audio src="character_narration.mp3" />
 *    - Word-level synchronization with speech timestamps.
 */
export const characterDemoStoryPlan: StoryPlan = {
  id: "character_inflation_deficit_story",
  fps: 30,
  durationInFrames: 440, // 14.6 seconds, matching narration
  width: 1920,
  height: 1080,
  safeMargin: 80,
  audioFileName: "character_narration.mp3",
  narration: {
    text: characterTimestamps.full_text,
    audioFile: characterTimestamps.audio_file,
    wordTimestamps: characterTimestamps.word_timestamps,
  },
  objects: [
    // 1. Futuristic Stick Character Primitive
    {
      id: "worker",
      type: "character",
      layout: "center_left",
      width: 240,
      height: 360,
      characterProps: {
        style: "futuristic_stick",
        role: "Salaried Investor",
        label: "Salaried Employee",
        pose: "idle",
        emotion: "neutral",
        facing: "right",
        accentColor: "#38BDF8", // Cyan
      },
    },

    // 2. Safe Fixed Return Deposit Card (Center Right)
    {
      id: "card_savings",
      type: "card",
      layout: "center_right",
      width: 420,
      height: 200,
      cardProps: {
        title: "Conservative Fixed Return",
        subtitle: "Nominal 6.5% Guaranteed APY",
        value: 2500000,
        displayValue: "₹25,00,000",
        format: "currency_inr",
        accentColor: "#38BDF8",
      },
    },

    // 3. Persistent Inflation Card (Top Right)
    {
      id: "card_inflation",
      type: "card",
      layout: "top_right",
      width: 420,
      height: 180,
      cardProps: {
        title: "Annual Inflation",
        subtitle: "Silent Value Erosion",
        value: 7.0,
        displayValue: "7.0%",
        format: "plain",
        accentColor: "#F59E0B", // Amber
      },
    },

    // 4. Real Wealth Deficit Card (Bottom Right)
    {
      id: "card_deficit",
      type: "card",
      layout: "bottom_right",
      width: 420,
      height: 190,
      cardProps: {
        title: "Real Wealth Deficit",
        subtitle: "30-Year Purchasing Gap",
        value: -3000000,
        displayValue: "-₹30,00,000",
        format: "currency_inr",
        accentColor: "#EF4444", // Red
      },
    },

    // 5. Connector: Inflation -> Savings
    {
      id: "conn_inflation_savings",
      type: "connector",
      layout: "center",
      connectorProps: {
        fromId: "card_inflation",
        toId: "card_savings",
        label: "Erodes Real Value",
        style: "dashed",
        arrow: true,
      },
    },
  ],
  events: [
    // Beat 1: "A salaried employee..."
    {
      action: "enter",
      targetId: "worker",
      startFrame: 10,
      durationFrames: 20,
      style: "fade_slide_up",
      anchor: "salaried employee",
    },

    // Beat 2: "...saves diligently every single month"
    {
      action: "enter",
      targetId: "card_savings",
      startFrame: 35,
      durationFrames: 20,
      style: "fade_slide_up",
      anchor: "saves diligently",
    },

    // Beat 3: "At first, a conservative fixed return feels completely safe..."
    {
      action: "change_pose",
      targetId: "worker",
      startFrame: 145,
      durationFrames: 20,
      pose: "point",
      emotion: "focused",
      facing: "right",
      anchor: "conservative fixed return",
    },
    {
      action: "highlight",
      targetId: "card_savings",
      startFrame: 155,
      durationFrames: 30,
      color: "#38BDF8",
      variant: "glow",
      anchor: "feels completely safe",
    },

    // Beat 4: "...until persistent inflation begins eroding real purchasing power"
    {
      action: "enter",
      targetId: "card_inflation",
      startFrame: 220,
      durationFrames: 20,
      style: "fade_slide_up",
      anchor: "persistent inflation",
    },
    {
      action: "connect",
      targetId: "conn_inflation_savings",
      startFrame: 258,
      durationFrames: 25,
      anchor: "begins eroding",
    },
    {
      action: "change_pose",
      targetId: "worker",
      startFrame: 285,
      durationFrames: 20,
      pose: "think",
      emotion: "concerned",
      facing: "right",
      anchor: "purchasing power",
    },

    // Beat 5: "...leaving them facing a thirty lakh wealth deficit over time"
    {
      action: "enter",
      targetId: "card_deficit",
      startFrame: 325,
      durationFrames: 20,
      style: "fade_slide_up",
      anchor: "leaving them facing",
    },
    {
      action: "change_visual_state",
      targetId: "card_deficit",
      startFrame: 360,
      durationFrames: 25,
      state: "danger",
      badge: "CRITICAL DEFICIT",
      anchor: "thirty lakh",
    },
    {
      action: "change_pose",
      targetId: "worker",
      startFrame: 380,
      durationFrames: 20,
      pose: "worried",
      emotion: "concerned",
      facing: "right",
      anchor: "wealth deficit",
    },
    {
      action: "highlight",
      targetId: "worker",
      startFrame: 395,
      durationFrames: 35,
      color: "#EF4444",
      variant: "pulse",
      anchor: "over time",
    },
  ],
};
