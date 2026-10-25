import React from "react";
import type { ChartProps } from "../types.ts";
import { handDrawn } from "../hand-drawn-theme.ts";

interface ChartPrimitiveProps {
  props: ChartProps;
  progress?: number; // 0 to 1 progress for line drawing or bar fill
  activePointIndex?: number;
  style?: React.CSSProperties;
}

export const ChartPrimitive: React.FC<ChartPrimitiveProps> = ({
  props,
  progress = 1,
  activePointIndex,
  style,
}) => {
  const { chartType, title, subtitle, series, segments, totalValue, accentColor } = props;
  const themeColor = accentColor || handDrawn.colors.teal;

  // 1. Trajectory Area Chart (e.g. 10-Year Inflation Decay or 20-Year Loan Burden)
  const trajectoryPoints =
    series && series.length > 0 && series[0].points && series[0].points.length > 0
      ? series[0].points
      : ((props as any).points as typeof series extends (infer S)[] ? S extends { points: infer P } ? P : never : never);

  if (chartType === "trajectory_area" && trajectoryPoints && trajectoryPoints.length > 0) {
    const points = trajectoryPoints;
    const width = 560;
    const height = 280;
    const padX = 50;
    const padY = 40;
    const plotW = width - padX * 2;
    const plotH = height - padY * 2;

    const yValues = points.map((p) => p.yValue ?? (p as any).value ?? 0);
    const minY = 0;
    const maxY = Math.max(1, Math.max(...yValues) * 1.15);

    // Coordinate mapping (safe against single point division by zero)
    const divisor = Math.max(1, points.length - 1);
    const coords = points.map((p, idx) => {
      const val = p.yValue ?? (p as any).value ?? 0;
      const px = padX + (idx / divisor) * plotW;
      const py = padY + plotH - ((val - minY) / (maxY - minY)) * plotH;
      return { x: px, y: py, label: p.xLabel ?? (p as any).label ?? `Pt ${idx + 1}`, value: val };
    });

    // Generate smooth SVG curve path
    const pathD = coords.reduce((acc, pt, i, arr) => {
      if (i === 0) return `M ${pt.x} ${pt.y}`;
      const prev = arr[i - 1];
      const cx = (prev.x + pt.x) / 2;
      return `${acc} C ${cx} ${prev.y}, ${cx} ${pt.y}, ${pt.x} ${pt.y}`;
    }, "");

    const areaD = `${pathD} L ${coords[coords.length - 1].x} ${padY + plotH} L ${coords[0].x} ${padY + plotH} Z`;

    const activeIdx = activePointIndex ?? Math.min(coords.length - 1, Math.floor(progress * (coords.length - 1)));
    const activeCoord = coords[activeIdx];

    return (
      <div
        style={{
          width: "100%",
          height: "100%",
          backgroundColor: handDrawn.colors.paperAlt,
          borderRadius: handDrawn.radius.card,
          border: `2px solid ${handDrawn.colors.ink}`,
          boxShadow: handDrawn.shadow.paper,
          padding: 24,
          display: "flex",
          flexDirection: "column",
          position: "relative",
          overflow: "hidden",
          ...style,
        }}
      >
        {/* Header */}
        {(title || subtitle) && (
          <div style={{ marginBottom: 12 }}>
            {title && (
              <div
                style={{
                  fontFamily: handDrawn.font.label,
                  fontSize: 16,
                  fontWeight: 600,
                  color: handDrawn.colors.ink,
                  letterSpacing: "0.04em",
                  textTransform: "uppercase",
                }}
              >
                {title}
              </div>
            )}
            {subtitle && (
              <div
                style={{
                  fontFamily: handDrawn.font.body,
                  fontSize: 13,
                  color: handDrawn.colors.inkMuted,
                  marginTop: 2,
                }}
              >
                {subtitle}
              </div>
            )}
          </div>
        )}

        {/* SVG Curve Plot */}
        <div style={{ flex: 1, position: "relative" }}>
          <svg
            viewBox={`0 0 ${width} ${height}`}
            style={{ width: "100%", height: "100%", overflow: "visible" }}
          >
            <defs>
              <linearGradient id="curveGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={themeColor} stopOpacity="0.35" />
                <stop offset="100%" stopColor={themeColor} stopOpacity="0.0" />
              </linearGradient>
              <filter id="glowFilter" x="-20%" y="-20%" width="140%" height="140%">
                <feGaussianBlur stdDeviation="3" result="blur" />
                <feComposite in="SourceGraphic" in2="blur" operator="over" />
              </filter>
            </defs>

            {/* Horizontal Gridlines */}
            {[0, 0.33, 0.66, 1].map((pct, i) => {
              const gy = padY + plotH * (1 - pct);
              return (
                <line
                  key={i}
                  x1={padX}
                  y1={gy}
                  x2={padX + plotW}
                  y2={gy}
                  stroke="#D6C9B5"
                  strokeDasharray="3 6"
                />
              );
            })}

            {/* Gradient Area Fill */}
            <path d={areaD} fill="url(#curveGradient)" />

            {/* Main Animated Line */}
            <path
              d={pathD}
              fill="none"
              stroke={themeColor}
              strokeWidth="3.5"
              strokeLinecap="round"
              filter="url(#glowFilter)"
            />

            {/* Data Point Nodes */}
            {coords.map((pt, i) => {
              const isSelected = i === activeIdx;
              return (
                <g key={i}>
                  <circle
                    cx={pt.x}
                    cy={pt.y}
                    r={isSelected ? 6 : 3.5}
                    fill={isSelected ? "#FFFFFF" : themeColor}
                    stroke={themeColor}
                    strokeWidth={isSelected ? 3 : 1}
                  />
                  {/* Axis Label */}
                  <text
                    x={pt.x}
                    y={padY + plotH + 20}
                    textAnchor="middle"
                    fill={handDrawn.colors.inkMuted}
                    fontSize="11"
                    fontFamily={handDrawn.font.body}
                  >
                    {pt.label}
                  </text>
                </g>
              );
            })}

            {/* Active Callout Indicator */}
            {activeCoord && (
              <g>
                <line
                  x1={activeCoord.x}
                  y1={padY}
                  x2={activeCoord.x}
                  y2={padY + plotH}
                  stroke={handDrawn.colors.inkMuted}
                  strokeDasharray="3 3"
                />
                <rect
                  x={activeCoord.x - 45}
                  y={activeCoord.y - 34}
                  width="90"
                  height="24"
                  rx="6"
                  fill={handDrawn.colors.paperAlt}
                  stroke={themeColor}
                  strokeWidth="1.5"
                />
                <text
                  x={activeCoord.x}
                  y={activeCoord.y - 18}
                  textAnchor="middle"
                  fill={handDrawn.colors.ink}
                  fontSize="12"
                  fontWeight="600"
                  fontFamily={handDrawn.font.label}
                >
                  ₹{(activeCoord.value / 100000).toFixed(2)}L
                </text>
              </g>
            )}
          </svg>
        </div>
      </div>
    );
  }

  // 2. Split Bar / Stack / Multi Bar Breakdown
  const palette = [
    handDrawn.colors.teal,
    handDrawn.colors.coral,
    handDrawn.colors.green,
    handDrawn.colors.amber,
    handDrawn.colors.blue,
    "#8B6FA8",
    "#D88987",
  ];

  let segmentList: { label: string; value: number; color: string }[] = segments || [];
  if (segmentList.length === 0) {
    if (series && series.length > 1) {
      segmentList = series.map((s, idx) => {
        const lastPt = s.points && s.points.length > 0 ? s.points[s.points.length - 1] : null;
        return {
          label: s.name || s.id || `Series ${idx + 1}`,
          value: lastPt ? (lastPt.yValue ?? (lastPt as any).value ?? 0) : 0,
          color: s.color || palette[idx % palette.length],
        };
      });
    } else if (series && series.length === 1 && series[0].points && series[0].points.length > 0) {
      segmentList = series[0].points.map((p: any, idx: number) => ({
        label: p.xLabel || p.label || `Item ${idx + 1}`,
        value: p.yValue !== undefined ? p.yValue : (p.value ?? 0),
        color: p.color || palette[idx % palette.length],
      }));
    } else if ((props as any).points && (props as any).points.length > 0) {
      segmentList = (props as any).points.map((p: any, idx: number) => ({
        label: p.xLabel || p.label || `Item ${idx + 1}`,
        value: p.yValue !== undefined ? p.yValue : (p.value ?? 0),
        color: p.color || palette[idx % palette.length],
      }));
    }
  }

  const total = totalValue || segmentList.reduce((sum, s) => sum + Math.abs(s.value), 0) || 1;

  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        backgroundColor: handDrawn.colors.paperAlt,
        borderRadius: handDrawn.radius.card,
        border: `2px solid ${handDrawn.colors.ink}`,
        boxShadow: handDrawn.shadow.paper,
        padding: 24,
        display: "flex",
        flexDirection: "column",
        justifyContent: "space-between",
        ...style,
      }}
    >
      <div>
        {title && (
          <div
            style={{
              fontFamily: handDrawn.font.label,
              fontSize: 16,
              fontWeight: 600,
              color: handDrawn.colors.ink,
              letterSpacing: "0.04em",
              textTransform: "uppercase",
              marginBottom: 4,
            }}
          >
            {title}
          </div>
        )}
        {subtitle && (
          <div
            style={{
              fontFamily: handDrawn.font.body,
              fontSize: 13,
              color: handDrawn.colors.inkMuted,
              marginBottom: 16,
            }}
          >
            {subtitle}
          </div>
        )}
      </div>

      {segmentList.length > 0 ? (
        <>
          {/* Segmented Progress Track */}
          <div
            style={{
              width: "100%",
              height: 18,
              borderRadius: 9,
              backgroundColor: handDrawn.colors.paperDeep,
              overflow: "hidden",
              display: "flex",
              boxShadow: "inset 0 1px 2px rgba(32,37,34,0.10)",
            }}
          >
            {segmentList.map((seg, i) => {
              const pct = (Math.abs(seg.value) / total) * 100 * Math.min(1, Math.max(0, progress));
              return (
                <div
                  key={i}
                  style={{
                    width: `${pct}%`,
                    height: "100%",
                    backgroundColor: seg.color,
                    transition: "width 0.2s ease-out",
                    boxShadow: `0 0 10px ${seg.color}66`,
                  }}
                />
              );
            })}
          </div>

          {/* Legend / Values List */}
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              gap: 12,
              marginTop: 16,
              flexWrap: "wrap",
            }}
          >
            {segmentList.map((seg, i) => {
              const pct = Math.round((Math.abs(seg.value) / total) * 100);
              return (
                <div key={i} style={{ display: "flex", alignItems: "center", gap: 8 }}>
                  <div
                    style={{
                      width: 10,
                      height: 10,
                      borderRadius: 2,
                      backgroundColor: seg.color,
                      boxShadow: `0 0 6px ${seg.color}`,
                    }}
                  />
                  <div>
                    <span
                      style={{
                        fontFamily: handDrawn.font.body,
                        fontSize: 12,
                        color: handDrawn.colors.inkMuted,
                        marginRight: 6,
                      }}
                    >
                      {seg.label}
                    </span>
                    <span
                      style={{
                        fontFamily: handDrawn.font.body,
                        fontSize: 12,
                        fontWeight: 600,
                        color: handDrawn.colors.ink,
                      }}
                    >
                      {pct}%
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </>
      ) : (
        <div style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center", color: handDrawn.colors.inkMuted, fontSize: 14 }}>
          {title || "Chart Data"}
        </div>
      )}
    </div>
  );
};
