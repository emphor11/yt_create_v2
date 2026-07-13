import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { type SplitComparisonRenderSpec } from "./SplitComparison";

export function NumberCounter(renderSpec: SplitComparisonRenderSpec) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const leftValue = renderSpec.props.left.value;
  const rightValue = renderSpec.props.right.value;
  const unit = renderSpec.props.left.unit;

  const countSpring = spring({
    frame,
    fps,
    config: { damping: 20, stiffness: 80 },
  });

  const currentValue = Math.round(interpolate(countSpring, [0, 1], [leftValue, rightValue]));

  return (
    <AbsoluteFill
      style={{
        background: "linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%)",
        color: "#ffffff",
        fontFamily: "Inter, ui-sans-serif, system-ui, sans-serif",
        overflow: "hidden",
        padding: "80px 100px",
      }}
    >
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          height: "100%",
          justifyContent: "space-between",
          alignItems: "center",
          textAlign: "center",
        }}
      >
        <header>
          <div
            style={{
              color: "#a855f7",
              fontSize: 24,
              fontWeight: 800,
              textTransform: "uppercase",
              letterSpacing: 2,
            }}
          >
            REALTIME COUNTER
          </div>
          <div
            style={{
              fontSize: 54,
              fontWeight: 900,
              marginTop: 16,
            }}
          >
            Watch the scaling metrics comparison
          </div>
        </header>

        <main
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <div style={{ color: "#9ca3af", fontSize: 28, fontWeight: 700, textTransform: "uppercase" }}>
            {renderSpec.props.left.label} ➔ {renderSpec.props.right.label}
          </div>
          <div
            style={{
              fontSize: 160,
              fontWeight: 950,
              color: "#a855f7",
              lineHeight: 1,
              marginTop: 20,
              textShadow: "0 0 40px rgba(168, 85, 247, 0.4)",
            }}
          >
            {unit === "INR" ? "₹" : ""}{currentValue.toLocaleString()} {unit !== "INR" ? unit : ""}
          </div>
        </main>

        <footer style={{ fontSize: 26, color: "#9ca3af", fontWeight: 600 }}>
          Compound difference scaling up automatically.
        </footer>
      </div>
    </AbsoluteFill>
  );
}
