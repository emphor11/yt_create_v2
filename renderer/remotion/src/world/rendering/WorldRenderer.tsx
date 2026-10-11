import React, { useMemo } from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";

import type { CompiledWorld } from "../compiledWorld";
import { createWorldRuntime, type WorldRuntime } from "../runtime";
import { WorldObject } from "./WorldObject";

export interface WorldRendererProps {
  world: CompiledWorld;
}

export const WorldRenderer: React.FC<WorldRendererProps> = ({ world }) => {
  const frame = useCurrentFrame();
  const runtime = useMemo<WorldRuntime>(() => createWorldRuntime(world), [world]);

  return (
    <AbsoluteFill
      style={{
        width: world.canvas_config.width,
        height: world.canvas_config.height,
        overflow: "hidden",
        backgroundColor: "#060911",
        background: "radial-gradient(ellipse 95% 75% at 50% 46%, #0b1222 0%, #060913 65%, #020408 100%)",
      }}
    >
      {runtime.roots.map((objectId) => (
        <WorldObject
          key={objectId}
          runtime={runtime}
          objectId={objectId}
          frame={frame}
          parentSpace={{
            width: world.canvas_config.width,
            height: world.canvas_config.height,
          }}
        />
      ))}
    </AbsoluteFill>
  );
};
