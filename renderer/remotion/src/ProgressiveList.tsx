import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { type ProgressiveListItem, type ProgressiveListProps } from "./types";
import { tokens } from "./design-tokens";

export function ProgressiveList(props: ProgressiveListProps | any) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Normalize boundary props wrapper
  const resolvedProps: ProgressiveListProps = props.props ? props.props : props;
  const duration_frames = (props as any).duration_frames || 180;

  const headerLabel = resolvedProps.headerLabel || "";
  const itemList: ProgressiveListItem[] = Array.isArray(resolvedProps.items)
    ? resolvedProps.items
    : [];
  const footerLabel = resolvedProps.footerLabel || "";

  const itemCount = itemList.length;

  // Auto-detect variant if not explicitly passed
  const isDetailed =
    resolvedProps.variant === "detailed" ||
    (!resolvedProps.variant && itemList.some((it) => Boolean(it.subtitle)));

  // Pacing Construction Timeline (Allocate 75% for list reveal, hold 25%)
  const totalBuildDuration = Math.round(duration_frames * 0.75);
  const timePerItem = Math.round(totalBuildDuration / Math.max(1, itemCount));

  // Determine current active item index for reading focus
  const currentActiveIndex = Math.min(
    itemCount - 1,
    Math.floor(frame / timePerItem)
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
        {/* Header Question / Eyebrow Context */}
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

        {/* Main Progressive Editorial List */}
        <main
          style={{
            position: "relative",
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
            gap: isDetailed ? "20px" : "14px",
            flex: 1,
            margin: "20px 0",
            paddingLeft: "20px",
          }}
        >
          {/* Vertical Guide Accent Line */}
          <div
            style={{
              position: "absolute",
              left: "48px",
              top: "20px",
              bottom: "20px",
              width: "2px",
              background: "rgba(59, 130, 246, 0.2)",
              zIndex: 0,
            }}
          />

          {itemList.map((item, idx) => {
            const itemFrameStart = idx * timePerItem;
            const isRevealed = frame >= itemFrameStart;

            const itemSpring = spring({
              frame: Math.max(0, frame - itemFrameStart),
              fps,
              config: { damping: 14, stiffness: 95 },
            });

            // Active Reading Focus Logic (Story Pacing)
            const isCurrentActive =
              (idx === currentActiveIndex && frame < totalBuildDuration) ||
              Boolean(item.highlight);

            const displayTitle = item.title || item.text || "Key Takeaway";
            const indexStr = String(idx + 1).padStart(2, "0");

            const numberBg = isCurrentActive
              ? tokens.accent.blue
              : "rgba(30, 41, 59, 0.9)";
            const numberTextColor = isCurrentActive ? "#ffffff" : tokens.accent.blue;

            const titleFontSize = isDetailed
              ? itemCount >= 5 ? 24 : 28
              : itemCount >= 5 ? 26 : 30;

            return (
              <div
                key={idx}
                style={{
                  position: "relative",
                  display: "flex",
                  alignItems: isDetailed ? "flex-start" : "center",
                  gap: "24px",
                  zIndex: 1,
                  opacity: isRevealed ? (isCurrentActive ? 1 : 0.72) : 0,
                  transform: `translateX(${(1 - itemSpring) * -30}px) scale(${
                    isRevealed ? (isCurrentActive ? 1.02 : 1) : 0.95
                  })`,
                  transition: "opacity 0.2s, transform 0.2s",
                }}
              >
                {/* Visual Anchor: Index Number Badge 01, 02, 03 */}
                <div
                  style={{
                    width: "56px",
                    height: "56px",
                    borderRadius: "14px",
                    background: numberBg,
                    border: `2px solid ${
                      isCurrentActive ? tokens.accent.blue : "rgba(59, 130, 246, 0.3)"
                    }`,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontSize: 22,
                    fontWeight: 900,
                    color: numberTextColor,
                    boxShadow: isCurrentActive
                      ? "0 6px 20px rgba(59, 130, 246, 0.4)"
                      : "0 4px 12px rgba(0,0,0,0.2)",
                    flexShrink: 0,
                  }}
                >
                  {indexStr}
                </div>

                {/* Content Text Block */}
                <div
                  style={{
                    flex: 1,
                    background: isCurrentActive
                      ? "rgba(30, 41, 59, 0.6)"
                      : "transparent",
                    borderLeft: isCurrentActive
                      ? `3px solid ${tokens.accent.blue}`
                      : "3px solid transparent",
                    padding: isCurrentActive ? "10px 16px" : "4px 0",
                    borderRadius: "0 10px 10px 0",
                    transition: "background 0.2s, border 0.2s",
                  }}
                >
                  {/* Headline Title */}
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: "10px",
                      fontSize: titleFontSize,
                      fontWeight: isCurrentActive ? 900 : 700,
                      color: isCurrentActive ? "#ffffff" : tokens.text.primary,
                      lineHeight: 1.25,
                    }}
                  >
                    {item.icon ? <span style={{ fontSize: titleFontSize - 2 }}>{item.icon}</span> : null}
                    <span>{displayTitle}</span>
                    {item.value ? (
                      <span
                        style={{
                          fontSize: titleFontSize - 4,
                          fontWeight: 900,
                          color: tokens.accent.blue,
                          marginLeft: "auto",
                        }}
                      >
                        {item.value}
                      </span>
                    ) : null}
                  </div>

                  {/* Optional Subtitle (Detailed Mode) */}
                  {isDetailed && item.subtitle ? (
                    <div
                      style={{
                        fontSize: itemCount >= 5 ? 16 : 18,
                        color: isCurrentActive
                          ? tokens.text.secondary
                          : tokens.text.muted,
                        fontWeight: 500,
                        marginTop: 4,
                      }}
                    >
                      {item.subtitle}
                    </div>
                  ) : null}
                </div>
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
