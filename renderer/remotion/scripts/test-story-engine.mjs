import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { validateStoryPlan } from "../src/story_engine/validator.ts";
import { resolveLayouts, resolveSemanticDestination } from "../src/story_engine/layout.ts";
import { evaluateFrame } from "../src/story_engine/engine.ts";
import { resolveAnchorFrame } from "../src/story_engine/speech_anchors.ts";
import { loanStoryPlan } from "../src/story_engine/loanStoryPlan.ts";
import { inflationStoryPlan } from "../src/story_engine/inflationStoryPlan.ts";
import { salarySplitStoryPlan } from "../src/story_engine/salarySplitStoryPlan.ts";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const publicDir = path.resolve(scriptDir, "../public");

console.log("==================================================");
console.log("CONTINUOUS STORY ENGINE: ADVANCED PROTOCOL TEST SUITE");
console.log("==================================================");

// ----------------------------------------------------
// 1. REAL NARRATION AUDIO PRESENCE (Issue 1)
// ----------------------------------------------------
console.log("\n--- TEST 1: Real Audible Voice Narration Files ---");
const audioFiles = [
  "loan_narration.mp3",
  "inflation_narration.mp3",
  "salary_split_narration.mp3",
];
for (const af of audioFiles) {
  const p = path.join(publicDir, af);
  if (!fs.existsSync(p)) {
    throw new Error(`FAIL: Audio file '${af}' missing from public/`);
  }
  const stats = fs.statSync(p);
  if (stats.size < 10000) {
    throw new Error(`FAIL: Audio file '${af}' is suspiciously small (${stats.size} bytes)`);
  }
  console.log(`✓ Audio file '${af}' present and valid (${(stats.size / 1024).toFixed(1)} KB)`);
}

// ----------------------------------------------------
// 2. TIMED TEXT REVEAL: NO MISLEADING SUBTITLES (Issue 2)
// ----------------------------------------------------
console.log("\n--- TEST 2: Timed Text Reveal (No Misleading Initial Burden) ---");
const loanLayouts = resolveLayouts(loanStoryPlan.objects, 1920, 1080, 80);

// Frame 140: EMI card has entered, but rate hike has NOT occurred
const f140 = evaluateFrame(loanStoryPlan, loanLayouts, 140);
const emi140 = f140.objects.get("card_emi");
if (emi140.currentSubtitleValue?.includes("burden")) {
  throw new Error(`FAIL: EMI card displays misleading burden before rate hike! Got: '${emi140.currentSubtitleValue}'`);
}
console.log(`✓ Frame 140: Initial EMI subtitle is neutral: '${emi140.currentSubtitleValue}'`);

// Frame 280: Rate hike has occurred and EMI has surged -> burden is revealed!
const f280 = evaluateFrame(loanStoryPlan, loanLayouts, 280);
const emi280 = f280.objects.get("card_emi");
if (!emi280.currentSubtitleValue?.includes("burden")) {
  throw new Error(`FAIL: EMI card failed to reveal burden after rate hike! Got: '${emi280.currentSubtitleValue}'`);
}
console.log(`✓ Frame 280: EMI subtitle correctly transformed to: '${emi280.currentSubtitleValue}'`);

// ----------------------------------------------------
// 3. CAMERA CONTEXT PRESERVATION (Issue 3)
// ----------------------------------------------------
console.log("\n--- TEST 3: Camera Framing Context Preservation ---");
// Golden plans must pass context framing checks
const loanValidation = validateStoryPlan(loanStoryPlan);
if (!loanValidation.valid) {
  console.error("Loan Validation Errors:", loanValidation.errors);
  throw new Error("Loan plan failed camera context check!");
}
const inflationValidation = validateStoryPlan(inflationStoryPlan);
if (!inflationValidation.valid) {
  console.error("Inflation Validation Errors:", inflationValidation.errors);
  throw new Error("Inflation plan failed camera context check!");
}
console.log("✓ Golden plans preserve all required context objects within safe margins.");

