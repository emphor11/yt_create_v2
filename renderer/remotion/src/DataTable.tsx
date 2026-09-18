import React from "react";
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { type DataTableProps } from "./types";
import { tokens } from "./design-tokens";
import { safeSpringDelay } from "./animation-safety";

/**
 * Format cell value and infer semantic color
 */
function getSemanticCellColor(
  cellVal: string | number,
  isHighlightRow: boolean,
  isHighlightCol: boolean
): { text: string; isNumeric: boolean } {
  const str = String(cellVal).trim();
  const isNumeric = /[\d]/.test(str);

  if (isHighlightRow || isHighlightCol) {
    return { text: "#f59e0b", isNumeric };
  }

  if (str.startsWith("+")) {
    return { text: "#10b981", isNumeric };
  }
  if (str.startsWith("-")) {
    return { text: "#ef4444", isNumeric };
  }

  return { text: isNumeric ? "#ffffff" : tokens.text.primary, isNumeric };
}

export function DataTable(props: DataTableProps | any) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Normalize boundary props wrapper
  const resolvedProps: DataTableProps =
    props?.props && typeof props.props === "object" && !Array.isArray(props.props)
      ? props.props
      : props || {};
  const duration_frames =
    props?.duration_frames || props?.props?.duration_frames || 180;

  const headerLabel = resolvedProps.headerLabel || "";
  const title = resolvedProps.title || "";
  const columns: string[] = Array.isArray(resolvedProps.columns)
    ? resolvedProps.columns
    : ["Company", "Revenue", "Operating Margin"];
  const rows: (string | number)[][] = Array.isArray(resolvedProps.rows)
    ? resolvedProps.rows
    : [
        ["Apple", "$383B", "27%"],
        ["Microsoft", "$245B", "36%"],
        ["Amazon", "$575B", "8%"],
      ];

  const annotation = resolvedProps.annotation || "";
  const footerLabel = resolvedProps.footerLabel || "";

  const colCount = Math.max(1, columns.length);
  const rowCount = rows.length;

  // Resolve Highlight Row Index
  let targetRowIdx = resolvedProps.highlightRow;
  if (targetRowIdx === undefined && resolvedProps.highlightKey) {
    const hk = String(resolvedProps.highlightKey).toLowerCase();
    const found = rows.findIndex((r) => r && String(r[0]).toLowerCase() === hk);
    if (found !== -1) targetRowIdx = found;
  }

  const targetColIdx = resolvedProps.highlightCol;

  // Scene fade in
  const sceneOpacity = interpolate(
    frame,
    [0, Math.min(8, Math.max(1, duration_frames - 1))],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // ─────────────────────────────────────────────────────────────────────────
  // PHASE 1 — HEADER & COLUMN HEADERS ENTRANCE (0 → ~10% D)
  // ─────────────────────────────────────────────────────────────────────────
  const headerDelay = safeSpringDelay(0, duration_frames, 0.08);
  const headerSpring = spring({
    frame: Math.max(0, frame - headerDelay),
    fps,
    config: { damping: 16, stiffness: 110 },
  });

  const colDelay = safeSpringDelay(Math.floor(duration_frames * 0.03), duration_frames, 0.10);
  const colSpring = spring({
    frame: Math.max(0, frame - colDelay),
    fps,
    config: { damping: 16, stiffness: 105 },
  });

  // ─────────────────────────────────────────────────────────────────────────
  // PHASE 2 — SEQUENTIAL ROW DISCLOSURE (8% D → 65% D)
  // ─────────────────────────────────────────────────────────────────────────
  const buildStart = Math.floor(duration_frames * 0.08);
  const buildEnd = Math.floor(duration_frames * 0.65);
  const totalBuildDuration = Math.max(1, buildEnd - buildStart);
  const timePerRow = Math.max(1, Math.floor(totalBuildDuration / Math.max(1, rowCount)));

  // ─────────────────────────────────────────────────────────────────────────
  // PHASE 3 — SPOTLIGHT PAYOFF, ANNOTATION & FOOTER (60% D → 100% D)
  // ─────────────────────────────────────────────────────────────────────────
  const nominalSpotlightStart = Math.max(
    buildStart + timePerRow * Math.min(rowCount, 2),
    Math.floor(duration_frames * 0.60)
  );
  const spotlightDelay = safeSpringDelay(nominalSpotlightStart, duration_frames, 0.72);
  const spotlightSpring = spring({
    frame: Math.max(0, frame - spotlightDelay),
    fps,
    config: { damping: 14, stiffness: 100 },
  });

  const footerDelay = safeSpringDelay(Math.floor(duration_frames * 0.72), duration_frames, 0.85);
  const footerSpring = spring({
    frame: Math.max(0, frame - footerDelay),
    fps,
    config: { damping: 16, stiffness: 90 },
  });

  const cellFontSize = rowCount >= 5 ? 20 : rowCount === 4 ? 24 : 26;
  const headerFontSize = rowCount >= 5 ? 15 : 18;
  const cellPadding = rowCount >= 5 ? "12px 18px" : "18px 24px";
  const gridTemplate = `repeat(${colCount}, 1fr)`;

  return (
    <AbsoluteFill
      style={{
        background: tokens.bg.base,
        color: tokens.text.primary,
        fontFamily: tokens.font.family,
        overflow: "hidden",
        padding: tokens.spacing.padding,
        opacity: sceneOpacity,
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
        {/* Header — Phase 1 */}
        {headerLabel || title ? (
          <header style={{ marginBottom: 12 }}>
            {headerLabel && (
              <div
                style={{
                  color: tokens.accent.blue,
                  fontSize: tokens.font.eyebrow,
                  fontWeight: 800,
                  textTransform: "uppercase",
                  letterSpacing: 2,
                  opacity: headerSpring,
                  transform: `translateY(${(1 - headerSpring) * -8}px)`,
                }}
              >
                {headerLabel}
              </div>
            )}
            {title && (
              <div
                style={{
                  color: tokens.text.primary,
                  fontSize: 28,
                  fontWeight: 800,
                  marginTop: headerLabel ? 4 : 0,
                  letterSpacing: -0.5,
                  opacity: headerSpring,
                  transform: `translateY(${(1 - headerSpring) * -8}px)`,
                }}
              >
                {title}
              </div>
            )}
          </header>
        ) : null}

        {/* Main Editorial Financial Table */}
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
          {/* Table Container */}
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              width: "100%",
            }}
          >
            {/* Table Column Headers (Quiet Uppercase Header) — Phase 1 */}
            <div
              style={{
                display: "grid",
                gridTemplateColumns: gridTemplate,
                padding: "10px 16px",
                borderBottom: "2px solid rgba(255, 255, 255, 0.15)",
                marginBottom: 8,
                opacity: colSpring,
                transform: `translateY(${(1 - colSpring) * -6}px)`,
              }}
            >
              {columns.map((colName, cIdx) => {
                const isHighlightCol = targetColIdx === cIdx;

                return (
                  <div
                    key={cIdx}
                    style={{
                      fontSize: headerFontSize,
                      fontWeight: 800,
                      color: isHighlightCol ? "#f59e0b" : tokens.text.muted,
                      textTransform: "uppercase",
                      letterSpacing: 1.5,
                      textAlign: cIdx === 0 ? "left" : "right",
                    }}
                  >
                    {colName}
                  </div>
                );
              })}
            </div>

            {/* Sequential Data Rows — Phase 2 & 3 */}
            {rows.map((rowCells, rIdx) => {
              const nominalRowStart = buildStart + rIdx * timePerRow;
              const rowDelay = safeSpringDelay(nominalRowStart, duration_frames, 0.68);

              const rowSpring = spring({
                frame: Math.max(0, frame - rowDelay),
                fps,
                config: { damping: 15, stiffness: 95 },
              });

              // Spotlight Focus State
              const isTargetRow = targetRowIdx !== undefined && targetRowIdx === rIdx;
              const hasTarget = targetRowIdx !== undefined;

              // Purely frame-driven opacity and scale (NO CSS transitions)
              const unselectedDim = hasTarget
                ? interpolate(spotlightSpring, [0, 1], [0.92, 0.40], {
                    extrapolateLeft: "clamp",
                    extrapolateRight: "clamp",
                  })
                : 0.95;

              const rowOpacity = (isTargetRow ? 1.0 : unselectedDim) * rowSpring;

              const rowScale =
                isTargetRow && hasTarget
                  ? interpolate(spotlightSpring, [0, 1], [1.0, 1.018], {
                      extrapolateLeft: "clamp",
                      extrapolateRight: "clamp",
                    })
                  : 1.0;

              const bgGradient =
                isTargetRow && hasTarget
                  ? `linear-gradient(135deg, rgba(245, 158, 11, ${0.04 + 0.14 * spotlightSpring}) 0%, rgba(30, 41, 59, ${0.5 + 0.35 * spotlightSpring}) 100%)`
                  : "transparent";

              const borderColor =
                isTargetRow && hasTarget
                  ? `rgba(245, 158, 11, ${0.15 + 0.35 * spotlightSpring})`
                  : "transparent";

              const shadow =
                isTargetRow && hasTarget
                  ? `0 10px 30px -5px rgba(245, 158, 11, ${0.25 * spotlightSpring})`
                  : "none";

              return (
                <div
                  key={rIdx}
                  style={{
                    display: "grid",
                    gridTemplateColumns: gridTemplate,
                    padding: cellPadding,
                    alignItems: "center",
                    borderBottom: "1px solid rgba(255, 255, 255, 0.08)",
                    borderRadius: "12px",
                    background: bgGradient,
                    border: `1px solid ${borderColor}`,
                    boxShadow: shadow,
                    opacity: rowOpacity,
                    transform: `translateY(${(1 - rowSpring) * 14}px) scale(${rowScale})`,
                    marginBottom: 4,
                  }}
                >
                  {rowCells.map((cellVal, cIdx) => {
                    const isHighlightCol = targetColIdx === cIdx;
                    const sem = getSemanticCellColor(cellVal, isTargetRow, isHighlightCol);

                    return (
                      <div
                        key={cIdx}
                        style={{
                          fontSize: cellFontSize,
                          fontWeight: isTargetRow || cIdx === 0 ? 900 : 700,
                          color: sem.text,
                          textAlign: cIdx === 0 ? "left" : "right",
                          fontVariantNumeric: sem.isNumeric ? "tabular-nums" : "normal",
                        }}
                      >
                        {String(cellVal)}
                      </div>
                    );
                  })}
                </div>
              );
            })}
          </div>
        </main>

        {/* Floating Story Callout Annotation — Phase 3 */}
        {annotation ? (
          <div
            style={{
              textAlign: "center",
              opacity: spotlightSpring,
              transform: `translateY(${(1 - spotlightSpring) * 14}px)`,
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
                border: "1px solid rgba(245, 158, 11, 0.6)",
                boxShadow: `0 0 ${20 * spotlightSpring}px rgba(245, 158, 11, 0.2)`,
                padding: "6px 20px",
                borderRadius: "20px",
                letterSpacing: 1,
              }}
            >
              ★ {annotation}
            </div>
          </div>
        ) : null}

        {/* Footer — Phase 3 */}
        {footerLabel ? (
          <footer
            style={{
              textAlign: "center",
              fontSize: 20,
              color: tokens.text.muted,
              fontWeight: 600,
              opacity: footerSpring,
              transform: `translateY(${(1 - footerSpring) * 10}px)`,
            }}
          >
            {footerLabel}
          </footer>
        ) : null}
      </div>
    </AbsoluteFill>
  );
}
