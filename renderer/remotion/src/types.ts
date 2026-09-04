export interface RenderFrameSpan {
  event_id: string;
  start_frame: number;
  end_frame: number;
  duration_frames: number;
}

export interface BaseRenderSpec<TProps> {
  scene_id: string;
  composition: string;
  fps: number;
  duration_frames: number;
  props: TProps;
  frame_spans?: RenderFrameSpan[];
}

export interface TypographyProps {
  headerLabel?: string;
  text?: string;
  subtitle?: string;
  variant?: "headline" | "question" | "statement" | "takeaway" | "metric" | "quote";
  highlight?: string;
  align?: "left" | "center";
  value?: string | number;
  author?: string;
  title?: string;
  footerLabel?: string;
  left?: { raw?: string; label?: string };
  right?: { raw?: string; label?: string };
}

export interface NumberCounterProps {
  headerLabel?: string;
  variant?: "single" | "change";
  startValue?: number;
  endValue?: number;
  label?: string;
  prefix?: string;
  suffix?: string;
  unit?: string;
  precision?: number;
  delta?: string;
  subtitle?: string;
  title?: string;
  footerLabel?: string;
  left?: { value?: number; label?: string; raw?: string; unit?: string };
  right?: { value?: number; label?: string; raw?: string; unit?: string };
}

export interface TimelineEvent {
  date: string;
  title: string;
  subtitle?: string;
  value?: string | number;
  type?: "normal" | "major" | "warning" | "positive";
  icon?: string;
}

export interface TimelineProps {
  headerLabel?: string;
  variant?: "milestone" | "detailed";
  title?: string;
  footerLabel?: string;
  events?: TimelineEvent[];
  steps?: string[];
  attention_shift_event_id?: string;
  left?: { label?: string; raw?: string };
  right?: { label?: string; raw?: string };
}

export interface ChartsProps {
  chartType?: "bar" | "pie" | "line" | "donut" | "horizontal_bar";
  labels?: string[];
  values?: number[];
  x?: string[];
  y?: number[];
  unit?: string;
  highlightIndex?: number;
  highlightLabel?: string;
  annotation?: string;
  centerLabel?: string;
  centerValue?: string;
  headerLabel?: string;
  title?: string;
  footerLabel?: string;
  attention_shift_event_id?: string;
  left?: { label?: string; value?: number; raw?: string };
  right?: { label?: string; value?: number; raw?: string };
}

export interface SplitComparisonSide {
  role?: string;
  semantic_entity_id?: string;
  label?: string;
  raw?: string;
  value?: number;
  unit?: string;
}

export interface SplitComparisonProps {
  headerLabel?: string;
  comparisonLabel?: string;
  variant?: "cards" | "versus" | "metric_compare";
  tone?: "neutral" | "positive_negative" | "before_after";
  left?: SplitComparisonSide;
  right?: SplitComparisonSide;
  leftRole?: string;
  leftLabel?: string;
  leftValue?: number | string;
  leftUnit?: string;
  rightRole?: string;
  rightLabel?: string;
  rightValue?: number | string;
  rightUnit?: string;
  delta?: string;
  winner?: "left" | "right" | string;
  title?: string;
  footerLabel?: string;
  attention_shift_event_id?: string;
}

export interface MediaComponentProps {
  text?: string;
  subtitle?: string;
  headerLabel?: string;
  title?: string;
  footerLabel?: string;
  icon?: string;
  left?: { label?: string; raw?: string };
  right?: { label?: string; raw?: string };
}

export interface ProcessStep {
  title: string;
  subtitle?: string;
  type?: "cause" | "step" | "outcome";
  value?: string | number;
  connectorLabel?: string;
  icon?: string;
}

export interface ProcessFlowProps {
  headerLabel?: string;
  layout?: "horizontal" | "vertical" | "auto";
  title?: string;
  footerLabel?: string;
  steps?: ProcessStep[];
  left?: { label?: string; raw?: string };
  right?: { label?: string; raw?: string };
}

export interface KPICard {
  label: string;
  value: number | string;
  unit?: string;
  trend?: string;
  subtitle?: string;
  icon?: string;
  is_primary?: boolean;
}

export interface KPIGridProps {
  headerLabel?: string;
  featuredIndex?: number;
  title?: string;
  footerLabel?: string;
  kpis?: KPICard[];
  left?: { label?: string; raw?: string };
  right?: { label?: string; raw?: string };
}