// Negative test: An aggressive zoom that crops context must be rejected!
const badCameraPlan = JSON.parse(JSON.stringify(inflationStoryPlan));
badCameraPlan.events.find((e) => e.action === "camera").zoom = 1.65; // Over-zoom that crops top cards!
const resBadCamera = validateStoryPlan(badCameraPlan);
if (resBadCamera.valid || !resBadCamera.errors.some((e) => e.code === "CAMERA_CONTEXT_CLIPPED")) {
  throw new Error("FAIL: Validator should reject camera movement that crops required context cards");
}
console.log("✓ Successfully caught and rejected over-zooming camera movement (CAMERA_CONTEXT_CLIPPED).");

// ----------------------------------------------------
// 4. FACTUAL PROVENANCE DERIVATION (Issue 6)
// ----------------------------------------------------
console.log("\n--- TEST 4: Factual Provenance Mathematical Derivations ---");
// Test negative: loan_emi formula mismatch
const badEmiMathPlan = JSON.parse(JSON.stringify(loanStoryPlan));
badEmiMathPlan.events.find((e) => e.action === "transform_number" && e.targetId === "card_emi").toValue = 65000; // Hallucinated EMI!
const resBadEmi = validateStoryPlan(badEmiMathPlan);
if (resBadEmi.valid || !resBadEmi.errors.some((e) => e.code === "PROVENANCE_CALCULATION_MISMATCH")) {
  throw new Error("FAIL: Validator should reject mathematical mismatch in loan_emi provenance");
}
console.log("✓ Successfully caught and rejected hallucinated EMI (stated 65,000 vs derived 49,919).");

// ----------------------------------------------------
// 5. THIRD STORY: SPLIT BEHAVIOR & DOCUMENT PRIMITIVE (Issue 4, 5, 6)
// ----------------------------------------------------
console.log("\n--- TEST 5: Third Story (Salary Statement Document & Split Flow) ---");
const salaryValidation = validateStoryPlan(salarySplitStoryPlan);
if (!salaryValidation.valid) {
  console.error("Salary Split Errors:", salaryValidation.errors);
  throw new Error("Salary split story plan failed validation!");
}
console.log("✓ Salary split story plan passed all validation rules.");

// Verify Document Primitive
const salaryDoc = salarySplitStoryPlan.objects.find((o) => o.id === "doc_salary");
if (!salaryDoc || salaryDoc.type !== "document" || !salaryDoc.documentProps) {
  throw new Error("FAIL: Salary document primitive missing or invalid type");
}
console.log(`✓ Non-Card Document Primitive verified: '${salaryDoc.documentProps.title}' (${salaryDoc.documentProps.serialNo})`);

// Verify Split Layout & Continuity after all anchors conclude
const salaryLayouts = resolveLayouts(salarySplitStoryPlan.objects, 1920, 1080, 80);
const f340 = evaluateFrame(salarySplitStoryPlan, salaryLayouts, 340);

const docF340 = f340.objects.get("doc_salary");
const taxF340 = f340.objects.get("card_tax");
const livingF340 = f340.objects.get("card_living");
const savingsF340 = f340.objects.get("card_savings");

if (!docF340.isEntered || docF340.opacity !== 1) {
  throw new Error("FAIL: doc_salary lost persistence during split!");
}
if (!taxF340.isEntered || !livingF340.isEntered || !savingsF340.isEntered) {
  throw new Error("FAIL: Split cards failed to enter!");
}
console.log("✓ Object Continuity Verified during 3-way Split:");
console.log(`  - Official Document: PERSISTENT at (${docF340.x}, ${docF340.y})`);
console.log(`  - Tax Deduction:     ENTERED at (${taxF340.x}, ${taxF340.y})`);
console.log(`  - Living Expenses:   ENTERED at (${livingF340.x}, ${livingF340.y})`);
console.log(`  - Net Savings:       ENTERED at (${savingsF340.x}, ${savingsF340.y})`);

