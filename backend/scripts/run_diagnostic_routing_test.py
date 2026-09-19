"""
Diagnostic test script: Nine Visual Relationships Routing Verification.

Creates a composition-mode diagnostic project with 9 body visual intents exercising:
1. metric -> MetricHero
2. calculation -> CalculationStory
3. cause_effect -> CauseEffect
4. multi_factor -> MultiFactorPressure
5. comparison -> ComparisonSplit
6. ranking -> RankedList
7. process -> ProcessFlow
8. decline -> TimeDecay
9. statement / broll -> BrollCaption

Runs stages:
- voice_generation
- video_assembly
- render

Reports:
1. Per-intent routing & fallback diagnostics (relationship_type, selected_composition, used_fallback, fallback_reason)
2. Final RenderSpec scene types in order
3. Composition distribution
4. Legacy body scenes count
5. Fallback count
"""
import os
import sys
import json
from pathlib import Path

backend_dir = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(backend_dir))

from app.dependencies import (
    get_artifact_store,
    get_media_storage,
    get_pipeline_service,
    get_llm_provider,
    _load_backend_dotenv,
)
from domain.generate_video_request import GenerateVideoRequest
from domain.research_packet import ResearchPacket
from domain.narrative_plan import NarrativePlan, SceneBeat
from domain.script_visual_strategy import ScriptVisualStrategy, VideoIdea
from domain.visual_intent import VisualIntent
from domain.composition_plan import FullCompositionPlan, IdeaCompositionPlan, CompositionBeat
from domain.validation import ValidationResult
from engines.composition_planner_engine import CompositionPlannerEngine


