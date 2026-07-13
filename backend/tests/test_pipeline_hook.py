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
    store = ArtifactStore(tmp_path / "hook_api.db")
    store.initialize()
    app = create_app()
    app.dependency_overrides[get_artifact_store] = lambda: store
    app.dependency_overrides[get_pipeline_service] = lambda: build_pipeline_service(
        store,
        llm_provider=llm_provider,
    )
    return TestClient(app), store


def create_ai_project_with_narrative(client: TestClient, store: ArtifactStore) -> tuple[dict, str, str]:
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
    store.save_artifact(
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
                },
                {
                    "scene_id": "scene_02",
                    "title": "Math",
                    "focus_concept": "The 5% Rule",
                    "core_teaching_point": "Math outline",
                },
                {
                    "scene_id": "scene_03",
                    "title": "Outro",
                    "focus_concept": "Mobility",
                    "core_teaching_point": "Salary benefits",
                },
            ],
        },
        parent_artifact_roles_json={"research_packet": res_art.id},
        validation_json=ValidationResult(status="valid"),
    )
    return created, project_id, run_id


def valid_hook_response_payload() -> dict:
    return {
        "conceptual_hook": "Anchor vs Engine comparison",
        "script_text": "Is renting really throwing money away? Let's check the numbers.",
        "visual_directives": [
            {
                "beat_id": "beat_01",
                "visual_instruction": "Show heavy ship anchor sinking",
                "onscreen_text": "RENTING = WASTED?",
            },
            {
                "beat_id": "beat_02",
                "visual_instruction": "Show rocket engine taking off",
                "onscreen_text": "THE RENT ENGINE",
            },
        ],
    }


def test_hook_requires_narrative_plan(tmp_path) -> None:
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

    # Trying to run hook without adding narrative_plan first
    response = client.post(
        f"/projects/{project_id}/runs/{run_id}/run/hook"
    )
    assert response.status_code == 409
    assert "required 'narrative_plan' artifact is missing" in response.json()["detail"]


def test_hook_runs_successfully_and_updates_run_state(tmp_path) -> None:
    provider = ScriptedTestLLMProvider([valid_hook_response_payload()])
    client, store = make_client(tmp_path, llm_provider=provider)
    _created, project_id, run_id = create_ai_project_with_narrative(client, store)

    response = client.post(
        f"/projects/{project_id}/runs/{run_id}/run/hook"
    )
    assert response.status_code == 200
    artifact = response.json()["artifact"]
    assert artifact["artifact_type"] == "hook"
    assert artifact["status"] == "valid"
    assert artifact["payload_json"]["conceptual_hook"] == "Anchor vs Engine comparison"

    # Verify run state machine transitioned to 'completed' (currently the final stage in NEXT_STAGE_BY_ARTIFACT_TYPE)
    run = store.get_run(project_id, run_id)
    assert run.state == "completed"
    assert run.current_stage == "hook"
    assert run.error_message is None


def test_hook_stores_failed_artifact_on_provider_error(tmp_path) -> None:
    provider = ScriptedTestLLMProvider([LLMProviderError("xAI API key expired")])
    client, store = make_client(tmp_path, llm_provider=provider)
    _created, project_id, run_id = create_ai_project_with_narrative(client, store)

    response = client.post(
        f"/projects/{project_id}/runs/{run_id}/run/hook"
    )
    assert response.status_code == 200
    artifact = response.json()["artifact"]
    assert artifact["status"] == "failed"
    assert artifact["validation_json"]["errors"] == ["xAI API key expired"]

    # Since the artifact status is 'failed' (non-advanceable), the run state must be 'failed'
    run = store.get_run(project_id, run_id)
    assert run.state == "failed"
    assert run.current_stage == "hook"
    assert "resulted in a non-advanceable status 'failed'" in run.error_message
