import os
from functools import lru_cache
from pathlib import Path

from artifact_store.sqlite_store import ArtifactStore
from app.pipeline_service import PipelineService, build_pipeline_service
from engines.render_engine import RenderEngine
from providers.gemini_provider import GeminiProvider
from providers.grok_provider import GrokProvider
from providers.llm_provider import LLMProvider
from providers.media_storage import LocalMediaStorage
from providers.remotion_provider import RemotionProvider


def _default_env_path() -> Path:
    configured_path = os.getenv("YTCREATE_ENV_FILE")
    if configured_path:
        return Path(configured_path)
    return Path(__file__).resolve().parents[1] / ".env"


@lru_cache
def _load_backend_dotenv() -> None:
    _load_env_file(_default_env_path())


def _load_env_file(path: Path) -> None:
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line.removeprefix("export ").strip()
        if "=" not in line:
            continue

        key, raw_value = line.split("=", 1)
        key = key.strip()
        value = raw_value.strip()
        if not key:
            continue
        if (
            len(value) >= 2
            and value[0] == value[-1]
            and value[0] in {"'", '"'}
        ):
            value = value[1:-1]
        os.environ.setdefault(key, value)


def _default_database_path() -> Path:
    _load_backend_dotenv()
    configured_path = os.getenv("YTCREATE_DB_PATH")
    if configured_path:
        return Path(configured_path)
    return Path(__file__).resolve().parents[1] / ".data" / "ytcreate_v2.db"


def _default_media_root() -> Path:
    _load_backend_dotenv()
    configured_path = os.getenv("YTCREATE_MEDIA_ROOT")
    if configured_path:
        return Path(configured_path)
    return Path(__file__).resolve().parents[1] / ".data" / "media"


def _default_gemini_model() -> str:
    _load_backend_dotenv()
    return os.getenv("GEMINI_MODEL", "gemini-3.5-flash")


def _default_grok_model() -> str:
    _load_backend_dotenv()
    return os.getenv("GROK_MODEL", "grok-2-1212")


@lru_cache
def get_artifact_store() -> ArtifactStore:
    store = ArtifactStore(_default_database_path())
    store.initialize()
    return store


@lru_cache
def get_media_storage() -> LocalMediaStorage:
    return LocalMediaStorage(_default_media_root())


@lru_cache
def get_llm_provider() -> LLMProvider | None:
    _load_backend_dotenv()
    
    grok_api_key = os.getenv("GROK_API_KEY", "").strip()
    if grok_api_key:
        return GrokProvider(
            api_key=grok_api_key,
            model=_default_grok_model(),
        )

    gemini_api_key = (
        os.getenv("GEMINI_API_KEY", "").strip()
        or os.getenv("GOOGLE_API_KEY", "").strip()
    )
    if gemini_api_key:
        return GeminiProvider(
            api_key=gemini_api_key,
            model=_default_gemini_model(),
        )

    return None


def get_pipeline_service() -> PipelineService:
    repo_root = Path(__file__).resolve().parents[2]
    render_engine = RenderEngine(
        media_storage=get_media_storage(),
        remotion_provider=RemotionProvider(repo_root / "renderer" / "remotion"),
    )
    return build_pipeline_service(
        get_artifact_store(),
        render_engine=render_engine,
        llm_provider=get_llm_provider(),
    )
