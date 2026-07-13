from fastapi.testclient import TestClient

from app.dependencies import get_artifact_store, get_pipeline_service
from app.main import create_app
from app.pipeline_service import build_pipeline_service
from artifact_store.sqlite_store import ArtifactStore
from domain.validation import ValidationResult
from providers.llm_provider import LLMJsonRequest, LLMJsonResponse, LLMProviderMetadata, LLMProviderError


class ScriptedTestLLMProvider:
    def __init__(self, payloads: list[dict | Exception]):
        self.payloads = payloads
        self.request_count = 0
        self.last_request: LLMJsonRequest | None = None

    def generate_json(self, request: LLMJsonRequest) -> LLMJsonResponse:
        self.last_request = request
        payload = self.payloads[self.request_count]
        self.request_count += 1
        if isinstance(payload, Exception):
            raise payload
        return LLMJsonResponse(
            payload=payload,
            metadata=LLMProviderMetadata(
                provider="scripted-test",
                model="scripted-test-model",
            ),
        )


def make_client(tmp_path, llm_provider=None) -> tuple[TestClient, ArtifactStore]:
    store = ArtifactStore(tmp_path / "strategy_api.db")
    store.initialize()
    app = create_app()
    app.dependency_overrides[get_artifact_store] = lambda: store
    app.dependency_overrides[get_pipeline_service] = lambda: build_pipeline_service(
        store,
        llm_provider=llm_provider,
    )
    return TestClient(app), store


def create_ai_project_with_hook(client: TestClient, store: ArtifactStore) -> tuple[dict, str, str]:
    # 1. Create project
    response = client.post(
        "/projects",
        json={
            "topic": "Why Renting a Home is Often Smarter Than Buying",
            "mode": "ai",
            "audience": "retail investors",
            "language": "English",
            "style": "educational",
            "channel": "FinanceChannel",
        },
    )
    assert response.status_code == 200
    created = response.json()
    project_id = created["project"]["id"]
    run_id = created["run"]["id"]

    # 2. Add research packet parent artifact
    res_art = store.save_artifact(
        project_id=project_id,
        run_id=run_id,
        artifact_type="research_packet",
        schema_version="1",
        payload_json={
            "topic": "Why Renting a Home is Often Smarter Than Buying",
            "audience": "retail investors",
            "channel": "FinanceChannel",
            "verified_facts": ["Fact 1", "Fact 2", "Fact 3"],
            "statistics": ["Stat 1"],
            "concepts": ["Concept 1", "Concept 2"],
            "trusted_sources": ["Source 1"],
        },
        parent_artifact_roles_json={"generate_video_request": created["generate_video_request_artifact"]["id"]},
        validation_json=ValidationResult(status="valid"),
    )

    # 3. Add narrative plan parent artifact
    narr_art = store.save_artifact(
        project_id=project_id,
        run_id=run_id,
        artifact_type="narrative_plan",
        schema_version="1",
        payload_json={
            "thesis": "Renting is smarter",
            "target_pain_point": "Guilt",
            "conceptual_hook": "Anchor vs Engine",
            "narrative_arc_type": "Problem-Agitation-Solution",
            "scene_beats": [
                {
                    "scene_id": "scene_01",
                    "title": "Intro",
                    "focus_concept": "Opportunity Cost",
                    "core_teaching_point": "Explain opportunity cost",
                }
            ],
        },
        parent_artifact_roles_json={"research_packet": res_art.id},
        validation_json=ValidationResult(status="valid"),
    )

    # 4. Add Hook parent artifact
    store.save_artifact(
        project_id=project_id,
        run_id=run_id,
        artifact_type="hook",
        schema_version="1",
        payload_json={
            "conceptual_hook": "Anchor vs Engine",
            "script_text": "Is renting throwing money away?",
            "visual_directives": [
                {
                    "beat_id": "beat_01",
                    "visual_instruction": "Show anchor sinking",
                },
                {
                    "beat_id": "beat_02",
                    "visual_instruction": "Show rocket engine taking off",
                },
            ],
        },
        parent_artifact_roles_json={
            "research_packet": res_art.id,
            "narrative_plan": narr_art.id,
        },
        validation_json=ValidationResult(status="valid"),
    )
    return created, project_id, run_id


