import pytest

from artifact_store.models import is_advanceable_status
from artifact_store.sqlite_store import ArtifactStore, LineageError
from domain.validation import ValidationResult


def make_store(tmp_path) -> ArtifactStore:
    store = ArtifactStore(tmp_path / "test.db")
    store.initialize()
    return store


def test_store_saves_and_reads_run_scoped_artifact(tmp_path) -> None:
    store = make_store(tmp_path)
    project = store.create_project("Monthly Payments")
    run = store.create_run(project.id)

    artifact = store.save_artifact(
        project_id=project.id,
        run_id=run.id,
        artifact_type="fixture",
        schema_version="1",
        payload_json={"title": "Monthly Payments"},
        parent_artifact_roles_json={},
        validation_json=ValidationResult(status="valid"),
    )

    retrieved = store.get_artifact(artifact.id)

    assert retrieved.project_id == project.id
    assert retrieved.run_id == run.id
    assert retrieved.payload_json == {"title": "Monthly Payments"}
    assert retrieved.parent_artifact_roles_json == {}
    assert retrieved.status == "valid"


def test_parent_child_lookup_uses_role_map(tmp_path) -> None:
    store = make_store(tmp_path)
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
        parent_artifact_roles_json={"fixture_parent": parent.id},
        validation_json=ValidationResult(status="warning", warnings=["inspectable warning"]),
    )

    parents = store.get_parents(child.id)
    children = store.get_children(parent.id)

    assert parents["fixture_parent"].id == parent.id
    assert [artifact.id for artifact in children] == [child.id]


def test_blocked_and_failed_artifacts_are_stored_but_not_advanceable(tmp_path) -> None:
    store = make_store(tmp_path)
    project = store.create_project("Monthly Payments")
    run = store.create_run(project.id)

    blocked = store.save_artifact(
        project_id=project.id,
        run_id=run.id,
        artifact_type="blocked_fixture",
        schema_version="1",
        payload_json={"reason": "missing role"},
        parent_artifact_roles_json={},
        validation_json=ValidationResult(status="blocked", errors=["missing role"]),
    )
    failed = store.save_artifact(
        project_id=project.id,
        run_id=run.id,
        artifact_type="failed_fixture",
        schema_version="1",
        payload_json={"reason": "exception"},
        parent_artifact_roles_json={},
        validation_json=ValidationResult(status="failed", errors=["exception"]),
    )

    assert store.get_artifact(blocked.id).status == "blocked"
    assert store.get_artifact(failed.id).status == "failed"
    assert is_advanceable_status("valid")
    assert is_advanceable_status("warning")
    assert not is_advanceable_status("blocked")
    assert not is_advanceable_status("failed")


def test_parent_artifact_must_belong_to_same_run(tmp_path) -> None:
    store = make_store(tmp_path)
    project = store.create_project("Monthly Payments")
    first_run = store.create_run(project.id)
    second_run = store.create_run(project.id)
    parent = store.save_artifact(
        project_id=project.id,
        run_id=first_run.id,
        artifact_type="parent_fixture",
        schema_version="1",
        payload_json={},
        parent_artifact_roles_json={},
        validation_json=ValidationResult(status="valid"),
    )

    with pytest.raises(LineageError):
        store.save_artifact(
            project_id=project.id,
            run_id=second_run.id,
            artifact_type="child_fixture",
            schema_version="1",
            payload_json={},
            parent_artifact_roles_json={"wrong_run_parent": parent.id},
            validation_json=ValidationResult(status="valid"),
        )

