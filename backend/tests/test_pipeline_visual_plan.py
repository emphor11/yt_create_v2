from fastapi.testclient import TestClient

from app.dependencies import get_artifact_store, get_pipeline_service
from app.main import create_app
from app.pipeline_service import build_pipeline_service
from artifact_store.sqlite_store import ArtifactStore


def make_client(tmp_path) -> tuple[TestClient, ArtifactStore]:
    store = ArtifactStore(tmp_path / "visual_plan.db")
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


def run_to_visual_event_sequence(client: TestClient, created: dict) -> dict:
    run_stage(client, created, "script_brief")
    run_stage(client, created, "narrative_arc")
    run_stage(client, created, "script_draft")
    run_stage(client, created, "scene_script")
    run_stage(client, created, "semantic_scene")
    return run_stage(client, created, "visual_event_sequence")


def test_run_visual_plan_creates_artifact_with_required_parents(tmp_path) -> None:
    client, _store = make_client(tmp_path)
    created = create_valid_project(client)
    run_to_visual_event_sequence(client, created)
    artifacts = client.get(
        f"/projects/{created['project']['id']}/runs/{created['run']['id']}/artifacts"
    ).json()
    semantic_scene_artifact = next(
        artifact for artifact in artifacts if artifact["artifact_type"] == "semantic_scene"
    )
    visual_event_sequence_artifact = next(
        artifact
        for artifact in artifacts
        if artifact["artifact_type"] == "visual_event_sequence"
    )

    response = client.post(
        f"/projects/{created['project']['id']}/runs/{created['run']['id']}/run/visual_plan"
    )

    assert response.status_code == 200
    body = response.json()
    artifact = body["artifact"]
    payload = artifact["payload_json"]
    assert body["validation"]["status"] == "valid"
    assert artifact["artifact_type"] == "visual_plan"
    assert artifact["parent_artifact_roles_json"] == {
        "semantic_scene": semantic_scene_artifact["id"],
        "visual_event_sequence": visual_event_sequence_artifact["id"],
    }
    assert payload["component"] == "SplitComparison"
    assert payload["props"]["left"]["role"] == "product_price"
    assert payload["props"]["left"]["value"] == 80000
    assert payload["props"]["left"]["semantic_entity_id"] == "entity_price"
    assert payload["props"]["right"]["role"] == "monthly_payment"
    assert payload["props"]["right"]["value"] == 6667
    assert payload["props"]["right"]["semantic_entity_id"] == "entity_emi"
    assert payload["props"]["attention_shift_event_id"] == "event_attention_shift"


def test_run_visual_plan_twice_returns_existing_artifact(tmp_path) -> None:
    client, _store = make_client(tmp_path)
    created = create_valid_project(client)
    run_to_visual_event_sequence(client, created)
    path = f"/projects/{created['project']['id']}/runs/{created['run']['id']}/run/visual_plan"

    first = client.post(path)
    second = client.post(path)
    artifacts = client.get(
        f"/projects/{created['project']['id']}/runs/{created['run']['id']}/artifacts"
    )

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["artifact_id"] == second.json()["artifact_id"]
    assert [artifact["artifact_type"] for artifact in artifacts.json()].count("visual_plan") == 1


def test_visual_plan_requires_semantic_scene(tmp_path) -> None:
    client, _store = make_client(tmp_path)
    created = create_valid_project(client)
    run_stage(client, created, "script_brief")
    run_stage(client, created, "narrative_arc")
    run_stage(client, created, "script_draft")
    run_stage(client, created, "scene_script")

    response = client.post(
        f"/projects/{created['project']['id']}/runs/{created['run']['id']}/run/visual_plan"
    )

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "Cannot run 'visual_plan': required 'semantic_scene' artifact is missing."
    )


def test_visual_plan_requires_visual_event_sequence(tmp_path) -> None:
    client, _store = make_client(tmp_path)
    created = create_valid_project(client)
    run_stage(client, created, "script_brief")
    run_stage(client, created, "narrative_arc")
    run_stage(client, created, "script_draft")
    run_stage(client, created, "scene_script")
    run_stage(client, created, "semantic_scene")

    response = client.post(
        f"/projects/{created['project']['id']}/runs/{created['run']['id']}/run/visual_plan"
    )

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "Cannot run 'visual_plan': required 'visual_event_sequence' artifact is missing."
    )
