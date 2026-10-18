"""
run_continuous_story.py — Vertical Slice Runner (Checkpoint 1).

Executes the initial vertical slice:
1. Loads approved story fixture (narration, audio metadata, approved facts, word timestamps).
2. Invokes FakeStoryLLMProvider (implements LLMProvider protocol) to produce the draft JSON.
3. Parses with Pydantic schema (ContinuousStoryDraft) with extra='forbid' & RelativeLayout.
4. Validates draft pre-compilation (validate_story_draft).
5. Compiles draft deterministically (compile_story_draft).
6. Writes output to output/loan_ai_story_plan.json.
7. Executes Remotion StoryPlan validator (renderer/remotion/src/story_engine/validator.ts).
"""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

# Ensure backend root is on Python path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from domain.continuous_story_plan import ContinuousStoryDraft
from engines.continuous_story_draft_validator import validate_story_draft
from engines.continuous_story_compiler import compile_story_draft
from providers.llm_provider import LLMJsonRequest, LLMJsonResponse, LLMMessage, LLMProviderMetadata


class FakeStoryLLMProvider:
    """
    Fake LLM Provider conforming to the LLMProvider protocol.
    Returns the canned AI choreography draft for the loan story.
    """

    def __init__(self, canned_draft: dict[str, any]) -> None:
        self.canned_draft = canned_draft

    def generate_json(self, request: LLMJsonRequest) -> LLMJsonResponse:
        return LLMJsonResponse(
            payload=self.canned_draft,
            metadata=LLMProviderMetadata(
                provider="fake_provider",
                model="fake-gemini-2.5-flash",
                raw_metadata={"purpose": "checkpoint_1_verification"},
            ),
        )


def get_fake_loan_draft() -> dict[str, any]:
    """Returns the targeted loan rate hike draft."""
    return {
        "story_id": "loan_rate_hike",
        "objects": [
            {
                "id": "card_loan",
                "type": "card",
                "purpose": "Home loan principal card",
                "layout": "center",
            },
            {
                "id": "num_loan",
                "type": "number",
                "purpose": "Principal amount",
                "parent_id": "card_loan",
                "fact_id": "loan_principal",
            },
            {
                "id": "card_rate",
                "type": "card",
                "purpose": "Interest rate card",
                "layout": {"right_of": "card_loan", "gap": 80},
            },
            {
                "id": "num_rate",
                "type": "number",
                "purpose": "Interest rate percentage",
                "parent_id": "card_rate",
                "fact_id": "rate_baseline",
            },
            {
                "id": "card_emi",
                "type": "card",
                "purpose": "Monthly EMI burden",
                "layout": {"below": "card_loan", "gap": 70},
            },
            {
                "id": "num_emi",
                "type": "number",
                "purpose": "Monthly EMI value",
                "parent_id": "card_emi",
                "fact_id": "emi_baseline",
            },
            {
                "id": "connector_rate_to_emi",
                "type": "connector",
                "purpose": "Drives payment",
                "from_id": "card_rate",
                "to_id": "card_emi",
            },
        ],
        "events": [
            {
                "action": "enter",
                "target_id": "card_loan",
                "anchor": "50 lakh",
            },
            {
                "action": "move",
                "target_id": "card_loan",
                "anchor": "starts at",
                "to": "left",
            },
            {
                "action": "enter",
                "target_id": "card_rate",
                "anchor": "8.5 percent",
            },
            {
                "action": "enter",
                "target_id": "card_emi",
                "anchor": "the monthly EMI",
            },
            {
                "action": "connect",
                "target_id": "connector_rate_to_emi",
                "anchor": "benchmark rate",
            },
            {
                "action": "transform_number",
                "target_id": "num_rate",
                "anchor": "rises to 10.5",
                "to_fact_id": "rate_high",
            },
            {
                "action": "transform_number",
                "target_id": "num_emi",
                "anchor": "surges to 49,919",
                "to_fact_id": "emi_high",
            },
        ],
    }


