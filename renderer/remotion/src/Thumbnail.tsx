import React from "react";

export type ThumbnailProps = {
  title: string;
  hook_line?: string;
  thumbnail_concept?: string;
  topic?: string;
};

export const defaultThumbnailProps: ThumbnailProps = {
  title: "Mastering YouTube Automation with AI",
  hook_line: "Stop spending 10 hours editing — automate the entire workflow",
  thumbnail_concept: "THE $100T REVOLUTION",
  topic: "Artificial Intelligence",
};

export const Thumbnail: React.FC<ThumbnailProps> = ({
  title,
  hook_line,
  thumbnail_concept,
  topic,
}) => {
  const displayConcept = (thumbnail_concept || title || "").toUpperCase();
  const displaySubtitle = hook_line || title || "";

  return (
    <div
      style={{
        width: 1280,
        height: 720,
        backgroundColor: "#0B0F19",
        backgroundImage: `
          radial-gradient(circle at 15% 20%, rgba(99, 102, 241, 0.25) 0%, transparent 50%),
          radial-gradient(circle at 85% 80%, rgba(244, 63, 94, 0.2) 0%, transparent 50%),
          linear-gradient(135deg, #090D16 0%, #111827 50%, #0F172A 100%)
        `,
        display: "flex",
        flexDirection: "column",
        justifyContent: "space-between",
        padding: "60px 80px",
        boxSizing: "border-box",
        fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
        position: "relative",
        overflow: "hidden",
      }}
    >
      {/* Subtle border glow */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          border: "2px solid rgba(255, 255, 255, 0.08)",
          pointerEvents: "none",
        }}
      />

      {/* Top row: Badge and Branding */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        {topic ? (
          <div
            style={{
              backgroundColor: "rgba(99, 102, 241, 0.2)",
              border: "1px solid rgba(129, 140, 248, 0.4)",
              color: "#818CF8",
              padding: "10px 24px",
              borderRadius: "9999px",
              fontSize: 20,
              fontWeight: 700,
              letterSpacing: "0.1em",
              textTransform: "uppercase",
            }}
          >
            {topic}
          </div>
        ) : <div />}

        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 12,
            backgroundColor: "rgba(0, 0, 0, 0.4)",
            border: "1px solid rgba(255, 255, 255, 0.1)",
            padding: "8px 20px",
            borderRadius: "12px",
          }}
        >
          <div
            style={{
              width: 12,
              height: 12,
              borderRadius: "50%",
              backgroundColor: "#EF4444",
              boxShadow: "0 0 10px #EF4444",
            }}
          />
          <span style={{ color: "#E2E8F0", fontSize: 18, fontWeight: 700, letterSpacing: "0.05em" }}>
            YTCREATE
          </span>
        </div>
      </div>

      {/* Center Hero: Punchy Concept & Title */}
      <div style={{ display: "flex", flexDirection: "column", gap: 24, maxWidth: "90%" }}>
        <h1
          style={{
            margin: 0,
            fontSize: displayConcept.length > 30 ? 58 : 72,
            fontWeight: 900,
            lineHeight: 1.1,
            letterSpacing: "-0.02em",
            color: "#FFFFFF",
            textShadow: "0 4px 24px rgba(0, 0, 0, 0.8)",
            display: "-webkit-box",
            WebkitLineClamp: 2,
            WebkitBoxOrient: "vertical",
            overflow: "hidden",
          }}
        >
          <span style={{ color: "#FACC15", textShadow: "0 0 35px rgba(250, 204, 21, 0.4)" }}>
            {displayConcept}
          </span>
        </h1>

        {displaySubtitle && (
          <p
            style={{
              margin: 0,
              fontSize: 28,
              fontWeight: 500,
              color: "#CBD5E1",
              lineHeight: 1.35,
              maxWidth: 900,
              display: "-webkit-box",
              WebkitLineClamp: 2,
              WebkitBoxOrient: "vertical",
              overflow: "hidden",
              textShadow: "0 2px 10px rgba(0, 0, 0, 0.6)",
            }}
          >
            {displaySubtitle}
          </p>
        )}
      </div>

      {/* Bottom row accent bar */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 16,
        }}
      >
        <div
          style={{
            height: 6,
            width: 120,
            borderRadius: 3,
            background: "linear-gradient(90deg, #FACC15 0%, #EF4444 100%)",
          }}
        />
        <span style={{ color: "#94A3B8", fontSize: 16, fontWeight: 600, letterSpacing: "0.08em", textTransform: "uppercase" }}>
          Full Deep Dive • 4K
        </span>
      </div>
    </div>
  );
};
