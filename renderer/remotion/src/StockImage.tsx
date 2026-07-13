import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { type SplitComparisonRenderSpec } from "./SplitComparison";

export function StockImage(renderSpec: SplitComparisonRenderSpec) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const imgSpring = spring({
    frame,
    fps,
    config: { damping: 24, stiffness: 60 },
  });

  return (
    <AbsoluteFill
      style={{
        background: "#030712",
        color: "#ffffff",
        fontFamily: "Inter, ui-sans-serif, system-ui, sans-serif",
        overflow: "hidden",
      }}
    >
      {/* Stock Image Background Layer (using premium Unsplash architecture background as standard) */}
      <img
        src="https://images.unsplash.com/photo-1560518883-ce09059eeffa?auto=format&fit=crop&w=1920&q=80"
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
          opacity: 0.35 * imgSpring,
          transform: `scale(${1 + (1 - imgSpring) * 0.05})`,
        }}
        alt="Stock background"
      />

      {/* Grid overlay */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: "radial-gradient(circle, transparent 40%, rgba(3,7,18,0.85) 100%)",
        }}
      />

      <div
        style={{
          position: "absolute",
          inset: 0,
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          padding: "80px 100px",
        }}
      >
        <header>
          <div
            style={{
              color: "#38bdf8",
              fontSize: 24,
              fontWeight: 800,
              textTransform: "uppercase",
              letterSpacing: 2,
            }}
          >
            CONCEPTUAL OUTLINE
          </div>
          <div
            style={{
              fontSize: 54,
              fontWeight: 900,
              marginTop: 16,
              maxWidth: "1000px",
            }}
          >
            Factual visual context representation
          </div>
        </header>

        <main style={{ display: "flex", gap: "40px", marginTop: "40px" }}>
          <div
            style={{
              background: "rgba(15, 23, 42, 0.75)",
              border: "1px solid rgba(255, 255, 255, 0.15)",
              borderRadius: "12px",
              padding: "36px",
              flex: 1,
              backdropFilter: "blur(8px)",
              transform: `translateY(${(1 - imgSpring) * 30}px)`,
              opacity: imgSpring,
            }}
          >
            <div style={{ color: "#38bdf8", fontSize: 24, fontWeight: 800, textTransform: "uppercase" }}>
              {renderSpec.props.left.label}
            </div>
            <div style={{ fontSize: 64, fontWeight: 950, color: "#ffffff", marginTop: 16 }}>
              {renderSpec.props.left.raw}
            </div>
          </div>

          <div
            style={{
              background: "rgba(15, 23, 42, 0.85)",
              border: "1.5px solid rgba(56, 189, 248, 0.4)",
              borderRadius: "12px",
              padding: "36px",
              flex: 1,
              backdropFilter: "blur(8px)",
              transform: `translateY(${(1 - imgSpring) * 40}px)`,
              opacity: imgSpring,
            }}
          >
            <div style={{ color: "#0ea5e9", fontSize: 24, fontWeight: 800, textTransform: "uppercase" }}>
              {renderSpec.props.right.label}
            </div>
            <div style={{ fontSize: 64, fontWeight: 950, color: "#38bdf8", marginTop: 16 }}>
              {renderSpec.props.right.raw}
            </div>
          </div>
        </main>

        <footer style={{ fontSize: 24, color: "#9ca3af", fontWeight: 600 }}>
          Background illustration matches target domain themes.
        </footer>
      </div>
    </AbsoluteFill>
  );
}
