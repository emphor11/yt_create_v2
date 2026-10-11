import { CANONICAL_WORLD_PRIMITIVE_TYPES } from "../compiledWorld";
import type { CompiledPrimitive, CompiledVisualInstance, CompiledWorld } from "../compiledWorld";
import { isVisualComponent } from "../../components/registry";
import { FrameResolver } from "./FrameResolver";
import { WorldRendererError } from "./errors";
import type { PreparedWorld, ResolvedPrimitiveFrame } from "./types";

export function assertWorldRendererContract(world: CompiledWorld): void {
  prepareWorld(world);
}

export function prepareWorld(world: CompiledWorld): PreparedWorld {
  return prepareWorldInternal(world);
}

function prepareWorldInternal(world: CompiledWorld): PreparedWorld {
  if (!world.world_id || world.total_duration_frames <= 0) {
    throw new WorldRendererError("Compiled world has no valid identity or duration.", {
      worldId: world.world_id,
    });
  }

  if (
    world.canvas_config.width <= 0 ||
    world.canvas_config.height <= 0 ||
    world.canvas_config.fps <= 0
  ) {
    throw new WorldRendererError("Compiled world has invalid canvas configuration.", {
      worldId: world.world_id,
    });
  }

  const sourceObjects = (world.objects && Object.keys(world.objects).length > 0)
    ? world.objects
    : (world.primitives ?? {});

  const primitives = new Map<string, CompiledVisualInstance>();
  const roots: string[] = [];

  for (const [objectId, rawInstance] of Object.entries(sourceObjects)) {
    const instance: CompiledVisualInstance = {
      ...rawInstance,
      kind: rawInstance.kind ?? (rawInstance.component_type ? "component" : "primitive"),
    };

    if (instance.object_id !== objectId) {
      fail(world, instance, 0, "Visual instance registry key does not match object ID.");
    }

    if (instance.kind === "component" || instance.component_type) {
      if (!instance.component_type || !isVisualComponent(instance.component_type)) {
        fail(world, instance, 0, `Unsupported visual component type: ${instance.component_type}`);
      }
    } else {
      if (!instance.primitive_type || !CANONICAL_WORLD_PRIMITIVE_TYPES.includes(instance.primitive_type)) {
        fail(world, instance, 0, "Unsupported canonical primitive type.");
      }
    }

    if (
      instance.parent_object_id !== null &&
      !sourceObjects[instance.parent_object_id]
    ) {
      fail(world, instance, 0, "Visual instance parent is not in the compiled registry.");
    }

    if (instance.parent_object_id === null) {
      roots.push(objectId);
    }

    if (new Set(instance.child_object_ids).size !== instance.child_object_ids.length) {
      fail(world, instance, 0, "Compiled child hierarchy contains duplicate child IDs.");
    }

    for (const childId of instance.child_object_ids) {
      const child = sourceObjects[childId];
      if (!child || child.parent_object_id !== objectId) {
        fail(world, instance, 0, "Compiled child hierarchy is inconsistent.");
      }
    }

    if (instance.parent_object_id !== null) {
      const parent = sourceObjects[instance.parent_object_id];
      if (!parent.child_object_ids.includes(objectId)) {
        fail(world, instance, 0, "Compiled parent does not reference its child.");
      }
    }

    if (instance.primitive_type === "connector" || instance.component_type === "FlowConnector") {
      if (!instance.connector_path) {
        fail(world, instance, 0, "Connector has no compiled path.");
      }
      if (instance.connector_path.parent_object_id !== instance.parent_object_id) {
        fail(world, instance, 0, "Connector path space does not match its parent.");
      }
      if (instance.connector_path.points.length < 2) {
        fail(world, instance, 0, "Connector path has fewer than two points.");
      }
      if (JSON.stringify(instance.properties).includes("target_id") && instance.primitive_type === "connector") {
        fail(world, instance, 0, "Connector contains an unresolved target ID.");
      }
    }

    primitives.set(objectId, instance);
  }

  validateHierarchy(world, roots);

  const stateTracks = new Map(
    world.state_tracks.map((track) => [track.object_id, track]),
  );

  const animations = new Map<string, CompiledWorld["animation_tracks"]>();
  for (const track of world.animation_tracks) {
    const primitive = primitives.get(track.object_id);
    if (!primitive) {
      throw new WorldRendererError("Animation references an unknown object.", {
        worldId: world.world_id,
        objectId: track.object_id,
        frame: track.trigger_frame,
      });
    }
    if (track.from_value === null || track.to_value === null) {
      fail(world, primitive, track.trigger_frame, "Animation contains a null endpoint.");
    }
    if (track.trigger_frame + track.duration_frames > world.total_duration_frames) {
      fail(world, primitive, track.trigger_frame, "Animation exceeds world duration.");
    }

    const existing = animations.get(track.object_id) ?? [];
    existing.push(track);
    animations.set(track.object_id, existing);
  }

  for (const tracks of animations.values()) {
    tracks.sort((a, b) =>
      a.trigger_frame - b.trigger_frame || a.animation_id.localeCompare(b.animation_id),
    );
  }

  const visibility = new Map<string, CompiledWorld["visibility_intervals"]>();
  for (const interval of world.visibility_intervals) {
    const existing = visibility.get(interval.object_id) ?? [];
    existing.push(interval);
    visibility.set(interval.object_id, existing);
  }

  for (const intervals of visibility.values()) {
    intervals.sort((a, b) => a.start_frame - b.start_frame);
  }

  return {
    world,
    primitives,
    roots,
    stateTracks,
    animations,
    visibility,
  };
}

