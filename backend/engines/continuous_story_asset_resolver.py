from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import logging
import os
import re
import shutil
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Literal

from domain.continuous_story_plan import ImageAssetRequest
from providers.media_storage import LocalMediaStorage

logger = logging.getLogger(__name__)


class ContinuousStoryAssetResolverError(Exception):
    """Raised when continuous story image asset resolution, search, or download fails."""
    pass


@dataclass
class ResolvedImageAsset:
    asset_id: str
    local_path: str
    provider: Literal["pexels", "pixabay"]
    source_url: str
    author: str
    query: str
    width: int
    height: int
    license: str = "Free Stock Media License"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ContinuousStoryAssetResolver:
    """
    Asset resolver for the Continuous Story Engine.

    Responsibilities:
    1. Receives an ImageAssetRequest.
    2. Searches Pexels as the primary provider.
    3. Falls back to Pixabay if Pexels returns no acceptable results.
    4. Downloads and validates the image file.
    5. Caches images locally to avoid redundant network round-trips.
    6. Returns a stable ResolvedImageAsset (local relative path for Remotion staticFile).
    7. Fails loudly with standardized error codes:
       - IMAGE_ASSET_REQUEST_MISSING
       - UNKNOWN_ASSET_ID
       - IMAGE_SEARCH_NO_RESULT
       - IMAGE_DOWNLOAD_FAILED
       - IMAGE_LOCAL_FILE_MISSING
    """

    def __init__(
        self,
        *,
        media_storage: LocalMediaStorage | None = None,
        cache_dir: str | Path | None = None,
        remotion_public_dir: str | Path | None = None,
    ) -> None:
        self.media_storage = media_storage
        self.cache_dir = Path(
            cache_dir or "/Users/dakshyadav/Documents/YTcreate_V2/backend/.data/media/assets_cache"
        )
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.remotion_public_dir = Path(
            remotion_public_dir or "/Users/dakshyadav/Documents/YTcreate_V2/renderer/remotion/public"
        )

    def resolve_image_asset(
        self,
        asset_request: ImageAssetRequest | dict[str, Any] | None,
        *,
        object_id: str,
        project_id: str = "default",
        run_id: str = "default",
    ) -> ResolvedImageAsset:
        """
        Resolves an ImageAssetRequest into a physical local image and returns a ResolvedImageAsset.
        """
        if asset_request is None:
            raise ContinuousStoryAssetResolverError(
                f"IMAGE_ASSET_REQUEST_MISSING: Image '{object_id}' has no asset_request."
            )

        if isinstance(asset_request, dict):
            try:
                request_model = ImageAssetRequest.model_validate(asset_request)
            except Exception as e:
                raise ContinuousStoryAssetResolverError(
                    f"IMAGE_ASSET_REQUEST_MISSING: Invalid asset_request on '{object_id}': {e}"
                ) from e
        elif isinstance(asset_request, ImageAssetRequest):
            request_model = asset_request
        else:
            raise ContinuousStoryAssetResolverError(
                f"IMAGE_ASSET_REQUEST_MISSING: Unknown asset_request type on '{object_id}'."
            )

        query = request_model.query.strip()
        if not query:
            raise ContinuousStoryAssetResolverError(
                f"IMAGE_ASSET_REQUEST_MISSING: Image '{object_id}' has empty search query."
            )

        # ----------------------------------------------------
        # 1. Check Local Cache First
        # ----------------------------------------------------
        query_slug = re.sub(r"[^\w\-]", "_", query.lower())[:60].strip("_")
        cache_image_path = self.cache_dir / f"img_{query_slug}.jpg"
        cache_meta_path = self.cache_dir / f"img_{query_slug}.json"

        if cache_image_path.exists():
            try:
                content = cache_image_path.read_bytes()
                if self._is_valid_image(content):
                    meta: dict[str, Any] = {}
                    if cache_meta_path.exists():
                        try:
                            meta = json.loads(cache_meta_path.read_text(encoding="utf-8"))
                        except Exception:
                            meta = {}

                    return self._finalize_asset(
                        source_file=cache_image_path,
                        object_id=object_id,
                        project_id=project_id,
                        run_id=run_id,
                        query=query,
                        provider=meta.get("provider", "pexels"),
                        source_url=meta.get("source_url", str(cache_image_path)),
                        author=meta.get("author", "Cached Stock Author"),
                        width=meta.get("width", 1920),
                        height=meta.get("height", 1080),
                    )
            except Exception as cache_err:
                logger.warning(f"Failed to load cached asset for '{query}': {cache_err}. Proceeding to search.")

        # ----------------------------------------------------
        # 2. Search Stock Providers (Pexels Primary, Pixabay Fallback)
        # ----------------------------------------------------
        pexels_key = os.environ.get("PEXELS_API_KEY", "").strip()
        pixabay_key = os.environ.get("PIXABAY_API_KEY", "").strip()

        candidates: list[dict[str, Any]] = []

        # Try Pexels first
        if pexels_key:
            try:
                candidates = self._search_pexels(
                    query=query,
                    orientation=request_model.orientation,
                    style=request_model.style,
                    api_key=pexels_key,
                )
            except Exception as e:
                logger.warning(f"Pexels search failed for query '{query}': {e}. Falling back to Pixabay.")

        # Fallback to Pixabay if Pexels returned no candidates
        if not candidates and pixabay_key:
            try:
                candidates = self._search_pixabay(
                    query=query,
                    orientation=request_model.orientation,
                    style=request_model.style,
                    api_key=pixabay_key,
                )
            except Exception as e:
                logger.warning(f"Pixabay search failed for query '{query}': {e}.")

        if not candidates:
            raise ContinuousStoryAssetResolverError(
                f"IMAGE_SEARCH_NO_RESULT: Search returned no usable image for query '{query}' on Pexels or Pixabay."
            )

        # ----------------------------------------------------
        # 3. Download, Validate, and Cache Candidate Image
        # ----------------------------------------------------
        last_error: Exception | None = None
        for cand in candidates:
            download_url = cand.get("download_url")
            if not download_url:
                continue

            try:
                headers = {
                    "User-Agent": (
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                    ),
                    "Referer": "https://www.pexels.com/" if cand.get("provider") == "pexels" else "https://pixabay.com/",
                }
                req = urllib.request.Request(download_url, headers=headers)
                with urllib.request.urlopen(req, timeout=20) as response:
                    image_bytes = response.read()

                if not self._is_valid_image(image_bytes):
                    raise ValueError(f"Downloaded file from {download_url} is not a valid JPEG/PNG/WebP image.")

                # Save to cache
                cache_image_path.write_bytes(image_bytes)
                meta_data = {
                    "provider": cand.get("provider", "pexels"),
                    "source_url": cand.get("source_url") or download_url,
                    "author": cand.get("author", "Stock Photographer"),
                    "query": query,
                    "width": cand.get("width", 1920),
                    "height": cand.get("height", 1080),
                }
                cache_meta_path.write_text(json.dumps(meta_data, indent=2), encoding="utf-8")

                return self._finalize_asset(
                    source_file=cache_image_path,
                    object_id=object_id,
                    project_id=project_id,
                    run_id=run_id,
                    query=query,
                    provider=cand.get("provider", "pexels"),
                    source_url=cand.get("source_url") or download_url,
                    author=cand.get("author", "Stock Photographer"),
                    width=cand.get("width", 1920),
                    height=cand.get("height", 1080),
                )
            except Exception as exc:
                last_error = exc
                logger.warning(f"Candidate download failed from {download_url}: {exc}. Trying next candidate...")
                if cache_image_path.exists():
                    try:
                        cache_image_path.unlink()
                    except Exception:
                        pass
                continue

        raise ContinuousStoryAssetResolverError(
            f"IMAGE_DOWNLOAD_FAILED: Failed to download candidate images for query '{query}': {last_error}"
        ) from last_error

    def _finalize_asset(
        self,
        *,
        source_file: Path,
        object_id: str,
        project_id: str,
        run_id: str,
        query: str,
        provider: Literal["pexels", "pixabay"],
        source_url: str,
        author: str,
        width: int,
        height: int,
    ) -> ResolvedImageAsset:
        """Copies downloaded image into project run storage and Remotion public dir."""
        if not source_file.exists() or source_file.stat().st_size == 0:
            raise ContinuousStoryAssetResolverError(
                f"IMAGE_LOCAL_FILE_MISSING: Downloaded local image file does not exist or is empty at {source_file}."
            )

        ext = source_file.suffix.lstrip(".") or "jpg"
        asset_id = f"assets/{object_id}.{ext}"

        # 1. Save into project media storage if available
        if self.media_storage:
            storage_key = f"projects/{project_id}/runs/{run_id}/{asset_id}"
            dest_media_path = self.media_storage.ensure_parent(storage_key)
            if not dest_media_path.exists() or dest_media_path.stat().st_size != source_file.stat().st_size:
                shutil.copy2(source_file, dest_media_path)
            local_target = dest_media_path
        else:
            local_target = source_file

        # 2. Stage into Remotion public directory for staticFile()
        public_dest = self.remotion_public_dir / "assets" / f"{object_id}.{ext}"
        public_dest.parent.mkdir(parents=True, exist_ok=True)
        if not public_dest.exists() or public_dest.stat().st_size != source_file.stat().st_size:
            shutil.copy2(source_file, public_dest)

        # 3. Verify file exists
        if not local_target.exists() or local_target.stat().st_size == 0:
            raise ContinuousStoryAssetResolverError(
                f"IMAGE_LOCAL_FILE_MISSING: Downloaded local image file does not exist or is empty at {local_target}."
            )

        return ResolvedImageAsset(
            asset_id=asset_id,
            local_path=asset_id,
            provider=provider,
            source_url=source_url,
            author=author,
            query=query,
            width=width,
            height=height,
        )

    def _search_pexels(
        self,
        query: str,
        orientation: str,
        style: str,
        api_key: str,
    ) -> list[dict[str, Any]]:
        encoded = urllib.parse.quote(query)
        orient = orientation if orientation in ("landscape", "portrait", "square") else "landscape"
        url = f"https://api.pexels.com/v1/search?query={encoded}&orientation={orient}&per_page=5"

        headers = {
            "Authorization": api_key,
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
        }
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=12) as response:
            data = json.loads(response.read().decode("utf-8"))

        photos = data.get("photos", [])
        candidates: list[dict[str, Any]] = []
        for p in photos:
            src = p.get("src", {})
            download_url = src.get("large2x") or src.get("large") or src.get("original")
            if download_url:
                candidates.append({
                    "provider": "pexels",
                    "download_url": download_url,
                    "source_url": p.get("url") or download_url,
                    "author": p.get("photographer", "Pexels Creator"),
                    "width": p.get("width", 1920),
                    "height": p.get("height", 1080),
                })
        return candidates

    def _search_pixabay(
        self,
        query: str,
        orientation: str,
        style: str,
        api_key: str,
    ) -> list[dict[str, Any]]:
        encoded = urllib.parse.quote(query)
        pix_orient = "horizontal" if orientation == "landscape" else ("vertical" if orientation == "portrait" else "all")
        img_type = "illustration" if style == "illustration" else "photo"
        url = f"https://pixabay.com/api/?key={api_key}&q={encoded}&orientation={pix_orient}&image_type={img_type}&per_page=5"

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
        }
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=12) as response:
            data = json.loads(response.read().decode("utf-8"))

        hits = data.get("hits", [])
        candidates: list[dict[str, Any]] = []
        for h in hits:
            download_url = h.get("largeImageURL") or h.get("fullHDURL") or h.get("imageURL")
            if download_url:
                candidates.append({
                    "provider": "pixabay",
                    "download_url": download_url,
                    "source_url": h.get("pageURL") or download_url,
                    "author": h.get("user", "Pixabay Creator"),
                    "width": h.get("imageWidth", 1920),
                    "height": h.get("imageHeight", 1080),
                })
        return candidates

    def _is_valid_image(self, b: bytes) -> bool:
        """Validates that bytes represent a valid JPEG, PNG, or WebP image."""
        if len(b) < 12:
            return False
        # JPEG
        if b.startswith(b"\xff\xd8"):
            return True
        # PNG
        if b.startswith(b"\x89PNG\r\n\x1a\n"):
            return True
        # WebP
        if b.startswith(b"RIFF") and b[8:12] == b"WEBP":
            return True
        return False
