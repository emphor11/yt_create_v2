import React, { useId } from "react";
import type {
  CharacterProps,
  CharacterPose,
  CharacterEmotion,
  CharacterFacing,
  VisualStateKind,
} from "../types.ts";

interface Point {
  x: number;
  y: number;
}

interface PoseJoints {
  head: Point;
  neck: Point;
  shoulderCenter: Point;
  spine: Point;
  leftShoulder: Point;
  leftElbow: Point;
  leftHand: Point;
  rightShoulder: Point;
  rightElbow: Point;
  rightHand: Point;
  leftHip: Point;
  leftKnee: Point;
  leftFoot: Point;
  rightHip: Point;
  rightKnee: Point;
  rightFoot: Point;
}

const POSES: Record<CharacterPose, PoseJoints> = {
  idle: {
    head: { x: 120, y: 52 },
    neck: { x: 120, y: 76 },
    shoulderCenter: { x: 120, y: 88 },
    spine: { x: 120, y: 180 },
    leftShoulder: { x: 94, y: 92 },
    leftElbow: { x: 86, y: 136 },
    leftHand: { x: 88, y: 180 },
    rightShoulder: { x: 146, y: 92 },
    rightElbow: { x: 154, y: 136 },
    rightHand: { x: 152, y: 180 },
    leftHip: { x: 104, y: 180 },
    leftKnee: { x: 102, y: 255 },
    leftFoot: { x: 100, y: 330 },
    rightHip: { x: 136, y: 180 },
    rightKnee: { x: 138, y: 255 },
    rightFoot: { x: 140, y: 330 },
  },
  walk: {
    head: { x: 126, y: 50 },
    neck: { x: 124, y: 74 },
    shoulderCenter: { x: 122, y: 86 },
    spine: { x: 116, y: 180 },
    leftShoulder: { x: 96, y: 90 },
    leftElbow: { x: 120, y: 132 },
    leftHand: { x: 142, y: 160 },
    rightShoulder: { x: 148, y: 90 },
    rightElbow: { x: 166, y: 134 },
    rightHand: { x: 176, y: 172 },
    leftHip: { x: 102, y: 180 },
    leftKnee: { x: 74, y: 248 },
    leftFoot: { x: 54, y: 324 },
    rightHip: { x: 132, y: 180 },
    rightKnee: { x: 160, y: 252 },
    rightFoot: { x: 184, y: 330 },
  },
  point: {
    head: { x: 124, y: 50 },
    neck: { x: 122, y: 74 },
    shoulderCenter: { x: 120, y: 86 },
    spine: { x: 118, y: 180 },
    leftShoulder: { x: 94, y: 90 },
    leftElbow: { x: 84, y: 136 },
    leftHand: { x: 86, y: 180 },
    rightShoulder: { x: 146, y: 88 },
    rightElbow: { x: 184, y: 80 },
    rightHand: { x: 226, y: 72 },
    leftHip: { x: 102, y: 180 },
    leftKnee: { x: 96, y: 255 },
    leftFoot: { x: 92, y: 330 },
    rightHip: { x: 134, y: 180 },
    rightKnee: { x: 146, y: 255 },
    rightFoot: { x: 154, y: 330 },
  },
  think: {
    head: { x: 116, y: 52 },
    neck: { x: 118, y: 76 },
    shoulderCenter: { x: 120, y: 88 },
    spine: { x: 120, y: 180 },
    leftShoulder: { x: 94, y: 92 },
    leftElbow: { x: 82, y: 136 },
    leftHand: { x: 120, y: 140 },
    rightShoulder: { x: 146, y: 92 },
    rightElbow: { x: 156, y: 126 },
    rightHand: { x: 130, y: 64 },
    leftHip: { x: 104, y: 180 },
    leftKnee: { x: 100, y: 255 },
    leftFoot: { x: 96, y: 330 },
    rightHip: { x: 136, y: 180 },
    rightKnee: { x: 138, y: 255 },
    rightFoot: { x: 138, y: 330 },
  },
  worried: {
    head: { x: 120, y: 56 },
    neck: { x: 120, y: 78 },
    shoulderCenter: { x: 120, y: 88 },
    spine: { x: 120, y: 182 },
    leftShoulder: { x: 92, y: 88 },
    leftElbow: { x: 72, y: 96 },
    leftHand: { x: 96, y: 60 },
    rightShoulder: { x: 148, y: 88 },
    rightElbow: { x: 168, y: 96 },
    rightHand: { x: 144, y: 60 },
    leftHip: { x: 104, y: 182 },
    leftKnee: { x: 96, y: 255 },
    leftFoot: { x: 92, y: 330 },
    rightHip: { x: 136, y: 182 },
    rightKnee: { x: 132, y: 255 },
    rightFoot: { x: 126, y: 330 },
  },
  celebrate: {
    head: { x: 120, y: 46 },
    neck: { x: 120, y: 70 },
    shoulderCenter: { x: 120, y: 84 },
    spine: { x: 120, y: 178 },
    leftShoulder: { x: 94, y: 90 },
    leftElbow: { x: 66, y: 48 },
    leftHand: { x: 48, y: 14 },
    rightShoulder: { x: 146, y: 90 },
    rightElbow: { x: 174, y: 48 },
    rightHand: { x: 192, y: 14 },
    leftHip: { x: 104, y: 178 },
    leftKnee: { x: 84, y: 252 },
    leftFoot: { x: 70, y: 330 },
    rightHip: { x: 136, y: 178 },
    rightKnee: { x: 156, y: 252 },
    rightFoot: { x: 166, y: 330 },
  },
};