def validate_with_remotion(compiled_plan_path: Path, approved_values: list[float | int]) -> bool:
    """Invokes Remotion's TypeScript validation engine via Node subprocess."""
    remotion_dir = backend_dir.parent / "renderer" / "remotion"
    node_script = f"""
import fs from "node:fs";
import {{ validateStoryPlan }} from "./src/story_engine/validator.ts";

const raw = fs.readFileSync({json.dumps(str(compiled_plan_path))}, "utf-8");
const plan = JSON.parse(raw);
const approved = new Set({json.dumps(approved_values)});

const result = validateStoryPlan(plan, approved);
if (!result.valid) {{
    console.error(JSON.stringify(result.errors, null, 2));
    process.exit(1);
}}
console.log("Remotion validation passed without error.");
"""
    result = subprocess.run(
        ["node", "--experimental-strip-types", "-e", node_script],
        cwd=str(remotion_dir),
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print("[FAIL] Remotion validator reported errors:")
        print(result.stderr)
        return False
    return True


def run_pipeline() -> int:
    print("=" * 60)
    print("RUNNING CONTINUOUS STORY ENGINE — CHECKPOINT 1 SLICE")
    print("=" * 60)

    # 1. Load Fixture
    fixture_path = backend_dir / "fixtures" / "loan_story_fixture.json"
    if not fixture_path.exists():
        print(f"[FAIL] Fixture file missing at {fixture_path}")
        return 1
    with open(fixture_path, "r", encoding="utf-8") as f:
        fixture = json.load(f)
    print(f"Step 1: Loaded fixture '{fixture['story_id']}' ({len(fixture['approved_facts'])} approved facts, {len(fixture['word_timestamps'])} word timestamps).")

    # 2. Invoke Fake LLM Provider
    fake_provider = FakeStoryLLMProvider(canned_draft=get_fake_loan_draft())
    req = LLMJsonRequest(
        messages=[LLMMessage(role="user", content="Generate continuous story plan for home loan.")],
        schema_name="ContinuousStoryDraft",
    )
    res = fake_provider.generate_json(req)
    print(f"Step 2: Provider '{res.metadata.provider}' ({res.metadata.model}) generated raw draft payload.")

    # 3. Parse with strict Pydantic model
    try:
        draft = ContinuousStoryDraft.model_validate(res.payload)
        print(f"Step 3: Pydantic schema validation PASSED ({len(draft.objects)} objects, {len(draft.events)} events).")
    except Exception as e:
        print(f"[FAIL] Pydantic parsing failed: {e}")
        return 1

    # 4. Validate Draft Pre-Compilation
    validation_res = validate_story_draft(
        draft=draft,
        approved_facts=fixture["approved_facts"],
        word_timestamps=fixture["word_timestamps"],
        total_duration_ms=fixture["total_duration_ms"],
    )
    if not validation_res.valid:
        print(f"[FAIL] Draft validation failed with {len(validation_res.errors)} errors:")
        for err in validation_res.errors:
            print(f"  - [{err.code}] {err.message}")
        return 1
    print("Step 4: Draft pre-compilation validation PASSED (0 errors).")

    # 5. Deterministic Compilation
    try:
        compiled_plan = compile_story_draft(draft, fixture)
        print(f"Step 5: Deterministic compilation SUCCESS ({len(compiled_plan['objects'])} surface elements, {len(compiled_plan['events'])} timed events).")
    except Exception as e:
        print(f"[FAIL] Compiler failed: {e}")
        return 1

    # 6. Save output JSON
    output_path = backend_dir.parent / "output" / "loan_ai_story_plan.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(compiled_plan, f, indent=2)
    print(f"Step 6: Compiled plan successfully saved to '{output_path.relative_to(backend_dir.parent)}'.")

    # 7. Remotion StoryPlan Validator
    approved_values = [f["value"] for f in fixture["approved_facts"].values() if isinstance(f.get("value"), (int, float))]
    if not validate_with_remotion(output_path, approved_values):
        print("[FAIL] Remotion validator failed on compiled plan.")
        return 1
    print("Step 7: Remotion StoryPlan validator PASSED (geometry, safe margins, and provenance verified).")

    print("\n" + "=" * 60)
    print("CHECKPOINT 1 SUCCESS: VERTICAL SLICE FULLY OPERATIONAL!")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(run_pipeline())
