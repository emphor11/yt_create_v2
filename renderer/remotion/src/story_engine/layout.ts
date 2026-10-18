import type { StoryObject, GridZone, ZoneName, PrimitiveType } from "./types.ts";

export interface ResolvedGeometry {
  x: number;
  y: number;
  width: number;
  height: number;
}

export const VALID_ZONES: readonly ZoneName[] = [
  "top_left",
  "top_center",
  "top_right",
  "center_left",
  "center",
  "center_right",
  "bottom_left",
  "bottom_center",
  "bottom_right",
  "full_screen",
  "full_top",
  "full_bottom",
] as const;

/**
 * Exact center coordinates for each of the 9 localized canvas zones on a 1920x1080 canvas.
 * Spaced with an 80px safe boundary margin.
 */
export const ZONE_COORDINATES: Record<GridZone, { x: number; y: number }> = {
  top_left: { x: 380, y: 260 },
  top_center: { x: 960, y: 260 },
  top_right: { x: 1540, y: 260 },

  center_left: { x: 380, y: 540 },
  center: { x: 960, y: 540 },
  center_right: { x: 1540, y: 540 },

  bottom_left: { x: 380, y: 800 },
  bottom_center: { x: 960, y: 780 },
  bottom_right: { x: 1540, y: 800 },
};

export interface BoundingBoxCollision {
  idA: string;
  idB: string;
  boxA: ResolvedGeometry;
  boxB: ResolvedGeometry;
  overlapWidth: number;
  overlapHeight: number;
}

/**
 * Checks for 2D Axis-Aligned Bounding Box (AABB) collisions between resolved geometries.
 * Returns all overlapping pairs of surface elements.
 */
export function checkRectangleCollisions(
  layouts: Map<string, ResolvedGeometry>,
  ignoredIds?: Set<string>
): BoundingBoxCollision[] {
  const collisions: BoundingBoxCollision[] = [];
  const entries = Array.from(layouts.entries()).filter(([id]) => !ignoredIds?.has(id));

  for (let i = 0; i < entries.length; i++) {
    for (let j = i + 1; j < entries.length; j++) {
      const [idA, boxA] = entries[i];
      const [idB, boxB] = entries[j];

      const xOverlap = Math.max(0, Math.min(boxA.x + boxA.width, boxB.x + boxB.width) - Math.max(boxA.x, boxB.x));
      const yOverlap = Math.max(0, Math.min(boxA.y + boxA.height, boxB.y + boxB.height) - Math.max(boxA.y, boxB.y));

      if (xOverlap > 0 && yOverlap > 0) {
        collisions.push({
          idA,
          idB,
          boxA,
          boxB,
          overlapWidth: xOverlap,
          overlapHeight: yOverlap,
        });
      }
    }
  }

  return collisions;
}

export function getDefaultDimensionsForType(type: PrimitiveType): { width: number; height: number } {
  switch (type) {
    case "chart":
      return { width: 560, height: 320 };
    case "document":
      return { width: 480, height: 320 };
    case "image":
      return { width: 640, height: 360 };
    case "number":
      return { width: 340, height: 160 };
    case "text":
      return { width: 400, height: 90 };
    case "card":
    default:
      return { width: 420, height: 240 };
  }
}

/**
 * Deterministic 12-Zone Spatial Layout Engine.
 *
 * Converts the 12 strict spatial zone names into pixel-perfect screen coordinates (x, y)
 * without relative graph dependencies, circular references, or AI guesswork.
 */
