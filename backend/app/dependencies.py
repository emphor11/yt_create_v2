import os
from functools import lru_cache
from pathlib import Path

from artifact_store.sqlite_store import ArtifactStore
from app.pipeline_service import PipelineService, build_pipeline_service
from engines.render_engine import RenderEngine
from providers.media_storage import LocalMediaStorage
from providers.remotion_provider import RemotionProvider


def _default_database_path() -> Path:
    configured_path = os.getenv("YTCREATE_DB_PATH")
    if configured_path:
        return Path(configured_path)
    return Path(__file__).resolve().parents[1] / ".data" / "ytcreate_v2.db"


def _default_media_root() -> Path:
    configured_path = os.getenv("YTCREATE_MEDIA_ROOT")
    if configured_path:
        return Path(configured_path)
    return Path(__file__).resolve().parents[1] / ".data" / "media"


@lru_cache
def get_artifact_store() -> ArtifactStore:
    store = ArtifactStore(_default_database_path())
    store.initialize()
    return store


@lru_cache
def get_media_storage() -> LocalMediaStorage:
    return LocalMediaStorage(_default_media_root())


def get_pipeline_service() -> PipelineService:
    repo_root = Path(__file__).resolve().parents[2]
    render_engine = RenderEngine(
        media_storage=get_media_storage(),
        remotion_provider=RemotionProvider(repo_root / "renderer" / "remotion"),
    )
    return build_pipeline_service(get_artifact_store(), render_engine=render_engine)
