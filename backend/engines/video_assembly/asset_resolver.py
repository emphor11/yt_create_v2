import os
import re
import urllib.request
import urllib.parse
import json
from pathlib import Path
from typing import Literal
from domain.video_assembly_props import AssetReference


class AssetResolverError(Exception):
    """Raised when stock asset resolution, search, or download fails loudly."""


class AssetResolver:
    def __init__(self, cache_dir: str | Path = "/Users/dakshyadav/Documents/YTcreate_V2/backend/.data/media/assets_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def resolve_asset(
        self,
        *,
        asset_id: str,
        preferred_component: str,
        asset_query: str | None,
    ) -> AssetReference | None:
        asset_type: Literal["image", "video"] = "image" if preferred_component in ("Stock Image", "StockImage") else "video"
        query = asset_query.strip() if asset_query else "abstract business"
        
        # 1. Check Cache first
        sanitized_query = re.sub(r"[^\w\-]", "_", query.lower())
        ext = "mp4" if asset_type == "video" else "jpg"
        cache_filename = f"{sanitized_query}_{asset_type}.{ext}"
        cache_path = self.cache_dir / cache_filename

        if cache_path.exists():
            try:
                cached_bytes = cache_path.read_bytes()
                is_valid = True
                if asset_type == "video" and b"ftyp" not in cached_bytes[:24]:
                    is_valid = False
                elif asset_type == "image" and not (cached_bytes.startswith(b"\xff\xd8") or cached_bytes.startswith(b"\x89PNG") or cached_bytes.startswith(b"GIF")):
                    is_valid = False
                
                if is_valid:
                    return AssetReference(
                        asset_id=asset_id,
                        asset_type=asset_type,
                        source="pexels",  
                        query=query,
                        local_path=str(cache_path),
                        url=None,
                        asset_status="cached"
                    )
                else:
                    cache_path.unlink()
            except Exception:
                try:
                    cache_path.unlink()
                except Exception:
                    pass

        # 2. Look for API Keys in Environment (Raise error loudly if keys are missing)
        pexels_key = os.environ.get("PEXELS_API_KEY")
        pixabay_key = os.environ.get("PIXABAY_API_KEY")

        if not pexels_key and not pixabay_key:
            raise AssetResolverError(
                f"Missing API keys. To resolve asset for query '{query}', PEXELS_API_KEY or PIXABAY_API_KEY must be set."
            )

        url_to_download = None
        source: Literal["pexels", "pixabay"] = "pexels"

        # Try queries: original query first, then fallback queries
        queries_to_try = [query]
        fallback_terms = ["business", "office", "work", "finance"]
        for term in fallback_terms:
            if term not in queries_to_try:
                queries_to_try.append(term)

        for q in queries_to_try:
            # Try Pexels search
            if pexels_key:
                try:
                    url_to_download = self._search_pexels(q, asset_type, pexels_key)
                    if url_to_download:
                        source = "pexels"
                        break
                except Exception:
                    pass

            # Try Pixabay search
            if not url_to_download and pixabay_key:
                try:
                    url_to_download = self._search_pixabay(q, asset_type, pixabay_key)
                    if url_to_download:
                        source = "pixabay"
                        break
                except Exception:
                    pass

        # Fail loudly if no links were returned by the stock APIs for any query
        if not url_to_download:
            raise AssetResolverError(
                f"No stock assets found matching query '{query}' or fallback terms {fallback_terms} (type: '{asset_type}') on Pexels or Pixabay."
            )

        # 3. Download the asset and save in cache (Fail loudly if network or format check fails)
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            req = urllib.request.Request(url_to_download, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as response:
                content_bytes = response.read()
                
                # Validate MP4 header
                if asset_type == "video":
                    if b"ftyp" not in content_bytes[:24]:
                        raise ValueError("Downloaded file is not a valid MP4 video.")
                # Validate image header
                elif asset_type == "image":
                    if not (content_bytes.startswith(b"\xff\xd8") or content_bytes.startswith(b"\x89PNG") or content_bytes.startswith(b"GIF")):
                        raise ValueError("Downloaded file is not a valid image format.")
                        
                cache_path.write_bytes(content_bytes)
            
            return AssetReference(
                asset_id=asset_id,
                asset_type=asset_type,
                source=source,
                query=query,
                local_path=str(cache_path),
                url=url_to_download,
                asset_status="cached"
            )
        except Exception as e:
            raise AssetResolverError(
                f"Failed to download or validate asset from URL '{url_to_download}' for query '{query}': {e}"
            ) from e

    def _search_pexels(self, query: str, asset_type: Literal["image", "video"], api_key: str) -> str | None:
        encoded_query = urllib.parse.quote(query)
        if asset_type == "video":
            url = f"https://api.pexels.com/videos/search?query={encoded_query}&per_page=1"
        else:
            url = f"https://api.pexels.com/v1/search?query={encoded_query}&per_page=1"

        req = urllib.request.Request(url)
        req.add_header("Authorization", api_key)
        req.add_header("User-Agent", "Mozilla/5.0")
        
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
            if asset_type == "video" and data.get("videos"):
                video_files = data["videos"][0].get("video_files", [])
                for f in video_files:
                    if f.get("quality") == "sd" or "sd" in f.get("link", ""):
                        return f["link"]
                if video_files:
                    return video_files[0]["link"]
            elif asset_type == "image" and data.get("photos"):
                return data["photos"][0]["src"].get("large")
        return None

    def _search_pixabay(self, query: str, asset_type: Literal["image", "video"], api_key: str) -> str | None:
        encoded_query = urllib.parse.quote(query)
        if asset_type == "video":
            url = f"https://pixabay.com/api/videos/?key={api_key}&q={encoded_query}&per_page=3"
        else:
            url = f"https://pixabay.com/api/?key={api_key}&q={encoded_query}&per_page=3"

        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
            hits = data.get("hits", [])
            if hits:
                if asset_type == "video":
                    video_streams = hits[0].get("videos", {})
                    for size in ["medium", "small", "large"]:
                        if video_streams.get(size) and video_streams[size].get("url"):
                            return video_streams[size]["url"]
                else:
                    return hits[0].get("largeImageURL")
        return None
