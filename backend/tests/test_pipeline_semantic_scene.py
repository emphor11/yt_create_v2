from fastapi.testclient import TestClient

from app.dependencies import get_artifact_store, get_pipeline_service
from app.main import create_app
from app.pipeline_service import build_pipeline_service
from artifact_store.sqlite_store import ArtifactStore


def make_client(tmp_path) -> tuple[TestClient, ArtifactStore]:
    store = ArtifactStore(tmp_path / "semantic_scene.db")
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


def run_stage(client: TestClient, created: dict, stage: str) -> dict:
    response = client.post(
        f"/projects/{created['project']['id']}/runs/{created['run']['id']}/run/{stage}"
    )
    assert response.status_code == 200
    return response.json()


def run_to_scene_script(client: TestClient, created: dict) -> dict:
    run_stage(client, created, "script_brief")
    run_stage(client, created, "narrative_arc")
    run_stage(client, created, "script_draft")
    return run_stage(client, created, "scene_script")


def test_run_semantic_scene_creates_artifact_with_scene_script_parent(tmp_path) -> None:
    client, _store = make_client(tmp_path)
    created = create_valid_project(client)
    scene_script_response = run_to_scene_script(client, created)

    response = client.post(
        f"/projects/{created['project']['id']}/runs/{created['run']['id']}/run/semantic_scene"
    )

    assert response.status_code == 200
    body = response.json()
    artifact = body["artifact"]
    payload = artifact["payload_json"]
    roles = {entity["role"]: entity for entity in payload["entities"]}
    assert body["validation"]["status"] == "valid"
    assert artifact["artifact_type"] == "semantic_scene"
    assert artifact["parent_artifact_roles_json"] == {
        "scene_script": scene_script_response["artifact_id"]
    }
    assert payload["scene_id"] == "scene_01"
    assert payload["primary_concept"] == "payment_pain_reduction"
    assert roles["product_price"]["value"] == 80000
    assert roles["monthly_payment"]["value"] == 6667
    assert payload["relationships"][0]["type"] == "reframes"


def test_run_semantic_scene_twice_returns_existing_artifact(tmp_path) -> None:
    client, _store = make_client(tmp_path)
    created = create_valid_project(client)
    run_to_scene_script(client, created)
    path = f"/projects/{created['project']['id']}/runs/{created['run']['id']}/run/semantic_scene"

    first = client.post(path)
    second = client.post(path)
    artifacts = client.get(
        f"/projects/{created['project']['id']}/runs/{created['run']['id']}/artifacts"
    )

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["artifact_id"] == second.json()["artifact_id"]
    assert [artifact["artifact_type"] for artifact in artifacts.json()].count("semantic_scene") == 1


def test_semantic_scene_requires_scene_script(tmp_path) -> None:
    client, _store = make_client(tmp_path)
    created = create_valid_project(client)
    run_stage(client, created, "script_brief")
    run_stage(client, created, "narrative_arc")
    run_stage(client, created, "script_draft")

    response = client.post(
        f"/projects/{created['project']['id']}/runs/{created['run']['id']}/run/semantic_scene"
    )

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "Cannot run 'semantic_scene': required 'scene_script' artifact is missing."
    )
