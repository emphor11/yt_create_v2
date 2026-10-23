import type { StoryPlan } from "./types.ts";
import loanTimestamps from "../../public/loan_story_timestamps.json" with { type: "json" };

/**
 * Visual Test Plan Demonstrating the 5 Reduced Layouts:
 * 1. full_screen: Real documentary B-roll stock video
 * 2. center: Single dominant hero metric card
 * 3. split_left: Left-side comparison surface (institutional lender)
 * 4. split_right: Right-side comparison surface (interest rate & hike)
 * 5. full_bottom: Wide trajectory area chart with subtitle clearance
 */
export const fiveLayoutsDemoStoryPlan: StoryPlan = {
  id: "five_layouts_reduced_demo",
  fps: 30,
  durationInFrames: 450, // 15 seconds
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
    // 1. full_screen primitive
    {
      id: "doc_broll",
      type: "stock_video",
      layout: "full_screen",
      stockVideoProps: {
        assetId: "assets/commercial_bank_exterior.mp4",
        fit: "cover",
        caption: "Banking Sector Documentary B-Roll",
        alt: "Commercial bank headquarters exterior",
      },
    },
    // 2. center primitive
    {
      id: "hero_loan_card",
      type: "card",
      layout: "center",
      width: 420,
      height: 240,
      cardProps: {
        title: "Home Loan Principal",
        subtitle: "20-Year Baseline Term",
        displayValue: "₹50 Lakh",
        value: 5000000,
        format: "currency_inr",
        accentColor: "#38BDF8",
      },
    },
    // 3. split_left primitive
    {
      id: "bank_image",
      type: "image",
      layout: "split_left",
      width: 640,
      height: 360,
      imageProps: {
        assetId: "assets/bank_building_image.jpg",
        caption: "Institutional Lending Partner",
        fit: "cover",
        borderRadius: 16,
        alt: "Commercial bank exterior",
      },
    },
    // 4. split_right primitive
    {
      id: "rate_card",
      type: "card",
      layout: "split_right",
      width: 420,
      height: 240,
      cardProps: {
        title: "Benchmark Rate",
        subtitle: "Floating Interest Rate",
        displayValue: "8.5%",
        value: 8.5,
        format: "percentage",
        decimals: 1,
        accentColor: "#F59E0B",
      },
    },
    // 5. full_bottom primitive
    {
      id: "interest_trajectory_chart",
      type: "chart",
      layout: "full_bottom",
      width: 1400,
      height: 320,
      chartProps: {
        title: "20-Year Extra Cumulative Interest Trajectory",
        subtitle: "Long-Term Cost Acceleration",
        chartType: "trajectory_area",
        accentColor: "#EF4444",
        series: [
          {
            id: "interest_trajectory",
            name: "Cumulative Extra Interest",
            color: "#EF4444",
            points: [
              { xLabel: "Year 0", yValue: 0 },
              { xLabel: "Year 5", yValue: 3.2 },
              { xLabel: "Year 10", yValue: 7.8 },
              { xLabel: "Year 15", yValue: 11.9 },
              { xLabel: "Year 20", yValue: 15.6 },
            ],
          },
        ],
      },
    },
  ],
  events: [
    // Beat 1: Documentary B-Roll owns entire canvas (full_screen)
    {
      action: "enter",
      targetId: "doc_broll",
      startFrame: 10,
      durationFrames: 1,
      style: "cut",
      anchor: "50 lakh",
    },
    {
      action: "exit",
      targetId: "doc_broll",
      startFrame: 60,
      durationFrames: 1,
      direction: "cut",
      anchor: "starts at",
    },

    // Beat 2: Hero Loan Card in center
    {
      action: "enter",
      targetId: "hero_loan_card",
      startFrame: 65,
      durationFrames: 20,
      style: "fade_slide_up",
      anchor: "starts at",
    },
    {
      action: "exit",
      targetId: "hero_loan_card",
      startFrame: 140,
      durationFrames: 20,
      direction: "fade",
      anchor: "benchmark rate",
    },

    // Beat 3: Split comparison (split_left + split_right)
    {
      action: "enter",
      targetId: "bank_image",
      startFrame: 145,
      durationFrames: 20,
      style: "fade_slide_up",
      anchor: "rises to",
    },
    {
      action: "enter",
      targetId: "rate_card",
      startFrame: 172,
      durationFrames: 20,
      style: "fade_slide_up",
      anchor: "rises to 10.5",
    },
    {
      action: "exit",
      targetId: "bank_image",
      startFrame: 270,
      durationFrames: 20,
      direction: "fade",
      anchor: "surges to",
    },
    {
      action: "exit",
      targetId: "rate_card",
      startFrame: 270,
      durationFrames: 20,
      direction: "fade",
      anchor: "surges to",
    },

    // Beat 4: Wide Evidence Trajectory Chart (full_bottom)
    {
      action: "enter",
      targetId: "interest_trajectory_chart",
      startFrame: 285,
      durationFrames: 25,
      style: "fade_slide_up",
      anchor: "heavy burden",
    },
  ],
};
