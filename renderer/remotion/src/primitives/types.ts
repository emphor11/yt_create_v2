export type CanonicalCapabilityType =
  | "text"
  | "number"
  | "shape"
  | "icon"
  | "connector"
  | "image"
  | "video"
  | "bar"
  | "line"
  | "point"
  | "segment"
  | "progress"
  | "group";

export interface PrimitiveIdentity {
  id: string;
  type: CanonicalCapabilityType;
  parent_id?: string | null;
  z_index?: number;
}

export interface MarginPadding {
  top?: number;
  right?: number;
  bottom?: number;
  left?: number;
}

export interface PrimitiveLayout {
  position_mode?: "absolute" | "relative" | "flex_item";
  x?: number | null;
  y?: number | null;
  width?: number | string | null;
  height?: number | string | null;
  anchor_origin?: "top-left" | "center" | "bottom-center" | "top-right" | null;
  margin?: MarginPadding | null;
  padding?: MarginPadding | null;
}

export interface BoxShadow {
  color?: string;
  blur?: number;
  x?: number;
  y?: number;
}

export interface PrimitiveStyle {
  fill?: string | null;
  stroke?: string | null;
  stroke_width?: number | null;
  stroke_style?: "solid" | "dashed" | "dotted" | null;
  corner_radius?: number | number[] | null;
  opacity?: number | null;
  shadow?: BoxShadow | null;
  blur_backdrop?: number | null;
  blend_mode?: "normal" | "multiply" | "screen" | "overlay" | null;
}

export interface PrimitiveTiming {
  enter_frame?: number;
  exit_frame?: number | null;
  visible?: boolean;
}

export interface SpringConfig {
  damping?: number;
  stiffness?: number;
  mass?: number;
}

export interface PrimitiveAnimation {
  action_id: string;
  trigger_frame: number;
  duration_frames?: number;
  easing?: "spring" | "ease-out" | "linear" | "bezier";
  spring_config?: SpringConfig;
  behavior: string;
  target_property: string;
  from_value?: any;
  to_value: any;
}

// -----------------------------------------------------------------------------
// Primitive-Specific Props
// -----------------------------------------------------------------------------

export interface TextHighlightSpan {
  word: string;
  color?: string;
  background?: string;
}

export interface TextProps {
  content: string;
  font_size?: number;
  font_weight?: number;
  line_height?: number;
  letter_spacing?: number;
  align?: "left" | "center" | "right";
  text_transform?: "none" | "uppercase" | "lowercase" | "capitalize";
  wrap?: boolean;
  highlight_spans?: TextHighlightSpan[];
}

export interface NumberProps {
  value: number;
  start_value?: number;
  prefix?: string | null;
  suffix?: string | null;
  precision?: number | null;
  tabular_nums?: boolean;
  font_size?: number;
  font_weight?: number;
}

export interface ShapeProps {
  shape_type?: "rectangle" | "circle" | "pill" | "capsule";
  corner_radius?: number | number[] | null;
}

export interface IconProps {
  name: string;
  size?: number;
  color?: string;
  stroke_width?: number;
}

export interface ConnectorAnchor {
  target_id?: string | null;
  side?: "left" | "right" | "top" | "bottom" | "center" | null;
  x?: number | null;
  y?: number | null;
}

export interface ConnectorLabel {
  text: string;
  font_size?: number;
  background?: string;
}

export interface ConnectorProps {
  from_anchor: ConnectorAnchor;
  to_anchor: ConnectorAnchor;
  routing?: "straight" | "curved" | "orthogonal_elbow";
  has_arrow?: boolean;
  stroke?: string;
  stroke_width?: number;
  stroke_dasharray?: string | null;
  label?: ConnectorLabel | null;
}

export interface ImageProps {
  source: string;
  object_fit?: "cover" | "contain" | "fill";
  border_radius?: number;
}

export interface VideoProps {
  source: string;
  loop?: boolean;
  muted?: boolean;
  playback_rate?: number;
  loop_duration_frames?: number | null;
}

export interface BarProps {
  orientation?: "horizontal" | "vertical";
  fill_percentage?: number;
  max_length?: number;
  thickness?: number;
  corner_radius?: number;
  foreground_color?: string;
  background_track_color?: string | null;
}

export interface LinePoint {
  x: number;
  y: number;
}

export interface LineProps {
  points?: LinePoint[];
  curve_type?: "linear" | "monotone_cubic" | "step";
  stroke?: string;
  stroke_width?: number;
  area_fill?: string | null;
}

export interface PointProps {
  x: number;
  y: number;
  radius?: number;
  fill?: string;
  stroke?: string | null;
  stroke_width?: number;
  label?: string | null;
}

export interface SegmentProps {
  parent_track_id: string;
  start_ratio?: number;
  length_ratio?: number;
  fill?: string;
  label?: string | null;
}

export interface ProgressProps {
  variant?: "radial_ring" | "linear_meter";
  progress_ratio?: number;
  radius?: number;
  stroke_width?: number;
  track_color?: string;
  fill_color?: string;
  center_label?: string | null;
}

export interface GroupProps {
  child_ids?: string[];
  layout_flow?: "none" | "row" | "column";
  gap?: number;
  align_items?: "flex-start" | "center" | "flex-end" | "stretch";
  justify_content?: "flex-start" | "center" | "flex-end" | "space-between" | "space-around";
}

// -----------------------------------------------------------------------------
// Spec and Tree Spec
// -----------------------------------------------------------------------------

export interface PrimitiveSpec<TProps = any> {
  identity: PrimitiveIdentity;
  layout?: PrimitiveLayout;
  style?: PrimitiveStyle;
  timing?: PrimitiveTiming;
  props: TProps;
  current_state?: Record<string, any>;
  animations?: PrimitiveAnimation[];
}

export interface PrimitiveTreeSpec {
  scene_id: string;
  duration_frames: number;
  root_primitive_ids: string[];
  primitives: Record<string, PrimitiveSpec>;
}
