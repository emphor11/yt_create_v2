import {
  AbsoluteFill,
  Easing,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { type ChartsRenderSpec } from "./types";
import { tokens } from "./design-tokens";

export function Charts(renderSpec: ChartsRenderSpec) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const duration_frames = renderSpec.duration_frames || 180;
  const props = renderSpec.props as any;

  // Extract exact component properties
  const headerLabel = props.headerLabel || "";
  const chartType = (props.chartType || "bar").toLowerCase();
  const rawLabels: string[] = props.labels || [];
  const rawValues: (number | string)[] = props.values || [];
  const unit = props.unit || "";
  const footerLabel = props.footerLabel || "";

  const count = Math.max(rawLabels.length, rawValues.length, 1);
  const labels = Array.from({ length: count }, (_, idx) => rawLabels[idx] ?? "");

  // Parse numeric values safely for proportional scaling
  const numericValues: number[] = Array.from({ length: count }, (_, idx) => {
    const v = rawValues[idx];
    if (typeof v === "number") return v;
    if (v !== undefined) {
      const parsed = parseFloat(String(v).replace(/[^0-9.-]/g, ""));
      if (!isNaN(parsed)) return parsed;
    }
    return 0;
  });
  const maxVal = Math.max(...numericValues, 1);
  const totalSum = numericValues.reduce((acc, curr) => acc + curr, 0) || 1;

  const barColors = [
    { main: tokens.accent.emerald, glow: "rgba(16, 185, 129, 0.4)", gradient: "linear-gradient(0deg, #047857 0%, #10b981 100%)", hex: "#10b981" },
    { main: tokens.accent.cyan, glow: "rgba(6, 182, 212, 0.4)", gradient: "linear-gradient(0deg, #0e7490 0%, #06b6d4 100%)", hex: "#06b6d4" },
    { main: tokens.accent.blue, glow: "rgba(59, 130, 246, 0.4)", gradient: "linear-gradient(0deg, #1d4ed8 0%, #3b82f6 100%)", hex: "#3b82f6" },
    { main: tokens.accent.purple, glow: "rgba(168, 85, 247, 0.4)", gradient: "linear-gradient(0deg, #7e22ce 0%, #a855f7 100%)", hex: "#a855f7" },
    { main: tokens.accent.amber, glow: "rgba(245, 158, 11, 0.4)", gradient: "linear-gradient(0deg, #b45309 0%, #f59e0b 100%)", hex: "#f59e0b" },
  ];

  // Synchronized animation progress
  const progress = interpolate(
    frame,
    [0, Math.round(duration_frames * 0.35)],
    [0, 1],
    {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
      easing: Easing.bezier(0.16, 1, 0.3, 1),
    }
  );

  return (
    <AbsoluteFill
      style={{
        background: tokens.bg.base,
        backdropFilter: "blur(4px)",
        color: tokens.text.primary,
        fontFamily: tokens.font.family,
        overflow: "hidden",
        padding: tokens.spacing.padding,
      }}
    >
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          height: "100%",
          justifyContent: "space-between",
        }}
      >
        {headerLabel ? (
          <header>
            <div
              style={{
                color: tokens.accent.emerald,
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

        {/* 1. LINE CHART RENDERER */}
        {chartType === "line" && (
          <main
            style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              flex: 1,
              margin: "20px 0",
              position: "relative",
            }}
          >
            <svg
              viewBox="0 0 1100 450"
              style={{ width: "100%", maxHeight: "450px", overflow: "visible" }}
            >
              <defs>
                <linearGradient id="lineAreaGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#06b6d4" stopOpacity="0.45" />
                  <stop offset="100%" stopColor="#06b6d4" stopOpacity="0.0" />
                </linearGradient>
              </defs>

              {/* Grid Lines */}
              <line x1="60" y1="380" x2="1040" y2="380" stroke="rgba(255,255,255,0.15)" strokeWidth="2" />
              <line x1="60" y1="230" x2="1040" y2="230" stroke="rgba(255,255,255,0.06)" strokeWidth="1" strokeDasharray="6 6" />
              <line x1="60" y1="80" x2="1040" y2="80" stroke="rgba(255,255,255,0.06)" strokeWidth="1" strokeDasharray="6 6" />

              {/* Compute Points */}
              {(() => {
                const svgW = 980;
                const svgH = 300;
                const startX = 60;
                const startY = 80;
                const stepX = count > 1 ? svgW / (count - 1) : svgW / 2;

                const points = numericValues.map((val, i) => {
                  const x = startX + (count > 1 ? i * stepX : svgW / 2);
                  const normY = (val / maxVal) * svgH * progress;
                  const y = startY + svgH - normY;
                  return { x, y, val: rawValues[i] ?? val, label: labels[i] };
                });

                const pathD = points.map((p, idx) => `${idx === 0 ? "M" : "L"} ${p.x} ${p.y}`).join(" ");
                const areaD = `${pathD} L ${points[points.length - 1].x} 380 L ${points[0].x} 380 Z`;

                return (
                  <>
                    {/* Area under curve */}
                    <path d={areaD} fill="url(#lineAreaGrad)" />

                    {/* Glowing Stroke line */}
                    <path
                      d={pathD}
                      fill="none"
                      stroke="#06b6d4"
                      strokeWidth="5"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      style={{ filter: "drop-shadow(0 0 12px rgba(6, 182, 212, 0.7))" }}
                    />

                    {/* Dots and Labels */}
                    {points.map((p, idx) => {
                      const displayVal = typeof p.val === "number" ? p.val.toLocaleString() : String(p.val);
                      return (
                        <g key={idx}>
                          {/* Value above point */}
                          <text
                            x={p.x}
                            y={p.y - 20}
                            fill="#38bdf8"
                            fontSize="26"
                            fontWeight="900"
                            textAnchor="middle"
                            opacity={progress}
                          >
                            {displayVal}{unit ? ` ${unit}` : ""}
                          </text>

                          {/* Glowing node dot */}
                          <circle
                            cx={p.x}
                            cy={p.y}
                            r="8"
                            fill="#06b6d4"
                            stroke="#ffffff"
                            strokeWidth="3"
                            style={{ filter: "drop-shadow(0 0 8px #06b6d4)" }}
                          />

                          {/* X-axis Label below axis */}
                          <text
                            x={p.x}
                            y={415}
                            fill={tokens.text.secondary}
                            fontSize="20"
                            fontWeight="700"
                            textAnchor="middle"
                            letterSpacing="1"
                          >
                            {p.label}
                          </text>
                        </g>
                      );
                    })}
                  </>
                );
              })()}
            </svg>
          </main>
        )}

        {/* 2. PIE / DONUT CHART RENDERER */}
        {chartType === "pie" && (
          <main
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-around",
              flex: 1,
              margin: "20px 0",
              gap: 40,
            }}
          >
            {/* Donut SVG */}
            {(() => {
              const radius = 140;
              const circumference = 2 * Math.PI * radius;
              let accumulatedPct = 0;

              return (
                <div style={{ position: "relative", width: "360px", height: "360px", display: "flex", alignItems: "center", justifyContent: "center" }}>
                  <svg viewBox="0 0 360 360" style={{ transform: "rotate(-90deg)", width: "100%", height: "100%" }}>
                    {/* Background ring */}
                    <circle cx="180" cy="180" r={radius} fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="36" />

                    {/* Donut Slices */}
                    {numericValues.map((val, idx) => {
                      const slicePct = val / totalSum;
                      const strokeDasharray = `${slicePct * circumference * progress} ${circumference}`;
                      const strokeDashoffset = -(accumulatedPct * circumference * progress);
                      accumulatedPct += slicePct;
                      const colorTheme = barColors[idx % barColors.length];

                      return (
                        <circle
                          key={idx}
                          cx="180"
                          cy="180"
                          r={radius}
                          fill="none"
                          stroke={colorTheme.hex}
                          strokeWidth="36"
                          strokeDasharray={strokeDasharray}
                          strokeDashoffset={strokeDashoffset}
                          style={{
                            filter: `drop-shadow(0 0 10px ${colorTheme.glow})`,
                            transition: "stroke-dasharray 0.2s ease",
                          }}
                        />
                      );
                    })}
                  </svg>

                  {/* Center Text inside Donut */}
                  <div style={{ position: "absolute", textAlign: "center" }}>
                    <div style={{ fontSize: 20, color: tokens.text.secondary, fontWeight: 700, textTransform: "uppercase" }}>
                      Total
                    </div>
                    <div style={{ fontSize: 34, color: tokens.text.primary, fontWeight: 950, marginTop: 4 }}>
                      {totalSum.toLocaleString()}{unit ? ` ${unit}` : ""}
                    </div>
                  </div>
                </div>
              );
            })()}

            {/* Legend List */}
            <div style={{ display: "flex", flexDirection: "column", gap: 20, minWidth: "340px" }}>
              {labels.map((label, idx) => {
                const rawVal = rawValues[idx] ?? numericValues[idx];
                const displayVal = typeof rawVal === "number" ? rawVal.toLocaleString() : String(rawVal);
                const pct = Math.round((numericValues[idx] / totalSum) * 100);
                const colorTheme = barColors[idx % barColors.length];

                return (
                  <div
                    key={idx}
                    style={{
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between",
                      background: "rgba(255,255,255,0.03)",
                      border: "1px solid rgba(255,255,255,0.08)",
                      borderRadius: 12,
                      padding: "16px 24px",
                      opacity: progress,
                    }}
                  >
                    <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
                      <div style={{ width: 16, height: 16, borderRadius: 4, background: colorTheme.hex, boxShadow: `0 0 8px ${colorTheme.glow}` }} />
                      <span style={{ fontSize: 24, fontWeight: 800, color: tokens.text.primary }}>{label}</span>
                    </div>
                    <div style={{ textAlign: "right" }}>
                      <span style={{ fontSize: 24, fontWeight: 950, color: colorTheme.hex }}>{displayVal}{unit ? ` ${unit}` : ""}</span>
                      <span style={{ fontSize: 18, color: tokens.text.secondary, marginLeft: 10, fontWeight: 600 }}>({pct}%)</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </main>
        )}

        {/* 3. BAR CHART RENDERER (Default) */}
        {chartType !== "line" && chartType !== "pie" && (
          <main
            style={{
              display: "flex",
              justifyContent: "center",
              alignItems: "flex-end",
              flex: 1,
              gap: count > 2 ? "60px" : "120px",
              borderBottom: "3px solid rgba(255, 255, 255, 0.15)",
              paddingBottom: "30px",
              margin: "40px 0 20px",
            }}
          >
            {Array.from({ length: count }).map((_, idx) => {
              const rawVal = rawValues[idx] ?? 0;
              const numericVal = numericValues[idx] ?? 0;
              const label = labels[idx] ?? `Item ${idx + 1}`;
              const targetHeightPct = (numericVal / maxVal) * 80;

              const displayVal = typeof rawVal === "number" ? rawVal.toLocaleString() : String(rawVal);
              const colorTheme = barColors[idx % barColors.length];

              return (
                <div
                  key={idx}
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    width: count > 3 ? "140px" : "180px",
                    height: "100%",
                    justifyContent: "flex-end",
                  }}
                >
                  {/* Numeric Value Label above bar */}
                  <div
                    style={{
                      fontSize: 36,
                      fontWeight: 950,
                      color: colorTheme.main,
                      marginBottom: 16,
                      opacity: progress,
                    }}
                  >
                    {displayVal}{unit ? ` ${unit}` : ""}
                  </div>

                  {/* Animated Growing Bar */}
                  <div
                    style={{
                      width: "100%",
                      height: `${targetHeightPct * progress}%`,
                      minHeight: "8px",
                      background: colorTheme.gradient,
                      borderRadius: "12px 12px 0 0",
                      boxShadow: `0 0 30px ${colorTheme.glow}`,
                    }}
                  />

                  {/* Category X-Axis Label */}
                  {label ? (
                    <div
                      style={{
                        marginTop: 20,
                        fontSize: 22,
                        fontWeight: 800,
                        color: tokens.text.secondary,
                        textAlign: "center",
                        textTransform: "uppercase",
                        letterSpacing: 1,
                      }}
                    >
                      {label}
                    </div>
                  ) : null}
                </div>
              );
            })}
          </main>
        )}

        {footerLabel ? (
          <footer style={{ textAlign: "center", fontSize: 24, color: tokens.text.muted, fontWeight: 600 }}>
            {footerLabel}
          </footer>
        ) : null}
      </div>
    </AbsoluteFill>
  );
}
