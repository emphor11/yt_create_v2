from fastapi.testclient import TestClient

from app.dependencies import get_artifact_store, get_pipeline_service
from app.main import create_app
from app.pipeline_service import build_pipeline_service
from artifact_store.sqlite_store import ArtifactStore


def make_client(tmp_path) -> tuple[TestClient, ArtifactStore]:
    store = ArtifactStore(tmp_path / "scene_script.db")
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


def run_narrative_arc(client: TestClient, created: dict) -> dict:
    response = client.post(
        f"/projects/{created['project']['id']}/runs/{created['run']['id']}/run/narrative_arc"
    )
    assert response.status_code == 200
    return response.json()


def run_script_draft(client: TestClient, created: dict) -> dict:
    response = client.post(
        f"/projects/{created['project']['id']}/runs/{created['run']['id']}/run/script_draft"
    )
    assert response.status_code == 200
    return response.json()


def test_run_scene_script_creates_artifact_with_required_parents(tmp_path) -> None:
    client, _store = make_client(tmp_path)
    created = create_valid_project(client)
    script_brief_response = run_script_brief(client, created)
    narrative_arc_response = run_narrative_arc(client, created)
    script_draft_response = run_script_draft(client, created)

    response = client.post(
        f"/projects/{created['project']['id']}/runs/{created['run']['id']}/run/scene_script"
    )

    assert response.status_code == 200
    body = response.json()
    artifact = body["artifact"]
    assert body["validation"]["status"] == "valid"
    assert artifact["artifact_type"] == "scene_script"
    assert artifact["parent_artifact_roles_json"] == {
        "script_brief": script_brief_response["artifact_id"],
        "narrative_arc": narrative_arc_response["artifact_id"],
        "script_draft": script_draft_response["artifact_id"],
    }
    assert artifact["payload_json"]["scene_id"] == "scene_01"
    assert artifact["payload_json"]["mechanism"] == "payment_pain_reduction"
    assert artifact["payload_json"]["story_state"]["recurring_example"] == "₹80,000 phone"
    assert "₹6,667 per month" in artifact["payload_json"]["narration"]


def test_run_scene_script_twice_returns_existing_artifact(tmp_path) -> None:
    client, _store = make_client(tmp_path)
    created = create_valid_project(client)
    run_script_brief(client, created)
    run_narrative_arc(client, created)
    run_script_draft(client, created)
    path = f"/projects/{created['project']['id']}/runs/{created['run']['id']}/run/scene_script"

    first = client.post(path)
    second = client.post(path)
    artifacts = client.get(
        f"/projects/{created['project']['id']}/runs/{created['run']['id']}/artifacts"
    )

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["artifact_id"] == second.json()["artifact_id"]
    assert [artifact["artifact_type"] for artifact in artifacts.json()].count("scene_script") == 1


def test_scene_script_requires_script_brief(tmp_path) -> None:
    client, _store = make_client(tmp_path)
    created = create_valid_project(client)

    response = client.post(
        f"/projects/{created['project']['id']}/runs/{created['run']['id']}/run/scene_script"
    )

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "Cannot run scene_script without a script_brief artifact."
    )


def test_scene_script_requires_narrative_arc(tmp_path) -> None:
    client, _store = make_client(tmp_path)
    created = create_valid_project(client)
    run_script_brief(client, created)

    response = client.post(
        f"/projects/{created['project']['id']}/runs/{created['run']['id']}/run/scene_script"
    )

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "Cannot run scene_script without a narrative_arc artifact."
    )


def test_scene_script_requires_script_draft(tmp_path) -> None:
    client, _store = make_client(tmp_path)
    created = create_valid_project(client)
    run_script_brief(client, created)
    run_narrative_arc(client, created)

    response = client.post(
        f"/projects/{created['project']['id']}/runs/{created['run']['id']}/run/scene_script"
    )

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "Cannot run scene_script without a script_draft artifact."
    )
