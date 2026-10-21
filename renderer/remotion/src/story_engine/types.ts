/**
 * Core type definitions for the Continuous Story Engine.
 *
 * Designed around:
 * - Primitives: Card, Number, Text, Connector, Highlight, Document, Chart
 * - Actions: Enter, Move, TransformNumber, TransformText, Connect, Highlight, Camera, Emphasize
 * - Provenance, camera context preservation, and real audio synchronization
 */

export type PrimitiveType =
  | "card"
  | "number"
  | "text"
  | "connector"
  | "highlight"
  | "document"
  | "chart"
  | "image"
  | "character";

export type CharacterStyle = "futuristic_stick";
export type CharacterPose =
  | "idle"
  | "walk"
  | "point"
  | "think"
  | "worried"
  | "celebrate";
export type CharacterEmotion =
  | "neutral"
  | "focused"
  | "concerned"
  | "surprised"
  | "happy";
export type CharacterFacing = "left" | "right";

export interface CharacterProps {
  style: CharacterStyle;
  role: string;
  label?: string;
  pose: CharacterPose;
  emotion?: CharacterEmotion;
  facing: CharacterFacing;
  accentColor?: string;
  width?: number;
  height?: number;
}

export type GridZone =
  | "top_left"
  | "top_center"
  | "top_right"
  | "center_left"
  | "center"
  | "center_right"
  | "bottom_left"
  | "bottom_center"
  | "bottom_right";

export type MacroZone =
  | "full_screen"
  | "full_top"
  | "full_bottom";

export type ZoneName = GridZone | MacroZone;

export interface FactualProvenance {
  evidence_ref?: string;
  derived_from?: {
    formula: "loan_emi" | "inflation_decay" | "salary_tax_split";
    inputs: Record<string, number>;
  };
}

export interface NumberProps {
  displayValue?: string;
  value: number;
  format: "currency_inr" | "percentage" | "plain";
  prefix?: string;
  suffix?: string;
  decimals?: number;
  provenance?: FactualProvenance;
}

export interface TextProps {
  text: string;
  variant?: "title" | "subtitle" | "label" | "caption";
  color?: string;
}

export interface CardProps {
  title?: string;
  subtitle?: string;
  displayValue?: string;
  value?: number;
  format?: "currency_inr" | "percentage" | "plain";
  valueFactId?: string;
  visualState?: VisualStateKind;
  badge?: string;
  decimals?: number;
  prefix?: string;
  suffix?: string;
  provenance?: FactualProvenance;
  width?: number;
  height?: number;
  accentColor?: string;
}

export interface DocumentItem {
  label: string;
  value: string;
  color?: string;
}

export interface DocumentProps {
  title: string;
  serialNo?: string;
  issuer?: string;
  date?: string;
  statusBadge?: string;
  items?: DocumentItem[];
  watermark?: string;
  accentColor?: string;
  value?: number;
  provenance?: FactualProvenance;
}

export interface ChartSegment {
  label: string;
  value: number;
  color: string;
}

export interface ChartPoint {
  xLabel: string;
  yValue: number;
}

export interface ChartSeries {
  id: string;
  name: string;
  color: string;
  points: ChartPoint[];
}

export interface ChartProps {
  chartType: "split_bar" | "stack" | "trajectory_area" | "multi_bar";
  title?: string;
  subtitle?: string;
  segments?: ChartSegment[];
  series?: ChartSeries[];
  totalValue?: number;
  accentColor?: string;
  highlightPointIndex?: number;
}

export interface ImageProps {
  src?: string;
  assetId?: string;
  alt?: string;
  caption?: string;
  badge?: string;
  borderColor?: string;
  borderRadius?: number;
  fit?: "cover" | "contain";
}

export interface ConnectorProps {
  fromId: string;
  toId: string;
  label?: string;
  style?: "solid" | "dashed";
  arrow?: boolean;
}

export interface HighlightProps {
  targetId: string;
  color?: string;
}

export interface StoryObject {
  id: string;
  type: PrimitiveType;
  /** Spatial layout zone (e.g. "center_left", "center_right", "full_screen") */
  layout?: ZoneName;
  /** Exact resolved coordinates (calculated by Layout Engine) */
  resolvedX?: number;
  resolvedY?: number;
  width?: number;
  height?: number;
  /** Primitive-specific content & styling */
  cardProps?: CardProps;
  numberProps?: NumberProps;
  textProps?: TextProps;
  documentProps?: DocumentProps;
  chartProps?: ChartProps;
  imageProps?: ImageProps;
  connectorProps?: ConnectorProps;
  highlightProps?: HighlightProps;
  characterProps?: CharacterProps;
}

// ----------------------------------------------------
// Actions
// ----------------------------------------------------

export type VisualStateKind =
  | "normal"
  | "dimmed"
  | "warning"
  | "danger"
  | "success"
  | "stamped"
  | "eroded";

export interface StampProps {
  text: string;
  color?: string;
  angle?: number;
}

