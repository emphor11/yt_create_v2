"""Stage-level structured logger for the YTCreate V2 pipeline.

Every pipeline stage calls log_start() on entry, log_finish() on success,
and log_error() on failure.  All records are linked to a project_id and
run_id so the full execution history of a video can be reconstructed.

This class is injected — never instantiated inside business logic.
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any

_logger = logging.getLogger("ytcreate.pipeline")


@dataclass
class StageLogRecord:
    """Immutable record of a single stage log event."""

    project_id: str
    run_id: str
    stage: str
    event: str                           # "start" | "finish" | "error"
    timestamp: float = field(default_factory=time.time)
    duration_ms: int | None = None
    llm_tokens_used: int | None = None
    error_type: str | None = None
    error_message: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)


class StageLogger:
    """Records structured log events for every pipeline stage.

    Writes to the standard Python logging system (ytcreate.pipeline logger)
    as structured dicts so any log aggregator (CloudWatch, Datadog, etc.)
    can ingest them without changes.
    """

    def log_start(self, project_id: str, run_id: str, stage: str) -> float:
        """Log stage entry and return the start timestamp for duration tracking."""
        start = time.time()
        self._emit(
            StageLogRecord(
                project_id=project_id,
                run_id=run_id,
                stage=stage,
                event="start",
                timestamp=start,
            )
        )
        return start

    def log_finish(
        self,
        project_id: str,
        run_id: str,
        stage: str,
        *,
        start_time: float,
        llm_tokens_used: int | None = None,
    ) -> None:
        """Log successful stage completion with duration and optional LLM cost."""
        duration_ms = int((time.time() - start_time) * 1000)
        self._emit(
            StageLogRecord(
                project_id=project_id,
                run_id=run_id,
                stage=stage,
                event="finish",
                duration_ms=duration_ms,
                llm_tokens_used=llm_tokens_used,
            )
        )

    def log_error(
        self,
        project_id: str,
        run_id: str,
        stage: str,
        *,
        error: Exception,
        start_time: float | None = None,
    ) -> None:
        """Log a stage failure with error type, message, and optional duration."""
        duration_ms = int((time.time() - start_time) * 1000) if start_time else None
        self._emit(
            StageLogRecord(
                project_id=project_id,
                run_id=run_id,
                stage=stage,
                event="error",
                duration_ms=duration_ms,
                error_type=type(error).__name__,
                error_message=str(error),
            )
        )

    @staticmethod
    def _emit(record: StageLogRecord) -> None:
        _logger.info(
            "pipeline.stage.%s",
            record.event,
            extra={
                "project_id": record.project_id,
                "run_id": record.run_id,
                "stage": record.stage,
                "event": record.event,
                "timestamp": record.timestamp,
                "duration_ms": record.duration_ms,
                "llm_tokens_used": record.llm_tokens_used,
                "error_type": record.error_type,
                "error_message": record.error_message,
            },
        )
