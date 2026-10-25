import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const remotionRoot = path.resolve(__dirname, "..");
const sfxDir = path.join(remotionRoot, "public", "assets", "sfx");

console.log("==================================================");
console.log("TEST SUITE: REMOTION AUDIO SFX ENGINE");
console.log("==================================================");

// 1. Verify all 6 MP3 assets exist and are non-empty
const EXPECTED_SFX = [
  "paper_slide.mp3",
  "photo_drop.mp3",
  "marker_stroke.mp3",
  "stamp_thud.mp3",
  "counter_tick.mp3",
  "whoosh_cut.mp3",
];

console.log("\n--- TEST 1: Physical SFX Asset Verification ---");
for (const file of EXPECTED_SFX) {
  const filePath = path.join(sfxDir, file);
  assert.ok(fs.existsSync(filePath), `SFX asset file missing: ${file}`);
  const stats = fs.statSync(filePath);
  assert.ok(stats.size > 1000, `SFX asset file too small: ${file} (${stats.size} bytes)`);
  console.log(`✓ ${file} verified (${(stats.size / 1024).toFixed(1)} KB)`);
}

// 2. Import generateSoundCues from SoundEffectsLayer
// Using TypeScript via node --experimental-strip-types
const soundEffectsModulePath = path.join(
  remotionRoot,
  "src",
  "story_engine",
  "audio",
  "sfxEngine.ts"
);
const { generateSoundCues } = await import(soundEffectsModulePath);

console.log("\n--- TEST 2: Deterministic Cue Generation ---");

const testPlan = {
  id: "test_sfx_story",
  fps: 30,
  durationInFrames: 300,
  width: 1920,
  height: 1080,
  objects: [
    { id: "hero_card", type: "card", cardProps: { title: "Loan Details" } },
    { id: "trap_card", type: "card", cardProps: { title: "The Balloon Catch", badge: "BALLOON TRAP" } },
    { id: "bank_img", type: "image", imageProps: { src: "assets/bank.jpg" } },
    { id: "bank_vid", type: "stock_video", stockVideoProps: { src: "assets/bank.mp4" } },
    { id: "conn_1", type: "connector", connectorProps: { fromId: "hero_card", toId: "trap_card" } },
    { id: "emi_num", type: "number", numberProps: { value: 15000, format: "currency_inr" } },
  ],
  events: [
    // 0s: Card enter -> paper_slide
    { action: "enter", targetId: "hero_card", startFrame: 10, durationFrames: 15 },
    // 1s: Image enter -> photo_drop
    { action: "enter", targetId: "bank_img", startFrame: 30, durationFrames: 15 },
    // 2s: Stock video enter -> whoosh_cut
    { action: "enter", targetId: "bank_vid", startFrame: 60, durationFrames: 15 },
    // 3s: Highlight card -> marker_stroke
    { action: "highlight", targetId: "hero_card", startFrame: 90, durationFrames: 20 },
    // 4s: Number transform -> counter_tick
    { action: "transform_number", targetId: "emi_num", startFrame: 120, durationFrames: 24, toValue: 35000 },
    // 5s: Trap card enter with badge -> stamp_thud
    { action: "enter", targetId: "trap_card", startFrame: 160, durationFrames: 15 },
    // 6s: Change visual state to danger -> stamp_thud
    { action: "change_visual_state", targetId: "hero_card", startFrame: 200, durationFrames: 15, state: "danger" },
    // 7s: Stock video exit -> whoosh_cut
    { action: "exit", targetId: "bank_vid", startFrame: 240, durationFrames: 15, direction: "fade" },
  ],
};

const cues = generateSoundCues(testPlan);
assert.ok(cues.length > 0, "generateSoundCues produced no cues");

// Verify specific cues exist
const paperCues = cues.filter((c) => c.sound === "paper_slide");
const photoCues = cues.filter((c) => c.sound === "photo_drop");
const whooshCues = cues.filter((c) => c.sound === "whoosh_cut");
const markerCues = cues.filter((c) => c.sound === "marker_stroke");
const stampCues = cues.filter((c) => c.sound === "stamp_thud");
const tickCues = cues.filter((c) => c.sound === "counter_tick");