def valid_strategy_response_payload() -> dict:
    return {
        "thesis": "Renting is mathematically superior due to low unrecoverable housing cost ratio.",
        "ideas": [
            {
                "idea_id": "idea_01",
                "title": "The Math",
                "focus_concept": "Opportunity Cost",
                "core_teaching_point": "Show unrecoverable costs comparison",
                "narration": "Let's compare the unrecoverable cost of renting a $3000 apartment with buying a $750000 property.",
                "visual_sequence": [
                    {
                        "beat_id": "beat_01",
                        "preferred_component": "SplitComparison",
                        "visual_goal": "Compare rent vs buying unrecoverable costs",
                        "component_data": {
                            "left_role": "product_price",
                            "left_label": "Rent cost",
                            "left_value": 30000,
                            "left_unit": "INR",
                            "right_role": "monthly_payment",
                            "right_label": "Buy cost",
                            "right_value": 75000,
                            "right_unit": "INR",
                        },
                    },
                    {
                        "beat_id": "beat_02",
                        "preferred_component": "Typography",
                        "visual_goal": "Show text overlays",
                    },
                ],
            }
        ],
    }


def test_strategy_requires_hook(tmp_path) -> None:
    client, _store = make_client(tmp_path)
    response = client.post(
        "/projects",
        json={
            "topic": "Why Renting a Home is Often Smarter Than Buying",
            "mode": "ai",
            "audience": "retail investors",
            "language": "English",
            "style": "educational",
            "channel": "FinanceChannel",
        },
    )
    created = response.json()
    project_id = created["project"]["id"]
    run_id = created["run"]["id"]

    # Trying to run script_visual_strategy without adding hook first
    response = client.post(
        f"/projects/{project_id}/runs/{run_id}/run/script_visual_strategy"
    )
    assert response.status_code == 409
    assert "required 'hook' artifact is missing" in response.json()["detail"]


def test_strategy_runs_successfully_and_compiles_legacy_artifacts(tmp_path) -> None:
    provider = ScriptedTestLLMProvider([valid_strategy_response_payload()])
    client, store = make_client(tmp_path, llm_provider=provider)
    _created, project_id, run_id = create_ai_project_with_hook(client, store)

    response = client.post(
        f"/projects/{project_id}/runs/{run_id}/run/script_visual_strategy"
    )
    assert response.status_code == 200
    artifact = response.json()["artifact"]
    assert artifact["artifact_type"] == "script_visual_strategy"
    assert artifact["status"] == "valid"

    # Verify that the 4 legacy backward-compatible artifacts were compiled and saved in the database
    scene_script = store.find_artifact_by_type(project_id, run_id, "scene_script")
    assert scene_script is not None
    assert scene_script.payload_json["narration"] == "Let's compare the unrecoverable cost of renting a $3000 apartment with buying a $750000 property."

    semantic_scene = store.find_artifact_by_type(project_id, run_id, "semantic_scene")
    assert semantic_scene is not None
    assert len(semantic_scene.payload_json["entities"]) == 2

    visual_event_seq = store.find_artifact_by_type(project_id, run_id, "visual_event_sequence")
    assert visual_event_seq is not None
    assert len(visual_event_seq.payload_json["events"]) == 3

    visual_plan = store.find_artifact_by_type(project_id, run_id, "visual_plan")
    assert visual_plan is not None
    assert visual_plan.payload_json["props"]["left"]["value"] == 30000

    # Verify run state machine transitioned to 'running' (since timing is the next stage in AI flow now)
    run = store.get_run(project_id, run_id)
    assert run.state == "running"
    assert run.current_stage == "script_visual_strategy"


def test_strategy_stores_failed_artifact_on_provider_error(tmp_path) -> None:
    provider = ScriptedTestLLMProvider([LLMProviderError("xAI API key expired")])
    client, store = make_client(tmp_path, llm_provider=provider)
    _created, project_id, run_id = create_ai_project_with_hook(client, store)

    response = client.post(
        f"/projects/{project_id}/runs/{run_id}/run/script_visual_strategy"
    )
    assert response.status_code == 200
    artifact = response.json()["artifact"]
    assert artifact["status"] == "failed"
    assert artifact["validation_json"]["errors"] == ["xAI API key expired"]

    # Verify run state machine transitioned to 'failed'
    run = store.get_run(project_id, run_id)
    assert run.state == "failed"
    assert run.current_stage == "script_visual_strategy"
