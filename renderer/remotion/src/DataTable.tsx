import {
  AbsoluteFill,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { type DataTableProps } from "./types";
import { tokens } from "./design-tokens";

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
  const resolvedProps: DataTableProps = props.props ? props.props : props;
  const duration_frames = (props as any).duration_frames || 180;

  const headerLabel = resolvedProps.headerLabel || "";
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

  // Staggered Sequential Row Reveal Timeline (75% for rows, 25% for hold)
  const totalBuildDuration = Math.round(duration_frames * 0.75);
  const timePerRow = Math.round(totalBuildDuration / Math.max(1, rowCount));

  // Spotlight animation lands after row 2 or frame duration*0.5
  const spotlightFrameStart = Math.round(duration_frames * 0.45);
  const spotlightSpring = spring({
    frame: Math.max(0, frame - spotlightFrameStart),
    fps,
    config: { damping: 14, stiffness: 100 },
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
          {/* Table Container (Flat Editorial Rows, no heavy widget card) */}
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              width: "100%",
            }}
          >
            {/* Table Column Headers (Quiet Uppercase Header) */}
            <div
              style={{
                display: "grid",
                gridTemplateColumns: gridTemplate,
                padding: "10px 16px",
                borderBottom: "2px solid rgba(255, 255, 255, 0.15)",
                marginBottom: 8,
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

            {/* Sequential Data Rows */}
            {rows.map((rowCells, rIdx) => {
              const rowFrameStart = rIdx * timePerRow;
              const isRevealed = frame >= rowFrameStart;

              const rowSpring = spring({
                frame: Math.max(0, frame - rowFrameStart),
                fps,
                config: { damping: 15, stiffness: 95 },
              });

              // Spotlight Focus State
              const isTargetRow = targetRowIdx !== undefined && targetRowIdx === rIdx;
              const hasActiveSpotlight = targetRowIdx !== undefined && frame >= spotlightFrameStart;

              const rowOpacity = isRevealed
                ? hasActiveSpotlight
                  ? isTargetRow
                    ? 1
                    : 0.35
                  : 0.9
                : 0;

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
                    background: isTargetRow
                      ? "linear-gradient(135deg, rgba(245, 158, 11, 0.15) 0%, rgba(30, 41, 59, 0.8) 100%)"
                      : "transparent",
                    border: isTargetRow
                      ? "1px solid rgba(245, 158, 11, 0.4)"
                      : "1px solid transparent",
                    opacity: rowOpacity,
                    transform: `translateY(${(1 - rowSpring) * 15}px) scale(${
                      isTargetRow && hasActiveSpotlight ? 1.02 : 1
                    })`,
                    transition: "opacity 0.25s, transform 0.25s, background 0.25s",
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

        {/* Floating Story Callout Annotation */}
        {annotation ? (
          <div
            style={{
              textAlign: "center",
              opacity: spotlightSpring,
              transform: `translateY(${(1 - spotlightSpring) * 15}px)`,
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
              ★ {annotation}
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