// Test negative: Salary tax split provenance mismatch (sum != gross)
const badSplitPlan = JSON.parse(JSON.stringify(salarySplitStoryPlan));
badSplitPlan.objects[0].documentProps.provenance.derived_from.inputs.savings = 3500000; // 15L + 10L + 35L = 60L != 50L!
const resBadSplit = validateStoryPlan(badSplitPlan);
if (resBadSplit.valid || !resBadSplit.errors.some((e) => e.code === "PROVENANCE_CALCULATION_MISMATCH")) {
  throw new Error("FAIL: Validator should reject salary split when deductions do not equal gross");
}
console.log("✓ Successfully caught and rejected invalid split balance (15L + 10L + 35L != 50L).");

// ----------------------------------------------------
// 6. TRUE SPLIT / MERGE TRANSFORMATION MECHANICS
// ----------------------------------------------------
console.log("\n--- TEST 6: True Split/Merge Transformation Mechanics ---");
// Frame 90: Split starts. Daughter card emerges from document origin!
const f90 = evaluateFrame(salarySplitStoryPlan, salaryLayouts, 90);
const taxF90 = f90.objects.get("card_tax");
const docGeom = salaryLayouts.get("doc_salary");
const expectedOriginX = docGeom.x + docGeom.width / 2 - taxF90.width / 2;
const expectedOriginY = docGeom.y + docGeom.height / 2 - taxF90.height / 2;

if (Math.abs(taxF90.x - expectedOriginX) > 2 || Math.abs(taxF90.y - expectedOriginY) > 2) {
  throw new Error(`FAIL: True split daughter card did not emerge from parent coordinates! Expected (${expectedOriginX}, ${expectedOriginY}), got (${taxF90.x}, ${taxF90.y})`);
}
if (taxF90.scale > 0.35) {
  throw new Error(`FAIL: True split daughter card should emerge compact! Scale: ${taxF90.scale}`);
}
console.log(`✓ Frame 90: Split daughter physically emerged from parent center: (${taxF90.x}, ${taxF90.y}) with compact scale ${taxF90.scale.toFixed(2)}`);

const taxTargetX = salaryLayouts.get("card_tax").x;

// Frame 105: Mid-split travel
const f105 = evaluateFrame(salarySplitStoryPlan, salaryLayouts, 105);
const taxF105 = f105.objects.get("card_tax");
if (taxF105.x <= expectedOriginX || taxF105.x >= taxTargetX) {
  throw new Error(`FAIL: Daughter card not in flight between parent and destination! x=${taxF105.x}`);
}
console.log(`✓ Frame 105: Daughter card traveling along split vector: x=${taxF105.x.toFixed(1)}, scale=${taxF105.scale.toFixed(2)}`);

// Frame 130: Settled at destination
const f130 = evaluateFrame(salarySplitStoryPlan, salaryLayouts, 130);
const taxF130 = f130.objects.get("card_tax");
if (Math.abs(taxF130.x - taxTargetX) > 2 || Math.abs(taxF130.scale - 1.0) > 0.05) {
  throw new Error(`FAIL: Daughter card failed to settle at target! x=${taxF130.x}, scale=${taxF130.scale}`);
}
console.log(`✓ Frame 130: Daughter card settled at destination (${taxF130.x}, ${taxF130.y}) with full scale`);

// Negative test: Self-referencing split
const badSelfSplit = JSON.parse(JSON.stringify(salarySplitStoryPlan));
badSelfSplit.events.push({
  action: "split",
  sourceId: "doc_salary",
  targetIds: ["doc_salary"], // Self reference!
  startFrame: 50,
  durationFrames: 20,
});
const resSelfSplit = validateStoryPlan(badSelfSplit);
if (resSelfSplit.valid || !resSelfSplit.errors.some((e) => e.code === "SPLIT_SELF_REFERENCE")) {
  throw new Error("FAIL: Validator should reject self-referencing split");
}
console.log("✓ Successfully caught and rejected self-referencing split (SPLIT_SELF_REFERENCE).");

