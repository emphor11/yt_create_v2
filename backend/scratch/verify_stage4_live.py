import json
import sqlite3
import os
from pathlib import Path

from domain.hook import Hook
from domain.narrative_plan import NarrativePlan
from domain.research_packet import ResearchPacket
from domain.validators.script_visual_strategy_validator import ScriptVisualStrategyValidator
from engines.script_visual_strategy_engine import ScriptVisualStrategyEngine
from providers.gemini_provider import GeminiProvider


def main():
    # 1. Load .env
    env_path = Path("backend/.env")
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

    # 2. Fetch artifacts from DB
    conn = sqlite3.connect("backend/.data/ytcreate_v2.db")
    cursor = conn.cursor()

    cursor.execute("SELECT payload_json FROM artifacts WHERE id = 'artifact_631ce278d5c146a285a57eb7b1c337a7'")
    research_packet = ResearchPacket.model_validate(json.loads(cursor.fetchone()[0]))

    cursor.execute("SELECT payload_json FROM artifacts WHERE id = 'artifact_036d5390b52d487e8ecd6e827e9d6116'")
    narrative_plan = NarrativePlan.model_validate(json.loads(cursor.fetchone()[0]))

    cursor.execute("SELECT payload_json FROM artifacts WHERE id = 'artifact_5721224de3a84295963bfe1f7bd8ba74'")
    hook = Hook.model_validate(json.loads(cursor.fetchone()[0]))

    print(f"Loaded Research: {research_packet.topic}")
    print(f"Loaded Narrative Plan: {len(narrative_plan.scene_beats)} scenes")
    print(f"Loaded Hook: {len(hook.script_text.split())} words")

    # 3. Instantiate Engine
    gemini = GeminiProvider(
        api_key=os.environ["GEMINI_API_KEY"],
        model=os.environ.get("GEMINI_MODEL", "gemini-3.5-flash-lite"),
    )
    engine = ScriptVisualStrategyEngine(llm_provider=gemini)
    validator = ScriptVisualStrategyValidator()

    # 4. Run Stage 4 Engine
    print("\nRunning ScriptVisualStrategyEngine with production prompt...")
    result = engine.run(
        research_packet=research_packet,
        narrative_plan=narrative_plan,
        hook=hook,
        duration_profile="long_5min",
    )

    strategy = result.strategy
    validation = validator.validate(strategy)

    print("\n" + "=" * 60)
    print("STAGE 4 PRODUCTION RUN RESULTS")
    print("=" * 60)
    print(f"Validation Status: {validation.status}")
    print(f"Validation Errors: {validation.errors}")
    print(f"Validation Warnings: {validation.warnings}")
    print(f"Thesis: {strategy.thesis}")
    print(f"Total Scenes: {len(strategy.ideas)}")

    total_words = 0
    for idx, idea in enumerate(strategy.ideas, 1):
        words = len(idea.narration.split())
        total_words += words
        print(f"\n--- Scene {idx:02d}: {idea.title} ({words} words) ---")
        print(f"Scene Role: {idea.scene_role}")
        print(f"Viewer Question: {idea.viewer_question}")
        print(f"Focus Concept: {idea.focus_concept}")
        print(f"Core Teaching Point: {idea.core_teaching_point}")
        print(f"Key Evidence: {idea.key_evidence}")
        print(f"Narration:\n  \"{idea.narration}\"")

    hook_words = len(hook.script_text.split())
    grand_total = hook_words + total_words
    print("\n" + "=" * 60)
    print(f"Total Body Words: {total_words}")
    print(f"Hook Words: {hook_words}")
    print(f"Grand Total Script Words: {grand_total} (~{grand_total / 2.4:.1f} seconds / ~{grand_total / 2.4 / 60:.1f} minutes)")
    print("=" * 60)

    # Save output to scratch for audit
    output_data = {
        "strategy": strategy.model_dump(),
        "validation": validation.model_dump(),
        "metadata": result.provider_metadata.__dict__ if hasattr(result.provider_metadata, "__dict__") else str(result.provider_metadata),
    }
    Path("backend/scratch/stage4_live_output.json").write_text(json.dumps(output_data, indent=2))
    print("\nSaved output to backend/scratch/stage4_live_output.json")


if __name__ == "__main__":
    main()
