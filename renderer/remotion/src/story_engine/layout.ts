import type { StoryObject, GridZone, ZoneName, PrimitiveType } from "./types.ts";

export interface ResolvedGeometry {
  x: number;
  y: number;
  width: number;
  height: number;
}

export const VALID_ZONES: readonly ZoneName[] = [
  "center",
  "split_left",
  "split_right",
  "full_screen",
  "full_bottom",
] as const;

/**
 * Exact center coordinates for localized canvas zones on a 1920x1080 canvas.
 */
export const ZONE_COORDINATES: Record<GridZone, { x: number; y: number }> = {
  center: { x: 960, y: 540 },
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
      return { width: 580, height: 360 };
    case "scale":
      return { width: 640, height: 360 };
    case "money_stack":
      return { width: 640, height: 360 };
    case "waterfall":
      return { width: 640, height: 360 };
    case "capital_flow":
      return { width: 680, height: 320 };
    case "image":
      return { width: 580, height: 435 };
    case "number":
      return { width: 340, height: 160 };
    case "text":
      return { width: 800, height: 160 };
    case "character":
      return { width: 240, height: 360 };
    case "stock_video":
      return { width: 1920, height: 1080 };
    case "card":
    default:
      return { width: 420, height: 240 };
  }
}

/**
 * Deterministic 5-Layout Spatial Engine.
 *
 * Converts the 5 strict spatial layout zones into pixel-perfect screen coordinates (x, y)
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

    // Strictly enforce valid 5 layout zones — never silently default
    if (!VALID_ZONES.includes(layout)) {
      throw new Error(
        `INVALID_LAYOUT_ZONE: Object "${obj.id}" specifies invalid layout zone "${layout}". Must be one of: ${VALID_ZONES.join(", ")}`
      );
    }

    if (obj.type === "stock_video" && layout !== "full_screen") {
      throw new Error(
        `STOCK_VIDEO_INVALID_LAYOUT: stock_video "${obj.id}" layout must be "full_screen", got "${layout}".`
      );
    }

    const defaults = getDefaultDimensionsForType(obj.type);
    let width = obj.width ?? (obj.cardProps?.width ?? defaults.width);
    let height = obj.height ?? (obj.cardProps?.height ?? defaults.height);

    // Ensure localized images stay under the zone's safe dimensions
    if (obj.type === "image" && layout !== "full_screen") {
      const maxW = (layout === "split_left" || layout === "split_right") ? 740 : 1080;
      const maxH = (layout === "split_left" || layout === "split_right") ? 440 : 640;
      width = Math.min(width, maxW);
      height = Math.min(height, maxH);
    }

    let x = (canvasWidth - width) / 2;
    let y = (canvasHeight - height) / 2;

    // 1. Center direct center lookup
    if (layout in ZONE_COORDINATES) {
      const center = ZONE_COORDINATES[layout as GridZone];
      x = Math.round(center.x - width / 2);
      y = Math.round(center.y - height / 2);
    }
    // 2. Macro Layouts
    else if (layout === "full_screen") {
      if (obj.type === "image" || obj.type === "stock_video") {
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
    } else if (layout === "full_bottom") {
      width = canvasWidth - safeMargin * 2;
      height = obj.height ?? 260;
      x = safeMargin;
      y = canvasHeight - safeMargin - height - 40; // Preserves subtitle line
    } else if (layout === "split_left") {
      // 3. Split-screen: Left half (divider at x = 960, center approximately x = 480, y = 540)
      x = Math.round(480 - width / 2);
      y = Math.round(540 - height / 2);
    } else if (layout === "split_right") {
      // 3. Split-screen: Right half (divider at x = 960, center approximately x = 1440, y = 540)
      x = Math.round(1440 - width / 2);
      y = Math.round(540 - height / 2);
    }

    // Safety boundary clamping so elements do not bleed past safe margins
    if (layout !== "full_screen" && layout !== "full_bottom") {
      let minX = safeMargin + 40;
      let maxX = canvasWidth - width - safeMargin - 40;
      if (layout === "split_left") {
        maxX = Math.min(maxX, 960 - width);
      } else if (layout === "split_right") {
        minX = Math.max(minX, 960);
      }
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

export function isDocumentImage(obj: StoryObject): boolean {
  if (obj.type !== "image") return false;
  const text = `${obj.imageProps?.caption || ""} ${obj.imageProps?.alt || ""} ${obj.imageProps?.badge || ""} ${obj.imageProps?.assetId || ""} ${obj.imageProps?.src || ""} ${obj.id || ""}`.toLowerCase();
  return (
    text.includes("document") ||
    text.includes("doc") ||
    text.includes("contract") ||
    text.includes("statement") ||
    text.includes("paperwork") ||
    text.includes("paper") ||
    text.includes("agreement") ||
    text.includes("letter") ||
    text.includes("report") ||
    text.includes("form") ||
    text.includes("policy") ||
    text.includes("circular") ||
    text.includes("deed") ||
    text.includes("receipt") ||
    text.includes("invoice") ||
    text.includes("certificate")
  );
}

export function resolveSurfacePreferredSize(
  obj: StoryObject,
  context: "solo" | "split" | "three_column" | "three_column_center" | "flank",
  availHeight: number
): { width: number; height: number } {
  if (obj.type === "image") {
    const isDoc = isDocumentImage(obj);
    const defaultW = isDoc ? 460 : 580;
    const defaultH = isDoc ? 610 : 435;
    if (context === "solo") {
      const width = isDoc ? 600 : 1040;
      const height = Math.min(isDoc ? 800 : 585, Math.max(80, availHeight - 20));
      return { width, height };
    } else if (context === "three_column") {
      const targetW = isDoc ? 460 : 540;
      const targetH = isDoc ? 580 : 405;
      const height = Math.min(targetH, Math.max(80, availHeight - 16));
      const width = Math.min(targetW, Math.round(height * (targetW / targetH)));
      return { width, height };
    } else {
      // split or flank: height adapts to available vertical slice while preserving aspect ratio
      const height = Math.min(defaultH, Math.max(80, availHeight - 16));
      const width = Math.min(defaultW, Math.round(height * (defaultW / defaultH)));
      return { width, height };
    }
  }

  if (obj.type === "card") {
    if (context === "solo") {
      return { width: 840, height: Math.min(420, Math.max(90, availHeight - 20)) };
    } else if (context === "split") {
      return { width: 640, height: Math.min(320, Math.max(90, availHeight - 16)) };
    } else if (context === "three_column_center") {
      return { width: 580, height: Math.min(360, Math.max(90, availHeight - 16)) };
    } else if (context === "three_column") {
      return { width: 540, height: Math.min(320, Math.max(90, availHeight - 16)) };
    } else {
      return { width: 680, height: Math.min(340, Math.max(90, availHeight - 16)) };
    }
  }

  if (obj.type === "number") {
    if (context === "solo") {
      return { width: 720, height: Math.min(240, Math.max(80, availHeight - 20)) };
    } else {
      return { width: 500, height: Math.min(220, Math.max(80, availHeight - 16)) };
    }
  }

  if (obj.type === "chart") {
    if (context === "solo") {
      return { width: 1360, height: Math.min(540, Math.max(120, availHeight - 20)) };
    } else {
      return { width: 680, height: Math.min(360, Math.max(120, availHeight - 16)) };
    }
  }

  if (obj.type === "text") {
    return { width: Math.min(obj.width ?? 1080, 1080), height: Math.min(180, Math.max(60, availHeight - 16)) };
  }

  if (obj.type === "character") {
    return { width: 280, height: Math.min(420, Math.max(100, availHeight - 16)) };
  }

  if (obj.type === "scale") {
    if (context === "solo") {
      return { width: 880, height: Math.min(460, Math.max(120, availHeight - 20)) };
    } else {
      return { width: 640, height: Math.min(360, Math.max(110, availHeight - 16)) };
    }
  }

  if (obj.type === "money_stack") {
    if (context === "solo") {
      return { width: 880, height: Math.min(460, Math.max(120, availHeight - 20)) };
    } else {
      return { width: 640, height: Math.min(360, Math.max(110, availHeight - 16)) };
    }
  }

  return {
    width: obj.width ?? 640,
    height: Math.min(obj.height ?? 360, Math.max(80, availHeight - 16)),
  };
}

/**
 * Dynamic Context-Aware Topology Solver.
 * 
 * Computes exact, responsive coordinates (x, y, width, height) based on the
 * active set of surfaces on screen at any given moment.
 * 
 * Topologies supported:
 * 1. Solitary Hero (1 surface) -> Maximizes focal scale (Center card: 840x420, Center image: 1040x585, etc.)
 *    Auto-centers solitary elements even if designated split_left/split_right, eliminating the lone-element void.
 * 2. 3-Column Symphony (split_left + center + split_right) -> Partitions safe width into 3 columns (540, 580, 540)
 * 3. Dual Inward Split (split_left + split_right) -> Elements breathe inward towards center (~140px central gap)
 *    Preserves native photographic geometry (Vertical A4 documents 460x610, 4:3 photos 580x435, horizontal cards 640x320)
 * 4. Center + Single Flank -> Balanced 2-column distribution
 * 
 * Vertical Ceiling Modifier:
 * If a 'full_bottom' element is active, the upper vertical region compresses from 860px to 570px (y: 100 to 670),
 * gracefully shifting upper elements upward and adapting their heights.
 */
