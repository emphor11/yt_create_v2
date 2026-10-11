import React from "react";
import type { CompiledVisualInstance } from "../world/compiledWorld";
import type { ResolvedPrimitiveFrame } from "../world/runtime/types";
import type { WorldRuntime } from "../world/runtime";

export interface ComponentProps {
  runtime: WorldRuntime;
  instance: CompiledVisualInstance;
  resolved: ResolvedPrimitiveFrame;
  frame: number;
}

export interface DataPoint {
  label: string;
  value: number;
}

export interface HighlightPoint {
  label: string;
  value?: string | number;
}

const colorByIntent: Record<
  string,
  {
    stroke: string;
    glow: string;
    fillGradientStart: string;
    fillGradientStop: string;
    badgeBg: string;
    badgeText: string;
    badgeBorder: string;
  }
> = {
  danger: {
    stroke: "#f43f5e",
    glow: "rgba(244, 63, 94, 0.4)",
    fillGradientStart: "rgba(244, 63, 94, 0.30)",
    fillGradientStop: "rgba(244, 63, 94, 0.0)",
    badgeBg: "rgba(244, 63, 94, 0.15)",
    badgeText: "#fb7185",
    badgeBorder: "rgba(244, 63, 94, 0.4)",
  },
  accent: {
    stroke: "#38bdf8",
    glow: "rgba(56, 189, 248, 0.4)",
    fillGradientStart: "rgba(56, 189, 248, 0.30)",
    fillGradientStop: "rgba(56, 189, 248, 0.0)",
    badgeBg: "rgba(56, 189, 248, 0.15)",
    badgeText: "#38bdf8",
    badgeBorder: "rgba(56, 189, 248, 0.4)",
  },
  success: {
    stroke: "#10b981",
    glow: "rgba(16, 185, 129, 0.4)",
    fillGradientStart: "rgba(16, 185, 129, 0.30)",
    fillGradientStop: "rgba(16, 185, 129, 0.0)",
    badgeBg: "rgba(16, 185, 129, 0.15)",
    badgeText: "#34d399",
    badgeBorder: "rgba(16, 185, 129, 0.4)",
  },
  warning: {
    stroke: "#fbbf24",
    glow: "rgba(245, 158, 11, 0.4)",
    fillGradientStart: "rgba(245, 158, 11, 0.30)",
    fillGradientStop: "rgba(245, 158, 11, 0.0)",
    badgeBg: "rgba(245, 158, 11, 0.15)",
    badgeText: "#fde047",
    badgeBorder: "rgba(245, 158, 11, 0.4)",
  },
  neutral: {
    stroke: "#94a3b8",
    glow: "rgba(148, 163, 184, 0.3)",
    fillGradientStart: "rgba(148, 163, 184, 0.20)",
    fillGradientStop: "rgba(148, 163, 184, 0.0)",
    badgeBg: "rgba(255, 255, 255, 0.08)",
    badgeText: "#cbd5e1",
    badgeBorder: "rgba(255, 255, 255, 0.15)",
  },
};

