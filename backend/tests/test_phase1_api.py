from fastapi.testclient import TestClient

from app.dependencies import get_artifact_store
from app.main import create_app
from artifact_store.sqlite_store import ArtifactStore
from domain.validation import ValidationResult


def make_client(tmp_path) -> tuple[TestClient, ArtifactStore]:
    store = ArtifactStore(tmp_path / "api.db")
    store.initialize()
    app = create_app()
    app.dependency_overrides[get_artifact_store] = lambda: store
    return TestClient(app), store


def test_create_project_creates_deterministic_run_and_topic_request(tmp_path) -> None:
    client, _store = make_client(tmp_path)

    response = client.post(
        "/projects",
        json={
            "topic": "Why Monthly Payments Feel Cheap",
            "angle": "How EMIs hide total cost",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["project"]["title"] == "Why Monthly Payments Feel Cheap"
    assert body["run"]["project_id"] == body["project"]["id"]
    assert body["run"]["mode"] == "deterministic"
    assert body["topic_request_artifact"]["artifact_type"] == "topic_request"
    assert body["topic_request_artifact"]["status"] == "valid"
    assert body["topic_request_artifact"]["parent_artifact_roles_json"] == {}
    assert body["topic_request_artifact"]["payload_json"] == {
        "schema_version": "1",
        "topic": "Why Monthly Payments Feel Cheap",
        "angle": "How EMIs hide total cost",
    }

    projects_response = client.get("/projects")
    runs_response = client.get(f"/projects/{body['project']['id']}/runs")
    artifacts_response = client.get(
        f"/projects/{body['project']['id']}/runs/{body['run']['id']}/artifacts"
    )

    assert projects_response.status_code == 200
    assert len(projects_response.json()) == 1
    assert runs_response.status_code == 200
    assert runs_response.json()[0]["id"] == body["run"]["id"]
    assert artifacts_response.status_code == 200
    assert len(artifacts_response.json()) == 1
    assert artifacts_response.json()[0]["artifact_type"] == "topic_request"


def test_empty_topic_creates_blocked_topic_request(tmp_path) -> None:
    client, _store = make_client(tmp_path)

    response = client.post(
        "/projects",
        json={"topic": "", "angle": "How EMIs hide total cost"},
    )

    assert response.status_code == 200
    artifact = response.json()["topic_request_artifact"]
    assert artifact["artifact_type"] == "topic_request"
    assert artifact["status"] == "blocked"
    assert artifact["validation_json"]["errors"] == ["Topic is required."]


def test_empty_angle_creates_blocked_topic_request(tmp_path) -> None:
    client, _store = make_client(tmp_path)

    response = client.post(
        "/projects",
        json={"topic": "Why Monthly Payments Feel Cheap", "angle": ""},
    )

    assert response.status_code == 200
    artifact = response.json()["topic_request_artifact"]
    assert artifact["artifact_type"] == "topic_request"
    assert artifact["status"] == "blocked"
    assert artifact["validation_json"]["errors"] == ["Angle is required."]


def test_local_frontend_origin_is_allowed(tmp_path) -> None:
    client, _store = make_client(tmp_path)

    response = client.options(
        "/projects",
        headers={
            "Origin": "http://127.0.0.1:5173",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://127.0.0.1:5173"


def test_artifact_get_parents_and_children_api(tmp_path) -> None:
    client, store = make_client(tmp_path)
    project = store.create_project("Monthly Payments")
    run = store.create_run(project.id)
    parent = store.save_artifact(
        project_id=project.id,
        run_id=run.id,
        artifact_type="parent_fixture",
        schema_version="1",
        payload_json={"value": "parent"},
        parent_artifact_roles_json={},
        validation_json=ValidationResult(status="valid"),
    )
    child = store.save_artifact(
        project_id=project.id,
        run_id=run.id,
        artifact_type="child_fixture",
        schema_version="1",
        payload_json={"value": "child"},
        parent_artifact_roles_json={"parent_fixture": parent.id},
        validation_json=ValidationResult(status="valid"),
    )

    artifact_response = client.get(f"/artifacts/{child.id}")
    parents_response = client.get(f"/artifacts/{child.id}/parents")
    children_response = client.get(f"/artifacts/{parent.id}/children")
    project_artifacts_response = client.get(f"/projects/{project.id}/artifacts")

    assert artifact_response.status_code == 200
    assert artifact_response.json()["id"] == child.id
    assert parents_response.status_code == 200
    assert parents_response.json()["parents"]["parent_fixture"]["id"] == parent.id
    assert children_response.status_code == 200
    assert children_response.json()["children"][0]["id"] == child.id
    assert project_artifacts_response.status_code == 200
    assert {artifact["id"] for artifact in project_artifacts_response.json()} == {
        parent.id,
        child.id,
    }
