from fastapi.testclient import TestClient

from app.dependencies import get_artifact_store, get_pipeline_service
from app.main import create_app
from app.pipeline_service import build_pipeline_service
from artifact_store.sqlite_store import ArtifactStore
from providers.llm_provider import (
    LLMJsonRequest,
    LLMJsonResponse,
    LLMProviderError,
    LLMProviderMetadata,
)


class ScriptedTestLLMProvider:
    def __init__(self, responses):
        self.responses = list(responses)
        self.last_request: LLMJsonRequest | None = None

    def generate_json(self, request: LLMJsonRequest) -> LLMJsonResponse:
        self.last_request = request
        response = self.responses.pop(0)
        if isinstance(response, LLMProviderError):
            raise response
        return LLMJsonResponse(
            payload=response,
            metadata=LLMProviderMetadata(
                provider="scripted-test",
                model="scripted-test-model",
            ),
        )


def valid_ai_script_brief_payload() -> dict:
    return {
        "schema_version": "1",
        "topic": "Why Monthly Payments Feel Cheap",
        "angle": "How EMIs hide total cost",
        "thesis": (
            "Monthly payments make an expensive phone feel cheaper by shrinking "
            "the moment of payment pain."
        ),
        "primary_mechanisms": [
            "payment_pain_reduction",
            "affordability_illusion",
        ],
        "recurring_example": "₹80,000 phone",
        "scene_functions": [
            {
                "scene_id": "scene_01",
                "label": "ai_full_price_vs_monthly_payment",
                "mechanism": "payment_pain_reduction",
                "purpose": (
                    "Use the phone example to contrast total price with monthly EMI framing."
                ),
            }
        ],
    }


def make_client(
    tmp_path,
    *,
    llm_provider=None,
) -> tuple[TestClient, ArtifactStore]:
    store = ArtifactStore(tmp_path / "pipeline.db")
    store.initialize()
    app = create_app()
    app.dependency_overrides[get_artifact_store] = lambda: store
    app.dependency_overrides[get_pipeline_service] = lambda: build_pipeline_service(
        store,
        llm_provider=llm_provider,
    )
    return TestClient(app), store


def create_valid_project(client: TestClient) -> dict:
    response = client.post(
        "/projects",
        json={
            "topic": "Why Monthly Payments Feel Cheap",
            "angle": "How EMIs hide total cost",
        },
    )
    assert response.status_code == 200
    return response.json()


def test_run_script_brief_creates_artifact_with_topic_request_parent(tmp_path) -> None:
    client, _store = make_client(tmp_path)
    created = create_valid_project(client)

    response = client.post(
        f"/projects/{created['project']['id']}/runs/{created['run']['id']}/run/script_brief"
    )

    assert response.status_code == 200
    body = response.json()
    artifact = body["artifact"]
    assert body["artifact_id"] == artifact["id"]
    assert body["validation"]["status"] == "valid"
    assert artifact["artifact_type"] == "script_brief"
    assert artifact["status"] == "valid"
    assert artifact["parent_artifact_roles_json"] == {
        "topic_request": created["topic_request_artifact"]["id"]
    }
    assert artifact["payload_json"]["recurring_example"] == "₹80,000 phone"
    assert artifact["payload_json"]["primary_mechanisms"] == [
        "payment_pain_reduction",
        "affordability_illusion",
    ]


def test_run_script_brief_twice_returns_existing_artifact(tmp_path) -> None:
    client, _store = make_client(tmp_path)
    created = create_valid_project(client)
    path = f"/projects/{created['project']['id']}/runs/{created['run']['id']}/run/script_brief"

    first = client.post(path)
    second = client.post(path)
    artifacts = client.get(
        f"/projects/{created['project']['id']}/runs/{created['run']['id']}/artifacts"
    )

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["artifact_id"] == second.json()["artifact_id"]
    assert [artifact["artifact_type"] for artifact in artifacts.json()].count("script_brief") == 1


def test_blocked_topic_request_cannot_run_script_brief(tmp_path) -> None:
    client, _store = make_client(tmp_path)
    created = client.post(
        "/projects",
        json={"topic": "", "angle": "How EMIs hide total cost"},
    ).json()

    response = client.post(
        f"/projects/{created['project']['id']}/runs/{created['run']['id']}/run/script_brief"
    )

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "Cannot run 'script_brief': 'topic_request' artifact has status 'blocked' and cannot be advanced."
    )