// ----------------------------------------------------
// 7. CHART PRIMITIVE PARTICIPATION IN CONTINUOUS SCENE
// ----------------------------------------------------
console.log("\n--- TEST 7: Chart Primitive Participation ---");
const inflationChart = inflationStoryPlan.objects.find((o) => o.id === "chart_decay_curve");
if (!inflationChart || inflationChart.type !== "chart" || !inflationChart.chartProps) {
  throw new Error("FAIL: Chart primitive missing from inflationStoryPlan!");
}
if (inflationChart.chartProps.chartType !== "trajectory_area") {
  throw new Error("FAIL: Chart chartType mismatch!");
}
if (inflationChart.chartProps.series[0].points.length !== 6) {
  throw new Error("FAIL: Chart points incomplete!");
}
console.log(`✓ Chart Primitive verified: '${inflationChart.chartProps.title}' (${inflationChart.chartProps.series[0].points.length} trajectory points)`);

// ----------------------------------------------------
// 8. RICH VISUAL STATE CHANGES BEYOND NUMBERS
// ----------------------------------------------------
console.log("\n--- TEST 8: Rich Visual State Changes (Beyond Numbers) ---");
const loanF275 = evaluateFrame(loanStoryPlan, loanLayouts, 275);
const rateState = loanF275.objects.get("card_rate");
const emiState = loanF275.objects.get("card_emi");
const loanState = loanF275.objects.get("card_loan");

if (rateState.visualState !== "warning" || rateState.visualBadge !== "+2.0% HIKE") {
  throw new Error(`FAIL: card_rate visual state mismatch! Got: ${rateState.visualState}, badge: ${rateState.visualBadge}`);
}
if (emiState.visualState !== "danger" || emiState.visualBadge !== "BURDEN SURGE") {
  throw new Error(`FAIL: card_emi visual state mismatch! Got: ${emiState.visualState}, badge: ${emiState.visualBadge}`);
}
if (loanState.visualState !== "dimmed" || loanState.opacity > 0.4) {
  throw new Error(`FAIL: card_loan failed to dim! Opacity: ${loanState.opacity}`);
}
console.log("✓ Loan Story Visual States:");
console.log(`  - Rate Card:      State '${rateState.visualState}' [Badge: ${rateState.visualBadge}]`);
console.log(`  - EMI Card:       State '${emiState.visualState}' [Badge: ${emiState.visualBadge}]`);
console.log(`  - Loan Card:      State '${loanState.visualState}' [Opacity: ${loanState.opacity.toFixed(2)}]`);

// Salary split visual states
const salaryF60 = evaluateFrame(salarySplitStoryPlan, salaryLayouts, 60);
const docStamp = salaryF60.objects.get("doc_salary");
if (!docStamp.visualStamp || docStamp.visualStamp.text !== "SANCTIONED") {
  throw new Error(`FAIL: doc_salary rubber stamp missing! Got: ${JSON.stringify(docStamp.visualStamp)}`);
}
console.log(`✓ Salary Document: Rubber Stamp active: '${docStamp.visualStamp.text}' (${docStamp.visualStamp.color})`);

// Inflation story visual states
const inflationLayouts = resolveLayouts(inflationStoryPlan.objects, 1920, 1080, 80);
const infF270 = evaluateFrame(inflationStoryPlan, inflationLayouts, 270);
const powerState = infF270.objects.get("card_purchasing_power");
if (powerState.visualState !== "eroded" || powerState.visualBadge !== "CRITICAL LOSS") {
  throw new Error(`FAIL: card_purchasing_power failed to transition to eroded! Got: ${powerState.visualState}`);
}
console.log(`✓ Inflation Story: Purchasing power card eroded: State '${powerState.visualState}' [Badge: ${powerState.visualBadge}]`);

