from fastapi.testclient import TestClient

from app.dependencies import get_artifact_store, get_pipeline_service
from app.main import create_app
from app.pipeline_service import build_pipeline_service
from artifact_store.sqlite_store import ArtifactStore


def make_client(tmp_path) -> tuple[TestClient, ArtifactStore]:
    store = ArtifactStore(tmp_path / "narrative.db")
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


def run_script_brief(client: TestClient, created: dict) -> dict:
    response = client.post(
        f"/projects/{created['project']['id']}/runs/{created['run']['id']}/run/script_brief"
    )
    assert response.status_code == 200
    return response.json()


def test_run_narrative_arc_creates_artifact_with_script_brief_parent(tmp_path) -> None:
    client, _store = make_client(tmp_path)
    created = create_valid_project(client)
    script_brief_response = run_script_brief(client, created)

    response = client.post(
        f"/projects/{created['project']['id']}/runs/{created['run']['id']}/run/narrative_arc"
    )

    assert response.status_code == 200
    body = response.json()
    artifact = body["artifact"]
    assert body["validation"]["status"] == "valid"
    assert artifact["artifact_type"] == "narrative_arc"
    assert artifact["parent_artifact_roles_json"] == {
        "script_brief": script_brief_response["artifact_id"]
    }
    assert artifact["payload_json"]["arc"] == [
        "curiosity",
        "comfort",
        "reversal",
        "realization",
    ]
    assert artifact["payload_json"]["scene_arc_steps"][0]["scene_id"] == "scene_01"
    assert artifact["payload_json"]["scene_arc_steps"][0]["is_payoff_scene"]


def test_run_narrative_arc_twice_returns_existing_artifact(tmp_path) -> None:
    client, _store = make_client(tmp_path)
    created = create_valid_project(client)
    run_script_brief(client, created)
    path = f"/projects/{created['project']['id']}/runs/{created['run']['id']}/run/narrative_arc"

    first = client.post(path)
    second = client.post(path)
    artifacts = client.get(
        f"/projects/{created['project']['id']}/runs/{created['run']['id']}/artifacts"
    )

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["artifact_id"] == second.json()["artifact_id"]
    assert [artifact["artifact_type"] for artifact in artifacts.json()].count("narrative_arc") == 1


def test_narrative_arc_requires_script_brief(tmp_path) -> None:
    client, _store = make_client(tmp_path)
    created = create_valid_project(client)

    response = client.post(
        f"/projects/{created['project']['id']}/runs/{created['run']['id']}/run/narrative_arc"
    )

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "Cannot run 'narrative_arc': required 'script_brief' artifact is missing."
    )
