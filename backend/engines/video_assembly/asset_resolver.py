import os
import re
import subprocess
import urllib.request
import urllib.parse
import json
from pathlib import Path
from typing import Literal, Any
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
        # Only resolve stock media assets when component is StockVideo or StockImage (Mode A)
        if preferred_component not in ("StockVideo", "Stock Video", "StockImage", "Stock Image"):
            return None

        asset_type: Literal["image", "video"] = "image" if preferred_component in ("Stock Image", "StockImage") else "video"
        query = asset_query.strip() 
        
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

        # 2. Look for API Keys in Environment (Raise error loudly if keys are missing)
        pexels_key = os.environ.get("PEXELS_API_KEY")
        pixabay_key = os.environ.get("PIXABAY_API_KEY")

        if not pexels_key and not pixabay_key:
            raise AssetResolverError(
                f"Missing API keys. To resolve asset for query '{query}', PEXELS_API_KEY or PIXABAY_API_KEY must be set."
            )

        url_to_download = None
        source: Literal["pexels", "pixabay"] = "pexels"

        # Try Pexels search
        if pexels_key:
            try:
                url_to_download = self._search_pexels(query, asset_type, pexels_key)
                if url_to_download:
                    source = "pexels"
            except Exception:
                pass

        # Try Pixabay search
        if not url_to_download and pixabay_key:
            try:
                url_to_download = self._search_pixabay(query, asset_type, pixabay_key)
                if url_to_download:
                    source = "pixabay"
            except Exception:
                pass

        # Fail loudly if no links were returned by the stock APIs for the query
        if not url_to_download:
            raise AssetResolverError(
                f"No stock assets found matching query '{query}' (type: '{asset_type}') on Pexels or Pixabay."
            )

        # 3. Download the asset and save in cache (Fail loudly if network or format check fails)
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
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

    def _search_pexels(self, query: str, asset_type: Literal["image", "video"], api_key: str) -> str | None:
        encoded_query = urllib.parse.quote(query)
        if asset_type == "video":
            url = f"https://api.pexels.com/videos/search?query={encoded_query}&per_page=10"
        else:
            url = f"https://api.pexels.com/v1/search?query={encoded_query}&per_page=1"

        req = urllib.request.Request(url)
        req.add_header("Authorization", api_key)
        req.add_header("User-Agent", "Mozilla/5.0")
        
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
                    best = max(candidates, key=_file_sort_key)
                    return best["link"]
            elif asset_type == "image" and data.get("photos"):
                src = data["photos"][0].get("src", {})
                return src.get("large2x") or src.get("large") or src.get("original")
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
                    for size in ["large", "medium", "small"]:
                        if video_streams.get(size) and video_streams[size].get("url"):
                            return video_streams[size]["url"]
                else:
                    return hits[0].get("largeImageURL") or hits[0].get("fullHDURL") or hits[0].get("imageURL")
        return None
