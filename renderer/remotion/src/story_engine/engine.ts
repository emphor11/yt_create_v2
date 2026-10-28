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
  CharacterPose,
  CharacterEmotion,
  CharacterFacing,
  ChangePoseAction,
  StampAction,
  StampTone,
} from "./types.ts";
import { resolveSemanticDestination, resolveContextualTopology } from "./layout.ts";
import type { ResolvedGeometry } from "./layout.ts";

export interface TopologySegment {
  startFrame: number;
  activeIds: Set<string>;
  layouts: Map<string, ResolvedGeometry>;
}

export const REFLOW_TRANSITION_FRAMES = 16;

const planSegmentsCache = new WeakMap<StoryPlan, TopologySegment[]>();

export function computeDynamicTopologyTimeline(
  plan: StoryPlan,
  baseLayouts: Map<string, ResolvedGeometry>
): TopologySegment[] {
  const surfaces = plan.objects.filter((o) => o.type !== "connector");
  if (surfaces.length === 0) {
    return [{ startFrame: 0, activeIds: new Set(), layouts: new Map(baseLayouts) }];
  }

  const enterFrames = new Map<string, number>();
  const exitFrames = new Map<string, number>();

  for (const surf of surfaces) {
    const enterEv = plan.events.find(
      (e): e is EnterAction => e.action === "enter" && "targetId" in e && e.targetId === surf.id
    );
    const splitEv = plan.events.find(
      (e): e is SplitAction => e.action === "split" && e.targetIds?.includes(surf.id)
    );

    let enterF = 0;
    if (enterEv) {
      enterF = enterEv.startFrame;
    } else if (splitEv) {
      const idx = splitEv.targetIds.indexOf(surf.id);
      const stagger = splitEv.staggerFrames ?? 12;
      enterF = splitEv.startFrame + idx * stagger;
    }
    enterFrames.set(surf.id, enterF);

    const exitEv = plan.events.find(
      (e): e is ExitAction => e.action === "exit" && "targetId" in e && e.targetId === surf.id
    );
    const exitF = exitEv ? exitEv.startFrame + (exitEv.durationFrames ?? 15) : (plan.durationInFrames ?? 999999);
    exitFrames.set(surf.id, exitF);
  }

  const boundarySet = new Set<number>([0]);
  for (const [, f] of enterFrames.entries()) {
    boundarySet.add(f);
  }
  for (const [, f] of exitFrames.entries()) {
    boundarySet.add(f);
  }

  const sortedBoundaries = Array.from(boundarySet).sort((a, b) => a - b);
  const segments: TopologySegment[] = [];

  for (const bFrame of sortedBoundaries) {
    const activeSurfaces = surfaces.filter((surf) => {
      const start = enterFrames.get(surf.id) ?? 0;
      const end = exitFrames.get(surf.id) ?? (plan.durationInFrames ?? 999999);
      return bFrame >= start && bFrame < end;
    });

    const activeIds = new Set(activeSurfaces.map((s) => s.id));

    if (activeSurfaces.length === 0) {
      segments.push({ startFrame: bFrame, activeIds, layouts: new Map(baseLayouts) });
    } else {
      const segmentMap = resolveContextualTopology(
        activeSurfaces,
        plan.width,
        plan.height,
        plan.safeMargin ?? 80
      );
      for (const [id, geom] of baseLayouts.entries()) {
        if (!segmentMap.has(id)) {
          segmentMap.set(id, geom);
        }
      }
      segments.push({ startFrame: bFrame, activeIds, layouts: segmentMap });
    }
  }

  return segments;
}

