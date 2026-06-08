from fastapi.testclient import TestClient

from app.dependencies import get_artifact_store, get_pipeline_service
from app.main import create_app
from app.pipeline_service import build_pipeline_service
from artifact_store.sqlite_store import ArtifactStore


def make_client(tmp_path) -> tuple[TestClient, ArtifactStore]:
    store = ArtifactStore(tmp_path / "visual_event_sequence.db")
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


def run_to_semantic_scene(client: TestClient, created: dict) -> dict:
    run_stage(client, created, "script_brief")
    run_stage(client, created, "narrative_arc")
    run_stage(client, created, "script_draft")
    run_stage(client, created, "scene_script")
    return run_stage(client, created, "semantic_scene")


def test_run_visual_event_sequence_creates_artifact_with_semantic_parent(tmp_path) -> None:
    client, _store = make_client(tmp_path)
    created = create_valid_project(client)
    semantic_scene_response = run_to_semantic_scene(client, created)

    response = client.post(
        f"/projects/{created['project']['id']}/runs/{created['run']['id']}/run/visual_event_sequence"
    )

    assert response.status_code == 200
    body = response.json()
    artifact = body["artifact"]
    payload = artifact["payload_json"]
    assert body["validation"]["status"] == "valid"
    assert artifact["artifact_type"] == "visual_event_sequence"
    assert artifact["parent_artifact_roles_json"] == {
        "semantic_scene": semantic_scene_response["artifact_id"]
    }
    assert [event["primitive"] for event in payload["events"]] == [
        "reveal_full_price",
        "reveal_monthly_payment",
        "attention_shift",
    ]
    assert payload["events"][0]["semantic_entity_id"] == "entity_price"
    assert payload["events"][1]["semantic_entity_id"] == "entity_emi"
    assert payload["events"][2]["semantic_relationship_type"] == "reframes"


def test_run_visual_event_sequence_twice_returns_existing_artifact(tmp_path) -> None:
    client, _store = make_client(tmp_path)
    created = create_valid_project(client)
    run_to_semantic_scene(client, created)
    path = (
        f"/projects/{created['project']['id']}/runs/"
        f"{created['run']['id']}/run/visual_event_sequence"
    )

    first = client.post(path)
    second = client.post(path)
    artifacts = client.get(
        f"/projects/{created['project']['id']}/runs/{created['run']['id']}/artifacts"
    )

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["artifact_id"] == second.json()["artifact_id"]
    assert (
        [artifact["artifact_type"] for artifact in artifacts.json()].count(
            "visual_event_sequence"
        )
        == 1
    )


def test_visual_event_sequence_requires_semantic_scene(tmp_path) -> None:
    client, _store = make_client(tmp_path)
    created = create_valid_project(client)
    run_stage(client, created, "script_brief")
    run_stage(client, created, "narrative_arc")
    run_stage(client, created, "script_draft")
    run_stage(client, created, "scene_script")

    response = client.post(
        f"/projects/{created['project']['id']}/runs/{created['run']['id']}/run/visual_event_sequence"
    )

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "Cannot run visual_event_sequence without a semantic_scene artifact."
    )
