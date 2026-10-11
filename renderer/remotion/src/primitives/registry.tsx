import React from "react";
import { type CanonicalCapabilityType, type PrimitiveSpec, type PrimitiveTreeSpec } from "./types";
import { evaluatePrimitiveEntrance } from "./animation";

import { PrimitiveText } from "./PrimitiveText";
import { PrimitiveNumber } from "./PrimitiveNumber";
import { PrimitiveShape } from "./PrimitiveShape";
import { PrimitiveIcon } from "./PrimitiveIcon";
import { PrimitiveConnector } from "./PrimitiveConnector";
import { PrimitiveImage } from "./PrimitiveImage";
import { PrimitiveVideo } from "./PrimitiveVideo";
import { PrimitiveBar } from "./PrimitiveBar";
import { PrimitiveLine } from "./PrimitiveLine";
import { PrimitivePoint } from "./PrimitivePoint";
import { PrimitiveSegment } from "./PrimitiveSegment";
import { PrimitiveProgress } from "./PrimitiveProgress";
import { PrimitiveGroup } from "./PrimitiveGroup";

export const CANONICAL_CAPABILITY_TYPES: readonly CanonicalCapabilityType[] = [
  "text",
  "number",
  "shape",
  "icon",
  "connector",
  "image",
  "video",
  "bar",
  "line",
  "point",
  "segment",
  "progress",
  "group",
] as const;

export const PRIMITIVE_REGISTRY: Record<CanonicalCapabilityType, React.FC<any>> = {
  text: PrimitiveText,
  number: PrimitiveNumber,
  shape: PrimitiveShape,
  icon: PrimitiveIcon,
  connector: PrimitiveConnector,
  image: PrimitiveImage,
  video: PrimitiveVideo,
  bar: PrimitiveBar,
  line: PrimitiveLine,
  point: PrimitivePoint,
  segment: PrimitiveSegment,
  progress: PrimitiveProgress,
  group: PrimitiveGroup,
};

export function renderPrimitiveNode(
  spec: PrimitiveSpec,
  tree: PrimitiveTreeSpec | undefined,
  currentFrame: number,
  fps: number = 30
): React.ReactNode {
  const { identity, timing = {}, layout = {} } = spec;

  // 1. Visibility & Timing check
  if (timing.visible === false) {
    return null;
  }

  const enterFrame = timing.enter_frame ?? 0;
  if (currentFrame < enterFrame) {
    return null;
  }

  if (timing.exit_frame !== undefined && timing.exit_frame !== null && currentFrame >= timing.exit_frame) {
    return null;
  }

  // 2. Lookup Component
  const Component = PRIMITIVE_REGISTRY[identity.type];
  if (!Component) {
    console.warn(`[PrimitiveRegistry] Unknown primitive type '${identity.type}'.`);
    return null;
  }

  // 3. Evaluate basic entrance spring
  const { opacity: entranceOpacity, scale: entranceScale } = evaluatePrimitiveEntrance(
    enterFrame,
    currentFrame,
    fps
  );

  const isPositioned = layout.position_mode === "absolute";
  const margin = layout.margin;

  // Render Connector and Group directly (they manage their own coordinate envelopes)
  if (identity.type === "connector" || identity.type === "group") {
    return (
      <React.Fragment key={identity.id}>
        <Component spec={spec} tree={tree} currentFrame={currentFrame} fps={fps} />
      </React.Fragment>
    );
  }

  return (
    <div
      key={identity.id}
      style={{
        position: isPositioned ? "absolute" : "relative",
        left: layout.x !== undefined && layout.x !== null ? `${layout.x}px` : undefined,
        top: layout.y !== undefined && layout.y !== null ? `${layout.y}px` : undefined,
        width: layout.width !== undefined && layout.width !== null ? (typeof layout.width === "number" ? `${layout.width}px` : layout.width) : undefined,
        height: layout.height !== undefined && layout.height !== null ? (typeof layout.height === "number" ? `${layout.height}px` : layout.height) : undefined,
        marginTop: margin?.top !== undefined ? `${margin.top}px` : undefined,
        marginRight: margin?.right !== undefined ? `${margin.right}px` : undefined,
        marginBottom: margin?.bottom !== undefined ? `${margin.bottom}px` : undefined,
        marginLeft: margin?.left !== undefined ? `${margin.left}px` : undefined,
        opacity: entranceOpacity * (spec.style?.opacity ?? 1.0),
        transform: `scale(${entranceScale})`,
        transformOrigin: "center center",
        zIndex: identity.z_index ?? 0,
        boxSizing: "border-box",
      }}
    >
      <Component spec={spec} tree={tree} currentFrame={currentFrame} fps={fps} />
    </div>
  );
}
