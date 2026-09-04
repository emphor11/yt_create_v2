import {
  AbsoluteFill,
  Easing,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { type ChartsProps } from "./types";
import { tokens } from "./design-tokens";

/**
 * Format numeric value with unit
 */
function formatChartVal(val: number, unit?: string): string {
  const isFloat = val % 1 !== 0;
  const numStr = isFloat ? val.toFixed(1) : Math.round(val).toLocaleString();
  if (!unit) return numStr;
  if (unit.startsWith("$") || unit.startsWith("₹") || unit.startsWith("€")) {
    return `${unit.charAt(0)}${numStr}${unit.slice(1)}`;
  }
  return `${numStr} ${unit}`;
}

export function Charts(props: ChartsProps | any) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Normalize boundary props wrapper
  const resolvedProps: ChartsProps = props.props
    ? props.props
    : props.chartType || props.labels
    ? props
    : (props as any).renderSpec?.props || props;

  const duration_frames = (props as any).duration_frames || 180;

  const headerLabel = resolvedProps.headerLabel || "";
  const chartType = (resolvedProps.chartType || "bar").toLowerCase();
  const rawLabels: string[] = resolvedProps.labels || [];
  const rawValues: (number | string)[] = resolvedProps.values || [];
  const unit = resolvedProps.unit || "";
  const footerLabel = resolvedProps.footerLabel || "";
  const annotation = resolvedProps.annotation || "";

  const count = Math.max(rawLabels.length, rawValues.length, 1);
  const labels = Array.from({ length: count }, (_, idx) => rawLabels[idx] ?? `Point ${idx + 1}`);

  // Safely parse numeric values
  const numericValues: number[] = Array.from({ length: count }, (_, idx) => {
    const v = rawValues[idx];
    if (typeof v === "number") return v;
    if (v !== undefined) {
      const parsed = parseFloat(String(v).replace(/[^0-9.-]/g, ""));
      if (!isNaN(parsed)) return parsed;
    }
    return 0;
  });

  // Calculate Highlight Index
  let highlightIdx = resolvedProps.highlightIndex;
  if (highlightIdx === undefined && resolvedProps.highlightLabel) {
    const found = labels.findIndex(
      (l) => l.toLowerCase() === String(resolvedProps.highlightLabel).toLowerCase()
    );
    if (found !== -1) highlightIdx = found;
  }

  // Min / Max for smart baseline calculation
  const rawMin = Math.min(...numericValues, 0);
  const rawMax = Math.max(...numericValues, 1);
  const valRange = rawMax - rawMin || 1;

  // Staggered Animation Timeline
  const lineDrawProgress = interpolate(
    frame,
    [0, Math.round(duration_frames * 0.45)],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.bezier(0.16, 1, 0.3, 1) }
  );

  const annotationSpring = spring({
    frame: Math.max(0, frame - Math.round(duration_frames * 0.4)),
    fps,
    config: { damping: 12, stiffness: 110 },
  });

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
        {/* Header */}
        {headerLabel ? (
          <header>
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

        {/* 1. HORIZONTAL BAR CHART (New Editorial Ranking Mode) */}
        {chartType === "horizontal_bar" && (
          <main
            style={{
              position: "relative",
              display: "flex",
              flexDirection: "column",
              justifyContent: "center",
              gap: count >= 5 ? "12px" : "18px",
              flex: 1,
              margin: "16px 0",
            }}
          >
            {labels.map((label, idx) => {
              const val = numericValues[idx];
              const isHighlight = highlightIdx !== undefined ? highlightIdx === idx : idx === 0;

              const itemDelay = idx * 6;
              const barSpring = spring({
                frame: Math.max(0, frame - itemDelay),
                fps,
                config: { damping: 15, stiffness: 95 },
              });

              const targetWidthPercent = Math.max(6, (val / rawMax) * 100);
              const barColor = isHighlight ? "#f59e0b" : "#3b82f6";

              return (
                <div
                  key={idx}
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    opacity: barSpring,
                    transform: `translateX(${(1 - barSpring) * -20}px)`,
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6 }}>
                    <span
                      style={{
                        fontSize: count >= 5 ? 20 : 24,
                        fontWeight: isHighlight ? 900 : 700,
                        color: isHighlight ? "#ffffff" : tokens.text.primary,
                      }}
                    >
                      {label}
                    </span>
                    <span
                      style={{
                        fontSize: count >= 5 ? 20 : 24,
                        fontWeight: 900,
                        color: isHighlight ? "#f59e0b" : tokens.text.primary,
                      }}
                    >
                      {formatChartVal(val, unit)}
                    </span>
                  </div>

                  {/* Horizontal Bar Track */}
                  <div
                    style={{
                      width: "100%",
                      height: isHighlight ? "12px" : "8px",
                      background: "rgba(255, 255, 255, 0.08)",
                      borderRadius: "6px",
                      overflow: "hidden",
                    }}
                  >
                    <div
                      style={{
                        width: `${barSpring * targetWidthPercent}%`,
                        height: "100%",
                        background: isHighlight
                          ? "linear-gradient(90deg, #f59e0b 0%, #fbbf24 100%)"
                          : "linear-gradient(90deg, #3b82f6 0%, #60a5fa 100%)",
                        borderRadius: "6px",
                        boxShadow: isHighlight ? "0 0 12px rgba(245, 158, 11, 0.4)" : "none",
                      }}
                    />
                  </div>
                </div>
              );
            })}
          </main>
        )}

        {/* 2. VERTICAL BAR CHART */}
        {chartType === "bar" && (
          <main
            style={{
              position: "relative",
              display: "flex",
              flexDirection: "column",
              justifyContent: "center",
              flex: 1,
              margin: "20px 0",
            }}
          >
            <div
              style={{
                position: "relative",
                display: "flex",
                alignItems: "flex-end",
                justifyContent: "space-around",
                height: "360px",
                paddingBottom: "40px",
                borderBottom: "2px solid rgba(255, 255, 255, 0.15)",
              }}
            >
              {labels.map((label, idx) => {
                const val = numericValues[idx];
                const isHighlight = highlightIdx !== undefined ? highlightIdx === idx : false;

                const itemDelay = idx * 6;
                const barSpring = spring({
                  frame: Math.max(0, frame - itemDelay),
                  fps,
                  config: { damping: 15, stiffness: 95 },
                });

                const heightPercent = Math.max(8, (val / rawMax) * 100);
                const barColor = isHighlight ? "#f59e0b" : tokens.accent.blue;

                return (
                  <div
                    key={idx}
                    style={{
                      position: "relative",
                      display: "flex",
                      flexDirection: "column",
                      alignItems: "center",
                      height: "100%",
                      justifyContent: "flex-end",
                      flex: 1,
                      maxWidth: "160px",
                    }}
                  >
                    {/* Value Badge on top */}
                    <div
                      style={{
                        fontSize: 22,
                        fontWeight: 900,
                        color: isHighlight ? "#f59e0b" : "#ffffff",
                        marginBottom: 10,
                        opacity: barSpring,
                      }}
                    >
                      {formatChartVal(val, unit)}
                    </div>

                    {/* Bar */}
                    <div
                      style={{
                        width: "60px",
                        height: `${barSpring * heightPercent}%`,
                        background: isHighlight
                          ? "linear-gradient(0deg, #b45309 0%, #f59e0b 100%)"
                          : "linear-gradient(0deg, #1d4ed8 0%, #3b82f6 100%)",
                        borderRadius: "8px 8px 0 0",
                        boxShadow: isHighlight ? "0 0 20px rgba(245, 158, 11, 0.4)" : "none",
                      }}
                    />

                    {/* Label below axis */}
                    <div
                      style={{
                        position: "absolute",
                        bottom: "-36px",
                        fontSize: 18,
                        fontWeight: 700,
                        color: isHighlight ? "#ffffff" : tokens.text.secondary,
                      }}
                    >
                      {label}
                    </div>
                  </div>
                );
              })}
            </div>
          </main>
        )}

        {/* 3. LINE CHART (Chronological Drawing & Y-Axis Reference Ticks) */}
        {chartType === "line" && (() => {
          const width = 1100;
          const height = 320;
          const padding = 50;

          const points = numericValues.map((val, idx) => {
            const x = padding + (idx / Math.max(1, count - 1)) * (width - 2 * padding);
            const normalizedY = (val - rawMin) / valRange;
            const y = height - padding - normalizedY * (height - 2 * padding);
            return { x, y, val, label: labels[idx], idx };
          });

          // SVG Path string
          const pathD = points.reduce((acc, pt, idx) => {
            return idx === 0 ? `M ${pt.x} ${pt.y}` : `${acc} L ${pt.x} ${pt.y}`;
          }, "");

          return (
            <main
              style={{
                position: "relative",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                flex: 1,
                margin: "20px 0",
              }}
            >
              <div style={{ position: "relative", width: `${width}px`, height: `${height}px` }}>
                {/* Reference Grid Lines & Y-Axis Ticks */}
                {[0, 0.5, 1].map((pct, i) => {
                  const tickVal = rawMin + (1 - pct) * valRange;
                  const lineY = padding + pct * (height - 2 * padding);

                  return (
                    <div key={i}>
                      <div
                        style={{
                          position: "absolute",
                          left: `${padding}px`,
                          right: `${padding}px`,
                          top: `${lineY}px`,
                          height: "1px",
                          background: "rgba(255, 255, 255, 0.1)",
                        }}
                      />
                      <span
                        style={{
                          position: "absolute",
                          left: "0px",
                          top: `${lineY - 10}px`,
                          fontSize: 14,
                          color: tokens.text.muted,
                          fontWeight: 600,
                        }}
                      >
                        {formatChartVal(tickVal, unit)}
                      </span>
                    </div>
                  );
                })}

                {/* Line Path SVG */}
                <svg width={width} height={height} style={{ overflow: "visible" }}>
                  <path
                    d={pathD}
                    fill="none"
                    stroke={tokens.accent.blue}
                    strokeWidth="4"
                    strokeLinecap="round"
                    strokeDasharray="2000"
                    strokeDashoffset={2000 * (1 - lineDrawProgress)}
                  />

                  {/* Data Points */}
                  {points.map((pt, idx) => {
                    const nodeRevealed = lineDrawProgress >= idx / Math.max(1, count - 1);
                    const isHighlight = highlightIdx !== undefined ? highlightIdx === idx : idx === count - 1;

                    return (
                      <g key={idx} style={{ opacity: nodeRevealed ? 1 : 0, transition: "opacity 0.2s" }}>
                        <circle
                          cx={pt.x}
                          cy={pt.y}
                          r={isHighlight ? "9" : "6"}
                          fill={isHighlight ? "#f59e0b" : "#ffffff"}
                          stroke={tokens.accent.blue}
                          strokeWidth="3"
                        />

                        {/* Value Text */}
                        <text
                          x={pt.x}
                          y={pt.y - 18}
                          textAnchor="middle"
                          fill={isHighlight ? "#f59e0b" : "#ffffff"}
                          fontSize={isHighlight ? "20" : "16"}
                          fontWeight="900"
                        >
                          {formatChartVal(pt.val, unit)}
                        </text>

                        {/* X-Axis Label */}
                        <text
                          x={pt.x}
                          y={height - 10}
                          textAnchor="middle"
                          fill={tokens.text.secondary}
                          fontSize="16"
                          fontWeight="700"
                        >
                          {pt.label}
                        </text>
                      </g>
                    );
                  })}
                </svg>
              </div>
            </main>
          );
        })()}

        {/* 4. DONUT / PIE CHART */}
        {(chartType === "pie" || chartType === "donut") && (() => {
          const totalSum = numericValues.reduce((acc, curr) => acc + curr, 0) || 1;
          let currentAngle = 0;

          return (
            <main
              style={{
                position: "relative",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                gap: "60px",
                flex: 1,
                margin: "20px 0",
              }}
            >
              {/* Donut Graphic */}
              <div
                style={{
                  position: "relative",
                  width: "280px",
                  height: "280px",
                  borderRadius: "50%",
                  background: `conic-gradient(${numericValues
                    .map((val, idx) => {
                      const start = currentAngle;
                      const pct = (val / totalSum) * 360;
                      currentAngle += pct;
                      const colors = ["#3b82f6", "#10b981", "#f59e0b", "#a855f7", "#06b6d4"];
                      const c = colors[idx % colors.length];
                      return `${c} ${start}deg ${currentAngle}deg`;
                    })
                    .join(", ")})`,
                  boxShadow: "0 10px 30px rgba(0,0,0,0.3)",
                }}
              >
                {/* Donut Center Hole */}
                <div
                  style={{
                    position: "absolute",
                    inset: "40px",
                    borderRadius: "50%",
                    background: tokens.bg.base,
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    justifyContent: "center",
                  }}
                >
                  <div style={{ fontSize: 32, fontWeight: 900, color: "#ffffff" }}>
                    {resolvedProps.centerValue || formatChartVal(totalSum, unit)}
                  </div>
                  <div style={{ fontSize: 14, color: tokens.text.muted, fontWeight: 700, textTransform: "uppercase" }}>
                    {resolvedProps.centerLabel || "TOTAL"}
                  </div>
                </div>
              </div>

              {/* Editorial Legend */}
              <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
                {labels.map((lbl, idx) => {
                  const colors = ["#3b82f6", "#10b981", "#f59e0b", "#a855f7", "#06b6d4"];
                  const c = colors[idx % colors.length];
                  const val = numericValues[idx];
                  const pct = Math.round((val / totalSum) * 100);

                  return (
                    <div key={idx} style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                      <div style={{ width: "12px", height: "12px", borderRadius: "50%", background: c }} />
                      <span style={{ fontSize: 20, fontWeight: 700, color: "#ffffff" }}>{lbl}</span>
                      <span style={{ fontSize: 18, color: tokens.text.secondary, marginLeft: "auto" }}>
                        {pct}% ({formatChartVal(val, unit)})
                      </span>
                    </div>
                  );
                })}
              </div>
            </main>
          );
        })()}

        {/* Floating Story Callout Annotation */}
        {annotation ? (
          <div
            style={{
              textAlign: "center",
              opacity: annotationSpring,
              transform: `translateY(${(1 - annotationSpring) * 15}px)`,
              marginBottom: 10,
            }}
          >
            <div
              style={{
                display: "inline-block",
                fontSize: 20,
                fontWeight: 900,
                color: "#f59e0b",
                background: "rgba(245, 158, 11, 0.15)",
                border: "1px solid #f59e0b",
                padding: "6px 20px",
                borderRadius: "20px",
                letterSpacing: 1,
              }}
            >
              ▲ {annotation}
            </div>
          </div>
        ) : null}

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
