import { interpolate, Easing } from "remotion";
import type {
  StoryPlan,
  StoryObject,
  StoryAction,
  MoveAction,
  TransformNumberAction,
  TransformTextAction,
  ConnectAction,
  HighlightAction,
  EnterAction,
  CameraAction,
  EmphasizeAction,
  SplitAction,
  MergeAction,
  ChangeVisualStateAction,
  ExitAction,
  VisualStateKind,
  StampProps,
} from "./types.ts";
import { resolveSemanticDestination } from "./layout.ts";
import type { ResolvedGeometry } from "./layout.ts";
import { resolveAnchorFrame } from "./speech_anchors.ts";

export interface EvaluatedObjectState {
  id: string;
  x: number;
  y: number;
  width: number;
  height: number;
  opacity: number;
  translateY: number;
  scale: number;
  zIndex: number;
  isEntered: boolean;
  currentDisplayValue?: string;
  currentNumberValue?: number;
  currentTextValue?: string;
  currentSubtitleValue?: string;
  currentTextColor?: string;
  highlightIntensity: number;
  highlightColor?: string;
  connectorProgress: number;
  isDominant: boolean;
  visualState: VisualStateKind;
  visualBadge?: string;
  visualStamp?: StampProps;
  customAccent?: string;
  chartProgress: number;
  chartActivePointIndex?: number;
}

export interface EvaluatedCameraState {
  zoom: number;
  panX: number;
  panY: number;
}

export interface EvaluatedFrameState {
  objects: Map<string, EvaluatedObjectState>;
  camera: EvaluatedCameraState;
  backdropDim: number;
  connectorIntensityMultiplier: number;
}

/**
 * Pre-processes events to resolve speech anchors if present.
 */
function resolvePlanEvents(plan: StoryPlan): StoryAction[] {
  if (!plan.narration?.wordTimestamps) {
    return plan.events;
  }
  return plan.events.map((e) => {
    if (e.anchor && plan.narration?.wordTimestamps) {
      const anchorStart = resolveAnchorFrame(
        plan.narration.wordTimestamps,
        e.anchor,
        plan.fps
      );
      if (anchorStart > 0) {
        return { ...e, startFrame: anchorStart };
      }
    }
    return e;
  });
}

/**
 * Evaluates the full continuous world state at a specific frame.
 */
