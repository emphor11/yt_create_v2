import type { PrimitiveStyle } from "../../primitives/types";
import type {
  CompiledAnimationTrack,
  CompiledPrimitive,
  CompiledVisualInstance,
  CompiledWorld,
  JsonObject,
} from "../compiledWorld";

export interface WorldRect {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface PreparedWorld {
  readonly world: CompiledWorld;
  readonly primitives: ReadonlyMap<string, CompiledVisualInstance>;
  readonly roots: readonly string[];
  readonly stateTracks: ReadonlyMap<string, CompiledWorld["state_tracks"][number]>;
  readonly animations: ReadonlyMap<string, readonly CompiledAnimationTrack[]>;
  readonly visibility: ReadonlyMap<
    string,
    CompiledWorld["visibility_intervals"]
  >;
}

export interface ResolvedPrimitiveFrame {
  readonly object_id: string;
  readonly visible: boolean;
  readonly geometry: WorldRect;
  readonly props: JsonObject;
  readonly style: PrimitiveStyle;
  readonly opacity: number;
  readonly transform?: string;
}
