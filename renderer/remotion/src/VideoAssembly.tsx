import { AbsoluteFill, Series, Audio, OffthreadVideo, Img, staticFile, useCurrentFrame, useVideoConfig, interpolate } from "remotion";
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
import { MultiFactorPressure } from "./compositions/MultiFactorPressure";
import { BrollCaption } from "./compositions/BrollCaption";
import { tokens } from "./design-tokens";
import { type VideoAssemblyRenderSpec } from "./types";

export function VideoAssembly(renderSpec: VideoAssemblyRenderSpec) {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const { props, frame_spans = [] } = renderSpec;
  const { scenes, audio } = props;

  // Video progress bar percentage across total duration
  const progressPct = interpolate(frame, [0, durationInFrames || 1], [0, 100], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      {/* Play the narration audio track directly using the static file resolver */}
      {audio && audio.local_path && (
        <Audio src={staticFile(audio.local_path)} />
      )}

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

          return (
            <Series.Sequence
              key={scene.scene_id}
              durationInFrames={scene.duration_frames}
            >
                {/* Render full-screen media at 100% opacity when this scene has an asset */}
                {scene.asset && scene.asset.local_path && (
                  scene.asset.asset_type === "video" ? (
                    <OffthreadVideo
                      src={staticFile(scene.asset.local_path)}
                      style={{ position: "absolute", inset: 0, width: "100%", height: "100%", objectFit: "cover", opacity: 1.0 }}
                      muted
                    />
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
                  {compId === "MultiFactorPressure" && <MultiFactorPressure {...childProps} />}
                  {compId === "BrollCaption" && <BrollCaption {...childProps} />}
                </AbsoluteFill>
            </Series.Sequence>
          );
        })}
      </Series>

      {/* Top-of-screen 4px Glowing Video Progress Bar */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          height: "4px",
          width: `${progressPct}%`,
          background: "linear-gradient(90deg, #06b6d4 0%, #3b82f6 50%, #a855f7 100%)",
          boxShadow: "0 0 12px rgba(6, 182, 212, 0.8)",
          zIndex: 1000,
        }}
      />
    </AbsoluteFill>
  );
}
