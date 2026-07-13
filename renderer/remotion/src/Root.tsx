import { Composition } from "remotion";
import { SplitComparison, type SplitComparisonRenderSpec } from "./SplitComparison";
import { Timeline } from "./Timeline";
import { NumberCounter } from "./NumberCounter";
import { Charts } from "./Charts";
import { StockImage } from "./StockImage";
import { StockVideo } from "./StockVideo";
import { Typography } from "./Typography";
import { IconAnimation } from "./IconAnimation";

const defaultProps: SplitComparisonRenderSpec = {
  scene_id: "scene_01",
  composition: "SplitComparison",
  fps: 30,
  duration_frames: 240,
  props: {
    left: {
      role: "product_price",
      semantic_entity_id: "entity_price",
      label: "Full price",
      raw: "₹80,000",
      value: 80000,
      unit: "INR",
    },
    right: {
      role: "monthly_payment",
      semantic_entity_id: "entity_emi",
      label: "Monthly payment",
      raw: "₹6,667",
      value: 6667,
      unit: "INR",
    },
    attention_shift_event_id: "event_attention_shift",
  },
  frame_spans: [
    {
      event_id: "event_full_price",
      start_frame: 0,
      end_frame: 80,
      duration_frames: 80,
    },
    {
      event_id: "event_monthly_payment",
      start_frame: 80,
      end_frame: 160,
      duration_frames: 80,
    },
    {
      event_id: "event_attention_shift",
      start_frame: 160,
      end_frame: 240,
      duration_frames: 80,
    },
  ],
};

export function RemotionRoot() {
  return (
    <>
      <Composition
        id="SplitComparison"
        component={SplitComparison}
        durationInFrames={240}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={defaultProps}
      />
      <Composition
        id="Timeline"
        component={Timeline}
        durationInFrames={240}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={defaultProps}
      />
      <Composition
        id="NumberCounter"
        component={NumberCounter}
        durationInFrames={240}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={defaultProps}
      />
      <Composition
        id="Charts"
        component={Charts}
        durationInFrames={240}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={defaultProps}
      />
      <Composition
        id="Stock Image"
        component={StockImage}
        durationInFrames={240}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={defaultProps}
      />
      <Composition
        id="Stock Video"
        component={StockVideo}
        durationInFrames={240}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={defaultProps}
      />
      <Composition
        id="Typography"
        component={Typography}
        durationInFrames={240}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={defaultProps}
      />
      <Composition
        id="Icon Animation"
        component={IconAnimation}
        durationInFrames={240}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={defaultProps}
      />
    </>
  );
}
