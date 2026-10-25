import type { StoryPlan, StoryObject, StoryAction } from "../types.ts";

export type SoundEffectType =
  | "paper_slide"
  | "photo_drop"
  | "marker_stroke"
  | "stamp_thud"
  | "counter_tick"
  | "whoosh_cut";

export interface SoundCue {
  id: string;
  sound: SoundEffectType;
  file: string;
  frame: number;
  durationFrames: number;
  volume: number;
  priority: number;
}

export const SFX_CONFIG: Record<
  SoundEffectType,
  {
    file: string;
    durationFrames: number;
    defaultVolume: number;
    priority: number;
    minIntervalFrames: number;
  }
> = {
  stamp_thud: {
    file: "stamp_thud.mp3",
    durationFrames: 12,
    defaultVolume: 0.50,
    priority: 5,
    minIntervalFrames: 12,
  },
  whoosh_cut: {
    file: "whoosh_cut.mp3",
    durationFrames: 12,
    defaultVolume: 0.40,
    priority: 4,
    minIntervalFrames: 15,
  },
  photo_drop: {
    file: "photo_drop.mp3",
    durationFrames: 9,
    defaultVolume: 0.32,
    priority: 3,
    minIntervalFrames: 10,
  },
  marker_stroke: {
    file: "marker_stroke.mp3",
    durationFrames: 14,
    defaultVolume: 0.42,
    priority: 3,
    minIntervalFrames: 12,
  },
  paper_slide: {
    file: "paper_slide.mp3",
    durationFrames: 11,
    defaultVolume: 0.35,
    priority: 2,
    minIntervalFrames: 10,
  },
  counter_tick: {
    file: "counter_tick.mp3",
    durationFrames: 3,
    defaultVolume: 0.25,
    priority: 1,
    minIntervalFrames: 4,
  },
};

const TRAP_BADGE_REGEX = /TRAP|HIDDEN|BURDEN|DANGER|RISK|PENALTY|WARNING|FEES|LOSS|FINE/i;
export const MIN_INTERVAL_SAME_SOUND_FRAMES = 10; // ~333ms anti-fatigue gap
export const MAX_CONCURRENT_SFX_PER_FRAME = 2; // Prevent muddy multi-sound pileups