def test_ai_mode_without_provider_does_not_silently_use_deterministic_script_brief(
    tmp_path,
) -> None:
    client, _store = make_client(tmp_path)
    created = client.post(
        "/projects",
        json={
            "topic": "Why Monthly Payments Feel Cheap",
            "angle": "How EMIs hide total cost",
            "mode": "ai",
        },
    ).json()

    response = client.post(
        f"/projects/{created['project']['id']}/runs/{created['run']['id']}/run/script_brief"
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "AI LLM provider is not configured for script_brief."


def test_ai_mode_script_brief_uses_llm_provider_and_stores_metadata(tmp_path) -> None:
    provider = ScriptedTestLLMProvider([valid_ai_script_brief_payload()])
    client, _store = make_client(tmp_path, llm_provider=provider)
    created = client.post(
        "/projects",
        json={
            "topic": "Why Monthly Payments Feel Cheap",
            "angle": "How EMIs hide total cost",
            "mode": "ai",
        },
    ).json()

    response = client.post(
        f"/projects/{created['project']['id']}/runs/{created['run']['id']}/run/script_brief"
    )

    assert response.status_code == 200
    artifact = response.json()["artifact"]
    assert artifact["artifact_type"] == "script_brief"
    assert artifact["status"] == "valid"
    assert artifact["payload_json"]["scene_functions"][0]["label"] == (
        "ai_full_price_vs_monthly_payment"
    )
    assert artifact["payload_json"]["provider_metadata"]["provider"] == "scripted-test"
    assert provider.last_request is not None
    assert provider.last_request.schema_name == "ScriptBrief"


def test_ai_mode_script_brief_stores_blocked_artifact_when_validator_rejects(
    tmp_path,
) -> None:
    invalid_mechanism_payload = valid_ai_script_brief_payload()
    invalid_mechanism_payload["primary_mechanisms"] = ["unsupported_mechanism"]
    invalid_mechanism_payload["scene_functions"][0]["mechanism"] = "unsupported_mechanism"
    provider = ScriptedTestLLMProvider([invalid_mechanism_payload])
    client, _store = make_client(tmp_path, llm_provider=provider)
    created = client.post(
        "/projects",
        json={
            "topic": "Why Monthly Payments Feel Cheap",
            "angle": "How EMIs hide total cost",
            "mode": "ai",
        },
    ).json()

    response = client.post(
        f"/projects/{created['project']['id']}/runs/{created['run']['id']}/run/script_brief"
    )

    assert response.status_code == 200
    artifact = response.json()["artifact"]
    assert artifact["status"] == "blocked"
    assert "Unsupported mechanism: unsupported_mechanism." in artifact["validation_json"]["errors"]
    assert artifact["payload_json"]["provider_metadata"]["provider"] == "scripted-test"


def test_ai_mode_script_brief_stores_failed_artifact_for_bad_shape(tmp_path) -> None:
    provider = ScriptedTestLLMProvider(
        [
            {
                "topic": "Why Monthly Payments Feel Cheap",
                "angle": "How EMIs hide total cost",
            }
        ]
    )
    client, _store = make_client(tmp_path, llm_provider=provider)
    created = client.post(
        "/projects",
        json={
            "topic": "Why Monthly Payments Feel Cheap",
            "angle": "How EMIs hide total cost",
            "mode": "ai",
        },
    ).json()

    response = client.post(
        f"/projects/{created['project']['id']}/runs/{created['run']['id']}/run/script_brief"
    )

    assert response.status_code == 200
    artifact = response.json()["artifact"]
    assert artifact["status"] == "failed"
    assert artifact["payload_json"]["raw_ai_payload"] == {
        "topic": "Why Monthly Payments Feel Cheap",
        "angle": "How EMIs hide total cost",
    }
    assert artifact["validation_json"]["errors"] == [
        "LLM returned invalid ScriptBrief JSON."
    ]


def test_ai_mode_script_brief_stores_failed_artifact_for_provider_error(tmp_path) -> None:
    provider = ScriptedTestLLMProvider([LLMProviderError("provider unavailable")])
    client, _store = make_client(tmp_path, llm_provider=provider)
    created = client.post(
        "/projects",
        json={
            "topic": "Why Monthly Payments Feel Cheap",
            "angle": "How EMIs hide total cost",
            "mode": "ai",
        },
    ).json()

    response = client.post(
        f"/projects/{created['project']['id']}/runs/{created['run']['id']}/run/script_brief"
    )

    assert response.status_code == 200
    artifact = response.json()["artifact"]
    assert artifact["status"] == "failed"
    assert artifact["payload_json"]["raw_ai_payload"] == {}
    assert artifact["validation_json"]["errors"] == ["provider unavailable"]


def test_ai_mode_narrative_arc_still_waits_for_its_ai_engine(tmp_path) -> None:
    provider = ScriptedTestLLMProvider([valid_ai_script_brief_payload()])
    client, _store = make_client(tmp_path, llm_provider=provider)
    created = client.post(
        "/projects",
        json={
            "topic": "Why Monthly Payments Feel Cheap",
            "angle": "How EMIs hide total cost",
            "mode": "ai",
        },
    ).json()
    client.post(
        f"/projects/{created['project']['id']}/runs/{created['run']['id']}/run/script_brief"
    )

    response = client.post(
        f"/projects/{created['project']['id']}/runs/{created['run']['id']}/run/narrative_arc"
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "AI mode is not implemented for narrative_arc yet."


def test_unimplemented_stage_returns_404(tmp_path) -> None:
    client, _store = make_client(tmp_path)
    created = create_valid_project(client)

    response = client.post(
        f"/projects/{created['project']['id']}/runs/{created['run']['id']}/run/publish"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Stage 'publish' is not implemented."
