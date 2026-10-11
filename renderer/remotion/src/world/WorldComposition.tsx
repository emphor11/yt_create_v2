import React from "react";
import { WorldRenderer } from "./WorldRenderer";
import type { CompiledWorld } from "./compiledWorld";

export interface WorldCompositionProps {
  world: CompiledWorld;
}

/** One Remotion composition for one continuous compiled visual world. */
export const WorldComposition: React.FC<WorldCompositionProps> = ({ world }) => (
  <WorldRenderer world={world} />
);
