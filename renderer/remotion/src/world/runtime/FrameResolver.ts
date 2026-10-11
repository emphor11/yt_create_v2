import { spring } from "remotion";
import { evaluateAnimatedProperty } from "../../primitives/animation";
import type { PrimitiveAnimation, PrimitiveStyle } from "../../primitives/types";
import type {
  CompiledAnimationTrack,
  CompiledPrimitive,
  CompiledStateTrack,
  CompiledVisualInstance,
  JsonObject,
  JsonValue,
} from "../compiledWorld";
import { WorldRendererError } from "./errors";
import type { PreparedWorld, ResolvedPrimitiveFrame, WorldRect } from "./types";

export class FrameResolver {
  constructor(private readonly prepared: PreparedWorld) {}

  resolve(objectId: string, frame: number): ResolvedPrimitiveFrame {
    const primitive = this.getPrimitive(objectId);
    const visible = this.isVisible(objectId, frame);

    const stateTrack = this.prepared.stateTracks.get(objectId);
    const props: JsonObject = {
      ...primitive.properties,
      ...(stateTrack?.initial_state ?? {}),
    };
    const style: PrimitiveStyle = { ...primitive.style };

    const tracks = this.prepared.animations.get(objectId) ?? [];
    const layoutTracks = tracks.filter((track) => track.target_property === "layout");
    const propertyTracks = tracks.filter((track) => track.target_property !== "layout");

    const geometry = resolveGeometry(
      primitive,
      layoutTracks,
      frame,
      this.prepared.world.canvas_config.fps,
    );

    const animations = propertyTracks.map(toPrimitiveAnimation);

    for (const track of propertyTracks) {
      const baseValue = readTrackBaseValue(props, style, track);
      const currentValue = evaluateAnimatedProperty<JsonValue>(
        track.target_property,
        baseValue,
        animations,
        frame,
        this.prepared.world.canvas_config.fps,
      );

      writeTrackValue(
        props,
        style,
        track.target_property,
        currentValue,
        this.prepared.world,
        primitive,
        frame,
      );
    }

    const opacity = style.opacity ?? 1;
    if (typeof opacity !== "number" || !Number.isFinite(opacity)) {
      fail(this.prepared.world, primitive, frame, "Resolved opacity is not numeric.");
    }

    let transform: string | undefined = undefined;
    const enterTrack = tracks.find(
      (track) => track.behavior === "enter" || track.behavior === "appear"
    );

    if (enterTrack && frame >= enterTrack.trigger_frame) {
      const enterElapsed = frame - enterTrack.trigger_frame;
      let motionProgress = 1.0;

      if (enterTrack.easing === "spring") {
        motionProgress = spring({
          frame: enterElapsed,
          fps: this.prepared.world.canvas_config.fps,
          config: enterTrack.spring_config || { damping: 15, stiffness: 100 },
        });
      } else if (enterTrack.easing === "ease-out") {
        const dur = Math.max(1, enterTrack.duration_frames);
        const p = clamp01(enterElapsed / dur);
        motionProgress = 1 - Math.pow(1 - p, 3);
      } else {
        const dur = Math.max(1, enterTrack.duration_frames);
        motionProgress = clamp01(enterElapsed / dur);
      }

      const preset = enterTrack.motion_preset || "reveal";
      let scaleStart = 0.88;
      let yOffsetStart = 16;

      if (preset === "impact") {
        scaleStart = 0.82;
        yOffsetStart = 20;
      } else if (preset === "settle") {
        scaleStart = 0.92;
        yOffsetStart = 12;
      } else if (preset === "gentle") {
        scaleStart = 0.95;
        yOffsetStart = 8;
      }

      const scale = lerp(scaleStart, 1.0, motionProgress);
      const translateY = lerp(yOffsetStart, 0.0, motionProgress);

      const pulseTrack = tracks.find(
        (t) => t.behavior === "pulse" && frame >= t.trigger_frame && frame < t.trigger_frame + t.duration_frames
      );
      let pulseScale = 1.0;
      if (pulseTrack) {
        const pFrame = frame - pulseTrack.trigger_frame;
        const halfDur = Math.max(1, Math.floor(pulseTrack.duration_frames / 2));
        if (pFrame < halfDur) {
          pulseScale = lerp(1.0, 1.06, pFrame / halfDur);
        } else {
          pulseScale = lerp(1.06, 1.0, (pFrame - halfDur) / halfDur);
        }
      }

      const finalScale = scale * pulseScale;
      const isAtRest = Math.abs(finalScale - 1.0) < 0.001 && Math.abs(translateY) < 0.05;
      if (!isAtRest) {
        transform = `scale(${finalScale.toFixed(4)}) translateY(${translateY.toFixed(2)}px)`;
      }
    }

    return {
      object_id: objectId,
      visible,
      geometry,
      props,
      style,
      opacity,
      transform,
    };
  }