/**
 * Lays out one or more surface elements vertically within a designated column.
 * - Single element: centered vertically at standard preferred size.
 * - Two elements: neatly stacked vertically (top and bottom) with a clean 20-24px gap.
 * - Three elements: compactly stacked vertically with 16px gaps.
 * Guarantees zero bounding box overlap between items in the column.
 */
function layoutColumnSurfaces(
  items: StoryObject[],
  colLeftX: number,
  colWidth: number,
  availTopY: number,
  availHeight: number,
  context: "solo" | "split" | "three_column" | "three_column_center" | "flank",
  resolved: Map<string, ResolvedGeometry>
): void {
  if (items.length === 0) return;

  if (items.length === 1) {
    const obj = items[0];
    const { width: w, height: h } = resolveSurfacePreferredSize(obj, context, availHeight);
    const clampedW = Math.min(w, colWidth);
    const clampedH = Math.min(h, availHeight);
    const x = Math.max(colLeftX, Math.round(colLeftX + (colWidth - clampedW) / 2));
    const y = Math.round(availTopY + (availHeight - clampedH) / 2);
    resolved.set(obj.id, { x, y, width: clampedW, height: clampedH });
    return;
  }

  // 2 or more elements in the same column: vertical distribution stack
  // Supports up to 4 elements gracefully by scaling gaps and maxItemHeight
  const count = items.length;
  const gap = count === 2 ? 24 : count === 3 ? 16 : 12;
  const totalGaps = gap * (count - 1);
  const maxItemHeight = Math.max(80, Math.floor((availHeight - totalGaps - 16) / count));

  const measurements = items.map((obj) => {
    const pref = resolveSurfacePreferredSize(obj, context, maxItemHeight);
    const clampedH = Math.min(pref.height, maxItemHeight);
    const clampedW = Math.min(pref.width, colWidth);
    return { obj, width: clampedW, height: clampedH };
  });

  const totalHeight = measurements.reduce((acc, m) => acc + m.height, 0) + totalGaps;
  let curY = availTopY + Math.max(0, Math.round((availHeight - totalHeight) / 2));

  for (const m of measurements) {
    const x = Math.round(colLeftX + (colWidth - m.width) / 2);
    resolved.set(m.obj.id, { x, y: curY, width: m.width, height: m.height });
    curY += m.height + gap;
  }
}

