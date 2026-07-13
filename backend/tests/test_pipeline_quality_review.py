from fastapi.testclient import TestClient

from app.dependencies import get_artifact_store, get_pipeline_service
from app.main import create_app
from app.pipeline_service import build_pipeline_service
from artifact_store.sqlite_store import ArtifactStore
from domain.validation import ValidationResult


def make_client(tmp_path) -> tuple[TestClient, ArtifactStore]:
    store = ArtifactStore(tmp_path / "review_api.db")
    store.initialize()
    app = create_app()
    app.dependency_overrides[get_artifact_store] = lambda: store
    app.dependency_overrides[get_pipeline_service] = lambda: build_pipeline_service(
        store,
        llm_provider=None,
    )
    return TestClient(app), store


def setup_project_with_research_and_strategy(
    store: ArtifactStore,
    verified_concepts: list[str],
    verified_facts: list[str],
    statistics: list[str],
    strategy_concepts: list[str],
    strategy_narrations: list[str],
    strategy_split_values: list[int] = None,
) -> tuple[str, str]:
    project = store.create_project("Review Test Project")
    run = store.create_run(project.id, mode="ai")

    # 1. Save ResearchPacket
    res_art = store.save_artifact(
        project_id=project.id,
        run_id=run.id,
        artifact_type="research_packet",
        schema_version="1",
        payload_json={
            "topic": "Review Test Topic",
            "audience": "investors",
            "channel": "Mindshift",
            "verified_facts": verified_facts,
            "statistics": statistics,
            "concepts": verified_concepts,
            "trusted_sources": ["Source"],
        },
        parent_artifact_roles_json={},
        validation_json=ValidationResult(status="valid"),
    )

    # 2. Save Hook (dummy, needed as strategy parent)
    hook_art = store.save_artifact(
        project_id=project.id,
        run_id=run.id,
        artifact_type="hook",
        schema_version="1",
        payload_json={
            "conceptual_hook": "Hook",
            "script_text": "Is salary a drug?",
            "visual_directives": [{"beat_id": "beat_01", "visual_instruction": "Instruction"}],
        },
        parent_artifact_roles_json={"research_packet": res_art.id},
        validation_json=ValidationResult(status="valid"),
    )

    # 3. Save ScriptVisualStrategy
    ideas = []
    for idx, (concept, narration) in enumerate(zip(strategy_concepts, strategy_narrations)):
        beat_data = {}
        if strategy_split_values and idx < len(strategy_split_values):
            beat_data = {
                "left_role": "product_price",
                "left_label": "Left Option",
                "left_value": strategy_split_values[idx],
                "left_unit": "INR",
                "right_role": "monthly_payment",
                "right_label": "Right Option",
                "right_value": strategy_split_values[idx] * 2,
                "right_unit": "INR",
            }
        ideas.append(
            {
                "idea_id": f"idea_{idx:02d}",
                "title": f"Idea {idx}",
                "focus_concept": concept,
                "core_teaching_point": "Teaching point",
                "narration": narration,
                "visual_sequence": [
                    {
                        "beat_id": f"beat_{idx}_01",
                        "preferred_component": "SplitComparison" if beat_data else "Typography",
                        "visual_goal": "Goal",
                        "component_data": beat_data,
                    }
                ],
            }
        )

    store.save_artifact(
        project_id=project.id,
        run_id=run.id,
        artifact_type="script_visual_strategy",
        schema_version="1",
        payload_json={
            "thesis": "Thesis statement",
            "ideas": ideas,
        },
        parent_artifact_roles_json={
            "hook": hook_art.id,
            "research_packet": res_art.id,
        },
        validation_json=ValidationResult(status="valid"),
    )

    return project.id, run.id


def test_quality_review_requires_strategy(tmp_path) -> None:
    client, _store = make_client(tmp_path)
    response = client.post(
        "/projects",
        json={
            "topic": "Home buying",
            "mode": "ai",
            "audience": "investors",
            "language": "English",
            "style": "educational",
            "channel": "Mindshift",
        },
    )
    created = response.json()
    project_id = created["project"]["id"]
    run_id = created["run"]["id"]

    response = client.post(f"/projects/{project_id}/runs/{run_id}/run/quality_review")
    assert response.status_code == 409
    assert "required 'script_visual_strategy' artifact is missing" in response.json()["detail"]


def test_quality_review_passes_on_aligned_concept_and_statistics(tmp_path) -> None:
    client, store = make_client(tmp_path)
    project_id, run_id = setup_project_with_research_and_strategy(
        store=store,
        verified_concepts=["Opportunity Cost", "Loss Aversion"],
        verified_facts=["Fact statement showing 80000 phone price cost and right value 160000."],
        statistics=["70% of people want entrepreneurship."],
        strategy_concepts=["Opportunity Cost"],
        strategy_narrations=["Let's compare the 80000 rupees cost. Note that 70% of people feel this."],
        strategy_split_values=[80000],
    )

    response = client.post(f"/projects/{project_id}/runs/{run_id}/run/quality_review")
    assert response.status_code == 200
    artifact = response.json()["artifact"]
    assert artifact["artifact_type"] == "review_result"
    assert artifact["status"] == "valid"
    assert artifact["payload_json"]["approved"] is True

    # Verify run state transitioned to 'running' (since timing is the next stage in AI flow now)
    run = store.get_run(project_id, run_id)
    assert run.state == "running"
    assert run.current_stage == "quality_review"


def test_quality_review_fails_on_unverified_concept(tmp_path) -> None:
    client, store = make_client(tmp_path)
    project_id, run_id = setup_project_with_research_and_strategy(
        store=store,
        verified_concepts=["Opportunity Cost"],
        verified_facts=["Fact statement"],
        statistics=[],
        strategy_concepts=["CompletelyNewUnverifiedConcept"],
        strategy_narrations=["Narration without stats"],
    )

    response = client.post(f"/projects/{project_id}/runs/{run_id}/run/quality_review")
    assert response.status_code == 200
    artifact = response.json()["artifact"]
    assert artifact["status"] == "failed"
    assert artifact["payload_json"]["approved"] is False
    assert "Script concept 'CompletelyNewUnverifiedConcept' is not present in the verified research concepts." in artifact["validation_json"]["errors"][0]

    # Verify run state transitioned to 'failed'
    run = store.get_run(project_id, run_id)
    assert run.state == "failed"
    assert run.current_stage == "quality_review"


def test_quality_review_fails_on_unverified_statistics(tmp_path) -> None:
    client, store = make_client(tmp_path)
    project_id, run_id = setup_project_with_research_and_strategy(
        store=store,
        verified_concepts=["Opportunity Cost"],
        verified_facts=["Fact statement without any numeric data"],
        statistics=[],
        strategy_concepts=["Opportunity Cost"],
        strategy_narrations=["We want to claim that 99% of salary earners feel this."],  # Unverified number 99
    )

    response = client.post(f"/projects/{project_id}/runs/{run_id}/run/quality_review")
    assert response.status_code == 200
    artifact = response.json()["artifact"]
    assert artifact["status"] == "failed"
    assert artifact["payload_json"]["approved"] is False
    assert "Statistic '99' mentioned in narration is not verified in research facts." in artifact["validation_json"]["errors"][0]

    # Verify run state transitioned to 'failed'
    run = store.get_run(project_id, run_id)
    assert run.state == "failed"
    assert run.current_stage == "quality_review"
