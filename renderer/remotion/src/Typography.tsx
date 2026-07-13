import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { type SplitComparisonRenderSpec } from "./SplitComparison";

export function Typography(renderSpec: SplitComparisonRenderSpec) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const titleSpring = spring({
    frame,
    fps,
    config: { damping: 14, stiffness: 120 },
  });

  const valueSpring = spring({
    frame: Math.max(0, frame - 15),
    fps,
    config: { damping: 14, stiffness: 120 },
  });

  return (
    <AbsoluteFill
      style={{
        background: "#09090b",
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
        }}
      >
        <header>
          <div
            style={{
              color: "#f43f5e",
              fontSize: 24,
              fontWeight: 800,
              textTransform: "uppercase",
              letterSpacing: 2,
            }}
          >
            FOCUS PHRASE
          </div>
        </header>

        <main
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "flex-start",
            justifyContent: "center",
            flex: 1,
          }}
        >
          <div
            style={{
              fontSize: 90,
              fontWeight: 950,
              lineHeight: 1.1,
              letterSpacing: -2,
              transform: `scale(${interpolate(titleSpring, [0, 1], [0.92, 1])})`,
              opacity: titleSpring,
            }}
          >
            {renderSpec.props.left.label}
          </div>
          <div
            style={{
              fontSize: 100,
              fontWeight: 950,
              color: "#f43f5e",
              lineHeight: 1.1,
              letterSpacing: -2,
              marginTop: 10,
              transform: `scale(${interpolate(valueSpring, [0, 1], [0.92, 1])})`,
              opacity: valueSpring,
            }}
          >
            ➔ {renderSpec.props.right.raw}
          </div>
        </main>

        <footer style={{ fontSize: 24, color: "#71717a", fontWeight: 600 }}>
          Typography focus enforces memorability.
        </footer>
      </div>
    </AbsoluteFill>
  );
}