def main():
    _load_backend_dotenv()
    store = get_artifact_store()
    media_storage = get_media_storage()
    pipeline_service = get_pipeline_service()
    llm_provider = get_llm_provider()

    print("=" * 75)
    print("STARTING NINE RELATIONSHIPS DIAGNOSTIC ROUTING TEST")
    print("=" * 75)

    # 1. Create Project & Run
    project = store.create_project("Nine Relationships Diagnostic")
    run = store.create_run(project.id, mode="ai")
    print(f"Project ID: {project.id}")
    print(f"Run ID: {run.id}")

    # 2. Save GenerateVideoRequest
    gen_req = GenerateVideoRequest(
        topic="Nine Rules of Financial Architecture",
        angle="A definitive diagnostic test of semantic visual compositions",
        audience="retail investors and financial students",
        language="English",
        style="educational and rigorously structured",
        channel="FinanceMastery",
        duration_profile="short_2min",
        visual_mode="composition",
    )
    req_art = store.save_artifact(
        project_id=project.id,
        run_id=run.id,
        artifact_type="generate_video_request",
        schema_version=gen_req.schema_version,
        payload_json=gen_req.model_dump(),
        parent_artifact_roles_json={},
        validation_json=ValidationResult(status="valid"),
    )
    print(f"Saved generate_video_request: {req_art.id}")

    # 3. Save ResearchPacket
    concepts = [
        "Milestone Target",
        "Withdrawal Formula",
        "Lifestyle Inflation",
        "Converging Pressures",
        "Asset Comparison",
        "Expense Hierarchy",
        "Execution Workflow",
        "Purchasing Power Erosion",
        "Core Philosophy",
    ]
    research_packet = ResearchPacket(
        topic="Nine Rules of Financial Architecture",
        audience="retail investors and financial students",
        channel="FinanceMastery",
        concepts=concepts,
        verified_facts=[
            "fifty lakh is the standard retail benchmark",
            "four percent of fifty lakh equals two lakh annually",
        ],
        statistics=["60% of individuals face capital erosion"],
        misconceptions=["Fixed nominal amounts retain their value indefinitely"],
        examples=[],
        trusted_sources=["RBI", "SEBI"],
    )
    res_art = store.save_artifact(
        project_id=project.id,
        run_id=run.id,
        artifact_type="research_packet",
        schema_version="1",
        payload_json=research_packet.model_dump(),
        parent_artifact_roles_json={"generate_video_request": req_art.id},
        validation_json=ValidationResult(status="valid"),
    )
    print(f"Saved research_packet: {res_art.id}")

    # 4. Save NarrativePlan (9 ideas)
    ideas_meta = [
        {
            "idea_id": "idea_01",
            "title": "The Milestone Benchmark",
            "focus_concept": "Milestone Target",
            "core_teaching_point": "Opening portfolio benchmark.",
            "narration": "To establish financial independence, your starting net worth benchmark should reach fifty lakh rupees.",
            "intent": VisualIntent(
                intent_id="intent_01",
                narration_excerpt="To establish financial independence, your starting net worth benchmark should reach fifty lakh rupees.",
                what_viewer_must_understand="fifty lakh rupees is the starting milestone target.",
                key_values=["fifty lakh rupees"],
                relationship_type="metric",
                emphasis="hero",
                trigger_word=None,
            ),
        },
        {
            "idea_id": "idea_02",
            "title": "The Income Calculation",
            "focus_concept": "Withdrawal Formula",
            "core_teaching_point": "Annual income math.",
            "narration": "A four percent annual withdrawal on fifty lakh generates two lakh rupees of annual income.",
            "intent": VisualIntent(
                intent_id="intent_02",
                narration_excerpt="A four percent annual withdrawal on fifty lakh generates two lakh rupees of annual income.",
                what_viewer_must_understand="4% on fifty lakh produces two lakh rupees annual income.",
                key_values=["4%", "fifty lakh", "two lakh rupees"],
                relationship_type="calculation",
                trigger_word=None,
            ),
        },
        {
            "idea_id": "idea_03",
            "title": "The Causal Trap",
            "focus_concept": "Lifestyle Inflation",
            "core_teaching_point": "Causal link to savings collapse.",
            "narration": "Unchecked lifestyle inflation directly causes household savings to plunge to zero.",
            "intent": VisualIntent(
                intent_id="intent_03",
                narration_excerpt="Unchecked lifestyle inflation directly causes household savings to plunge to zero.",
                what_viewer_must_understand="Lifestyle inflation causes savings to drop to zero.",
                key_values=["lifestyle inflation", "zero"],
                relationship_type="cause_effect",
                trigger_word=None,
            ),
        },
        {
            "idea_id": "idea_04",
            "title": "The Convergence of Risk",
            "focus_concept": "Converging Pressures",
            "core_teaching_point": "Multi-factor converging forces.",
            "narration": "Surging healthcare costs, high inflation, and tax drag converge to create extreme retirement pressure.",
            "intent": VisualIntent(
                intent_id="intent_04",
                narration_excerpt="Surging healthcare costs, high inflation, and tax drag converge to create extreme retirement pressure.",
                what_viewer_must_understand="Three independent factors combine to threaten retirement capital.",
                key_values=["healthcare", "inflation", "tax drag"],
                relationship_type="multi_factor",
                trigger_word=None,
            ),
        },
        {
            "idea_id": "idea_05",
            "title": "The Asset Class Divergence",
            "focus_concept": "Asset Comparison",
            "core_teaching_point": "Side-by-side comparison.",
            "narration": "Comparing traditional fixed deposits at six percent versus equity index funds at twelve percent reveals a massive compounding gap.",
            "intent": VisualIntent(
                intent_id="intent_05",
                narration_excerpt="Comparing traditional fixed deposits at six percent versus equity index funds at twelve percent reveals a massive compounding gap.",
                what_viewer_must_understand="Equity funds at twelve percent outperform fixed deposits at six percent.",
                key_values=["6%", "12%"],
                relationship_type="comparison",
                trigger_word=None,
            ),
        },
        {
            "idea_id": "idea_06",
            "title": "The Expense Hierarchy",
            "focus_concept": "Expense Hierarchy",
            "core_teaching_point": "Ranked expense breakdown.",
            "narration": "Ranked by magnitude, housing rent consumes forty thousand rupees, followed by twenty thousand in car EMIs and ten thousand in lifestyle spending.",
            "intent": VisualIntent(
                intent_id="intent_06",
                narration_excerpt="Ranked by magnitude, housing rent consumes forty thousand rupees, followed by twenty thousand in car EMIs and ten thousand in lifestyle spending.",
                what_viewer_must_understand="Housing rent ranks first in expense size, followed by EMIs and lifestyle.",
                key_values=["forty thousand", "twenty thousand", "ten thousand"],
                relationship_type="ranking",
                trigger_word=None,
            ),
        },
        {
            "idea_id": "idea_07",
            "title": "The Accumulation Flow",
            "focus_concept": "Execution Workflow",
            "core_teaching_point": "Sequential process steps.",
            "narration": "The automated wealth process moves through four steps: earn income, budget savings, automate transfers, and reinvest dividends.",
            "intent": VisualIntent(
                intent_id="intent_07",
                narration_excerpt="The automated wealth process moves through four steps: earn income, budget savings, automate transfers, and reinvest dividends.",
                what_viewer_must_understand="Wealth compounding executes in four sequential stages.",
                key_values=["four steps"],
                relationship_type="process",
                trigger_word=None,
            ),
        },
        {
            "idea_id": "idea_08",
            "title": "The Depletion Curve",
            "focus_concept": "Purchasing Power Erosion",
            "core_teaching_point": "Purchasing power decline.",
            "narration": "Over twenty years, a fixed pension loses half its purchasing power under persistent price inflation.",
            "intent": VisualIntent(
                intent_id="intent_08",
                narration_excerpt="Over twenty years, a fixed pension loses half its purchasing power under persistent price inflation.",
                what_viewer_must_understand="Fixed pension loses fifty percent purchasing power over twenty years.",
                key_values=["twenty years", "fifty percent"],
                relationship_type="decline",
                emphasis="purchasing_power_decline",
                trigger_word=None,
            ),
        },
        {
            "idea_id": "idea_09",
            "title": "The Discipline Anchor",
            "focus_concept": "Core Philosophy",
            "core_teaching_point": "Philosophical takeaway.",
            "narration": "In the final analysis, enduring financial peace requires patient discipline rather than chasing speculative trends.",
            "intent": VisualIntent(
                intent_id="intent_09",
                narration_excerpt="In the final analysis, enduring financial peace requires patient discipline rather than chasing speculative trends.",
                what_viewer_must_understand="Patient discipline is the ultimate foundation of enduring financial peace.",
                key_values=[],
                relationship_type="statement",
                trigger_word=None,
            ),
        },
    ]

    scene_beats = [
        SceneBeat(
            scene_id=f"scene_{idx+1:02d}",
            title=item["title"],
            focus_concept=item["focus_concept"],
            core_teaching_point=item["core_teaching_point"],
        )
        for idx, item in enumerate(ideas_meta)
    ]
    narrative_plan = NarrativePlan(
        thesis="Sustainable wealth creation requires mastering metrics, calculations, causal risks, rankings, workflows, and decay dynamics.",
        target_pain_point="Lack of visual clarity on personal finance mechanics",
        conceptual_hook="The Nine Semantic Principles of Wealth",
        narrative_arc_type="problem_mechanism_solution",
        scene_beats=scene_beats,
    )
    narr_art = store.save_artifact(
        project_id=project.id,
        run_id=run.id,
        artifact_type="narrative_plan",
        schema_version="1",
        payload_json=narrative_plan.model_dump(),
        parent_artifact_roles_json={"research_packet": res_art.id},
        validation_json=ValidationResult(status="valid"),
    )
    print(f"Saved narrative_plan: {narr_art.id}")

    # 5. Save Hook (2 beats)
    hook = Hook(
        conceptual_hook="The Nine Laws of Financial Survival",
        script_text="Most wealth plans fail because investors misjudge how numbers interact.",
        visual_directives=[
            HookVisualDirective(
                beat_id="hook_01",
                preferred_component="Typography",
                visual_goal="Bold hook statement on wealth failure",
                trigger_word=None,
                component_data={"text": "Most wealth plans fail in silence", "variant": "headline"},
            ),
            HookVisualDirective(
                beat_id="hook_02",
                preferred_component="StockVideo",
                visual_goal="Moody financial city footage",
                trigger_word="interact",
                asset_query="financial district skyscrapers night",
            ),
        ],
    )
    hook_art = store.save_artifact(
        project_id=project.id,
        run_id=run.id,
        artifact_type="hook",
        schema_version="1",
        payload_json=hook.model_dump(),
        parent_artifact_roles_json={"narrative_plan": narr_art.id},
        validation_json=ValidationResult(status="valid"),
    )
    print(f"Saved hook: {hook_art.id}")

    # 6. Run CompositionPlannerEngine on all 9 VisualIntents
    planner_engine = CompositionPlannerEngine(llm_provider)
    print("\n--- Running CompositionPlannerEngine for 9 visual intents ---")
    comp_beats: list[CompositionBeat] = []
    planner_results: list[dict] = []

    for idx, item in enumerate(ideas_meta):
        intent = item["intent"]
        beat_id = f"beat_{idx+1:02d}_01"
        plan_res = planner_engine.run(
            intent=intent,
            beat_id=beat_id,
            topic=gen_req.topic,
            audience=gen_req.audience,
        )
        comp_beats.append(plan_res.beat)
        planner_results.append({
            "beat_id": beat_id,
            "relationship_type": intent.relationship_type,
            "selected_composition": plan_res.beat.composition_id,
            "used_fallback": plan_res.used_fallback,
            "fallback_reason": plan_res.fallback_reason,
            "composition_data": plan_res.beat.composition_data,
        })
        print(f"Beat {idx+1:02d} ({beat_id}): intent={intent.relationship_type:<15s} -> composition={plan_res.beat.composition_id:<22s} fallback={plan_res.used_fallback} reason={plan_res.fallback_reason}")

    # Build FullCompositionPlan
    comp_ideas = [
        IdeaCompositionPlan(
            idea_id=item["idea_id"],
            narration=item["narration"],
            beats=[beat],
        )
        for item, beat in zip(ideas_meta, comp_beats)
    ]
    full_comp_plan = FullCompositionPlan(
        thesis=narrative_plan.thesis,
        visual_mode="composition",
        ideas=comp_ideas,
    )

    # 7. Save ScriptVisualStrategy with composition_plan
    strategy_ideas = [
        VideoIdea(
            idea_id=item["idea_id"],
            title=item["title"],
            focus_concept=item["focus_concept"],
            core_teaching_point=item["core_teaching_point"],
            narration=item["narration"],
        )
        for idx, item in enumerate(ideas_meta)
    ]
    strategy = ScriptVisualStrategy(
        thesis=narrative_plan.thesis,
        ideas=strategy_ideas,
    )
    strategy_payload = strategy.model_dump()
    strategy_payload["visual_mode"] = "composition"
    strategy_payload["composition_plan"] = full_comp_plan.model_dump()

    strat_art = store.save_artifact(
        project_id=project.id,
        run_id=run.id,
        artifact_type="script_visual_strategy",
        schema_version="1",
        payload_json=strategy_payload,
        parent_artifact_roles_json={
            "hook": hook_art.id,
            "narrative_plan": narr_art.id,
            "research_packet": res_art.id,
        },
        validation_json=ValidationResult(status="valid"),
    )
    print(f"Saved script_visual_strategy: {strat_art.id}")

    # 8. Save QualityReview
    rev_art = store.save_artifact(
        project_id=project.id,
        run_id=run.id,
        artifact_type="review_result",
        schema_version="1",
        payload_json={
            "schema_version": "1",
            "approved": True,
            "checks": [
                {"name": "Concept Alignment", "status": "passed", "message": "All 9 concepts aligned"},
                {"name": "Visual Variety", "status": "passed", "message": "9 distinct compositions exercised"},
            ],
            "feedback": "Approved for diagnostic assembly",
        },
        parent_artifact_roles_json={
            "script_visual_strategy": strat_art.id,
            "research_packet": res_art.id,
        },
        validation_json=ValidationResult(status="valid"),
    )
    print(f"Saved review_result: {rev_art.id}")

    # 9. Run Voice Generation stage
    print("\n--- Running stage: voice_generation ---")
    voice_art = pipeline_service.run_stage("voice_generation", project.id, run.id)
    voice_payload = voice_art.payload_json
    duration_s = voice_payload.get("duration_seconds", 0)
    words_count = len(voice_payload.get("word_timestamps", []))
    print(f"voice_generation completed! Duration: {duration_s:.2f}s, Words: {words_count}")

    # 10. Run Video Assembly stage
    print("\n--- Running stage: video_assembly ---")
    assembly_art = pipeline_service.run_stage("video_assembly", project.id, run.id)
    render_spec_payload = assembly_art.payload_json
    scenes = render_spec_payload.get("props", {}).get("scenes", [])
    total_frames = render_spec_payload.get("duration_frames", 0)
    print(f"video_assembly completed! Total Scenes: {len(scenes)}, Total Frames: {total_frames}")

    # 11. Run Render stage
    print("\n--- Running stage: render ---")
    render_art = pipeline_service.run_stage("render", project.id, run.id)
    storage_key = render_art.payload_json.get("storage_key")
    video_path = str(media_storage.path_for_key(storage_key)) if storage_key else None
    print(f"render completed! Video path: {video_path}")

    # 12. Compile Diagnostic Report
    print("\n" + "=" * 75)
    print("FINAL REPORT: NINE RELATIONSHIPS DIAGNOSTIC ROUTING")
    print("=" * 75)

    print("\n1. Intent Routing & Fallback Diagnostics:")
    for r in planner_results:
        print(f"   - {r['relationship_type']:<14s} -> {r['selected_composition']:<22s} | fallback={r['used_fallback']} | reason={r['fallback_reason']}")

    print("\n2. RenderSpec scene types in order:")
    for idx, sc in enumerate(scenes):
        cid = sc.get("component", {}).get("component_id")
        dur = sc.get("duration_frames")
        print(f"   Scene {idx+1:02d}: component={cid:<22s} duration={dur} frames")

    # 3. Composition distribution in body
    body_scenes = scenes[2:]  # Exclude 2 hook scenes
    comp_counts: dict[str, int] = {}
    for sc in body_scenes:
        cid = sc.get("component", {}).get("component_id")
        comp_counts[cid] = comp_counts.get(cid, 0) + 1

    print("\n3. Composition distribution in body:")
    for cid, count in sorted(comp_counts.items()):
        print(f"   - {cid}: {count}")

    # 4. Count of legacy fallbacks in body (in composition mode, fallback is Typography)
    legacy_fallbacks = [sc for sc in body_scenes if sc.get("component", {}).get("component_id") == "Typography"]
    print(f"\n4. Count of legacy fallback scenes in body: {len(legacy_fallbacks)}")

    # 5. Fallback count from planner
    total_fallbacks = sum(1 for r in planner_results if r["used_fallback"])
    print(f"\n5. Total planner fallback count across 9 intents: {total_fallbacks}")

    final_duration_seconds = total_frames / 30.0
    print(f"\n6. Final video duration: {final_duration_seconds:.2f}s ({total_frames} frames @ 30fps)")

    # Save diagnostic results json
    diag_summary = {
        "project_id": project.id,
        "run_id": run.id,
        "planner_results": planner_results,
        "scenes_in_order": [sc.get("component", {}).get("component_id") for sc in scenes],
        "composition_distribution": comp_counts,
        "legacy_fallbacks": len(legacy_fallbacks),
        "planner_fallbacks": total_fallbacks,
        "final_duration_seconds": final_duration_seconds,
        "video_path": video_path,
    }
    summary_path = backend_dir / ".data" / "diagnostic_routing_results.json"
    summary_path.write_text(json.dumps(diag_summary, indent=2))
    print(f"\nSaved diagnostic summary to: {summary_path}")


if __name__ == "__main__":
    main()
