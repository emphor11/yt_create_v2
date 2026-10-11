import React from "react";
import { type PrimitiveSpec, type TextProps } from "./types";
import { evaluateAnimatedProperty } from "./animation";

interface PrimitiveComponentProps {
  spec: PrimitiveSpec<TextProps>;
  currentFrame: number;
  fps: number;
}

export const PrimitiveText: React.FC<PrimitiveComponentProps> = ({
  spec,
  currentFrame,
  fps,
}) => {
  const { props, style = {}, animations = [] } = spec;

  const content = evaluateAnimatedProperty(
    "content",
    props.content,
    animations,
    currentFrame,
    fps
  );

  const fill = evaluateAnimatedProperty(
    "style.fill",
    style.fill || "#f4f4f5",
    animations,
    currentFrame,
    fps
  );

  const fontSize = props.font_size ?? 32;
  const fontWeight = props.font_weight ?? 500;
  const lineHeight = props.line_height ?? 1.3;
  const letterSpacing = props.letter_spacing ?? 0;
  const align = props.align ?? "left";
  const textTransform = props.text_transform ?? "none";
  const wrap = props.wrap ?? true;
  const highlights = props.highlight_spans || [];

  // Render text with highlight spans if any
  const renderContent = () => {
    if (!highlights || highlights.length === 0) {
      return content;
    }

    let elements: React.ReactNode[] = [content];

    for (const h of highlights) {
      const target = h.word.toLowerCase();
      const nextElements: React.ReactNode[] = [];

      for (const el of elements) {
        if (typeof el !== "string") {
          nextElements.push(el);
          continue;
        }

        const lower = el.toLowerCase();
        let start = 0;
        let idx = lower.indexOf(target, start);

        if (idx === -1) {
          nextElements.push(el);
          continue;
        }

        while (idx !== -1) {
          if (idx > start) {
            nextElements.push(el.slice(start, idx));
          }
          const matched = el.slice(idx, idx + target.length);
          nextElements.push(
            <span
              key={`${target}-${idx}`}
              style={{
                display: "inline-block",
                color: h.color || "#38bdf8",
                backgroundColor: h.background || "rgba(56, 189, 248, 0.16)",
                padding: "2px 8px",
                borderRadius: "6px",
                margin: "0 2px",
                fontWeight: 700,
              }}
            >
              {matched}
            </span>
          );
          start = idx + target.length;
          idx = lower.indexOf(target, start);
        }

        if (start < el.length) {
          nextElements.push(el.slice(start));
        }
      }

      elements = nextElements;
    }

    return elements;
  };

  return (
    <div
      style={{
        color: fill,
        fontSize: `${fontSize}px`,
        fontWeight,
        lineHeight,
        letterSpacing: `${letterSpacing}px`,
        textAlign: align,
        textTransform,
        whiteSpace: wrap ? "normal" : "nowrap",
        fontFamily: "Inter, ui-sans-serif, system-ui, sans-serif",
      }}
    >
      {renderContent()}
    </div>
  );
};
