import os
from functools import lru_cache
from pathlib import Path

from artifact_store.sqlite_store import ArtifactStore
from app.pipeline_service import PipelineService, build_pipeline_service


def _default_database_path() -> Path:
    configured_path = os.getenv("YTCREATE_DB_PATH")
    if configured_path:
        return Path(configured_path)
    return Path(__file__).resolve().parents[1] / ".data" / "ytcreate_v2.db"


@lru_cache
def get_artifact_store() -> ArtifactStore:
    store = ArtifactStore(_default_database_path())
    store.initialize()
    return store


def get_pipeline_service() -> PipelineService:
    return build_pipeline_service(get_artifact_store())

