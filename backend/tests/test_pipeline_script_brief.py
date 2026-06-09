from fastapi.testclient import TestClient

from app.dependencies import get_artifact_store, get_pipeline_service
from app.main import create_app
from app.pipeline_service import build_pipeline_service
from artifact_store.sqlite_store import ArtifactStore


def make_client(tmp_path) -> tuple[TestClient, ArtifactStore]:
    store = ArtifactStore(tmp_path / "pipeline.db")
    store.initialize()
    app = create_app()
    app.dependency_overrides[get_artifact_store] = lambda: store
    app.dependency_overrides[get_pipeline_service] = lambda: build_pipeline_service(store)
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
        "Cannot run script_brief because the topic_request artifact is not advanceable."
    )


def test_unimplemented_stage_returns_404(tmp_path) -> None:
    client, _store = make_client(tmp_path)
    created = create_valid_project(client)

    response = client.post(
        f"/projects/{created['project']['id']}/runs/{created['run']['id']}/run/render"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Stage render is not implemented."