export const TrendLineChart: React.FC<ComponentProps> = ({
  runtime,
  instance,
  resolved,
  frame,
}) => {
  const props = resolved.props;
  const header = (props.header as string) || "TRAJECTORY OVERVIEW";
  const trend = (props.trend as string) || "neutral"; // "up" | "down" | "neutral"
  const intent = (props.intent as string) || (trend === "down" ? "danger" : trend === "up" ? "success" : "neutral");
  const highlightPoint = (props.highlight_point as unknown) as HighlightPoint | undefined;
  const subtext = props.subtext as string | undefined;

  // Raw data points parsing with resilience
  let rawDataPoints: DataPoint[] = [];
  if (Array.isArray(props.data_points)) {
    rawDataPoints = props.data_points.map((pt: any) => ({
      label: String(pt?.label ?? ""),
      value: typeof pt?.value === "number" ? pt.value : parseFloat(String(pt?.value || 0)) || 0,
    }));
  }

  const hasExplicitPoints = rawDataPoints.length >= 2;

  const theme = colorByIntent[intent] || colorByIntent.neutral;

  // Chart coordinates calculation
  const cardWidth = resolved.geometry.width || 760;
  const cardHeight = resolved.geometry.height || 420;

  const paddingX = 40;
  const paddingTop = 75;
  const paddingBottom = 48;
  const plotWidth = Math.max(100, cardWidth - paddingX * 2);
  const plotHeight = Math.max(60, cardHeight - paddingTop - paddingBottom);

  type CoordPoint = { x: number; y: number; pt?: DataPoint };
  let coords: CoordPoint[] = [];

  if (hasExplicitPoints) {
    const values = rawDataPoints.map((d) => d.value);
    const minVal = Math.min(...values);
    const maxVal = Math.max(...values);
    const valSpread = maxVal - minVal === 0 ? 1 : maxVal - minVal;
    // Give 10% head and foot room
    const yMin = minVal - valSpread * 0.1;
    const yMax = maxVal + valSpread * 0.1;
    const ySpread = yMax - yMin;

    coords = rawDataPoints.map((pt, i) => {
      const x = paddingX + (i / (rawDataPoints.length - 1)) * plotWidth;
      const normY = (pt.value - yMin) / ySpread;
      const y = paddingTop + plotHeight - normY * plotHeight;
      return { x, y, pt };
    });
  } else {
    // When data points are omitted, render smooth illustrative trend trajectory without fake points/labels
    const steps = 5;
    coords = Array.from({ length: steps }, (_, i) => {
      const t = i / (steps - 1);
      const x = paddingX + t * plotWidth;
      let normY = 0.5;
      if (trend === "up") {
        normY = 0.15 + 0.7 * (t * t * (3 - 2 * t)); // smoothstep up
      } else if (trend === "down") {
        normY = 0.85 - 0.7 * (t * t * (3 - 2 * t)); // smoothstep down
      }
      const y = paddingTop + plotHeight - normY * plotHeight;
      return { x, y };
    });
  }

  // Build SVG path
  const linePathD = coords.reduce((acc, c, idx) => {
    return idx === 0 ? `M ${c.x.toFixed(1)} ${c.y.toFixed(1)}` : `${acc} L ${c.x.toFixed(1)} ${c.y.toFixed(1)}`;
  }, "");

  const areaBottomY = paddingTop + plotHeight;
  const firstX = coords[0]?.x.toFixed(1) || String(paddingX);
  const lastX = coords[coords.length - 1]?.x.toFixed(1) || String(paddingX + plotWidth);
  const areaPathD = `${linePathD} L ${lastX} ${areaBottomY} L ${firstX} ${areaBottomY} Z`;

  // Entrance and drawing animation
  const enterFrame = runtime.getEntranceFrame(instance.object_id);
  const elapsed = Math.max(0, frame - enterFrame);
  const drawDuration = 32; // ~1 second drawing time at 30fps
  const progress = Math.min(1, Math.max(0, elapsed / drawDuration));
  const easedProgress = 1 - Math.pow(1 - progress, 3); // Cubic ease out

  // Approximate line length for stroke-dasharray animation
  let totalLength = 0;
  for (let i = 1; i < coords.length; i++) {
    const dx = coords[i].x - coords[i - 1].x;
    const dy = coords[i].y - coords[i - 1].y;
    totalLength += Math.sqrt(dx * dx + dy * dy);
  }
  const dashOffset = totalLength * (1 - easedProgress);

  // Identify highlight point index (default to last point if specified without matching index)
  let highlightIdx = coords.length - 1;
  if (highlightPoint && hasExplicitPoints) {
    const foundIdx = rawDataPoints.findIndex(
      (p) => p.label.toLowerCase() === highlightPoint.label.toLowerCase()
    );
    if (foundIdx !== -1) {
      highlightIdx = foundIdx;
    }
  }
  const activeHighlight = coords[highlightIdx];

  const trendIcon = trend === "up" ? "▲" : trend === "down" ? "▼" : "●";
  const trendLabel = trend === "up" ? "UPWARD TREND" : trend === "down" ? "DOWNWARD TREND" : "STABLE";

  return (
    <div
      data-visual-component="TrendLineChart"
      data-object-id={instance.object_id}
      style={{
        position: "absolute",
        left: resolved.geometry.x,
        top: resolved.geometry.y,
        width: cardWidth,
        height: cardHeight,
        opacity: resolved.opacity,
        transform: resolved.transform,
        transformOrigin: "center center",
        background: "linear-gradient(180deg, #131722 0%, #0d111a 100%)",
        border: "1px solid rgba(255, 255, 255, 0.10)",
        borderRadius: 16,
        boxShadow: "0 24px 48px -12px rgba(0, 0, 0, 0.8), 0 0 0 1px rgba(255, 255, 255, 0.04) inset",
        boxSizing: "border-box",
        overflow: "hidden",
        display: "flex",
        flexDirection: "column",
        justifyContent: "space-between",
        fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
      }}
    >
      {/* Header bar */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          padding: "20px 28px 0 28px",
          zIndex: 2,
        }}
      >
        <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
          <span
            style={{
              fontSize: 13,
              fontWeight: 700,
              letterSpacing: 1.5,
              textTransform: "uppercase",
              color: "rgba(255, 255, 255, 0.65)",
            }}
          >
            {header}
          </span>
          {subtext && (
            <span style={{ fontSize: 11, color: "rgba(255, 255, 255, 0.40)" }}>
              {subtext}
            </span>
          )}
        </div>

        {/* Trend Pill */}
        <div
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: 6,
            padding: "5px 12px",
            borderRadius: 9999,
            backgroundColor: theme.badgeBg,
            border: `1px solid ${theme.badgeBorder}`,
            color: theme.badgeText,
            fontSize: 11,
            fontWeight: 700,
            letterSpacing: 0.8,
          }}
        >
          <span style={{ fontSize: 10 }}>{trendIcon}</span>
          <span>{trendLabel}</span>
        </div>
      </div>

      {/* SVG Chart Graphic */}
      <div style={{ position: "relative", width: "100%", height: "100%" }}>
        <svg
          width={cardWidth}
          height={cardHeight}
          style={{ position: "absolute", top: 0, left: 0, overflow: "visible" }}
        >
          <defs>
            <linearGradient id={`gradient-${instance.object_id}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={theme.fillGradientStart} />
              <stop offset="100%" stopColor={theme.fillGradientStop} />
            </linearGradient>
            <filter id={`glow-${instance.object_id}`} x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="4" result="blur" />
              <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>
          </defs>

          {/* Gridlines */}
          {[0.25, 0.5, 0.75].map((fraction) => {
            const gy = paddingTop + plotHeight * fraction;
            return (
              <line
                key={fraction}
                x1={paddingX}
                y1={gy}
                x2={paddingX + plotWidth}
                y2={gy}
                stroke="rgba(255, 255, 255, 0.05)"
                strokeDasharray="4 4"
                strokeWidth={1}
              />
            );
          })}

          {/* Area Fill */}
          <path
            d={areaPathD}
            fill={`url(#gradient-${instance.object_id})`}
            opacity={Math.min(1, easedProgress * 1.2)}
          />

          {/* Trend Line */}
          <path
            d={linePathD}
            fill="none"
            stroke={theme.stroke}
            strokeWidth={3.5}
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeDasharray={totalLength}
            strokeDashoffset={dashOffset}
            filter={`url(#glow-${instance.object_id})`}
          />

          {/* Data Points */}
          {hasExplicitPoints && coords.map((c, i) => {
            const isPointVisible = easedProgress >= i / (coords.length - 1);
            if (!isPointVisible) return null;

            const isHighlighted = i === highlightIdx && highlightPoint;
            return (
              <g key={i}>
                <circle
                  cx={c.x}
                  cy={c.y}
                  r={isHighlighted ? 6 : 4}
                  fill={isHighlighted ? theme.stroke : "#0d111a"}
                  stroke={theme.stroke}
                  strokeWidth={isHighlighted ? 3 : 2}
                  style={{
                    filter: isHighlighted ? `drop-shadow(0 0 8px ${theme.glow})` : undefined,
                  }}
                />
              </g>
            );
          })}
        </svg>

        {/* Highlight Callout Tag / Bubble */}
        {highlightPoint && activeHighlight && easedProgress > 0.8 && (
          <div
            style={{
              position: "absolute",
              left: activeHighlight.x,
              top: activeHighlight.y - 42,
              transform: "translate(-50%, -100%)",
              backgroundColor: theme.badgeBg,
              border: `1px solid ${theme.badgeBorder}`,
              borderRadius: 8,
              padding: "4px 10px",
              boxShadow: `0 8px 16px -4px rgba(0, 0, 0, 0.6), 0 0 12px ${theme.glow}`,
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              gap: 2,
              pointerEvents: "none",
              zIndex: 3,
            }}
          >
            <span
              style={{
                fontSize: 10,
                fontWeight: 700,
                color: theme.badgeText,
                letterSpacing: 0.8,
                textTransform: "uppercase",
                whiteSpace: "nowrap",
              }}
            >
              {highlightPoint.label}
            </span>
            {highlightPoint.value !== undefined && (
              <span
                style={{
                  fontSize: 12,
                  fontWeight: 800,
                  color: "#ffffff",
                  whiteSpace: "nowrap",
                }}
              >
                {String(highlightPoint.value)}
              </span>
            )}
          </div>
        )}

        {/* X-Axis Labels */}
        {hasExplicitPoints && (
          <div
            style={{
              position: "absolute",
              bottom: 14,
              left: paddingX,
              width: plotWidth,
              display: "flex",
              justifyContent: "space-between",
              pointerEvents: "none",
            }}
          >
            {rawDataPoints.map((pt, i) => (
              <span
                key={i}
                style={{
                  fontSize: 11,
                  fontWeight: 600,
                  color: "rgba(255, 255, 255, 0.45)",
                  letterSpacing: 0.5,
                }}
              >
                {pt.label}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
