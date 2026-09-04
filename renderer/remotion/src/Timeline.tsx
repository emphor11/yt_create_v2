import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { type TimelineEvent, type TimelineProps } from "./types";
import { tokens } from "./design-tokens";

export function Timeline(props: TimelineProps | any) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Normalize boundary props wrapper
  const resolvedProps: TimelineProps = props.props ? props.props : props;
  const duration_frames = (props as any).duration_frames || 180;

  const headerLabel = resolvedProps.headerLabel || "";
  const footerLabel = resolvedProps.footerLabel || "";

  // Normalize Events List (support events array or legacy steps array)
  let eventList: TimelineEvent[] = [];
  if (Array.isArray(resolvedProps.events) && resolvedProps.events.length > 0) {
    eventList = resolvedProps.events;
  } else if (Array.isArray(resolvedProps.steps) && resolvedProps.steps.length > 0) {
    eventList = resolvedProps.steps.map((st, idx) => {
      const match = String(st).match(/\b(19\d\d|20\d\d)\b/);
      const yr = match ? match[1] : `Phase ${idx + 1}`;
      const cleanTitle = match ? String(st).replace(yr, "").replace(/^[\s\-:]+|[\s\-:]+$/g, "").trim() : String(st);
      return { date: yr, title: cleanTitle || String(st) };
    });
  } else {
    eventList = [
      { date: "2019", title: "IPO Launch", subtitle: "Public listing" },
      { date: "2021", title: "$1T Valuation", subtitle: "Mass market scale", value: "$1.0T", type: "major" },
      { date: "2024", title: "Profitability", subtitle: "Record cash flow", type: "positive" },
      { date: "2026", title: "Global Scale", subtitle: "Worldwide expansion" },
    ];
  }

  const eventCount = eventList.length;

  // Staggered Chronological Line Extension Timeline (75% build, 25% hold)
  const totalBuildDuration = Math.round(duration_frames * 0.75);
  const timePerEvent = Math.round(totalBuildDuration / Math.max(1, eventCount));

  // Animated Track Line Progress (0% to 100% across the timeline track)
  const trackLineProgress = interpolate(
    frame,
    [0, totalBuildDuration],
    [0, 100],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // Active Event Index for story focus
  const currentActiveIndex = Math.min(
    eventCount - 1,
    Math.floor(frame / timePerEvent)
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
        {/* Header Eyebrow */}
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

        {/* Main Horizontal Chronological Timeline Track */}
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
          {/* Horizontal Axis Container */}
          <div
            style={{
              position: "relative",
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              width: "100%",
              padding: "0 40px",
            }}
          >
            {/* Background Axis Line (Inactive Track) */}
            <div
              style={{
                position: "absolute",
                left: "60px",
                right: "60px",
                top: "50%",
                height: "4px",
                background: "rgba(255, 255, 255, 0.1)",
                borderRadius: "2px",
                transform: "translateY(-50%)",
                zIndex: 0,
              }}
            />

            {/* Active Extension Line (Forward Chronological Fill) */}
            <div
              style={{
                position: "absolute",
                left: "60px",
                top: "50%",
                height: "4px",
                width: `calc(${trackLineProgress}% * 0.88)`,
                background: "linear-gradient(90deg, #3b82f6 0%, #60a5fa 100%)",
                borderRadius: "2px",
                transform: "translateY(-50%)",
                boxShadow: "0 0 12px rgba(59, 130, 246, 0.6)",
                zIndex: 1,
              }}
            />

            {/* Timeline Event Nodes */}
            {eventList.map((ev, idx) => {
              const eventFrameStart = idx * timePerEvent;
              const isRevealed = frame >= eventFrameStart;

              const nodeSpring = spring({
                frame: Math.max(0, frame - eventFrameStart),
                fps,
                config: { damping: 14, stiffness: 95 },
              });

              // Active Reading Focus Logic
              const isCurrentActive = idx === currentActiveIndex && frame < totalBuildDuration;

              // Node Colors by Event Type
              const evType = ev.type || "normal";
              const nodeColor =
                evType === "major"
                  ? "#f59e0b"
                  : evType === "positive"
                  ? "#10b981"
                  : evType === "warning"
                  ? "#ef4444"
                  : tokens.accent.blue;

              return (
                <div
                  key={idx}
                  style={{
                    position: "relative",
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    zIndex: 2,
                    opacity: isRevealed ? (isCurrentActive ? 1 : 0.78) : 0,
                    transform: `scale(${isRevealed ? (isCurrentActive ? 1.08 : 1) : 0.85})`,
                    transition: "opacity 0.2s, transform 0.2s",
                  }}
                >
                  {/* Date / Year Badge (Positioned Above Timeline Node) */}
                  <div
                    style={{
                      fontSize: isCurrentActive ? 22 : 18,
                      fontWeight: 900,
                      color: isCurrentActive ? "#ffffff" : nodeColor,
                      background: isCurrentActive ? nodeColor : "rgba(30, 41, 59, 0.9)",
                      border: `2px solid ${nodeColor}`,
                      padding: "4px 14px",
                      borderRadius: "14px",
                      marginBottom: 12,
                      boxShadow: isCurrentActive ? `0 4px 15px ${nodeColor}66` : "none",
                      letterSpacing: 1,
                    }}
                  >
                    {ev.date}
                  </div>

                  {/* Timeline Point Node Circle / Diamond */}
                  <div
                    style={{
                      width: isCurrentActive ? "24px" : "18px",
                      height: isCurrentActive ? "24px" : "18px",
                      borderRadius: evType === "major" ? "4px" : "50%",
                      transform: evType === "major" ? "rotate(45deg)" : "none",
                      background: nodeColor,
                      border: "3px solid #0f172a",
                      boxShadow: isCurrentActive ? `0 0 16px ${nodeColor}` : "none",
                      marginBottom: 14,
                    }}
                  />

                  {/* Title & Subtitle & Metric Callout (Positioned Below Timeline Node) */}
                  <div
                    style={{
                      textAlign: "center",
                      maxWidth: "220px",
                      background: isCurrentActive ? "rgba(30, 41, 59, 0.6)" : "transparent",
                      border: isCurrentActive ? `1px solid ${nodeColor}44` : "1px solid transparent",
                      borderRadius: "12px",
                      padding: isCurrentActive ? "10px 12px" : "4px 0",
                    }}
                  >
                    {/* Event Title */}
                    <div
                      style={{
                        fontSize: eventCount >= 5 ? 18 : 20,
                        fontWeight: isCurrentActive ? 900 : 700,
                        color: isCurrentActive ? "#ffffff" : tokens.text.primary,
                        lineHeight: 1.2,
                      }}
                    >
                      {ev.title}
                    </div>

                    {/* Metric Value Callout if present */}
                    {ev.value ? (
                      <div
                        style={{
                          fontSize: 16,
                          fontWeight: 900,
                          color: nodeColor,
                          marginTop: 4,
                        }}
                      >
                        {ev.value}
                      </div>
                    ) : null}

                    {/* Subtitle */}
                    {ev.subtitle ? (
                      <div
                        style={{
                          fontSize: 14,
                          color: isCurrentActive ? tokens.text.secondary : tokens.text.muted,
                          fontWeight: 500,
                          marginTop: 4,
                        }}
                      >
                        {ev.subtitle}
                      </div>
                    ) : null}

                    {/* Current Focus Indicator */}
                    {isCurrentActive ? (
                      <div
                        style={{
                          marginTop: 8,
                          fontSize: 11,
                          fontWeight: 900,
                          color: nodeColor,
                          letterSpacing: 1.5,
                          textTransform: "uppercase",
                        }}
                      >
                        ▲ CURRENT FOCUS
                      </div>
                    ) : null}
                  </div>
                </div>
              );
            })}
          </div>
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