export function resolveContextualTopology(
  activeObjects: StoryObject[],
  canvasWidth: number = 1920,
  canvasHeight: number = 1080,
  safeMargin: number = 80
): Map<string, ResolvedGeometry> {
  const resolved = new Map<string, ResolvedGeometry>();
  const surfaces = activeObjects.filter((o) => o.type !== "connector");

  if (surfaces.length === 0) {
    return resolved;
  }

  // 1. Check for full_screen (e.g. stock_video or backdrop image)
  for (const obj of surfaces) {
    if (obj.layout === "full_screen" || obj.type === "stock_video") {
      resolved.set(obj.id, { x: 0, y: 0, width: canvasWidth, height: canvasHeight });
    }
  }

  // 2. Check for full_bottom (e.g. baseline evidence chart or ticker)
  const bottomObj = surfaces.find((o) => o.layout === "full_bottom");
  let availTopY = safeMargin + 20;
  let availBottomY = canvasHeight - safeMargin - 40;

  if (bottomObj) {
    const bottomH = Math.min(bottomObj.height ?? 280, 280);
    const bottomW = canvasWidth - safeMargin * 2;
    const bottomY = canvasHeight - safeMargin - bottomH - 30; // Preserves subtitle clearance
    resolved.set(bottomObj.id, { x: safeMargin, y: bottomY, width: bottomW, height: bottomH });

    availBottomY = bottomY - 30; // 30px breathing buffer above bottom chart
  }

  const availHeight = availBottomY - availTopY;
  const availCenterY = Math.round((availTopY + availBottomY) / 2);

  // Filter upper surfaces (excluding full_screen and full_bottom)
  const upperSurfaces = surfaces.filter(
    (o) => o.layout !== "full_bottom" && o.layout !== "full_screen" && o.type !== "stock_video"
  );

  if (upperSurfaces.length === 0) {
    return resolved;
  }

  const centerSurfaces = upperSurfaces.filter((o) => (o.layout ?? "center") === "center");
  const leftSurfaces = upperSurfaces.filter((o) => o.layout === "split_left");
  const rightSurfaces = upperSurfaces.filter((o) => o.layout === "split_right");

  const safeLeftX = safeMargin; // 80px

  // TOPOLOGY A: Solitary Surface (Only 1 upper element active)
  // Even if declared as split_left or split_right, a lone element auto-centers at hero scale,
  // preventing the awkward 70% empty canvas void.
  if (upperSurfaces.length === 1) {
    const obj = upperSurfaces[0];
    const { width: w, height: h } = resolveSurfacePreferredSize(obj, "solo", availHeight);
    const x = Math.round((canvasWidth - w) / 2);
    const y = Math.round(availCenterY - h / 2);
    resolved.set(obj.id, { x, y, width: w, height: h });
    return resolved;
  }

  // TOPOLOGY B: 3-Column Symphony (Center + Split-Left + Split-Right all present)
  if (centerSurfaces.length > 0 && leftSurfaces.length > 0 && rightSurfaces.length > 0) {
    const gutter = 50;
    const colLeftW = 540;
    const colCenterW = 580;
    const colRightW = 540;

    const colLeftX = safeLeftX; // 80px
    const colCenterX = colLeftX + colLeftW + gutter; // 670px
    const colRightX = colCenterX + colCenterW + gutter; // 1300px

    layoutColumnSurfaces(leftSurfaces, colLeftX, colLeftW, availTopY, availHeight, "three_column", resolved);
    layoutColumnSurfaces(centerSurfaces, colCenterX, colCenterW, availTopY, availHeight, "three_column_center", resolved);
    layoutColumnSurfaces(rightSurfaces, colRightX, colRightW, availTopY, availHeight, "three_column", resolved);
    return resolved;
  }

  // TOPOLOGY C: Dual Inward Split (split_left + split_right, no center)
  // Preserves genuine editorial asymmetry (e.g. Portrait Document 460x610 vs Horizontal Card 640x320)
  if (leftSurfaces.length > 0 && rightSurfaces.length > 0 && centerSurfaces.length === 0) {
    const centerGutter = 140;

    if (leftSurfaces.length === 1 && rightSurfaces.length === 1) {
      const leftObj = leftSurfaces[0];
      const rightObj = rightSurfaces[0];
      const { width: leftW, height: leftH } = resolveSurfacePreferredSize(leftObj, "split", availHeight);
      const { width: rightW, height: rightH } = resolveSurfacePreferredSize(rightObj, "split", availHeight);

      const leftX = Math.round((canvasWidth / 2) - (centerGutter / 2) - leftW);
      const leftY = Math.round(availCenterY - leftH / 2);
      resolved.set(leftObj.id, { x: leftX, y: leftY, width: leftW, height: leftH });

      const rightX = Math.round((canvasWidth / 2) + (centerGutter / 2));
      const rightY = Math.round(availCenterY - rightH / 2);
      resolved.set(rightObj.id, { x: rightX, y: rightY, width: rightW, height: rightH });
      return resolved;
    }

    // Multi-element dual split (2 on left, or 2 on right):
    const colW = Math.round((canvasWidth / 2) - (centerGutter / 2) - safeLeftX);
    const colLeftX = safeLeftX;
    const colRightX = Math.round((canvasWidth / 2) + (centerGutter / 2));

    layoutColumnSurfaces(leftSurfaces, colLeftX, colW, availTopY, availHeight, "split", resolved);
    layoutColumnSurfaces(rightSurfaces, colRightX, colW, availTopY, availHeight, "split", resolved);
    return resolved;
  }

  // TOPOLOGY D: Center + Single Flank (e.g. Center Card + Left Image)
  if (centerSurfaces.length > 0 && (leftSurfaces.length > 0 || rightSurfaces.length > 0)) {
    const isLeft = leftSurfaces.length > 0;
    const flankSurfaces = isLeft ? leftSurfaces : rightSurfaces;
    const gutter = 60;
    const flankW = 560;
    const centerW = 600;

    if (isLeft) {
      layoutColumnSurfaces(leftSurfaces, safeLeftX + 20, flankW, availTopY, availHeight, "flank", resolved);
      layoutColumnSurfaces(centerSurfaces, safeLeftX + 20 + flankW + gutter, centerW, availTopY, availHeight, "flank", resolved);
    } else {
      layoutColumnSurfaces(centerSurfaces, safeLeftX + 20, centerW, availTopY, availHeight, "flank", resolved);
      layoutColumnSurfaces(rightSurfaces, safeLeftX + 20 + centerW + gutter, flankW, availTopY, availHeight, "flank", resolved);
    }
    return resolved;
  }

  // TOPOLOGY E: Multi-element in single zones (e.g. 2 cards in split_left only, or 2 in split_right only, or 2 in center only)
  if (leftSurfaces.length > 0 && rightSurfaces.length === 0 && centerSurfaces.length === 0) {
    layoutColumnSurfaces(leftSurfaces, safeLeftX + 40, 680, availTopY, availHeight, "split", resolved);
    return resolved;
  }

  if (rightSurfaces.length > 0 && leftSurfaces.length === 0 && centerSurfaces.length === 0) {
    layoutColumnSurfaces(rightSurfaces, canvasWidth - safeMargin - 720, 680, availTopY, availHeight, "split", resolved);
    return resolved;
  }

  if (centerSurfaces.length > 0 && leftSurfaces.length === 0 && rightSurfaces.length === 0) {
    layoutColumnSurfaces(centerSurfaces, Math.round((canvasWidth - 840) / 2), 840, availTopY, availHeight, "solo", resolved);
    return resolved;
  }

  // Fallback for any remaining unmapped multi-element configurations:
  for (const obj of upperSurfaces) {
    const { width: w, height: h } = resolveSurfacePreferredSize(obj, "split", availHeight);
    const layout = obj.layout ?? "center";
    let x = Math.round((canvasWidth - w) / 2);
    let y = Math.round(availCenterY - h / 2);

    if (layout === "split_left") {
      x = Math.round(480 - w / 2);
    } else if (layout === "split_right") {
      x = Math.round(1440 - w / 2);
    }

    resolved.set(obj.id, { x, y, width: w, height: h });
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
  } else if (to === "full_bottom") {
    destX = safeMargin;
    destY = canvasHeight - safeMargin - currentGeom.height - 40;
  } else if (to === "split_left") {
    destX = Math.round(480 - currentGeom.width / 2);
    destY = Math.round(540 - currentGeom.height / 2);
  } else if (to === "split_right") {
    destX = Math.round(1440 - currentGeom.width / 2);
    destY = Math.round(540 - currentGeom.height / 2);
  }

  // Safety boundary clamping
  let minX = safeMargin + 40;
  let maxX = canvasWidth - currentGeom.width - safeMargin - 40;
  if (to === "split_left") {
    maxX = Math.min(maxX, 960 - currentGeom.width);
  } else if (to === "split_right") {
    minX = Math.max(minX, 960);
  }
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
