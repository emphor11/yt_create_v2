import { AbsoluteFill, Series, Audio, Loop, OffthreadVideo, Img, staticFile, useVideoConfig, useCurrentFrame, interpolate } from "remotion";
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
import { CauseEffect } from "./compositions/CauseEffect";
import { TimeDecay } from "./compositions/TimeDecay";
import { GrowthTrajectory } from "./compositions/GrowthTrajectory";
import { MultiFactorPressure } from "./compositions/MultiFactorPressure";
import { BrollCaption } from "./compositions/BrollCaption";
import { TrajectoryDivergence } from "./compositions/TrajectoryDivergence";
import { CashFlowWaterfall } from "./compositions/CashFlowWaterfall";
import { AccumulationDecomposition } from "./compositions/AccumulationDecomposition";
import { DebtAmortizationSchedule } from "./compositions/DebtAmortizationSchedule";
import { type VideoAssemblyRenderSpec } from "./types";
import { getMediaLoopDurationInFrames } from "./media-playback";

export function VideoAssembly(renderSpec: VideoAssemblyRenderSpec) {
  const { props, frame_spans = [] } = renderSpec;
  const { scenes, audio } = props;

  const frame = useCurrentFrame();
  const { durationInFrames, fps } = useVideoConfig();

  // --- Background Music ---
  // Professional standard: BGM at ~8% volume sits as texture under narration.
  // Fades in over 1s at start, fades out over 1.5s before the end.
  const BGM_VOLUME = 0.08;
  const FADE_IN_FRAMES = Math.round(fps * 4.0);   // 4 second fade in
  const FADE_OUT_FRAMES = Math.round(fps * 4.0);  // 4 second fade out
  const fadeOutStart = durationInFrames - FADE_OUT_FRAMES;

  const bgmVolume = interpolate(
    frame,
    [0, FADE_IN_FRAMES, fadeOutStart, durationInFrames],
    [0, BGM_VOLUME, BGM_VOLUME, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      {/* Narration voice track */}
      {audio && audio.local_path && (
        <Audio src={staticFile(audio.local_path)} />
      )}

      {/* Background music — looped, subtle, fades in/out */}
      <Audio
        src={staticFile("music/Voxscape.mp3")}
        loop
        volume={bgmVolume}
      />

      <Series>
        {scenes.map((scene) => {
          const compId = scene.component.component_id;
          const isStockMedia = compId === "StockVideo" || compId === "StockImage";
          
          // Reconstruct standard composition props
          const childProps = {
            scene_id: scene.scene_id,
            composition: compId,
            fps: 30,
            duration_frames: scene.duration_frames,
            props: scene.component.props,
            frame_spans: frame_spans
          };
          const assetLoopDurationInFrames = getMediaLoopDurationInFrames(
            scene.asset?.asset_type === "video" ? scene.asset.duration_seconds : null,
            fps,
          );
          const sceneVideo = scene.asset && scene.asset.local_path ? (
            <OffthreadVideo
              src={staticFile(scene.asset.local_path)}
              style={{ position: "absolute", inset: 0, width: "100%", height: "100%", objectFit: "cover", opacity: 1.0 }}
              muted
            />
          ) : null;

          return (
            <Series.Sequence
              key={scene.scene_id}
              durationInFrames={scene.duration_frames}
            >
                {/* Render full-screen media at 100% opacity when this scene has an asset */}
                {scene.asset && scene.asset.local_path && (
                  scene.asset.asset_type === "video" ? (
                    assetLoopDurationInFrames ? (
                      <Loop durationInFrames={assetLoopDurationInFrames}>
                        {sceneVideo}
                      </Loop>
                    ) : sceneVideo
                  ) : (
                    <Img
                      src={staticFile(scene.asset.local_path)}
                      style={{ position: "absolute", inset: 0, width: "100%", height: "100%", objectFit: "cover", opacity: 1.0 }}
                    />
                  )
                )}

                <AbsoluteFill style={{ position: "relative" }}>
                  {compId === "SplitComparison" && <SplitComparison {...childProps} />}
                  {compId === "Typography" && <Typography {...childProps} />}
                  {compId === "StockVideo" && <StockVideo {...childProps} />}
                  {compId === "StockImage" && <StockImage {...childProps} />}
                  {compId === "Timeline" && <Timeline {...childProps} />}
                  {compId === "ProcessFlow" && <ProcessFlow {...childProps} />}
                  {compId === "KPIGrid" && <KPIGrid {...childProps} />}
                  {compId === "ProgressiveList" && <ProgressiveList {...childProps} />}
                  {compId === "RankedList" && <RankedList {...childProps} />}
                  {compId === "DataTable" && <DataTable {...childProps} />}
                  {compId === "BeforeAfter" && <BeforeAfter {...childProps} />}
                  {compId === "QuoteCallout" && <QuoteCallout {...childProps} />}
                  {compId === "NumberCounter" && <NumberCounter {...childProps} />}
                  {compId === "Charts" && <Charts {...childProps} />}
                  {compId === "IconAnimation" && <IconAnimation {...childProps} />}

                  {/* Composition Pipeline Compositions */}
                  {compId === "MetricHero" && <MetricHero {...childProps} />}
                  {compId === "CalculationStory" && <CalculationStory {...childProps} />}
                  {compId === "CauseEffect" && <CauseEffect {...childProps} />}
                  {compId === "TimeDecay" && <TimeDecay {...childProps} />}
                  {compId === "GrowthTrajectory" && <GrowthTrajectory {...childProps} />}
                  {compId === "MultiFactorPressure" && <MultiFactorPressure {...childProps} />}
                  {compId === "BrollCaption" && <BrollCaption {...childProps} />}
                  {compId === "TrajectoryDivergence" && <TrajectoryDivergence {...childProps} />}
                  {compId === "CashFlowWaterfall" && <CashFlowWaterfall {...childProps} />}
                  {compId === "AccumulationDecomposition" && <AccumulationDecomposition {...childProps} />}
                  {compId === "DebtAmortizationSchedule" && <DebtAmortizationSchedule {...childProps} />}
                </AbsoluteFill>
            </Series.Sequence>
          );
        })}
      </Series>
    </AbsoluteFill>
  );
}
