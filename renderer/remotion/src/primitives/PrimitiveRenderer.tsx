import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { type PrimitiveTreeSpec } from "./types";
import { renderPrimitiveNode } from "./registry";

export interface PrimitiveRendererProps {
  tree: PrimitiveTreeSpec;
}

export const PrimitiveRenderer: React.FC<PrimitiveRendererProps> = ({ tree }) => {
  const currentFrame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const rootIds = tree.root_primitive_ids || [];
  const rootSpecs = rootIds
    .map((id) => tree.primitives[id])
    .filter(Boolean)
    .sort((a, b) => (a.identity.z_index ?? 0) - (b.identity.z_index ?? 0));

  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#060911",
        overflow: "hidden",
        width: "100%",
        height: "100%",
        fontFamily: "Inter, ui-sans-serif, system-ui, sans-serif",
      }}
    >
      {rootSpecs.map((spec) => renderPrimitiveNode(spec, tree, currentFrame, fps))}
    </AbsoluteFill>
  );
};