assert.ok(paperCues.length >= 1, "Expected at least 1 paper_slide cue");
assert.ok(photoCues.length >= 1, "Expected at least 1 photo_drop cue");
assert.ok(whooshCues.length >= 2, "Expected at least 2 whoosh_cut cues (enter + exit)");
assert.ok(markerCues.length >= 1, "Expected at least 1 marker_stroke cue");
assert.ok(stampCues.length >= 2, "Expected at least 2 stamp_thud cues (trap badge + danger state)");
assert.ok(tickCues.length >= 3, "Expected at least 3 counter_tick cues across number transform");

console.log(`✓ paper_slide cues generated: ${paperCues.length}`);
console.log(`✓ photo_drop cues generated: ${photoCues.length}`);
console.log(`✓ whoosh_cut cues generated: ${whooshCues.length}`);
console.log(`✓ marker_stroke cues generated: ${markerCues.length}`);
console.log(`✓ stamp_thud cues generated: ${stampCues.length}`);
console.log(`✓ counter_tick cues generated: ${tickCues.length}`);

console.log("\n--- TEST 3: Anti-Ear-Fatigue Interval Throttling ---");
// Plan with two rapid paper_slide triggers 4 frames apart (< 10 frame threshold)
const rapidPlan = {
  id: "rapid_plan",
  fps: 30,
  durationInFrames: 100,
  width: 1920,
  height: 1080,
  objects: [
    { id: "c1", type: "card" },
    { id: "c2", type: "card" },
  ],
  events: [
    { action: "enter", targetId: "c1", startFrame: 10, durationFrames: 15 },
    { action: "enter", targetId: "c2", startFrame: 14, durationFrames: 15 }, // Only 4 frames later!
  ],
};
const rapidCues = generateSoundCues(rapidPlan);
assert.equal(
  rapidCues.length,
  1,
  `Throttling failed: expected 1 cue due to < 10-frame gap, but got ${rapidCues.length}`
);
assert.equal(rapidCues[0].frame, 10, "First cue at frame 10 should be preserved");
console.log("✓ Rapid identical SFX suppressed within 10 frames (anti-fatigue throttle working)");

console.log("\n--- TEST 4: Max Concurrent Cues Cap Per Frame ---");
// Plan with 4 simultaneous events at frame 50
const pileupPlan = {
  id: "pileup_plan",
  fps: 30,
  durationInFrames: 100,
  width: 1920,
  height: 1080,
  objects: [
    { id: "c1", type: "card" },
    { id: "img1", type: "image" },
    { id: "vid1", type: "stock_video" },
    { id: "danger_c", type: "card", cardProps: { badge: "TRAP" } },
  ],
  events: [
    { action: "enter", targetId: "c1", startFrame: 50, durationFrames: 15 },       // priority 2
    { action: "enter", targetId: "img1", startFrame: 50, durationFrames: 15 },     // priority 3
    { action: "enter", targetId: "vid1", startFrame: 50, durationFrames: 15 },     // priority 4
    { action: "enter", targetId: "danger_c", startFrame: 50, durationFrames: 15 }, // priority 5
  ],
};
const pileupCues = generateSoundCues(pileupPlan);
assert.equal(
  pileupCues.length,
  2,
  `Concurrent cap failed: expected exactly 2 cues, but got ${pileupCues.length}`
);
// The 2 highest priority cues (priority 5: stamp_thud, priority 4: whoosh_cut) must survive
const survivingSounds = pileupCues.map((c) => c.sound);
assert.ok(survivingSounds.includes("stamp_thud"), "Highest priority stamp_thud should survive");
assert.ok(survivingSounds.includes("whoosh_cut"), "Second highest priority whoosh_cut should survive");
console.log("✓ Concurrent frame cap enforced: 4 simultaneous events capped to top 2 priority cues");

console.log("\n==================================================");
console.log("SUCCESS: ALL AUDIO SFX ENGINE TESTS PASSED (0 ERRORS)");
console.log("==================================================");