function interpolatePoint(p1: Point, p2: Point, t: number): Point {
  return {
    x: p1.x + (p2.x - p1.x) * t,
    y: p1.y + (p2.y - p1.y) * t,
  };
}

function interpolatePose(p1: PoseJoints, p2: PoseJoints, t: number): PoseJoints {
  const clampT = Math.max(0, Math.min(1, t));
  return {
    head: interpolatePoint(p1.head, p2.head, clampT),
    neck: interpolatePoint(p1.neck, p2.neck, clampT),
    shoulderCenter: interpolatePoint(p1.shoulderCenter, p2.shoulderCenter, clampT),
    spine: interpolatePoint(p1.spine, p2.spine, clampT),
    leftShoulder: interpolatePoint(p1.leftShoulder, p2.leftShoulder, clampT),
    leftElbow: interpolatePoint(p1.leftElbow, p2.leftElbow, clampT),
    leftHand: interpolatePoint(p1.leftHand, p2.leftHand, clampT),
    rightShoulder: interpolatePoint(p1.rightShoulder, p2.rightShoulder, clampT),
    rightElbow: interpolatePoint(p1.rightElbow, p2.rightElbow, clampT),
    rightHand: interpolatePoint(p1.rightHand, p2.rightHand, clampT),
    leftHip: interpolatePoint(p1.leftHip, p2.leftHip, clampT),
    leftKnee: interpolatePoint(p1.leftKnee, p2.leftKnee, clampT),
    leftFoot: interpolatePoint(p1.leftFoot, p2.leftFoot, clampT),
    rightHip: interpolatePoint(p1.rightHip, p2.rightHip, clampT),
    rightKnee: interpolatePoint(p1.rightKnee, p2.rightKnee, clampT),
    rightFoot: interpolatePoint(p1.rightFoot, p2.rightFoot, clampT),
  };
}

export interface CharacterPrimitiveProps {
  props: CharacterProps;
  currentPose?: CharacterPose;
  prevPose?: CharacterPose;
  poseProgress?: number;
  currentEmotion?: CharacterEmotion;
  currentFacing?: CharacterFacing;
  visualState?: VisualStateKind;
  customAccent?: string;
  style?: React.CSSProperties;
}

