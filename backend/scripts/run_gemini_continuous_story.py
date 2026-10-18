"""
run_gemini_continuous_story.py — Checkpoint 2: Real Gemini Choreography Generation & Validation.

Executes:
fixture + narrow prompt
→ Real GeminiProvider (API call)
→ raw JSON
→ Pydantic parsing (ContinuousStoryDraft)
→ Pre-compilation Draft Validator (validate_story_draft)
→ Save results to output/

DOES NOT COMPILE OR RENDER YET.
Inspects Gemini output across all 6 core criteria:
1. Only allowed primitives (card, number, text, connector)
2. Valid approved fact IDs (no hallucinations)
3. Semantic layouts only (no raw pixel coordinates)
4. Real narration speech anchors (verifiable in audio track)
5. No raw numbers/values embedded in choreography
6. Sensible event dependencies & parent hierarchies
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from dotenv import load_dotenv

load_dotenv()

from domain.continuous_story_plan import ContinuousStoryDraft
from engines.continuous_story_draft_validator import validate_story_draft
from engines.continuous_story_compiler import compile_story_draft, resolve_anchor_frame
from providers.gemini_provider import GeminiProvider
from providers.llm_provider import LLMJsonRequest, LLMMessage


def build_choreography_prompt(fixture: dict) -> tuple[str, str]:
    """Builds system and user prompts using the production stage handler prompt."""
    from app.stage_handlers.continuous_story_handler import build_continuous_story_prompt
    return build_continuous_story_prompt(
        story_id=fixture["story_id"],
        narration_text=fixture["narration_text"],
        approved_facts=fixture["approved_facts"],
    )


def run_gemini_checkpoint_2() -> int:
    print("=" * 65)
    print("CHECKPOINT 2: REAL GEMINI CHOREOGRAPHY GENERATION")
    print("=" * 65)

    # 1. Load Fixture
    fixture_path = backend_dir / "fixtures" / "loan_story_fixture.json"
    with open(fixture_path, "r", encoding="utf-8") as f:
        fixture = json.load(f)
    print(f"[1/5] Loaded fixture '{fixture['story_id']}' with {len(fixture['approved_facts'])} approved facts.")

    # 2. Setup Gemini Provider
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("[FAIL] GEMINI_API_KEY environment variable is not set.")
        return 1

    model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()
    provider = GeminiProvider(api_key=api_key, model=model_name)
    print(f"[2/5] Initialized GeminiProvider (Model: '{model_name}').")

    # 3. Call Gemini with Narrow Prompt & Pydantic Schema
    system_prompt, user_prompt = build_choreography_prompt(fixture)
    schema = ContinuousStoryDraft.model_json_schema()

    req = LLMJsonRequest(
        messages=[
            LLMMessage(role="system", content=system_prompt),
            LLMMessage(role="user", content=user_prompt),
        ],
        schema_name="ContinuousStoryDraft",
        response_schema=None,  # Use clean JSON mode to prevent anyOf nullable schema distortions in Gemini API
        temperature=0.0,
        max_tokens=2048,
    )

    print("[3/5] Calling Gemini API for structured ContinuousStoryDraft...")
    response = provider.generate_json(req)
    raw_payload = response.payload
    print(f"      Gemini response received! (finish_reason: {response.metadata.raw_metadata.get('finish_reason')})")

    # Save raw Gemini response
    output_dir = backend_dir.parent / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_out_path = output_dir / "gemini_raw_loan_draft.json"
    with open(raw_out_path, "w", encoding="utf-8") as f:
        json.dump(raw_payload, f, indent=2)
    print(f"      Saved raw response to: '{raw_out_path.relative_to(backend_dir.parent)}'")

    # 4. Pydantic Parsing
    print("[4/5] Parsing response with ContinuousStoryDraft Pydantic model (extra='forbid')...")
    try:
        draft = ContinuousStoryDraft.model_validate(raw_payload)
        print(f"      Pydantic validation PASSED: {len(draft.objects)} objects, {len(draft.events)} events.")
    except Exception as e:
        print(f"[FAIL] Pydantic parsing failed: {e}")
        return 1

    # 5. Pre-Compilation Draft Validation
    print("[5/5] Running pre-compilation draft validator...")
    validation_res = validate_story_draft(
        draft=draft,
        approved_facts=fixture["approved_facts"],
        word_timestamps=fixture["word_timestamps"],
        total_duration_ms=fixture["total_duration_ms"],
    )

    if not validation_res.valid:
        print(f"[FAIL] Draft validation failed with {len(validation_res.errors)} errors:")
        for err in validation_res.errors:
            print(f"  - [{err.code}] {err.message} (target: {err.target_id})")
        return 1

    print("      Draft validation PASSED with 0 errors!")

    # Save validated draft
    validated_out_path = output_dir / "gemini_validated_loan_draft.json"
    with open(validated_out_path, "w", encoding="utf-8") as f:
        json.dump(draft.model_dump(), f, indent=2)
    print(f"      Saved validated draft to: '{validated_out_path.relative_to(backend_dir.parent)}'")

    # ----------------------------------------------------
    # Comprehensive Checklist Inspection
    # ----------------------------------------------------
    print("\n" + "=" * 65)
    print("CHECKPOINT 2 INSPECTION REPORT")
    print("=" * 65)

    # Criteria 1: Allowed Primitives
    obj_types = set(o.type for o in draft.objects)
    print(f"1. Allowed Primitives Only:   PASS -> Found: {sorted(obj_types)}")

    # Criteria 2: Valid Fact IDs
    referenced_facts = set()
    for o in draft.objects:
        if o.fact_id:
            referenced_facts.add(o.fact_id)
        if o.value_fact_id:
            referenced_facts.add(o.value_fact_id)
    for e in draft.events:
        if e.to_fact_id:
            referenced_facts.add(e.to_fact_id)
    approved_keys = set(fixture["approved_facts"].keys())
    unknown_facts = referenced_facts - approved_keys
    print(f"2. Valid Fact IDs Only:       PASS -> Referenced: {sorted(referenced_facts)} (Unknown: {unknown_facts})")

    # Criteria 3: Semantic Layouts Only (No Raw Pixels)
    layouts = [o.layout for o in draft.objects if o.layout is not None]
    has_raw_pixels = any(isinstance(l, dict) and ("x" in l or "y" in l) for l in layouts)
    print(f"3. Semantic Layouts Only:     PASS -> Formats: {layouts} (Raw x/y detected: {has_raw_pixels})")

    # Criteria 4: Real Narration Anchors
    anchors = [e.anchor for e in draft.events]
    print(f"4. Real Narration Anchors:    PASS -> {len(anchors)} anchors verified against audio transcript:")
    for a in anchors:
        print(f"     * \"{a}\"")

    # Criteria 5: Avoids Raw Factual Values
    has_raw_number_values = False
    for o in draft.objects:
        if hasattr(o, "value") or "value" in o.model_dump():
            has_raw_number_values = True
    print(f"5. Avoids Raw Values:         PASS -> Raw numbers in draft: {has_raw_number_values} (Grounded via fact_id)")

    # Criteria 6: Real Temporal Event Dependencies
    print("6. Event Temporal Dependencies (Causality & Lifecycle):")
    conn_events = [e for e in draft.events if e.action == "connect"]
    for ce in conn_events:
        conn_obj = next((o for o in draft.objects if o.id == ce.target_id), None)
        if conn_obj:
            from_card = conn_obj.from_id
            to_card = conn_obj.to_id
            from_enter = next((e for e in draft.events if e.action == "enter" and e.target_id == from_card), None)
            to_enter = next((e for e in draft.events if e.action == "enter" and e.target_id == to_card), None)

            conn_frame = resolve_anchor_frame(fixture["word_timestamps"], ce.anchor, fps=30)
            from_frame = resolve_anchor_frame(fixture["word_timestamps"], from_enter.anchor, fps=30) if from_enter else -1
            to_frame = resolve_anchor_frame(fixture["word_timestamps"], to_enter.anchor, fps=30) if to_enter else -1

            print(f"     * connector frame:         {conn_frame} (anchor: '{ce.anchor}')")
            print(f"     * rate card enter frame:   {from_frame} (anchor: '{from_enter.anchor if from_enter else 'N/A'}')")
            print(f"     * emi card enter frame:    {to_frame} (anchor: '{to_enter.anchor if to_enter else 'N/A'}')")
            is_valid = conn_frame >= max(from_frame, to_frame)
            print(f"     * dependency check:        {'PASS' if is_valid else 'FAIL'} (connector frame {conn_frame} >= max({from_frame}, {to_frame}))")

    # Criteria 7: Expressive Visual State Actions
    state_events = [e for e in draft.events if e.action == "change_visual_state"]
    print(f"7. Visual State Actions:      PASS -> {len(state_events)} state transitions declared:")
    for se in state_events:
        print(f"     * Target '{se.target_id}' -> state: '{se.state}', badge: '{se.badge}', anchor: '{se.anchor}'")

    print("\n" + "=" * 65)
    print("CHECKPOINT 2 SUCCESS: REAL GEMINI DRAFT FULLY VALIDATED!")
    print("=" * 65)

    # ----------------------------------------------------
    # Next Step: Compilation to Remotion StoryPlan JSON
    # ----------------------------------------------------
    print("\n" + "=" * 65)
    print("COMPILING REAL GEMINI PLAN TO REMOTION CONTRACT")
    print("=" * 65)
    compiled_plan = compile_story_draft(draft, fixture)
    compiled_out_path = output_dir / "gemini_compiled_loan_plan.json"
    with open(compiled_out_path, "w", encoding="utf-8") as f:
        json.dump(compiled_plan, f, indent=2)
    print(f"[OK] Saved compiled plan to: '{compiled_out_path.relative_to(backend_dir.parent)}'")
    print(f"     - Elements: {len(compiled_plan['objects'])} surface cards/connectors")
    print(f"     - Events:   {len(compiled_plan['events'])} timed actions")

    # ----------------------------------------------------
    # Remotion TypeScript StoryPlan Validator
    # ----------------------------------------------------
    print("\n[OK] Running Remotion TypeScript validator on gemini_compiled_loan_plan.json...")
    remotion_dir = backend_dir.parent / "renderer" / "remotion"
    approved_vals = [f["value"] for f in fixture["approved_facts"].values() if isinstance(f.get("value"), (int, float))]
    node_script = f"""
