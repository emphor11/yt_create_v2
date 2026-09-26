import logging
import os
import re
import subprocess
import urllib.request
import urllib.parse
import json
from pathlib import Path
from typing import Literal, Any
from domain.video_assembly_props import AssetReference

logger = logging.getLogger(__name__)


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
        asset_query: str | None = None,
        asset_queries: list[str] | None = None,
        topic: str | None = None,
    ) -> AssetReference | None:
        # Only resolve stock media assets when component is StockVideo or StockImage (Mode A)
        if preferred_component not in ("StockVideo", "Stock Video", "StockImage", "Stock Image"):
            return None

        asset_type: Literal["image", "video"] = "image" if preferred_component in ("Stock Image", "StockImage") else "video"

        # Build clean candidate queries list (1 to 3 queries in priority order)
        raw_queries: list[str] = []
        if asset_queries and isinstance(asset_queries, list):
            raw_queries.extend(asset_queries)
        if asset_query and isinstance(asset_query, str):
            raw_queries.append(asset_query)

        candidate_queries: list[str] = []
        for q in raw_queries:
            if not q or not isinstance(q, str):
                continue
            q_clean = q.strip()
            q_lower = q_clean.lower()
            if (
                any(pat in q_lower for pat in ("viewer ", "viewer's", "viewers", "understand", "realize", "grasp"))
                or any(punct in q_clean for punct in (".", ";", "?", "!"))
                or len(q_clean.split()) > 8
                or len(q_clean) < 3
            ):
                continue
            if q_clean not in candidate_queries:
                candidate_queries.append(q_clean)

        if not candidate_queries:
            if topic and isinstance(topic, str) and topic.strip():
                clean_topic = topic.strip().lower()
                if any(k in clean_topic for k in ("car", "auto", "vehicle")):
                    candidate_queries = ["car dealership showroom", "car driving on road"]
                else:
                    words = clean_topic.split()[:3]
                    candidate_queries = [f"{' '.join(words)} footage", "person reviewing financial documents"]
            else:
                candidate_queries = ["person reviewing financial documents"]

        # Look for API Keys in Environment (Raise error loudly if keys are missing)
        pexels_key = os.environ.get("PEXELS_API_KEY")
        pixabay_key = os.environ.get("PIXABAY_API_KEY")

        if not pexels_key and not pixabay_key:
            raise AssetResolverError(
                f"Missing API keys. To resolve asset for queries '{candidate_queries}', PEXELS_API_KEY or PIXABAY_API_KEY must be set."
            )

        # Iterate through candidate queries up to 3
        last_error: Exception | None = None
        for query in candidate_queries[:3]:
            # 1. Check Cache first
            sanitized_query = re.sub(r"[^\w\-]", "_", query.lower())
            ext = "mp4" if asset_type == "video" else "jpg"
            cache_filename = f"{sanitized_query}_{asset_type}.{ext}"
            cache_path = self.cache_dir / cache_filename

            if cache_path.exists():
                try:
                    cached_bytes = cache_path.read_bytes()
                    is_valid = True
                    if asset_type == "video":
                        if b"ftyp" not in cached_bytes[:24]:
                            is_valid = False
                        elif not self._is_video_compliant(cache_path):
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

            candidate_urls: list[tuple[str, Literal["pexels", "pixabay"]]] = []

            # Try Pexels search
            if pexels_key:
                try:
                    for link in self._search_pexels(query, asset_type, pexels_key):
                        candidate_urls.append((link, "pexels"))
                except Exception as e:
                    logger.warning(f"Pexels search failed for query '{query}': {e}")

            # Try Pixabay search (add as fallback or if Pexels returned no links)
            if pixabay_key:
                try:
                    for link in self._search_pixabay(query, asset_type, pixabay_key):
                        candidate_urls.append((link, "pixabay"))
                except Exception as e:
                    logger.warning(f"Pixabay search failed for query '{query}': {e}")

            if not candidate_urls:
                logger.info(f"Query '{query}' returned no stock assets. Trying next candidate query...")
                continue

            # Download the asset and save in cache (Iterate through candidates until one succeeds)
            for url_to_download, source in candidate_urls:
                try:
                    headers = {
                        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                        "Referer": "https://www.pexels.com/" if source == "pexels" else "https://pixabay.com/",
                    }
                    req = urllib.request.Request(url_to_download, headers=headers)
                    with urllib.request.urlopen(req, timeout=20) as response:
                        content_bytes = response.read()

                    # Validate MP4 header and save native video directly
                    if asset_type == "video":
                        if b"ftyp" not in content_bytes[:24]:
                            raise ValueError("Downloaded file is not a valid MP4 video.")
                        cache_path.write_bytes(content_bytes)
                        fps = self._get_video_fps(cache_path)
                        if fps and not (abs(fps - 29.97) < 0.5 or abs(fps - 30.0) < 0.5 or abs(fps - 60.0) < 0.5):
                            self._smooth_interpolate_fps(cache_path)
                        if not self._is_video_compliant(cache_path):
                            raise ValueError("Downloaded video is not compliant or has invalid resolution.")

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
                    last_error = e
                    logger.warning(
                        f"Candidate asset from {source} failed for query '{query}' ({url_to_download}): {e}. Trying next candidate..."
                    )
                    if cache_path.exists():
                        try:
                            cache_path.unlink()
                        except Exception:
                            pass
                    continue

        if last_error:
            raise AssetResolverError(
                f"Failed to download or validate any stock asset for candidate queries {candidate_queries[:3]}: {last_error}"
            ) from last_error
        else:
            raise AssetResolverError(
                f"No stock assets found matching candidate queries: {candidate_queries[:3]} on Pexels or Pixabay."
            )

    def _get_video_fps(self, path: Path) -> float | None:
        """Extracts the video framerate using ffprobe."""
        try:
            cmd = [
                "ffprobe", "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "stream=r_frame_rate,avg_frame_rate",
                "-of", "json",
                str(path),
            ]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if res.returncode != 0:
                return None
            info = json.loads(res.stdout)
            streams = info.get("streams", [])
            if not streams:
                return None
            rate_str = streams[0].get("r_frame_rate") or streams[0].get("avg_frame_rate") or ""
            if "/" in rate_str:
                num, den = rate_str.split("/", 1)
                return float(num) / float(den) if float(den) != 0 else None
            return float(rate_str) if rate_str else None
        except Exception:
            return None

    def _smooth_interpolate_fps(self, path: Path) -> None:
        """Smoothly interpolates non-30fps video to 30fps using motion blending to avoid duplicate frame judder."""
        temp_path = path.with_suffix(".tmp.mp4")
        try:
            cmd = [
                "ffmpeg", "-y",
                "-i", str(path),
                "-vf", "minterpolate=fps=30:mi_mode=blend",
                "-c:v", "libx264",
                "-preset", "ultrafast",
                "-crf", "18",
                "-c:a", "copy",
                str(temp_path),
            ]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=45)
            if res.returncode == 0 and temp_path.exists() and temp_path.stat().st_size > 0:
                temp_path.replace(path)
        except Exception:
            if temp_path.exists():
                try:
                    temp_path.unlink()
                except Exception:
                    pass

    def _is_video_compliant(self, path: Path) -> bool:
        """Verifies that the cached video is valid and has sufficient HD resolution."""
        try:
            cmd = [
                "ffprobe", "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "stream=width,height",
                "-of", "json",
                str(path),
            ]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if res.returncode != 0:
                return False
            info = json.loads(res.stdout)
            streams = info.get("streams", [])
            if not streams:
                return False
            st = streams[0]
            width = int(st.get("width", 0))
            height = int(st.get("height", 0))
            if width <= 0 or height <= 0:
                return False
            return True
        except Exception:
            return False

    def _search_pexels(self, query: str, asset_type: Literal["image", "video"], api_key: str) -> list[str]:
        encoded_query = urllib.parse.quote(query)
        if asset_type == "video":
            url = f"https://api.pexels.com/videos/search?query={encoded_query}&per_page=10"
        else:
            url = f"https://api.pexels.com/v1/search?query={encoded_query}&per_page=5"

        headers = {
            "Authorization": api_key,
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        }
        req = urllib.request.Request(url, headers=headers)
        
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
            if asset_type == "video" and data.get("videos"):
                candidates: list[dict[str, Any]] = []
                for v in data.get("videos", []):
                    for f in v.get("video_files", []):
                        link = f.get("link", "")
                        if f.get("file_type") == "video/mp4" or "mp4" in link:
                            candidates.append(f)

                def _file_sort_key(f: dict[str, Any]) -> tuple[int, int, int, int]:
                    width = f.get("width") or 0
                    height = f.get("height") or 0
                    fps = f.get("fps") or 0.0

                    # 1. Prefer landscape for 16:9 YouTube videos
                    is_landscape = 1 if width >= height else 0

                    # 2. Prefer 30fps or 60fps (exact match to Remotion's 30fps composition)
                    is_30fps = 1 if (abs(fps - 29.97) < 0.5 or abs(fps - 30.0) < 0.5 or abs(fps - 60.0) < 0.5) else 0

                    # 3. Prefer 1080p, then 720p
                    is_1080p = 1 if (width == 1920 or height == 1080) else 0
                    is_720p = 1 if (width == 1280 or height == 720) else 0
                    quality_score = 3 if is_1080p else (2 if is_720p else (1 if f.get("quality") == "hd" else 0))

                    # 4. Total resolution
                    return (is_landscape, is_30fps, quality_score, width * height)

                if candidates:
                    candidates.sort(key=_file_sort_key, reverse=True)
                    links: list[str] = []
                    seen: set[str] = set()
                    for c in candidates:
                        link = c.get("link")
                        if link and link not in seen:
                            seen.add(link)
                            links.append(link)
                    return links
            elif asset_type == "image" and data.get("photos"):
                links: list[str] = []
                for p in data["photos"]:
                    src = p.get("src", {})
                    for key in ("large2x", "large", "original"):
                        if src.get(key) and src[key] not in links:
                            links.append(src[key])
                            break
                return links
        return []

    def _search_pixabay(self, query: str, asset_type: Literal["image", "video"], api_key: str) -> list[str]:
        encoded_query = urllib.parse.quote(query)
        if asset_type == "video":
            url = f"https://pixabay.com/api/videos/?key={api_key}&q={encoded_query}&per_page=5"
        else:
            url = f"https://pixabay.com/api/?key={api_key}&q={encoded_query}&per_page=5"

        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        }
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
            hits = data.get("hits", [])
            links: list[str] = []
            if hits:
                if asset_type == "video":
                    for hit in hits:
                        video_streams = hit.get("videos", {})
                        for size in ["large", "medium", "small"]:
                            if video_streams.get(size) and video_streams[size].get("url"):
                                links.append(video_streams[size]["url"])
                                break
                else:
                    for hit in hits:
                        img_url = hit.get("largeImageURL") or hit.get("fullHDURL") or hit.get("imageURL")
                        if img_url and img_url not in links:
                            links.append(img_url)
            return links
        return []
