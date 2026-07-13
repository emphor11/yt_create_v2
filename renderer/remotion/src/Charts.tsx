import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { type SplitComparisonRenderSpec } from "./SplitComparison";

export function Charts(renderSpec: SplitComparisonRenderSpec) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const attentionShiftSpan = renderSpec.frame_spans.find(
    (span) => span.event_id === renderSpec.props.attention_shift_event_id
  );

  const shiftProgress = attentionShiftSpan
    ? interpolate(
        frame,
        [
          attentionShiftSpan.start_frame,
          attentionShiftSpan.start_frame + Math.min(24, attentionShiftSpan.duration_frames),
        ],
        [0, 1],
        { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
      )
    : 0;

  const leftSpring = spring({
    frame,
    fps,
    config: { damping: 18, stiffness: 100 },
  });

  const rightSpring = spring({
    frame: Math.max(0, frame - 30), // Delay the right bar animation slightly for dynamic appeal
    fps,
    config: { damping: 18, stiffness: 100 },
  });

  const maxVal = Math.max(renderSpec.props.left.value, renderSpec.props.right.value, 1);
  const leftPercent = (renderSpec.props.left.value / maxVal) * 80;
  const rightPercent = (renderSpec.props.right.value / maxVal) * 80;

  return (
    <AbsoluteFill
      style={{
        background: "linear-gradient(135deg, #111827 0%, #030712 100%)",
        color: "#f9fafb",
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
              color: "#10b981",
              fontSize: 24,
              fontWeight: 800,
              textTransform: "uppercase",
              letterSpacing: 2,
            }}
          >
            DATA VISUALIZATION
          </div>
          <div
            style={{
              fontSize: 54,
              fontWeight: 900,
              marginTop: 16,
            }}
          >
            Comparative analysis metrics
          </div>
        </header>

        <main
          style={{
            display: "flex",
            justifyContent: "center",
            alignItems: "flex-end",
            height: "450px",
            gap: "120px",
            borderBottom: "4px solid #374151",
            paddingBottom: "20px",
          }}
        >
          {/* Left Bar */}
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              width: "180px",
            }}
          >
            <div
              style={{
                fontSize: 34,
                fontWeight: 900,
                color: "#10b981",
                marginBottom: 16,
                opacity: leftSpring,
              }}
            >
              {renderSpec.props.left.raw}
            </div>
            <div
              style={{
                width: "100%",
                height: `${leftPercent * leftSpring}%`,
                background: "linear-gradient(0deg, #047857 0%, #10b981 100%)",
                borderRadius: "8px 8px 0 0",
                boxShadow: "0 0 20px rgba(16, 185, 129, 0.3)",
              }}
            />
            <div style={{ marginTop: 20, fontSize: 24, fontWeight: 700, color: "#9ca3af", textAlign: "center" }}>
              {renderSpec.props.left.label}
            </div>
          </div>

          {/* Right Bar */}
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              width: "180px",
            }}
          >
            <div
              style={{
                fontSize: 34,
                fontWeight: 900,
                color: "#3b82f6",
                marginBottom: 16,
                opacity: rightSpring,
              }}
            >
              {renderSpec.props.right.raw}
            </div>
            <div
              style={{
                width: "100%",
                height: `${rightPercent * rightSpring}%`,
                background: "linear-gradient(0deg, #1d4ed8 0%, #3b82f6 100%)",
                borderRadius: "8px 8px 0 0",
                boxShadow: "0 0 20px rgba(59, 130, 246, 0.3)",
              }}
            />
            <div style={{ marginTop: 20, fontSize: 24, fontWeight: 700, color: "#9ca3af", textAlign: "center" }}>
              {renderSpec.props.right.label}
            </div>
          </div>
        </main>

        <footer style={{ textAlign: "center", fontSize: 26, color: "#9ca3af", fontWeight: 600 }}>
          Visual comparison highlights the ratio gap clearly.
        </footer>
      </div>
    </AbsoluteFill>
  );
}