export type ActionType =
  | "enter"
  | "move"
  | "transform_number"
  | "transform_text"
  | "connect"
  | "highlight"
  | "camera"
  | "emphasize"
  | "split"
  | "merge"
  | "change_visual_state"
  | "exit"
  | "change_pose";

export interface EnterAction {
  action: "enter";
  targetId: string;
  startFrame: number;
  durationFrames: number;
  style?: "fade" | "fade_slide_up" | "pop";
  anchor?: string;
}

export interface MoveAction {
  action: "move";
  targetId: string;
  startFrame: number;
  durationFrames: number;
  /** Target position: strictly one of the 12 spatial ZoneNames */
  to: ZoneName;
  anchor?: string;
}

export interface TransformNumberAction {
  action: "transform_number";
  targetId: string;
  startFrame: number;
  durationFrames: number;
  toValue: number;
  toDisplayValue?: string;
  provenance?: FactualProvenance;
  anchor?: string;
}

export interface TransformTextAction {
  action: "transform_text";
  targetId: string;
  startFrame: number;
  durationFrames: number;
  toText: string;
  toColor?: string;
  anchor?: string;
}

export interface ConnectAction {
  action: "connect";
  targetId: string; // The connector object ID
  startFrame: number;
  durationFrames: number;
  anchor?: string;
}

export interface HighlightAction {
  action: "highlight";
  targetId: string;
  startFrame: number;
  durationFrames: number;
  variant?: "pulse" | "glow" | "border";
  color?: string;
  anchor?: string;
}

export type CameraBehavior = "focus" | "push_in" | "pull_out" | "pan" | "reset";

export interface CameraAction {
  action: "camera";
  startFrame: number;
  durationFrames: number;
  behavior: CameraBehavior;
  targetId?: string; // Optional target card to focus/pan on
  zoom?: number;     // e.g. 1.15 for push_in
  pan?: { x: number; y: number };
  /** Critical IDs that MUST remain within safe view after camera move */
  requiredContextIds?: string[];
  anchor?: string;
}

export interface EmphasizeAction {
  action: "emphasize";
  targetId: string;
  startFrame: number;
  durationFrames: number;
  grow?: number;               // Scale factor e.g. 1.15 (moves toward viewer)
  darkenBackdrop?: number;     // 0 to 1 dim factor for background & non-focused elements
  connectorIntensity?: number; // Multiplier for connected arrows (1.0 to 3.0)
  dominant?: boolean;          // Visually dominant glowing effect
  anchor?: string;
}

export interface SplitAction {
  action: "split";
  sourceId: string;          // Origin parent object that splits
  targetIds: string[];       // Spawned daughter objects
  startFrame: number;
  durationFrames: number;    // Ejection travel duration
  staggerFrames?: number;    // Stagger between consecutive births
  style?: "eject" | "cascade" | "radial";
  anchor?: string;
}

export interface MergeAction {
  action: "merge";
  sourceIds: string[];       // Objects flying in to merge
  targetId: string;          // Destination merged object
  startFrame: number;
  durationFrames: number;
  style?: "converge" | "absorb";
  anchor?: string;
}

export interface ChangeVisualStateAction {
  action: "change_visual_state";
  targetId: string;
  startFrame: number;
  durationFrames: number;
  state: VisualStateKind;
  badge?: string;
  stamp?: StampProps;
  customAccent?: string;
  anchor?: string;
}

export type ExitDirection = "left" | "right" | "up" | "down" | "fade";

export interface ExitAction {
  action: "exit";
  targetId: string;
  startFrame: number;
  durationFrames: number;
  direction: ExitDirection;
  anchor?: string;
}

export interface ChangePoseAction {
  action: "change_pose";
  targetId: string;
  startFrame: number;
  durationFrames: number;
  pose: CharacterPose;
  emotion?: CharacterEmotion;
  facing?: CharacterFacing;
  anchor?: string;
}

export type StoryAction =
  | EnterAction
  | MoveAction
  | TransformNumberAction
  | TransformTextAction
  | ConnectAction
  | HighlightAction
  | CameraAction
  | EmphasizeAction
  | SplitAction
  | MergeAction
  | ChangeVisualStateAction
  | ExitAction
  | ChangePoseAction;

// ----------------------------------------------------
// Real Narration Timing
// ----------------------------------------------------

export interface NarrationCue {
  timeSeconds: number;
  frame: number;
  text: string;
}

export interface NarrationWord {
  word: string;
  start_ms: number;
  end_ms: number;
}

export interface NarrationTrack {
  text: string;
  audioFile?: string;
  wordTimestamps?: NarrationWord[];
  cues?: NarrationCue[];
}

// ----------------------------------------------------
// The Story Plan (Single continuous timeline)
// ----------------------------------------------------

export interface StoryPlan {
  id: string;
  fps: number;
  durationInFrames: number;
  width: number;
  height: number;
  safeMargin?: number; // e.g. 80px default safe boundary
  audioFileName?: string; // Real audible MP3 file in public/
  narration?: NarrationTrack;
  objects: StoryObject[];
  events: StoryAction[];
}
