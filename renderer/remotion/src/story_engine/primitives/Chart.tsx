import React from "react";
import type { ChartProps } from "../types.ts";
import { handDrawn } from "../hand-drawn-theme.ts";

export interface ChartPrimitiveProps {
  props: ChartProps;
  progress?: number; // 0 to 1 progress for line drawing or bar fill
  activePointIndex?: number;
  width?: number;
  height?: number;
  layout?: string;
  style?: React.CSSProperties;
}

function formatCurrencyVal(val: number): string {
  if (Math.abs(val) >= 10000000) {
    return `₹${(val / 10000000).toFixed(2)} Cr`;
  }
  if (Math.abs(val) >= 100000) {
    return `₹${(val / 100000).toFixed(1)}L`;
  }
  if (Math.abs(val) >= 1000) {
    return `₹${(val / 1000).toFixed(0)}K`;
  }
  return `₹${Math.round(val)}`;
}

export const ChartPrimitive: React.FC<ChartPrimitiveProps> = ({
  props,
  progress = 1,
  activePointIndex,
  width,
  height,
  layout,
  style,
}) => {
  const { chartType, title, subtitle, series, segments, totalValue, accentColor } = props;
  const themeColor = accentColor || handDrawn.colors.teal;

  const containerW = width ?? 560;
  const containerH = height ?? 280;
  const isHero = layout === "center" || containerH >= 400;
  const isPanoramic = layout === "full_bottom" || containerW >= 1200 || isHero;

  // ----------------------------------------------------
  // 1. Trajectory Area Chart (e.g. 20-Year Loan Burden or Cumulative Savings)
  // ----------------------------------------------------
  const trajectoryPoints =
    series && series.length > 0 && series[0].points && series[0].points.length > 0
      ? series[0].points
      : ((props as any).points as typeof series extends (infer S)[] ? S extends { points: infer P } ? P : never : never);

  if (chartType === "trajectory_area" && trajectoryPoints && trajectoryPoints.length > 0) {
    const points = trajectoryPoints;
    const yValues = points.map((p) => p.yValue ?? (p as any).value ?? 0);
    const minY = 0;
    const maxY = Math.max(1, Math.max(...yValues) * 1.15);

    // Dynamic responsive dimensions matching container slot
    const cardPaddingX = isPanoramic ? 32 : 24;
    const cardPaddingY = isPanoramic ? 16 : 22;
    const headerHeight = title ? (isPanoramic ? 46 : 64) : 12;

    const svgW = containerW - cardPaddingX * 2;
    const svgH = Math.max(90, containerH - cardPaddingY * 2 - headerHeight);

    const padX = isPanoramic ? 70 : 44;
    const padYTop = 16;
    const padYBottom = 26;
    const plotW = Math.max(100, svgW - padX * 2);
    const plotH = Math.max(45, svgH - padYTop - padYBottom);

    // Coordinate mapping mapped directly to allocated viewport pixels
    const divisor = Math.max(1, points.length - 1);
    const coords = points.map((p, idx) => {
      const val = p.yValue ?? (p as any).value ?? 0;
      const px = padX + (idx / divisor) * plotW;
      const py = padYTop + plotH - ((val - minY) / (maxY - minY)) * plotH;
      return { x: px, y: py, label: p.xLabel ?? (p as any).label ?? `Pt ${idx + 1}`, value: val };
    });

    // Generate smooth SVG curve path
    const pathD = coords.reduce((acc, pt, i, arr) => {
      if (i === 0) return `M ${pt.x} ${pt.y}`;
      const prev = arr[i - 1];
      const cx = (prev.x + pt.x) / 2;
      return `${acc} C ${cx} ${prev.y}, ${cx} ${pt.y}, ${pt.x} ${pt.y}`;
    }, "");

    const areaD = `${pathD} L ${coords[coords.length - 1].x} ${padYTop + plotH} L ${coords[0].x} ${padYTop + plotH} Z`;

    const activeIdx = activePointIndex ?? Math.min(coords.length - 1, Math.floor(progress * (coords.length - 1)));
    const activeCoord = coords[activeIdx];
    const lastPoint = points[points.length - 1];

    return (
      <div
        style={{
          width: "100%",
          height: "100%",
          backgroundColor: handDrawn.colors.paperAlt,
          borderRadius: handDrawn.radius.card,
          border: `2px solid ${handDrawn.colors.ink}`,
          boxShadow: handDrawn.shadow.paper,
          padding: `${cardPaddingY}px ${cardPaddingX}px`,
          display: "flex",
          flexDirection: "column",
          position: "relative",
          overflow: "hidden",
          boxSizing: "border-box",
          ...style,
        }}
      >
        {/* Responsive Header */}
        {(title || subtitle) && (
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "flex-start",
              marginBottom: isPanoramic ? 6 : 10,
            }}
          >
            <div>
              {title && (
                <div
                  style={{
                    fontFamily: handDrawn.font.label,
                    fontSize: isPanoramic ? 15 : 16,
                    fontWeight: 700,
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
                    fontSize: 12,
                    color: handDrawn.colors.inkMuted,
                    marginTop: 2,
                  }}
                >
                  {subtitle}
                </div>
              )}
            </div>

            {isPanoramic && lastPoint && (
              <div
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: 8,
                  padding: "4px 12px",
                  borderRadius: 6,
                  backgroundColor: `${themeColor}15`,
                  border: `1px solid ${themeColor}40`,
                }}
              >
                <span style={{ fontSize: 11, fontFamily: handDrawn.font.body, color: handDrawn.colors.inkMuted, textTransform: "uppercase" }}>
                  Horizon Peak
                </span>
                <span style={{ fontSize: 13, fontFamily: handDrawn.font.label, fontWeight: 700, color: themeColor }}>
                  {formatCurrencyVal(lastPoint.yValue ?? (lastPoint as any).value ?? 0)}
                </span>
              </div>
            )}
          </div>
        )}

        {/* Dynamic Responsive SVG Plot */}
        <div style={{ flex: 1, position: "relative", width: "100%", height: "100%", overflow: "hidden" }}>
          <svg
            viewBox={`0 0 ${svgW} ${svgH}`}
            preserveAspectRatio="none"
            style={{ width: "100%", height: "100%", display: "block", overflow: "visible" }}
          >
            <defs>
              <linearGradient id="curveGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={themeColor} stopOpacity="0.38" />
                <stop offset="100%" stopColor={themeColor} stopOpacity="0.02" />
              </linearGradient>
              <filter id="glowFilter" x="-20%" y="-20%" width="140%" height="140%">
                <feGaussianBlur stdDeviation="3.5" result="blur" />
                <feComposite in="SourceGraphic" in2="blur" operator="over" />
              </filter>
            </defs>

            {/* Horizontal Gridlines & Y-Axis Baseline Ticks */}
            {[0, 0.5, 1].map((pct, i) => {
              const gy = padYTop + plotH * (1 - pct);
              const tickVal = minY + (maxY - minY) * pct;
              return (
                <g key={i}>
                  <line
                    x1={padX}
                    y1={gy}
                    x2={padX + plotW}
                    y2={gy}
                    stroke="#D6C9B5"
                    strokeDasharray="4 6"
                    strokeWidth="1"
                  />
                  <text
                    x={padX - 8}
                    y={gy + 4}
                    textAnchor="end"
                    fill={handDrawn.colors.inkMuted}
                    fontSize="10"
                    fontFamily={handDrawn.font.body}
                  >
                    {formatCurrencyVal(tickVal)}
                  </text>
                </g>
              );
            })}

            {/* Gradient Area Fill */}
            <path d={areaD} fill="url(#curveGradient)" />

            {/* Main Dynamic Line */}
            <path
              d={pathD}
              fill="none"
              stroke={themeColor}
              strokeWidth={isPanoramic ? "4" : "3.5"}
              strokeLinecap="round"
              filter="url(#glowFilter)"
            />

            {/* Milestone Nodes & X-Axis Labels */}
            {coords.map((pt, i) => {
              const isSelected = i === activeIdx;
              return (
                <g key={i}>
                  <circle
                    cx={pt.x}
                    cy={pt.y}
                    r={isSelected ? 6.5 : 4}
                    fill={isSelected ? "#FFFFFF" : themeColor}
                    stroke={themeColor}
                    strokeWidth={isSelected ? 3 : 1}
                  />
                  <text
                    x={pt.x}
                    y={padYTop + plotH + 18}
                    textAnchor="middle"
                    fill={isSelected ? handDrawn.colors.ink : handDrawn.colors.inkMuted}
                    fontSize={isPanoramic ? "12" : "11"}
                    fontWeight={isSelected ? "700" : "500"}
                    fontFamily={handDrawn.font.body}
                  >
                    {pt.label}
                  </text>
                </g>
              );
            })}

            {/* Active Data Callout Tooltip */}
            {activeCoord && (
              <g>
                <line
                  x1={activeCoord.x}
                  y1={padYTop}
                  x2={activeCoord.x}
                  y2={padYTop + plotH}
                  stroke={themeColor}
                  strokeDasharray="3 3"
                  strokeWidth="1.5"
                  opacity="0.8"
                />
                <rect
                  x={Math.max(8, Math.min(svgW - 108, activeCoord.x - 50))}
                  y={Math.max(4, activeCoord.y - 28)}
                  width="100"
                  height="22"
                  rx="5"
                  fill={handDrawn.colors.paperAlt}
                  stroke={themeColor}
                  strokeWidth="1.5"
                  filter="drop-shadow(0 2px 4px rgba(0,0,0,0.15))"
                />
                <text
                  x={Math.max(8, Math.min(svgW - 108, activeCoord.x - 50)) + 50}
                  y={Math.max(4, activeCoord.y - 28) + 15}
                  textAnchor="middle"
                  fill={handDrawn.colors.ink}
                  fontSize="11"
                  fontWeight="700"
                  fontFamily={handDrawn.font.label}
                >
                  {formatCurrencyVal(activeCoord.value)}
                </text>
              </g>
            )}
          </svg>
        </div>
      </div>
    );
  }

  // ----------------------------------------------------
  // 2. Split Bar / Stack / Multi Bar Breakdown
  // ----------------------------------------------------
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
  const barHeight = isHero ? 52 : isPanoramic ? 38 : (containerH > 300 ? 32 : 24);

  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        backgroundColor: handDrawn.colors.paperAlt,
        borderRadius: handDrawn.radius.card,
        border: `${isHero ? 3 : 2}px solid ${handDrawn.colors.ink}`,
        boxShadow: handDrawn.shadow.paper,
        padding: isHero ? "28px 36px" : isPanoramic ? "18px 32px" : "22px 24px",
        display: "flex",
        flexDirection: "column",
        justifyContent: "space-between",
        boxSizing: "border-box",
        ...style,
      }}
    >
      {/* Header */}
      <div>
        {title && (
          <div
            style={{
              fontFamily: handDrawn.font.label,
              fontSize: isHero ? 24 : isPanoramic ? 15 : 16,
              fontWeight: 800,
              color: handDrawn.colors.ink,
              letterSpacing: "0.05em",
              textTransform: "uppercase",
              marginBottom: isHero ? 6 : 4,
            }}
          >
            {title}
          </div>
        )}
        {subtitle && (
          <div
            style={{
              fontFamily: handDrawn.font.body,
              fontSize: isHero ? 15 : 12,
              color: handDrawn.colors.inkMuted,
              marginBottom: isHero ? 14 : isPanoramic ? 8 : 12,
            }}
          >
            {subtitle}
          </div>
        )}
      </div>

      {segmentList.length > 0 ? (
        <>
          {/* Prominent High-Density Segmented Progress Track */}
          <div
            style={{
              width: "100%",
              height: barHeight,
              borderRadius: barHeight / 2,
              backgroundColor: handDrawn.colors.paperDeep,
              overflow: "hidden",
              display: "flex",
              alignItems: "center",
              boxShadow: "inset 0 2px 4px rgba(32,37,34,0.12)",
              border: `1px solid ${handDrawn.colors.ink}22`,
            }}
          >
            {segmentList.map((seg, i) => {
              const pct = (Math.abs(seg.value) / total) * 100 * Math.min(1, Math.max(0, progress));
              const roundedPct = Math.round((Math.abs(seg.value) / total) * 100);
              return (
                <div
                  key={i}
                  style={{
                    width: `${pct}%`,
                    height: "100%",
                    backgroundColor: seg.color,
                    transition: "width 0.25s ease-out",
                    boxShadow: `0 0 10px ${seg.color}55`,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    overflow: "hidden",
                  }}
                >
                  {/* Inline Percentage Badge when segment is wide enough */}
                  {pct > 9 && (
                    <span
                      style={{
                        color: "#FFFFFF",
                        fontFamily: handDrawn.font.label,
                        fontSize: isHero ? 17 : isPanoramic ? 13 : 11,
                        fontWeight: 700,
                        textShadow: "0 1px 2px rgba(0,0,0,0.5)",
                        letterSpacing: "0.02em",
                        whiteSpace: "nowrap",
                      }}
                    >
                      {roundedPct}%
                    </span>
                  )}
                </div>
              );
            })}
          </div>

          {/* Panoramic / Responsive Stats & Legend Grid */}
          {isPanoramic ? (
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                gap: isHero ? 20 : 16,
                marginTop: isHero ? 16 : 10,
                flexWrap: "nowrap",
              }}
            >
              {segmentList.map((seg, i) => {
                const pct = Math.round((Math.abs(seg.value) / total) * 100);
                return (
                  <div
                    key={i}
                    style={{
                      flex: 1,
                      minWidth: isHero ? 180 : 140,
                      padding: isHero ? "14px 20px" : "8px 14px",
                      backgroundColor: handDrawn.colors.paperDeep,
                      borderRadius: isHero ? 10 : 8,
                      border: `1.5px solid ${seg.color}44`,
                      display: "flex",
                      alignItems: "center",
                      gap: isHero ? 16 : 12,
                    }}
                  >
                    <div
                      style={{
                        width: isHero ? 8 : 6,
                        height: isHero ? 28 : 20,
                        borderRadius: 3,
                        backgroundColor: seg.color,
                        flexShrink: 0,
                      }}
                    />
                    <div style={{ display: "flex", flexDirection: "column" }}>
                      <span
                        style={{
                          fontFamily: handDrawn.font.label,
                          fontSize: isHero ? 22 : 15,
                          fontWeight: 800,
                          color: handDrawn.colors.ink,
                          lineHeight: 1.1,
                        }}
                      >
                        {pct}%
                      </span>
                      <span
                        style={{
                          fontFamily: handDrawn.font.body,
                          fontSize: isHero ? 14 : 11,
                          color: handDrawn.colors.inkMuted,
                          marginTop: 2,
                          whiteSpace: "nowrap",
                          overflow: "hidden",
                          textOverflow: "ellipsis",
                        }}
                      >
                        {seg.label}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                gap: 12,
                marginTop: 12,
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
                          fontWeight: 700,
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
          )}
        </>
      ) : (
        <div style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center", color: handDrawn.colors.inkMuted, fontSize: 14 }}>
          {title || "Chart Data"}
        </div>
      )}
    </div>
  );
};
