import React from "react";

import type {
  BarProps,
  CanonicalCapabilityType,
  IconProps,
  ImageProps,
  LineProps,
  NumberProps,
  PointProps,
  PrimitiveSpec,
  PrimitiveStyle,
  ProgressProps,
  SegmentProps,
  ShapeProps,
  TextProps,
  VideoProps,
} from "../../primitives/types";
import {
  PrimitiveBar,
  PrimitiveIcon,
  PrimitiveImage,
  PrimitiveLine,
  PrimitiveNumber,
  PrimitivePoint,
  PrimitiveProgress,
  PrimitiveSegment,
  PrimitiveShape,
  PrimitiveText,
  PrimitiveVideo,
} from "./PrimitiveRenderer";
import type { CompiledPrimitive, CompiledVisualInstance, CompiledWorld, JsonObject } from "../compiledWorld";
import { WorldRuntime, WorldRendererError } from "../runtime";
import type { ResolvedPrimitiveFrame } from "../../runtime";
import { WorldConnector } from "./WorldConnector";
import { VisualComponentRegistry, isVisualComponent } from "../../components/registry";

export interface ParentSpace {
  width: number;
  height: number;
}

interface WorldObjectProps {
  runtime: WorldRuntime;
  objectId: string;
  frame: number;
  parentSpace: ParentSpace;
}

export const WorldObject: React.FC<WorldObjectProps> = ({
  runtime,
  objectId,
  frame,
  parentSpace,
}) => {
  const primitive = runtime.getPrimitive(objectId);
  const resolved = runtime.resolveObject(objectId, frame);

  if (!resolved.visible) return null;

  // 1. Direct Visual Component Dispatch
  if (primitive.kind === "component" || (primitive.component_type && isVisualComponent(primitive.component_type))) {
    const Component = VisualComponentRegistry[primitive.component_type!];
    if (Component) {
      return (
        <Component
          runtime={runtime}
          instance={primitive}
          resolved={resolved}
          frame={frame}
          renderChild={(childId) => (
            <WorldObject
              key={childId}
              runtime={runtime}
              objectId={childId}
              frame={frame}
              parentSpace={{
                width: resolved.geometry.width,
                height: resolved.geometry.height,
              }}
            />
          )}
        />
      );
    }
  }

  if (primitive.primitive_type === "group") {
    return (
      <div
        data-world-object-id={primitive.object_id}
        style={boxStyle(resolved)}
      >
        {primitive.child_object_ids.map((childId) => (
          <WorldObject
            key={childId}
            runtime={runtime}
            objectId={childId}
            frame={frame}
            parentSpace={{
              width: resolved.geometry.width,
              height: resolved.geometry.height,
            }}
          />
        ))}
      </div>
    );
  }

  if (primitive.primitive_type === "connector") {
    return (
      <WorldConnector
        world={runtime.world}
        primitive={primitive as CompiledPrimitive}
        frame={frame}
        parentSpace={parentSpace}
        resolved={resolved}
      />
    );
  }

  const spec = makeLeafSpec(runtime.world, primitive as CompiledPrimitive, frame, resolved);

  return (
    <div
      data-world-object-id={primitive.object_id}
      style={boxStyle(resolved)}
    >
      <PrimitiveRenderer
        primitiveType={primitive.primitive_type as Exclude<CanonicalCapabilityType, "group" | "connector">}
        spec={spec}
        frame={frame}
        fps={runtime.world.canvas_config.fps}
      />
    </div>
  );
};

function boxStyle(resolved: ResolvedPrimitiveFrame): React.CSSProperties {
  return {
    position: "absolute",
    left: resolved.geometry.x,
    top: resolved.geometry.y,
    width: resolved.geometry.width,
    height: resolved.geometry.height,
    opacity: resolved.opacity,
    transform: resolved.transform,
    transformOrigin: "center center",
    overflow: "visible",
    boxSizing: "border-box",
  };
}