export function resolveLayouts(
  objects: StoryObject[],
  canvasWidth: number = 1920,
  canvasHeight: number = 1080,
  safeMargin: number = 80
): Map<string, ResolvedGeometry> {
  const resolved = new Map<string, ResolvedGeometry>();

  for (const obj of objects) {
    if (obj.type === "connector") {
      continue;
    }

    const layout = obj.layout ?? "center";

    // Strictly enforce valid 12 layout zones — never silently default
    if (!VALID_ZONES.includes(layout)) {
      throw new Error(
        `INVALID_LAYOUT_ZONE: Object "${obj.id}" specifies invalid layout zone "${layout}". Must be one of: ${VALID_ZONES.join(", ")}`
      );
    }

    const defaults = getDefaultDimensionsForType(obj.type);
    let width = obj.width ?? (obj.cardProps?.width ?? defaults.width);
    let height = obj.height ?? (obj.cardProps?.height ?? defaults.height);

    let x = (canvasWidth - width) / 2;
    let y = (canvasHeight - height) / 2;

    // 1. 9-Zone Grid direct center lookup
    if (layout in ZONE_COORDINATES) {
      const center = ZONE_COORDINATES[layout as GridZone];
      x = Math.round(center.x - width / 2);
      y = Math.round(center.y - height / 2);
    }
    // 2. Macro Layouts
    else if (layout === "full_screen") {
      if (obj.type === "image") {
        x = 0;
        y = 0;
        width = canvasWidth;
        height = canvasHeight;
      } else {
        x = safeMargin;
        y = safeMargin;
        width = canvasWidth - safeMargin * 2;
        height = canvasHeight - safeMargin * 2;
      }
    } else if (layout === "full_top") {
      x = safeMargin;
      y = safeMargin;
      width = canvasWidth - safeMargin * 2;
      height = obj.height ?? 360;
    } else if (layout === "full_bottom") {
      width = canvasWidth - safeMargin * 2;
      height = obj.height ?? 360;
      x = safeMargin;
      y = canvasHeight - safeMargin - height - 40; // Preserves subtitle line
    }

    // Safety boundary clamping so elements do not bleed past safe margins
    if (layout !== "full_screen" && layout !== "full_top" && layout !== "full_bottom") {
      const minX = safeMargin + 40;
      const maxX = canvasWidth - width - safeMargin - 40;
      if (maxX >= minX) {
        x = Math.max(minX, Math.min(x, maxX));
      }
      const minY = safeMargin + 40;
      const maxY = canvasHeight - height - safeMargin - 40;
      if (maxY >= minY) {
        y = Math.max(minY, Math.min(y, maxY));
      }
    }

    resolved.set(obj.id, { x, y, width, height });
  }

  return resolved;
}

/**
 * Resolves spatial destination coordinates for a Move action.
 * Strictly requires a valid ZoneName — arbitrary dx/dy pixel offsets are forbidden.
 */
export function resolveSemanticDestination(
  to: ZoneName,
  currentGeom: ResolvedGeometry,
  canvasWidth: number = 1920,
  canvasHeight: number = 1080,
  safeMargin: number = 80
): { targetX: number; targetY: number } {
  if (!VALID_ZONES.includes(to)) {
    throw new Error(
      `INVALID_LAYOUT_ZONE: Move target "${to}" is not a valid spatial layout zone. Must be one of: ${VALID_ZONES.join(", ")}`
    );
  }

  let destX = currentGeom.x;
  let destY = currentGeom.y;

  if (to in ZONE_COORDINATES) {
    const center = ZONE_COORDINATES[to as GridZone];
    destX = Math.round(center.x - currentGeom.width / 2);
    destY = Math.round(center.y - currentGeom.height / 2);
  } else if (to === "full_screen") {
    destX = safeMargin;
    destY = safeMargin;
  } else if (to === "full_top") {
    destX = safeMargin;
    destY = safeMargin;
  } else if (to === "full_bottom") {
    destX = safeMargin;
    destY = canvasHeight - safeMargin - currentGeom.height - 40;
  }

  // Safety boundary clamping
  const minX = safeMargin + 40;
  const maxX = canvasWidth - currentGeom.width - safeMargin - 40;
  if (maxX >= minX) {
    destX = Math.max(minX, Math.min(destX, maxX));
  }
  const minY = safeMargin + 40;
  const maxY = canvasHeight - currentGeom.height - safeMargin - 40;
  if (maxY >= minY) {
    destY = Math.max(minY, Math.min(destY, maxY));
  }

  return { targetX: destX, targetY: destY };
}
