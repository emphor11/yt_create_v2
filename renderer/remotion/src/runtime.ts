import type { CompiledPrimitive, CompiledWorld } from "./world/compiledWorld";
import {
  assertWorldRendererContract,
  createWorldRuntime,
  WorldRendererError,
} from "./world/runtime/index";
import type { ResolvedPrimitiveFrame } from "./world/runtime/index";

export { assertWorldRendererContract, createWorldRuntime, WorldRendererError };
export type { ResolvedPrimitiveFrame } from "./world/runtime/index";

export function isPrimitiveVisible(
  world: CompiledWorld,
  objectId: string,
  frame: number,
): boolean {
  const runtime = createWorldRuntime(world);
  return runtime.isVisible(objectId, frame);
}

export function getVisiblePrimitiveIds(
  world: CompiledWorld,
  frame: number,
): string[] {
  const runtime = createWorldRuntime(world);
  const sourceObjects = (world.objects && Object.keys(world.objects).length > 0)
    ? world.objects
    : (world.primitives ?? {});
  return Object.keys(sourceObjects).filter((id) => runtime.isVisible(id, frame));
}

export function resolvePrimitiveFrameState(
  world: CompiledWorld,
  primitive: CompiledPrimitive,
  frame: number,
): ResolvedPrimitiveFrame {
  const runtime = createWorldRuntime(world);
  return runtime.resolveObject(primitive.object_id, frame);
}
