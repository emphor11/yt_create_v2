import type { StoryPlan } from "./types.ts";
import loanTimestamps from "../../public/loan_story_timestamps.json" with { type: "json" };

/**
 * Visual Test Plan for Left-Right Split-Screen Layout Mode.
 *
 * Demonstrates:
 * - Left-side bank image in split_left
 * - Right-side interest card in split_right
 * - Narration-synchronized entrance events
 * - Zero collision (separated by x=960 conceptual divider)
 * - Visible debug divider line only in debug mode (debug: true)
 */
export const splitScreenStoryPlan: StoryPlan = {
  id: "split_screen_visual_test",
  fps: 30,
  durationInFrames: 505, // 16.8 seconds
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
      id: "bank_image",
      type: "image",
      layout: "split_left",
      width: 640,
      height: 360,
      imageProps: {
        assetId: "assets/bank_building_image.jpg",
        caption: "Commercial Banking Partner",
        fit: "cover",
        borderRadius: 16,
        alt: "Modern banking institution building exterior",
      },
    },
    {
      id: "interest_card",
      type: "card",
      layout: "split_right",
      width: 420,
      height: 240,
      cardProps: {
        title: "Cumulative Interest",
        subtitle: "20-Year Extra Burden",
        displayValue: "₹15.6 Lakh",
        value: 1560000,
        format: "currency_inr",
        visualState: "danger",
        badge: "+2.0% HIKE",
        accentColor: "#EF4444",
      },
    },
  ],
  events: [
    {
      action: "enter",
      targetId: "bank_image",
      startFrame: 10, // Anchor "50 lakh" (~0.335s)
      durationFrames: 25,
      style: "fade_slide_up",
      anchor: "50 lakh",
    },
    {
      action: "enter",
      targetId: "interest_card",
      startFrame: 172, // Anchor "rises to 10.5" (~5.739s)
      durationFrames: 25,
      style: "fade_slide_up",
      anchor: "rises to 10.5",
    },
  ],
};