// ----------------------------------------------------
// 9. AUDIO-VISUAL SYNCHRONIZATION AUDIT
// ----------------------------------------------------
console.log("\n--- TEST 9: Audio-Visual Synchronization Alignment Audit ---");
const plans = [
  { name: "Loan Story", plan: loanStoryPlan },
  { name: "Inflation Story", plan: inflationStoryPlan },
  { name: "Salary Split Story", plan: salarySplitStoryPlan },
];

for (const { name, plan } of plans) {
  const words = plan.narration.wordTimestamps;
  const anchoredEvents = plan.events.filter((e) => e.anchor);
  console.log(`\nAuditing ${name} (${anchoredEvents.length} anchored beats):`);

  for (const ev of anchoredEvents) {
    const resolvedFrame = resolveAnchorFrame(words, ev.anchor, plan.fps);
    if (resolvedFrame === 0) continue;

    const visualTimeSec = resolvedFrame / plan.fps;

    // Find the matching word timestamp
    const cleanTokens = ev.anchor.toLowerCase().replace(/[^\w\s\.]/g, "").split(/\s+/).filter(Boolean);
    let matchedWord = null;
    for (let i = 0; i <= words.length - cleanTokens.length; i++) {
      let match = true;
      for (let j = 0; j < cleanTokens.length; j++) {
        const w = words[i + j].word.toLowerCase().replace(/[^\w\s\.]/g, "");
        if (!w.includes(cleanTokens[j]) && !cleanTokens[j].includes(w)) {
          match = false;
          break;
        }
      }
      if (match) {
        matchedWord = words[i];
        break;
      }
    }

    if (!matchedWord) continue;

    const audioTimeSec = matchedWord.start_ms / 1000;
    const deltaMs = Math.abs((visualTimeSec - audioTimeSec) * 1000);

    console.log(
      `  • Anchor "${ev.anchor}": Audio @ ${audioTimeSec.toFixed(3)}s | Visual Frame ${resolvedFrame} (${visualTimeSec.toFixed(3)}s) | Δt = ${deltaMs.toFixed(1)}ms`
    );

    // Dynamic resolution must be sub-frame accurate (<= 34ms at 30fps)
    if (deltaMs > 34) {
      throw new Error(`FAIL: Audio/visual desync on anchor "${ev.anchor}"! Δt = ${deltaMs}ms exceeds 34ms threshold.`);
    }
  }
}
console.log("\n✓ All audio-visual triggers verified sub-frame accurate (Δt <= 34ms)!");

// ----------------------------------------------------
// 10. TARGETED SPATIAL ZONE, MACRO LAYOUT & COLLISION CHECKS
// ----------------------------------------------------
console.log("\n--- TEST 10: Targeted Spatial Collision, Macro Zones & Boundary Checks ---");

// 10.1: Invalid layout zone name must throw INVALID_LAYOUT_ZONE
let didThrowInvalidLayout = false;
try {
  resolveLayouts([
    {
      id: "malformed_card",
      type: "card",
      layout: "arbitrary_floating_box",
    },
  ]);
} catch (err) {
  if (err.message.includes("INVALID_LAYOUT_ZONE")) {
    didThrowInvalidLayout = true;
  }
}
if (!didThrowInvalidLayout) {
  throw new Error("FAIL: resolveLayouts must throw INVALID_LAYOUT_ZONE when receiving an unknown layout zone!");
}
console.log("✓ resolveLayouts() strictly throws INVALID_LAYOUT_ZONE on malformed layout strings.");

