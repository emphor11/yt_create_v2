import type {
  StoryPlan,
  StoryObject,
  StoryAction,
  MoveAction,
  TransformNumberAction,
  ConnectAction,
  CameraAction,
  SplitAction,
  MergeAction,
  ChangeVisualStateAction,
  ExitAction,
  ChangePoseAction,
} from "./types.ts";
import { resolveLayouts, resolveSemanticDestination, VALID_ZONES, checkRectangleCollisions } from "./layout.ts";
import type { ResolvedGeometry } from "./layout.ts";

export interface ValidationError {
  code: string;
  message: string;
  targetId?: string;
  details?: Record<string, any>;
}

export interface ValidationResult {
  valid: boolean;
  errors: ValidationError[];
}

/**
 * Validates factual mathematical derivations (Grounding Provenance).
 */
function verifyFactualDerivation(
  targetId: string,
  value: number,
  provenance: any,
  errors: ValidationError[]
) {
  if (!provenance?.derived_from) return;

  const { formula, inputs } = provenance.derived_from;

  if (formula === "loan_emi") {
    const { principal, rate, tenure_months } = inputs;
    if (principal && rate && tenure_months) {
      const r = rate / (12 * 100);
      const factor = Math.pow(1 + r, tenure_months);
      const expectedEmi = Math.round((principal * r * factor) / (factor - 1));
      if (Math.abs(value - expectedEmi) > 2) {
        errors.push({
          code: "PROVENANCE_CALCULATION_MISMATCH",
          message: `Factual derivation mismatch for '${targetId}': stated ${value}, expected ${expectedEmi} from loan_emi formula.`,
          targetId,
          details: { value, expectedEmi, inputs },
        });
      }
    }
  } else if (formula === "inflation_decay") {
    const { initial, rate, years } = inputs;
    if (initial && rate && years) {
      const expectedReal = Math.round(initial / Math.pow(1 + rate / 100, years));
      if (Math.abs(value - expectedReal) > 2) {
        errors.push({
          code: "PROVENANCE_CALCULATION_MISMATCH",
          message: `Factual derivation mismatch for '${targetId}': stated ${value}, expected ${expectedReal} from inflation_decay formula.`,
          targetId,
          details: { value, expectedReal, inputs },
        });
      }
    }
  } else if (formula === "salary_tax_split") {
    const { gross, tax, living, savings } = inputs;
    if (gross !== undefined && tax !== undefined && living !== undefined && savings !== undefined) {
      if (gross !== tax + living + savings) {
        errors.push({
          code: "PROVENANCE_CALCULATION_MISMATCH",
          message: `Factual derivation mismatch for '${targetId}': gross (${gross}) does not equal sum of deductions (${tax} + ${living} + ${savings} = ${tax + living + savings}).`,
          targetId,
          details: { inputs },
        });
      }
    }
  }
}

/**
 * Validates camera viewport framing to prevent cropping required context objects.
 */
function verifyCameraViewport(
  cam: CameraAction,
  layouts: Map<string, ResolvedGeometry>,
  canvasWidth: number,
  canvasHeight: number,
  safeMargin: number,
  errors: ValidationError[]
) {
  if (!cam.requiredContextIds || cam.requiredContextIds.length === 0) return;

  const zoom = cam.zoom ?? (cam.behavior === "push_in" ? 1.15 : 1.0);
  let panX = cam.pan?.x ?? 0;
  let panY = cam.pan?.y ?? 0;

  if (cam.behavior === "focus" && cam.targetId) {
    const targetGeom = layouts.get(cam.targetId);
    if (targetGeom) {
      const cardCenterX = targetGeom.x + targetGeom.width / 2;
      const cardCenterY = targetGeom.y + targetGeom.height / 2;
      panX = (canvasWidth / 2 - cardCenterX) * 0.45;
      panY = (canvasHeight / 2 - cardCenterY) * 0.45;
    }
  }

  for (const reqId of cam.requiredContextIds) {
    const geom = layouts.get(reqId);
    if (!geom) continue;

    // Transform world coordinates to camera viewport screen coordinates
    const screenX = canvasWidth / 2 + (geom.x - canvasWidth / 2 + panX) * zoom;
    const screenY = canvasHeight / 2 + (geom.y - canvasHeight / 2 + panY) * zoom;
    const screenW = geom.width * zoom;
    const screenH = geom.height * zoom;

    if (
      screenX < safeMargin ||
      screenY < safeMargin ||
      screenX + screenW > canvasWidth - safeMargin ||
      screenY + screenH > canvasHeight - safeMargin
    ) {
      errors.push({
        code: "CAMERA_CONTEXT_CLIPPED",
        message: `Camera behavior '${cam.behavior}' crops required context card '${reqId}'. Screen bounds [${Math.round(screenX)}, ${Math.round(screenY)}, ${Math.round(screenW)}x${Math.round(screenH)}] violate safe margin (${safeMargin}).`,
        targetId: reqId,
        details: { reqId, screenX, screenY, screenW, screenH, safeMargin },
      });
    }
  }
}

