from pathlib import Path

from fastapi.testclient import TestClient

from app.dependencies import get_artifact_store, get_media_storage, get_pipeline_service
from app.main import create_app
from app.pipeline_service import build_pipeline_service
from artifact_store.sqlite_store import ArtifactStore
from domain.validation import ValidationResult
from engines.render_engine import RenderEngine
from providers.media_storage import LocalMediaStorage
from providers.remotion_provider import RemotionRenderOutput


class SuccessfulProvider:
    def render(self, *, render_spec, output_path: Path) -> RemotionRenderOutput:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(b"fake mp4")
        return RemotionRenderOutput(output_path=output_path, size_bytes=8)


def make_client(tmp_path) -> tuple[TestClient, ArtifactStore]:
    store = ArtifactStore(tmp_path / "hardening.db")
    store.initialize()
    media_storage = LocalMediaStorage(tmp_path / "media")
    render_engine = RenderEngine(
        media_storage=media_storage,
        remotion_provider=SuccessfulProvider(),
    )
    app = create_app()
    app.dependency_overrides[get_artifact_store] = lambda: store
    app.dependency_overrides[get_media_storage] = lambda: media_storage
    app.dependency_overrides[get_pipeline_service] = lambda: build_pipeline_service(
        store,
        render_engine=render_engine,
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


def run_stage(client: TestClient, created: dict, stage: str) -> dict:
    response = client.post(
        f"/projects/{created['project']['id']}/runs/{created['run']['id']}/run/{stage}"
    )
    assert response.status_code == 200
    return response.json()


def run_golden_pipeline(client: TestClient, created: dict) -> dict:
    for stage in [
        "script_brief",
        "narrative_arc",
        "script_draft",
        "scene_script",
        "semantic_scene",
        "visual_event_sequence",
        "visual_plan",
        "timing",
        "render_spec",
    ]:
        run_stage(client, created, stage)
    return run_stage(client, created, "render")


def test_full_monthly_payment_golden_pipeline_status_is_valid(tmp_path) -> None:
    client, _store = make_client(tmp_path)
    created = create_valid_project(client)

    video_response = run_golden_pipeline(client, created)
    status_response = client.get(
        f"/projects/{created['project']['id']}/runs/{created['run']['id']}/status"
    )

    assert status_response.status_code == 200
    stages = status_response.json()["stages"]
    assert [stage["stage"] for stage in stages] == [
        "topic_request",
        "script_brief",
        "narrative_arc",
        "script_draft",
        "scene_script",
        "semantic_scene",
        "visual_event_sequence",
        "visual_plan",
        "timing",
        "render_spec",
        "render",
    ]
    assert all(stage["status"] == "valid" for stage in stages)
    assert all(stage["error_count"] == 0 for stage in stages)
    assert video_response["artifact"]["artifact_type"] == "video"


def test_video_trace_reaches_semantic_scene_that_owns_numbers(tmp_path) -> None:
    client, _store = make_client(tmp_path)
    created = create_valid_project(client)
    video_response = run_golden_pipeline(client, created)
    video_id = video_response["artifact_id"]

    trace_response = client.get(f"/artifacts/{video_id}/trace")

    assert trace_response.status_code == 200
    trace = trace_response.json()
    semantic_node = next(
        node for node in trace["ancestors"] if node["artifact_type"] == "semantic_scene"
    )
    semantic_response = client.get(f"/artifacts/{semantic_node['artifact_id']}")
    semantic_payload = semantic_response.json()["payload_json"]
    values_by_role = {
        entity["role"]: entity["value"]
        for entity in semantic_payload["entities"]
    }

    assert semantic_node["role_path"]
    assert values_by_role == {
        "product_price": 80000,
        "monthly_payment": 6667,
    }


def test_regenerate_descendants_clears_downstream_artifacts(tmp_path) -> None:
    client, _store = make_client(tmp_path)
    created = create_valid_project(client)
    run_golden_pipeline(client, created)
    artifacts_response = client.get(
        f"/projects/{created['project']['id']}/runs/{created['run']['id']}/artifacts"
    )
    semantic_artifact = next(
        artifact
        for artifact in artifacts_response.json()
        if artifact["artifact_type"] == "semantic_scene"
    )

    regenerate_response = client.post(
        f"/projects/{created['project']['id']}/runs/{created['run']['id']}/artifacts/"
        f"{semantic_artifact['id']}/regenerate-descendants"
    )
    status_response = client.get(
        f"/projects/{created['project']['id']}/runs/{created['run']['id']}/status"
    )

    assert regenerate_response.status_code == 200
    body = regenerate_response.json()
    deleted_types = {artifact["artifact_type"] for artifact in body["deleted_artifacts"]}
    assert body["next_stage"] == "visual_event_sequence"
    assert {
        "visual_event_sequence",
        "visual_plan",
        "timed_scene_plan",
        "render_spec",
        "video",
    }.issubset(deleted_types)

    status_by_stage = {
        stage["stage"]: stage["status"]
        for stage in status_response.json()["stages"]
    }
    assert status_by_stage["semantic_scene"] == "valid"
    assert status_by_stage["visual_event_sequence"] == "missing"
    assert status_by_stage["render"] == "missing"


def test_run_status_reports_blocked_validation_summary(tmp_path) -> None:
    client, store = make_client(tmp_path)
    created = create_valid_project(client)
    store.save_artifact(
        project_id=created["project"]["id"],
        run_id=created["run"]["id"],
        artifact_type="script_brief",
        schema_version="1",
        payload_json={"fixture": "blocked"},
        parent_artifact_roles_json={
            "topic_request": created["topic_request_artifact"]["id"]
        },
        validation_json=ValidationResult(
            status="blocked",
            errors=["fixture validation error"],
        ),
    )

    response = client.get(
        f"/projects/{created['project']['id']}/runs/{created['run']['id']}/status"
    )

    assert response.status_code == 200
    script_brief_status = next(
        stage for stage in response.json()["stages"] if stage["stage"] == "script_brief"
    )
    assert script_brief_status["status"] == "blocked"
    assert script_brief_status["error_count"] == 1
    assert script_brief_status["errors"] == ["fixture validation error"]