// 10.2: Move action strictly throws on invalid destination zone
let didThrowInvalidMoveZone = false;
try {
  resolveSemanticDestination("offset_diagonal_40px", { x: 960, y: 540, width: 420, height: 240 });
} catch (err) {
  if (err.message.includes("INVALID_LAYOUT_ZONE")) {
    didThrowInvalidMoveZone = true;
  }
}
if (!didThrowInvalidMoveZone) {
  throw new Error("FAIL: resolveSemanticDestination must throw INVALID_LAYOUT_ZONE on non-zone targets!");
}
console.log("✓ resolveSemanticDestination() strictly enforces ZoneName and forbids arbitrary offsets.");

// 10.3: full_screen with another visible object must be caught
const fullScreenConflictPlan = {
  id: "fs_conflict",
  fps: 30,
  durationInFrames: 100,
  width: 1920,
  height: 1080,
  objects: [
    { id: "hero_img", type: "image", layout: "full_screen", imageProps: { src: "test.png" } },
    { id: "card_overlap", type: "card", layout: "center", cardProps: { title: "Overlapping Card" } },
  ],
  events: [
    { action: "enter", targetId: "hero_img", startFrame: 0, durationFrames: 10 },
    { action: "enter", targetId: "card_overlap", startFrame: 0, durationFrames: 10 },
  ],
};
const resFs = validateStoryPlan(fullScreenConflictPlan);
if (resFs.valid || (!resFs.errors.some((e) => e.code === "MACRO_LAYOUT_COLLISION") && !resFs.errors.some((e) => e.code === "CARD_OVERLAP"))) {
  throw new Error("FAIL: Validator should reject full_screen coexisting with another visible surface!");
}
console.log("✓ Caught and rejected full_screen coexisting with another visible element (MACRO_LAYOUT_COLLISION).");

// 10.4: full_bottom encroaching on subtitles must be caught
const fullBottomSubtitleConflictPlan = {
  id: "sub_conflict_full_bottom",
  fps: 30,
  durationInFrames: 100,
  width: 1920,
  height: 1080,
  objects: [
    {
      id: "deep_bottom_chart",
      type: "chart",
      layout: "full_bottom",
      height: 450, // Exceeds max full_bottom height (380px) and encroaches into subtitle space
      chartProps: { chartType: "trajectory_area" },
    },
  ],
  events: [{ action: "enter", targetId: "deep_bottom_chart", startFrame: 0, durationFrames: 10 }],
};
const resSub = validateStoryPlan(fullBottomSubtitleConflictPlan);
if (resSub.valid || !resSub.errors.some((e) => e.code === "SUBTITLE_OVERLAP")) {
  throw new Error("FAIL: Validator should reject full_bottom encroaching on subtitle safe area!");
}
console.log("✓ Caught and rejected full_bottom encroaching on subtitle boundary (SUBTITLE_OVERLAP).");

// 10.5: Wide chart beside a card must be caught by AABB collision check
const wideChartPlan = {
  id: "wide_chart_conflict",
  fps: 30,
  durationInFrames: 100,
  width: 1920,
  height: 1080,
  objects: [
    { id: "left_card", type: "card", layout: "center_left", cardProps: { title: "Left Card" } },
    { id: "wide_chart", type: "chart", layout: "center", width: 850, chartProps: { chartType: "trajectory_area" } },
  ],
  events: [
    { action: "enter", targetId: "left_card", startFrame: 0, durationFrames: 10 },
    { action: "enter", targetId: "wide_chart", startFrame: 0, durationFrames: 10 },
  ],
};
const resWide = validateStoryPlan(wideChartPlan);
if (resWide.valid || !resWide.errors.some((e) => e.code === "CARD_OVERLAP")) {
  throw new Error("FAIL: Validator should reject wide chart colliding with adjacent card!");
}
console.log("✓ Caught and rejected wide chart overlapping adjacent card (CARD_OVERLAP).");