export function resolveDynamicGeometry(
  objId: string,
  frame: number,
  segments: TopologySegment[],
  baseGeom: ResolvedGeometry
): ResolvedGeometry {
  if (segments.length === 0) return baseGeom;

  let curIndex = 0;
  for (let i = 0; i < segments.length; i++) {
    if (frame >= segments[i].startFrame) {
      curIndex = i;
    } else {
      break;
    }
  }

  const curSegment = segments[curIndex];
  const targetGeom = curSegment.layouts.get(objId) || baseGeom;

  if (curIndex === 0) {
    return targetGeom;
  }

  const windowProgress = (frame - curSegment.startFrame) / REFLOW_TRANSITION_FRAMES;
  if (windowProgress >= 1) {
    return targetGeom;
  }

  const prevSegment = segments[curIndex - 1];
  // If this object was not active in the previous segment, it newly entered; do not tween from inactive position
  if (!prevSegment.activeIds.has(objId)) {
    return targetGeom;
  }

  const prevGeom = prevSegment.layouts.get(objId) || baseGeom;

  const p = interpolate(
    frame,
    [curSegment.startFrame, curSegment.startFrame + REFLOW_TRANSITION_FRAMES],
    [0, 1],
    {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
      easing: Easing.inOut(Easing.cubic),
    }
  );

  return {
    x: Math.round(prevGeom.x + (targetGeom.x - prevGeom.x) * p),
    y: Math.round(prevGeom.y + (targetGeom.y - prevGeom.y) * p),
    width: Math.round(prevGeom.width + (targetGeom.width - prevGeom.width) * p),
    height: Math.round(prevGeom.height + (targetGeom.height - prevGeom.height) * p),
  };
}

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
  highlightProgress: number;
  highlightColor?: string;
  connectorProgress: number;
  isDominant: boolean;
  visualState: VisualStateKind;
  visualBadge?: string;
  visualStamp?: StampProps;
  customAccent?: string;
  chartProgress: number;
  chartActivePointIndex?: number;
  characterPose?: CharacterPose;
  characterPrevPose?: CharacterPose;
  characterPoseProgress?: number;
  characterEmotion?: CharacterEmotion;
  characterFacing?: CharacterFacing;
}

export interface EvaluatedCameraState {
  zoom: number;
  panX: number;
  panY: number;
}

export interface EvaluatedStampState {
  id: string;
  text: string;
  tone?: StampTone;
  color?: string;
  rotationDeg?: number;
  startFrame: number;
  durationFrames: number;
  targetId?: string;
}

export interface EvaluatedFrameState {
  objects: Map<string, EvaluatedObjectState>;
  camera: EvaluatedCameraState;
  backdropDim: number;
  connectorIntensityMultiplier: number;
  activeStamps: EvaluatedStampState[];
}

/**
 * Speech anchors are resolved strictly during compilation.
 * At rendering time, compiled startFrame is used directly and anchors are not resolved again.
 */
function resolvePlanEvents(plan: StoryPlan): StoryAction[] {
  return plan.events;
}

