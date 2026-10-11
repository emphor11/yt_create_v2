import React from "react";
import { SurfaceCard, type ComponentProps } from "./SurfaceCard";
import { MetricCard } from "./MetricCard";
import { HeroStat } from "./HeroStat";
import { ComparisonCard } from "./ComparisonCard";
import { ProcessCard } from "./ProcessCard";
import { MetricBlock } from "./MetricBlock";
import { Badge } from "./Badge";
import { Callout } from "./Callout";
import { FlowConnector } from "./FlowConnector";
import { TrendLineChart } from "./TrendLineChart";
import { RankedBarChart } from "./RankedBarChart";
import { AllocationDonut } from "./AllocationDonut";
import { WaterfallBridge } from "./WaterfallBridge";

export const VisualComponentRegistry: Record<string, React.FC<ComponentProps>> = {
  MetricCard: MetricCard as React.FC<ComponentProps>,
  HeroStat: HeroStat as React.FC<ComponentProps>,
  ComparisonCard: ComparisonCard as React.FC<ComponentProps>,
  ProcessCard: ProcessCard as React.FC<ComponentProps>,
  SurfaceCard: SurfaceCard as React.FC<ComponentProps>,
  MetricBlock: MetricBlock as React.FC<ComponentProps>,
  Badge: Badge as React.FC<ComponentProps>,
  Callout: Callout as React.FC<ComponentProps>,
  FlowConnector: FlowConnector as React.FC<ComponentProps>,
  TrendLineChart: TrendLineChart as React.FC<ComponentProps>,
  RankedBarChart: RankedBarChart as React.FC<ComponentProps>,
  AllocationDonut: AllocationDonut as React.FC<ComponentProps>,
  WaterfallBridge: WaterfallBridge as React.FC<ComponentProps>,
};

export function isVisualComponent(componentType: string | undefined): boolean {
  return typeof componentType === "string" && componentType in VisualComponentRegistry;
}