function validateHierarchy(world: CompiledWorld, roots: readonly string[]): void {
  const source = (world.objects && Object.keys(world.objects).length > 0)
    ? world.objects
    : (world.primitives ?? {});
  const visited = new Set<string>();
  const visiting = new Set<string>();

  const visit = (objectId: string): void => {
    if (visiting.has(objectId)) {
      const primitive = source[objectId];
      fail(world, primitive, 0, "Compiled hierarchy contains a cycle.");
    }
    if (visited.has(objectId)) return;

    const primitive = source[objectId];
    if (!primitive) {
      throw new WorldRendererError("Compiled hierarchy references an unknown object.", {
        worldId: world.world_id,
        objectId,
      });
    }

    visiting.add(objectId);
    for (const childId of primitive.child_object_ids) visit(childId);
    visiting.delete(objectId);
    visited.add(objectId);
  };

  roots.forEach(visit);

  if (visited.size !== Object.keys(source).length) {
    throw new WorldRendererError("Compiled hierarchy has unreachable objects.", {
      worldId: world.world_id,
    });
  }
}

function fail(
  world: CompiledWorld,
  primitive: CompiledVisualInstance | undefined,
  frame: number,
  message: string,
): never {
  throw new WorldRendererError(message, {
    worldId: world.world_id,
    objectId: primitive?.object_id,
    primitiveType: primitive?.primitive_type,
    componentType: primitive?.component_type,
    frame,
  });
}

export class WorldRuntime {
  readonly prepared: PreparedWorld;
  private readonly resolver: FrameResolver;

  constructor(world: CompiledWorld) {
    this.prepared = prepareWorld(world);
    this.resolver = new FrameResolver(this.prepared);
  }

  get world(): CompiledWorld {
    return this.prepared.world;
  }

  get roots(): readonly string[] {
    return this.prepared.roots;
  }

  getPrimitive(objectId: string): CompiledVisualInstance {
    const primitive = this.prepared.primitives.get(objectId);
    if (!primitive) {
      throw new WorldRendererError("Compiled visual instance is missing.", {
        worldId: this.world.world_id,
        objectId,
      });
    }
    return primitive;
  }

  isVisible(objectId: string, frame: number): boolean {
    const intervals = this.prepared.visibility.get(objectId) ?? [];
    return intervals.some(
      (interval) => frame >= interval.start_frame && frame < interval.end_frame,
    );
  }

  resolveObject(objectId: string, frame: number): ResolvedPrimitiveFrame {
    return this.resolver.resolve(objectId, frame);
  }

  getEntranceFrame(objectId: string): number {
    const tracks = this.prepared.animations.get(objectId) ?? [];
    const enterTrack = tracks.find((t) => t.behavior === "enter" || t.behavior === "appear");
    if (enterTrack) return enterTrack.trigger_frame;
    const intervals = this.prepared.visibility.get(objectId) ?? [];
    return intervals[0]?.start_frame ?? 0;
  }
}

export function createWorldRuntime(world: CompiledWorld): WorldRuntime {
  return new WorldRuntime(world);
}
