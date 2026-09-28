import json
import sqlite3
import os
from pathlib import Path
from dataclasses import asdict

from artifact_store.sqlite_store import ArtifactStore
from domain.hook import Hook
from domain.script_visual_strategy import ScriptVisualStrategy
from domain.research_packet import ResearchPacket
from domain.narrative_plan import NarrativePlan
from domain.validation import ValidationResult
from domain.visual_intent_artifact import (
    VisualIntentArtifact,
    build_visual_intent_provenance,
)
from engines.visual_intent_engine import VisualIntentEngine
from engines.composition_selector import select_composition_for_intent
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

    project_id = "project_2b0c28fc64c744cc84c5b66a2b23053b"
    run_id = "run_42ad7757020045fabe74b7d3e04539af"

    # 2. Fetch artifacts from DB
    store = ArtifactStore("backend/.data/ytcreate_v2.db")

    research_artifact = store.require_artifact(project_id, run_id, "research_packet", for_stage="visual_intent")
    research_packet = ResearchPacket.model_validate(research_artifact.payload_json)

    narrative_artifact = store.require_artifact(project_id, run_id, "narrative_plan", for_stage="visual_intent")
    narrative_plan = NarrativePlan.model_validate(narrative_artifact.payload_json)

    hook_artifact = store.require_artifact(project_id, run_id, "hook", for_stage="visual_intent")
    hook = Hook.model_validate(hook_artifact.payload_json)

    strategy_artifact = store.require_artifact(project_id, run_id, "script_visual_strategy", for_stage="visual_intent")
    strategy = ScriptVisualStrategy.model_validate(strategy_artifact.payload_json)

    print(f"Loaded Research: {research_packet.topic}")
    print(f"Loaded Hook: {len(hook.script_text.split())} words")
    print(f"Loaded Strategy: {len(strategy.ideas)} body scenes")

    # 3. Instantiate Engine with Gemini
    gemini = GeminiProvider(
        api_key=os.environ["GEMINI_API_KEY"],
        model=os.environ.get("GEMINI_MODEL", "gemini-3.5-flash-lite"),
    )
    engine = VisualIntentEngine(llm_provider=gemini)

    sequences = []
    provenance = []
    provider_metadata = []

    # 4. Run on Hook
    print("\n" + "=" * 80)
    print("RUNNING STAGE 5: HOOK")
    print("=" * 80)
    hook_res = engine.run(
        idea_id="hook",
        narration=hook.script_text,
        topic=research_packet.topic,
        audience=research_packet.audience,
        is_hook=True,
        scene_role="hook",
        viewer_question=hook.conceptual_hook,
        focus_concept="Attention Capture & Core Tension",
        core_teaching_point="Engage the viewer immediately and establish the core curiosity gap.",
        key_evidence=["Gold hit all-time high of ₹1,50,000."],
    )
    sequences.append(hook_res.sequence)
    provenance.extend(build_visual_intent_provenance(hook_res.sequence, source_kind="hook"))
    provider_metadata.append(asdict(hook_res.provider_metadata))

    print(f"Hook generated {len(hook_res.sequence.intents)} visual beats:")
    for intent in hook_res.sequence.intents:
        comp_id = select_composition_for_intent(intent)
        print(f"  [{intent.intent_id}] Trigger: {intent.trigger_word!r:15} | Rel: {intent.relationship_type:12} | Mode: {intent.evidence_mode:16} | Comp: {comp_id}")
        print(f"       Understand: {intent.what_viewer_must_understand}")

    # 5. Run on all 7 Body Scenes
    for idx, idea in enumerate(strategy.ideas):
        print("\n" + "=" * 80)
        print(f"RUNNING STAGE 5: SCENE {idx+1}/{len(strategy.ideas)} ({idea.idea_id}) — Role: {idea.scene_role}")
        print("=" * 80)
        idea_res = engine.run(
            idea_id=idea.idea_id,
            narration=idea.narration,
            topic=research_packet.topic,
            audience=research_packet.audience,
            is_hook=False,
            scene_role=idea.scene_role,
            viewer_question=idea.viewer_question,
            focus_concept=idea.focus_concept,
            core_teaching_point=idea.core_teaching_point,
            key_evidence=idea.key_evidence,
        )
        sequences.append(idea_res.sequence)
        provenance.extend(build_visual_intent_provenance(idea_res.sequence, source_kind="idea"))
        provider_metadata.append(asdict(idea_res.provider_metadata))

        diag = idea_res.pacing_diagnostic or {}
        print(f"{idea.idea_id} generated {len(idea_res.sequence.intents)} beats (words: {diag.get('word_count', 0)}, target: {diag.get('target_beats_min', 0)}-{diag.get('target_beats_max', 0)}):")
        for intent in idea_res.sequence.intents:
            comp_id = select_composition_for_intent(intent)
            print(f"  [{intent.intent_id}] Trigger: {intent.trigger_word!r:15} | Rel: {intent.relationship_type:12} | Mode: {intent.evidence_mode:16} | Comp: {comp_id}")
            print(f"       Understand: {intent.what_viewer_must_understand}")

    # 6. Save VisualIntentArtifact into SQLite
    intent_artifact = VisualIntentArtifact(
        sequences=sequences,
        provenance=provenance,
        provider_metadata=provider_metadata,
    )
    saved = store.save_artifact(
        project_id=project_id,
        run_id=run_id,
        artifact_type="visual_intent",
        schema_version=intent_artifact.schema_version,
        payload_json=intent_artifact.model_dump(),
        parent_artifact_roles_json={
            "hook": hook_artifact.id,
            "narrative_plan": narrative_artifact.id,
            "research_packet": research_artifact.id,
            "script_visual_strategy": strategy_artifact.id,
        },
        validation_json=ValidationResult(status="valid"),
    )

    print("\n" + "=" * 80)
    print(f"SUCCESS: Saved VisualIntentArtifact {saved.id} into database!")
    total_beats = sum(len(seq.intents) for seq in sequences)
    print(f"Total Sequences: {len(sequences)} (1 Hook + {len(strategy.ideas)} Scenes)")
    print(f"Total Visual Beats: {total_beats}")
    print("=" * 80)


if __name__ == "__main__":
    main()
