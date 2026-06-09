from fastapi.testclient import TestClient

from app.dependencies import get_artifact_store, get_pipeline_service
from app.main import create_app
from app.pipeline_service import build_pipeline_service
from artifact_store.sqlite_store import ArtifactStore


def make_client(tmp_path) -> tuple[TestClient, ArtifactStore]:
    store = ArtifactStore(tmp_path / "render_spec.db")
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


def run_to_visual_plan(client: TestClient, created: dict) -> dict:
    run_stage(client, created, "script_brief")
    run_stage(client, created, "narrative_arc")
    run_stage(client, created, "script_draft")
    run_stage(client, created, "scene_script")
    run_stage(client, created, "semantic_scene")
    run_stage(client, created, "visual_event_sequence")
    return run_stage(client, created, "visual_plan")


def run_to_timing(client: TestClient, created: dict) -> dict:
    run_to_visual_plan(client, created)
    return run_stage(client, created, "timing")


def test_run_render_spec_creates_artifact_with_required_parents(tmp_path) -> None:
    client, _store = make_client(tmp_path)
    created = create_valid_project(client)
    timed_scene_plan_response = run_to_timing(client, created)
    artifacts = client.get(
        f"/projects/{created['project']['id']}/runs/{created['run']['id']}/artifacts"
    ).json()
    visual_plan_artifact = next(
        artifact for artifact in artifacts if artifact["artifact_type"] == "visual_plan"
    )

    response = client.post(
        f"/projects/{created['project']['id']}/runs/{created['run']['id']}/run/render_spec"
    )

    assert response.status_code == 200
    body = response.json()
    artifact = body["artifact"]
    payload = artifact["payload_json"]
    assert body["validation"]["status"] == "valid"
    assert artifact["artifact_type"] == "render_spec"
    assert artifact["parent_artifact_roles_json"] == {
        "visual_plan": visual_plan_artifact["id"],
        "timed_scene_plan": timed_scene_plan_response["artifact_id"],
    }
    assert payload["composition"] == "SplitComparison"
    assert payload["fps"] == 30
    assert payload["duration_frames"] == 240
    assert payload["props"]["left"]["role"] == "product_price"
    assert payload["props"]["right"]["role"] == "monthly_payment"
    assert [span["event_id"] for span in payload["frame_spans"]] == [
        "event_full_price",
        "event_monthly_payment",
        "event_attention_shift",
    ]
    assert [span["start_frame"] for span in payload["frame_spans"]] == [0, 80, 160]
    assert payload["frame_spans"][-1]["end_frame"] == 240


def test_run_render_spec_twice_returns_existing_artifact(tmp_path) -> None:
    client, _store = make_client(tmp_path)
    created = create_valid_project(client)
    run_to_timing(client, created)
    path = f"/projects/{created['project']['id']}/runs/{created['run']['id']}/run/render_spec"

    first = client.post(path)
    second = client.post(path)
    artifacts = client.get(
        f"/projects/{created['project']['id']}/runs/{created['run']['id']}/artifacts"
    )

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["artifact_id"] == second.json()["artifact_id"]
    assert [artifact["artifact_type"] for artifact in artifacts.json()].count("render_spec") == 1


def test_render_spec_requires_visual_plan(tmp_path) -> None:
    client, _store = make_client(tmp_path)
    created = create_valid_project(client)
    run_stage(client, created, "script_brief")
    run_stage(client, created, "narrative_arc")
    run_stage(client, created, "script_draft")
    run_stage(client, created, "scene_script")
    run_stage(client, created, "semantic_scene")
    run_stage(client, created, "visual_event_sequence")

    response = client.post(
        f"/projects/{created['project']['id']}/runs/{created['run']['id']}/run/render_spec"
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Cannot run render_spec without a visual_plan artifact."


def test_render_spec_requires_timed_scene_plan(tmp_path) -> None:
    client, _store = make_client(tmp_path)
    created = create_valid_project(client)
    run_to_visual_plan(client, created)

    response = client.post(
        f"/projects/{created['project']['id']}/runs/{created['run']['id']}/run/render_spec"
    )

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "Cannot run render_spec without a timed_scene_plan artifact."
    )
