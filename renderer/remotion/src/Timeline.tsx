import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { type SplitComparisonRenderSpec } from "./SplitComparison";

export function Timeline(renderSpec: SplitComparisonRenderSpec) {
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

  const springProgress = spring({
    frame,
    fps,
    config: { damping: 15, stiffness: 100 },
  });

  return (
    <AbsoluteFill
      style={{
        background: "linear-gradient(135deg, #111827 0%, #1f2937 100%)",
        color: "#f3f4f6",
        fontFamily: "Inter, ui-sans-serif, system-ui, sans-serif",
        overflow: "hidden",
        padding: "80px 100px",
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
        <header>
          <div
            style={{
              color: "#3b82f6",
              fontSize: 24,
              fontWeight: 800,
              textTransform: "uppercase",
              letterSpacing: 2,
            }}
          >
            TIMELINE MILESTONES
          </div>
          <div
            style={{
              fontSize: 54,
              fontWeight: 900,
              marginTop: 16,
            }}
          >
            Tracking the progression over time
          </div>
        </header>

        <main
          style={{
            position: "relative",
            display: "flex",
            alignItems: "center",
            height: "300px",
          }}
        >
          {/* Main timeline track line */}
          <div
            style={{
              position: "absolute",
              left: 0,
              right: 0,
              height: "8px",
              background: "#374151",
              borderRadius: "4px",
            }}
          />
          {/* Animated filled progress path */}
          <div
            style={{
              position: "absolute",
              left: 0,
              width: `${interpolate(springProgress, [0, 1], [0, 100])}%`,
              height: "8px",
              background: "linear-gradient(90deg, #3b82f6 0%, #60a5fa 100%)",
              borderRadius: "4px",
              boxShadow: "0 0 16px rgba(59, 130, 246, 0.5)",
            }}
          />

          {/* Left Node */}
          <div
            style={{
              position: "absolute",
              left: "10%",
              transform: "translateX(-50%)",
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              opacity: springProgress,
            }}
          >
            <div
              style={{
                width: "36px",
                height: "36px",
                borderRadius: "50%",
                background: "#3b82f6",
                border: "6px solid #111827",
                boxShadow: "0 0 10px rgba(59, 130, 246, 0.8)",
              }}
            />
            <div style={{ marginTop: "16px", textAlign: "center" }}>
              <div style={{ fontSize: 24, color: "#9ca3af", fontWeight: 700 }}>
                {renderSpec.props.left.label}
              </div>
              <div style={{ fontSize: 44, fontWeight: 900, color: "#3b82f6", marginTop: 4 }}>
                {renderSpec.props.left.raw}
              </div>
            </div>
          </div>

          {/* Right Node */}
          <div
            style={{
              position: "absolute",
              left: "90%",
              transform: "translateX(-50%)",
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              opacity: shiftProgress,
            }}
          >
            <div
              style={{
                width: "36px",
                height: "36px",
                borderRadius: "50%",
                background: "#60a5fa",
                border: "6px solid #111827",
                boxShadow: "0 0 10px rgba(96, 165, 250, 0.8)",
              }}
            />
            <div style={{ marginTop: "16px", textAlign: "center" }}>
              <div style={{ fontSize: 24, color: "#9ca3af", fontWeight: 700 }}>
                {renderSpec.props.right.label}
              </div>
              <div style={{ fontSize: 44, fontWeight: 900, color: "#60a5fa", marginTop: 4 }}>
                {renderSpec.props.right.raw}
              </div>
            </div>
          </div>
        </main>

        <footer style={{ textAlign: "center", fontSize: 28, color: "#9ca3af", fontWeight: 600 }}>
          Timeline shifts are driven by decision logic.
        </footer>
      </div>
    </AbsoluteFill>
  );
}
