"""
Benchmark Script: Growth Trajectory Semantic Verification & Video Render

Topic: "The first ₹10 lakh / wealth snowball / linear savings → compounding growth"
Exercises:
1. "Early growth is strictly linear, with monthly savings adding predictable, incremental amounts."
2. "Subsequent capital blocks build faster over time as annual investment returns add substantial yearly gains."
3. "The wealth snowball transitions from painful initial accumulation to rapid portfolio compounding."
4. "Reaching the first ₹10 Lakh milestone is the hardest part; after this tipping point, compounding begins to carry the weight."
5. "Starting from ₹50,000 monthly contributions, your corpus grows to ₹1.5 Crore over 15 years at 12% annual return."

Runs:
- CompositionPlannerEngine
- voice_generation
- video_assembly
- render (generating MP4)

Verifies:
- 0 fallbacks to BrollCaption for growth moments
- Proper growth_type & variant assignment
- Complete RenderSpec with GrowthTrajectory components
- Successful MP4 video rendering
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
from domain.hook import Hook, VisualDirective
from domain.script_visual_strategy import ScriptVisualStrategy, VideoIdea
from domain.visual_intent import (
    VisualIntent,
    QuantitativeMeasurement,
    TemporalContext,
    VisualDynamics,
    SemanticEntity,
)
from domain.composition_plan import FullCompositionPlan, IdeaCompositionPlan, CompositionBeat
from domain.validation import ValidationResult
from engines.composition_planner_engine import CompositionPlannerEngine


def main():
    _load_backend_dotenv()
    store = get_artifact_store()
    media_storage = get_media_storage()
    pipeline_service = get_pipeline_service()
    llm_provider = get_llm_provider()

    print("=" * 80)
    print("STARTING GROWTH TRAJECTORY REAL BENCHMARK")
    print("Topic: The first ₹10 lakh / wealth snowball / linear savings → compounding growth")
    print("=" * 80)

    # 1. Create Project & Run
    project = store.create_project("Growth Trajectory Benchmark")
    run = store.create_run(project.id, mode="ai")
    print(f"Project ID: {project.id}")
    print(f"Run ID:     {run.id}")

    # 2. Save GenerateVideoRequest
    gen_req = GenerateVideoRequest(
        topic="The first ₹10 lakh: linear savings to compounding wealth snowball",
        angle="How the first ₹10 lakh turns disciplined linear savings into an accelerating wealth snowball",
        audience="young professionals and retail investors",
        language="English",
        style="educational, analytical, and visually concrete",
        channel="FinanceMastery",
        duration_profile="short_2min",
        visual_mode="composition",
    )
    req_art = store.save_artifact(
        project_id=project.id,
        run_id=run.id,
        artifact_type="generate_video_request",
        schema_version="1",
        payload_json=gen_req.model_dump(),
        parent_artifact_roles_json={},
        validation_json=ValidationResult(status="valid"),
    )
    print(f"Saved generate_video_request: {req_art.id}")

    # 3. Save Research Packet
    res_art = store.save_artifact(
        project_id=project.id,
        run_id=run.id,
        artifact_type="research_packet",
        schema_version="1",
        payload_json={
            "topic": gen_req.topic,
            "core_thesis": "Accumulating the first ₹10 lakh requires strictly linear manual savings, after which compounding returns start generating more annual wealth than annual contributions.",
            "key_findings": [
                "The first ₹10 lakh takes the longest because capital returns are negligible.",
                "Subsequent ₹10 lakh blocks take exponentially fewer years to achieve.",
                "Compounding returns eventually overtake fresh monthly savings.",
            ],
            "raw_sources": [],
        },
        parent_artifact_roles_json={"generate_video_request": req_art.id},
        validation_json=ValidationResult(status="valid"),
    )
    print(f"Saved research_packet: {res_art.id}")

    # 4. Define the 5 benchmark visual intents
    ideas_meta = [
        {
            "idea_id": "idea_01",
            "title": "The Linear Accumulation Phase",
            "focus_concept": "Linear Savings",
            "core_teaching_point": "Early growth is strictly linear, with monthly savings adding predictable, incremental amounts.",
            "narration": "Early growth is strictly linear, with monthly savings adding predictable, incremental amounts.",
            "intent": VisualIntent(
                intent_id="intent_01",
                chunk_index=1,
                narration_excerpt="Early growth is strictly linear, with monthly savings adding predictable, incremental amounts.",
                what_viewer_must_understand="Initial wealth accumulation is strictly linear driven by savings discipline",
                key_values=["linear", "monthly savings", "incremental"],
                relationship_type="growth",
                measurements=[],
                temporal=TemporalContext(horizon="early years"),
                visual_dynamics=VisualDynamics(
                    focal_point="Predictable incremental savings build the starting foundation",
                    visual_priority="high",
                ),
            ),
        },
        {
            "idea_id": "idea_02",
            "title": "Accelerating Capital Blocks",
            "focus_concept": "Accelerating Returns",
            "core_teaching_point": "Subsequent capital blocks build faster over time as annual investment returns add substantial yearly gains.",
            "narration": "Subsequent capital blocks build faster over time as annual investment returns add substantial yearly gains.",
            "intent": VisualIntent(
                intent_id="intent_02",
                chunk_index=2,
                narration_excerpt="Subsequent capital blocks build faster over time as annual investment returns add substantial yearly gains.",
                what_viewer_must_understand="Growth accelerates as investment returns begin contributing substantial capital",
                key_values=["faster", "returns", "yearly gains"],
                relationship_type="growth",
                measurements=[],
                temporal=TemporalContext(horizon="over time"),
                visual_dynamics=VisualDynamics(
                    focal_point="Growth pace speeds up significantly as returns add capital",
                    visual_priority="high",
                ),
            ),
        },
        {
            "idea_id": "idea_03",
            "title": "The Wealth Snowball Transition",
            "focus_concept": "Compounding Snowball",
            "core_teaching_point": "The wealth snowball transitions from painful initial accumulation to rapid portfolio compounding.",
            "narration": "The wealth snowball transitions from painful initial accumulation to rapid portfolio compounding.",
            "intent": VisualIntent(
                intent_id="intent_03",
                chunk_index=3,
                narration_excerpt="The wealth snowball transitions from painful initial accumulation to rapid portfolio compounding.",
                what_viewer_must_understand="The wealth snowball shifts into rapid compounding returns",
                key_values=["wealth snowball", "compounding"],
                relationship_type="growth",
                measurements=[],
                visual_dynamics=VisualDynamics(
                    focal_point="The compounding inflection point accelerates wealth",
                    visual_priority="hero",
                ),
            ),
        },
        {
            "idea_id": "idea_04",
            "title": "The ₹10 Lakh Milestone Inflection",
            "focus_concept": "Tipping Point",
            "core_teaching_point": "Reaching the first ₹10 Lakh milestone is the hardest part; after this tipping point, compounding begins to carry the weight.",
            "narration": "Reaching the first ₹10 Lakh milestone is the hardest part; after this tipping point, compounding begins to carry the weight.",
            "intent": VisualIntent(
                intent_id="intent_04",
                chunk_index=4,
                narration_excerpt="Reaching the first ₹10 Lakh milestone is the hardest part; after this tipping point, compounding begins to carry the weight.",
                what_viewer_must_understand="The first ₹10 Lakh marks the critical inflection milestone before compounding accelerates",
                key_values=["₹10 Lakh", "tipping point"],
                relationship_type="growth",
                measurements=[
                    QuantitativeMeasurement(
                        raw_value="₹10 Lakh",
                        entity_name="First Milestone",
                        role="benchmark",
                    ),
                ],
                visual_dynamics=VisualDynamics(
                    focal_point="The first ₹10 Lakh tipping point",
                    visual_priority="high",
                ),
            ),
        },
        {
            "idea_id": "idea_05",
            "title": "The Exponential Payoff",
            "focus_concept": "Long-Term Corpus",
            "core_teaching_point": "Starting from ₹50,000 monthly contributions, your corpus grows to ₹1.5 Crore over 15 years at 12% annual return.",
            "narration": "Starting from ₹50,000 monthly contributions, your corpus grows to ₹1.5 Crore over 15 years at 12% annual return.",
            "intent": VisualIntent(
                intent_id="intent_05",
                chunk_index=5,
                narration_excerpt="Starting from ₹50,000 monthly contributions, your corpus grows to ₹1.5 Crore over 15 years at 12% annual return.",
                what_viewer_must_understand="Disciplined ₹50,000 monthly contributions expand to ₹1.5 Crore via 12% compounding",
                key_values=["₹50,000/mo", "₹1.5 Crore", "12%", "15 years"],
                relationship_type="growth",
                measurements=[
                    QuantitativeMeasurement(
                        raw_value="₹50,000/mo",
                        entity_name="Initial Contributions",
                        role="baseline",
                    ),
                    QuantitativeMeasurement(
                        raw_value="₹1.5 Crore",
                        entity_name="Target Corpus",
                        role="result",
                    ),
                    QuantitativeMeasurement(
                        raw_value="12% Annual Return",
                        metric_name="Return Rate",
                        role="rate",
                    ),
                ],
                temporal=TemporalContext(horizon="15 years"),
                visual_dynamics=VisualDynamics(
                    focal_point="₹1.5 Crore terminal wealth",
                    visual_priority="hero",
                ),
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
        thesis="The path to wealth begins with disciplined linear accumulation until reaching the critical ₹10 lakh tipping point where compounding creates an exponential snowball.",
        target_pain_point="Frustration with slow early portfolio growth",
        conceptual_hook="The First ₹10 Lakh Snowball",
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
        conceptual_hook="The First ₹10 Lakh Snowball",
        script_text="Why is the first ₹10 lakh the hardest financial milestone you will ever reach?",
        visual_directives=[
            VisualDirective(
                beat_id="hook_01",
                preferred_component="Typography",
                visual_goal="Dramatic opening hook text",
                trigger_word=None,
                component_data={"text": "The hardest milestone in wealth creation", "variant": "headline"},
            ),
            VisualDirective(
                beat_id="hook_02",
                preferred_component="StockVideo",
                visual_goal="Timelapse of growing financial numbers",
                trigger_word="milestone",
                asset_query="gold bullion vault currency wealth accumulation",
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

    # 6. Run CompositionPlannerEngine on all 5 Growth VisualIntents
    planner_engine = CompositionPlannerEngine(llm_provider)
    print("\n--- Running CompositionPlannerEngine on 5 Growth Visual Intents ---")
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
        print(f"  ✓ {beat_id}: intent='{intent.relationship_type}' -> composition='{plan_res.beat.composition_id}' (fallback={plan_res.used_fallback})")

    # 7. Construct FullCompositionPlan and save ScriptVisualStrategy
    idea_plans = [
        IdeaCompositionPlan(
            idea_id=item["idea_id"],
            narration=item["narration"],
            beats=[comp_beats[idx]],
        )
        for idx, item in enumerate(ideas_meta)
    ]
    full_comp_plan = FullCompositionPlan(
        thesis=narrative_plan.thesis,
        ideas=idea_plans,
    )

    strategy_ideas = [
        VideoIdea(
            idea_id=item["idea_id"],
            title=item["title"],
            focus_concept=item["focus_concept"],
            core_teaching_point=item["core_teaching_point"],
            narration=item["narration"],
            visual_intents=[item["intent"]],
        )
        for item in ideas_meta
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
                {"name": "Concept Alignment", "status": "passed", "message": "All 5 concepts aligned to growth trajectory"},
                {"name": "Visual Variety", "status": "passed", "message": "Growth trajectory variations demonstrated"},
            ],
            "feedback": "Approved for growth benchmark assembly and render",
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

    # 12. Compile Benchmark Verification Report
    print("\n" + "=" * 80)
    print("FINAL BENCHMARK VERIFICATION REPORT")
    print("=" * 80)

    print("\n1. Visual Intent Routing & Fallback Verification:")
    growth_count = 0
    fallback_count = 0
    for r in planner_results:
        is_growth = r["selected_composition"] == "growth_trajectory"
        if is_growth:
            growth_count += 1
        if r["used_fallback"]:
            fallback_count += 1
        status_flag = "✓ CORRECT" if is_growth and not r["used_fallback"] else "✗ FAILED"
        print(f"   [{status_flag}] Beat: {r['beat_id']} | Type: {r['relationship_type']} -> Composition: {r['selected_composition']} (Fallback: {r['used_fallback']})")

    print(f"\n2. Growth Trajectory Success Rate: {growth_count}/{len(planner_results)} ({100 * growth_count / len(planner_results):.0f}%)")
    print(f"   Fallback Count: {fallback_count} (Must be 0)")

    print("\n3. RenderSpec Scene Sequence:")
    growth_scene_count = 0
    for idx, sc in enumerate(scenes):
        cid = sc.get("component", {}).get("component_id")
        dur = sc.get("duration_frames")
        if cid == "GrowthTrajectory":
            growth_scene_count += 1
        print(f"   Scene {idx+1:02d}: component='{cid}' | frames={dur} ({dur/30:.2f}s)")

    print(f"\n4. Final Rendered Video Asset:")
    if video_path and os.path.exists(video_path):
        size_mb = os.path.getsize(video_path) / (1024 * 1024)
        print(f"   File: {video_path}")
        print(f"   Size: {size_mb:.2f} MB")
        print(f"   Status: ✓ RENDERED AND VERIFIED ON DISK")
    else:
        print(f"   File: {video_path}")
        print(f"   Status: ✗ FILE NOT FOUND")

    print("=" * 80)


if __name__ == "__main__":
    main()
