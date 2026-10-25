import React, { useMemo } from "react";
import { Sequence, Audio, staticFile } from "remotion";
import type { StoryPlan } from "../types.ts";
import { generateSoundCues, SoundCue, SoundEffectType, SFX_CONFIG } from "./sfxEngine.ts";

export { generateSoundCues, SFX_CONFIG };
export type { SoundCue, SoundEffectType };

export interface SoundEffectsLayerProps {
  plan: StoryPlan;
  volumeMultiplier?: number;
}

export const SoundEffectsLayer: React.FC<SoundEffectsLayerProps> = ({
  plan,
  volumeMultiplier = 1.0,
}) => {
  const cues = useMemo(() => generateSoundCues(plan), [plan]);

  return (
    <>
      {cues.map((cue) => {
        const finalVolume = Math.max(0, Math.min(1.0, cue.volume * volumeMultiplier));
        return (
          <Sequence
            key={cue.id}
            from={cue.frame}
            durationInFrames={cue.durationFrames}
            layout="none"
          >
            <Audio
              src={staticFile(`assets/sfx/${cue.file}`)}
              volume={finalVolume}
            />
          </Sequence>
        );
      })}
    </>
  );
};
