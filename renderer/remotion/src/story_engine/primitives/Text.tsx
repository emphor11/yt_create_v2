import React from "react";
import { TextProps } from "../types";
import { handDrawn } from "../hand-drawn-theme.ts";

export interface TextComponentProps {
  props: TextProps;
  width?: number;
  height?: number;
  layout?: string;
  style?: React.CSSProperties;
}

export const TextPrimitive: React.FC<TextComponentProps> = ({
  props,
  width,
  height,
  layout,
  style,
}) => {
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

  const len = (props.text || "").length;
  const isCompact = (width ?? 800) <= 600 || (height ?? 160) <= 120;

  let fontSize = 44;
  let fontWeight = 700;
  let color = isLightOrWhite ? inkBlack : props.color;

  if (variant === "title") {
    fontWeight = 800;
    if (len > 90) {
      fontSize = isCompact ? 24 : 28;
    } else if (len > 60) {
      fontSize = isCompact ? 28 : 34;
    } else if (len > 35) {
      fontSize = isCompact ? 34 : 40;
    } else {
      fontSize = isCompact ? 40 : 48;
    }
  } else if (variant === "subtitle") {
    fontWeight = 600;
    color = isLightOrWhite ? handDrawn.colors.inkMuted : props.color;
    if (len > 80) {
      fontSize = isCompact ? 20 : 24;
    } else if (len > 45) {
      fontSize = isCompact ? 24 : 28;
    } else {
      fontSize = isCompact ? 28 : 34;
    }
  } else if (variant === "caption") {
    fontSize = isCompact ? 22 : 28;
    fontWeight = 600;
    color = isLightOrWhite ? inkBlack : props.color;
  } else if (variant === "label") {
    fontSize = isCompact ? 18 : 24;
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
        lineHeight: 1.28,
        textAlign: "center",
        maxWidth: "94%",
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
