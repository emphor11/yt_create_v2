import React from "react";
import { TextProps } from "../types";
import { tokens } from "../../design-tokens";

interface TextComponentProps {
  props: TextProps;
  style?: React.CSSProperties;
}

export const TextPrimitive: React.FC<TextComponentProps> = ({ props, style }) => {
  const variant = props.variant || "label";

  let fontSize = 20;
  let fontWeight = 500;
  let color = props.color || tokens.text.secondary;

  if (variant === "title") {
    fontSize = 32;
    fontWeight = 700;
    color = props.color || tokens.text.primary;
  } else if (variant === "subtitle") {
    fontSize = 24;
    fontWeight = 600;
    color = props.color || tokens.text.secondary;
  } else if (variant === "caption") {
    fontSize = 18;
    fontWeight = 500;
    color = props.color || tokens.text.muted;
  }

  return (
    <div
      style={{
        fontFamily: tokens.font.family,
        fontSize,
        fontWeight,
        color,
        lineHeight: 1.3,
        ...style,
      }}
    >
      {props.text}
    </div>
  );
};
