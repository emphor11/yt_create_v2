import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

import { type SplitComparisonRenderSpec, type RenderFrameSpan } from "./types";
import { tokens } from "./design-tokens";

function spanById(renderSpec: SplitComparisonRenderSpec, eventId: string) {
  return renderSpec.frame_spans?.find((span) => span.event_id === eventId);
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

function formatValue(side: any) {
  return side?.raw || "";
}

export function SplitComparison(renderSpec: SplitComparisonRenderSpec) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const duration_frames = renderSpec.duration_frames || 180;
  const fullPriceSpan = spanById(renderSpec, "event_full_price");
  const monthlyPaymentSpan = spanById(renderSpec, "event_monthly_payment");
  const attentionShiftSpan = spanById(
    renderSpec,
    renderSpec.props.attention_shift_event_id || ""
  );

  const props = renderSpec.props as any;

  // Extract roles, labels, values, and units safely
  const leftRole = props.leftRole || props.left?.role || props.leftLabel || props.left?.label || "Before";
  const leftLabel = props.leftLabel && props.leftLabel !== leftRole ? props.leftLabel : (props.left?.label || "");
  const leftRawVal = props.leftValue !== undefined ? String(props.leftValue) : (formatValue(props.left) || "0");
  const leftUnit = props.leftUnit || props.left?.unit || "";

  const rightRole = props.rightRole || props.right?.role || props.rightLabel || props.right?.label || "After";
  const rightLabel = props.rightLabel && props.rightLabel !== rightRole ? props.rightLabel : (props.right?.label || "");
  const rightRawVal = props.rightValue !== undefined ? String(props.rightValue) : (formatValue(props.right) || "0");
  const rightUnit = props.rightUnit || props.right?.unit || "";

  const leftProgress = fullPriceSpan
    ? progressForSpan(frame, fullPriceSpan)
    : interpolate(frame, [0, 15], [0, 1], { extrapolateRight: "clamp" });

  const rightStartFrame = monthlyPaymentSpan?.start_frame ?? Math.round(duration_frames * 0.25);
  const rightProgress = monthlyPaymentSpan
    ? progressForSpan(frame, monthlyPaymentSpan)
    : interpolate(frame, [rightStartFrame, rightStartFrame + 15], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  const shiftStartFrame = attentionShiftSpan?.start_frame ?? Math.round(duration_frames * 0.55);
  const shiftProgress = attentionShiftSpan
    ? progressForSpan(frame, attentionShiftSpan)
    : interpolate(frame, [shiftStartFrame, shiftStartFrame + Math.round(duration_frames * 0.15)], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  const leftSpring = spring({
    frame: Math.max(0, frame - (fullPriceSpan?.start_frame ?? 0)),
    fps,
    config: { damping: 18, stiffness: 110 },
  });
  const rightSpring = spring({
    frame: Math.max(0, frame - rightStartFrame),
    fps,
    config: { damping: 18, stiffness: 110 },
  });
  const focusWidth = interpolate(shiftProgress, [0, 1], [46, 64]);
  const leftOpacity = interpolate(shiftProgress, [0, 1], [1, 0.58]);

  return (
    <AbsoluteFill
      style={{
        background: tokens.bg.base,
        backdropFilter: "blur(4px)",
        color: tokens.text.primary,
        fontFamily: tokens.font.family,
        overflow: "hidden",
      }}
    >
      <div
        style={{
          position: "absolute",
          inset: 0,
          background:
            "linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px), linear-gradient(0deg, rgba(255,255,255,0.02) 1px, transparent 1px)",
          backgroundSize: "96px 96px",
        }}
      />
      <div
        style={{
          position: "relative",
          display: "grid",
          gridTemplateRows: "auto 1fr auto",
          height: "100%",
          padding: tokens.spacing.padding,
        }}
      >
        <header>
          <div
            style={{
              color: tokens.accent.cyan,
              fontSize: tokens.font.eyebrow,
              fontWeight: 800,
              letterSpacing: 2,
              textTransform: "uppercase",
            }}
          >
            {renderSpec.props.headerLabel || "COMPARISON"}
          </div>
          {renderSpec.props.title && (
            <div
              style={{
                fontSize: 64,
                fontWeight: 900,
                lineHeight: 1.1,
                marginTop: 16,
                maxWidth: 1200,
                color: tokens.text.primary,
              }}
            >
              {renderSpec.props.title}
            </div>
          )}
        </header>

        <main
          style={{
            alignItems: "center",
            display: "grid",
            gap: 34,
            gridTemplateColumns: `${100 - focusWidth}% ${focusWidth}%`,
            marginTop: 32,
            transition: "grid-template-columns 200ms ease",
          }}
        >
          {/* Left Panel - Dark Glass Red Accent */}
          <section
            style={{
              border: "2px solid rgba(244, 63, 94, 0.35)",
              borderRadius: 16,
              background: tokens.bg.cardLeft,
              boxShadow: "0 24px 70px rgba(0, 0, 0, 0.5)",
              minHeight: 400,
              opacity: leftOpacity * leftProgress,
              padding: 44,
              display: "flex",
              flexDirection: "column",
              justifyContent: "space-between",
              transform: `translateY(${(1 - leftSpring) * 40}px)`,
              backdropFilter: "blur(8px)",
            }}
          >
            <div>
              <div
                style={{
                  color: tokens.accent.rose,
                  fontSize: 28,
                  fontWeight: 900,
                  textTransform: "uppercase",
                  letterSpacing: 1.5,
                }}
              >
                {leftRole}
              </div>
              {leftLabel ? (
                <div style={{ color: tokens.text.secondary, fontSize: 22, marginTop: 6, fontWeight: 600 }}>
                  {leftLabel}
                </div>
              ) : null}
            </div>
            <div
              style={{
                color: tokens.accent.rose,
                fontSize: 104,
                fontWeight: 950,
                lineHeight: 1,
                marginTop: 36,
                textShadow: "0 0 30px rgba(244, 63, 94, 0.3)",
              }}
            >
              {leftRawVal}{leftUnit ? <span style={{ fontSize: 44, marginLeft: 10, color: tokens.text.secondary }}>{leftUnit}</span> : null}
            </div>
          </section>

          {/* Right Panel - Dark Glass Emerald Accent */}
          <section
            style={{
              border: "3px solid rgba(16, 185, 129, 0.45)",
              borderRadius: 16,
              background: tokens.bg.cardRight,
              boxShadow: `0 28px 86px rgba(16, 185, 129, ${0.15 + shiftProgress * 0.2})`,
              minHeight: 400,
              opacity: rightProgress,
              padding: 44,
              display: "flex",
              flexDirection: "column",
              justifyContent: "space-between",
              transform: `translateY(${(1 - rightSpring) * 44}px) scale(${
                1 + shiftProgress * 0.035
              })`,
              backdropFilter: "blur(8px)",
            }}
          >
            <div>
              <div
                style={{
                  color: tokens.accent.emerald,
                  fontSize: 28,
                  fontWeight: 900,
                  textTransform: "uppercase",
                  letterSpacing: 1.5,
                }}
              >
                {rightRole}
              </div>
              {rightLabel ? (
                <div style={{ color: tokens.text.secondary, fontSize: 22, marginTop: 6, fontWeight: 600 }}>
                  {rightLabel}
                </div>
              ) : null}
            </div>
            <div
              style={{
                color: tokens.accent.emerald,
                fontSize: 110,
                fontWeight: 950,
                lineHeight: 1,
                marginTop: 36,
                textShadow: "0 0 30px rgba(16, 185, 129, 0.4)",
              }}
            >
              {rightRawVal}{rightUnit ? <span style={{ fontSize: 44, marginLeft: 10, color: tokens.text.secondary }}>{rightUnit}</span> : null}
            </div>
          </section>
        </main>

        {renderSpec.props.footerLabel ? (
          <footer
            style={{
              alignItems: "center",
              color: tokens.text.muted,
              display: "flex",
              fontSize: 26,
              fontWeight: 700,
              justifyContent: "center",
            }}
          >
            <span>{renderSpec.props.footerLabel}</span>
          </footer>
        ) : null}
      </div>
    </AbsoluteFill>
  );
}
