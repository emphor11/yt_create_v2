import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import {
  assertWorldRendererContract,
  getVisiblePrimitiveIds,
  resolvePrimitiveFrameState,
} from "../src/world/runtime.ts";

const worldPath = path.resolve("test-renders/salary_compiled_world.json");
const world = JSON.parse(fs.readFileSync(worldPath, "utf8"));

console.log("Validating runtime contract for real world:", world.world_id);
assertWorldRendererContract(world);
console.log("assertWorldRendererContract PASSED!");

const testFrames = [
  { frame: 10, label: "beat_01 beginning" },
  { frame: 65, label: "first raise action" },
  { frame: 950, label: "beat_02 salary comparison" },
  { frame: 2600, label: "beat_03 fixed cost" },
  { frame: 3400, label: "beat_04 rent" },
  { frame: 4000, label: "beat_05 inflation" },
  { frame: 5200, label: "beat_06 taxation" },
  { frame: 6500, label: "beat_07 savings" },
  { frame: 7920, label: "beat_08 conclusion" },
  { frame: 8003, label: "terminal hold" },
];

for (const { frame, label } of testFrames) {
  const visible = getVisiblePrimitiveIds(world, frame);
  console.log(`Frame ${frame} (${label}): ${visible.length} visible primitives: ${visible.join(", ")}`);
  for (const id of visible) {
    const primitive = world.primitives[id];
    const state = resolvePrimitiveFrameState(world, primitive, frame);
    assert(state.opacity >= 0 && state.opacity <= 1, `Invalid opacity at frame ${frame} for ${id}`);
  }
}

console.log("ALL RUNTIME STATE CHECKS PASSED!");
