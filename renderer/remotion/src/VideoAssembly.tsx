import { AbsoluteFill, Series, Audio, Video, Img, staticFile, useCurrentFrame, useVideoConfig, interpolate } from "remotion";
import { SplitComparison } from "./SplitComparison";
import { Timeline } from "./Timeline";
import { NumberCounter } from "./NumberCounter";
import { Charts } from "./Charts";
import { StockImage } from "./StockImage";
import { StockVideo } from "./StockVideo";
import { Typography } from "./Typography";
import { IconAnimation } from "./IconAnimation";
import { tokens } from "./design-tokens";

interface AssetReference {
  asset_id: string;
  asset_type: "image" | "video";
  source: string;
  query: string;
  local_path: string;
  url: string | null;
  asset_status: string;
}

interface ComponentSpec {
  component_id: string;
  props: any;
}

interface SceneSpec {
  scene_id: string;
  start_frame: number;
  end_frame: number;
  duration_frames: number;
  component: ComponentSpec;
  asset: AssetReference | null;
  narration_text: string | null;
}

interface AudioSpec {
  audio_file_name: string;
  local_path: string;
  duration_seconds: number;
}

export interface VideoAssemblyRenderSpec {
  scene_id: string;
  composition: string;
  fps: number;
  duration_frames: number;
  props: {
    scenes: SceneSpec[];
    audio: AudioSpec;
  };
}

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
          // Tuned B-roll opacity so background footage is clearly visible behind glass cards
          const assetOpacity = (compId === "StockVideo" || compId === "StockImage") ? 0.90 : 0.65;
          
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
              <AbsoluteFill>
                {/* Render resolved background stock asset if present */}
                {scene.asset && scene.asset.asset_type === "video" && scene.asset.local_path && (
                  <Video
                    src={staticFile(scene.asset.local_path)}
                    style={{ position: "absolute", inset: 0, width: "100%", height: "100%", objectFit: "cover", opacity: assetOpacity }}
                    loop
                    muted
                  />
                )}
                {scene.asset && scene.asset.asset_type === "image" && scene.asset.local_path && (
                  <Img
                    src={staticFile(scene.asset.local_path)}
                    style={{ position: "absolute", inset: 0, width: "100%", height: "100%", objectFit: "cover", opacity: assetOpacity }}
                  />
                )}

                <AbsoluteFill style={{ position: "relative" }}>
                  {compId === "SplitComparison" && <SplitComparison {...childProps} />}
                  {compId === "Typography" && <Typography {...childProps} />}
                  {compId === "StockVideo" && <StockVideo {...childProps} />}
                  {compId === "StockImage" && <StockImage {...childProps} />}
                  {compId === "Timeline" && <Timeline {...childProps} />}
                  {compId === "NumberCounter" && <NumberCounter {...childProps} />}
                  {compId === "Charts" && <Charts {...childProps} />}
                  {compId === "IconAnimation" && <IconAnimation {...childProps} />}
                </AbsoluteFill>
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
