"""
End-to-end test script: Six Compositions Showcase.

Creates a composition-mode test project with 6 body visual intents,
exercises each of the 6 compositions:
1. metric_hero
2. calculation_story
3. cause_effect
4. time_decay
5. multi_factor_pressure
6. broll_caption

Renders the video and reports:
1. CompositionPlan beats
2. RenderSpec scene types in order
3. Count of each composition
4. Count of legacy ComponentRegistry scenes
5. Final duration
6. Any planner validation/fallback events
"""
import os
import sys
import json
from pathlib import Path

# Add backend directory to sys.path
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
from domain.hook import Hook, VisualDirective as HookVisualDirective
from domain.script_visual_strategy import ScriptVisualStrategy, VideoIdea, VisualStrategyBeat
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

    print("=" * 70)
    print("STARTING SIX COMPOSITIONS TEST PROJECT")
    print("=" * 70)

    # 1. Create Project & Run
    project = store.create_project("Six Compositions Showcase")
    run = store.create_run(project.id, mode="ai")
    print(f"Project ID: {project.id}")
    print(f"Run ID: {run.id}")

    # 2. Save GenerateVideoRequest (composition mode, short_2min)
    gen_req = GenerateVideoRequest(
        topic="Six Rules of Retirement Mathematics",
        angle="A definitive visual breakdown of portfolio survival",
        audience="retail investors planning retirement",
        language="English",
        style="educational and mathematically rigorous",
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
        "Retirement Target",
        "Four Percent Rule",
        "Portfolio Depletion",
        "Purchasing Power",
        "Compound Risk",
        "Disciplined Execution",
    ]
    research_packet = ResearchPacket(
        topic="Six Rules of Retirement Mathematics",
        audience="retail investors planning retirement",
        channel="FinanceMastery",
        concepts=concepts,
        verified_facts=[
            "₹50 lakh is the standard retail retirement benchmark.",
            "4% withdrawal yields ₹2 lakh annually.",
            "Inflation at 7% cuts real purchasing power in half over 15 years.",
        ],
        statistics=[
            "60% of retirees run out of money prematurely.",
        ],
        misconceptions=[
            "Standard 4% rule accounts for inflation shocks.",
        ],
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

    # 4. Save NarrativePlan (6 concise ideas)
    ideas_meta = [
        {
            "idea_id": "idea_01",
            "title": "The Milestone",
            "focus_concept": "Retirement Target",
            "core_teaching_point": "Starting corpus milestone.",
            "narration": "To retire safely, your starting portfolio target must reach fifty lakh rupees.",
        },
        {
            "idea_id": "idea_02",
            "title": "The Drawdown",
            "focus_concept": "Four Percent Rule",
            "core_teaching_point": "Annual income formula.",
            "narration": "A four percent annual withdrawal gives you exactly two lakh rupees per year.",
        },
        {
            "idea_id": "idea_03",
            "title": "The Double Drag",
            "focus_concept": "Portfolio Depletion",
            "core_teaching_point": "Causal factors destroying capital.",
            "narration": "High inflation and weak market returns combine to deplete your principal rapidly.",
        },
        {
            "idea_id": "idea_04",
            "title": "The Purchasing Power Trap",
            "focus_concept": "Purchasing Power",
            "core_teaching_point": "Value erosion over a decade.",
            "narration": "Over fifteen years, that fixed two lakh loses forty percent of its purchasing power.",
        },
        {
            "idea_id": "idea_05",
            "title": "The Triple Risk",
            "focus_concept": "Compound Risk",
            "core_teaching_point": "Multiple converging systemic risks.",
            "narration": "Surging healthcare costs, market volatility, and tax drag converge to create extreme retirement pressure.",
        },
        {
            "idea_id": "idea_06",
            "title": "The True Defense",
            "focus_concept": "Disciplined Execution",
            "core_teaching_point": "Philosophical discipline over speculation.",
            "narration": "True financial peace requires disciplined execution rather than chasing speculation.",
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
        thesis="Retirement calculations require real-world stress testing across compounding, decay, and converging risks.",
        target_pain_point="Fear of running out of money in retirement",
        conceptual_hook="Why standard 4% rules fail under inflation",
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

    # 5. Save Hook (2 beats: Typography + StockVideo)
    hook = Hook(
        conceptual_hook="The Retirement Math Trap",
        script_text="Most people think retirement math is safe, but sixty percent run out of money.",
        visual_directives=[
            HookVisualDirective(
                beat_id="hook_b1",
                preferred_component="Typography",
                visual_instruction="Show bold retirement trap statement",
                trigger_word=None,
                component_data={"text": "The Retirement Math Trap", "subtitle": "Why standard models fail"},
            ),
            HookVisualDirective(
                beat_id="hook_b2",
                preferred_component="StockVideo",
                visual_instruction="Show financial chart declining",
                trigger_word="sixty",
                asset_query="stock market ticker monitor",
                component_data={},
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

    # 6. Run CompositionPlannerEngine on 6 VisualIntents
    planner_engine = CompositionPlannerEngine(llm_provider)
    intents = [
        VisualIntent(
            intent_id="intent_01",
            narration_excerpt=ideas_meta[0]["narration"],
            what_viewer_must_understand="₹50 lakh is the target retirement corpus.",
            key_values=["₹50 lakh"],
            relationship_type="metric",
            emphasis="hero",
        ),
        VisualIntent(
            intent_id="intent_02",
            narration_excerpt=ideas_meta[1]["narration"],
            what_viewer_must_understand="Four percent of ₹50 lakh gives ₹2 lakh annual income.",
            key_values=["₹50 lakh", "4%", "₹2 lakh"],
            relationship_type="calculation",
        ),
        VisualIntent(
            intent_id="intent_03",
            narration_excerpt=ideas_meta[2]["narration"],
            what_viewer_must_understand="Inflation and poor returns combine to cause corpus depletion.",
            key_values=["7% inflation", "3% returns"],
            relationship_type="cause_effect",
        ),
        VisualIntent(
            intent_id="intent_04",
            narration_excerpt=ideas_meta[3]["narration"],
            what_viewer_must_understand="A fixed ₹2 lakh loses 40% of its purchasing power over 15 years.",
            key_values=["₹2 lakh", "15 years", "40%"],
            relationship_type="decline",
        ),
        VisualIntent(
            intent_id="intent_05",
            narration_excerpt=ideas_meta[4]["narration"],
            what_viewer_must_understand="Three independent risk factors converge to create extreme retirement pressure.",
            key_values=["healthcare", "market volatility", "tax drag"],
            relationship_type="multi_factor",
        ),
        VisualIntent(
            intent_id="intent_06",
            narration_excerpt=ideas_meta[5]["narration"],
            what_viewer_must_understand="Lasting wealth requires steady discipline over speculation.",
            key_values=["steady discipline"],
            relationship_type="statement",
        ),
    ]

    print("\n--- Running CompositionPlannerEngine for 6 visual intents ---")
    comp_beats: list[CompositionBeat] = []
    planner_events: list[dict] = []

    for idx, (item, intent) in enumerate(zip(ideas_meta, intents)):
        beat_id = f"beat_{idx+1:02d}_01"
        plan_res = planner_engine.run(
            intent=intent,
            beat_id=beat_id,
            topic=gen_req.topic,
            audience=gen_req.audience,
        )
        comp_beats.append(plan_res.beat)
        planner_events.append({
            "beat_id": beat_id,
            "intent_type": intent.relationship_type,
            "selected_composition": plan_res.beat.composition_id,
            "used_fallback": plan_res.used_fallback,
            "data": plan_res.beat.composition_data,
        })
        print(f"Beat {idx+1} ({beat_id}): intent={intent.relationship_type:12s} -> {plan_res.beat.composition_id:22s} fallback={plan_res.used_fallback}")

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
            visual_sequence=[
                VisualStrategyBeat(
                    beat_id=f"leg_{idx+1:02d}_01",
                    preferred_component="Typography",
                    visual_goal=item["core_teaching_point"],
                    trigger_word=None,
                ),
            ],
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

    # 8. Save QualityReview (ReviewResult)
    rev_art = store.save_artifact(
        project_id=project.id,
        run_id=run.id,
        artifact_type="review_result",
        schema_version="1",
        payload_json={
            "schema_version": "1",
            "approved": True,
            "checks": [
                {"name": "Concept Alignment", "status": "passed", "message": "All concepts verified"},
                {"name": "Visual Variety", "status": "passed", "message": "6 distinct compositions"},
            ],
            "feedback": "Approved for production",
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

    # 12. Compile Audit Report
    print("\n" + "=" * 70)
    print("FINAL REPORT: SIX COMPOSITIONS TEST PROJECT")
    print("=" * 70)

    # 1. CompositionPlan beats
    print("\n1. CompositionPlan beats:")
    for b in comp_beats:
        print(f"   - [{b.beat_id}] {b.composition_id} (asset={b.asset_requirement})")
        print(f"     data: {json.dumps(b.composition_data)}")

    # 2. RenderSpec scene types in order
    print("\n2. RenderSpec scene types in order:")
    for idx, sc in enumerate(scenes):
        cid = sc.get("component", {}).get("component_id")
        dur = sc.get("duration_frames")
        print(f"   Scene {idx+1:02d}: component={cid:<22s} duration={dur} frames")

    # 3. Count of each composition
    body_scenes = scenes[2:]  # Exclude 2 hook scenes
    comp_counts: dict[str, int] = {}
    for sc in body_scenes:
        cid = sc.get("component", {}).get("component_id")
        comp_counts[cid] = comp_counts.get(cid, 0) + 1

    print("\n3. Count of each composition in body:")
    for cid, count in sorted(comp_counts.items()):
        print(f"   - {cid}: {count}")

    # 4. Count of legacy ComponentRegistry scenes in body
    legacy_set = {
        "Typography", "NumberCounter", "StockVideo", "StockImage",
        "ProcessFlow", "ProgressiveList", "SplitComparison", "Charts",
        "DataTable", "RankedList", "Timeline", "KPIGrid", "BeforeAfter",
        "QuoteCallout", "IconAnimation",
    }
    legacy_in_body = [sc.get("component", {}).get("component_id") for sc in body_scenes if sc.get("component", {}).get("component_id") in legacy_set]
    print(f"\n4. Count of legacy ComponentRegistry scenes in body: {len(legacy_in_body)}")
    if legacy_in_body:
        print(f"   Legacy scenes detected: {legacy_in_body}")
    else:
        print("   ZERO legacy scenes in body! (100% pure composition mode)")

    # 5. Final duration
    final_duration_frames = total_frames
    final_duration_seconds = final_duration_frames / 30.0
    print(f"\n5. Final duration: {final_duration_seconds:.2f}s ({final_duration_frames} frames @ 30fps)")

    # 6. Any planner validation/fallback events
    fallback_events = [e for e in planner_events if e["used_fallback"]]
    print(f"\n6. Planner validation/fallback events: {len(fallback_events)}")
    if fallback_events:
        for ev in fallback_events:
            print(f"   - Fallback on {ev['beat_id']} ({ev['intent_type']}): fell back to {ev['selected_composition']}")
    else:
        print("   ZERO fallback events! All 6 compositions passed validation directly!")

    # Video file verification
    if video_path and Path(video_path).exists():
        size_mb = Path(video_path).stat().st_size / (1024 * 1024)
        print(f"\nRendered MP4 file verified! Path: {video_path} (Size: {size_mb:.2f} MB)")
    else:
        print(f"\nWarning: Video path not found or empty: {video_path}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