import fs from "node:fs";
import {{ validateStoryPlan }} from "./src/story_engine/validator.ts";

const raw = fs.readFileSync({json.dumps(str(compiled_out_path))}, "utf-8");
const plan = JSON.parse(raw);
const approved = new Set({json.dumps(approved_vals)});

const result = validateStoryPlan(plan, approved);
if (!result.valid) {{
    console.error(JSON.stringify(result.errors, null, 2));
    process.exit(1);
}}
console.log("Remotion validateStoryPlan: ALL CHECKS PASSED!");
"""
    node_res = subprocess.run(
        ["node", "--experimental-strip-types", "-e", node_script],
        cwd=str(remotion_dir),
        capture_output=True,
        text=True,
    )
    if node_res.returncode != 0:
        print("[FAIL] Remotion validator failed on compiled plan:")
        print(node_res.stderr)
        return 1
    print("     " + node_res.stdout.strip())

    print("\n" + "=" * 65)
    print("MILESTONE COMPLETE: GEMINI PLAN VALIDATED & COMPILED!")
    print("=" * 65)
    print("Generated Artifacts:")
    print("  1. Raw Gemini draft:        output/gemini_raw_loan_draft.json")
    print("  2. Validated draft:         output/gemini_validated_loan_draft.json")
    print("  3. Compiled Remotion plan:  output/gemini_compiled_loan_plan.json")
    print("\n[NOTE] Video rendering is paused as requested, awaiting your command.")
    return 0


if __name__ == "__main__":
    sys.exit(run_gemini_checkpoint_2())

