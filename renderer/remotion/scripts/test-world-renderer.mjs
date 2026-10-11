import assert from "node:assert/strict";
import { loanCompiledWorld } from "../src/world/loanCompiledWorldFixture.ts";
import {
  assertWorldRendererContract,
  getVisiblePrimitiveIds,
  isPrimitiveVisible,
  resolvePrimitiveFrameState,
} from "../src/runtime.ts";

assertWorldRendererContract(loanCompiledWorld);

assert.equal(loanCompiledWorld.world_id, "loan_world");
assert.equal(loanCompiledWorld.total_duration_frames, 120);
assert.deepEqual(
  loanCompiledWorld.beat_intervals.map((beat) => [beat.beat_id, beat.start_frame, beat.end_frame]),
  [
    ["establish", 0, 60],
    ["rate_change", 60, 84],
    ["emi_change", 84, 114],
  ],
);

for (const frame of [0, 3, 20, 66, 75, 90, 110, 114, 119]) {
  const visible = new Set(getVisiblePrimitiveIds(loanCompiledWorld, frame));
  assert.equal(visible.has("loan_panel"), frame >= 3, `loan panel visibility at frame ${frame}`);
  if (frame >= 3) {
    assert.ok(visible.has("rate"), `rate remains visible at frame ${frame}`);
    assert.ok(visible.has("emi"), `EMI remains visible at frame ${frame}`);
  }
}

const rate = loanCompiledWorld.primitives.rate;
const emi = loanCompiledWorld.primitives.emi;
assert.equal(resolvePrimitiveFrameState(loanCompiledWorld, rate, 66).props.value, 8.5);
assert.equal(resolvePrimitiveFrameState(loanCompiledWorld, rate, 75).props.value, 9.4);
assert.equal(resolvePrimitiveFrameState(loanCompiledWorld, emi, 90).props.value, 43391);
assert.equal(resolvePrimitiveFrameState(loanCompiledWorld, emi, 110).props.value, 49919);
assert.equal(resolvePrimitiveFrameState(loanCompiledWorld, rate, 119).props.value, 10.5);
assert.equal(resolvePrimitiveFrameState(loanCompiledWorld, emi, 119).props.value, 49919);
assert.equal(loanCompiledWorld.animation_tracks.every((track) => track.easing === "linear"), true);

const ledgerOnlyChange = structuredClone(loanCompiledWorld);
ledgerOnlyChange.state_tracks.find((track) => track.object_id === "rate").changes[0].to_value = 99;
assert.equal(resolvePrimitiveFrameState(ledgerOnlyChange, rate, 75).props.value, 9.4);

const compiledEase = structuredClone(loanCompiledWorld);
compiledEase.animation_tracks.find((track) => track.animation_id === "rate_to_high").easing = "ease-out";
assert.ok(resolvePrimitiveFrameState(compiledEase, rate, 75).props.value > 9.4);

assert.deepEqual(
  loanCompiledWorld.animation_tracks.map((track) => [
    track.animation_id,
    track.object_id,
    track.trigger_frame,
    track.target_property,
    track.from_value,
    track.to_value,
  ]),
  [
    ["reveal_loan", "loan_panel", 3, "opacity", 0, 1],
    [
      "move_loan_panel",
      "loan_panel",
      30,
      "layout",
      { x: 355.2, y: 190.4, width: 1209.6, height: 699.2 },
      { x: 650, y: 190.4, width: 1209.6, height: 699.2 },
    ],
    ["rate_to_high", "rate", 66, "value", 8.5, 10.5],
    ["emi_to_high", "emi", 90, "value", 43391, 49919],
  ],
);

const panel = loanCompiledWorld.primitives.loan_panel;
const metrics = loanCompiledWorld.primitives.metrics_group;
assert.equal(panel.parent_object_id, null);
assert.equal(metrics.parent_object_id, "loan_panel");
assert.equal(metrics.local_geometry.x, 477.2);
assert.equal(rate.parent_object_id, "metrics_group");
assert.equal(rate.local_geometry.x, 8);
assert.notEqual(rate.local_geometry.x, panel.local_geometry.x + metrics.local_geometry.x);
assert.deepEqual(panel.child_object_ids, ["loan_surface", "metrics_group", "rate_to_emi"]);
assert.deepEqual(metrics.child_object_ids, ["rate", "emi"]);

const connector = loanCompiledWorld.primitives.rate_to_emi;
assert.equal(connector.connector_path.parent_object_id, "loan_panel");
assert.deepEqual(connector.connector_path.points, [
  { x: 574.48, y: 53.6 },
  { x: 582.48, y: 53.6 },
  { x: 582.48, y: 53.6 },
  { x: 590.48, y: 53.6 },
]);
assert.deepEqual(connector.properties, { has_arrow: true });
assert.equal(Object.hasOwn(connector.properties, "target_id"), false);

assert.deepEqual(loanCompiledWorld.primitives.loan_panel.properties, {});
assert.equal(loanCompiledWorld.primitives.loan_panel.style.fill, null);
assert.equal(loanCompiledWorld.primitives.loan_surface.primitive_type, "shape");
assert.equal(loanCompiledWorld.terminal_hold.start_frame, 114);
assert.equal(loanCompiledWorld.terminal_hold.end_frame, 120);

console.log("WorldRenderer isolated fixture checks passed.");
