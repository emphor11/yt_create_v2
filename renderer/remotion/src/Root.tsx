import { Composition } from "remotion";
import { SplitComparison } from "./SplitComparison";
import { Timeline } from "./Timeline";
import { ProcessFlow } from "./ProcessFlow";
import { KPIGrid } from "./KPIGrid";
import { ProgressiveList } from "./ProgressiveList";
import { RankedList } from "./RankedList";
import { DataTable } from "./DataTable";
import { BeforeAfter } from "./BeforeAfter";
import { QuoteCallout } from "./QuoteCallout";
import { NumberCounter } from "./NumberCounter";
import { Charts } from "./Charts";
import { StockImage } from "./StockImage";
import { StockVideo } from "./StockVideo";
import { Typography } from "./Typography";
import { IconAnimation } from "./IconAnimation";
import { MetricHero } from "./compositions/MetricHero";
import { CalculationStory } from "./compositions/CalculationStory";
import { TimeDecay } from "./compositions/TimeDecay";
import { GrowthTrajectory } from "./compositions/GrowthTrajectory";
import { CauseEffect } from "./compositions/CauseEffect";
import { MultiFactorPressure } from "./compositions/MultiFactorPressure";
import { BrollCaption } from "./compositions/BrollCaption";
import { TrajectoryDivergence } from "./compositions/TrajectoryDivergence";
import { CashFlowWaterfall } from "./compositions/CashFlowWaterfall";
import { AccumulationDecomposition } from "./compositions/AccumulationDecomposition";
import { DebtAmortizationSchedule } from "./compositions/DebtAmortizationSchedule";
import { ValueFlowNetwork } from "./compositions/ValueFlowNetwork";
import { CausalChain } from "./compositions/CausalChain";
import { StateTransition } from "./compositions/StateTransition";
import { RangeThreshold } from "./compositions/RangeThreshold";
import { TimelineMilestone } from "./compositions/TimelineMilestone";
import { VideoAssembly } from "./VideoAssembly";
import { Thumbnail, defaultThumbnailProps } from "./Thumbnail";
import { type SplitComparisonRenderSpec, type VideoAssemblyRenderSpec } from "./types";
import { StoryScene } from "./story_engine/StoryScene";
import { loanStoryPlan } from "./story_engine/loanStoryPlan";
import { inflationStoryPlan } from "./story_engine/inflationStoryPlan";
import { salarySplitStoryPlan } from "./story_engine/salarySplitStoryPlan";
import { characterDemoStoryPlan } from "./story_engine/characterDemoStoryPlan";
import { splitScreenStoryPlan } from "./story_engine/splitScreenStoryPlan";
import { stockVideoStoryPlan } from "./story_engine/stockVideoStoryPlan";
import { fiveLayoutsDemoStoryPlan } from "./story_engine/fiveLayoutsDemoStoryPlan";


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
        component={SplitComparison as any}
        durationInFrames={240}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{} as any}
      />
      <Composition
        id="Timeline"
        component={Timeline as any}
        durationInFrames={240}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={defaultProps as any}
      />
      <Composition
        id="ProcessFlow"
        component={ProcessFlow as any}
        durationInFrames={240}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{} as any}
      />
      <Composition
        id="KPIGrid"
        component={KPIGrid as any}
        durationInFrames={240}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={defaultProps as any}
      />
      <Composition
        id="ProgressiveList"
        component={ProgressiveList as any}
        durationInFrames={240}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={defaultProps as any}
      />
      <Composition
        id="RankedList"
        component={RankedList as any}
        durationInFrames={240}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{} as any}
      />
      <Composition
        id="DataTable"
        component={DataTable as any}
        durationInFrames={240}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={defaultProps as any}
      />
      <Composition
        id="BeforeAfter"
        component={BeforeAfter as any}
        durationInFrames={240}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={defaultProps as any}
      />
      <Composition
        id="QuoteCallout"
        component={QuoteCallout as any}
        durationInFrames={240}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={defaultProps as any}
      />
      <Composition
        id="NumberCounter"
        component={NumberCounter as any}
        durationInFrames={240}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={defaultProps as any}
      />
      <Composition
        id="Charts"
        component={Charts as any}
        durationInFrames={240}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={defaultProps as any}
      />
      <Composition
        id="StockImage"
        component={StockImage as any}
        durationInFrames={240}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={defaultProps as any}
      />
      <Composition
        id="StockVideo"
        component={StockVideo as any}
        durationInFrames={240}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={defaultProps as any}
      />
      <Composition
        id="Typography"
        component={Typography as any}
        durationInFrames={240}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={defaultProps as any}
      />
      <Composition
        id="IconAnimation"
        component={IconAnimation as any}
        durationInFrames={240}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={defaultProps as any}
      />
      <Composition
        id="MetricHero"
        component={MetricHero as any}
        durationInFrames={180}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{} as any}
      />
      <Composition
        id="CalculationStory"
        component={CalculationStory as any}
        durationInFrames={180}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{} as any}
      />
      <Composition
        id="TimeDecay"
        component={TimeDecay as any}
        durationInFrames={180}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{} as any}
      />
      <Composition
        id="GrowthTrajectory"
        component={GrowthTrajectory as any}
        durationInFrames={180}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{} as any}
      />
      <Composition
        id="TrajectoryDivergence"
        component={TrajectoryDivergence as any}
        durationInFrames={180}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{} as any}
      />
      <Composition
        id="CashFlowWaterfall"
        component={CashFlowWaterfall as any}
        durationInFrames={180}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{} as any}
      />
      <Composition
        id="AccumulationDecomposition"
        component={AccumulationDecomposition as any}
        durationInFrames={180}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{} as any}
      />
      <Composition
        id="DebtAmortizationSchedule"
        component={DebtAmortizationSchedule as any}
        durationInFrames={180}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{} as any}
      />
      <Composition
        id="CauseEffect"
        component={CauseEffect as any}
        durationInFrames={180}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{} as any}
      />
      <Composition
        id="MultiFactorPressure"
        component={MultiFactorPressure as any}
        durationInFrames={180}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{} as any}
      />
      <Composition
        id="BrollCaption"
        component={BrollCaption as any}
        durationInFrames={180}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{} as any}
      />
      <Composition
        id="ValueFlowNetwork"
        component={ValueFlowNetwork as any}
        durationInFrames={180}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{} as any}
      />
      <Composition
        id="CausalChain"
        component={CausalChain as any}
        durationInFrames={180}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{} as any}
      />
      <Composition
        id="StateTransition"
        component={StateTransition as any}
        durationInFrames={180}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{} as any}
      />
      <Composition
        id="RangeThreshold"
        component={RangeThreshold as any}
        durationInFrames={180}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{} as any}
      />
      <Composition
        id="TimelineMilestone"
        component={TimelineMilestone as any}
        durationInFrames={180}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{} as any}
      />
      <Composition
        id="VideoAssembly"
        component={VideoAssembly as any}
        durationInFrames={18000}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={defaultAssemblyProps as any}
      />
      <Composition
        id="Thumbnail"
        component={Thumbnail as any}
        durationInFrames={1}
        fps={30}
        width={1280}
        height={720}
        defaultProps={defaultThumbnailProps as any}
      />
      <Composition
        id="StoryScene"
        component={StoryScene as any}
        durationInFrames={loanStoryPlan.durationInFrames}
        fps={loanStoryPlan.fps}
        width={loanStoryPlan.width}
        height={loanStoryPlan.height}
        defaultProps={{ plan: loanStoryPlan } as any}
        calculateMetadata={({ props }) => {
          const plan = (props as any)?.plan;
          return {
            durationInFrames: plan?.durationInFrames ?? loanStoryPlan.durationInFrames,
            fps: plan?.fps ?? loanStoryPlan.fps,
            width: plan?.width ?? loanStoryPlan.width,
            height: plan?.height ?? loanStoryPlan.height,
          };
        }}
      />
      <Composition
        id="InflationStoryScene"
        component={StoryScene as any}
        durationInFrames={inflationStoryPlan.durationInFrames}
        fps={inflationStoryPlan.fps}
        width={inflationStoryPlan.width}
        height={inflationStoryPlan.height}
        defaultProps={{ plan: inflationStoryPlan } as any}
      />
      <Composition
        id="SalarySplitStoryScene"
        component={StoryScene as any}
        durationInFrames={salarySplitStoryPlan.durationInFrames}
        fps={salarySplitStoryPlan.fps}
        width={salarySplitStoryPlan.width}
        height={salarySplitStoryPlan.height}
        defaultProps={{ plan: salarySplitStoryPlan } as any}
      />
      <Composition
        id="CharacterStoryScene"
        component={StoryScene as any}
        durationInFrames={characterDemoStoryPlan.durationInFrames}
        fps={characterDemoStoryPlan.fps}
        width={characterDemoStoryPlan.width}
        height={characterDemoStoryPlan.height}
        defaultProps={{ plan: characterDemoStoryPlan } as any}
      />
      <Composition
        id="SplitScreenStoryScene"
        component={StoryScene as any}
        durationInFrames={splitScreenStoryPlan.durationInFrames}
        fps={splitScreenStoryPlan.fps}
        width={splitScreenStoryPlan.width}
        height={splitScreenStoryPlan.height}
        defaultProps={{ plan: splitScreenStoryPlan } as any}
      />
      <Composition
        id="StockVideoStoryScene"
        component={StoryScene as any}
        durationInFrames={stockVideoStoryPlan.durationInFrames}
        fps={stockVideoStoryPlan.fps}
        width={stockVideoStoryPlan.width}
        height={stockVideoStoryPlan.height}
        defaultProps={{ plan: stockVideoStoryPlan } as any}
      />
      <Composition
        id="FiveLayoutsDemoStoryScene"
        component={StoryScene as any}
        durationInFrames={fiveLayoutsDemoStoryPlan.durationInFrames}
        fps={fiveLayoutsDemoStoryPlan.fps}
        width={fiveLayoutsDemoStoryPlan.width}
        height={fiveLayoutsDemoStoryPlan.height}
        defaultProps={{ plan: fiveLayoutsDemoStoryPlan } as any}
      />
    </>
  );
}

const defaultAssemblyProps = {
  scene_id: "assembly_scene",
  composition: "VideoAssembly",
  fps: 30,
  duration_frames: 240,
  props: {
    scenes: [
      {
        scene_id: "mock_scene_01",
        start_frame: 0,
        end_frame: 240,
        duration_frames: 240,
        component: {
          component_id: "Typography",
          props: {
            left: { label: "Typography Mock", raw: "Mock Left" },
            right: { label: "Key Idea", raw: "Mock Right" }
          }
        },
        asset: null,
        narration_text: "Mock text"
      }
    ],
    audio: {
      audio_file_name: "narration.mp3",
      local_path: "",
      duration_seconds: 8.0
    }
  },
  frame_spans: []
};
