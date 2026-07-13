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
    store = ArtifactStore(tmp_path / "research_api.db")
    store.initialize()
    app = create_app()
    app.dependency_overrides[get_artifact_store] = lambda: store
    app.dependency_overrides[get_pipeline_service] = lambda: build_pipeline_service(
        store,
        llm_provider=llm_provider,
    )
    return TestClient(app), store


def create_ai_project(client: TestClient) -> dict:
    response = client.post(
        "/projects",
        json={
            "topic": "Why Monthly Payments Feel Cheap",
            "mode": "ai",
            "audience": "retail investors",
            "language": "English",
            "style": "educational",
            "channel": "FinanceChannel",
        },
    )
    assert response.status_code == 200
    return response.json()


def valid_research_response_payload() -> dict:
    return {
        "schema_version": "1",
        "topic": "Why Monthly Payments Feel Cheap",
        "audience": "retail investors",
        "channel": "FinanceChannel",
        "verified_facts": ["Fact 1", "Fact 2", "Fact 3"],
        "statistics": ["Stat 1"],
        "concepts": ["Concept 1", "Concept 2"],
        "misconceptions": ["Misconception 1"],
        "examples": ["Example 1"],
        "trusted_sources": ["Source 1"],
    }


def test_research_requires_generate_video_request(tmp_path) -> None:
    # Creating deterministic project has no generate_video_request (it has topic_request)
    client, _store = make_client(tmp_path)
    response = client.post("/projects", json={"topic": "A", "angle": "B"})
    created = response.json()

    response = client.post(
        f"/projects/{created['project']['id']}/runs/{created['run']['id']}/run/research"
    )
    assert response.status_code == 409
    assert "required 'generate_video_request' artifact is missing" in response.json()["detail"]


def test_research_runs_successfully_and_updates_run_state(tmp_path) -> None:
    provider = ScriptedTestLLMProvider([valid_research_response_payload()])
    client, store = make_client(tmp_path, llm_provider=provider)
    created = create_ai_project(client)

    project_id = created["project"]["id"]
    run_id = created["run"]["id"]

    response = client.post(f"/projects/{project_id}/runs/{run_id}/run/research")
    assert response.status_code == 200
    artifact = response.json()["artifact"]
    assert artifact["artifact_type"] == "research_packet"
    assert artifact["status"] == "valid"
    assert artifact["payload_json"]["verified_facts"] == ["Fact 1", "Fact 2", "Fact 3"]

    # Verify run state machine transitioned to 'running' (since next stage 'narrative_plan' is now registered)
    run = store.get_run(project_id, run_id)
    assert run.state == "running"
    assert run.current_stage == "research"
    assert run.error_message is None


def test_research_stores_failed_artifact_on_provider_error(tmp_path) -> None:
    provider = ScriptedTestLLMProvider([LLMProviderError("xAI is down")])
    client, store = make_client(tmp_path, llm_provider=provider)
    created = create_ai_project(client)

    project_id = created["project"]["id"]
    run_id = created["run"]["id"]

    response = client.post(f"/projects/{project_id}/runs/{run_id}/run/research")
    assert response.status_code == 200
    artifact = response.json()["artifact"]
    assert artifact["status"] == "failed"
    assert artifact["validation_json"]["errors"] == ["xAI is down"]

    # Since the artifact status is 'failed' (non-advanceable), the run state must be 'failed'
    run = store.get_run(project_id, run_id)
    assert run.state == "failed"
    assert run.current_stage == "research"
    assert "resulted in a non-advanceable status 'failed'" in run.error_message