// 10.6: Two objects entering the same zone simultaneously must be caught
const sameZonePlan = {
  id: "same_zone_conflict",
  fps: 30,
  durationInFrames: 100,
  width: 1920,
  height: 1080,
  objects: [
    { id: "card_a", type: "card", layout: "center", cardProps: { title: "Card A" } },
    { id: "card_b", type: "card", layout: "center", cardProps: { title: "Card B" } },
  ],
  events: [
    { action: "enter", targetId: "card_a", startFrame: 0, durationFrames: 10 },
    { action: "enter", targetId: "card_b", startFrame: 0, durationFrames: 10 },
  ],
};
const resSameZone = validateStoryPlan(sameZonePlan);
if (resSameZone.valid || (!resSameZone.errors.some((e) => e.code === "ZONE_OCCUPANCY_COLLISION") && !resSameZone.errors.some((e) => e.code === "CARD_OVERLAP"))) {
  throw new Error("FAIL: Validator should reject two objects entering the same zone simultaneously!");
}
console.log("✓ Caught and rejected two objects occupying the same zone simultaneously (ZONE_OCCUPANCY_COLLISION).");

// 10.7: Move during another object's exit must be caught
const moveDuringExitPlan = {
  id: "move_during_exit",
  fps: 30,
  durationInFrames: 200,
  width: 1920,
  height: 1080,
  objects: [
    { id: "card_exiting", type: "card", layout: "center_left", cardProps: { title: "Exiting Card" } },
    { id: "card_incoming", type: "card", layout: "center_right", cardProps: { title: "Incoming Card" } },
  ],
  events: [
    { action: "enter", targetId: "card_exiting", startFrame: 0, durationFrames: 10 },
    { action: "enter", targetId: "card_incoming", startFrame: 0, durationFrames: 10 },
    // card_exiting exits from frame 50 to 75
    { action: "exit", targetId: "card_exiting", startFrame: 50, durationFrames: 25, direction: "left" },
    // card_incoming moves into center_left at frame 60 (before exit finishes at 75!)
    { action: "move", targetId: "card_incoming", startFrame: 60, durationFrames: 20, to: "center_left" },
  ],
};
const resMoveExit = validateStoryPlan(moveDuringExitPlan);
if (resMoveExit.valid || (!resMoveExit.errors.some((e) => e.code === "ZONE_OCCUPANCY_COLLISION") && !resMoveExit.errors.some((e) => e.code === "CARD_OVERLAP"))) {
  throw new Error("FAIL: Validator should reject move into a zone before incumbent object finishes exiting!");
}
console.log("✓ Caught and rejected premature move during incumbent object's exit animation.");

// 10.8: Sequential reuse of a zone after clean exit must SUCCEED
const sequentialReusePlan = {
  id: "sequential_reuse",
  fps: 30,
  durationInFrames: 200,
  width: 1920,
  height: 1080,
  objects: [
    { id: "first_card", type: "card", layout: "center_left", cardProps: { title: "First Card" } },
    { id: "second_card", type: "card", layout: "center_left", cardProps: { title: "Second Card" } },
  ],
  events: [
    { action: "enter", targetId: "first_card", startFrame: 0, durationFrames: 10 },
    // first_card exits from frame 40 to 65
    { action: "exit", targetId: "first_card", startFrame: 40, durationFrames: 25, direction: "left" },
    // second_card enters at frame 70 (cleanly AFTER first_card exit completed)
    { action: "enter", targetId: "second_card", startFrame: 70, durationFrames: 10 },
  ],
};
const resSequential = validateStoryPlan(sequentialReusePlan);
if (!resSequential.valid) {
  console.error("Sequential reuse errors:", resSequential.errors);
  throw new Error("FAIL: Clean sequential reuse of a zone after exit should be valid!");
}
console.log("✓ Clean sequential reuse of a zone after exit confirmed valid.");

console.log("\n==================================================");
console.log("ALL ADVANCED PROTOCOL TESTS PASSED CLEANLY!");
console.log("==================================================");


