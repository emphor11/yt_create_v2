import type { CanonicalCapabilityType, PrimitiveStyle, SpringConfig } from "../primitives/types";

export type JsonPrimitive = string | number | boolean | null;
export type JsonValue = JsonPrimitive | JsonValue[] | { [key: string]: JsonValue };
export type JsonObject = { [key: string]: JsonValue };

export interface CompiledCanvasConfig {
  width: number;
  height: number;
  fps: number;
  safe_margin_x?: number;
  safe_margin_y?: number;
}

export interface CompiledLocalRect {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface CompiledPoint {
  x: number;
  y: number;
}

export interface CompiledConnectorPath {
  parent_object_id: string | null;
  from_point: CompiledPoint;
  to_point: CompiledPoint;
  points: CompiledPoint[];
  routing: "straight" | "curved" | "orthogonal_elbow";
}

export type CompiledObjectKind = "primitive" | "component";

export interface CompiledVisualInstance {
  object_id: string;
  kind?: CompiledObjectKind;
  primitive_type?: CanonicalCapabilityType;
  component_type?: string;
  parent_object_id: string | null;
  child_object_ids: string[];
  local_geometry: CompiledLocalRect;
  style: PrimitiveStyle;
  properties: JsonObject;
  connector_path: CompiledConnectorPath | null;
}

export interface CompiledPrimitive {
  object_id: string;
  primitive_type: CanonicalCapabilityType;
  parent_object_id: string | null;
  child_object_ids: string[];
  local_geometry: CompiledLocalRect;
  style: PrimitiveStyle;
  properties: JsonObject;
  connector_path: CompiledConnectorPath | null;
}

export interface CompiledBeatInterval {
  beat_id: string;
  start_ms: number;
  end_ms: number;
  start_frame: number;
  end_frame: number;
}

export interface CompiledSpeechAnchor {
  anchor_id: string;
  beat_id: string;
  text: string;
  occurrence: number;
  start_ms: number;
  end_ms: number;
  global_frame: number;
}

export interface CompiledTransitionEvent {
  event_id: string;
  from_beat_id: string;
  to_beat_id: string;
  global_frame: number;
  kind: string;
  preserve_object_ids: string[];
}

export interface CompiledVisibilityInterval {
  object_id: string;
  start_frame: number;
  end_frame: number;
}

export interface CompiledStateChange {
  event_id: string;
  object_id: string;
  beat_id: string;
  global_frame: number;
  kind: string;
  target_property: string;
  from_value: JsonValue;
  to_value: JsonValue;
  visible: boolean | null;
}

export interface CompiledStateTrack {
  object_id: string;
  initial_state: JsonObject;
  changes: CompiledStateChange[];
}

export interface CompiledAnimationTrack {
  animation_id: string;
  object_id: string;
  trigger_frame: number;
  duration_frames: number;
  easing: "linear" | "ease-out" | "spring" | "bezier";
  motion_preset?: "reveal" | "settle" | "impact" | "gentle" | string | null;
  spring_config?: SpringConfig | null;
  behavior: string;
  target_property: string;
  from_value: JsonValue;
  to_value: JsonValue;
}

export interface CompiledLifecycleTrack {
  object_id: string;
  introduced_frame: number;
  exit_frame: number | null;
  mode: "persistent" | "beat_local" | "until_exit";
}

export interface CompiledTerminalHold {
  start_frame: number;
  end_frame: number;
}

export interface CompiledMacroZoneAllocation {
  object_id: string;
  zone: string;
  rect: CompiledLocalRect;
}

export interface CompiledWorld {
  schema_version: string;
  world_id: string;
  canvas_config: CompiledCanvasConfig;
  total_duration_frames: number;
  beat_intervals: CompiledBeatInterval[];
  speech_anchors: CompiledSpeechAnchor[];
  transition_events: CompiledTransitionEvent[];
  objects?: Record<string, CompiledVisualInstance>;
  primitives?: Record<string, CompiledPrimitive>;
  lifecycle_tracks: CompiledLifecycleTrack[];
  visibility_intervals: CompiledVisibilityInterval[];
  state_tracks: CompiledStateTrack[];
  animation_tracks: CompiledAnimationTrack[];
  terminal_hold: CompiledTerminalHold | null;
  macro_zone_allocations: CompiledMacroZoneAllocation[];
  semantic_lineage: Array<{
    kind: string;
    reference_id: string;
    excerpt: string | null;
  }>;
}

export const CANONICAL_WORLD_PRIMITIVE_TYPES: readonly CanonicalCapabilityType[] = [
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