export function evaluateFrame(
  plan: StoryPlan,
  baseLayouts: Map<string, ResolvedGeometry>,
  frame: number
): EvaluatedFrameState {
  const result = new Map<string, EvaluatedObjectState>();
  const safeMargin = plan.safeMargin ?? 80;
  const resolvedEvents = resolvePlanEvents(plan);

  const eventsByTarget = new Map<string, StoryAction[]>();
  const cameraEvents: CameraAction[] = [];
  const emphasizeEvents: EmphasizeAction[] = [];
  const splitEvents: SplitAction[] = [];
  const mergeEvents: MergeAction[] = [];
  const visualStateEvents: ChangeVisualStateAction[] = [];

  for (const event of resolvedEvents) {
    if (event.action === "camera") {
      cameraEvents.push(event as CameraAction);
    } else if (event.action === "emphasize") {
      emphasizeEvents.push(event as EmphasizeAction);
      const list = eventsByTarget.get(event.targetId) || [];
      list.push(event);
      eventsByTarget.set(event.targetId, list);
    } else if (event.action === "split") {
      splitEvents.push(event as SplitAction);
    } else if (event.action === "merge") {
      mergeEvents.push(event as MergeAction);
    } else if (event.action === "change_visual_state") {
      visualStateEvents.push(event as ChangeVisualStateAction);
      const list = eventsByTarget.get(event.targetId) || [];
      list.push(event);
      eventsByTarget.set(event.targetId, list);
    } else if ("targetId" in event && event.targetId) {
      const list = eventsByTarget.get(event.targetId) || [];
      list.push(event);
      eventsByTarget.set(event.targetId, list);
    }
  }

  // ----------------------------------------------------
  // Global Scene Atmosphere
  // ----------------------------------------------------
  let backdropDim = 0;
  let connectorIntensityMultiplier = 1;

  for (const emp of emphasizeEvents) {
    if (frame >= emp.startFrame) {
      const p = interpolate(
        frame,
        [emp.startFrame, emp.startFrame + emp.durationFrames],
        [0, 1],
        {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
          easing: Easing.out(Easing.cubic),
        }
      );
      if (emp.darkenBackdrop) {
        backdropDim = Math.max(backdropDim, emp.darkenBackdrop * p);
      }
      if (emp.connectorIntensity) {
        connectorIntensityMultiplier = Math.max(
          connectorIntensityMultiplier,
          1 + (emp.connectorIntensity - 1) * p
        );
      }
    }
  }

  // ----------------------------------------------------
  // Evaluate Each Object
  // ----------------------------------------------------
  function evalObject(obj: StoryObject) {
    const baseGeom = baseLayouts.get(obj.id) || {
      x: 0,
      y: 0,
      width: obj.width || 420,
      height: obj.height || 240,
    };

    const targetEvents = eventsByTarget.get(obj.id) || [];

    // Check if object is born from a true SplitAction
    const splitForObj = splitEvents.find((s) => s.targetIds.includes(obj.id));
    let isSplitTarget = Boolean(splitForObj);

    // 1. Entrance action / Split birth
    let opacity = 1;
    let translateY = 0;
    let baseScale = 1;
    let isEntered = true;
    let curX = baseGeom.x;
    let curY = baseGeom.y;

    if (splitForObj) {
      const daughterIdx = splitForObj.targetIds.indexOf(obj.id);
      const stagger = splitForObj.staggerFrames ?? 12;
      const birthFrame = splitForObj.startFrame + daughterIdx * stagger;
      const sourceGeom = baseLayouts.get(splitForObj.sourceId);

      if (sourceGeom) {
        // Emerge physically from inside the source parent's bounding box
        const originX = sourceGeom.x + sourceGeom.width / 2 - baseGeom.width / 2;
        const originY = sourceGeom.y + sourceGeom.height / 2 - baseGeom.height / 2;

        if (frame < birthFrame) {
          opacity = 0;
          baseScale = 0.25;
          curX = originX;
          curY = originY;
          isEntered = false;
        } else if (frame < birthFrame + splitForObj.durationFrames) {
          const p = interpolate(
            frame,
            [birthFrame, birthFrame + splitForObj.durationFrames],
            [0, 1],
            {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
              easing: Easing.out(Easing.cubic),
            }
          );
          curX = originX + (baseGeom.x - originX) * p;
          curY = originY + (baseGeom.y - originY) * p;
          baseScale = 0.25 + 0.75 * p;
          opacity = p;
          isEntered = true;
        } else {
          curX = baseGeom.x;
          curY = baseGeom.y;
          opacity = 1;
          baseScale = 1;
          isEntered = true;
        }
      }
    } else {
      const enterEvent = targetEvents.find((e): e is EnterAction => e.action === "enter");
      if (enterEvent) {
        if (frame < enterEvent.startFrame) {
          opacity = 0;
          translateY = 24;
          baseScale = 0.95;
          isEntered = false;
        } else if (frame < enterEvent.startFrame + enterEvent.durationFrames) {
          const p = interpolate(
            frame,
            [enterEvent.startFrame, enterEvent.startFrame + enterEvent.durationFrames],
            [0, 1],
            {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
              easing: Easing.out(Easing.cubic),
            }
          );
          opacity = p;
          translateY = (1 - p) * 24;
          baseScale = 0.95 + 0.05 * p;
          isEntered = true;
        } else {
          opacity = 1;
          translateY = 0;
          baseScale = 1;
          isEntered = true;
        }
      }
    }

    // 2. Move actions (Semantic & Offset)
    const moveEvents = targetEvents.filter((e): e is MoveAction => e.action === "move");
    for (const move of moveEvents) {
      const dest = resolveSemanticDestination(
        move.to,
        baseGeom,
        plan.width,
        plan.height,
        safeMargin
      );
      const dx = dest.targetX - baseGeom.x;
      const dy = dest.targetY - baseGeom.y;

      if (frame >= move.startFrame + move.durationFrames) {
        curX += dx;
        curY += dy;
      } else if (frame >= move.startFrame) {
        const p = interpolate(
          frame,
          [move.startFrame, move.startFrame + move.durationFrames],
          [0, 1],
          {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: Easing.inOut(Easing.cubic),
          }
        );
        curX += dx * p;
        curY += dy * p;
      }
    }

    // 3. Merge actions (Converge into target destination)
    const mergeAsSource = mergeEvents.find((m) => m.sourceIds.includes(obj.id));
    if (mergeAsSource && frame >= mergeAsSource.startFrame) {
      const targetGeom = baseLayouts.get(mergeAsSource.targetId);
      if (targetGeom) {
        const destX = targetGeom.x + targetGeom.width / 2 - baseGeom.width / 2;
        const destY = targetGeom.y + targetGeom.height / 2 - baseGeom.height / 2;

        if (frame < mergeAsSource.startFrame + mergeAsSource.durationFrames) {
          const p = interpolate(
            frame,
            [mergeAsSource.startFrame, mergeAsSource.startFrame + mergeAsSource.durationFrames],
            [0, 1],
            {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
              easing: Easing.in(Easing.cubic),
            }
          );
          curX = curX + (destX - curX) * p;
          curY = curY + (destY - curY) * p;
          baseScale = 1.0 - 0.75 * p;
          opacity = 1.0 - p;
        } else {
          opacity = 0;
          isEntered = false;
        }
      }
    }

    // 4. Number transformation action
    let currentNumberValue: number | undefined = obj.cardProps?.value ?? obj.numberProps?.value;
    let currentDisplayValue: string | undefined = obj.cardProps?.displayValue ?? obj.numberProps?.displayValue;
    const transformEvents = targetEvents.filter(
      (e): e is TransformNumberAction => e.action === "transform_number"
    );

    let startVal = obj.cardProps?.value ?? obj.numberProps?.value ?? 0;
    for (const trans of transformEvents) {
      if (frame >= trans.startFrame + trans.durationFrames) {
        currentNumberValue = trans.toValue;
        if (trans.toDisplayValue) {
          currentDisplayValue = trans.toDisplayValue;
        }
        startVal = trans.toValue;
      } else if (frame >= trans.startFrame) {
        const p = interpolate(
          frame,
          [trans.startFrame, trans.startFrame + trans.durationFrames],
          [0, 1],
          {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: Easing.out(Easing.quad),
          }
        );
        currentNumberValue = startVal + (trans.toValue - startVal) * p;
        break;
      }
    }

    // 5. Text transformation action
    let currentTextValue: string | undefined = obj.textProps?.text;
    let currentSubtitleValue: string | undefined = obj.cardProps?.subtitle;
    let currentTextColor: string | undefined = obj.textProps?.color;
    const textEvents = targetEvents.filter(
      (e): e is TransformTextAction => e.action === "transform_text"
    );
    for (const txt of textEvents) {
      if (frame >= txt.startFrame) {
        currentTextValue = txt.toText;
        currentSubtitleValue = txt.toText;
        if (txt.toColor) {
          currentTextColor = txt.toColor;
        }
      }
    }

    // 6. Highlight action (Smooth bell-curve pulse)
    let highlightIntensity = 0;
    let highlightColor: string | undefined = undefined;
    const highlightEvents = targetEvents.filter((e): e is HighlightAction => e.action === "highlight");
    for (const h of highlightEvents) {
      if (frame >= h.startFrame && frame < h.startFrame + h.durationFrames) {
        const relProgress = (frame - h.startFrame) / h.durationFrames;
        highlightIntensity = Math.sin(relProgress * Math.PI);
        highlightColor = h.color;
      }
    }

    // If source of a split, pulse highlight during split division
    const splitsAsSource = splitEvents.filter((s) => s.sourceId === obj.id);
    for (const s of splitsAsSource) {
      const totalSplitDuration =
        s.durationFrames + (s.targetIds.length - 1) * (s.staggerFrames ?? 12);
      if (frame >= s.startFrame && frame < s.startFrame + totalSplitDuration) {
        const relProgress = (frame - s.startFrame) / totalSplitDuration;
        highlightIntensity = Math.max(highlightIntensity, Math.sin(relProgress * Math.PI) * 0.85);
      }
    }

    // 7. Emphasize & Merge Consolidation action
    let extraScale = 0;
    let zIndex = 10;
    let isDominant = false;
    const objEmphasize = targetEvents.filter((e): e is EmphasizeAction => e.action === "emphasize");
    for (const emp of objEmphasize) {
      if (frame >= emp.startFrame) {
        const p = interpolate(
          frame,
          [emp.startFrame, emp.startFrame + emp.durationFrames],
          [0, 1],
          {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: Easing.out(Easing.cubic),
          }
        );
        if (emp.grow) {
          extraScale = (emp.grow - 1.0) * p;
        }
        if (emp.dominant) {
          isDominant = true;
        }
        zIndex = 25;
      }
    }

    // If target of a merge, pop scale on consolidation impact
    const mergeAsTarget = mergeEvents.find((m) => m.targetId === obj.id);
    if (mergeAsTarget) {
      const impactFrame = mergeAsTarget.startFrame + mergeAsTarget.durationFrames;
      if (frame >= impactFrame && frame < impactFrame + 25) {
        const relProgress = (frame - impactFrame) / 25;
        extraScale += Math.sin(relProgress * Math.PI) * 0.15;
        highlightIntensity = Math.max(highlightIntensity, Math.sin(relProgress * Math.PI) * 0.9);
      }
    }

    // 8. Visual State Transformations (warning, danger, success, dimmed, stamped, eroded)
    let visualState: VisualStateKind = "normal";
    let visualBadge: string | undefined = undefined;
    let visualStamp: StampProps | undefined = undefined;
    let customAccent: string | undefined = undefined;

    const vsEvents = visualStateEvents.filter((vs) => vs.targetId === obj.id);
    for (const vs of vsEvents) {
      if (frame >= vs.startFrame) {
        visualState = vs.state;
        if (vs.badge) visualBadge = vs.badge;
        if (vs.stamp) visualStamp = vs.stamp;
        if (vs.customAccent) customAccent = vs.customAccent;

        if (vs.state === "dimmed") {
          opacity *= 0.35;
          baseScale *= 0.96;
        }
      }
    }

    // 9. Exit actions (Directional slide out & fade)
    const exitEvents = targetEvents.filter((e): e is ExitAction => e.action === "exit");
    for (const exit of exitEvents) {
      if (frame >= exit.startFrame + exit.durationFrames) {
        opacity = 0;
        isEntered = false;
        if (exit.direction === "left") curX -= 400;
        else if (exit.direction === "right") curX += 400;
        else if (exit.direction === "up") curY -= 300;
        else if (exit.direction === "down") curY += 300;
      } else if (frame >= exit.startFrame) {
        const p = interpolate(
          frame,
          [exit.startFrame, exit.startFrame + exit.durationFrames],
          [0, 1],
          {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: Easing.in(Easing.cubic),
          }
        );
        opacity *= 1 - p;
        if (exit.direction === "left") curX -= p * 400;
        else if (exit.direction === "right") curX += p * 400;
        else if (exit.direction === "up") curY -= p * 300;
        else if (exit.direction === "down") curY += p * 300;
      }
    }

    // 10. Connector progress action
    let connectorProgress = 0;
    const connectEvents = targetEvents.filter((e): e is ConnectAction => e.action === "connect");
    for (const c of connectEvents) {
      if (frame >= c.startFrame + c.durationFrames) {
        connectorProgress = 1;
      } else if (frame >= c.startFrame) {
        connectorProgress = interpolate(
          frame,
          [c.startFrame, c.startFrame + c.durationFrames],
          [0, 1],
          {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: Easing.out(Easing.cubic),
          }
        );
      }
    }

    // 10. Chart progress & active point
    let chartProgress = 1;
    let chartActivePointIndex: number | undefined = obj.chartProps?.highlightPointIndex;
    if (obj.type === "chart") {
      const enterEv = targetEvents.find((e): e is EnterAction => e.action === "enter");
      if (enterEv) {
        if (frame < enterEv.startFrame) {
          chartProgress = 0;
        } else if (frame < enterEv.startFrame + enterEv.durationFrames) {
          chartProgress = (frame - enterEv.startFrame) / enterEv.durationFrames;
        } else {
          chartProgress = 1;
        }
      }
    }

    const finalScale = (baseScale + extraScale) * (1 + 0.03 * highlightIntensity);

    const state: EvaluatedObjectState = {
      id: obj.id,
      x: curX,
      y: curY,
      width: baseGeom.width,
      height: baseGeom.height,
      opacity,
      translateY,
      scale: finalScale,
      zIndex,
      isEntered,
      currentDisplayValue,
      currentNumberValue,
      currentTextValue,
      currentSubtitleValue,
      currentTextColor,
      highlightIntensity,
      highlightColor,
      connectorProgress,
      isDominant,
      visualState,
      visualBadge,
      visualStamp,
      customAccent,
      chartProgress,
      chartActivePointIndex,
    };

    result.set(obj.id, state);
  }

  for (const obj of plan.objects) {
    evalObject(obj);
  }

  // ----------------------------------------------------
  // 11. Camera Evaluation
  // ----------------------------------------------------
  let camZoom = 1.0;
  let camPanX = 0;
  let camPanY = 0;

  for (const cam of cameraEvents) {
    if (frame >= cam.startFrame) {
      const p = interpolate(
        frame,
        [cam.startFrame, cam.startFrame + cam.durationFrames],
        [0, 1],
        {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
          easing: Easing.inOut(Easing.cubic),
        }
      );

      if (cam.behavior === "push_in") {
        const targetZoom = cam.zoom ?? 1.15;
        camZoom = 1.0 + (targetZoom - 1.0) * p;
      } else if (cam.behavior === "pull_out") {
        const targetZoom = cam.zoom ?? 0.95;
        camZoom = 1.0 + (targetZoom - 1.0) * p;
      } else if (cam.behavior === "pan") {
        const targetX = cam.pan?.x ?? 0;
        const targetY = cam.pan?.y ?? 0;
        camPanX += targetX * p;
        camPanY += targetY * p;
      } else if (cam.behavior === "focus" && cam.targetId) {
        const targetState = result.get(cam.targetId);
        if (targetState) {
          const targetZoom = cam.zoom ?? 1.18;
          camZoom = 1.0 + (targetZoom - 1.0) * p;

          const cardCenterX = targetState.x + targetState.width / 2;
          const cardCenterY = targetState.y + targetState.height / 2;
          const sceneCenterX = plan.width / 2;
          const sceneCenterY = plan.height / 2;

          const panOffsetX = (sceneCenterX - cardCenterX) * 0.45;
          const panOffsetY = (sceneCenterY - cardCenterY) * 0.45;

          camPanX += panOffsetX * p;
          camPanY += panOffsetY * p;
        }
      }
    }
  }

  return {
    objects: result,
    camera: { zoom: camZoom, panX: camPanX, panY: camPanY },
    backdropDim,
    connectorIntensityMultiplier,
  };
}