  private getPrimitive(objectId: string): CompiledVisualInstance {
    const primitive = this.prepared.primitives.get(objectId);
    if (!primitive) {
      throw new WorldRendererError("Compiled visual instance is missing.", {
        worldId: this.prepared.world.world_id,
        objectId,
      });
    }
    return primitive;
  }

  private isVisible(objectId: string, frame: number): boolean {
    const intervals = this.prepared.visibility.get(objectId) ?? [];
    return intervals.some(
      (interval) => frame >= interval.start_frame && frame < interval.end_frame,
    );
  }
}

function resolveGeometry(
  primitive: CompiledVisualInstance,
  tracks: readonly CompiledAnimationTrack[],
  frame: number,
  fps: number,
): WorldRect {
  const geometry: WorldRect = {
    x: primitive.local_geometry.x,
    y: primitive.local_geometry.y,
    width: primitive.local_geometry.width,
    height: primitive.local_geometry.height,
  };

  if (tracks.length === 0) return geometry;

  let resolvedTrack: CompiledAnimationTrack | undefined;

  for (const track of tracks) {
    if (frame < track.trigger_frame) break;
    resolvedTrack = track;

    const endFrame = track.trigger_frame + track.duration_frames;
    if (frame < endFrame) {
      break;
    }
  }

  if (!resolvedTrack) return geometry;

  const start = resolvedTrack.trigger_frame;
  const duration = Math.max(1, resolvedTrack.duration_frames);
  const end = start + duration;

  if (frame >= end) {
    return asRect(resolvedTrack.to_value, primitive, frame);
  }

  const from = asRect(resolvedTrack.from_value, primitive, frame);
  const to = asRect(resolvedTrack.to_value, primitive, frame);

  let eased: number;
  if (resolvedTrack.easing === "spring") {
    eased = spring({
      frame: frame - start,
      fps,
      config: resolvedTrack.spring_config || { damping: 15, stiffness: 100 },
    });
  } else {
    const progress = clamp01((frame - start) / duration);
    eased = applyEasing(progress, resolvedTrack.easing);
  }

  // Geometry is resolved as a concrete runtime value.
  // Never expose semantic layout names to the renderer.
  return {
    x: lerp(from.x, to.x, eased),
    y: lerp(from.y, to.y, eased),
    width: lerp(from.width, to.width, eased),
    height: lerp(from.height, to.height, eased),
  };
}

function asRect(
  value: JsonValue,
  primitive: CompiledVisualInstance,
  frame: number,
): WorldRect {
  if (!isJsonObject(value)) {
    throw new WorldRendererError("Compiled layout endpoint is not a geometry object.", {
      objectId: primitive.object_id,
      primitiveType: primitive.primitive_type,
      frame,
    });
  }

  const { x, y, width, height } = value;
  if (
    typeof x !== "number" ||
    typeof y !== "number" ||
    typeof width !== "number" ||
    typeof height !== "number" ||
    !Number.isFinite(x) ||
    !Number.isFinite(y) ||
    !Number.isFinite(width) ||
    !Number.isFinite(height)
  ) {
    throw new WorldRendererError("Compiled layout endpoint contains invalid geometry.", {
      objectId: primitive.object_id,
      primitiveType: primitive.primitive_type,
      frame,
    });
  }

  return { x, y, width, height };
}