function PrimitiveRenderer({
  primitiveType,
  spec,
  frame,
  fps,
}: {
  primitiveType: Exclude<CanonicalCapabilityType, "group" | "connector">;
  spec: PrimitiveSpec<unknown>;
  frame: number;
  fps: number;
}): React.ReactNode {
  switch (primitiveType) {
    case "text":
      return <PrimitiveText spec={spec as PrimitiveSpec<TextProps>} currentFrame={frame} fps={fps} />;
    case "number":
      return <PrimitiveNumber spec={spec as PrimitiveSpec<NumberProps>} currentFrame={frame} fps={fps} />;
    case "shape":
      return <PrimitiveShape spec={spec as PrimitiveSpec<ShapeProps>} currentFrame={frame} fps={fps} />;
    case "icon":
      return <PrimitiveIcon spec={spec as PrimitiveSpec<IconProps>} currentFrame={frame} fps={fps} />;
    case "image":
      return <PrimitiveImage spec={spec as PrimitiveSpec<ImageProps>} currentFrame={frame} fps={fps} />;
    case "video":
      return <PrimitiveVideo spec={spec as PrimitiveSpec<VideoProps>} currentFrame={frame} fps={fps} />;
    case "bar":
      return <PrimitiveBar spec={spec as PrimitiveSpec<BarProps>} currentFrame={frame} fps={fps} />;
    case "line":
      return <PrimitiveLine spec={spec as PrimitiveSpec<LineProps>} currentFrame={frame} fps={fps} />;
    case "point":
      return <PrimitivePoint spec={spec as PrimitiveSpec<PointProps>} currentFrame={frame} fps={fps} />;
    case "segment":
      return <PrimitiveSegment spec={spec as PrimitiveSpec<SegmentProps>} currentFrame={frame} fps={fps} />;
    case "progress":
      return <PrimitiveProgress spec={spec as PrimitiveSpec<ProgressProps>} currentFrame={frame} fps={fps} />;
    default:
      return assertNever(primitiveType);
  }
}

function makeLeafSpec(
  world: CompiledWorld,
  primitive: CompiledPrimitive,
  frame: number,
  resolved: ResolvedPrimitiveFrame,
): PrimitiveSpec<unknown> {
  return {
    identity: {
      id: primitive.object_id,
      type: primitive.primitive_type as Exclude<CanonicalCapabilityType, "group" | "connector">,
      parent_id: primitive.parent_object_id,
    },
    layout: {
      position_mode: "absolute",
      x: 0,
      y: 0,
      width: resolved.geometry.width,
      height: resolved.geometry.height,
    },
    style: resolved.style,
    props: makeTypedProps(world, primitive, frame, primitive.primitive_type, resolved.props),
    animations: [],
  };
}

function makeTypedProps(
  world: CompiledWorld,
  primitive: CompiledPrimitive,
  frame: number,
  primitiveType: CanonicalCapabilityType,
  props: JsonObject,
): unknown {
  switch (primitiveType) {
    case "text":
      return {
        ...props,
        content: requiredString(world, primitive, frame, props, "content"),
      } as TextProps;
    case "number":
      return {
        ...props,
        value: requiredNumber(world, primitive, frame, props, "value"),
      } as NumberProps;
    case "shape":
      return props as ShapeProps;
    case "icon":
      return {
        ...props,
        name: requiredString(world, primitive, frame, props, "name"),
      } as IconProps;
    case "image":
      return {
        ...props,
        source: requiredString(world, primitive, frame, props, "source"),
      } as ImageProps;
    case "video":
      return {
        ...props,
        source: requiredString(world, primitive, frame, props, "source"),
      } as VideoProps;
    case "bar":
      return props as BarProps;
    case "line":
      return props as LineProps;
    case "point":
      return {
        ...props,
        x: requiredNumber(world, primitive, frame, props, "x"),
        y: requiredNumber(world, primitive, frame, props, "y"),
      } as PointProps;
    case "segment":
      return {
        ...props,
        parent_track_id: requiredString(world, primitive, frame, props, "parent_track_id"),
      } as SegmentProps;
    case "progress":
      return props as ProgressProps;
    case "group":
    case "connector":
      throw new WorldRendererError(`Non-leaf primitive '${primitiveType}' cannot use leaf props.`, {
        worldId: world.world_id,
        objectId: primitive.object_id,
        primitiveType: primitive.primitive_type,
        frame,
      });
    default:
      return assertNever(primitiveType);
  }
}

function requiredString(
  world: CompiledWorld,
  primitive: CompiledPrimitive,
  frame: number,
  props: JsonObject,
  key: string,
): string {
  const value = props[key];
  if (typeof value !== "string") {
    throw new WorldRendererError(`Compiled property '${key}' is not a string.`, {
      worldId: world.world_id,
      objectId: primitive.object_id,
      primitiveType: primitive.primitive_type,
      frame,
    });
  }
  return value;
}

function requiredNumber(
  world: CompiledWorld,
  primitive: CompiledPrimitive,
  frame: number,
  props: JsonObject,
  key: string,
): number {
  const value = props[key];
  if (typeof value !== "number" || !Number.isFinite(value)) {
    throw new WorldRendererError(`Compiled property '${key}' is not numeric.`, {
      worldId: world.world_id,
      objectId: primitive.object_id,
      primitiveType: primitive.primitive_type,
      frame,
    });
  }
  return value;
}

function assertNever(value: never): never {
  throw new Error(`Unsupported canonical primitive type '${String(value)}'.`);
}
