import { AbsoluteFill, Series, Audio, Video, Img, staticFile } from "remotion";
import { SplitComparison } from "./SplitComparison";
import { Timeline } from "./Timeline";
import { NumberCounter } from "./NumberCounter";
import { Charts } from "./Charts";
import { StockImage } from "./StockImage";
import { StockVideo } from "./StockVideo";
import { Typography } from "./Typography";
import { IconAnimation } from "./IconAnimation";

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

export function VideoAssembly({ props }: VideoAssemblyRenderSpec) {
  const { scenes, audio } = props;

  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      {/* Play the narration audio track directly using the static file resolver */}
      {audio && audio.local_path && (
        <Audio src={staticFile(audio.local_path)} />
      )}

      <Series>
        {scenes.map((scene) => {
          const compId = scene.component.component_id;
          
          // Reconstruct standard composition props
          const childProps = {
            scene_id: scene.scene_id,
            composition: compId,
            fps: 30,
            duration_frames: scene.duration_frames,
            props: scene.component.props,
            frame_spans: []
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
                    style={{ position: "absolute", inset: 0, width: "100%", height: "100%", objectFit: "cover", opacity: 0.3 }}
                    loop
                    muted
                  />
                )}
                {scene.asset && scene.asset.asset_type === "image" && scene.asset.local_path && (
                  <Img
                    src={staticFile(scene.asset.local_path)}
                    style={{ position: "absolute", inset: 0, width: "100%", height: "100%", objectFit: "cover", opacity: 0.3 }}
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
    </AbsoluteFill>
  );
}
