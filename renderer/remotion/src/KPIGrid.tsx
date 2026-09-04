import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { type KPICard, type KPIGridProps } from "./types";
import { tokens } from "./design-tokens";

/**
 * Smart Number Formatter & Interpolator for Finance YouTube Visuals
 * Handles formats like "$1.02T", "27.4%", "$96.8B", "150,000", "+24% YoY"
 */
function formatAnimatedValue(rawVal: string | number, progress: number): { formatted: string; isNumeric: boolean } {
  if (typeof rawVal === "number") {
    const isFloat = rawVal % 1 !== 0;
    const current = progress * rawVal;
    return {
      formatted: isFloat ? current.toFixed(1) : Math.round(current).toString(),
      isNumeric: true,
    };
  }

  const str = String(rawVal).trim();
  // Match prefix (e.g., $, ₹, €), number (int or float), and suffix (e.g., B, M, K, T, %)
  const match = str.match(/^([^\d\.-]*)([\d,]+(?:\.\d+)?)(.*)$/);
  if (!match) {
    return { formatted: str, isNumeric: false };
  }

  const prefix = match[1] || "";
  const numStr = match[2].replace(/,/g, "");
  const suffix = match[3] || "";
  const targetNum = parseFloat(numStr);

  if (isNaN(targetNum)) {
    return { formatted: str, isNumeric: false };
  }

  const currentNum = progress * targetNum;
  const hasDecimals = numStr.includes(".");
  const decimalPlaces = hasDecimals ? (numStr.split(".")[1]?.length || 1) : 0;

  const formattedNum = decimalPlaces > 0 ? currentNum.toFixed(decimalPlaces) : Math.round(currentNum).toLocaleString();
  return {
    formatted: `${prefix}${formattedNum}${suffix}`,
    isNumeric: true,
  };
}

