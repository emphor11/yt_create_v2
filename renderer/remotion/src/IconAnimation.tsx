import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { type SplitComparisonRenderSpec } from "./SplitComparison";

export function IconAnimation(renderSpec: SplitComparisonRenderSpec) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const iconSpring = spring({
    frame,
    fps,
    config: { damping: 12, stiffness: 130 },
  });

  return (
    <AbsoluteFill
      style={{
        background: "linear-gradient(135deg, #090514 0%, #1c0e35 100%)",
        color: "#f5f3ff",
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
              color: "#a78bfa",
              fontSize: 24,
              fontWeight: 800,
              textTransform: "uppercase",
              letterSpacing: 2,
            }}
          >
            ICON METAPHORS
          </div>
          <div
            style={{
              fontSize: 54,
              fontWeight: 900,
              marginTop: 16,
            }}
          >
            Visual domain representations
          </div>
        </header>

        <main
          style={{
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            gap: "100px",
            flex: 1,
          }}
        >
          {/* Left Icon Block */}
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              transform: `scale(${iconSpring})`,
              opacity: iconSpring,
            }}
          >
            <div
              style={{
                width: "160px",
                height: "160px",
                borderRadius: "32px",
                background: "rgba(167, 139, 250, 0.15)",
                border: "2px solid #a78bfa",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: 64,
                boxShadow: "0 0 30px rgba(167, 139, 250, 0.2)",
              }}
            >
              💼
            </div>
            <div style={{ marginTop: 24, fontSize: 28, fontWeight: 800, color: "#c084fc" }}>
              {renderSpec.props.left.label}
            </div>
            <div style={{ fontSize: 34, fontWeight: 900, color: "#ffffff", marginTop: 8 }}>
              {renderSpec.props.left.raw}
            </div>
          </div>

          <div style={{ fontSize: 48, color: "#a78bfa", opacity: iconSpring }}>➔</div>

          {/* Right Icon Block */}
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              transform: `scale(${iconSpring})`,
              opacity: iconSpring,
            }}
          >
            <div
              style={{
                width: "160px",
                height: "160px",
                borderRadius: "32px",
                background: "rgba(192, 132, 252, 0.2)",
                border: "3px solid #c084fc",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: 64,
                boxShadow: "0 0 40px rgba(192, 132, 252, 0.3)",
              }}
            >
              🏠
            </div>
            <div style={{ marginTop: 24, fontSize: 28, fontWeight: 800, color: "#c084fc" }}>
              {renderSpec.props.right.label}
            </div>
            <div style={{ fontSize: 34, fontWeight: 900, color: "#ffffff", marginTop: 8 }}>
              {renderSpec.props.right.raw}
            </div>
          </div>
        </main>

        <footer style={{ textAlign: "center", fontSize: 26, color: "#a78bfa", fontWeight: 600 }}>
          Animated representations map onto core concepts.
        </footer>
      </div>
    </AbsoluteFill>
  );
}
