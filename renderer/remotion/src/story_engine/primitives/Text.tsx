import React from "react";
import { TextProps } from "../types";
import { handDrawn } from "../hand-drawn-theme.ts";

interface TextComponentProps {
  props: TextProps;
  style?: React.CSSProperties;
}

export const TextPrimitive: React.FC<TextComponentProps> = ({ props, style }) => {
  const variant = props.variant || "title";
  const inkBlack = handDrawn.colors.ink; // #202522 deep black

  // Prevent washed-out white text on cream/paper background
  const isLightOrWhite =
    !props.color ||
    props.color.toLowerCase() === "#f8fafc" ||
    props.color.toLowerCase() === "#ffffff" ||
    props.color.toLowerCase() === "#fff" ||
    props.color.toLowerCase() === "#f1f5f9" ||
    props.color.toLowerCase() === "white";

  let fontSize = 44;
  let fontWeight = 700;
  let color = isLightOrWhite ? inkBlack : props.color;

  if (variant === "title") {
    fontSize = 50;
    fontWeight = 800;
    color = isLightOrWhite ? inkBlack : props.color;
  } else if (variant === "subtitle") {
    fontSize = 36;
    fontWeight = 600;
    color = isLightOrWhite ? handDrawn.colors.inkMuted : props.color;
  } else if (variant === "caption") {
    fontSize = 32;
    fontWeight = 600;
    color = isLightOrWhite ? inkBlack : props.color;
  } else if (variant === "label") {
    fontSize = 28;
    fontWeight = 600;
    color = isLightOrWhite ? inkBlack : props.color;
  }

  return (
    <div
      style={{
        fontFamily: variant === "title" ? handDrawn.font.display : handDrawn.font.body,
        fontSize,
        fontWeight,
        color,
        lineHeight: 1.35,
        textAlign: "center",
        maxWidth: "92%",
        margin: "0 auto",
        letterSpacing: "-0.015em",
        wordBreak: "break-word",
        ...style,
      }}
    >
      {props.text}
    </div>
  );
};