export function generateSoundCues(plan: StoryPlan): SoundCue[] {
  if (!plan.events || plan.events.length === 0) {
    return [];
  }

  const objectMap = new Map<string, StoryObject>();
  for (const obj of plan.objects) {
    objectMap.set(obj.id, obj);
  }

  const rawCues: SoundCue[] = [];
  let cueCounter = 0;

  for (const event of plan.events) {
    const targetId = "targetId" in event && typeof event.targetId === "string" ? event.targetId : undefined;
    const targetObj = targetId ? objectMap.get(targetId) : undefined;

    switch (event.action) {
      case "enter": {
        if (!targetObj || !targetId) break;
        if (targetObj.type === "image") {
          rawCues.push({
            id: `sfx_enter_${targetId}_${cueCounter++}`,
            sound: "photo_drop",
            file: SFX_CONFIG.photo_drop.file,
            frame: event.startFrame,
            durationFrames: SFX_CONFIG.photo_drop.durationFrames,
            volume: SFX_CONFIG.photo_drop.defaultVolume,
            priority: SFX_CONFIG.photo_drop.priority,
          });
        } else if (targetObj.type === "stock_video") {
          rawCues.push({
            id: `sfx_enter_${targetId}_${cueCounter++}`,
            sound: "whoosh_cut",
            file: SFX_CONFIG.whoosh_cut.file,
            frame: event.startFrame,
            durationFrames: SFX_CONFIG.whoosh_cut.durationFrames,
            volume: SFX_CONFIG.whoosh_cut.defaultVolume,
            priority: SFX_CONFIG.whoosh_cut.priority,
          });
        } else if (["card", "document", "text", "character"].includes(targetObj.type)) {
          // If the card already enters with a TRAP or DANGER badge, give it a stamp thud!
          const hasTrapBadge =
            (targetObj.cardProps?.badge && TRAP_BADGE_REGEX.test(targetObj.cardProps.badge)) ||
            (targetObj.documentProps?.statusBadge && TRAP_BADGE_REGEX.test(targetObj.documentProps.statusBadge));

          if (hasTrapBadge) {
            rawCues.push({
              id: `sfx_enter_trap_${targetId}_${cueCounter++}`,
              sound: "stamp_thud",
              file: SFX_CONFIG.stamp_thud.file,
              frame: event.startFrame,
              durationFrames: SFX_CONFIG.stamp_thud.durationFrames,
              volume: SFX_CONFIG.stamp_thud.defaultVolume,
              priority: SFX_CONFIG.stamp_thud.priority,
            });
          } else {
            rawCues.push({
              id: `sfx_enter_${targetId}_${cueCounter++}`,
              sound: "paper_slide",
              file: SFX_CONFIG.paper_slide.file,
              frame: event.startFrame,
              durationFrames: SFX_CONFIG.paper_slide.durationFrames,
              volume: SFX_CONFIG.paper_slide.defaultVolume,
              priority: SFX_CONFIG.paper_slide.priority,
            });
          }
        }
        break;
      }

      case "exit": {
        if (!targetObj || !targetId) break;
        if (targetObj.type === "stock_video") {
          rawCues.push({
            id: `sfx_exit_${targetId}_${cueCounter++}`,
            sound: "whoosh_cut",
            file: SFX_CONFIG.whoosh_cut.file,
            frame: event.startFrame,
            durationFrames: SFX_CONFIG.whoosh_cut.durationFrames,
            volume: 0.30,
            priority: SFX_CONFIG.whoosh_cut.priority,
          });
        } else if (["card", "document"].includes(targetObj.type)) {
          rawCues.push({
            id: `sfx_exit_${targetId}_${cueCounter++}`,
            sound: "paper_slide",
            file: SFX_CONFIG.paper_slide.file,
            frame: event.startFrame,
            durationFrames: SFX_CONFIG.paper_slide.durationFrames,
            volume: 0.22,
            priority: SFX_CONFIG.paper_slide.priority,
          });
        }
        break;
      }

      case "highlight": {
        if (!targetId) break;
        rawCues.push({
          id: `sfx_highlight_${targetId}_${cueCounter++}`,
          sound: "marker_stroke",
          file: SFX_CONFIG.marker_stroke.file,
          frame: event.startFrame,
          durationFrames: SFX_CONFIG.marker_stroke.durationFrames,
          volume: SFX_CONFIG.marker_stroke.defaultVolume,
          priority: SFX_CONFIG.marker_stroke.priority,
        });
        break;
      }

      case "connect": {
        if (!targetId) break;
        rawCues.push({
          id: `sfx_connect_${targetId}_${cueCounter++}`,
          sound: "marker_stroke",
          file: SFX_CONFIG.marker_stroke.file,
          frame: event.startFrame,
          durationFrames: SFX_CONFIG.marker_stroke.durationFrames,
          volume: 0.28,
          priority: SFX_CONFIG.marker_stroke.priority,
        });
        break;
      }

      case "change_visual_state": {
        if (!targetId) break;
        const isTrapState =
          ["danger", "stamped", "eroded"].includes(event.state) ||
          Boolean(event.stamp) ||
          Boolean(event.badge && TRAP_BADGE_REGEX.test(event.badge));

        if (isTrapState) {
          rawCues.push({
            id: `sfx_state_${targetId}_${cueCounter++}`,
            sound: "stamp_thud",
            file: SFX_CONFIG.stamp_thud.file,
            frame: event.startFrame,
            durationFrames: SFX_CONFIG.stamp_thud.durationFrames,
            volume: SFX_CONFIG.stamp_thud.defaultVolume,
            priority: SFX_CONFIG.stamp_thud.priority,
          });
        } else if (event.state === "warning") {
          rawCues.push({
            id: `sfx_state_warn_${targetId}_${cueCounter++}`,
            sound: "stamp_thud",
            file: SFX_CONFIG.stamp_thud.file,
            frame: event.startFrame,
            durationFrames: SFX_CONFIG.stamp_thud.durationFrames,
            volume: 0.35,
            priority: SFX_CONFIG.stamp_thud.priority,
          });
        } else {
          rawCues.push({
            id: `sfx_state_${targetId}_${cueCounter++}`,
            sound: "paper_slide",
            file: SFX_CONFIG.paper_slide.file,
            frame: event.startFrame,
            durationFrames: SFX_CONFIG.paper_slide.durationFrames,
            volume: 0.25,
            priority: SFX_CONFIG.paper_slide.priority,
          });
        }
        break;
      }

      case "transform_number": {
        if (!targetId) break;
        const duration = Math.max(1, event.durationFrames);
        const steps = duration >= 24 ? 4 : duration >= 12 ? 3 : 2;
        for (let i = 0; i < steps; i++) {
          const tickOffset = Math.round((i / (steps - 1 || 1)) * (duration - 2));
          rawCues.push({
            id: `sfx_tick_${targetId}_${i}_${cueCounter++}`,
            sound: "counter_tick",
            file: SFX_CONFIG.counter_tick.file,
            frame: event.startFrame + tickOffset,
            durationFrames: SFX_CONFIG.counter_tick.durationFrames,
            volume: SFX_CONFIG.counter_tick.defaultVolume,
            priority: SFX_CONFIG.counter_tick.priority,
          });
        }
        break;
      }

      default:
        break;
    }
  }

  // Sort chronologically by start frame
  rawCues.sort((a, b) => {
    if (a.frame !== b.frame) return a.frame - b.frame;
    return b.priority - a.priority; // higher priority first at same frame
  });

  // Apply Anti-Fatigue Throttling & Concurrent Cues Cap
  const filteredCues: SoundCue[] = [];
  const lastPlayedBySound: Record<string, number> = {};
  const frameCountMap: Record<number, number> = {};

  for (const cue of rawCues) {
    // 1. Boundary check: must be >= 0 and within plan duration
    if (cue.frame < 0 || cue.frame >= plan.durationInFrames) {
      continue;
    }

    // 2. Anti-fatigue interval throttle for identical sound cues
    const lastFrame = lastPlayedBySound[cue.sound];
    const minGap = SFX_CONFIG[cue.sound]?.minIntervalFrames ?? MIN_INTERVAL_SAME_SOUND_FRAMES;
    if (lastFrame !== undefined && cue.frame - lastFrame < minGap) {
      continue; // Dropped to avoid robotic repetition
    }

    // 3. Concurrent cues cap per frame
    const currentFrameCount = frameCountMap[cue.frame] || 0;
    if (currentFrameCount >= MAX_CONCURRENT_SFX_PER_FRAME) {
      continue; // Dropped to avoid ear clutter
    }

    // Accept cue
    filteredCues.push(cue);
    lastPlayedBySound[cue.sound] = cue.frame;
    frameCountMap[cue.frame] = currentFrameCount + 1;
  }

  return filteredCues;
}
