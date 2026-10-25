import React, { useMemo } from "react";
import { useCurrentFrame, Audio, staticFile } from "remotion";
import type { StoryPlan, StoryObject } from "./types.ts";
import { resolveLayouts } from "./layout.ts";
import { evaluateFrame } from "./engine.ts";
import {
  Card,
  NumberPrimitive,
  TextPrimitive,
  Connector,
  Highlight,
  DocumentPrimitive,
  ChartPrimitive,
  ImagePrimitive,
  StockVideoPrimitive,
  Character,
} from "./primitives/index.ts";
import { tokens } from "../design-tokens.ts";
import { handDrawn } from "./hand-drawn-theme.ts";
import { SoundEffectsLayer } from "./audio/SoundEffectsLayer.tsx";

interface StorySceneProps {
  plan: StoryPlan;
}

export const StoryScene: React.FC<StorySceneProps> = ({ plan }) => {
  const frame = useCurrentFrame();

  // 1. Resolve base semantic layout once
  const baseLayouts = useMemo(() => {
    return resolveLayouts(plan.objects, plan.width, plan.height, plan.safeMargin ?? 80);
  }, [plan]);

  // 2. Evaluate full continuous world state at current frame
  const evaluated = useMemo(() => {
    return evaluateFrame(plan, baseLayouts, frame);
  }, [plan, baseLayouts, frame]);


  const connectors = plan.objects.filter((o) => o.type === "connector");
  const surfaces = plan.objects.filter((o) => o.type !== "connector");

  const { camera, backdropDim, connectorIntensityMultiplier } = evaluated;

  return (
    <div
      style={{
        position: "relative",
        width: plan.width,
        height: plan.height,
        backgroundColor: handDrawn.colors.paper,
        overflow: "hidden",
      }}
    >
      {/* Real Audible Narration Track */}
      {plan.audioFileName && (
        <Audio src={staticFile(plan.audioFileName)} />
      )}

      {/* Tactile Audio SFX Engine Layer */}
      <SoundEffectsLayer plan={plan} />

      {/* 1. Base Tactile Paper Canvas */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: `radial-gradient(ellipse at 50% 25%, ${handDrawn.colors.paperAlt} 0%, ${handDrawn.colors.paper} 70%, ${handDrawn.colors.paperDeep} 100%)`,
          opacity: 1 - backdropDim * 0.4,
        }}
      />

      {/* 2. Architectural / Accounting Ledger Grid (Subtle tactile desk texture) */}
      <svg
        style={{
          position: "absolute",
          inset: 0,
          width: "100%",
          height: "100%",
          pointerEvents: "none",
          opacity: 0.045,
        }}
      >
        <defs>
          <pattern
            id="accounting-grid"
            width="48"
            height="48"
            patternUnits="userSpaceOnUse"
          >
            <path
              d="M 48 0 L 0 0 0 48"
              fill="none"
              stroke="#202522"
              strokeWidth="0.75"
            />
            <circle cx="0" cy="0" r="1.2" fill="#202522" />
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#accounting-grid)" />
      </svg>

      {/* 3. Studio Overhead Lighting & Optical Vignette (Draws eye to active elements) */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: `
            radial-gradient(ellipse at 50% 28%, rgba(255, 253, 247, 0.65) 0%, rgba(247, 241, 229, 0) 62%),
            radial-gradient(ellipse at 50% 50%, transparent 48%, rgba(32, 37, 34, 0.05) 75%, rgba(32, 37, 34, 0.16) 100%)
          `,
          pointerEvents: "none",
          opacity: 1 - backdropDim * 0.5,
        }}
      />

      {/* 4. Documentary Registration Inset & Corner Crosshairs */}
      <div
        style={{
          position: "absolute",
          inset: 32,
          border: "1px solid rgba(32, 37, 34, 0.045)",
          pointerEvents: "none",
        }}
      >
        <span style={{ position: "absolute", top: -8, left: -8, fontSize: 13, color: "rgba(32, 37, 34, 0.2)", fontFamily: "monospace", userSelect: "none" }}>+</span>
        <span style={{ position: "absolute", top: -8, right: -8, fontSize: 13, color: "rgba(32, 37, 34, 0.2)", fontFamily: "monospace", userSelect: "none" }}>+</span>
        <span style={{ position: "absolute", bottom: -8, left: -8, fontSize: 13, color: "rgba(32, 37, 34, 0.2)", fontFamily: "monospace", userSelect: "none" }}>+</span>
        <span style={{ position: "absolute", bottom: -8, right: -8, fontSize: 13, color: "rgba(32, 37, 34, 0.2)", fontFamily: "monospace", userSelect: "none" }}>+</span>
      </div>

      {/* Camera Viewport Wrapper (Handles Focus, Push-in, Pull-out, Pan) */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          transform: `scale(${camera.zoom}) translate(${camera.panX}px, ${camera.panY}px)`,
          transformOrigin: "center center",
          willChange: "transform",
        }}
      >
        {/* Render Connectors */}
        {connectors.map((conn) => {
          if (!conn.connectorProps) return null;
          const fromState = evaluated.objects.get(conn.connectorProps.fromId);
          const toState = evaluated.objects.get(conn.connectorProps.toId);
          const connState = evaluated.objects.get(conn.id);

          if (!fromState || !toState || !connState) return null;
          if (!fromState.isEntered || !toState.isEntered || !connState.isEntered) return null;
          const connectorOpacity = Math.min(fromState.opacity, toState.opacity, connState.opacity);
          if (connectorOpacity <= 0) return null;

          // Smart edge attachment: connect closest edges (horizontal or vertical)
          let fromPoint = {
            x: fromState.x + fromState.width / 2,
            y: fromState.y + fromState.height / 2,
          };
          let toPoint = {
            x: toState.x + toState.width / 2,
            y: toState.y + toState.height / 2,
          };

          const dx = (toState.x + toState.width / 2) - (fromState.x + fromState.width / 2);
          const dy = (toState.y + toState.height / 2) - (fromState.y + fromState.height / 2);

          if (Math.abs(dx) >= Math.abs(dy)) {
            // Primarily horizontal relationship
            if (dx > 0) {
              fromPoint = { x: fromState.x + fromState.width, y: fromState.y + fromState.height / 2 };
              toPoint = { x: toState.x, y: toState.y + toState.height / 2 };
            } else {
              fromPoint = { x: fromState.x, y: fromState.y + fromState.height / 2 };
              toPoint = { x: toState.x + toState.width, y: toState.y + toState.height / 2 };
            }
          } else {
            // Primarily vertical relationship
            if (dy > 0) {
              fromPoint = { x: fromState.x + fromState.width / 2, y: fromState.y + fromState.height };
              toPoint = { x: toState.x + toState.width / 2, y: toState.y };
            } else {
              fromPoint = { x: fromState.x + fromState.width / 2, y: fromState.y };
              toPoint = { x: toState.x + toState.width / 2, y: toState.y + toState.height };
            }
          }

          return (
            <div key={conn.id} style={{ opacity: connectorOpacity }}>
              <Connector
                props={conn.connectorProps}
                fromPoint={fromPoint}
                toPoint={toPoint}
                progress={connState.connectorProgress}
                intensityMultiplier={connectorIntensityMultiplier}
              />
            </div>
          );
        })}

        {/* Render Surface Objects (Cards, Documents, Charts, Images) */}
        {surfaces.map((obj) => {
          const state = evaluated.objects.get(obj.id);
          if (!state || state.opacity <= 0) return null;

          const dominanceGlow = state.isDominant
            ? `0 0 45px 8px ${
                obj.cardProps?.accentColor ||
                obj.documentProps?.accentColor ||
                obj.chartProps?.accentColor ||
                tokens.accent.primary
              }88`
            : undefined;

          // 1. Render Document Primitive
          if (obj.type === "document" && obj.documentProps) {
            return (
              <div
                key={obj.id}
                style={{
                  position: "absolute",
                  left: state.x,
                  top: state.y,
                  width: state.width,
                  height: state.height,
                  opacity: state.opacity,
                  transform: `translateY(${state.translateY}px) scale(${state.scale})`,
                  zIndex: state.zIndex,
                }}
              >
                <Highlight
                  intensity={state.highlightIntensity}
                  progress={state.highlightProgress}
                  color={state.highlightColor || state.customAccent || obj.documentProps.accentColor || "#FACC15"}
                  strokePosition="bottom"
                  style={{
                    width: "100%",
                    height: "100%",
                    boxShadow: dominanceGlow,
                    borderRadius: 12,
                  }}
                >
                  <DocumentPrimitive
                    props={obj.documentProps}
                    visualState={state.visualState}
                    badge={state.visualBadge}
                    stamp={state.visualStamp}
                    customAccent={state.customAccent}
                    style={{ width: "100%", height: "100%" }}
                  />
                </Highlight>
              </div>
            );
          }

          // 2. Render Chart Primitive
          if (obj.type === "chart" && obj.chartProps) {
            return (
              <div
                key={obj.id}
                style={{
                  position: "absolute",
                  left: state.x,
                  top: state.y,
                  width: state.width,
                  height: state.height,
                  opacity: state.opacity,
                  transform: `translateY(${state.translateY}px) scale(${state.scale})`,
                  zIndex: state.zIndex,
                }}
              >
                <Highlight
                  intensity={state.highlightIntensity}
                  progress={state.highlightProgress}
                  color={state.highlightColor || state.customAccent || obj.chartProps.accentColor || "#FACC15"}
                  style={{
                    width: "100%",
                    height: "100%",
                    boxShadow: dominanceGlow,
                    borderRadius: tokens.radius.card,
                  }}
                >
                  <ChartPrimitive
                    props={obj.chartProps}
                    progress={state.chartProgress}
                    activePointIndex={state.chartActivePointIndex}
                    width={state.width}
                    height={state.height}
                    layout={obj.layout}
                    style={{ width: "100%", height: "100%" }}
                  />
                </Highlight>
              </div>
            );
          }

          // 3. Render Image Primitive
          if (obj.type === "image" && obj.imageProps) {
            return (
              <div
                key={obj.id}
                style={{
                  position: "absolute",
                  left: state.x,
                  top: state.y,
                  width: state.width,
                  height: state.height,
                  opacity: state.opacity,
                  transform: `translateY(${state.translateY}px) scale(${state.scale})`,
                  zIndex: state.zIndex,
                }}
              >
                <Highlight
                  intensity={state.highlightIntensity}
                  progress={state.highlightProgress}
                  color={state.highlightColor || state.customAccent || obj.imageProps.borderColor || "#FACC15"}
                  style={{
                    width: "100%",
                    height: "100%",
                    boxShadow: dominanceGlow,
                    borderRadius: obj.imageProps.borderRadius ?? 16,
                  }}
                >
                  <ImagePrimitive
                    props={obj.imageProps}
                    style={{ width: "100%", height: "100%" }}
                  />
                </Highlight>
              </div>
            );
          }

          // 3b. Render Stock Video Primitive
          if (obj.type === "stock_video" && obj.stockVideoProps) {
            return (
              <div
                key={obj.id}
                style={{
                  position: "absolute",
                  left: state.x,
                  top: state.y,
                  width: state.width,
                  height: state.height,
                  opacity: state.opacity,
                  transform: `translateY(${state.translateY}px) scale(${state.scale})`,
                  zIndex: state.zIndex,
                }}
              >
                <StockVideoPrimitive
                  props={obj.stockVideoProps}
                  style={{ width: "100%", height: "100%" }}
                />
              </div>
            );
          }

          // 4. Render Card Primitive
          if (obj.type === "card" && obj.cardProps) {
            return (
              <div
                key={obj.id}
                style={{
                  position: "absolute",
                  left: state.x,
                  top: state.y,
                  width: state.width,
                  height: state.height,
                  opacity: state.opacity,
                  transform: `translateY(${state.translateY}px) scale(${state.scale})`,
                  zIndex: state.zIndex,
                }}
              >
                <Highlight
                  intensity={state.highlightIntensity}
                  progress={state.highlightProgress}
                  color={state.highlightColor || state.customAccent || obj.cardProps.accentColor || "#FACC15"}
                  strokePosition="bottom"
                  style={{
                    width: "100%",
                    height: "100%",
                    boxShadow: dominanceGlow,
                    borderRadius: tokens.radius.card,
                  }}
                >
                  <Card
                    props={obj.cardProps}
                    visualState={state.visualState}
                    badge={state.visualBadge}
                    stamp={state.visualStamp}
                    customAccent={state.customAccent}
                    currentDisplayValue={state.currentDisplayValue}
                    currentValue={state.currentNumberValue}
                    currentSubtitle={state.currentSubtitleValue}
                    style={{
                      width: "100%",
                      height: "100%",
                    }}
                  />
                </Highlight>
              </div>
            );
          }

          // 5. Render Standalone Number Primitive
          if (obj.type === "number" && obj.numberProps) {
            return (
              <div
                key={obj.id}
                style={{
                  position: "absolute",
                  left: state.x,
                  top: state.y,
                  width: state.width,
                  height: state.height,
                  opacity: state.opacity,
                  transform: `translateY(${state.translateY}px) scale(${state.scale})`,
                  zIndex: state.zIndex,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                }}
              >
                <Highlight
                  intensity={state.highlightIntensity}
                  progress={state.highlightProgress}
                  color={state.highlightColor || state.customAccent || "#FACC15"}
                  strokePosition="middle"
                  style={{ borderRadius: 12 }}
                >
                  <NumberPrimitive
                    props={obj.numberProps}
                    currentDisplayValue={state.currentDisplayValue}
                    currentValue={state.currentNumberValue}
                  />
                </Highlight>
              </div>
            );
          }

          // 6. Render Standalone Text Primitive
          if (obj.type === "text" && obj.textProps) {
            return (
              <div
                key={obj.id}
                style={{
                  position: "absolute",
                  left: state.x,
                  top: state.y,
                  width: state.width,
                  height: state.height,
                  opacity: state.opacity,
                  transform: `translateY(${state.translateY}px) scale(${state.scale})`,
                  zIndex: state.zIndex,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                }}
              >
                <Highlight
                  intensity={state.highlightIntensity}
                  progress={state.highlightProgress}
                  color={state.highlightColor || state.customAccent || "#FACC15"}
                  strokePosition="middle"
                  style={{ borderRadius: 8 }}
                >
                  <TextPrimitive
                    props={{
                      ...obj.textProps,
                      text: state.currentTextValue || obj.textProps.text,
                      color: state.currentTextColor || obj.textProps.color,
                    }}
                  />
                </Highlight>
              </div>
            );
          }

          // 7. Render Character Primitive
          if (obj.type === "character" && obj.characterProps) {
            return (
              <div
                key={obj.id}
                style={{
                  position: "absolute",
                  left: state.x,
                  top: state.y,
                  width: state.width,
                  height: state.height,
                  opacity: state.opacity,
                  transform: `translateY(${state.translateY}px) scale(${state.scale})`,
                  zIndex: state.zIndex,
                }}
              >
                <Highlight
                  intensity={state.highlightIntensity}
                  progress={state.highlightProgress}
                  color={state.highlightColor || state.customAccent || obj.characterProps.accentColor || "#FACC15"}
                  style={{
                    width: "100%",
                    height: "100%",
                    boxShadow: dominanceGlow,
                    borderRadius: 16,
                  }}
                >
                  <Character
                    props={obj.characterProps}
                    currentPose={state.characterPose || obj.characterProps.pose}
                    prevPose={state.characterPrevPose}
                    poseProgress={state.characterPoseProgress ?? 1}
                    currentEmotion={state.characterEmotion || obj.characterProps.emotion}
                    currentFacing={state.characterFacing || obj.characterProps.facing}
                    visualState={state.visualState}
                    customAccent={state.customAccent}
                    style={{ width: "100%", height: "100%" }}
                  />
                </Highlight>
              </div>
            );
          }

          return null;
        })}
      </div>

      {/* Cinematic Dramatic Dimming Veil */}
      {backdropDim > 0 && (
        <div
          style={{
            position: "absolute",
            inset: 0,
            backgroundColor: "#000000",
            opacity: backdropDim * 0.55,
            pointerEvents: "none",
            zIndex: 15,
          }}
        />
      )}
    </div>
  );
};