/**
 * Enhanced Validation Engine.
 */
export function validateStoryPlan(
  plan: StoryPlan,
  approvedValues?: Set<number>
): ValidationResult {
  const errors: ValidationError[] = [];
  const safeMargin = plan.safeMargin ?? 80;

  const objectMap = new Map<string, StoryObject>();
  function index(obj: StoryObject) {
    if (objectMap.has(obj.id)) {
      errors.push({
        code: "DUPLICATE_OBJECT_ID",
        message: `Duplicate object ID '${obj.id}' found in plan.`,
        targetId: obj.id,
      });
    }
    objectMap.set(obj.id, obj);
  }
  plan.objects.forEach(index);

  // 1. Validate Initial Values & Derivations
  for (const [id, obj] of objectMap.entries()) {
    if (obj.type === "number" && obj.numberProps) {
      if (approvedValues && approvedValues.size > 0) {
        if (!approvedValues.has(obj.numberProps.value)) {
          errors.push({
            code: "UNAPPROVED_INITIAL_VALUE",
            message: `Initial value ${obj.numberProps.value} on '${id}' is not in approved factual values.`,
            targetId: id,
            details: { initialValue: obj.numberProps.value },
          });
        }
      }
      if (obj.numberProps.provenance) {
        verifyFactualDerivation(id, obj.numberProps.value, obj.numberProps.provenance, errors);
      }
    }
    if (obj.type === "card" && obj.cardProps?.value !== undefined) {
      if (approvedValues && approvedValues.size > 0) {
        if (!approvedValues.has(obj.cardProps.value)) {
          errors.push({
            code: "UNAPPROVED_INITIAL_VALUE",
            message: `Initial value ${obj.cardProps.value} on '${id}' is not in approved factual values.`,
            targetId: id,
            details: { initialValue: obj.cardProps.value },
          });
        }
      }
      if (obj.cardProps.provenance) {
        verifyFactualDerivation(id, obj.cardProps.value, obj.cardProps.provenance, errors);
      }
    }
    if (obj.type === "document" && obj.documentProps?.provenance) {
      verifyFactualDerivation(id, obj.documentProps.value ?? 0, obj.documentProps.provenance, errors);
    }
  }

  // 2. Validate Events & Target Compatibility
  for (const event of plan.events) {
    if ("targetId" in event && event.targetId) {
      const target = objectMap.get(event.targetId);
      if (!target) {
        errors.push({
          code: "TARGET_NOT_FOUND",
          message: `Event '${event.action}' references non-existent object ID '${event.targetId}'.`,
          targetId: event.targetId,
        });
        continue;
      }

      if (event.action === "transform_number" && target.type !== "number" && target.type !== "card") {
        errors.push({
          code: "INVALID_TARGET_TYPE",
          message: `Action 'transform_number' can only target a 'number' or 'card' primitive, but '${target.id}' is a '${target.type}'.`,
          targetId: target.id,
        });
      }

      if (event.action === "transform_text" && target.type !== "text" && target.type !== "card") {
        errors.push({
          code: "INVALID_TARGET_TYPE",
          message: `Action 'transform_text' can only target a 'text' or 'card' primitive, but '${target.id}' is a '${target.type}'.`,
          targetId: target.id,
        });
      }

      if (event.action === "move") {
        const moveEv = event as MoveAction;
        if (typeof moveEv.to === "string" && !VALID_ZONES.includes(moveEv.to as any)) {
          errors.push({
            code: "INVALID_MOVE_ZONE",
            message: `Move action for '${target.id}' targets invalid layout '${moveEv.to}'. Must be one of the 12 strict zone names.`,
            targetId: target.id,
          });
        }
      }

      if (event.action === "connect" && target.type !== "connector") {
        errors.push({
          code: "INVALID_TARGET_TYPE",
          message: `Action 'connect' can only target a 'connector' primitive, but '${target.id}' is a '${target.type}'.`,
          targetId: target.id,
        });
      }

      if (event.action === "exit") {
        const exitEv = event as ExitAction;
        if (!exitEv.direction || !["left", "right", "up", "down", "fade"].includes(exitEv.direction)) {
          errors.push({
            code: "INVALID_EXIT_DIRECTION",
            message: `Exit action requires valid direction ('left', 'right', 'up', 'down', 'fade'), got '${exitEv.direction}'.`,
            targetId: target.id,
          });
        }
      }

      if (event.action === "change_pose") {
        if (target.type !== "character") {
          errors.push({
            code: "INVALID_TARGET_TYPE",
            message: `Action 'change_pose' can only target a 'character' primitive, but '${target.id}' is a '${target.type}'.`,
            targetId: target.id,
          });
        }
        const cp = event as ChangePoseAction;
        const validPoses = ["idle", "walk", "point", "think", "worried", "celebrate"];
        if (!validPoses.includes(cp.pose)) {
          errors.push({
            code: "INVALID_POSE",
            message: `Action 'change_pose' specifies invalid pose '${cp.pose}'. Must be one of: ${validPoses.join(", ")}`,
            targetId: target.id,
          });
        }
        const enterEv = plan.events.find((e) => e.action === "enter" && "targetId" in e && e.targetId === target.id);
        if (enterEv && event.startFrame < enterEv.startFrame) {
          errors.push({
            code: "ACTION_BEFORE_ENTER",
            message: `Action 'change_pose' on '${target.id}' at frame ${event.startFrame} occurs before enter at frame ${enterEv.startFrame}.`,
            targetId: target.id,
          });
        }
        const exitEv = plan.events.find((e) => e.action === "exit" && "targetId" in e && e.targetId === target.id);
        if (exitEv && event.startFrame >= exitEv.startFrame) {
          errors.push({
            code: "ACTION_AFTER_EXIT",
            message: `Action 'change_pose' on '${target.id}' at frame ${event.startFrame} occurs after exit at frame ${exitEv.startFrame}.`,
            targetId: target.id,
          });
        }
      }
    }

    if (event.startFrame < 0 || event.durationFrames <= 0) {
      errors.push({
        code: "INVALID_EVENT_TIMING",
        message: `Event '${event.action}' has invalid startFrame (${event.startFrame}) or durationFrames (${event.durationFrames}).`,
        targetId: "targetId" in event ? event.targetId : undefined,
      });
    }

    if (event.startFrame + event.durationFrames > plan.durationInFrames) {
      errors.push({
        code: "EVENT_EXCEEDS_DURATION",
        message: `Event '${event.action}' ends at frame ${event.startFrame + event.durationFrames}, exceeding total plan duration (${plan.durationInFrames}).`,
        targetId: "targetId" in event ? event.targetId : undefined,
      });
    }

    // Transformed Value Grounding & Provenance
    if (event.action === "transform_number") {
      const trans = event as TransformNumberAction;
      if (approvedValues && approvedValues.size > 0 && !approvedValues.has(trans.toValue)) {
        errors.push({
          code: "UNAPPROVED_TRANSFORM_VALUE",
          message: `Transformed value ${trans.toValue} in 'transform_number' on '${trans.targetId}' is not in approved factual values.`,
          targetId: trans.targetId,
          details: { attemptedValue: trans.toValue },
        });
      }
      if (trans.provenance) {
        verifyFactualDerivation(trans.targetId, trans.toValue, trans.provenance, errors);
      }
    }

    // Split Action Validation
    if (event.action === "split") {
      const split = event as SplitAction;
      if (!objectMap.has(split.sourceId)) {
        errors.push({
          code: "SPLIT_MISSING_SOURCE",
          message: `Split action references missing source object '${split.sourceId}'.`,
          targetId: split.sourceId,
        });
      }
      if (!split.targetIds || split.targetIds.length === 0) {
        errors.push({
          code: "SPLIT_NO_TARGETS",
          message: `Split action on '${split.sourceId}' has no target daughter IDs.`,
          targetId: split.sourceId,
        });
      } else {
        for (const tid of split.targetIds) {
          if (!objectMap.has(tid)) {
            errors.push({
              code: "SPLIT_MISSING_TARGET",
              message: `Split action references non-existent target ID '${tid}'.`,
              targetId: tid,
            });
          }
          if (tid === split.sourceId) {
            errors.push({
              code: "SPLIT_SELF_REFERENCE",
              message: `Split action cannot split an object '${tid}' into itself.`,
              targetId: tid,
            });
          }
        }
      }
    }

    // Merge Action Validation
    if (event.action === "merge") {
      const merge = event as MergeAction;
      if (!objectMap.has(merge.targetId)) {
        errors.push({
          code: "MERGE_MISSING_TARGET",
          message: `Merge action references missing target object '${merge.targetId}'.`,
          targetId: merge.targetId,
        });
      }
      if (!merge.sourceIds || merge.sourceIds.length === 0) {
        errors.push({
          code: "MERGE_NO_SOURCES",
          message: `Merge action targeting '${merge.targetId}' has no source IDs.`,
          targetId: merge.targetId,
        });
      } else {
        for (const sid of merge.sourceIds) {
          if (!objectMap.has(sid)) {
            errors.push({
              code: "MERGE_MISSING_SOURCE",
              message: `Merge action references non-existent source ID '${sid}'.`,
              targetId: sid,
            });
          }
          if (sid === merge.targetId) {
            errors.push({
              code: "MERGE_SELF_REFERENCE",
              message: `Merge action cannot merge an object '${sid}' into itself.`,
              targetId: sid,
            });
          }
        }
      }
    }
  }

  // 3. Connectors
  const connectors = plan.objects.filter((o) => o.type === "connector");
  for (const conn of connectors) {
    if (!conn.connectorProps) {
      errors.push({
        code: "CONNECTOR_MISSING_PROPS",
        message: `Connector '${conn.id}' missing connectorProps.`,
        targetId: conn.id,
      });
      continue;
    }
    const { fromId, toId } = conn.connectorProps;
    if (!objectMap.has(fromId)) {
      errors.push({
        code: "CONNECTOR_MISSING_SOURCE",
        message: `Connector '${conn.id}' references missing source object '${fromId}'.`,
        targetId: conn.id,
      });
    }
    if (!objectMap.has(toId)) {
      errors.push({
        code: "CONNECTOR_MISSING_TARGET",
        message: `Connector '${conn.id}' references missing target object '${toId}'.`,
        targetId: conn.id,
      });
    }
    if (fromId === toId) {
      errors.push({
        code: "CONNECTOR_SELF_REFERENCE",
        message: `Connector '${conn.id}' cannot connect an object to itself (${fromId}).`,
        targetId: conn.id,
      });
    }
  }

  // 4. Resolve Layouts and Validate Safe Areas & Overlaps
  let layouts: Map<string, ResolvedGeometry>;
  try {
    layouts = resolveLayouts(plan.objects, plan.width, plan.height, safeMargin);
  } catch (err: any) {
    errors.push({
      code: "INVALID_LAYOUT_ZONE",
      message: err.message,
    });
    return { valid: false, errors };
  }

  const surfaceElements = plan.objects.filter((o) => o.type !== "connector");

  // Safe area checks
  for (const surf of surfaceElements) {
    const geom = layouts.get(surf.id);
    if (!geom) continue;

    if (
      geom.x < safeMargin ||
      geom.y < safeMargin ||
      geom.x + geom.width > plan.width - safeMargin ||
      geom.y + geom.height > plan.height - safeMargin
    ) {
      errors.push({
        code: "OUT_OF_SAFE_BOUNDS",
        message: `Surface element '${surf.id}' at (${geom.x}, ${geom.y}, ${geom.width}x${geom.height}) violates safe margin bounds.`,
        targetId: surf.id,
      });
    }
  }

  // Validate layout zone names (strict 12 zones)
  for (const [id, obj] of objectMap.entries()) {
    if (obj.type !== "connector" && obj.layout && !VALID_ZONES.includes(obj.layout as any)) {
      errors.push({
        code: "INVALID_LAYOUT_ZONE",
        message: `Object '${id}' has invalid layout '${obj.layout}'. Must be one of the 12 strict zone names.`,
        targetId: id,
      });
    }
  }

  // Macro zone collision conflict rules
  const MACRO_ZONE_CONFLICTS: Record<string, Set<string>> = {
    full_screen: new Set([
      "top_left", "top_center", "top_right",
      "center_left", "center", "center_right",
      "bottom_left", "bottom_center", "bottom_right",
      "full_top", "full_bottom", "full_screen",
    ]),
    full_top: new Set(["top_left", "top_center", "top_right", "full_top", "full_screen"]),
    full_bottom: new Set(["bottom_left", "bottom_center", "bottom_right", "full_bottom", "full_screen"]),
  };

  // Build temporal spatial intervals per surface element
  interface SpatialInterval {
    targetId: string;
    startFrame: number;
    endFrame: number;
    zone: string;
    geom: ResolvedGeometry;
  }

  const objectIntervals = new Map<string, SpatialInterval[]>();

  for (const surf of surfaceElements) {
    const baseGeom = layouts.get(surf.id);
    if (!baseGeom) continue;

    const enterEvent = plan.events.find((e) => e.action === "enter" && "targetId" in e && e.targetId === surf.id);
    const splitEvent = plan.events.find((e): e is SplitAction => e.action === "split" && e.targetIds?.includes(surf.id));
    if (!enterEvent && !splitEvent) {
      errors.push({
        code: "MISSING_ENTER_EVENT",
        message: `Surface element '${surf.id}' has no explicit 'enter' event. Every object must have an explicit enter event.`,
        targetId: surf.id,
      });
    }

    const enterFrame = enterEvent ? enterEvent.startFrame : (splitEvent ? splitEvent.startFrame : 0);
    const exitEvent = plan.events.find((e): e is ExitAction => e.action === "exit" && "targetId" in e && e.targetId === surf.id);
    const exitEndFrame = exitEvent ? exitEvent.startFrame + exitEvent.durationFrames : plan.durationInFrames;

    const moves = plan.events
      .filter((e): e is MoveAction => e.action === "move" && e.targetId === surf.id)
      .sort((a, b) => a.startFrame - b.startFrame);

    let curStart = enterFrame;
    let curZone = surf.layout ?? "center";
    let curGeom = { ...baseGeom };
    const intervals: SpatialInterval[] = [];

    for (const m of moves) {
      if (m.startFrame > curStart && m.startFrame < exitEndFrame) {
        intervals.push({
          targetId: surf.id,
          startFrame: curStart,
          endFrame: m.startFrame,
          zone: curZone,
          geom: curGeom,
        });
        const dest = resolveSemanticDestination(m.to, curGeom, plan.width, plan.height, safeMargin);
        curGeom = { ...curGeom, x: dest.targetX, y: dest.targetY };
        curZone = m.to;
        curStart = m.startFrame;
      }
    }

    if (curStart < exitEndFrame) {
      intervals.push({
        targetId: surf.id,
        startFrame: curStart,
        endFrame: exitEndFrame,
        zone: curZone,
        geom: curGeom,
      });
    }

    objectIntervals.set(surf.id, intervals);

    // Subtitle reservation check (full_bottom must respect height budget and non-full_screen elements must not encroach bottom subtitle line)
    for (const int of intervals) {
      if (int.zone === "full_bottom" && int.geom.height > 380) {
        errors.push({
          code: "SUBTITLE_OVERLAP",
          message: `Surface element '${surf.id}' in 'full_bottom' has height ${int.geom.height}px exceeding maximum 380px, encroaching into subtitle space.`,
          targetId: surf.id,
          details: { height: int.geom.height, maxHeight: 380 },
        });
      }
      if (int.zone !== "full_screen" && int.geom.y + int.geom.height > plan.height - safeMargin - 40) {
        errors.push({
          code: "SUBTITLE_OVERLAP",
          message: `Surface element '${surf.id}' bottom edge at y=${int.geom.y + int.geom.height} encroaches on the subtitle display area (must remain at or above ${plan.height - safeMargin - 40}px).`,
          targetId: surf.id,
          details: { bottomY: int.geom.y + int.geom.height, maxAllowedY: plan.height - safeMargin - 40 },
        });
      }
    }
  }

  // Check pairwise intervals across distinct surface elements
  const surfIds = Array.from(objectIntervals.keys());
  for (let i = 0; i < surfIds.length; i++) {
    for (let j = i + 1; j < surfIds.length; j++) {
      const idA = surfIds[i];
      const idB = surfIds[j];
      const intervalsA = objectIntervals.get(idA) || [];
      const intervalsB = objectIntervals.get(idB) || [];

      for (const intA of intervalsA) {
        for (const intB of intervalsB) {
          const overlapStart = Math.max(intA.startFrame, intB.startFrame);
          const overlapEnd = Math.min(intA.endFrame, intB.endFrame);

          if (overlapStart < overlapEnd) {
            // 1. Exact zone occupancy conflict
            if (intA.zone === intB.zone) {
              errors.push({
                code: "ZONE_OCCUPANCY_COLLISION",
                message: `Spatial collision in zone '${intA.zone}': '${idA}' and '${idB}' occupy the same zone simultaneously between frames ${overlapStart} and ${overlapEnd}.`,
                details: { idA, idB, zone: intA.zone, overlapStart, overlapEnd },
              });
            }

            // 2. Macro zone conflicts
            if (MACRO_ZONE_CONFLICTS[intA.zone]?.has(intB.zone)) {
              errors.push({
                code: "MACRO_LAYOUT_COLLISION",
                message: `Macro layout collision: '${idA}' in macro '${intA.zone}' conflicts with '${idB}' in '${intB.zone}' between frames ${overlapStart} and ${overlapEnd}.`,
                details: { idA, idB, macroZone: intA.zone, conflictingZone: intB.zone, overlapStart, overlapEnd },
              });
            } else if (MACRO_ZONE_CONFLICTS[intB.zone]?.has(intA.zone)) {
              errors.push({
                code: "MACRO_LAYOUT_COLLISION",
                message: `Macro layout collision: '${idB}' in macro '${intB.zone}' conflicts with '${idA}' in '${intA.zone}' between frames ${overlapStart} and ${overlapEnd}.`,
                details: { idA, idB, macroZone: intB.zone, conflictingZone: intA.zone, overlapStart, overlapEnd },
              });
            }

            // 3. AABB Geometric Overlap
            const xOverlap = Math.max(0, Math.min(intA.geom.x + intA.geom.width, intB.geom.x + intB.geom.width) - Math.max(intA.geom.x, intB.geom.x));
            const yOverlap = Math.max(0, Math.min(intA.geom.y + intA.geom.height, intB.geom.y + intB.geom.height) - Math.max(intA.geom.y, intB.geom.y));

            if (xOverlap > 0 && yOverlap > 0) {
              errors.push({
                code: "CARD_OVERLAP",
                message: `Surface elements '${idA}' and '${idB}' have overlapping bounding boxes (${Math.round(xOverlap)}x${Math.round(yOverlap)}px) between frames ${overlapStart} and ${overlapEnd}.`,
                details: { idA, idB, xOverlap, yOverlap, overlapStart, overlapEnd },
              });
            }
          }
        }
      }
    }
  }

  // Camera Viewport Framing Check
  for (const event of plan.events) {
    if (event.action === "camera") {
      verifyCameraViewport(
        event as CameraAction,
        layouts,
        plan.width,
        plan.height,
        safeMargin,
        errors
      );
    }
  }

  return {
    valid: errors.length === 0,
    errors,
  };
}