export interface ProgressiveListItem {
  title?: string;
  text?: string;
  subtitle?: string;
  icon?: string;
  highlight?: boolean;
  value?: string | number;
}

export interface ProgressiveListProps {
  headerLabel?: string;
  variant?: "compact" | "detailed";
  title?: string;
  footerLabel?: string;
  items?: ProgressiveListItem[];
  left?: { label?: string; raw?: string };
  right?: { label?: string; raw?: string };
}

export interface RankedListItem {
  title: string;
  rank?: number | string;
  subtitle?: string;
  value?: string | number;
  numericValue?: number;
  badge?: string;
  change?: string;
  logo?: string;
  icon?: string;
}

export interface RankedListProps {
  headerLabel?: string;
  showBars?: boolean;
  title?: string;
  footerLabel?: string;
  items?: RankedListItem[];
  left?: { label?: string; raw?: string };
  right?: { label?: string; raw?: string };
}

export interface DataTableProps {
  headerLabel?: string;
  variant?: "standard" | "comparison";
  title?: string;
  footerLabel?: string;
  columns?: string[];
  rows?: (string | number)[][];
  highlightRow?: number;
  highlightCol?: number;
  highlightKey?: string;
  showDataBars?: boolean;
  annotation?: string;
  left?: { label?: string; raw?: string };
  right?: { label?: string; raw?: string };
}

export interface BeforeAfterState {
  label?: string;
  title: string;
  value?: number | string;
  unit?: string;
  subtitle?: string;
  image?: string;
  icon?: string;
}

export interface BeforeAfterProps {
  headerLabel?: string;
  variant?: "numeric" | "visual";
  tone?: "neutral" | "positive" | "negative";
  before?: BeforeAfterState;
  after?: BeforeAfterState;
  delta?: string;
  deltaLabel?: string;
  title?: string;
  footerLabel?: string;
  left?: { label?: string; raw?: string };
  right?: { label?: string; raw?: string };
}

export interface QuoteCalloutProps {
  headerLabel?: string;
  quote: string;
  author?: string;
  role?: string;
  avatar?: string;
  title?: string;
  footerLabel?: string;
  left?: { label?: string; raw?: string };
  right?: { label?: string; raw?: string };
}

export interface AssetReference {
  asset_id: string;
  asset_type: "image" | "video";
  source: string;
  query: string;
  local_path: string;
  url: string | null;
  asset_status: string;
}

export interface ComponentSpec {
  component_id: string;
  props: any;
}

export interface SceneSpec {
  scene_id: string;
  start_frame: number;
  end_frame: number;
  duration_frames: number;
  component: ComponentSpec;
  asset: AssetReference | null;
  narration_text: string | null;
}

export interface AudioSpec {
  audio_file_name: string;
  local_path: string;
  duration_seconds: number;
}

export interface VideoAssemblyProps {
  scenes: SceneSpec[];
  audio: AudioSpec;
}

export type TypographyRenderSpec = BaseRenderSpec<TypographyProps>;
export type NumberCounterRenderSpec = BaseRenderSpec<NumberCounterProps>;
export type TimelineRenderSpec = BaseRenderSpec<TimelineProps>;
export type ProcessFlowRenderSpec = BaseRenderSpec<ProcessFlowProps>;
export type KPIGridRenderSpec = BaseRenderSpec<KPIGridProps>;
export type ProgressiveListRenderSpec = BaseRenderSpec<ProgressiveListProps>;
export type RankedListRenderSpec = BaseRenderSpec<RankedListProps>;
export type DataTableRenderSpec = BaseRenderSpec<DataTableProps>;
export type BeforeAfterRenderSpec = BaseRenderSpec<BeforeAfterProps>;
export type QuoteCalloutRenderSpec = BaseRenderSpec<QuoteCalloutProps>;
export type ChartsRenderSpec = BaseRenderSpec<ChartsProps>;
export type SplitComparisonRenderSpec = BaseRenderSpec<SplitComparisonProps>;
export type StockImageRenderSpec = BaseRenderSpec<MediaComponentProps>;
export type StockVideoRenderSpec = BaseRenderSpec<MediaComponentProps>;
export type IconAnimationRenderSpec = BaseRenderSpec<MediaComponentProps>;
export type VideoAssemblyRenderSpec = BaseRenderSpec<VideoAssemblyProps>;
