import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { type SplitComparisonRenderSpec } from "./SplitComparison";

export function StockVideo(renderSpec: SplitComparisonRenderSpec) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const scaleSpring = spring({
    frame,
    fps,
    config: { damping: 20, stiffness: 70 },
  });

  // Animating circles to simulate dynamic video/stock motion
  const pulse = Math.sin(frame * 0.05) * 0.05 + 1;

  return (
    <AbsoluteFill
      style={{
        background: "#080710",
        color: "#ffffff",
        fontFamily: "Inter, ui-sans-serif, system-ui, sans-serif",
        overflow: "hidden",
      }}
    >
      {/* Simulated stock video looping circles background */}
      <div
        style={{
          position: "absolute",
          top: "50%",
          left: "50%",
          width: "800px",
          height: "800px",
          borderRadius: "50%",
          background: "radial-gradient(circle, rgba(139,92,246,0.18) 0%, transparent 70%)",
          transform: `translate(-50%, -50%) scale(${pulse * scaleSpring})`,
        }}
      />
      <div
        style={{
          position: "absolute",
          top: "30%",
          left: "20%",
          width: "400px",
          height: "400px",
          borderRadius: "50%",
          background: "radial-gradient(circle, rgba(59,130,246,0.12) 0%, transparent 60%)",
          transform: `scale(${pulse})`,
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
              color: "#a78bfa",
              fontSize: 24,
              fontWeight: 800,
              textTransform: "uppercase",
              letterSpacing: 2,
            }}
          >
            DYNAMIC FOOTAGE
          </div>
          <div
            style={{
              fontSize: 54,
              fontWeight: 900,
              marginTop: 16,
            }}
          >
            Contextual stock video playback reference
          </div>
        </header>

        <main style={{ display: "flex", gap: "40px" }}>
          <div
            style={{
              background: "rgba(17, 12, 34, 0.8)",
              border: "1px solid rgba(167, 139, 250, 0.25)",
              borderRadius: "12px",
              padding: "36px",
              flex: 1,
              transform: `translateY(${(1 - scaleSpring) * 20}px)`,
              opacity: scaleSpring,
            }}
          >
            <div style={{ color: "#a78bfa", fontSize: 24, fontWeight: 800, textTransform: "uppercase" }}>
              {renderSpec.props.left.label}
            </div>
            <div style={{ fontSize: 64, fontWeight: 950, marginTop: 16 }}>
              {renderSpec.props.left.raw}
            </div>
          </div>

          <div
            style={{
              background: "rgba(17, 12, 34, 0.9)",
              border: "1.5px solid rgba(167, 139, 250, 0.5)",
              borderRadius: "12px",
              padding: "36px",
              flex: 1,
              transform: `translateY(${(1 - scaleSpring) * 30}px)`,
              opacity: scaleSpring,
            }}
          >
            <div style={{ color: "#c084fc", fontSize: 24, fontWeight: 800, textTransform: "uppercase" }}>
              {renderSpec.props.right.label}
            </div>
            <div style={{ fontSize: 64, fontWeight: 950, color: "#a78bfa", marginTop: 16 }}>
              {renderSpec.props.right.raw}
            </div>
          </div>
        </main>

        <footer style={{ fontSize: 24, color: "#9ca3af", fontWeight: 600 }}>
          High definition media layer overlays.
        </footer>
      </div>
    </AbsoluteFill>
  );
}
