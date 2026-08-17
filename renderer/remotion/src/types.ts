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
  text?: string;
  subtitle?: string;
  headerLabel?: string;
  footerLabel?: string;
  left?: { raw?: string; label?: string };
  right?: { raw?: string; label?: string };
}

export interface NumberCounterProps {
  startValue?: number;
  endValue?: number;
  label?: string;
  unit?: string;
  title?: string;
  headerLabel?: string;
  footerLabel?: string;
  left?: { value?: number; label?: string; raw?: string; unit?: string };
  right?: { value?: number; label?: string; raw?: string; unit?: string };
}

export interface TimelineProps {
  steps?: string[];
  title?: string;
  headerLabel?: string;
  footerLabel?: string;
  attention_shift_event_id?: string;
  left?: { label?: string; raw?: string };
  right?: { label?: string; raw?: string };
}

export interface ChartsProps {
  chartType?: "bar" | "pie" | "line";
  labels?: string[];
  values?: number[];
  x?: string[];
  y?: number[];
  unit?: string;
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
  headerLabel?: string;
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

export type TypographyRenderSpec = BaseRenderSpec<TypographyProps>;
export type NumberCounterRenderSpec = BaseRenderSpec<NumberCounterProps>;
export type TimelineRenderSpec = BaseRenderSpec<TimelineProps>;
export type ChartsRenderSpec = BaseRenderSpec<ChartsProps>;
export type SplitComparisonRenderSpec = BaseRenderSpec<SplitComparisonProps>;
export type StockImageRenderSpec = BaseRenderSpec<MediaComponentProps>;
export type StockVideoRenderSpec = BaseRenderSpec<MediaComponentProps>;
export type IconAnimationRenderSpec = BaseRenderSpec<MediaComponentProps>;
