import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

type VisualPlanSide = {
  role: string;
  semantic_entity_id: string;
  label: string;
  raw: string;
  value: number;
  unit: string;
};

type SplitComparisonProps = {
  left: VisualPlanSide;
  right: VisualPlanSide;
  attention_shift_event_id: string;
};

type RenderFrameSpan = {
  event_id: string;
  start_frame: number;
  end_frame: number;
  duration_frames: number;
};

export type SplitComparisonRenderSpec = {
  scene_id: string;
  composition: "SplitComparison";
  fps: number;
  duration_frames: number;
  props: SplitComparisonProps;
  frame_spans: RenderFrameSpan[];
};

function spanById(renderSpec: SplitComparisonRenderSpec, eventId: string) {
  return renderSpec.frame_spans.find((span) => span.event_id === eventId);
}

function progressForSpan(frame: number, span: RenderFrameSpan | undefined) {
  if (!span) {
    return 0;
  }
  return interpolate(
    frame,
    [span.start_frame, span.start_frame + Math.min(24, span.duration_frames)],
    [0, 1],
    {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    }
  );
}

function formatValue(side: VisualPlanSide) {
  return side.raw;
}

export function SplitComparison(renderSpec: SplitComparisonRenderSpec) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const fullPriceSpan = spanById(renderSpec, "event_full_price");
  const monthlyPaymentSpan = spanById(renderSpec, "event_monthly_payment");
  const attentionShiftSpan = spanById(
    renderSpec,
    renderSpec.props.attention_shift_event_id
  );
  const leftProgress = progressForSpan(frame, fullPriceSpan);
  const rightProgress = progressForSpan(frame, monthlyPaymentSpan);
  const shiftProgress = progressForSpan(frame, attentionShiftSpan);
  const leftSpring = spring({
    frame: Math.max(0, frame - (fullPriceSpan?.start_frame ?? 0)),
    fps,
    config: { damping: 18, stiffness: 110 },
  });
  const rightSpring = spring({
    frame: Math.max(0, frame - (monthlyPaymentSpan?.start_frame ?? 0)),
    fps,
    config: { damping: 18, stiffness: 110 },
  });
  const focusWidth = interpolate(shiftProgress, [0, 1], [46, 64]);
  const leftOpacity = interpolate(shiftProgress, [0, 1], [1, 0.58]);

  return (
    <AbsoluteFill
      style={{
        background:
          "linear-gradient(135deg, #f5f7fb 0%, #e7f0ed 46%, #f8efe4 100%)",
        color: "#172026",
        fontFamily: "Inter, ui-sans-serif, system-ui, sans-serif",
        overflow: "hidden",
      }}
    >
      <div
        style={{
          position: "absolute",
          inset: 0,
          background:
            "linear-gradient(90deg, rgba(23,32,38,0.045) 1px, transparent 1px), linear-gradient(0deg, rgba(23,32,38,0.035) 1px, transparent 1px)",
          backgroundSize: "96px 96px",
        }}
      />
      <div
        style={{
          position: "relative",
          display: "grid",
          gridTemplateRows: "auto 1fr auto",
          height: "100%",
          padding: "86px 104px 72px",
        }}
      >
        <header>
          <div
            style={{
              color: "#52616f",
              fontSize: 30,
              fontWeight: 800,
              letterSpacing: 0,
              textTransform: "uppercase",
            }}
          >
            EMI perception
          </div>
          <div
            style={{
              fontSize: 68,
              fontWeight: 900,
              lineHeight: 1.08,
              marginTop: 18,
              maxWidth: 1180,
            }}
          >
            The same phone feels different when the price is split.
          </div>
        </header>

        <main
          style={{
            alignItems: "center",
            display: "grid",
            gap: 34,
            gridTemplateColumns: `${100 - focusWidth}% ${focusWidth}%`,
            marginTop: 42,
            transition: "grid-template-columns 200ms ease",
          }}
        >
          <section
            style={{
              border: "2px solid rgba(23, 32, 38, 0.14)",
              borderRadius: 8,
              background: "rgba(255, 255, 255, 0.78)",
              boxShadow: "0 24px 70px rgba(23, 32, 38, 0.12)",
              minHeight: 430,
              opacity: leftOpacity * leftProgress,
              padding: 44,
              transform: `translateY(${(1 - leftSpring) * 40}px)`,
            }}
          >
            <div
              style={{
                color: "#52616f",
                fontSize: 32,
                fontWeight: 900,
                textTransform: "uppercase",
              }}
            >
              {renderSpec.props.left.label}
            </div>
            <div
              style={{
                color: "#7a2730",
                fontSize: 112,
                fontWeight: 950,
                lineHeight: 1,
                marginTop: 58,
              }}
            >
              {formatValue(renderSpec.props.left)}
            </div>
            <div
              style={{
                color: "#52616f",
                fontSize: 34,
                fontWeight: 700,
                marginTop: 40,
              }}
            >
              The actual cost arrives as one big number.
            </div>
          </section>

          <section
            style={{
              border: "3px solid rgba(22, 102, 99, 0.36)",
              borderRadius: 8,
              background: "rgba(255, 255, 255, 0.92)",
              boxShadow: `0 28px 86px rgba(22, 102, 99, ${0.14 + shiftProgress * 0.16})`,
              minHeight: 430,
              opacity: rightProgress,
              padding: 44,
              transform: `translateY(${(1 - rightSpring) * 44}px) scale(${
                1 + shiftProgress * 0.035
              })`,
            }}
          >
            <div
              style={{
                color: "#166663",
                fontSize: 32,
                fontWeight: 900,
                textTransform: "uppercase",
              }}
            >
              {renderSpec.props.right.label}
            </div>
            <div
              style={{
                color: "#166663",
                fontSize: 118,
                fontWeight: 950,
                lineHeight: 1,
                marginTop: 58,
              }}
            >
              {formatValue(renderSpec.props.right)}
            </div>
            <div
              style={{
                color: "#52616f",
                fontSize: 34,
                fontWeight: 800,
                marginTop: 40,
              }}
            >
              Per month feels smaller, so the pain drops.
            </div>
          </section>
        </main>

        <footer
          style={{
            alignItems: "center",
            color: "#172026",
            display: "flex",
            fontSize: 34,
            fontWeight: 850,
            gap: 20,
            justifyContent: "center",
            opacity: interpolate(shiftProgress, [0, 1], [0, 1], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            }),
          }}
        >
          <span>Full price</span>
          <span style={{ color: "#166663" }}>gets reframed as</span>
          <span>monthly comfort</span>
        </footer>
      </div>
    </AbsoluteFill>
  );
}
