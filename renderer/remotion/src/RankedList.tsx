import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { type RankedListItem, type RankedListProps } from "./types";
import { tokens } from "./design-tokens";

/**
 * Helper to extract numeric value for bar scaling calculation
 */
function parseNumericValue(item: RankedListItem): number {
  if (item.numericValue !== undefined && item.numericValue !== null) {
    return item.numericValue;
  }
  if (typeof item.value === "number") {
    return item.value;
  }
  if (typeof item.value === "string") {
    const match = item.value.match(/[\d,]+(?:\.\d+)?/);
    if (match) {
      const num = parseFloat(match[0].replace(/,/g, ""));
      return isNaN(num) ? 0 : num;
    }
  }
  return 0;
}

export function RankedList(props: RankedListProps | any) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Normalize boundary props wrapper
  const resolvedProps: RankedListProps = props.props ? props.props : props;
  const duration_frames = (props as any).duration_frames || 180;

  const headerLabel = resolvedProps.headerLabel || "";
  const itemList: RankedListItem[] = Array.isArray(resolvedProps.items)
    ? resolvedProps.items
    : [];
  const showBars = resolvedProps.showBars !== false;
  const footerLabel = resolvedProps.footerLabel || "";

  const itemCount = itemList.length;

  // Calculate Max Numeric Value for Relative Proportional Bar Widths
  const numericValues = itemList.map(parseNumericValue);
  const maxNumericValue = Math.max(...numericValues, 0.001);

  // Staggered Timeline Construction (75% duration for build, 25% hold)
  const totalBuildDuration = Math.round(duration_frames * 0.75);
  const timePerItem = Math.round(totalBuildDuration / Math.max(1, itemCount));

  const headerSpring = spring({
    frame,
    fps,
    config: { damping: 15, stiffness: 100 },
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
        {/* Editorial Leaderboard Header */}
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

        {/* Main Editorial Leaderboard List */}
        <main
          style={{
            position: "relative",
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
            gap: itemCount >= 5 ? "12px" : "18px",
            flex: 1,
            margin: "16px 0",
          }}
        >
          {itemList.map((item, idx) => {
            const itemFrameStart = idx * timePerItem;
            const isRevealed = frame >= itemFrameStart;

            // Row Entrance Spring
            const rowSpring = spring({
              frame: Math.max(0, frame - itemFrameStart),
              fps,
              config: { damping: 14, stiffness: 95 },
            });

            // Proportional Bar Expansion Progress (starts 6 frames after row lands)
            const barFrameStart = itemFrameStart + 6;
            const barProgress = interpolate(
              frame,
              [barFrameStart, barFrameStart + Math.round(timePerItem * 0.65)],
              [0, 1],
              { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
            );

            const rankNum = item.rank !== undefined ? item.rank : idx + 1;
            const isTopRank = String(rankNum) === "1" || String(rankNum) === "#1";

            const numVal = numericValues[idx];
            const targetBarPercent = Math.max(8, (numVal / maxNumericValue) * 100);
            const currentBarWidth = barProgress * targetBarPercent;

            // Rank Shift Badge (+2, -1, NEW)
            const changeStr = item.change ? String(item.change).trim() : "";
            const isPosChange = changeStr.startsWith("+") || changeStr.startsWith("↑");
            const isNegChange = changeStr.startsWith("-") || changeStr.startsWith("↓");
            const isNew = changeStr.toUpperCase() === "NEW";

            const changeColor = isPosChange ? "#10b981" : isNegChange ? "#ef4444" : "#06b6d4";
            const changeIcon = isPosChange ? "↑ " : isNegChange ? "↓ " : "";

            const rankBadgeColor = isTopRank ? "#f59e0b" : idx === 1 ? "#94a3b8" : tokens.text.secondary;

            const rowFontSize = itemCount >= 5 ? 22 : 26;
            const valueFontSize = itemCount >= 5 ? 22 : 26;

            return (
              <div
                key={idx}
                style={{
                  position: "relative",
                  display: "flex",
                  flexDirection: "column",
                  padding: itemCount >= 5 ? "8px 0" : "12px 0",
                  borderBottom: "1px solid rgba(255, 255, 255, 0.07)",
                  opacity: isRevealed ? (isTopRank ? 1 : 0.88) : 0,
                  transform: `translateX(${(1 - rowSpring) * -25}px)`,
                }}
              >
                {/* Top Line: Rank Number + Logo/Icon + Title + Change Pill + Value */}
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 6 }}>
                  {/* Left Group: #Rank + Title */}
                  <div style={{ display: "flex", alignItems: "center", gap: "14px" }}>
                    {/* Rank Badge Number */}
                    <span
                      style={{
                        fontSize: isTopRank ? 24 : 20,
                        fontWeight: 900,
                        color: rankBadgeColor,
                        minWidth: "36px",
                      }}
                    >
                      #{rankNum}
                    </span>

                    {/* Optional Logo / Icon */}
                    {item.logo || item.icon ? (
                      <span style={{ fontSize: 22, marginRight: 2 }}>{item.logo || item.icon}</span>
                    ) : null}

                    {/* Title */}
                    <span
                      style={{
                        fontSize: rowFontSize,
                        fontWeight: isTopRank ? 900 : 700,
                        color: isTopRank ? "#ffffff" : tokens.text.primary,
                      }}
                    >
                      {item.title}
                    </span>

                    {/* Subtitle if available */}
                    {item.subtitle ? (
                      <span style={{ fontSize: 15, color: tokens.text.muted, fontWeight: 500, marginLeft: 8 }}>
                        {item.subtitle}
                      </span>
                    ) : null}

                    {/* Rank Shift Callout (+2, -1, NEW) */}
                    {changeStr ? (
                      <span
                        style={{
                          fontSize: 13,
                          fontWeight: 900,
                          color: changeColor,
                          background: `${changeColor}20`,
                          border: `1px solid ${changeColor}66`,
                          padding: "2px 8px",
                          borderRadius: "10px",
                          marginLeft: 6,
                        }}
                      >
                        {isNew ? "NEW" : `${changeIcon}${changeStr.replace(/^[+-]/, "")}`}
                      </span>
                    ) : null}
                  </div>

                  {/* Right Group: Display Value */}
                  {item.value !== undefined && item.value !== null ? (
                    <div
                      style={{
                        fontSize: valueFontSize,
                        fontWeight: 900,
                        color: isTopRank ? "#f59e0b" : tokens.text.primary,
                        fontVariantNumeric: "tabular-nums",
                      }}
                    >
                      {item.value}
                    </div>
                  ) : null}
                </div>

                {/* Bottom Line: Proportional Magnitude Progress Bar */}
                {showBars ? (
                  <div
                    style={{
                      position: "relative",
                      width: "100%",
                      height: isTopRank ? "8px" : "6px",
                      background: "rgba(255, 255, 255, 0.08)",
                      borderRadius: "4px",
                      overflow: "hidden",
                      marginTop: 4,
                    }}
                  >
                    <div
                      style={{
                        width: `${currentBarWidth}%`,
                        height: "100%",
                        background: isTopRank
                          ? "linear-gradient(90deg, #f59e0b 0%, #fbbf24 100%)"
                          : "linear-gradient(90deg, #3b82f6 0%, #60a5fa 100%)",
                        borderRadius: "4px",
                        boxShadow: isTopRank ? "0 0 10px rgba(245, 158, 11, 0.4)" : "none",
                      }}
                    />
                  </div>
                ) : null}
              </div>
            );
          })}
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