export const Character: React.FC<CharacterPrimitiveProps> = ({
  props,
  currentPose,
  prevPose,
  poseProgress = 1,
  currentEmotion,
  currentFacing,
  visualState = "normal",
  customAccent,
  style,
}) => {
  const filterId = useId();

  const activePose = currentPose || props.pose || "idle";
  const priorPose = prevPose || activePose;
  const emotion = currentEmotion || props.emotion || "neutral";
  const facing = currentFacing || props.facing || "right";

  // Resolve active joints through interpolation
  const targetJoints = POSES[activePose] || POSES.idle;
  const sourceJoints = POSES[priorPose] || targetJoints;
  const joints = poseProgress >= 1 ? targetJoints : interpolatePose(sourceJoints, targetJoints, poseProgress);

  // Dynamic accent color based on visualState / customAccent
  let accentColor = customAccent || props.accentColor || "#38BDF8";
  if (visualState === "warning") {
    accentColor = "#F59E0B";
  } else if (visualState === "danger") {
    accentColor = "#EF4444";
  } else if (visualState === "success") {
    accentColor = "#10B981";
  }

  // Visor color based on emotion
  let visorColor = accentColor;
  if (emotion === "concerned") {
    visorColor = "#F59E0B";
  } else if (emotion === "focused") {
    visorColor = "#60A5FA";
  } else if (emotion === "happy") {
    visorColor = "#34D399";
  } else if (emotion === "surprised") {
    visorColor = "#38BDF8";
  }

  const chestY = (joints.shoulderCenter.y + joints.spine.y) * 0.45;
  const chestX = (joints.shoulderCenter.x + joints.spine.x) * 0.5;

  return (
    <div
      style={{
        position: "relative",
        width: 240,
        height: 360,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "flex-start",
        pointerEvents: "none",
        userSelect: "none",
        ...style,
      }}
    >
      <svg
        viewBox="0 0 240 360"
        width="100%"
        height="100%"
        style={{ overflow: "visible" }}
      >
        <defs>
          <filter id={`neon-glow-${filterId}`} x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur in="SourceGraphic" stdDeviation="2.5" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
          <radialGradient id={`holo-floor-${filterId}`} cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor={accentColor} stopOpacity="0.35" />
            <stop offset="60%" stopColor={accentColor} stopOpacity="0.1" />
            <stop offset="100%" stopColor={accentColor} stopOpacity="0" />
          </radialGradient>
        </defs>

        {/* Subtle holographic floor ring at base */}
        <ellipse
          cx="120"
          cy="338"
          rx="52"
          ry="10"
          fill={`url(#holo-floor-${filterId})`}
        />

        {/* Stick figure group with horizontal facing reflection */}
        <g
          transform={facing === "left" ? "translate(240, 0) scale(-1, 1)" : undefined}
          filter={`url(#neon-glow-${filterId})`}
        >
          {/* Spine / Torso */}
          <line
            x1={joints.shoulderCenter.x}
            y1={joints.shoulderCenter.y}
            x2={joints.spine.x}
            y2={joints.spine.y}
            stroke={accentColor}
            strokeWidth="3.5"
            strokeLinecap="round"
          />

          {/* Neck */}
          <line
            x1={joints.head.x}
            y1={joints.head.y + 16}
            x2={joints.shoulderCenter.x}
            y2={joints.shoulderCenter.y}
            stroke={accentColor}
            strokeWidth="3"
            strokeLinecap="round"
          />

          {/* Shoulders clavicle bar */}
          <line
            x1={joints.leftShoulder.x}
            y1={joints.leftShoulder.y}
            x2={joints.rightShoulder.x}
            y2={joints.rightShoulder.y}
            stroke={accentColor}
            strokeWidth="3.5"
            strokeLinecap="round"
          />

          {/* Left Arm: Shoulder -> Elbow -> Hand */}
          <path
            d={`M ${joints.leftShoulder.x} ${joints.leftShoulder.y} L ${joints.leftElbow.x} ${joints.leftElbow.y} L ${joints.leftHand.x} ${joints.leftHand.y}`}
            fill="none"
            stroke={accentColor}
            strokeWidth="3.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />

          {/* Right Arm: Shoulder -> Elbow -> Hand */}
          <path
            d={`M ${joints.rightShoulder.x} ${joints.rightShoulder.y} L ${joints.rightElbow.x} ${joints.rightElbow.y} L ${joints.rightHand.x} ${joints.rightHand.y}`}
            fill="none"
            stroke={accentColor}
            strokeWidth="3.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />

          {/* Pelvis bar */}
          <line
            x1={joints.leftHip.x}
            y1={joints.leftHip.y}
            x2={joints.rightHip.x}
            y2={joints.rightHip.y}
            stroke={accentColor}
            strokeWidth="3.5"
            strokeLinecap="round"
          />

          {/* Left Leg: Hip -> Knee -> Foot */}
          <path
            d={`M ${joints.leftHip.x} ${joints.leftHip.y} L ${joints.leftKnee.x} ${joints.leftKnee.y} L ${joints.leftFoot.x} ${joints.leftFoot.y}`}
            fill="none"
            stroke={accentColor}
            strokeWidth="3.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />

          {/* Right Leg: Hip -> Knee -> Foot */}
          <path
            d={`M ${joints.rightHip.x} ${joints.rightHip.y} L ${joints.rightKnee.x} ${joints.rightKnee.y} L ${joints.rightFoot.x} ${joints.rightFoot.y}`}
            fill="none"
            stroke={accentColor}
            strokeWidth="3.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />

          {/* Joint Nodes */}
          <circle cx={joints.leftElbow.x} cy={joints.leftElbow.y} r="2.8" fill="#F0F9FF" />
          <circle cx={joints.rightElbow.x} cy={joints.rightElbow.y} r="2.8" fill="#F0F9FF" />
          <circle cx={joints.leftKnee.x} cy={joints.leftKnee.y} r="2.8" fill="#F0F9FF" />
          <circle cx={joints.rightKnee.x} cy={joints.rightKnee.y} r="2.8" fill="#F0F9FF" />
          <circle cx={joints.spine.x} cy={joints.spine.y} r="3" fill="#F0F9FF" />

          {/* Futuristic Chest Core Node */}
          <circle cx={chestX} cy={chestY} r="3.2" fill={accentColor} />
          <circle cx={chestX} cy={chestY} r="1.5" fill="#FFFFFF" />

          {/* Head & Futuristic Helmet/Visor */}
          <circle
            cx={joints.head.x}
            cy={joints.head.y}
            r="19"
            fill="#090D16"
            stroke={accentColor}
            strokeWidth="2.8"
          />

          {/* Glowing Visor Slit */}
          {emotion === "happy" ? (
            <path
              d={`M ${joints.head.x - 11} ${joints.head.y - 1} Q ${joints.head.x} ${joints.head.y + 4} ${joints.head.x + 11} ${joints.head.y - 1}`}
              fill="none"
              stroke={visorColor}
              strokeWidth="2.8"
              strokeLinecap="round"
            />
          ) : emotion === "concerned" ? (
            <path
              d={`M ${joints.head.x - 11} ${joints.head.y + 2} L ${joints.head.x + 11} ${joints.head.y - 2}`}
              fill="none"
              stroke={visorColor}
              strokeWidth="2.8"
              strokeLinecap="round"
            />
          ) : emotion === "surprised" ? (
            <circle
              cx={joints.head.x}
              cy={joints.head.y}
              r="4.5"
              fill="none"
              stroke={visorColor}
              strokeWidth="2.5"
            />
          ) : (
            <line
              x1={joints.head.x - 11}
              y1={joints.head.y}
              x2={joints.head.x + 11}
              y2={joints.head.y}
              stroke={visorColor}
              strokeWidth="2.8"
              strokeLinecap="round"
            />
          )}

          {/* Visor Core Highlight */}
          <circle
            cx={joints.head.x}
            cy={joints.head.y}
            r="1.4"
            fill="#FFFFFF"
          />
        </g>
      </svg>

      {/* Role / Label Tag (Unflipped, readable) */}
      {(props.label || props.role) && (
        <div
          style={{
            position: "absolute",
            bottom: 6,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <div
            style={{
              padding: "3px 10px",
              borderRadius: 8,
              background: "rgba(9, 13, 22, 0.85)",
              border: `1px solid ${accentColor}55`,
              boxShadow: `0 2px 8px rgba(0,0,0,0.6)`,
              fontSize: 11,
              fontWeight: 600,
              fontFamily: "monospace",
              color: "#E2E8F0",
              letterSpacing: "0.08em",
              textTransform: "uppercase",
              whiteSpace: "nowrap",
            }}
          >
            {props.label || props.role}
          </div>
        </div>
      )}
    </div>
  );
};