function toPrimitiveAnimation(track: CompiledAnimationTrack): PrimitiveAnimation {
  return {
    action_id: track.animation_id,
    trigger_frame: track.trigger_frame,
    duration_frames: track.duration_frames,
    easing: track.easing,
    spring_config: track.spring_config ?? undefined,
    behavior: track.behavior,
    target_property: track.target_property,
    from_value: track.from_value,
    to_value: track.to_value,
  };
}

function readTrackBaseValue(
  props: JsonObject,
  style: PrimitiveStyle,
  track: CompiledAnimationTrack,
): JsonValue {
  if (track.target_property === "opacity") {
    return style.opacity ?? track.from_value;
  }

  if (track.target_property.startsWith("style.")) {
    const styleProperty = track.target_property.slice("style.".length) as keyof PrimitiveStyle;
    const value = style[styleProperty];
    return (value as JsonValue | undefined) ?? track.from_value;
  }

  return readJsonPath(props, track.target_property) ?? track.from_value;
}

function writeTrackValue(
  props: JsonObject,
  style: PrimitiveStyle,
  targetProperty: string,
  value: JsonValue,
  world: PreparedWorld["world"],
  primitive: CompiledVisualInstance,
  frame: number,
): void {
  if (targetProperty === "opacity") {
    if (typeof value !== "number" || !Number.isFinite(value)) {
      fail(world, primitive, frame, "Compiled opacity interpolation is not numeric.");
    }
    style.opacity = value;
    return;
  }

  if (targetProperty.startsWith("style.")) {
    const styleProperty = targetProperty.slice("style.".length) as keyof PrimitiveStyle;
    if (!(styleProperty in style)) {
      fail(world, primitive, frame, `Unsupported compiled style property '${targetProperty}'.`);
    }
    (style as Record<string, JsonValue>)[styleProperty] = value;
    return;
  }

  writeJsonPath(props, targetProperty, value, world, primitive, frame);
}

function readJsonPath(object: JsonObject, path: string): JsonValue | undefined {
  let current: JsonValue = object;
  for (const part of path.split(".")) {
    if (!isJsonObject(current) || !(part in current)) return undefined;
    current = current[part];
  }
  return current;
}

function writeJsonPath(
  object: JsonObject,
  path: string,
  value: JsonValue,
  world: PreparedWorld["world"],
  primitive: CompiledVisualInstance,
  frame: number,
): void {
  const parts = path.split(".");
  if (parts.length !== 1) {
    fail(world, primitive, frame, `Unsupported nested render property '${path}'.`);
  }
  object[parts[0]] = value;
}

function isJsonObject(value: JsonValue): value is JsonObject {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function clamp01(value: number): number {
  return Math.min(1, Math.max(0, value));
}

function lerp(from: number, to: number, progress: number): number {
  return from + (to - from) * progress;
}

function applyEasing(progress: number, easing: string): number {
  switch (easing) {
    case "ease_in":
    case "easeIn":
    case "ease-in":
      return progress * progress;
    case "ease_out":
    case "easeOut":
    case "ease-out":
      return 1 - Math.pow(1 - progress, 3);
    case "ease_in_out":
    case "easeInOut":
    case "ease-in-out":
      return progress < 0.5
        ? 4 * progress * progress * progress
        : 1 - Math.pow(-2 * progress + 2, 3) / 2;
    case "linear":
    default:
      return progress;
  }
}

function fail(
  world: PreparedWorld["world"],
  primitive: CompiledVisualInstance,
  frame: number,
  message: string,
): never {
  throw new WorldRendererError(message, {
    worldId: world.world_id,
    objectId: primitive.object_id,
    primitiveType: primitive.primitive_type,
    frame,
  });
}
