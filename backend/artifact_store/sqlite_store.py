from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from artifact_store.models import (
    ArtifactRecord,
    PipelineRunRecord,
    ProjectRecord,
    RunMode,
    RunState,
    VALID_RUN_MODES,
)
from domain.validation import ValidationResult


class StoreError(Exception):
    """Base exception for artifact store failures."""


class RecordNotFoundError(StoreError):
    """Raised when a requested row does not exist."""


class LineageError(StoreError):
    """Raised when artifact lineage violates run-scoped ownership."""


class ArtifactStore:
    def __init__(self, database_path: str | Path):
        self.database_path = Path(database_path)

    def initialize(self) -> None:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS projects (
                  id TEXT PRIMARY KEY,
                  title TEXT NOT NULL,
                  created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS pipeline_runs (
                  id TEXT PRIMARY KEY,
                  project_id TEXT NOT NULL,
                  created_at TEXT NOT NULL,
                  mode TEXT NOT NULL,
                  state TEXT NOT NULL DEFAULT 'pending',
                  current_stage TEXT,
                  started_at TEXT,
                  completed_at TEXT,
                  error_message TEXT,
                  FOREIGN KEY(project_id) REFERENCES projects(id)
                );

                CREATE TABLE IF NOT EXISTS artifacts (
                  id TEXT PRIMARY KEY,
                  project_id TEXT NOT NULL,
                  run_id TEXT NOT NULL,
                  artifact_type TEXT NOT NULL,
                  schema_version TEXT NOT NULL,
                  payload_json TEXT NOT NULL,
                  parent_artifact_roles_json TEXT NOT NULL,
                  validation_json TEXT NOT NULL,
                  status TEXT NOT NULL,
                  created_at TEXT NOT NULL,
                  FOREIGN KEY(project_id) REFERENCES projects(id),
                  FOREIGN KEY(run_id) REFERENCES pipeline_runs(id)
                );
                """
            )
            # Safe migrations for existing databases that predate these columns.
            self._migrate_run_state_columns(connection)

    def _migrate_run_state_columns(self, connection: sqlite3.Connection) -> None:
        """Add run state columns to pipeline_runs if they do not yet exist.

        SQLite does not support IF NOT EXISTS on ALTER TABLE, so we check the
        column list first and add only the columns that are missing.
        """
        existing = {
            row["name"]
            for row in connection.execute(
                "PRAGMA table_info(pipeline_runs)"
            ).fetchall()
        }
        migrations = [
            ("state",         "ALTER TABLE pipeline_runs ADD COLUMN state TEXT NOT NULL DEFAULT 'pending'"),
            ("current_stage", "ALTER TABLE pipeline_runs ADD COLUMN current_stage TEXT"),
            ("started_at",    "ALTER TABLE pipeline_runs ADD COLUMN started_at TEXT"),
            ("completed_at",  "ALTER TABLE pipeline_runs ADD COLUMN completed_at TEXT"),
            ("error_message", "ALTER TABLE pipeline_runs ADD COLUMN error_message TEXT"),
        ]
        for column, sql in migrations:
            if column not in existing:
                connection.execute(sql)

    def create_project(self, title: str) -> ProjectRecord:
        normalized_title = title.strip()
        if not normalized_title:
            raise ValueError("Project title is required.")

        record = ProjectRecord(
            id=self._new_id("project"),
            title=normalized_title,
            created_at=self._now(),
        )
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO projects (id, title, created_at) VALUES (?, ?, ?)",
                (record.id, record.title, record.created_at),
            )
        return record

    def list_projects(self) -> list[ProjectRecord]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT id, title, created_at FROM projects ORDER BY created_at DESC"
            ).fetchall()
        return [self._project_from_row(row) for row in rows]

    def get_project(self, project_id: str) -> ProjectRecord:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT id, title, created_at FROM projects WHERE id = ?",
                (project_id,),
            ).fetchone()
        if row is None:
            raise RecordNotFoundError(f"Project {project_id} was not found.")
        return self._project_from_row(row)

    def create_run(self, project_id: str, mode: RunMode = "deterministic") -> PipelineRunRecord:
        self.get_project(project_id)
        if mode not in VALID_RUN_MODES:
            raise ValueError(f"Run mode must be one of: {', '.join(sorted(VALID_RUN_MODES))}.")
        record = PipelineRunRecord(
            id=self._new_id("run"),
            project_id=project_id,
            created_at=self._now(),
            mode=mode,
            state="pending",
        )
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO pipeline_runs
                  (id, project_id, created_at, mode, state)
                VALUES (?, ?, ?, ?, ?)
                """,
                (record.id, record.project_id, record.created_at, record.mode, record.state),
            )
        return record

    def update_run_state(
        self,
        project_id: str,
        run_id: str,
        *,
        state: RunState,
        current_stage: str | None = None,
        error_message: str | None = None,
    ) -> PipelineRunRecord:
        """Transition a run to a new state and record the current stage.

        Sets started_at on the first transition to 'running' and
        completed_at on transitions to 'completed' or 'failed'.
        """
        run = self.get_run(project_id, run_id)
        now = self._now()
        started_at = run.started_at
        completed_at = run.completed_at

        if state == "running" and started_at is None:
            started_at = now
        if state in ("completed", "failed"):
            completed_at = now

        with self._connect() as connection:
            connection.execute(
                """
                UPDATE pipeline_runs
                SET state = ?, current_stage = ?, started_at = ?,
                    completed_at = ?, error_message = ?
                WHERE id = ?
                """,
                (state, current_stage, started_at, completed_at, error_message, run_id),
            )
        return self.get_run(project_id, run_id)

    def require_artifact(
        self,
        project_id: str,
        run_id: str,
        artifact_type: str,
        *,
        for_stage: str,
    ) -> ArtifactRecord:
        """Return a prerequisite artifact or raise a descriptive error.

        Centralises the repeated None-check + advanceable-status-check pattern
        that would otherwise be duplicated across every pipeline stage.
        """
        from artifact_store.models import is_advanceable_status
        from app.pipeline_service import PipelineServiceError

        artifact = self.find_artifact_by_type(project_id, run_id, artifact_type)
        if artifact is None:
            raise PipelineServiceError(
                f"Cannot run '{for_stage}': required '{artifact_type}' artifact is missing."
            )
        if not is_advanceable_status(artifact.status):
            raise PipelineServiceError(
                f"Cannot run '{for_stage}': '{artifact_type}' artifact "
                f"has status '{artifact.status}' and cannot be advanced."
            )
        return artifact

    def list_runs(self, project_id: str) -> list[PipelineRunRecord]:
        self.get_project(project_id)
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT id, project_id, created_at, mode,
                       state, current_stage, started_at, completed_at, error_message
                FROM pipeline_runs
                WHERE project_id = ?
                ORDER BY created_at DESC
                """,
                (project_id,),
            ).fetchall()
        return [self._run_from_row(row) for row in rows]

    def get_run(self, project_id: str, run_id: str) -> PipelineRunRecord:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT id, project_id, created_at, mode,
                       state, current_stage, started_at, completed_at, error_message
                FROM pipeline_runs
                WHERE project_id = ? AND id = ?
                """,
                (project_id, run_id),
            ).fetchone()
        if row is None:
            raise RecordNotFoundError(f"Run {run_id} was not found in project {project_id}.")
        return self._run_from_row(row)

    def save_artifact(
        self,
        *,
        project_id: str,
        run_id: str,
        artifact_type: str,
        schema_version: str,
        payload_json: dict[str, Any],
        parent_artifact_roles_json: dict[str, str],
        validation_json: ValidationResult,
    ) -> ArtifactRecord:
        self.get_run(project_id, run_id)
        self._validate_parent_roles(project_id, run_id, parent_artifact_roles_json)

        record = ArtifactRecord(
            id=self._new_id("artifact"),
            project_id=project_id,
            run_id=run_id,
            artifact_type=artifact_type,
            schema_version=schema_version,
            payload_json=payload_json,
            parent_artifact_roles_json=parent_artifact_roles_json,
            validation_json=validation_json,
            status=validation_json.status,
            created_at=self._now(),
        )
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO artifacts (
                  id,
                  project_id,
                  run_id,
                  artifact_type,
                  schema_version,
                  payload_json,
                  parent_artifact_roles_json,
                  validation_json,
                  status,
                  created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.id,
                    record.project_id,
                    record.run_id,
                    record.artifact_type,
                    record.schema_version,
                    json.dumps(record.payload_json),
                    json.dumps(record.parent_artifact_roles_json),
                    record.validation_json.model_dump_json(),
                    record.status,
                    record.created_at,
                ),
            )
        return record

    def get_artifact(self, artifact_id: str) -> ArtifactRecord:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT id, project_id, run_id, artifact_type, schema_version,
                       payload_json, parent_artifact_roles_json, validation_json,
                       status, created_at
                FROM artifacts
                WHERE id = ?
                """,
                (artifact_id,),
            ).fetchone()
        if row is None:
            raise RecordNotFoundError(f"Artifact {artifact_id} was not found.")
        return self._artifact_from_row(row)

    def list_project_artifacts(
        self, project_id: str, run_id: str | None = None
    ) -> list[ArtifactRecord]:
        self.get_project(project_id)
        with self._connect() as connection:
            if run_id is None:
                rows = connection.execute(
                    """
                    SELECT id, project_id, run_id, artifact_type, schema_version,
                           payload_json, parent_artifact_roles_json, validation_json,
                           status, created_at
                    FROM artifacts
                    WHERE project_id = ?
                    ORDER BY created_at DESC
                    """,
                    (project_id,),
                ).fetchall()
            else:
                self.get_run(project_id, run_id)
                rows = connection.execute(
                    """
                    SELECT id, project_id, run_id, artifact_type, schema_version,
                           payload_json, parent_artifact_roles_json, validation_json,
                           status, created_at
                    FROM artifacts
                    WHERE project_id = ? AND run_id = ?
                    ORDER BY created_at DESC
                    """,
                    (project_id, run_id),
                ).fetchall()
        return [self._artifact_from_row(row) for row in rows]

    def find_artifact_by_type(
        self,
        project_id: str,
        run_id: str,
        artifact_type: str,
    ) -> ArtifactRecord | None:
        self.get_run(project_id, run_id)
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT id, project_id, run_id, artifact_type, schema_version,
                       payload_json, parent_artifact_roles_json, validation_json,
                       status, created_at
                FROM artifacts
                WHERE project_id = ? AND run_id = ? AND artifact_type = ?
                ORDER BY created_at ASC
                LIMIT 1
                """,
                (project_id, run_id, artifact_type),
            ).fetchone()
        if row is None:
            return None
        return self._artifact_from_row(row)

    def get_parents(self, artifact_id: str) -> dict[str, ArtifactRecord]:
        artifact = self.get_artifact(artifact_id)
        return {
            role: self.get_artifact(parent_id)
            for role, parent_id in artifact.parent_artifact_roles_json.items()
        }

    def get_children(self, artifact_id: str) -> list[ArtifactRecord]:
        artifact = self.get_artifact(artifact_id)
        artifacts = self.list_project_artifacts(artifact.project_id, artifact.run_id)
        return [
            candidate
            for candidate in artifacts
            if artifact_id in candidate.parent_artifact_roles_json.values()
        ]

    def delete_artifacts(self, artifact_ids: list[str]) -> list[ArtifactRecord]:
        if not artifact_ids:
            return []

        records = [self.get_artifact(artifact_id) for artifact_id in artifact_ids]
        with self._connect() as connection:
            connection.executemany(
                "DELETE FROM artifacts WHERE id = ?",
                [(artifact_id,) for artifact_id in artifact_ids],
            )
        return records

    def _validate_parent_roles(
        self,
        project_id: str,
        run_id: str,
        parent_artifact_roles_json: dict[str, str],
    ) -> None:
        for role, parent_id in parent_artifact_roles_json.items():
            if not role.strip():
                raise LineageError("Parent role names must be non-empty.")
            parent = self.get_artifact(parent_id)
            if parent.project_id != project_id or parent.run_id != run_id:
                raise LineageError(
                    f"Parent artifact {parent_id} must belong to project {project_id} and run {run_id}."
                )

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    @staticmethod
    def _new_id(prefix: str) -> str:
        return f"{prefix}_{uuid4().hex}"

    @staticmethod
    def _now() -> str:
        return datetime.now(UTC).isoformat()

    @staticmethod
    def _project_from_row(row: sqlite3.Row) -> ProjectRecord:
        return ProjectRecord(
            id=row["id"],
            title=row["title"],
            created_at=row["created_at"],
        )

    @staticmethod
    def _run_from_row(row: sqlite3.Row) -> PipelineRunRecord:
        return PipelineRunRecord(
            id=row["id"],
            project_id=row["project_id"],
            created_at=row["created_at"],
            mode=row["mode"],
            state=row["state"] or "pending",
            current_stage=row["current_stage"],
            started_at=row["started_at"],
            completed_at=row["completed_at"],
            error_message=row["error_message"],
        )

    @staticmethod
    def _artifact_from_row(row: sqlite3.Row) -> ArtifactRecord:
        return ArtifactRecord(
            id=row["id"],
            project_id=row["project_id"],
            run_id=row["run_id"],
            artifact_type=row["artifact_type"],
            schema_version=row["schema_version"],
            payload_json=json.loads(row["payload_json"]),
            parent_artifact_roles_json=json.loads(row["parent_artifact_roles_json"]),
            validation_json=ValidationResult.model_validate_json(row["validation_json"]),
            status=row["status"],
            created_at=row["created_at"],
        )