export function KPIGrid(props: KPIGridProps | any) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Normalize boundary props wrapper
  const resolvedProps: KPIGridProps = props.props ? props.props : props;
  const duration_frames = (props as any).duration_frames || 180;

  const headerLabel = resolvedProps.headerLabel || "";
  const kpiList: KPICard[] = Array.isArray(resolvedProps.kpis) ? resolvedProps.kpis : [];
  const footerLabel = resolvedProps.footerLabel || "";

  // Identify Primary/Featured KPI vs Secondary KPIs
  let primaryKPI: KPICard | null = null;
  const secondaryKPIs: KPICard[] = [];

  const explicitFeatIdx = resolvedProps.featuredIndex !== undefined ? resolvedProps.featuredIndex : 0;

  kpiList.forEach((card, idx) => {
    if (card.is_primary || idx === explicitFeatIdx) {
      if (!primaryKPI) {
        primaryKPI = card;
      } else {
        secondaryKPIs.push(card);
      }
    } else {
      secondaryKPIs.push(card);
    }
  });

  // Fallback if no primary designated
  if (!primaryKPI && kpiList.length > 0) {
    primaryKPI = kpiList[0];
    secondaryKPIs.push(...kpiList.slice(1));
  }

  // Pacing Timeline (0-15% Header, 15-45% Primary, 45-70% Secondary, 70-85% Trend Pulse)
  const headerFrameStart = 0;
  const primaryFrameStart = Math.round(duration_frames * 0.12);
  const secondaryFrameStart = Math.round(duration_frames * 0.40);
  const trendFrameStart = Math.round(duration_frames * 0.68);

  // Springs
  const headerSpring = spring({
    frame: Math.max(0, frame - headerFrameStart),
    fps,
    config: { damping: 15, stiffness: 100 },
  });

  const primarySpring = spring({
    frame: Math.max(0, frame - primaryFrameStart),
    fps,
    config: { damping: 14, stiffness: 90 },
  });

  const trendPulseSpring = spring({
    frame: Math.max(0, frame - trendFrameStart),
    fps,
    config: { damping: 10, stiffness: 140 },
  });

  // Primary number count-up progress (15-45%)
  const primaryCountProgress = interpolate(
    frame,
    [primaryFrameStart, primaryFrameStart + Math.round(duration_frames * 0.28)],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  return (
    <AbsoluteFill
      style={{
        background: tokens.bg.base,
        color: tokens.text.primary,
        fontFamily: tokens.font.family,
        overflow: "hidden",
        padding: tokens.spacing.padding,
      }}
    >
      <div
        style={{
          position: "relative",
          display: "flex",
          flexDirection: "column",
          height: "100%",
          justifyContent: "space-between",
        }}
      >
        {/* Header Eyebrow */}
        {headerLabel ? (
          <header style={{ opacity: headerSpring, transform: `translateY(${(1 - headerSpring) * -15}px)` }}>
            <div
              style={{
                color: tokens.accent.blue,
                fontSize: tokens.font.eyebrow,
                fontWeight: 800,
                textTransform: "uppercase",
                letterSpacing: 2,
              }}
            >
              {headerLabel}
            </div>
          </header>
        ) : null}

        {/* Main Content Layout: Hero Primary KPI on top + Supporting Grid below */}
        <main
          style={{
            position: "relative",
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
            gap: "20px",
            flex: 1,
            margin: "20px 0",
          }}
        >
          {/* PRIMARY HERO KPI CARD */}
          {primaryKPI ? (() => {
            const pk = primaryKPI as KPICard;
            const animatedValue = formatAnimatedValue(pk.value, primaryCountProgress);
            const isPositiveTrend = pk.trend ? !pk.trend.includes("-") : true;
            const trendColor = isPositiveTrend ? "#10b981" : "#ef4444";
            const trendIcon = isPositiveTrend ? "↑" : "↓";

            return (
              <div
                style={{
                  position: "relative",
                  background: "linear-gradient(135deg, rgba(30, 41, 59, 0.95) 0%, rgba(15, 23, 42, 0.9) 100%)",
                  borderLeft: `4px solid ${tokens.accent.blue}`,
                  borderTop: "1px solid rgba(59, 130, 246, 0.3)",
                  borderRight: "1px solid rgba(59, 130, 246, 0.2)",
                  borderBottom: "1px solid rgba(59, 130, 246, 0.2)",
                  borderRadius: "16px",
                  padding: "32px 36px",
                  boxShadow: "0 10px 30px rgba(0, 0, 0, 0.3)",
                  opacity: primarySpring,
                  transform: `scale(${0.96 + primarySpring * 0.04}) translateY(${(1 - primarySpring) * 20}px)`,
                }}
              >
                {/* Top Row: Icon + Label + Subtitle */}
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 12 }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                    {pk.icon ? <span style={{ fontSize: 24 }}>{pk.icon}</span> : null}
                    <span
                      style={{
                        fontSize: 20,
                        fontWeight: 800,
                        textTransform: "uppercase",
                        letterSpacing: 1.5,
                        color: tokens.text.secondary,
                      }}
                    >
                      {pk.label}
                    </span>
                  </div>
                  {pk.subtitle ? (
                    <span
                      style={{
                        fontSize: 16,
                        fontWeight: 600,
                        color: tokens.text.muted,
                        background: "rgba(255, 255, 255, 0.06)",
                        padding: "4px 12px",
                        borderRadius: "12px",
                      }}
                    >
                      {pk.subtitle}
                    </span>
                  ) : null}
                </div>

                {/* Hero Value & Integrated Trend Callout */}
                <div style={{ display: "flex", alignItems: "baseline", justifyContent: "space-between" }}>
                  <div style={{ fontSize: 68, fontWeight: 900, color: "#ffffff", lineHeight: 1, letterSpacing: -1 }}>
                    {animatedValue.formatted}
                    {pk.unit ? <span style={{ fontSize: 32, marginLeft: 6, color: tokens.text.secondary }}>{pk.unit}</span> : null}
                  </div>

                  {pk.trend ? (
                    <div
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: "6px",
                        fontSize: 22,
                        fontWeight: 900,
                        color: trendColor,
                        background: isPositiveTrend ? "rgba(16, 185, 129, 0.15)" : "rgba(239, 68, 68, 0.15)",
                        border: `1px solid ${trendColor}`,
                        padding: "6px 16px",
                        borderRadius: "20px",
                        opacity: frame > trendFrameStart ? 1 : 0.85,
                        transform: `scale(${1 + (frame > trendFrameStart ? trendPulseSpring * 0.08 : 0)})`,
                      }}
                    >
                      <span>{trendIcon}</span>
                      <span>{pk.trend}</span>
                    </div>
                  ) : null}
                </div>
              </div>
            );
          })() : null}

          {/* SECONDARY SUPPORTING KPIS GRID */}
          {secondaryKPIs.length > 0 ? (
            <div
              style={{
                display: "grid",
                gridTemplateColumns: `repeat(${Math.min(3, secondaryKPIs.length)}, 1fr)`,
                gap: "16px",
              }}
            >
              {secondaryKPIs.map((card, sIdx) => {
                const itemDelay = secondaryFrameStart + sIdx * 6;
                const secSpring = spring({
                  frame: Math.max(0, frame - itemDelay),
                  fps,
                  config: { damping: 15, stiffness: 100 },
                });

                const secCountProgress = interpolate(
                  frame,
                  [itemDelay, itemDelay + Math.round(duration_frames * 0.25)],
                  [0, 1],
                  { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
                );

                const secAnimValue = formatAnimatedValue(card.value, secCountProgress);
                const isPos = card.trend ? !card.trend.includes("-") : true;
                const tColor = isPos ? "#10b981" : "#ef4444";

                return (
                  <div
                    key={sIdx}
                    style={{
                      background: "rgba(15, 23, 42, 0.75)",
                      border: "1px solid rgba(59, 130, 246, 0.25)",
                      borderRadius: "14px",
                      padding: "20px 24px",
                      boxShadow: "0 6px 20px rgba(0, 0, 0, 0.2)",
                      opacity: secSpring,
                      transform: `translateY(${(1 - secSpring) * 15}px)`,
                    }}
                  >
                    {/* Secondary Label & Subtitle */}
                    <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 8 }}>
                      <div style={{ fontSize: 15, fontWeight: 700, color: tokens.text.secondary, textTransform: "uppercase" }}>
                        {card.label}
                      </div>
                      {card.subtitle ? (
                        <div style={{ fontSize: 13, color: tokens.text.muted, fontWeight: 500 }}>
                          {card.subtitle}
                        </div>
                      ) : null}
                    </div>

                    {/* Secondary Value & Trend */}
                    <div style={{ display: "flex", alignItems: "baseline", justifyContent: "space-between" }}>
                      <div style={{ fontSize: 36, fontWeight: 900, color: "#ffffff", lineHeight: 1 }}>
                        {secAnimValue.formatted}
                        {card.unit ? <span style={{ fontSize: 18, marginLeft: 4, color: tokens.text.muted }}>{card.unit}</span> : null}
                      </div>

                      {card.trend ? (
                        <div style={{ fontSize: 15, fontWeight: 800, color: tColor }}>
                          {card.trend}
                        </div>
                      ) : null}
                    </div>
                  </div>
                );
              })}
            </div>
          ) : null}
        </main>

        {/* Footer */}
        {footerLabel ? (
          <footer style={{ textAlign: "center", fontSize: 20, color: tokens.text.muted, fontWeight: 600 }}>
            {footerLabel}
          </footer>
        ) : null}
      </div>
    </AbsoluteFill>
  );
}
