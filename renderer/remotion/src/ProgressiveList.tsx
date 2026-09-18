import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { type ProgressiveListItem, type ProgressiveListProps } from "./types";
import { tokens } from "./design-tokens";
import { safeSpringDelay } from "./animation-safety";

export function ProgressiveList(props: ProgressiveListProps | any) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Normalize boundary props wrapper
  const resolvedProps: ProgressiveListProps = props.props ? props.props : props;
  const duration_frames: number =
    (props as any).duration_frames ||
    (props as any).durationInFrames ||
    (props as any).renderSpec?.duration_frames ||
    180;

  const headerLabel = resolvedProps.headerLabel || "";
  const itemList: ProgressiveListItem[] = Array.isArray(resolvedProps.items)
    ? resolvedProps.items
    : [];
  const footerLabel = resolvedProps.footerLabel || "";

  const itemCount = Math.max(1, itemList.length);

  // Auto-detect variant if not explicitly passed
  const isDetailed =
    resolvedProps.variant === "detailed" ||
    (!resolvedProps.variant && itemList.some((it) => Boolean(it.subtitle)));

  // ─────────────────────────────────────────────────────────────────────────
  // PHASE 1 — HEADER & GUIDE ACCENT (0 → ~10% D)
  // ─────────────────────────────────────────────────────────────────────────
  const headerDelay = safeSpringDelay(0, duration_frames, 0.08);
  const headerSpring = spring({
    frame: Math.max(0, frame - headerDelay),
    fps,
    config: { damping: 16, stiffness: 110 },
  });

  // Vertical guide line draws down smoothly during Phase 1
  const guideProgress = interpolate(
    frame,
    [0, Math.max(2, Math.floor(duration_frames * 0.22))],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // ─────────────────────────────────────────────────────────────────────────
  // PHASE 2 — PROGRESSIVE ITEM REVEAL (10% D → 72% D)
  // Each item enters sequentially with safeSpringDelay.
  // In the build phase, the active item has reading spotlight; in Phase 3
  // (hold phase), all items settle into balanced, unified readability.
  // ─────────────────────────────────────────────────────────────────────────
  const buildStart = Math.floor(duration_frames * 0.08);
  const totalBuildDuration = Math.max(
    1,
    Math.floor(duration_frames * 0.72) - buildStart
  );
  const timePerItem = Math.max(1, Math.floor(totalBuildDuration / itemCount));

  const isHoldPhase = frame >= Math.floor(duration_frames * 0.72);
  const currentActiveIndex = isHoldPhase
    ? -1
    : Math.min(itemCount - 1, Math.max(0, Math.floor((frame - buildStart) / timePerItem)));

  // ─────────────────────────────────────────────────────────────────────────
  // PHASE 3 — FOOTER & CONSOLIDATION HOLD (72% D → 100% D)
  // ─────────────────────────────────────────────────────────────────────────
  const footerDelay = safeSpringDelay(
    Math.floor(duration_frames * 0.72),
    duration_frames,
    0.85
  );
  const footerSpring = spring({
    frame: Math.max(0, frame - footerDelay),
    fps,
    config: { damping: 16, stiffness: 90 },
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
        {/* Header Question / Eyebrow Context */}
        {headerLabel ? (
          <header
            style={{
              opacity: headerSpring,
              transform: `translateY(${(1 - headerSpring) * -12}px)`,
            }}
          >
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
          {/* Vertical Guide Accent Line (animated scaleY) */}
          <div
            style={{
              position: "absolute",
              left: "48px",
              top: "20px",
              bottom: "20px",
              width: "2px",
              background: "rgba(59, 130, 246, 0.25)",
              transformOrigin: "top",
              transform: `scaleY(${guideProgress})`,
              zIndex: 0,
            }}
          />

          {itemList.map((item, idx) => {
            const nominalItemStart = buildStart + idx * timePerItem;
            const itemDelay = safeSpringDelay(
              nominalItemStart,
              duration_frames,
              0.72
            );

            const itemSpring = spring({
              frame: Math.max(0, frame - itemDelay),
              fps,
              config: { damping: 15, stiffness: 100 },
            });

            // Entrance state: item has arrived once frame >= itemDelay
            const isRevealed = frame >= itemDelay;
            const isCurrentActive =
              (!isHoldPhase && idx === currentActiveIndex) || Boolean(item.highlight);

            const displayTitle = item.title || item.text || "Key Takeaway";
            const indexStr = String(idx + 1).padStart(2, "0");

            // Frame-interpolated active emphasis (NO CSS transition)
            const baseOpacity = isHoldPhase ? 1.0 : isCurrentActive ? 1.0 : 0.72;
            const currentOpacity = isRevealed ? baseOpacity * itemSpring : 0;
            const currentScale = isRevealed
              ? 0.96 + itemSpring * (isCurrentActive && !isHoldPhase ? 0.06 : 0.04)
              : 0.95;

            const numberBg = isCurrentActive && !isHoldPhase
              ? tokens.accent.blue
              : "rgba(30, 41, 59, 0.9)";
            const numberTextColor = isCurrentActive && !isHoldPhase
              ? "#ffffff"
              : tokens.accent.blue;

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
                  opacity: currentOpacity,
                  transform: `translateX(${(1 - itemSpring) * -24}px) scale(${currentScale})`,
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
                      isCurrentActive && !isHoldPhase
                        ? tokens.accent.blue
                        : "rgba(59, 130, 246, 0.3)"
                    }`,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontSize: 22,
                    fontWeight: 900,
                    color: numberTextColor,
                    boxShadow: isCurrentActive && !isHoldPhase
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
                    background: isCurrentActive && !isHoldPhase
                      ? "rgba(30, 41, 59, 0.6)"
                      : "transparent",
                    borderLeft: isCurrentActive && !isHoldPhase
                      ? `3px solid ${tokens.accent.blue}`
                      : "3px solid transparent",
                    padding: isCurrentActive && !isHoldPhase ? "10px 16px" : "4px 0",
                    borderRadius: "0 10px 10px 0",
                  }}
                >
                  {/* Headline Title */}
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: "10px",
                      fontSize: titleFontSize,
                      fontWeight: isCurrentActive || isHoldPhase ? 900 : 700,
                      color: isCurrentActive || isHoldPhase ? "#ffffff" : tokens.text.primary,
                      lineHeight: 1.25,
                    }}
                  >
                    {item.icon ? (
                      <span style={{ fontSize: titleFontSize - 2 }}>{item.icon}</span>
                    ) : null}
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
                        color: isCurrentActive || isHoldPhase
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
          <footer
            style={{
              textAlign: "center",
              fontSize: 20,
              color: tokens.text.muted,
              fontWeight: 600,
              opacity: footerSpring,
            }}
          >
            {footerLabel}
          </footer>
        ) : null}
      </div>
    </AbsoluteFill>
  );
}