function parseNumericFromDisplay(display?: string): number | undefined {
  if (!display) return undefined;
  const cleaned = display.replace(/,/g, "").trim();
  const crMatch = cleaned.match(/([\d.]+)\s*(?:cr|crore)/i);
  if (crMatch) return parseFloat(crMatch[1]) * 10000000;
  const lakhMatch = cleaned.match(/([\d.]+)\s*(?:lakh|lakhs|l)/i);
  if (lakhMatch) return parseFloat(lakhMatch[1]) * 100000;
  const numMatch = cleaned.match(/[-+]?[\d.]+/);
  if (numMatch) {
    const parsed = parseFloat(numMatch[0]);
    return isNaN(parsed) ? undefined : parsed;
  }
  return undefined;
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
  const stampEvents: StampAction[] = [];

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
    } else if (event.action === "stamp") {
      stampEvents.push(event as StampAction);
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

  const useAutoLayout = plan.autoLayout === true;
  let segments: TopologySegment[] = [];
  if (useAutoLayout) {
    let cached = planSegmentsCache.get(plan);
    if (!cached) {
      cached = computeDynamicTopologyTimeline(plan, baseLayouts);
      planSegmentsCache.set(plan, cached);
    }
    segments = cached;
  }

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

    const targetGeom = useAutoLayout
      ? resolveDynamicGeometry(obj.id, frame, segments, baseGeom)
      : baseGeom;

    const targetEvents = eventsByTarget.get(obj.id) || [];

    // Check if object is born from a true SplitAction
    const splitForObj = splitEvents.find((s) => s.targetIds.includes(obj.id));
    let isSplitTarget = Boolean(splitForObj);

    // 1. Entrance action / Split birth
    let opacity = 0;
    let translateY = 24;
    let baseScale = 0.95;
    let isEntered = false;
    let curX = targetGeom.x;
    let curY = targetGeom.y;

    if (splitForObj) {
      const daughterIdx = splitForObj.targetIds.indexOf(obj.id);
      const stagger = splitForObj.staggerFrames ?? 12;
      const birthFrame = splitForObj.startFrame + daughterIdx * stagger;
      const sourceGeom = baseLayouts.get(splitForObj.sourceId);

      if (sourceGeom) {
        // Emerge physically from inside the source parent's bounding box
        const originX = sourceGeom.x + sourceGeom.width / 2 - targetGeom.width / 2;
        const originY = sourceGeom.y + sourceGeom.height / 2 - targetGeom.height / 2;

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
          curX = originX + (targetGeom.x - originX) * p;
          curY = originY + (targetGeom.y - originY) * p;
          baseScale = 0.25 + 0.75 * p;
          opacity = p;
          isEntered = true;
        } else {
          curX = targetGeom.x;
          curY = targetGeom.y;
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
        } else if (enterEvent.style === "cut" || enterEvent.durationFrames === 0) {
          opacity = 1;
          translateY = 0;
          baseScale = 1;
          isEntered = true;
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
      } else if (obj.type === "connector") {
        const connectEvent = targetEvents.find((e): e is ConnectAction => e.action === "connect");
        if (connectEvent && frame >= connectEvent.startFrame) {
          opacity = 1;
          translateY = 0;
          baseScale = 1;
          isEntered = true;
        } else {
          opacity = 0;
          translateY = 0;
          baseScale = 1;
          isEntered = false;
        }
      } else {
        opacity = 0;
        translateY = 24;
        baseScale = 0.95;
        isEntered = false;
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
      } else {
        opacity = 0;
        isEntered = false;
      }
    }

    // 4. Number transformation action
    let currentNumberValue: number | undefined = obj.cardProps?.value ?? obj.numberProps?.value;
    let currentDisplayValue: string | undefined = obj.cardProps?.displayValue ?? obj.numberProps?.displayValue;
    const transformEvents = targetEvents.filter(
      (e): e is TransformNumberAction => e.action === "transform_number"
    );

    const explicitVal = obj.cardProps?.value ?? obj.numberProps?.value;
    let startVal = explicitVal !== undefined ? explicitVal : (parseNumericFromDisplay(currentDisplayValue) ?? 0);
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

    // 6. Highlight action (Smooth draw-on & persistent marker stroke)
    let highlightIntensity = 0;
    let highlightProgress = 0;
    let highlightColor: string | undefined = undefined;
    const highlightEvents = targetEvents.filter((e): e is HighlightAction => e.action === "highlight");
    for (const h of highlightEvents) {
      if (frame >= h.startFrame) {
        const elapsed = frame - h.startFrame;
        const duration = Math.max(1, h.durationFrames);
        const relProgress = Math.min(1.0, elapsed / duration);
        highlightProgress = relProgress;
        if (elapsed < duration) {
          highlightIntensity = Math.sin((elapsed / duration) * Math.PI);
        } else {
          highlightIntensity = 0.15; // gentle resting presence
        }
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
      if (exit.direction === "cut" || exit.durationFrames === 0) {
        if (frame >= exit.startFrame) {
          opacity = 0;
          isEntered = false;
        }
      } else if (frame >= exit.startFrame + exit.durationFrames) {
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

    // 11. Character evaluation (pose, emotion, facing, transitions)
    let characterPose: CharacterPose | undefined = obj.characterProps?.pose;
    let characterPrevPose: CharacterPose | undefined = obj.characterProps?.pose;
    let characterPoseProgress: number = 1;
    let characterEmotion: CharacterEmotion | undefined = obj.characterProps?.emotion ?? "neutral";
    let characterFacing: CharacterFacing | undefined = obj.characterProps?.facing ?? "right";

    if (obj.type === "character") {
      const poseEvents = targetEvents
        .filter((e): e is ChangePoseAction => e.action === "change_pose")
        .sort((a, b) => a.startFrame - b.startFrame);

      let lastPose = obj.characterProps?.pose ?? "idle";
      let lastEmotion = obj.characterProps?.emotion ?? "neutral";
      let lastFacing = obj.characterProps?.facing ?? "right";

      for (const cp of poseEvents) {
        if (frame < cp.startFrame) {
          // Hasn't started yet
          break;
        } else if (frame < cp.startFrame + cp.durationFrames) {
          // Transition in progress
          const p = interpolate(
            frame,
            [cp.startFrame, cp.startFrame + cp.durationFrames],
            [0, 1],
            {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
              easing: Easing.inOut(Easing.cubic),
            }
          );
          characterPrevPose = lastPose;
          characterPose = cp.pose;
          characterPoseProgress = p;
          if (cp.emotion) characterEmotion = cp.emotion;
          if (cp.facing) characterFacing = cp.facing;
          break;
        } else {
          // Transition completed
          lastPose = cp.pose;
          if (cp.emotion) lastEmotion = cp.emotion;
          if (cp.facing) lastFacing = cp.facing;
          characterPose = lastPose;
          characterPrevPose = lastPose;
          characterPoseProgress = 1;
          characterEmotion = lastEmotion;
          characterFacing = lastFacing;
        }
      }
    }

    const finalScale = (baseScale + extraScale) * (1 + 0.03 * highlightIntensity);

    const state: EvaluatedObjectState = {
      id: obj.id,
      x: curX,
      y: curY,
      width: targetGeom.width,
      height: targetGeom.height,
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
      highlightProgress,
      highlightColor,
      connectorProgress,
      isDominant,
      visualState,
      visualBadge,
      visualStamp,
      customAccent,
      chartProgress,
      chartActivePointIndex,
      characterPose,
      characterPrevPose,
      characterPoseProgress,
      characterEmotion,
      characterFacing,
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

  if (cameraEvents.length > 0) {
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
  } else {
    // ----------------------------------------------------
    // Automatic Cinematic Camera Track (Documentary Auto-Framing)
    // Evaluates focal framing and organic push-in when explicit
    // camera events are absent.
    // ----------------------------------------------------
    const beatFramesSet = new Set<number>([0]);
    for (const ev of plan.events) {
      if (ev.action === "enter" || ev.action === "exit" || ev.action === "highlight") {
        beatFramesSet.add(ev.startFrame);
      }
    }
    const beatFrames = Array.from(beatFramesSet).sort((a, b) => a - b);

    const getTargetAtFrame = (f: number) => {
      const active: Array<{ type: string; layout?: string }> = [];
      for (const obj of plan.objects) {
        if (obj.type === "connector") continue;
        const enterEv = plan.events.find(
          (e) => (e.action === "enter" || e.action === "connect") && e.targetId === obj.id
        );
        const exitEv = plan.events.find((e) => e.action === "exit" && e.targetId === obj.id);
        const start = enterEv ? enterEv.startFrame : 0;
        const end = exitEv ? exitEv.startFrame : plan.durationInFrames;
        if (obj.type !== "stock_video" && f >= start && f < end) {
          active.push({ type: obj.type, layout: obj.layout });
        }
      }

      if (active.length === 0) return { zoom: 1.0, panX: 0, panY: 0 };
      if (active.some((o) => o.layout === "full_screen")) {
        return { zoom: 1.03, panX: 0, panY: 0 };
      }
      const hasLeft = active.some((o) => o.layout === "split_left");
      const hasRight = active.some((o) => o.layout === "split_right");
      const hasCenter = active.some((o) => o.layout === "center");
      const hasBottom = active.some((o) => o.layout === "full_bottom");

      if (hasBottom) {
        return { zoom: 1.05, panX: 0, panY: -35 };
      }
      if (hasLeft && hasRight) {
        return { zoom: 1.05, panX: 0, panY: 0 };
      }
      if (hasCenter) {
        return { zoom: 1.08, panX: 0, panY: -10 };
      }
      if (hasLeft && !hasRight) {
        return { zoom: 1.15, panX: 135, panY: -10 };
      }
      if (hasRight && !hasLeft) {
        return { zoom: 1.15, panX: -135, panY: -10 };
      }
      return { zoom: 1.04, panX: 0, panY: 0 };
    };

    const keyframes = beatFrames.map((bf) => ({ frame: bf, ...getTargetAtFrame(bf + 2) }));

    let prev = keyframes[0];
    for (let i = 0; i < keyframes.length; i++) {
      if (keyframes[i].frame <= frame) {
        prev = keyframes[i];
      } else {
        break;
      }
    }

    const transFrames = 26;
    let curZoom = prev.zoom;
    let curPanX = prev.panX;
    let curPanY = prev.panY;

    const dt = frame - prev.frame;
    if (dt < transFrames) {
      const prevIdx = keyframes.indexOf(prev);
      const beforePrev = prevIdx > 0 ? keyframes[prevIdx - 1] : { zoom: 1.0, panX: 0, panY: 0 };
      const p = Math.min(1, Math.max(0, dt / transFrames));
      const eased = interpolate(p, [0, 1], [0, 1], {
        easing: Easing.inOut(Easing.cubic),
      });
      curZoom = beforePrev.zoom + (prev.zoom - beforePrev.zoom) * eased;
      curPanX = beforePrev.panX + (prev.panX - beforePrev.panX) * eased;
      curPanY = beforePrev.panY + (prev.panY - beforePrev.panY) * eased;
    }

    const isFullScreenActive = plan.objects.some((obj) => {
      if (obj.layout === "full_screen" && obj.type !== "stock_video") {
        const s = result.get(obj.id);
        return s && s.isEntered && s.opacity > 0.1;
      }
      return false;
    });

    const drift = isFullScreenActive ? 0 : 0.015 * Math.sin((frame / 45) * Math.PI);

    camZoom = Math.max(0.95, Math.min(1.25, curZoom + drift));
    camPanX = curPanX;
    camPanY = curPanY;
  }

  // ----------------------------------------------------
  // 12. Transient Impact Camera Shake & Active Stamps
  // ----------------------------------------------------
  let shakeX = 0;
  let shakeY = 0;
  const activeStamps: EvaluatedStampState[] = [];

  for (const stampEv of stampEvents) {
    const startF = stampEv.startFrame;
    const durF = stampEv.durationFrames ?? 180;
    if (frame >= startF && frame <= startF + durF) {
      activeStamps.push({
        id: `stamp_${stampEv.startFrame}_${stampEv.text.slice(0, 10)}`,
        text: stampEv.text,
        tone: stampEv.tone,
        color: stampEv.color,
        rotationDeg: stampEv.rotationDeg,
        startFrame: startF,
        durationFrames: durF,
        targetId: stampEv.targetId,
      });
    }

    if (stampEv.shake !== false) {
      const impactFrame = startF + 6;
      const relShake = frame - impactFrame;
      if (relShake >= 0 && relShake <= 10) {
        const amplitude = 5.0 * Math.exp(-0.45 * relShake);
        shakeX += amplitude * Math.sin(relShake * 2.1);
        shakeY += amplitude * Math.cos(relShake * 2.4);
      }
    }
  }

  // Also check change_visual_state with stamp
  for (const vsEv of visualStateEvents) {
    if (vsEv.stamp || vsEv.state === "stamped") {
      const impactFrame = vsEv.startFrame + 6;
      const relShake = frame - impactFrame;
      if (relShake >= 0 && relShake <= 10) {
        const amplitude = 4.0 * Math.exp(-0.45 * relShake);
        shakeX += amplitude * Math.sin(relShake * 2.1);
        shakeY += amplitude * Math.cos(relShake * 2.4);
      }
    }
  }

  camPanX += shakeX;
  camPanY += shakeY;

  return {
    objects: result,
    camera: { zoom: camZoom, panX: camPanX, panY: camPanY },
    backdropDim,
    connectorIntensityMultiplier,
    activeStamps,
  };
}
