import React from "react";
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { type RankedListItem, type RankedListProps } from "./types";
import { tokens } from "./design-tokens";
import { safeAnimationWindow, safeSpringDelay } from "./animation-safety";

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
  const duration_frames = (props as any).duration_frames || (props as any).durationInFrames || 180;

  const headerLabel = resolvedProps.headerLabel || "";
  const itemList: RankedListItem[] = Array.isArray(resolvedProps.items)
    ? resolvedProps.items
    : [];
  const showBars = resolvedProps.showBars !== false;
  const footerLabel = resolvedProps.footerLabel || "";

  const itemCount = itemList.length;

  // Calculate Max Numeric Value for Relative Proportional Bar Widths
  const numericValues = itemList.map(parseNumericValue);
  const maxNumericValue = Math.max(...numericValues, 0);

  // Cascade Animation Timing: Brisk cascade so all items arrive early and remain held for full comprehension
  const totalBuildDuration = Math.min(36, Math.max(1, Math.floor(duration_frames * 0.40)));
  const timePerItem = Math.max(2, Math.floor(totalBuildDuration / Math.max(1, itemCount)));

  const headerDelay = safeSpringDelay(0, duration_frames, 0.15);
  const headerSpring = spring({
    frame: Math.max(0, frame - headerDelay),
    fps,
    config: tokens.motion.reveal,
  });

  return (
    <AbsoluteFill
      style={{
        background: "radial-gradient(ellipse 90% 70% at 50% 40%, rgba(15, 23, 42, 0.96) 0%, rgba(5, 7, 10, 0.99) 100%)",
        color: tokens.text.primary,
        fontFamily: tokens.font.family,
        overflow: "hidden",
        padding: "50px 80px",
      }}
    >
      {/* Cinematic Top and Bottom Subtle Letterbox Hairlines */}
      <div
        style={{
          position: "absolute",
          top: 24,
          left: 80,
          right: 80,
          height: "1px",
          background: "linear-gradient(90deg, transparent 0%, rgba(255, 255, 255, 0.12) 30%, rgba(255, 255, 255, 0.12) 70%, transparent 100%)",
        }}
      />
      <div
        style={{
          position: "absolute",
          bottom: 24,
          left: 80,
          right: 80,
          height: "1px",
          background: "linear-gradient(90deg, transparent 0%, rgba(255, 255, 255, 0.12) 30%, rgba(255, 255, 255, 0.12) 70%, transparent 100%)",
        }}
      />

      {/* Ambient Halo behind Rank 1 */}
      <div
        style={{
          position: "absolute",
          top: "22%",
          left: "50%",
          transform: "translate(-50%, -50%)",
          width: "700px",
          height: "300px",
          borderRadius: "50%",
          background: "radial-gradient(circle, rgba(245, 158, 11, 0.14) 0%, transparent 70%)",
          filter: "blur(50px)",
          pointerEvents: "none",
          zIndex: 0,
        }}
      />

      <div
        style={{
          position: "relative",
          display: "flex",
          flexDirection: "column",
          height: "100%",
          justifyContent: "space-between",
          zIndex: 1,
        }}
      >
        {/* Editorial Leaderboard Header */}
        <header
          style={{
            textAlign: "center",
            opacity: headerSpring,
            transform: `translateY(${(1 - headerSpring) * -14}px)`,
          }}
        >
          {headerLabel ? (
            <div
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: 8,
                padding: "6px 18px",
                borderRadius: tokens.radius.pill,
                background: "rgba(255, 255, 255, 0.05)",
                border: "1px solid rgba(255, 255, 255, 0.12)",
                color: tokens.accent.cyan,
                fontSize: 13,
                fontWeight: 800,
                textTransform: "uppercase",
                letterSpacing: 2,
                boxShadow: "0 2px 10px rgba(0, 0, 0, 0.2)",
              }}
            >
              <span
                style={{
                  width: 6,
                  height: 6,
                  borderRadius: "50%",
                  backgroundColor: tokens.accent.cyan,
                  boxShadow: `0 0 8px ${tokens.accent.cyan}`,
                }}
              />
              {headerLabel}
            </div>
          ) : null}
        </header>

        {/* Main Editorial Leaderboard List */}
        <main
          style={{
            position: "relative",
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
            gap: itemCount >= 5 ? "12px" : itemCount === 4 ? "14px" : "18px",
            flex: 1,
            margin: "20px 0",
            maxWidth: "1100px",
            width: "100%",
            alignSelf: "center",
          }}
        >
          {itemList.map((item, idx) => {
            const nominalDelay = idx * timePerItem;
            const itemDelay = safeSpringDelay(nominalDelay, duration_frames, 0.65);

            // Row Entrance Spring
            const rowSpring = spring({
              frame: Math.max(0, frame - itemDelay),
              fps,
              config: tokens.motion.reveal,
            });

            // Proportional Bar Expansion Window (guaranteed monotonic increasing)
            const [barStart, barEnd] = safeAnimationWindow(
              itemDelay + 2,
              itemDelay + Math.max(4, timePerItem),
              duration_frames,
              2
            );
            const barProgress = interpolate(
              frame,
              [barStart, barEnd],
              [0, 1],
              { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
            );

            const rankNum = item.rank !== undefined ? item.rank : idx + 1;
            const isTopRank = String(rankNum) === "1" || String(rankNum) === "#1" || idx === 0;

            const numVal = numericValues[idx];
            // Proportional calculation: if numeric values exist, use them; otherwise descending default
            let targetBarPercent: number;
            if (maxNumericValue > 0 && numVal > 0) {
              targetBarPercent = Math.max(6, Math.min(100, (numVal / maxNumericValue) * 100));
            } else {
              const fallbackRatios = [100, 72, 54, 38, 26];
              targetBarPercent = fallbackRatios[Math.min(idx, fallbackRatios.length - 1)];
            }
            const currentBarWidth = barProgress * targetBarPercent;

            // Rank Shift Badge (+2, -1, NEW)
            const changeStr = item.change ? String(item.change).trim() : "";
            const isPosChange = changeStr.startsWith("+") || changeStr.startsWith("↑");
            const isNegChange = changeStr.startsWith("-") || changeStr.startsWith("↓");
            const isNew = changeStr.toUpperCase() === "NEW";

            const changeColor = isPosChange ? tokens.accent.emerald : isNegChange ? tokens.accent.rose : tokens.accent.cyan;
            const changeIcon = isPosChange ? "↑ " : isNegChange ? "↓ " : "";

            const rankBadgeColor = isTopRank
              ? tokens.accent.amber
              : idx === 1
              ? "#cbd5e1"
              : idx === 2
              ? "#d97706"
              : tokens.text.secondary;

            const formattedRank = typeof rankNum === "number" ? String(rankNum).padStart(2, "0") : String(rankNum).replace("#", "").padStart(2, "0");

            return (
              <div
                key={idx}
                style={{
                  position: "relative",
                  display: "flex",
                  flexDirection: "column",
                  padding: isTopRank
                    ? itemCount >= 5 ? "16px 22px" : "20px 26px"
                    : itemCount >= 5 ? "12px 18px" : "14px 22px",
                  background: isTopRank
                    ? "linear-gradient(135deg, rgba(30, 41, 59, 0.90) 0%, rgba(15, 23, 42, 0.95) 100%)"
                    : "rgba(15, 23, 42, 0.65)",
                  border: isTopRank
                    ? `2px solid ${tokens.accent.amber}`
                    : "1px solid rgba(255, 255, 255, 0.08)",
                  borderRadius: isTopRank ? "18px" : "14px",
                  boxShadow: isTopRank
                    ? "0 10px 30px rgba(245, 158, 11, 0.22), inset 0 1px 0 rgba(255, 255, 255, 0.1)"
                    : "0 4px 16px rgba(0, 0, 0, 0.25)",
                  backdropFilter: "blur(12px)",
                  opacity: rowSpring,
                  transform: `translateX(${(1 - rowSpring) * -30}px) scale(${isTopRank ? 1.015 : 1})`,
                  zIndex: isTopRank ? 2 : 1,
                  transition: "transform 0.25s ease",
                }}
              >
                {/* Top Row: Rank Number + Details + Value */}
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    marginBottom: showBars ? 8 : 0,
                  }}
                >
                  {/* Left Group: #Rank + Logo + Title + Badges */}
                  <div style={{ display: "flex", alignItems: "center", gap: "14px", flex: 1, minWidth: 0 }}>
                    {/* Rank Badge Number */}
                    <div
                      style={{
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        fontSize: isTopRank ? 18 : 15,
                        fontWeight: 900,
                        color: isTopRank ? "#05070a" : rankBadgeColor,
                        background: isTopRank ? tokens.accent.amber : "rgba(255, 255, 255, 0.06)",
                        border: isTopRank ? "none" : "1px solid rgba(255, 255, 255, 0.12)",
                        minWidth: isTopRank ? "40px" : "34px",
                        height: isTopRank ? "28px" : "24px",
                        borderRadius: "8px",
                        fontVariantNumeric: "tabular-nums",
                        letterSpacing: 0.5,
                        boxShadow: isTopRank ? `0 2px 8px ${tokens.accent.amber}66` : "none",
                      }}
                    >
                      #{formattedRank}
                    </div>

                    {/* Optional Logo / Icon */}
                    {item.logo || item.icon ? (
                      <span style={{ fontSize: isTopRank ? 24 : 20, marginRight: 2 }}>
                        {item.logo || item.icon}
                      </span>
                    ) : null}

                    {/* Title and Subtitle */}
                    <div style={{ display: "flex", alignItems: "baseline", gap: 10, minWidth: 0, overflow: "hidden" }}>
                      <span
                        style={{
                          fontSize: isTopRank ? (itemCount >= 5 ? 24 : 26) : itemCount >= 5 ? 20 : 22,
                          fontWeight: isTopRank ? 900 : 700,
                          color: isTopRank ? "#ffffff" : tokens.text.primary,
                          whiteSpace: "nowrap",
                          overflow: "hidden",
                          textOverflow: "ellipsis",
                        }}
                      >
                        {item.title}
                      </span>

                      {/* Subtitle if available */}
                      {item.subtitle ? (
                        <span
                          style={{
                            fontSize: 14,
                            color: tokens.text.secondary,
                            fontWeight: 500,
                            whiteSpace: "nowrap",
                            overflow: "hidden",
                            textOverflow: "ellipsis",
                          }}
                        >
                          {item.subtitle}
                        </span>
                      ) : null}
                    </div>

                    {/* Leader Chip on Rank 1 */}
                    {isTopRank ? (
                      <span
                        style={{
                          fontSize: 10,
                          fontWeight: 900,
                          color: tokens.accent.amber,
                          background: "rgba(245, 158, 11, 0.18)",
                          border: "1px solid rgba(245, 158, 11, 0.4)",
                          padding: "2px 8px",
                          borderRadius: tokens.radius.pill,
                          letterSpacing: 1.2,
                          textTransform: "uppercase",
                          whiteSpace: "nowrap",
                        }}
                      >
                        {item.badge || "TOP LEADER"}
                      </span>
                    ) : item.badge ? (
                      <span
                        style={{
                          fontSize: 10,
                          fontWeight: 800,
                          color: tokens.text.secondary,
                          background: "rgba(255, 255, 255, 0.08)",
                          padding: "2px 8px",
                          borderRadius: tokens.radius.pill,
                          letterSpacing: 1,
                        }}
                      >
                        {item.badge}
                      </span>
                    ) : null}

                    {/* Rank Shift Callout (+2, -1, NEW) */}
                    {changeStr ? (
                      <span
                        style={{
                          fontSize: 11,
                          fontWeight: 900,
                          color: changeColor,
                          background: `${changeColor}20`,
                          border: `1px solid ${changeColor}66`,
                          padding: "2px 8px",
                          borderRadius: "10px",
                          whiteSpace: "nowrap",
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
                        fontSize: isTopRank ? (itemCount >= 5 ? 30 : 34) : itemCount >= 5 ? 22 : 25,
                        fontWeight: 900,
                        color: isTopRank ? tokens.accent.amber : "#ffffff",
                        fontVariantNumeric: "tabular-nums",
                        letterSpacing: -0.5,
                        marginLeft: 16,
                        flexShrink: 0,
                        textShadow: isTopRank ? "0 0 20px rgba(245, 158, 11, 0.4)" : "none",
                      }}
                    >
                      {item.value}
                    </div>
                  ) : null}
                </div>

                {/* Bottom Row: Proportional Magnitude Progress Bar */}
                {showBars ? (
                  <div
                    style={{
                      position: "relative",
                      width: "100%",
                      height: isTopRank ? "10px" : "7px",
                      background: "rgba(255, 255, 255, 0.07)",
                      borderRadius: "5px",
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
                          : "linear-gradient(90deg, #06b6d4 0%, #3b82f6 100%)",
                        borderRadius: "5px",
                        boxShadow: isTopRank ? "0 0 12px rgba(245, 158, 11, 0.5)" : "none",
                        transition: "width 0.1s linear",
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
          <footer
            style={{
              textAlign: "center",
              fontSize: 16,
              color: tokens.text.muted,
              fontWeight: 600,
              letterSpacing: 0.5,
            }}
          >
            {footerLabel}
          </footer>
        ) : null}
      </div>
    </AbsoluteFill>
  );
}

