import type { StoryPlan } from "./types.ts";
import loanTimestamps from "../../public/loan_story_timestamps.json" with { type: "json" };

/**
 * Vertical Slice Test Plan for Stock Video Primitive.
 *
 * Demonstrates:
 * 1. A normal card before the stock video (Initial Home Loan ₹50 Lakh)
 * 2. A stock_video entering on an exact spoken narration anchor ("rate rises")
 * 3. A hard cut at the enter frame (durationFrames: 0, style: "cut")
 * 4. The stock video occupying the full screen (layout: "full_screen", 1920x1080)
 * 5. Subtitle/caption readability maintained (tint overlay and muted audio)
 * 6. A hard cut out on a later exact narration phrase ("heavy burden", direction: "cut")
 * 7. The next card entering afterward (Monthly EMI Hike ₹49,919)
 * 8. Zero collision and muted OffthreadVideo audio.
 */
export const stockVideoStoryPlan: StoryPlan = {
  id: "stock_video_vertical_slice",
  fps: 30,
  durationInFrames: 505, // 16.8 seconds (loan narration duration)
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
      id: "card_before",
      type: "card",
      layout: "center",
      width: 520,
      height: 320,
      cardProps: {
        title: "Initial Home Loan",
        subtitle: "Principal Sanction",
        displayValue: "₹50 Lakh",
        value: 5000000,
        format: "currency_inr",
        visualState: "normal",
        badge: "8.5% BASE",
        accentColor: "#3B82F6",
      },
    },
    {
      id: "bank_stock_video",
      type: "stock_video",
      layout: "full_screen",
      width: 1920,
      height: 1080,
      stockVideoProps: {
        assetId: "assets/commercial_bank_exterior.mp4",
        fit: "cover",
        alt: "Commercial banking institution exterior",
        caption: "Commercial Banking Institution — Lending Desk",
        overlayTint: "linear-gradient(180deg, rgba(0,0,0,0.2) 0%, rgba(0,0,0,0.55) 100%)",
      },
    },
    {
      id: "card_after",
      type: "card",
      layout: "center",
      width: 520,
      height: 320,
      cardProps: {
        title: "Monthly EMI Hike",
        subtitle: "Revised Outflow",
        displayValue: "₹49,919",
        value: 49919,
        format: "currency_inr",
        visualState: "danger",
        badge: "+₹6,300/mo",
        accentColor: "#EF4444",
      },
    },
  ],
  events: [
    // 1. Card Before enters on spoken phrase "50 lakh" (~0.335s)
    {
      action: "enter",
      targetId: "card_before",
      startFrame: 10,
      durationFrames: 25,
      style: "fade_slide_up",
      anchor: "50 lakh",
    },
    // 2. Card Before exits with hard cut as rate rises (~5.739s)
    {
      action: "exit",
      targetId: "card_before",
      startFrame: 172,
      durationFrames: 0,
      direction: "cut",
      anchor: "rate rises",
    },
    // 3. Stock Video enters with hard cut at exact spoken anchor "rate rises"
    {
      action: "enter",
      targetId: "bank_stock_video",
      startFrame: 172,
      durationFrames: 0,
      style: "cut",
      anchor: "rate rises",
    },
    // 4. Stock Video exits with hard cut at spoken anchor "heavy burden" (~11.0s)
    {
      action: "exit",
      targetId: "bank_stock_video",
      startFrame: 330,
      durationFrames: 0,
      direction: "cut",
      anchor: "heavy burden",
    },
    // 5. Card After enters with smooth animation as stock video cuts out
    {
      action: "enter",
      targetId: "card_after",
      startFrame: 330,
      durationFrames: 25,
      style: "fade_slide_up",
      anchor: "heavy burden",
    },
  ],
};
