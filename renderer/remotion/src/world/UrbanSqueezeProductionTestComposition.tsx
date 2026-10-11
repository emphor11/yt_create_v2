import React from "react";
import rawWorld from "./urbanSqueezeCompiledWorld.json";
import { WorldComposition } from "./WorldComposition";
import type { CompiledWorld } from "./compiledWorld";

const world = rawWorld as unknown as CompiledWorld;

export const UrbanSqueezeProductionTestComposition: React.FC = () => {
  return <WorldComposition world={world} />;
};
